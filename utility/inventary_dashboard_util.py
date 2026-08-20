from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app_pages.executive_dashboard import create_empty_figure


def calculate_inventory_metrics(inventory_analysis):
    """Calculate inventory metrics"""

    total_stock_value = inventory_analysis['stock_value'].sum()
    avg_stock_value = inventory_analysis['stock_value'].mean()

    return {
        'total_stock_value': total_stock_value,
        'avg_stock_value': avg_stock_value,
        'total_skus': len(inventory_analysis),
        'avg_stock_on_hand': inventory_analysis['stock_on_hand'].mean(),
        'median_stock_on_hand': inventory_analysis['stock_on_hand'].median(),
        'max_stock_value': inventory_analysis['stock_value'].max(),
        'avg_reorder_point': inventory_analysis['reorder_point'].mean(),
        'min_reorder_point': inventory_analysis['reorder_point'].min(),
        'max_reorder_point': inventory_analysis['reorder_point'].max(),
        'stockout_risk_count': len
            (inventory_analysis[inventory_analysis['stock_on_hand'] < inventory_analysis['reorder_point']])
    }


def create_inventory_value_chart(inv_by_category):
    """Inventory Value by Category - Treemap"""

    # --------------------------------------------
    # Validate data
    # --------------------------------------------
    required_cols = [
        "category",
        "stock_value"
    ]

    if (
        inv_by_category is None
        or inv_by_category.empty
        or not all(col in inv_by_category.columns for col in required_cols)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Inventory data not available",
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
                text="Inventory Value by Category",
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

    # --------------------------------------------
    # Clean data
    # --------------------------------------------
    df = inv_by_category.copy()

    df = df.dropna(
        subset=["category", "stock_value"]
    )

    df = df[df["stock_value"] > 0]

    if df.empty:
        return create_empty_figure(
            "No inventory value data available"
        )

    # --------------------------------------------
    # Treemap
    # --------------------------------------------
    hover_data = {}

    if "stock_value" in df.columns:
        hover_data["stock_value"] = ":,.0f"

    if "total_units" in df.columns:
        hover_data["total_units"] = ":,.0f"

    if "sku_count" in df.columns:
        hover_data["sku_count"] = ":,.0f"

    fig = px.treemap(
        df,

        path=["category"],

        values="stock_value",

        color="stock_value",

        color_continuous_scale="Teal",

        hover_data=hover_data
    )

    # --------------------------------------------
    # Layout
    # --------------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Inventory Value by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        font=dict(
            size=12,
            color="white"
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),

        coloraxis_colorbar=dict(
            title=dict(
                text="Stock Value",
                font=dict(
                    color="white"
                )
            ),

            tickfont=dict(
                color="white"
            ),

            tickprefix="₹",

            tickformat=",.0f"
        )
    )

    # --------------------------------------------
    # Treemap text
    # --------------------------------------------
    fig.update_traces(

        textinfo="label+value",

        texttemplate=(
            "<b>%{label}</b><br>"
            "₹%{value:,.0f}"
        ),

        textfont=dict(
            color="white",
            size=12
        ),

        marker=dict(
            line=dict(
                color="#ffffff",
                width=1
            )
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "Inventory Value: ₹%{value:,.0f}"
            "<extra></extra>"
        )
    )

    return fig

