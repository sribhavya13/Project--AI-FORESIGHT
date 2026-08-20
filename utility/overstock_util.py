import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_pages.executive_dashboard import create_empty_figure

@st.cache_data
def calculate_overstock_risk(row):
    """Calculate overstock risk for a single SKU"""

    daily_avg = row['units_sold'] / 30 if 30 > 0 else 0
    if daily_avg == 0:
        return 'HIGH', 0

    weeks_of_stock = row['stock_on_hand'] / (daily_avg * 7) if daily_avg > 0 else float('inf')

    if weeks_of_stock > 12:
        return 'HIGH', weeks_of_stock
    elif weeks_of_stock > 8:
        return 'MEDIUM', weeks_of_stock
    elif weeks_of_stock > 5:
        return 'LOW', weeks_of_stock
    else:
        return 'NONE', weeks_of_stock

@st.cache_data
def calculate_overstock_metrics(risk_analysis):
    """Calculate overstock metrics"""

    total_skus = len(risk_analysis)
    high_overstock = len(risk_analysis[risk_analysis['overstock_risk'] == 'HIGH'])
    medium_overstock = len(risk_analysis[risk_analysis['overstock_risk'] == 'MEDIUM'])
    low_overstock = len(risk_analysis[risk_analysis['overstock_risk'] == 'LOW'])
    none_overstock = len(risk_analysis[risk_analysis['overstock_risk'] == 'NONE'])
    high_overstock_value = risk_analysis[risk_analysis['overstock_risk'] == 'HIGH']['stock_value'].sum()

    # Zero sales SKUs (dead stock)
    zero_sales = len(risk_analysis[risk_analysis['units_sold'] == 0])

    # Top overstock category
    high_overstock_skus = risk_analysis[risk_analysis['overstock_risk'] == 'HIGH']
    if len(high_overstock_skus) > 0:
        top_category = high_overstock_skus.groupby('category').size().idxmax()
    else:
        top_category = 'N/A'

    return {
        'total_skus': total_skus,
        'high_overstock': high_overstock,
        'medium_overstock': medium_overstock,
        'low_overstock': low_overstock,
        'none_overstock': none_overstock,
        'high_overstock_value': high_overstock_value,
        'zero_sales': zero_sales,
        'avg_weeks_of_stock': risk_analysis['weeks_of_stock'].mean(),
        'top_category': top_category
    }

