import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go


import api


@st.cache_data
def load_customer_data():
    """Load customer data"""

    #sales = pd.DataFrame(api.get_sales())
    daily_sales = api.get_daily_sales()

    if 'date' in daily_sales.columns:
        daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

    return daily_sales


def calculate_rfm(daily_sales):
    """Calculate RFM metrics."""

    daily_sales = daily_sales.copy()
    daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

    current_date = daily_sales['date'].max()

    rfm = (
        daily_sales.groupby('customer_id')
        .agg(
            recency=('date', lambda x: (current_date - x.max()).days),
            frequency=('receipt_id', 'count'),
            monetary=('revenue', 'sum')
        )
        .reset_index()
    )

    # Remove outliers above the 99th percentile
    rfm_clean = rfm[
        (rfm['recency'] < rfm['recency'].quantile(0.99)) &
        (rfm['frequency'] < rfm['frequency'].quantile(0.99)) &
        (rfm['monetary'] < rfm['monetary'].quantile(0.99))
    ].copy()

    return (rfm, rfm_clean)


def calculate_rfm_scores(df):
    """Calculate RFM scores using custom binning"""

    # Recency Score (lower is better)
    recency_bins = [0, 7, 30, 60, float('inf')]
    recency_labels = [4, 3, 2, 1]
    df['r_score'] = pd.cut(df['recency'], bins=recency_bins, labels=recency_labels, right=False).astype(int)

    # Frequency Score (higher is better)
    freq_bins = [0, 1, 3, 5, float('inf')]
    freq_labels = [1, 2, 3, 4]
    df['f_score'] = pd.cut(df['frequency'], bins=freq_bins, labels=freq_labels, right=False).astype(int)

    # Monetary Score (higher is better)
    monetary_bins = [0, 100, 500, 1000, float('inf')]
    monetary_labels = [1, 2, 3, 4]
    df['m_score'] = pd.cut(df['monetary'], bins=monetary_bins, labels=monetary_labels, right=False).astype(int)

    return df


def segment_customers(df):
    """Segment customers based on RFM scores"""

    segments = []

    for _, row in df.iterrows():
        r, f, m = row['r_score'], row['f_score'], row['m_score']

        if r >= 3 and f >= 3 and m >= 3:
            segments.append('Champions')
        elif r >= 3 and f >= 2 and m >= 2:
            segments.append('Loyal Customers')
        elif r >= 3 and f >= 1 and m >= 1:
            segments.append('Potential Loyalists')
        elif r >= 2 and f >= 3 and m >= 3:
            segments.append('Recent Customers')
        elif r >= 2 and f >= 1 and m >= 1:
            segments.append('Promising')
        elif r >= 1 and f >= 3 and m >= 3:
            segments.append('Need Attention')
        elif r >= 1 and f >= 1 and m >= 1:
            segments.append('At Risk')
        else:
            segments.append('Lost')

    df['segment'] = segments
    return df


def perform_kmeans(rfm):
    """Perform KMeans clustering"""

    # Prepare data
    cluster_data = rfm[['recency', 'frequency', 'monetary']].copy()

    # Log transform
    cluster_data['monetary_log'] = np.log1p(cluster_data['monetary'])
    cluster_data['frequency_log'] = np.log1p(cluster_data['frequency'])
    cluster_data['recency_log'] = np.log1p(cluster_data['recency'])

    # Scale
    scaler = StandardScaler()
    cluster_scaled = scaler.fit_transform(
        cluster_data[['recency_log', 'frequency_log', 'monetary_log']]
    )

    # Find optimal clusters
    inertia = []
    silhouette_scores = []
    K = range(2, 8)

    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(cluster_scaled)
        inertia.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(cluster_scaled, kmeans.labels_))

    # Choose optimal k (4)
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    rfm['cluster'] = kmeans.fit_predict(cluster_scaled)

    return rfm, optimal_k, inertia, silhouette_scores


def apply_chart_style(fig, height=400):
    """Apply common black dashboard styling."""

    fig.update_layout(
        height=height,

        # Black background
        template="plotly_dark",
        plot_bgcolor="#0a0a0a",
        paper_bgcolor="#000000",

        # White text
        font=dict(
            color="white",
            size=12
        ),

        # Center title
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        margin=dict(
            l=50,
            r=50,
            t=70,
            b=50
        )
    )

    return fig


# =========================================================
# 1. CUSTOMER SEGMENT DISTRIBUTION
# =========================================================

