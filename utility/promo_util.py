from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def process_promotion_data(daily_sales, promotions):
    """Process promotion data and calculate metrics"""

    # Check if promotion data exists in sales
    if 'promo_id' in daily_sales.columns:
        promo_sales = daily_sales[daily_sales['promo_id'].notna()]
        non_promo_sales = daily_sales[daily_sales['promo_id'].isna()]
    else:
        promo_sales = pd.DataFrame()
        non_promo_sales = daily_sales

    # Check if promotions file has data
    has_promo_file = len(promotions) > 0

    return promo_sales, non_promo_sales, has_promo_file


def calculate_promotion_metrics(promo_sales, non_promo_sales, daily_sales, promotions):
    """Calculate promotion metrics"""

    total_revenue = daily_sales['revenue'].sum()
    total_orders = len(daily_sales)

    promo_revenue = promo_sales['revenue'].sum() if len(promo_sales) > 0 else 0
    non_promo_revenue = non_promo_sales['revenue'].sum() if len(non_promo_sales) > 0 else 0

    promo_orders = len(promo_sales) if len(promo_sales) > 0 else 0
    non_promo_orders = len(non_promo_sales) if len(non_promo_sales) > 0 else 0

    promo_avg = promo_sales['revenue'].mean() if promo_orders > 0 else 0
    non_promo_avg = non_promo_sales['revenue'].mean() if non_promo_orders > 0 else 0

    promo_share = (promo_revenue / total_revenue * 100) if total_revenue > 0 else 0

    # Lift calculation
    lift = ((promo_avg - non_promo_avg) / non_promo_avg * 100) if non_promo_avg > 0 else 0

    # Promotion types distribution
    if len(promotions) > 0 and 'promo_type' in promotions.columns:
        promo_types = promotions['promo_type'].value_counts().to_dict()
    else:
        promo_types = {}

    # Active promotions
    today = datetime.now().date()
    if len(promotions) > 0 and 'start_date' in promotions.columns and 'end_date' in promotions.columns:
        promotions['start_date'] = pd.to_datetime(promotions['start_date']).dt.date
        promotions['end_date'] = pd.to_datetime(promotions['end_date']).dt.date
        active_promos = len(promotions[(promotions['start_date'] <= today) & (promotions['end_date'] >= today)])
    else:
        active_promos = 0

    # Average discount
    if len(promotions) > 0 and 'discount_pct' in promotions.columns:
        avg_discount = promotions['discount_pct'].mean()
    else:
        avg_discount = 0

    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'promo_revenue': promo_revenue,
        'non_promo_revenue': non_promo_revenue,
        'promo_orders': promo_orders,
        'non_promo_orders': non_promo_orders,
        'promo_avg': promo_avg,
        'non_promo_avg': non_promo_avg,
        'promo_share': promo_share,
        'lift': lift,
        'total_promotions': len(promotions),
        'active_promotions': active_promos,
        'avg_discount': avg_discount,
        'promo_types': promo_types
    }


def create_promo_revenue_chart(metrics):
    """1. Donut Chart - Promotion Revenue Share"""

    promo_revenue = metrics.get('promo_revenue', 0)
    non_promo_revenue = metrics.get('non_promo_revenue', 0)

    fig = go.Figure(
        go.Pie(
            labels=['Promotion', 'Non-Promotion'],
            values=[promo_revenue, non_promo_revenue],

            hole=0.48,

            marker=dict(
                colors=['#667eea', '#c4b5fd'],
                line=dict(
                    color='#0e1117',
                    width=2
                )
            ),

            textinfo='label+percent',
            textposition='inside',

            textfont=dict(
                color='white',
                size=12
            ),

            hovertemplate=(
                '<b>%{label}</b><br>'
                'Revenue: ₹%{value:,.0f}<br>'
                'Share: %{percent}<extra></extra>'
            )
        )
    )

    fig.update_layout(
        height=400,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Promotion Revenue Share',
            x=0.5,
            xanchor='center',
            y=0.95,
            yanchor='top',
            font=dict(
                size=18,
                color='white'
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=30
        ),

        font=dict(
            family='Arial',
            size=12,
            color='white'
        ),

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0,
            xanchor='center',
            x=0.5,

            font=dict(
                color='white',
                size=11
            ),

            bgcolor='rgba(0,0,0,0)'
        )
    )

    # Center text inside donut
    total_revenue = promo_revenue + non_promo_revenue

    fig.add_annotation(
        text=(
            f"<b>₹{total_revenue:,.0f}</b>"
            "<br><span style='font-size:11px'>Total Revenue</span>"
        ),
        x=0.5,
        y=0.5,
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(
            color='white',
            size=15
        )
    )

    return fig



