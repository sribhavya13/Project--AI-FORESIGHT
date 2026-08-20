import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app_pages.executive_dashboard import create_empty_figure


def calculate_category_metrics(daily_sales):
    """Calculate category performance metrics"""

    # Category metrics
    category_metrics = daily_sales.groupby('category').agg({
        'revenue': 'sum',
        'units_sold': 'sum',
        'sku_id': 'nunique'
    }).reset_index()

    category_metrics.columns = ['category', 'revenue', 'units_sold', 'sku_count']
    category_metrics['avg_sku_revenue'] = category_metrics['revenue'] / category_metrics['sku_count']
    category_metrics['revenue_per_unit'] = category_metrics['revenue'] / category_metrics['units_sold']

    # Total revenue for share calculation
    total_revenue = daily_sales['revenue'].sum()

    return category_metrics, total_revenue


def create_category_revenue_chart(category_metrics, top_n=None):
    """Revenue by Category - Horizontal Bar Chart"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if category_metrics is None or category_metrics.empty:
        return create_empty_figure("No category revenue data available")

    required_cols = {"category", "revenue"}

    if not required_cols.issubset(category_metrics.columns):
        return create_empty_figure("Category revenue data not available")

    # -----------------------------------------
    # Prepare data
    # -----------------------------------------
    df = category_metrics[
        ["category", "revenue"]
    ].copy()

    df["category"] = df["category"].fillna("Unknown")

    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce"
    ).fillna(0)

    df = df.sort_values(
        "revenue",
        ascending=False
    )

    # Optional Top N
    if top_n is not None:
        df = df.head(top_n)

    # Reverse for horizontal chart
    df = df.sort_values(
        "revenue",
        ascending=True
    )

    if df.empty:
        return create_empty_figure(
            "No category revenue data available"
        )

    # -----------------------------------------
    # Create chart
    # -----------------------------------------
    fig = px.bar(
        df,
        x="revenue",
        y="category",
        orientation="h",

        color="revenue",

        color_continuous_scale="Blues",

        labels={
            "revenue": "Revenue (₹)",
            "category": ""
        }
    )

    # -----------------------------------------
    # Value labels
    # -----------------------------------------
    fig.update_traces(
        texttemplate="₹%{x:,.0f}",
        textposition="outside",

        textfont=dict(
            color="white",
            size=10
        ),

        marker_line_color="white",
        marker_line_width=0.5
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        title=dict(
            text="Revenue by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",

            font=dict(
                size=18,
                color="white"
            )
        ),

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        xaxis_title="Revenue (₹)",
        yaxis_title="",

        showlegend=False,

        coloraxis_showscale=False,

        margin=dict(
            l=100,
            r=80,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # -----------------------------------------
    # X-axis
    # -----------------------------------------
    fig.update_xaxes(

        gridcolor="rgba(255,255,255,0.08)",

        zeroline=False,

        tickprefix="₹",

        tickformat=",.0f",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=13
        )
    )

    # -----------------------------------------
    # Y-axis
    # -----------------------------------------
    fig.update_yaxes(

        gridcolor="rgba(255,255,255,0.05)",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white"
        )
    )

    return fig


def create_category_units_chart(category_metrics, top_n=None):
    """Units Sold by Category - Horizontal Bar Chart"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if category_metrics is None or category_metrics.empty:
        return create_empty_figure("No category units data available")

    required_cols = {"category", "units_sold"}

    if not required_cols.issubset(category_metrics.columns):
        return create_empty_figure("Category units data not available")

    # -----------------------------------------
    # Prepare data
    # -----------------------------------------
    df = category_metrics[
        ["category", "units_sold"]
    ].copy()

    df["category"] = df["category"].fillna("Unknown")

    df["units_sold"] = pd.to_numeric(
        df["units_sold"],
        errors="coerce"
    ).fillna(0)

    df = df.sort_values(
        "units_sold",
        ascending=False
    )

    # Optional Top N
    if top_n is not None:
        df = df.head(top_n)

    # Reverse order for horizontal bar chart
    df = df.sort_values(
        "units_sold",
        ascending=True
    )

    if df.empty:
        return create_empty_figure(
            "No category units data available"
        )

    # -----------------------------------------
    # Create chart
    # -----------------------------------------
    fig = px.bar(
        df,
        x="units_sold",
        y="category",
        orientation="h",

        color="units_sold",

        color_continuous_scale="Oranges",

        labels={
            "units_sold": "Units Sold",
            "category": ""
        }
    )

    # -----------------------------------------
    # Value labels
    # -----------------------------------------
    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",

        textfont=dict(
            color="white",
            size=10
        ),

        marker_line_color="white",
        marker_line_width=0.5
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        title=dict(
            text="Units Sold by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",

            font=dict(
                size=18,
                color="white"
            )
        ),

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        xaxis_title="Units Sold",
        yaxis_title="",

        showlegend=False,

        coloraxis_showscale=False,

        margin=dict(
            l=100,
            r=80,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # -----------------------------------------
    # X-axis
    # -----------------------------------------
    fig.update_xaxes(

        gridcolor="rgba(255,255,255,0.08)",

        zeroline=False,

        tickformat=",",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=13
        )
    )

    # -----------------------------------------
    # Y-axis
    # -----------------------------------------
    fig.update_yaxes(

        gridcolor="rgba(255,255,255,0.05)",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white"
        )
    )

    return fig