@st.cache_data
def create_overstock_distribution_chart(risk_analysis):
    """1. Sunburst Chart - Overstock Distribution by Category"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if risk_analysis is None or risk_analysis.empty:
        return create_empty_figure(
            "No overstock risk data available"
        )

    required_columns = ["category", "overstock_risk"]

    if not all(col in risk_analysis.columns for col in required_columns):
        return create_empty_figure(
            "Overstock data not available"
        )

    # -----------------------------------------
    # Aggregate overstock risk
    # -----------------------------------------
    overstock_by_cat = (
        risk_analysis
        .dropna(subset=["category", "overstock_risk"])
        .groupby(["category", "overstock_risk"])
        .size()
        .reset_index(name="count")
    )

    if overstock_by_cat.empty:
        return create_empty_figure(
            "No overstock risk data available"
        )

    overstock_by_cat.columns = [
        "category",
        "risk_level",
        "count"
    ]

    # -----------------------------------------
    # Sunburst
    # -----------------------------------------
    fig = px.sunburst(
        overstock_by_cat,
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

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(
        height=450,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Overstock Risk Distribution by Category",
            x=0.5,
            xanchor="center",
            y=0.96,
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
        ),

        showlegend=False
    )

    # -----------------------------------------
    # Sunburst styling
    # -----------------------------------------
    fig.update_traces(
        textinfo="label+value",

        insidetextfont=dict(
            color="white",
            size=11
        ),

        outsidetextfont=dict(
            color="white",
            size=11
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "SKUs: %{value:,}"
            "<extra></extra>"
        ),

        marker=dict(
            line=dict(
                color="#0e1117",
                width=1.5
            )
        )
    )

    return fig

@st.cache_data
def create_high_overstock_category_chart(risk_analysis):
    """2. Horizontal Bar - High Overstock SKUs by Category"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if risk_analysis is None or risk_analysis.empty:
        return create_empty_figure(
            "No overstock risk data available"
        )

    required_columns = ["category", "overstock_risk"]

    if not all(col in risk_analysis.columns for col in required_columns):
        return create_empty_figure(
            "Overstock data not available"
        )

    # -----------------------------------------
    # Filter HIGH overstock
    # -----------------------------------------
    high_overstock = risk_analysis[
        risk_analysis["overstock_risk"] == "HIGH"
    ]

    if high_overstock.empty:
        return create_empty_figure(
            "No high overstock SKUs found"
        )

    # -----------------------------------------
    # Top 10 categories
    # -----------------------------------------
    high_over_cat = (
        high_overstock
        .dropna(subset=["category"])
        .groupby("category")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    if high_over_cat.empty:
        return create_empty_figure(
            "No high overstock category data available"
        )

    df = high_over_cat.reset_index()
    df.columns = ["category", "count"]

    # -----------------------------------------
    # Create chart
    # -----------------------------------------
    fig = px.bar(
        df,
        x="count",
        y="category",
        orientation="h",
        labels={
            "count": "Number of SKUs",
            "category": ""
        },
        color="count",
        color_continuous_scale="Reds"
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
            text="High Overstock SKUs by Category (Top 10)",
            x=0.5,
            xanchor="center",
            y=0.96,
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Number of SKUs",
        yaxis_title="",

        showlegend=False,

        margin=dict(
            l=80,
            r=50,
            t=75,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        ),

        coloraxis_showscale=False
    )

    # -----------------------------------------
    # X Axis
    # -----------------------------------------
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",
        tickfont=dict(
            color="white",
            size=10
        ),
        title_font=dict(
            color="white",
            size=12
        ),
        dtick=1
    )

    # -----------------------------------------
    # Y Axis
    # -----------------------------------------
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        tickfont=dict(
            color="white",
            size=10
        ),
        title_font=dict(
            color="white",
            size=12
        ),
        autorange="reversed"
    )

    # -----------------------------------------
    # Bar styling + value labels
    # -----------------------------------------
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
            "High Overstock SKUs: %{x:,}"
            "<extra></extra>"
        )
    )

    return fig

