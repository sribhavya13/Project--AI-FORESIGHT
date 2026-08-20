import plotly.express as px
from pygments.lexers import go
import streamlit as st


def create_store_performance_chart(sales):
    """Revenue by Store (Top 10)"""

    # Find store column
    store_col = None
    for col in ["store_id_x", "store_id", "store"]:
        if col in sales.columns:
            store_col = col
            break

    if store_col:

        # Top 10 stores by revenue
        store_sales = (
            sales.groupby(store_col)["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        df = store_sales.reset_index()
        df.columns = ["store", "revenue"]

        fig = px.bar(
            df,
            x="revenue",
            y="store",
            orientation="h",
            color="revenue",
            color_continuous_scale="Oranges",
            labels={
                "revenue": "Revenue (₹)",
                "store": "Store"
            }
        )

        # Value labels
        fig.update_traces(
            texttemplate="₹%{x:,.0f}",
            textposition="outside",
            textfont=dict(
                size=11,
                color="white"
            ),
            marker_line_color="white",
            marker_line_width=0.5
        )

        # Layout
        fig.update_layout(

            height=400,

            template="plotly_dark",

            title=dict(
                text="Revenue by Store (Top 10)",
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

            margin=dict(
                l=80,
                r=40,
                t=70,
                b=50
            ),

            showlegend=False,

            font=dict(
                size=12,
                color="white"
            ),

            coloraxis_showscale=False
        )

        # Axis styling
        fig.update_xaxes(
            gridcolor="#333333",
            tickfont=dict(color="white"),
            tickprefix="₹",
            tickformat=",.0f"
        )

        fig.update_yaxes(
            autorange="reversed",
            gridcolor="#333333",
            tickfont=dict(color="white")
        )

    else:
        fig = go.Figure()

        fig.add_annotation(
            text="Store data not available",
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
                text="Revenue by Store (Top 10)",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            )
        )

    return fig


def create_sales_by_day_chart(daily_sales):
    """Sales by Day of Week"""

    sales_by_day = (
        daily_sales.groupby("day_name")["revenue"]
        .sum()
        .reindex([
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ])
    )

    df = sales_by_day.reset_index()
    df.columns = ["day", "revenue"]

    fig = px.bar(
        df,
        x="day",
        y="revenue",
        color="revenue",
        color_continuous_scale="Blues",
        labels={
            "day": "Day",
            "revenue": "Revenue (₹)"
        }
    )

    # Value labels
    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside",
        textfont=dict(
            size=11,
            color="white"
        ),
        marker_line_color="white",
        marker_line_width=0.5
    )

    # Layout
    fig.update_layout(

        height=400,

        template="plotly_dark",

        title=dict(
            text="Sales by Day of Week",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Day",
        yaxis_title="Revenue (₹)",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        showlegend=False,

        font=dict(
            size=12,
            color="white"
        ),

        coloraxis_showscale=False
    )

    # Axis styling
    fig.update_xaxes(
        gridcolor="#333333",
        tickfont=dict(color="white")
    )

    fig.update_yaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        tickprefix="₹",
        tickformat=",.0f"
    )

    return fig



def create_weekly_sales_trend(daily_sales):
    """Weekly Sales Trend"""

    # Aggregate weekly revenue
    weekly_sales = (
        daily_sales.groupby("week")["revenue"]
        .sum()
        .reset_index()
    )

    weekly_sales.columns = ["week", "revenue"]

    # Create line chart
    fig = px.line(
        weekly_sales,
        x="week",
        y="revenue",
        labels={
            "week": "Week Number",
            "revenue": "Revenue (₹)"
        },
        color_discrete_sequence=["#667eea"]
    )

    # Line styling
    fig.update_traces(
        mode="lines+markers",
        line=dict(
            width=3,
            color="#667eea"
        ),
        marker=dict(
            size=7,
            color="#667eea",
            line=dict(
                color="white",
                width=1
            )
        ),
        hovertemplate=
            "<b>Week %{x}</b><br>"
            "Revenue: ₹%{y:,.0f}"
            "<extra></extra>"
    )

    # Layout
    fig.update_layout(
        height=400,

        template="plotly_dark",

        title=dict(
            text="Weekly Sales Trend",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Week Number",
        yaxis_title="Revenue (₹)",

        hovermode="x unified",

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

    # X-axis styling
    fig.update_xaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        dtick=5      # Show every 5th week
    )

    # Y-axis styling
    fig.update_yaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        tickprefix="₹",
        tickformat=",.0f"
    )

    return fig

def create_quarterly_sales_chart(daily_sales):
    """Quarterly Sales"""

    # Aggregate quarterly revenue
    quarterly_sales = (
        daily_sales.groupby("quarter")["revenue"]
        .sum()
        .reset_index()
    )

    quarterly_sales.columns = ["quarter", "revenue"]

    # Create chart
    fig = px.bar(
        quarterly_sales,
        x="quarter",
        y="revenue",
        color="revenue",
        color_continuous_scale="Greens",
        labels={
            "quarter": "Quarter",
            "revenue": "Revenue (₹)"
        }
    )

    # Value labels
    fig.update_traces(
        texttemplate="₹%{y:,.0f}",
        textposition="outside",
        textfont=dict(
            size=11,
            color="white"
        ),
        marker_line_color="white",
        marker_line_width=0.5
    )

    # Layout
    fig.update_layout(
        height=400,

        template="plotly_dark",

        title=dict(
            text="Quarterly Sales",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Quarter",
        yaxis_title="Revenue (₹)",

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
        ),

        coloraxis_showscale=False
    )

    # Axis styling
    fig.update_xaxes(
        gridcolor="#333333",
        tickfont=dict(color="white")
    )

    fig.update_yaxes(
        gridcolor="#333333",
        tickfont=dict(color="white"),
        tickprefix="₹",
        tickformat=",.0f"
    )

    return fig
def create_order_value_distribution(sales):
    """Order Value Distribution"""

    if "revenue" in sales.columns:

        # Remove outliers (top 5%)
        transactions = sales["revenue"].dropna()
        transactions = transactions[
            transactions < transactions.quantile(0.95)
        ]

        # Histogram
        fig = px.histogram(
            transactions,
            nbins=50,
            color_discrete_sequence=["#764ba2"],
            labels={
                "value": "Order Value (₹)",
                "count": "Frequency"
            }
        )

        # Mean line
        mean_value = transactions.mean()

        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color="#34d399",
            line_width=2,
            annotation_text=f"Mean: ₹{mean_value:,.0f}",
            annotation_position="top right",
            annotation_font=dict(
                color="white",
                size=11
            )
        )

        # Layout
        fig.update_layout(
            height=400,

            template="plotly_dark",

            title=dict(
                text="Order Value Distribution",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),

            xaxis_title="Order Value (₹)",
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

        # Axis styling
        fig.update_xaxes(
            gridcolor="#333333",
            tickfont=dict(color="white"),
            tickprefix="₹",
            tickformat=",.0f"
        )

        fig.update_yaxes(
            gridcolor="#333333",
            tickfont=dict(color="white")
        )

        # Histogram styling
        fig.update_traces(
            marker_line_color="white",
            marker_line_width=0.3,
            opacity=0.9
        )

    else:
        fig = go.Figure()

        fig.add_annotation(
            text="Order data not available",
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

            title=dict(
                text="Order Value Distribution",
                x=0.5,
                xanchor="center",
                font=dict(
                    size=18,
                    color="white"
                )
            ),

            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117"
        )

    return fig