def create_avg_sku_revenue_chart(category_metrics, top_n=None):
    """Average Revenue per SKU by Category - Horizontal Bar Chart"""

    # -----------------------------------------
    # Validate data
    # -----------------------------------------
    if category_metrics is None or category_metrics.empty:
        return create_empty_figure(
            "No average SKU revenue data available"
        )

    required_cols = {"category", "avg_sku_revenue"}

    if not required_cols.issubset(category_metrics.columns):
        return create_empty_figure(
            "Average SKU revenue data not available"
        )

    # -----------------------------------------
    # Prepare data
    # -----------------------------------------
    df = category_metrics[
        ["category", "avg_sku_revenue"]
    ].copy()

    df["category"] = df["category"].fillna("Unknown")

    df["avg_sku_revenue"] = pd.to_numeric(
        df["avg_sku_revenue"],
        errors="coerce"
    ).fillna(0)

    df = df.sort_values(
        "avg_sku_revenue",
        ascending=False
    )

    # Optional Top N
    if top_n is not None:
        df = df.head(top_n)

    # Reverse order for horizontal chart
    df = df.sort_values(
        "avg_sku_revenue",
        ascending=True
    )

    if df.empty:
        return create_empty_figure(
            "No average SKU revenue data available"
        )

    # -----------------------------------------
    # Create chart
    # -----------------------------------------
    fig = px.bar(
        df,
        x="avg_sku_revenue",
        y="category",
        orientation="h",

        color="avg_sku_revenue",

        color_continuous_scale="Greens",

        labels={
            "avg_sku_revenue": "Avg Revenue per SKU (₹)",
            "category": ""
        }
    )

    # -----------------------------------------
    # Value labels
    # -----------------------------------------
    fig.update_traces(
        texttemplate="₹%{x:,.0f}",
        textposition="outside",

        textfont=dict(
            color="white",
            size=10
        ),

        marker_line_color="white",
        marker_line_width=0.5
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        title=dict(
            text="Avg Revenue per SKU by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",

            font=dict(
                size=18,
                color="white"
            )
        ),

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        xaxis_title="Avg Revenue per SKU (₹)",
        yaxis_title="",

        showlegend=False,

        coloraxis_showscale=False,

        margin=dict(
            l=100,
            r=90,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )

    # -----------------------------------------
    # X-axis
    # -----------------------------------------
    fig.update_xaxes(

        gridcolor="rgba(255,255,255,0.08)",

        zeroline=False,

        tickprefix="₹",

        tickformat=",.0f",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white",
            size=13
        )
    )

    # -----------------------------------------
    # Y-axis
    # -----------------------------------------
    fig.update_yaxes(

        gridcolor="rgba(255,255,255,0.05)",

        tickfont=dict(
            color="white",
            size=11
        ),

        title_font=dict(
            color="white"
        )
    )

    return fig