@st.cache_data
def create_weeks_of_stock_histogram(risk_analysis):
    """3. Histogram - Weeks of Stock Distribution"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if risk_analysis is None or risk_analysis.empty:
        return create_empty_figure(
            "No stock coverage data available"
        )

    if "weeks_of_stock" not in risk_analysis.columns:
        return create_empty_figure(
            "Weeks of stock data not available"
        )

    # -----------------------------------------
    # Clean data
    # -----------------------------------------
    df = risk_analysis.copy()

    df["weeks_of_stock"] = pd.to_numeric(
        df["weeks_of_stock"],
        errors="coerce"
    )

    df = df.dropna(subset=["weeks_of_stock"])

    # Remove negative values and extreme values
    df = df[
        (df["weeks_of_stock"] >= 0) &
        (df["weeks_of_stock"] < 20)
    ]

    if df.empty:
        return create_empty_figure(
            "No valid weeks of stock data available"
        )

    # -----------------------------------------
    # Histogram
    # -----------------------------------------
    fig = px.histogram(
        df,
        x="weeks_of_stock",
        nbins=30,
        labels={
            "weeks_of_stock": "Weeks of Stock",
            "count": "Number of SKUs"
        },
        color_discrete_sequence=["#f59e0b"]
    )

    # -----------------------------------------
    # High Overstock Threshold
    # -----------------------------------------
    fig.add_vline(
        x=12,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,

        annotation_text="High Overstock (12w)",

        annotation_position="top right",

        annotation_font=dict(
            color="#ef4444",
            size=10
        )
    )

    # -----------------------------------------
    # Medium Overstock Threshold
    # -----------------------------------------
    fig.add_vline(
        x=8,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=2,

        annotation_text="Medium Overstock (8w)",

        annotation_position="top right",

        annotation_font=dict(
            color="#f59e0b",
            size=10
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
            text="Weeks of Stock Distribution",
            x=0.5,
            xanchor="center",
            y=0.96,

            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Weeks of Stock",
        yaxis_title="Number of SKUs",

        showlegend=False,

        margin=dict(
            l=60,
            r=40,
            t=75,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # -----------------------------------------
    # X Axis
    # -----------------------------------------
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",

        tickfont=dict(
            color="white",
            size=10
        ),

        title_font=dict(
            color="white",
            size=12
        ),

        dtick=2
    )

    # -----------------------------------------
    # Y Axis
    # -----------------------------------------
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.15)",

        tickfont=dict(
            color="white",
            size=10
        ),

        title_font=dict(
            color="white",
            size=12
        )
    )

    # -----------------------------------------
    # Histogram Styling
    # -----------------------------------------
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
            "Weeks of Stock: %{x:.1f}<br>"
            "SKUs: %{y:,}"
            "<extra></extra>"
        )
    )

    return fig

@st.cache_data
def create_overstock_value_chart(risk_analysis):
    """4. Treemap - Overstock Value by Category"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if risk_analysis is None or risk_analysis.empty:
        return create_empty_figure(
            "No overstock data available"
        )

    required_columns = [
        "category",
        "overstock_risk",
        "stock_value"
    ]

    if not all(
        col in risk_analysis.columns
        for col in required_columns
    ):
        return create_empty_figure(
            "Overstock value data not available"
        )

    # -----------------------------------------
    # Filter HIGH overstock
    # -----------------------------------------
    high_overstock = risk_analysis[
        risk_analysis["overstock_risk"] == "HIGH"
    ].copy()

    if high_overstock.empty:
        return create_empty_figure(
            "No high overstock SKUs found"
        )

    # -----------------------------------------
    # Clean stock value
    # -----------------------------------------
    high_overstock["stock_value"] = pd.to_numeric(
        high_overstock["stock_value"],
        errors="coerce"
    )

    high_overstock = high_overstock.dropna(
        subset=["category", "stock_value"]
    )

    high_overstock = high_overstock[
        high_overstock["stock_value"] > 0
    ]

    if high_overstock.empty:
        return create_empty_figure(
            "No valid overstock value data available"
        )

    # -----------------------------------------
    # Aggregate by category
    # -----------------------------------------
    overstock_value = (
        high_overstock
        .groupby("category")["stock_value"]
        .sum()
        .reset_index()
    )

    overstock_value = overstock_value.sort_values(
        "stock_value",
        ascending=False
    )

    # -----------------------------------------
    # Treemap
    # -----------------------------------------
    fig = px.treemap(
        overstock_value,
        path=["category"],
        values="stock_value",
        color="stock_value",
        color_continuous_scale="Reds",
        hover_data={
            "stock_value": ":,.0f"
        }
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
            text="Overstock Value by Category",
            x=0.5,
            xanchor="center",
            y=0.96,

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
        ),

        coloraxis_showscale=False
    )

    # -----------------------------------------
    # Treemap styling
    # -----------------------------------------
    fig.update_traces(
        textinfo="label+value",

        textfont=dict(
            color="white",
            size=12
        ),

        marker=dict(
            line=dict(
                color="#0e1117",
                width=1.5
            )
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "Overstock Value: ₹%{value:,.0f}"
            "<extra></extra>"
        )
    )

    return fig

