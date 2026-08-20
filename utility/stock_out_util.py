import plotly.express as px
from pygments.lexers import go
import streamlit as st

from app_pages.executive_dashboard import create_empty_figure


def calculate_stockout_risk(row):
    """Calculate stockout risk for a single SKU"""

    daily_avg = row['units_sold'] / 30 if 30 > 0 else 0
    if daily_avg == 0:
        return 'LOW', 0

    lead_time_demand = daily_avg * row['reorder_point']
    stock_cover = row['stock_on_hand'] / lead_time_demand if lead_time_demand > 0 else 0

    if stock_cover <= 0.3:
        return 'HIGH', stock_cover
    elif stock_cover <= 0.6:
        return 'MEDIUM', stock_cover
    elif stock_cover <= 1.0:
        return 'LOW', stock_cover
    else:
        return 'NONE', stock_cover


def calculate_risk_metrics(risk_analysis):
    """Calculate risk metrics"""

    total_skus = len(risk_analysis)
    high_risk = len(risk_analysis[risk_analysis['stockout_risk'] == 'HIGH'])
    medium_risk = len(risk_analysis[risk_analysis['stockout_risk'] == 'MEDIUM'])
    low_risk = len(risk_analysis[risk_analysis['stockout_risk'] == 'LOW'])
    none_risk = len(risk_analysis[risk_analysis['stockout_risk'] == 'NONE'])
    high_risk_value = risk_analysis[risk_analysis['stockout_risk'] == 'HIGH']['stock_value'].sum()

    return {
        'total_skus': total_skus,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'none_risk': none_risk,
        'high_risk_value': high_risk_value,
        'avg_stock_cover': risk_analysis['stock_cover'].mean()
    }


def create_risk_distribution_chart(risk_analysis):
    """1. Sunburst Chart - Risk Distribution by Category"""

    # ============================================
    # SAFETY CHECK
    # ============================================

    if (
        risk_analysis is None
        or risk_analysis.empty
        or 'category' not in risk_analysis.columns
        or 'stockout_risk' not in risk_analysis.columns
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Risk distribution data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=450,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="Stockout Risk Distribution by Category",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # COUNT RISK LEVELS BY CATEGORY
    # ============================================

    risk_by_cat = (
        risk_analysis
        .groupby(["category", "stockout_risk"])
        .size()
        .reset_index(name="count")
    )

    risk_by_cat.columns = [
        "category",
        "risk_level",
        "count"
    ]

    # ============================================
    # SUNBURST
    # ============================================

    fig = px.sunburst(
        risk_by_cat,
        path=["risk_level", "category"],
        values="count",
        color="risk_level",

        color_discrete_map={
            "HIGH": "#ef4444",
            "MEDIUM": "#f59e0b",
            "LOW": "#fcd34d",
            "NONE": "#34d399"
        },

        hover_data={
            "count": True
        }
    )

    # ============================================
    # LAYOUT
    # ============================================

    fig.update_layout(

        height=450,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Stockout Risk Distribution by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # ============================================
    # SUNBURST TEXT
    # ============================================

    fig.update_traces(
        textinfo="label+percent entry",
        insidetextfont=dict(
            color="white",
            size=12
        ),

        marker=dict(
            line=dict(
                color="#0e1117",
                width=2
            )
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "Count: %{value:,}<br>"
            "Percentage: %{percentEntry:.1%}"
            "<extra></extra>"
        )
    )

    return fig


def create_high_risk_category_chart(risk_analysis):
    """2. Horizontal Bar - High Risk SKUs by Category"""

    # ============================================
    # SAFETY CHECK
    # ============================================

    if (
        risk_analysis is None
        or risk_analysis.empty
        or "stockout_risk" not in risk_analysis.columns
        or "category" not in risk_analysis.columns
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="High risk category data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="High Risk SKUs by Category (Top 10)",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # FILTER HIGH RISK
    # ============================================

    high_risk = risk_analysis[
        risk_analysis["stockout_risk"].astype(str).str.upper() == "HIGH"
    ]

    high_risk_cat = (
        high_risk
        .groupby("category")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    # ============================================
    # NO HIGH-RISK DATA
    # ============================================

    if high_risk_cat.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No HIGH risk SKUs found",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="High Risk SKUs by Category (Top 10)",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # DATAFRAME
    # ============================================

    df = high_risk_cat.reset_index()

    df.columns = [
        "category",
        "count"
    ]

    # ============================================
    # BAR CHART
    # ============================================

    fig = px.bar(
        df,
        x="count",
        y="category",
        orientation="h",
        color="count",
        color_continuous_scale="Reds",
        labels={
            "count": "Number of SKUs",
            "category": ""
        }
    )

    # ============================================
    # LAYOUT
    # ============================================

    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="High Risk SKUs by Category (Top 10)",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Number of SKUs",
        yaxis_title="",

        showlegend=False,

        margin=dict(
            l=60,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        ),

        coloraxis_showscale=False
    )

    # ============================================
    # X AXIS
    # ============================================

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",
        tickfont=dict(
            color="white",
            size=11
        ),
        title_font=dict(
            color="white",
            size=13
        ),
        tickformat=",d"
    )

    # ============================================
    # Y AXIS
    # ============================================

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",
        tickfont=dict(
            color="white",
            size=11
        ),
        title_font=dict(
            color="white",
            size=13
        ),
        autorange="reversed"
    )

    # ============================================
    # VALUE LABELS
    # ============================================

    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        textfont=dict(
            color="white",
            size=11
        ),

        marker=dict(
            line=dict(
                color="white",
                width=0.5
            )
        ),

        hovertemplate=(
            "<b>%{y}</b><br>"
            "High Risk SKUs: %{x:,.0f}"
            "<extra></extra>"
        )
    )

    return fig