def create_category_quarter_chart(daily_sales):
    """Category Revenue by Quarter - Line Chart"""

    # --------------------------------------------
    # Validate data
    # --------------------------------------------
    required_cols = ["category", "quarter", "revenue"]

    if (
        daily_sales is None
        or daily_sales.empty
        or not all(col in daily_sales.columns for col in required_cols)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Quarter data not available",
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
                text="Category Revenue by Quarter",
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
    # Get top 8 categories
    # --------------------------------------------
    top_cats = (
        daily_sales
        .groupby("category")["revenue"]
        .sum()
        .nlargest(8)
        .index
    )

    filtered_data = daily_sales[
        daily_sales["category"].isin(top_cats)
    ]

    # --------------------------------------------
    # Aggregate category + quarter
    # --------------------------------------------
    cat_quarter = (
        filtered_data
        .groupby(["category", "quarter"])["revenue"]
        .sum()
        .unstack(fill_value=0)
    )

    if cat_quarter.empty:
        return create_empty_figure(
            "No category quarter data available"
        )

    # --------------------------------------------
    # Sort quarters
    # --------------------------------------------
    try:
        cat_quarter = cat_quarter.sort_index(axis=1)
    except Exception:
        pass

    # --------------------------------------------
    # Create figure
    # --------------------------------------------
    fig = go.Figure()

    colors = [
        "#667eea",
        "#764ba2",
        "#f59e0b",
        "#34d399",
        "#f87171",
        "#60a5fa",
        "#a78bfa",
        "#f472b6"
    ]

    for i, category in enumerate(cat_quarter.index):

        color = colors[i % len(colors)]

        fig.add_trace(
            go.Scatter(
                x=cat_quarter.columns,
                y=cat_quarter.loc[category],
                mode="lines+markers",

                name=str(category)[:18],

                line=dict(
                    width=3,
                    color=color
                ),

                marker=dict(
                    size=8,
                    color=color,
                    line=dict(
                        color="white",
                        width=1
                    )
                ),

                hovertemplate=(
                    f"<b>{category}</b><br>"
                    "Quarter: %{x}<br>"
                    "Revenue: ₹%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

    # --------------------------------------------
    # Layout
    # --------------------------------------------
    fig.update_layout(

        height=400,

        template="plotly_dark",

        # Centered title
        title=dict(
            text="Category Revenue by Quarter (Top 8)",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        # Axis titles
        xaxis_title="Quarter",
        yaxis_title="Revenue (₹)",

        # Background
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        # All default text
        font=dict(
            size=12,
            color="white"
        ),

        # Legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,

            font=dict(
                color="white",
                size=10
            ),

            bgcolor="rgba(0,0,0,0)"
        ),

        # Hover
        hovermode="x unified",

        # Margins
        margin=dict(
            l=60,
            r=40,
            t=90,
            b=55
        ),

        showlegend=True
    )

    # --------------------------------------------
    # X Axis
    # --------------------------------------------
    fig.update_xaxes(
        title_font=dict(
            color="white",
            size=13
        ),

        tickfont=dict(
            color="white",
            size=11
        ),

        gridcolor="rgba(255,255,255,0.08)",

        linecolor="rgba(255,255,255,0.2)",

        zeroline=False
    )

    # --------------------------------------------
    # Y Axis
    # --------------------------------------------
    fig.update_yaxes(
        title_font=dict(
            color="white",
            size=13
        ),

        tickfont=dict(
            color="white",
            size=11
        ),

        gridcolor="rgba(255,255,255,0.08)",

        linecolor="rgba(255,255,255,0.2)",

        tickprefix="₹",

        tickformat=",.0f",

        zeroline=False
    )

    return fig

def create_revenue_vs_units_chart(category_metrics):
    """Revenue vs Units by Category - Scatter Plot"""

    # --------------------------------------------
    # Validate data
    # --------------------------------------------
    required_cols = [
        "category",
        "units_sold",
        "revenue"
    ]

    if (
        category_metrics is None
        or category_metrics.empty
        or not all(col in category_metrics.columns for col in required_cols)
    ):
        fig = go.Figure()

        fig.add_annotation(
            text="Category performance data not available",
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
                text="Revenue vs Units by Category",
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
    # Remove invalid values
    # --------------------------------------------
    df = category_metrics.copy()

    df = df.dropna(
        subset=[
            "category",
            "units_sold",
            "revenue"
        ]
    )

    df = df[
        (df["units_sold"] > 0) &
        (df["revenue"] > 0)
    ]

    if df.empty:
        return create_empty_figure(
            "No category performance data available"
        )

    # --------------------------------------------
    # Create scatter chart
    # --------------------------------------------
    fig = px.scatter(
        df,

        x="units_sold",
        y="revenue",

        text="category",

        labels={
            "units_sold": "Units Sold",
            "revenue": "Revenue (₹)",
            "category": "Category"
        },

        color="revenue",
        color_continuous_scale="Purples",

        size="revenue",
        size_max=45,

        hover_data=[
            col for col in [
                "sku_count",
                "avg_sku_revenue"
            ]
            if col in df.columns
        ]
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
            text="Revenue vs Units by Category",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Units Sold",
        yaxis_title="Revenue (₹)",

        font=dict(
            size=12,
            color="white"
        ),

        margin=dict(
            l=60,
            r=50,
            t=75,
            b=55
        ),

        showlegend=False,

        coloraxis_colorbar=dict(
            title=dict(
                text="Revenue",
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
    # X Axis
    # --------------------------------------------
    fig.update_xaxes(

        title_font=dict(
            color="white",
            size=13
        ),

        tickfont=dict(
            color="white",
            size=11
        ),

        gridcolor="rgba(255,255,255,0.08)",

        linecolor="rgba(255,255,255,0.2)",

        zeroline=False,

        tickformat=",.0f"
    )

    # --------------------------------------------
    # Y Axis
    # --------------------------------------------
    fig.update_yaxes(

        title_font=dict(
            color="white",
            size=13
        ),

        tickfont=dict(
            color="white",
            size=11
        ),

        gridcolor="rgba(255,255,255,0.08)",

        linecolor="rgba(255,255,255,0.2)",

        zeroline=False,

        tickprefix="₹",

        tickformat=",.0f"
    )

    # --------------------------------------------
    # Scatter styling
    # --------------------------------------------
    fig.update_traces(

        mode="markers+text",

        textposition="top center",

        textfont=dict(
            color="white",
            size=10
        ),

        marker=dict(
            line=dict(
                color="white",
                width=1
            ),
            opacity=0.9
        ),

        hovertemplate=(
            "<b>%{text}</b><br>"
            "Units Sold: %{x:,.0f}<br>"
            "Revenue: ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )

    # --------------------------------------------
    # Add hover information if columns exist
    # --------------------------------------------
    customdata_cols = []

    if "sku_count" in df.columns:
        customdata_cols.append("sku_count")

    if "avg_sku_revenue" in df.columns:
        customdata_cols.append("avg_sku_revenue")

    if customdata_cols:

        customdata = df[customdata_cols].values

        fig.update_traces(
            customdata=customdata,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Units Sold: %{x:,.0f}<br>"
                "Revenue: ₹%{y:,.0f}<br>"
                + (
                    "SKUs: %{customdata[0]:,.0f}<br>"
                    if "sku_count" in customdata_cols
                    else ""
                )
                + (
                    "Avg SKU Revenue: ₹%{customdata[1]:,.0f}<br>"
                    if (
                        "avg_sku_revenue" in customdata_cols
                        and "sku_count" in customdata_cols
                    )
                    else (
                        "Avg SKU Revenue: ₹%{customdata[0]:,.0f}<br>"
                        if "avg_sku_revenue" in customdata_cols
                        else ""
                    )
                )
                + "<extra></extra>"
            )
        )

    return fig