def create_promo_type_chart(promotions):
    """2. Bar Chart - Promotion Type Distribution"""

    if promotions is None or len(promotions) == 0 or 'promo_type' not in promotions.columns:

        fig = go.Figure()

        fig.add_annotation(
            text='No promotion type data available',
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            showarrow=False,
            font=dict(
                size=16,
                color='white'
            )
        )

        fig.update_layout(
            height=400,
            template='plotly_dark',
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',

            title=dict(
                text='Promotion Type Distribution',
                x=0.5,
                xanchor='center',
                font=dict(
                    size=18,
                    color='white'
                )
            ),

            font=dict(
                color='white'
            )
        )

        return fig

    promo_types = (
        promotions['promo_type']
        .value_counts()
        .reset_index()
    )

    promo_types.columns = ['type', 'count']

    # Sort so largest appears at top
    promo_types = promo_types.sort_values(
        'count',
        ascending=True
    )

    fig = px.bar(
        promo_types,
        x='count',
        y='type',
        orientation='h',

        labels={
            'count': 'Number of Promotions',
            'type': 'Promotion Type'
        },

        color='count',

        color_continuous_scale=[
            '#4c1d95',
            '#6d28d9',
            '#8b5cf6',
            '#a78bfa',
            '#c4b5fd'
        ]
    )

    # Value labels
    fig.update_traces(
        texttemplate='%{x:,.0f}',
        textposition='outside',

        textfont=dict(
            color='white',
            size=10
        ),

        marker_line_color='white',
        marker_line_width=0.5,

        hovertemplate=(
            '<b>%{y}</b><br>'
            'Promotions: %{x:,.0f}'
            '<extra></extra>'
        )
    )

    fig.update_layout(
        height=400,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Promotion Type Distribution',
            x=0.5,
            xanchor='center',
            y=0.95,
            yanchor='top',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Number of Promotions',
        yaxis_title='',

        showlegend=False,

        margin=dict(
            l=70,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            family='Arial',
            size=12,
            color='white'
        ),

        coloraxis_showscale=False
    )

    # X axis
    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zeroline=False,

        tickfont=dict(
            color='white',
            size=10
        ),

        title_font=dict(
            color='white',
            size=12
        )
    )

    # Y axis
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zeroline=False,
        autorange=True,

        tickfont=dict(
            color='white',
            size=10
        ),

        title_font=dict(
            color='white',
            size=12
        )
    )

    return fig


def create_promo_target_chart(promotions):
    """3. Bar Chart - Promotion Target Distribution"""

    if (
        promotions is None
        or len(promotions) == 0
        or 'target_type' not in promotions.columns
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="No target data available",
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
                text="Promotion Target Distribution",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),

            font=dict(
                color="white"
            )
        )

        return fig

    target_types = (
        promotions["target_type"]
        .value_counts()
        .reset_index()
    )

    target_types.columns = ["target", "count"]

    # Largest at the top
    target_types = target_types.sort_values(
        "count",
        ascending=True
    )

    fig = px.bar(
        target_types,
        x="count",
        y="target",
        orientation="h",

        labels={
            "count": "Number of Promotions",
            "target": "Target Type"
        },

        color="count",

        color_continuous_scale=[
            "#1e3a8a",
            "#2563eb",
            "#3b82f6",
            "#60a5fa",
            "#93c5fd"
        ]
    )

    # Value labels
    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",

        textfont=dict(
            color="white",
            size=10
        ),

        marker_line_color="white",
        marker_line_width=0.5,

        hovertemplate=(
            "<b>%{y}</b><br>"
            "Promotions: %{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Promotion Target Distribution",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Number of Promotions",
        yaxis_title="",

        showlegend=False,

        margin=dict(
            l=70,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            family="Arial",
            size=12,
            color="white"
        ),

        coloraxis_showscale=False
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        tickfont=dict(
            color="white",
            size=10
        ),
        title_font=dict(
            color="white",
            size=12
        )
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        tickfont=dict(
            color="white",
            size=10
        ),
        title_font=dict(
            color="white",
            size=12
        )
    )

    return fig