def create_inventory_units_chart(inv_by_category):
    """Inventory Units Distribution - Donut Chart"""

    # --------------------------------------------
    # Validate data
    # --------------------------------------------
    required_cols = [
        "category",
        "total_units"
    ]

    if (
        inv_by_category is None
        or inv_by_category.empty
        or not all(col in inv_by_category.columns for col in required_cols)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Inventory units data not available",
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
                text="Inventory Units Distribution",
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

    # --------------------------------------------
    # Clean data
    # --------------------------------------------
    df = inv_by_category.copy()

    df = df.dropna(
        subset=["category", "total_units"]
    )

    df = df[df["total_units"] > 0]

    if df.empty:
        return create_empty_figure(
            "No inventory units data available"
        )

    # --------------------------------------------
    # Donut chart
    # --------------------------------------------
    fig = px.pie(
        df,

        values="total_units",

        names="category",

        hole=0.45,

        color_discrete_sequence=px.colors.sequential.Oranges_r
    )

    # --------------------------------------------
    # Layout
    # --------------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Inventory Units Distribution",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        font=dict(
            size=12,
            color="white"
        ),

        margin=dict(
            l=20,
            r=20,
            t=75,
            b=20
        ),

        showlegend=True,

        legend=dict(
            orientation="h",

            yanchor="bottom",
            y=-0.05,

            xanchor="center",
            x=0.5,

            font=dict(
                color="white",
                size=10
            ),

            bgcolor="rgba(0,0,0,0)"
        )
    )

    # --------------------------------------------
    # Donut styling
    # --------------------------------------------
    fig.update_traces(

        textposition="inside",

        textinfo="percent+label",

        textfont=dict(
            color="white",
            size=11
        ),

        marker=dict(
            line=dict(
                color="#ffffff",
                width=1
            )
        ),

        hovertemplate=(
            "<b>%{label}</b><br>"
            "Units: %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    return fig


def create_stock_value_per_sku_chart(inv_by_category):
    """Stock Value per SKU by Category - Radar Chart"""

    # --------------------------------------------
    # Validate data
    # --------------------------------------------
    required_cols = [
        "category",
        "stock_value_per_sku"
    ]

    if (
        inv_by_category is None
        or inv_by_category.empty
        or not all(col in inv_by_category.columns for col in required_cols)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Stock value per SKU data not available",
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
                text="Stock Value per SKU by Category",
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

    # --------------------------------------------
    # Copy data
    # --------------------------------------------
    df = inv_by_category.copy()

    # Remove invalid values
    df = df.dropna(
        subset=[
            "category",
            "stock_value_per_sku"
        ]
    )

    df = df[
        df["stock_value_per_sku"] >= 0
    ]

    if df.empty:
        return create_empty_figure(
            "No stock value per SKU data available"
        )

    # --------------------------------------------
    # Find maximum value
    # --------------------------------------------
    max_val = df["stock_value_per_sku"].max()

    if max_val <= 0:
        return create_empty_figure(
            "Stock value per SKU contains no positive values"
        )

    # --------------------------------------------
    # Normalize to 0-100
    # --------------------------------------------
    df["normalized"] = (
        df["stock_value_per_sku"]
        / max_val
        * 100
    )

    # --------------------------------------------
    # Radar chart
    # --------------------------------------------
    fig = px.line_polar(

        df,

        r="normalized",

        theta="category",

        line_close=True,

        color_discrete_sequence=[
            "#00ff99"
        ],

        hover_data={
            "stock_value_per_sku": ":,.0f",
            "normalized": False
        }
    )

    # --------------------------------------------
    # Layout
    # --------------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Stock Value per SKU by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        font=dict(
            size=12,
            color="white"
        ),

        margin=dict(
            l=50,
            r=50,
            t=75,
            b=50
        ),

        showlegend=False,

        polar=dict(

            bgcolor="#0e1117",

            # ------------------------------------
            # Radial axis
            # ------------------------------------
            radialaxis=dict(

                visible=True,

                range=[
                    0,
                    100
                ],

                tickfont=dict(
                    color="white",
                    size=10
                ),

                tickcolor="white",

                gridcolor=(
                    "rgba(255,255,255,0.15)"
                ),

                linecolor=(
                    "rgba(255,255,255,0.25)"
                ),

                title=dict(
                    text="Normalized Value",
                    font=dict(
                        color="white",
                        size=11
                    )
                )
            ),

            # ------------------------------------
            # Category axis
            # ------------------------------------
            angularaxis=dict(

                tickfont=dict(
                    color="white",
                    size=11
                ),

                tickcolor="white",

                gridcolor=(
                    "rgba(255,255,255,0.15)"
                ),

                linecolor=(
                    "rgba(255,255,255,0.25)"
                )
            )
        )
    )

    # --------------------------------------------
    # Radar line + fill
    # --------------------------------------------
    fig.update_traces(

        mode="lines+markers",

        line=dict(
            color="#00ff99",
            width=3
        ),

        marker=dict(
            size=8,
            color="#00ff99",
            line=dict(
                color="white",
                width=1
            )
        ),

        fill="toself",

        fillcolor="rgba(0,255,153,0.15)",

        hovertemplate=(
            "<b>%{theta}</b><br>"
            "Stock Value per SKU: "
            "₹%{customdata[0]:,.0f}"
            "<br>"
            "Normalized: %{r:.1f}%"
            "<extra></extra>"
        ),

        customdata=df[
            ["stock_value_per_sku"]
        ].values
    )

    return fig

def create_inventory_distribution_chart(inventory_analysis):
    """4. Box Plot - Stock Distribution by Category"""

    if inventory_analysis is None or inventory_analysis.empty:
        return create_empty_figure("No inventory distribution data available")

    # ============================================
    # CREATE CHART
    # ============================================

    if 'category' in inventory_analysis.columns:

        fig = px.box(
            inventory_analysis,
            x='category',
            y='stock_on_hand',
            title='Stock Distribution by Category',
            labels={
                'stock_on_hand': 'Units in Stock',
                'category': 'Category'
            },
            color='category',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        # Hide legend because category is already on X-axis
        show_legend = False

    else:

        fig = px.histogram(
            inventory_analysis,
            x='stock_on_hand',
            nbins=30,
            title='Stock Level Distribution',
            labels={
                'stock_on_hand': 'Units in Stock'
            },
            color_discrete_sequence=['#764ba2']
        )

        show_legend = False

    # ============================================
    # LAYOUT
    # ============================================

    fig.update_layout(

        height=400,

        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text=(
                'Stock Distribution by Category'
                if 'category' in inventory_analysis.columns
                else 'Stock Level Distribution'
            ),
            x=0.5,
            xanchor='center',
            y=0.95,
            yanchor='top',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title=(
            'Category'
            if 'category' in inventory_analysis.columns
            else 'Units in Stock'
        ),

        yaxis_title=(
            'Units in Stock'
            if 'category' in inventory_analysis.columns
            else 'Frequency'
        ),

        showlegend=show_legend,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=60
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    # ============================================
    # X AXIS
    # ============================================

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zerolinecolor='rgba(255,255,255,0.15)',
        tickfont=dict(
            color='white',
            size=11
        ),
        title_font=dict(
            color='white',
            size=13
        )
    )

    # ============================================
    # Y AXIS
    # ============================================

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.08)',
        zerolinecolor='rgba(255,255,255,0.15)',
        tickfont=dict(
            color='white',
            size=11
        ),
        title_font=dict(
            color='white',
            size=13
        ),
        tickformat=',.0f'
    )

    # ============================================
    # BOX PLOT STYLING
    # ============================================

    if 'category' in inventory_analysis.columns:

        fig.update_traces(
            marker=dict(
                color='white',
                size=4
            ),
            line=dict(
                color='white',
                width=1
            ),
            opacity=0.85
        )

    else:

        fig.update_traces(
            marker_line_color='white',
            marker_line_width=0.4,
            opacity=0.9
        )

    return fig