def create_segment_chart(rfm):
    """Customer Segment Distribution - Donut Chart."""

    if rfm is None or rfm.empty or "segment" not in rfm.columns:
        fig = go.Figure()

        fig.add_annotation(
            text="No customer segment data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color="white"
            )
        )

        return apply_chart_style(fig, 400)

    segment_dist = (
        rfm["segment"]
        .value_counts()
    )

    colors = {
        "Champions": "#34d399",
        "Loyal Customers": "#667eea",
        "Potential Loyalists": "#f59e0b",
        "Recent Customers": "#60a5fa",
        "Promising": "#a78bfa",
        "Need Attention": "#f87171",
        "At Risk": "#fb923c",
        "Lost": "#9ca3af"
    }

    fig = px.pie(
        values=segment_dist.values,
        names=segment_dist.index,
        title="Customer Segment Distribution",
        hole=0.45,
        color=segment_dist.index,
        color_discrete_map=colors
    )

    fig = apply_chart_style(fig, 400)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                color="white"
            )
        )
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(
            color="white",
            size=11
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Customers: %{value:,}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    return fig


# =========================================================
# 2. RFM 3D SCATTER
# =========================================================

def create_rfm_scatter(rfm):
    """RFM 3D Visualization."""

    if rfm is None or rfm.empty:
        fig = go.Figure()

        fig.add_annotation(
            text="No RFM data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color="white"
            )
        )

        return apply_chart_style(fig, 450)

    colors = {
        "Champions": "#34d399",
        "Loyal Customers": "#667eea",
        "Potential Loyalists": "#f59e0b",
        "Recent Customers": "#60a5fa",
        "Promising": "#a78bfa",
        "Need Attention": "#f87171",
        "At Risk": "#fb923c",
        "Lost": "#9ca3af"
    }

    fig = px.scatter_3d(
        rfm,
        x="recency",
        y="frequency",
        z="monetary",
        color="segment",

        title="RFM 3D Visualization",

        labels={
            "recency": "Recency (Days)",
            "frequency": "Frequency",
            "monetary": "Monetary (₹)"
        },

        color_discrete_map=colors,

        opacity=0.75
    )

    fig = apply_chart_style(fig, 500)

    fig.update_layout(
        scene=dict(
            bgcolor="#0a0a0a",

            xaxis=dict(
                title="Recency (Days)",
                color="white",
                gridcolor="rgba(255,255,255,0.08)"
            ),

            yaxis=dict(
                title="Frequency",
                color="white",
                gridcolor="rgba(255,255,255,0.08)"
            ),

            zaxis=dict(
                title="Monetary (₹)",
                color="white",
                gridcolor="rgba(255,255,255,0.08)"
            )
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                color="white"
            )
        )
    )

    return fig


# =========================================================
# 3. CUSTOMER CLUSTER DISTRIBUTION
# =========================================================

def create_cluster_chart(rfm):
    """Customer Cluster Distribution - Bar Chart."""

    if rfm is None or rfm.empty or "cluster" not in rfm.columns:
        fig = go.Figure()

        fig.add_annotation(
            text="No cluster data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color="white"
            )
        )

        return apply_chart_style(fig, 400)

    cluster_counts = (
        rfm["cluster"]
        .value_counts()
        .sort_index()
    )

    df = cluster_counts.reset_index()

    df.columns = [
        "cluster",
        "count"
    ]

    fig = px.bar(
        df,
        x="cluster",
        y="count",

        title="Customer Cluster Distribution",

        labels={
            "cluster": "Cluster",
            "count": "Number of Customers"
        },

        color="count",
        color_continuous_scale=[
            "#312e81",
            "#667eea",
            "#34d399"
        ]
    )

    fig = apply_chart_style(fig, 400)

    fig.update_layout(
        showlegend=False
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.05)",
        color="white"
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.05)",
        color="white"
    )

    fig.update_traces(
        texttemplate="%{y}",
        textposition="outside",
        textfont=dict(
            color="white",
            size=12
        )
    )

    return fig


# =========================================================
# 4. CLUSTER RADAR
# =========================================================

def create_cluster_radar(rfm):
    """Cluster Characteristics - Radar Chart."""

    if rfm is None or rfm.empty:
        fig = go.Figure()

        fig.add_annotation(
            text="No cluster data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color="white"
            )
        )

        return apply_chart_style(fig, 450)

    cluster_avg = (
        rfm
        .groupby("cluster")
        .agg({
            "recency": "mean",
            "frequency": "mean",
            "monetary": "mean"
        })
        .reset_index()
    )

    # -----------------------------------------
    # Normalize values
    # -----------------------------------------

    for col in [
        "recency",
        "frequency",
        "monetary"
    ]:

        min_value = cluster_avg[col].min()
        max_value = cluster_avg[col].max()

        if max_value == min_value:
            cluster_avg[f"{col}_norm"] = 0.5
        else:
            cluster_avg[f"{col}_norm"] = (
                cluster_avg[col] - min_value
            ) / (
                max_value - min_value
            )

    fig = go.Figure()

    colors = [
        "#667eea",
        "#f59e0b",
        "#34d399",
        "#f87171",
        "#a78bfa",
        "#60a5fa"
    ]

    for i, row in cluster_avg.iterrows():

        color = colors[
            i % len(colors)
        ]

        fig.add_trace(
            go.Scatterpolar(
                r=[
                    row["recency_norm"],
                    row["frequency_norm"],
                    row["monetary_norm"]
                ],

                theta=[
                    "Recency",
                    "Frequency",
                    "Monetary"
                ],

                fill="toself",

                name=f"Cluster {int(row['cluster'])}",

                line=dict(
                    color=color,
                    width=2
                ),

                fillcolor=color.replace(
                    "#",
                    "rgba("
                ) if False else None
            )
        )

    fig = apply_chart_style(fig, 450)

    fig.update_layout(

        polar=dict(

            bgcolor="#0a0a0a",

            radialaxis=dict(
                visible=True,
                range=[0, 1],
                color="white",
                gridcolor="rgba(255,255,255,0.12)",
                tickfont=dict(
                    color="white"
                )
            ),

            angularaxis=dict(
                color="white",
                gridcolor="rgba(255,255,255,0.12)",
                tickfont=dict(
                    color="white"
                )
            )
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(
                color="white"
            )
        )
    )

    return fig