@st.cache_data
def create_risk_quadrant_chart(risk_analysis):
    """5. Scatter Plot - Stockout vs Overstock Risk Quadrant"""

    # Work on a copy so the original dataframe is not modified
    risk_analysis = risk_analysis.copy()

    risk_map = {
        'NONE': 0,
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3
    }

    risk_analysis['stockout_score'] = (
        risk_analysis['stockout_risk'].map(risk_map).fillna(0)
    )

    risk_analysis['overstock_score'] = (
        risk_analysis['overstock_risk'].map(risk_map).fillna(0)
    )

    # Add quadrant labels
    risk_analysis['quadrant'] = risk_analysis.apply(
        lambda row:
            'Reorder Now'
            if row['stockout_score'] >= 2 and row['overstock_score'] <= 1
            else 'Markdown/Clear'
            if row['overstock_score'] >= 2 and row['stockout_score'] <= 1
            else 'Watch Carefully'
            if row['stockout_score'] >= 2 and row['overstock_score'] >= 2
            else 'Healthy',
        axis=1
    )

    quadrant_colors = {
        'Reorder Now': '#ef4444',
        'Markdown/Clear': '#f59e0b',
        'Watch Carefully': '#8b5cf6',
        'Healthy': '#34d399'
    }

    fig = px.scatter(
        risk_analysis,
        x='stockout_score',
        y='overstock_score',
        color='quadrant',
        color_discrete_map=quadrant_colors,
        size='stock_value',
        size_max=30,
        hover_data=['sku_id', 'category'],
        labels={
            'stockout_score': 'Stockout Risk',
            'overstock_score': 'Overstock Risk',
            'quadrant': 'Action'
        }
    )

    # ------------------------------------------------
    # Main layout
    # ------------------------------------------------
    fig.update_layout(
        height=450,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Stockout vs Overstock Risk Quadrant',
            x=0.5,
            xanchor='center',
            y=0.95,
            yanchor='top',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Stockout Risk',
        yaxis_title='Overstock Risk',

        font=dict(
            family='Arial',
            size=12,
            color='white'
        ),

        margin=dict(
            l=60,
            r=40,
            t=75,
            b=60
        ),

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.01,
            xanchor='center',
            x=0.5,
            font=dict(
                color='white',
                size=10
            ),
            bgcolor='rgba(0,0,0,0)'
        ),

        hovermode='closest'
    )

    # ------------------------------------------------
    # X Axis
    # ------------------------------------------------
    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zeroline=False,
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
        range=[-0.5, 3.5]
    )

    # ------------------------------------------------
    # Y Axis
    # ------------------------------------------------
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zeroline=False,
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
        range=[-0.5, 3.5]
    )

    # ------------------------------------------------
    # Quadrant background shading
    # ------------------------------------------------

    # Healthy
    fig.add_shape(
        type='rect',
        x0=-0.5,
        x1=1.5,
        y0=-0.5,
        y1=1.5,
        fillcolor='rgba(52,211,153,0.08)',
        line_width=0,
        layer='below'
    )

    # Reorder Now
    fig.add_shape(
        type='rect',
        x0=1.5,
        x1=3.5,
        y0=-0.5,
        y1=1.5,
        fillcolor='rgba(239,68,68,0.08)',
        line_width=0,
        layer='below'
    )

    # Markdown / Clear
    fig.add_shape(
        type='rect',
        x0=-0.5,
        x1=1.5,
        y0=1.5,
        y1=3.5,
        fillcolor='rgba(245,158,11,0.08)',
        line_width=0,
        layer='below'
    )

    # Watch Carefully
    fig.add_shape(
        type='rect',
        x0=1.5,
        x1=3.5,
        y0=1.5,
        y1=3.5,
        fillcolor='rgba(139,92,246,0.08)',
        line_width=0,
        layer='below'
    )

    # ------------------------------------------------
    # Quadrant divider lines
    # ------------------------------------------------
    fig.add_vline(
        x=1.5,
        line_dash='dash',
        line_color='rgba(255,255,255,0.35)',
        line_width=1
    )

    fig.add_hline(
        y=1.5,
        line_dash='dash',
        line_color='rgba(255,255,255,0.35)',
        line_width=1
    )

    # ------------------------------------------------
    # Quadrant labels
    # ------------------------------------------------

    fig.add_annotation(
        x=0.5,
        y=0.35,
        text='<b>HEALTHY</b>',
        showarrow=False,
        font=dict(
            color='#34d399',
            size=11
        )
    )

    fig.add_annotation(
        x=2.5,
        y=0.35,
        text='<b>REORDER NOW</b>',
        showarrow=False,
        font=dict(
            color='#ef4444',
            size=11
        )
    )

    fig.add_annotation(
        x=0.5,
        y=2.65,
        text='<b>MARKDOWN / CLEAR</b>',
        showarrow=False,
        font=dict(
            color='#f59e0b',
            size=11
        )
    )

    fig.add_annotation(
        x=2.5,
        y=2.65,
        text='<b>WATCH CAREFULLY</b>',
        showarrow=False,
        font=dict(
            color='#8b5cf6',
            size=11
        )
    )

    # ------------------------------------------------
    # Marker styling
    # ------------------------------------------------
    fig.update_traces(
        marker=dict(
            opacity=0.85,
            line=dict(
                color='white',
                width=1
            )
        )
    )

    return fig