def create_stockout_risk_gauge(inventory_analysis):
    """6. Gauge Chart - Stockout Risk"""

    # ============================================
    # SAFETY CHECK
    # ============================================

    if (
        inventory_analysis is None
        or inventory_analysis.empty
        or 'stock_on_hand' not in inventory_analysis.columns
        or 'reorder_point' not in inventory_analysis.columns
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Stockout risk data not available",
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
                text="Stockout Risk (%)",
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

    # ============================================
    # CALCULATE RISK
    # ============================================

    total_skus = len(inventory_analysis)

    risk_skus = len(
        inventory_analysis[
            inventory_analysis["stock_on_hand"]
            < inventory_analysis["reorder_point"]
        ]
    )

    risk_percent = (
        risk_skus / total_skus * 100
        if total_skus > 0
        else 0
    )

    # ============================================
    # GAUGE COLOR
    # ============================================

    if risk_percent > 30:
        bar_color = "#ef4444"
    elif risk_percent > 15:
        bar_color = "#f59e0b"
    else:
        bar_color = "#34d399"

    # ============================================
    # GAUGE
    # ============================================

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",

            value=risk_percent,

            title={
                "text": "Stockout Risk (%)",
                "font": {
                    "color": "white",
                    "size": 18
                }
            },

            number={
                "font": {
                    "color": "white",
                    "size": 36
                },
                "suffix": "%"
            },

            domain={
                "x": [0, 1],
                "y": [0, 1]
            },

            gauge={

                "axis": {
                    "range": [0, 100],
                    "tickfont": {
                        "color": "white",
                        "size": 11
                    },
                    "tickcolor": "white"
                },

                "bar": {
                    "color": bar_color,
                    "thickness": 0.25
                },

                "bgcolor": "#1a1d24",

                "bordercolor": "#444444",
                "borderwidth": 1,

                "steps": [
                    {
                        "range": [0, 15],
                        "color": "rgba(52, 211, 153, 0.20)"
                    },
                    {
                        "range": [15, 30],
                        "color": "rgba(245, 158, 11, 0.20)"
                    },
                    {
                        "range": [30, 100],
                        "color": "rgba(239, 68, 68, 0.20)"
                    }
                ],

                "threshold": {
                    "line": {
                        "color": "white",
                        "width": 3
                    },
                    "thickness": 0.75,
                    "value": risk_percent
                }
            }
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
            text="Stockout Risk",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        margin=dict(
            l=30,
            r=30,
            t=70,
            b=60
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # ============================================
    # RISK COUNT
    # ============================================

    fig.add_annotation(
        text=f"<b>{risk_skus:,}</b> SKUs at risk",
        x=0.5,
        y=0.18,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            color="white",
            size=14
        )
    )

    return fig