def create_promo_avg_order_chart(metrics):
    """4. Bar Chart - Average Order Value Comparison"""

    promo_avg = metrics.get("promo_avg", 0)
    non_promo_avg = metrics.get("non_promo_avg", 0)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[
                "With Promotion",
                "Without Promotion"
            ],

            y=[
                promo_avg,
                non_promo_avg
            ],

            marker=dict(
                color=[
                    "#667eea",
                    "#c4b5fd"
                ],

                line=dict(
                    color="white",
                    width=0.5
                )
            ),

            text=[
                f"₹{promo_avg:,.2f}",
                f"₹{non_promo_avg:,.2f}"
            ],

            textposition="outside",

            textfont=dict(
                color="white",
                size=11
            ),

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Order Value: ₹%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Average Order Value: Promotion vs Non-Promotion",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="",
        yaxis_title="Avg Order Value (₹)",

        showlegend=False,

        margin=dict(
            l=60,
            r=40,
            t=70,
            b=60
        ),

        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=12
        )
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,

        tickprefix="₹",
        tickformat=",.0f",

        tickfont=dict(
            color="white",
            size=10
        ),

        title_font=dict(
            color="white",
            size=12
        )
    )

    return fig

def create_promo_discount_distribution(promotions):
    """5. Histogram - Discount Distribution"""

    if len(promotions) == 0 or 'discount_pct' not in promotions.columns:
        fig = go.Figure()

        fig.add_annotation(
            text="No discount data available",
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
                text="Discount Distribution",
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

    # Remove missing values
    discount_data = promotions["discount_pct"].dropna()

    # Histogram
    fig = px.histogram(
        x=discount_data,
        nbins=20,
        labels={
            "x": "Discount (%)",
            "y": "Number of Promotions"
        },
        color_discrete_sequence=["#f59e0b"]
    )

    # Mean discount
    mean_discount = discount_data.mean()

    fig.add_vline(
        x=mean_discount,
        line_dash="dash",
        line_color="#34d399",
        line_width=2,

        annotation_text=f"Avg: {mean_discount:.1f}%",

        annotation_position="top right",

        annotation_font=dict(
            color="white",
            size=11
        ),

        annotation_bgcolor="#0e1117"
    )

    # Layout
    fig.update_layout(
        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Discount Distribution",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Discount (%)",
        yaxis_title="Number of Promotions",

        showlegend=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # X-axis
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.05)",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        tickformat=".0f",
        zeroline=False
    )

    # Y-axis
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.05)",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        zeroline=False
    )

    # Histogram styling
    fig.update_traces(
        marker_line_color="white",
        marker_line_width=0.5,
        opacity=0.9,
        hovertemplate=(
            "<b>Discount: %{x}</b><br>"
            "Promotions: %{y}<extra></extra>"
        )
    )

    return fig

def create_promo_timeline(promotions):
    """6. Timeline - Promotions Over Time"""

    if len(promotions) == 0 or 'start_date' not in promotions.columns:
        fig = go.Figure()

        fig.add_annotation(
            text="No timeline data available",
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
                text="Promotions Over Time",
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

    # Work on a copy so the original dataframe is not modified
    promotions = promotions.copy()

    # Convert dates
    promotions["start_date"] = pd.to_datetime(
        promotions["start_date"],
        errors="coerce"
    )

    if "end_date" in promotions.columns:
        promotions["end_date"] = pd.to_datetime(
            promotions["end_date"],
            errors="coerce"
        )

    # Remove invalid dates
    promotions = promotions.dropna(subset=["start_date"])

    if len(promotions) == 0:
        return create_empty_figure("No valid promotion dates available")

    # Group promotions by month
    promotions["month"] = promotions["start_date"].dt.to_period("M")

    monthly_promos = (
        promotions
        .groupby("month")
        .size()
        .reset_index(name="count")
    )

    monthly_promos["month"] = monthly_promos["month"].astype(str)

    # Create bar chart
    fig = px.bar(
        monthly_promos,
        x="month",
        y="count",
        color="count",
        color_continuous_scale="Greens",
        labels={
            "count": "Number of Promotions",
            "month": "Month"
        }
    )

    # Layout
    fig.update_layout(
        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Promotions Over Time",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Month",
        yaxis_title="Number of Promotions",

        showlegend=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=70
        ),

        font=dict(
            size=12,
            color="white"
        ),

        coloraxis_showscale=False
    )

    # X-axis
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.05)",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        tickangle=45
    )

    # Y-axis
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.05)",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        tickformat=",d"
    )

    # Bar styling + labels
    fig.update_traces(
        texttemplate="%{y}",
        textposition="outside",
        textfont=dict(
            color="white",
            size=10
        ),
        marker_line_color="white",
        marker_line_width=0.5,

        hovertemplate=(
            "<b>%{x}</b><br>"
            "Promotions: %{y}<extra></extra>"
        )
    )

    return fig