import pandas as pd
import streamlit
from pygments.lexers import go
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_pages.executive_dashboard import create_empty_figure


def create_top_products_chart(daily_sales, top_n=10):
    """Top N Products by Revenue"""

    if 'sku_id' not in daily_sales.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Product data not available",
            x=0.5, y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=14, color="white")
        )
        fig.update_layout(
            height=400,
            template="plotly_dark"
        )
        return fig


    top_products = (
        daily_sales.groupby('sku_id')['revenue']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )


    # Product names
    if 'sku_name' in daily_sales.columns:
        product_names = (
            daily_sales.groupby('sku_id')['sku_name']
            .first()
            .to_dict()
        )

        labels = [
            str(product_names.get(sku, sku))[:25]
            for sku in top_products.index
        ]

    else:
        labels = top_products.index.astype(str)


    df = pd.DataFrame({
        "product": labels,
        "revenue": top_products.values
    })


    fig = px.bar(
        df,
        x="revenue",
        y="product",
        orientation="h",
        labels={
            "revenue": "Revenue (₹)",
            "product": ""
        },
        color="revenue",
        color_continuous_scale=[
            "#14b8a6",
            "#2dd4bf",
            "#99f6e4"
        ]
    )


    # Value labels
    fig.update_traces(
        texttemplate="₹%{x:,.0f}",
        textposition="outside",
        textfont=dict(
            color="white",
            size=10
        )
    )


    fig.update_layout(

        height=400,

        template="plotly_dark",

        title=dict(
            text=f"Top {top_n} Products by Revenue",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Revenue (₹)",
        yaxis_title="",


        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        showlegend=False,

        margin=dict(
            l=80,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color="white"
        )
    )


    fig.update_xaxes(
        gridcolor="#333333",
        tickprefix="₹",
        tickformat=",.0f",
        tickfont=dict(color="white")
    )


    fig.update_yaxes(
        gridcolor="#333333",
        autorange="reversed",
        tickfont=dict(color="white")
    )


    return fig

def create_price_distribution_chart(daily_sales):
    """Product Price Distribution"""

    # Find price column
    if 'unit_price' in daily_sales.columns:
        prices = daily_sales['unit_price'].dropna()

    elif 'unit_price_x' in daily_sales.columns:
        prices = daily_sales['unit_price_x'].dropna()

    else:
        fig = go.Figure()

        fig.add_annotation(
            text="Price data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=14,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark"
        )

        return fig


    # Remove extreme prices
    prices = prices[prices < prices.quantile(0.95)]


    fig = px.histogram(
        prices,

        nbins=50,

        labels={
            "value": "Unit Price (₹)",
            "count": "Frequency"
        },

        color_discrete_sequence=[
            "#8b5cf6"
        ]
    )


    # Mean price
    mean_price = prices.mean()


    fig.add_vline(

        x=mean_price,

        line_dash="dash",

        line_color="#10b981",

        annotation_text=f"Avg: ₹{mean_price:,.0f}",

        annotation_position="top right",

        annotation_font=dict(
            color="white",
            size=11
        )
    )



    fig.update_traces(

        marker_line_color="white",

        marker_line_width=0.5
    )



    fig.update_layout(

        height=400,


        template="plotly_dark",


        title=dict(

            text="Product Price Distribution",

            x=0.5,

            xanchor="center",

            font=dict(
                size=18,
                color="white"
            )
        ),


        xaxis_title="Unit Price (₹)",

        yaxis_title="Frequency",


        plot_bgcolor="#0e1117",

        paper_bgcolor="#0e1117",


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



    fig.update_xaxes(

        gridcolor="#333333",

        tickprefix="₹",

        tickformat=",.0f",

        tickfont=dict(
            color="white"
        )
    )


    fig.update_yaxes(

        gridcolor="#333333",

        tickfont=dict(
            color="white"
        )
    )


    return fig

def create_product_scatter_chart(daily_sales):
    """Product Performance Scatter: Units vs Revenue"""

    if 'sku_id' not in daily_sales.columns:

        fig = go.Figure()

        fig.add_annotation(
            text="Product data not available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=14,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template="plotly_dark"
        )

        return fig



    # Aggregate product performance
    product_perf = (
        daily_sales.groupby("sku_id")
        .agg({
            "units_sold": "sum",
            "revenue": "sum"
        })
        .reset_index()
    )


    product_perf.columns = [
        "sku_id",
        "units_sold",
        "revenue"
    ]


    # Top 100 products by revenue
    product_perf = (
        product_perf
        .nlargest(100, "revenue")
    )



    fig = px.scatter(

        product_perf,

        x="units_sold",

        y="revenue",

        labels={

            "units_sold": "Units Sold",

            "revenue": "Revenue (₹)"
        },

        color_discrete_sequence=[
            "#8b5cf6"
        ],

        hover_data=[
            "sku_id"
        ]

    )



    # Point styling
    fig.update_traces(

        marker=dict(

            size=12,

            opacity=0.75,

            color="#8b5cf6",

            line=dict(

                color="white",

                width=0.5
            )
        ),


        hovertemplate=(

            "<b>SKU: %{customdata[0]}</b><br>" +

            "Units Sold: %{x:,}<br>" +

            "Revenue: ₹%{y:,.0f}" +

            "<extra></extra>"
        )
    )



    fig.update_layout(

        height=400,


        template="plotly_dark",


        title=dict(

            text="Product Performance: Units vs Revenue",

            x=0.5,

            xanchor="center",

            font=dict(

                size=18,

                color="white"
            )
        ),


        xaxis_title="Units Sold",

        yaxis_title="Revenue (₹)",


        plot_bgcolor="#0e1117",

        paper_bgcolor="#0e1117",


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



    # Axis styling
    fig.update_xaxes(

        gridcolor="#333333",

        tickfont=dict(

            color="white"
        )
    )


    fig.update_yaxes(

        gridcolor="#333333",

        tickprefix="₹",

        tickformat=",.0f",

        tickfont=dict(

            color="white"
        )
    )


    return fig

def create_top_units_chart(daily_sales, top_n=10):
    """Top N Products by Units Sold"""

    if daily_sales is None or daily_sales.empty:
        return create_empty_figure("No product data available")

    if "sku_id" not in daily_sales.columns or "units_sold" not in daily_sales.columns:
        return create_empty_figure("Product data not available")

    # Top products by units sold
    top_units = (
        daily_sales
        .groupby("sku_id")["units_sold"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    if top_units.empty:
        return create_empty_figure("No units sold data available")

    # Product names
    if "sku_name" in daily_sales.columns:

        product_names = (
            daily_sales
            .groupby("sku_id")["sku_name"]
            .first()
            .to_dict()
        )

        labels = [
            str(product_names.get(sku, sku))[:25]
            for sku in top_units.index
        ]

    else:
        labels = [
            str(sku)
            for sku in top_units.index
        ]

    df = pd.DataFrame({
        "product": labels,
        "units": top_units.values
    })

    # Bar chart
    fig = px.bar(
        df,
        x="units",
        y="product",
        orientation="h",
        color="units",
        color_continuous_scale="Oranges",
        labels={
            "units": "Units Sold",
            "product": "Product"
        }
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
        marker_line_width=0.5
    )

    # Layout
    fig.update_layout(
        height=400,

        template="plotly_dark",

        title=dict(
            text=f"Top {top_n} Products by Units Sold",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Units Sold",
        yaxis_title="",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        showlegend=False,

        margin=dict(
            l=100,
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

    # X-axis
    fig.update_xaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        tickformat=","
    )

    # Y-axis
    fig.update_yaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        title_font=dict(color="white"),
        autorange="reversed"
    )

    return fig

def create_category_performance_chart(daily_sales):
    """
    Category Performance: Units vs Revenue
    """

    # -----------------------------------------
    # Validate dataframe
    # -----------------------------------------
    if daily_sales is None or daily_sales.empty:
        return create_empty_figure("No category data available")

    # -----------------------------------------
    # Find category column
    # -----------------------------------------
    if "category" not in daily_sales.columns:
        return create_empty_figure("Category column not available")

    # -----------------------------------------
    # Find units column
    # -----------------------------------------
    if "units_sold" in daily_sales.columns:
        qty_col = "units_sold"
    elif "quantity" in daily_sales.columns:
        qty_col = "quantity"
    else:
        return create_empty_figure("Units sold data not available")

    # -----------------------------------------
    # Find revenue column
    # -----------------------------------------
    if "revenue" in daily_sales.columns:
        rev_col = "revenue"
    elif "total_value" in daily_sales.columns:
        rev_col = "total_value"
    else:
        return create_empty_figure("Revenue data not available")

    # -----------------------------------------
    # Clean data
    # -----------------------------------------
    df = daily_sales[
        ["category", qty_col, rev_col]
    ].copy()

    df["category"] = df["category"].fillna("Unknown")

    df[qty_col] = pd.to_numeric(
        df[qty_col],
        errors="coerce"
    ).fillna(0)

    df[rev_col] = pd.to_numeric(
        df[rev_col],
        errors="coerce"
    ).fillna(0)

    # -----------------------------------------
    # Aggregate by category
    # -----------------------------------------
    cat_perf = (
        df.groupby("category", as_index=False)
        .agg(
            units_sold=(qty_col, "sum"),
            revenue=(rev_col, "sum")
        )
    )

    # Remove only completely empty categories
    cat_perf = cat_perf[
        (cat_perf["units_sold"] > 0) |
        (cat_perf["revenue"] > 0)
    ]

    if cat_perf.empty:
        return create_empty_figure(
            "No category performance data available"
        )

    # -----------------------------------------
    # Create Scatter Plot
    # -----------------------------------------
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=cat_perf["units_sold"],
            y=cat_perf["revenue"],

            mode="markers+text",

            text=cat_perf["category"],

            textposition="top center",

            textfont=dict(
                color="white",
                size=11
            ),

            marker=dict(
                size=18,
                color="#667eea",
                opacity=0.9,
                line=dict(
                    color="white",
                    width=1.5
                )
            ),

            hovertemplate=(
                "<b>%{text}</b><br>"
                "Units Sold: %{x:,.0f}<br>"
                "Revenue: ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------
    fig.update_layout(

        height=450,

        template="plotly_dark",

        title=dict(
            text="Category Performance: Units vs Revenue",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis=dict(
            title=dict(
                text="Units Sold",
                font=dict(
                    size=13,
                    color="white"
                )
            ),

            tickfont=dict(
                color="white"
            ),

            gridcolor="#333333",

            zeroline=True,
            zerolinecolor="#555555"
        ),

        yaxis=dict(
            title=dict(
                text="Revenue (₹)",
                font=dict(
                    size=13,
                    color="white"
                )
            ),

            tickfont=dict(
                color="white"
            ),

            gridcolor="#333333",

            zeroline=True,
            zerolinecolor="#555555"
        ),

        plot_bgcolor="#0e1117",

        paper_bgcolor="#0e1117",

        font=dict(
            size=12,
            color="white"
        ),

        showlegend=False,

        margin=dict(
            l=70,
            r=50,
            t=80,
            b=60
        ),

        hovermode="closest"
    )

    fig.update_xaxes(
        tickformat=",",
        gridcolor="rgba(255,255,255,0.08)"
    )

    fig.update_yaxes(
        tickprefix="₹",
        tickformat=",.0f",
        gridcolor="rgba(255,255,255,0.08)"
    )

    return fig