def create_stock_cover_histogram(risk_analysis):
    """3. Histogram with Threshold Lines - Stock Cover Distribution"""

    # ============================================
    # SAFETY CHECK
    # ============================================

    if (
        risk_analysis is None
        or risk_analysis.empty
        or "stock_cover" not in risk_analysis.columns
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Stock cover data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="Stock Cover Distribution",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # CLEAN DATA
    # ============================================

    df = risk_analysis[
        risk_analysis["stock_cover"].notna()
        & (risk_analysis["stock_cover"] < 5)
        & (risk_analysis["stock_cover"] >= 0)
    ].copy()

    # ============================================
    # NO DATA AFTER FILTER
    # ============================================

    if df.empty:
        fig = go.Figure()

        fig.add_annotation(
            text="No stock cover data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="Stock Cover Distribution",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # HISTOGRAM
    # ============================================

    fig = px.histogram(
        df,
        x="stock_cover",
        nbins=40,
        color_discrete_sequence=["#f59e0b"],
        labels={
            "stock_cover": "Stock Cover (Days)",
            "count": "Number of SKUs"
        }
    )

    # ============================================
    # HIGH-RISK THRESHOLD
    # ============================================

    fig.add_vline(
        x=0.3,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,

        annotation_text="High Risk (0.3 days)",

        annotation_position="top right",

        annotation_font=dict(
            color="#ef4444",
            size=11
        )
    )

    # ============================================
    # MEDIUM-RISK THRESHOLD
    # ============================================

    fig.add_vline(
        x=0.6,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=2,

        annotation_text="Medium Risk (0.6 days)",

        annotation_position="top right",

        annotation_font=dict(
            color="#f59e0b",
            size=11
        )
    )

    # ============================================
    # LAYOUT
    # ============================================

    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Stock Cover Distribution",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Stock Cover (Days)",
        yaxis_title="Number of SKUs",

        showlegend=False,

        margin=dict(
            l=55,
            r=45,
            t=75,
            b=55
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # ============================================
    # X AXIS
    # ============================================

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=13
        ),

        tickformat=".1f"
    )

    # ============================================
    # Y AXIS
    # ============================================

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=13
        ),

        tickformat=",d"
    )

    # ============================================
    # HISTOGRAM STYLING
    # ============================================

    fig.update_traces(
        marker=dict(
            color="#f59e0b",
            line=dict(
                color="white",
                width=0.5
            )
        ),

        opacity=0.9,

        hovertemplate=(
            "<b>Stock Cover: %{x:.2f} days</b><br>"
            "SKUs: %{y:,}"
            "<extra></extra>"
        )
    )

    return fig