@st.cache_data
def create_overstock_gauge(risk_metrics):
    """6. Gauge Chart - Overstock Risk"""

    total_skus = risk_metrics.get('total_skus', 0)
    high_overstock = risk_metrics.get('high_overstock', 0)

    high_pct = (
        high_overstock / total_skus * 100
        if total_skus > 0
        else 0
    )

    # Keep gauge value within 0-50
    gauge_value = min(high_pct, 50)

    # Determine gauge color
    if high_pct > 20:
        gauge_color = "#ef4444"
    elif high_pct > 10:
        gauge_color = "#f59e0b"
    else:
        gauge_color = "#34d399"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=gauge_value,

            title={
                'text': "High Overstock SKUs (%)",
                'font': {
                    'color': 'white',
                    'size': 18
                }
            },

            number={
                'suffix': '%',
                'font': {
                    'color': 'white',
                    'size': 32
                }
            },

            domain={
                'x': [0, 1],
                'y': [0, 1]
            },

            gauge={
                'axis': {
                    'range': [0, 50],
                    'tickvals': [0, 10, 20, 30, 40, 50],
                    'ticktext': [
                        '0%',
                        '10%',
                        '20%',
                        '30%',
                        '40%',
                        '50%'
                    ],
                    'tickfont': {
                        'color': 'white',
                        'size': 10
                    },
                    'tickcolor': 'white'
                },

                'bar': {
                    'color': gauge_color,
                    'thickness': 0.7
                },

                'bgcolor': '#1a1f2b',
                'borderwidth': 1,
                'bordercolor': '#333333',

                'steps': [
                    {
                        'range': [0, 10],
                        'color': 'rgba(52, 211, 153, 0.20)'
                    },
                    {
                        'range': [10, 20],
                        'color': 'rgba(245, 158, 11, 0.20)'
                    },
                    {
                        'range': [20, 50],
                        'color': 'rgba(239, 68, 68, 0.20)'
                    }
                ],

                'threshold': {
                    'line': {
                        'color': 'white',
                        'width': 3
                    },
                    'thickness': 0.75,
                    'value': gauge_value
                }
            }
        )
    )

    fig.update_layout(
        height=400,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        margin=dict(
            l=25,
            r=25,
            t=70,
            b=45
        ),

        font=dict(
            family='Arial',
            size=12,
            color='white'
        )
    )

    # Additional information below gauge
    fig.add_annotation(
        text=f"<b>{high_overstock}</b> SKUs with high overstock risk",
        x=0.5,
        y=0.05,
        xref='paper',
        yref='paper',
        showarrow=False,
        font=dict(
            color='white',
            size=13
        )
    )

    return fig