def create_risk_value_chart(risk_analysis):
    """4. Treemap - At-Risk Inventory Value by Category"""

    # ============================================
    # SAFETY CHECK
    # ============================================

    required_columns = [
        "stockout_risk",
        "category",
        "stock_value"
    ]

    if (
        risk_analysis is None
        or risk_analysis.empty
        or not all(col in risk_analysis.columns for col in required_columns)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="At-risk inventory data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="At-Risk Inventory Value by Category",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # FILTER HIGH-RISK SKUs
    # ============================================

    high_risk = risk_analysis[
        risk_analysis["stockout_risk"]
        .astype(str)
        .str.upper()
        .eq("HIGH")
    ].copy()

    # ============================================
    # NO HIGH-RISK DATA
    # ============================================

    if high_risk.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No HIGH risk SKUs found",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="At-Risk Inventory Value by Category",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),
            font=dict(
                size=12,
                color="white"
            )
        )

        return fig

    # ============================================
    # AGGREGATE INVENTORY VALUE
    # ============================================

    risk_value = (
        high_risk
        .groupby("category")["stock_value"]
        .sum()
        .reset_index()
    )

    # Remove invalid / zero values
    risk_value = risk_value[
        risk_value["stock_value"].notna()
        & (risk_value["stock_value"] > 0)
    ]

    if risk_value.empty:
        fig = go.Figure()

        fig.add_annotation(
            text="No at-risk inventory value available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            title=dict(
                text="At-Risk Inventory Value by Category",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            )
        )

        return fig

    # ============================================
    # TREEMAP
    # ============================================

    fig = px.treemap(
        risk_value,
        path=["category"],
        values="stock_value",
        color="stock_value",
        color_continuous_scale="Reds",
        hover_data={
            "stock_value": ":,.0f"
        }
    )

    # ============================================
    # LAYOUT
    # ============================================

    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="At-Risk Inventory Value by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # ============================================
    # TREEMAP STYLING
    # ============================================

    fig.update_traces(

        textinfo="label+value",

        textfont=dict(
            color="white",
            size=13
        ),

        marker=dict(
            line=dict(
                color="#0e1117",
                width=2
            )
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "At-Risk Value: ₹%{value:,.0f}"
            "<extra></extra>"
        )
    )

    return fig

def create_risk_scatter_chart(risk_analysis):
    """5. Scatter Plot - Risk Score vs Stock Cover"""

    if risk_analysis is None or risk_analysis.empty:
        return create_empty_figure("No risk analysis data available")

    # Work on a copy so the original DataFrame is not modified
    df = risk_analysis.copy()

    # Convert risk levels to numeric scores
    risk_map = {
        'HIGH': 3,
        'MEDIUM': 2,
        'LOW': 1,
        'NONE': 0
    }

    df['risk_score'] = (
        df['stockout_risk']
        .map(risk_map)
        .fillna(0)
    )

    # Remove invalid stock cover values
    df = df.dropna(subset=['stock_cover'])

    if df.empty:
        return create_empty_figure("No valid stock cover data available")

    # Make sure stock cover is non-negative
    df = df[df['stock_cover'] >= 0]

    # --------------------------------------------------
    # Scatter Plot
    # --------------------------------------------------

    fig = px.scatter(
        df,
        x='stock_cover',
        y='risk_score',
        title='Risk Level vs Stock Cover',
        labels={
            'stock_cover': 'Stock Cover (Days)',
            'risk_score': 'Risk Score'
        },
        color='stockout_risk',
        color_discrete_map={
            'HIGH': '#ef4444',
            'MEDIUM': '#f59e0b',
            'LOW': '#fcd34d',
            'NONE': '#34d399'
        },
        size='stock_value' if 'stock_value' in df.columns else None,
        size_max=30,
        hover_data=[
            col for col in ['sku_id', 'category', 'stock_value']
            if col in df.columns
        ]
    )

    # --------------------------------------------------
    # Threshold Lines
    # --------------------------------------------------

    fig.add_vline(
        x=0.3,
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text="High Risk",
        annotation_position="top right",
        annotation_font=dict(
            color="#ef4444",
            size=10
        )
    )

    fig.add_vline(
        x=0.6,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=1.5,
        annotation_text="Medium Risk",
        annotation_position="top right",
        annotation_font=dict(
            color="#f59e0b",
            size=10
        )
    )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    max_cover = df['stock_cover'].max()

    fig.update_layout(
        height=400,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Risk Level vs Stock Cover',
            x=0.5,
            xanchor='center',
            y=0.95,
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Stock Cover (Days)',
        yaxis_title='Risk Level',

        margin=dict(
            l=60,
            r=40,
            t=75,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        ),

        hovermode='closest',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(
                color='white',
                size=10
            ),
            bgcolor='rgba(0,0,0,0)'
        )
    )

    # --------------------------------------------------
    # X Axis
    # --------------------------------------------------

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zerolinecolor='rgba(255,255,255,0.15)',
        tickfont=dict(
            color='white',
            size=10
        ),
        title_font=dict(
            color='white',
            size=12
        ),
        range=[
            0,
            max_cover * 1.1 if max_cover > 0 else 1
        ]
    )

    # --------------------------------------------------
    # Y Axis
    # --------------------------------------------------

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zerolinecolor='rgba(255,255,255,0.15)',

        tickvals=[0, 1, 2, 3],

        ticktext=[
            'NONE',
            'LOW',
            'MEDIUM',
            'HIGH'
        ],

        tickfont=dict(
            color='white',
            size=10
        ),

        title_font=dict(
            color='white',
            size=12
        ),

        range=[-0.2, 3.2]
    )

    # --------------------------------------------------
    # Marker Styling
    # --------------------------------------------------

    fig.update_traces(
        marker=dict(
            opacity=0.85,
            line=dict(
                color='white',
                width=0.5
            )
        )
    )

    return fig

def create_risk_gauge(risk_metrics):
    """6. Gauge Chart - Overall Stockout Risk"""

    # -----------------------------------------
    # Safe data access
    # -----------------------------------------
    if not isinstance(risk_metrics, dict):
        return create_empty_figure("Risk metrics not available")

    total_skus = risk_metrics.get("total_skus", 0)
    high_risk = risk_metrics.get("high_risk", 0)

    high_risk_pct = (
        (high_risk / total_skus) * 100
        if total_skus > 0
        else 0
    )

    # Keep value inside gauge range
    high_risk_pct = min(max(high_risk_pct, 0), 50)

    # -----------------------------------------
    # Gauge color
    # -----------------------------------------
    if high_risk_pct > 20:
        bar_color = "#ef4444"       # Red
    elif high_risk_pct > 10:
        bar_color = "#f59e0b"       # Orange
    else:
        bar_color = "#34d399"       # Green

    # -----------------------------------------
    # Create Gauge
    # -----------------------------------------
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",

            value=high_risk_pct,

            number=dict(
                suffix="%",
                font=dict(
                    color="white",
                    size=32
                )
            ),

            delta=dict(
                reference=15,
                suffix="%",
                increasing=dict(
                    color="#ef4444"
                ),
                decreasing=dict(
                    color="#34d399"
                ),
                font=dict(
                    color="white",
                    size=14
                )
            ),

            title=dict(
                text="High Risk SKUs (%)",
                font=dict(
                    color="white",
                    size=18
                )
            ),

            domain=dict(
                x=[0, 1],
                y=[0, 1]
            ),

            gauge=dict(

                axis=dict(
                    range=[0, 50],
                    tickmode="array",
                    tickvals=[0, 10, 20, 30, 40, 50],
                    ticktext=[
                        "0%",
                        "10%",
                        "20%",
                        "30%",
                        "40%",
                        "50%"
                    ],
                    tickfont=dict(
                        color="white",
                        size=10
                    ),
                    tickcolor="white"
                ),

                bar=dict(
                    color=bar_color,
                    thickness=0.7
                ),

                bgcolor="#1a1f2b",

                borderwidth=1,
                bordercolor="#444444",

                steps=[
                    {
                        "range": [0, 10],
                        "color": "rgba(52, 211, 153, 0.20)"
                    },
                    {
                        "range": [10, 20],
                        "color": "rgba(245, 158, 11, 0.20)"
                    },
                    {
                        "range": [20, 50],
                        "color": "rgba(239, 68, 68, 0.20)"
                    }
                ],

                threshold=dict(
                    line=dict(
                        color="white",
                        width=3
                    ),
                    thickness=0.75,
                    value=15
                )
            )
        )
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(
        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Overall Stockout Risk",
            x=0.5,
            xanchor="center",
            y=0.98,
            font=dict(
                size=18,
                color="white"
            )
        ),

        margin=dict(
            l=30,
            r=30,
            t=70,
            b=40
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # -----------------------------------------
    # Additional information
    # -----------------------------------------
    fig.add_annotation(
        text=f"{high_risk:,} of {total_skus:,} SKUs at high risk",
        x=0.5,
        y=0.08,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            color="white",
            size=13
        )
    )

    return fig