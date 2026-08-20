import numpy as np
import plotly.express as px


import pandas as pd

from app_pages.executive_dashboard import create_empty_figure


def calculate_customer_metrics(daily_sales):
    """Calculate customer metrics from daily_sales"""

    df = daily_sales.copy()

    # -----------------------------
    # Data Cleaning
    # -----------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce"
    )

    df["units_sold"] = pd.to_numeric(
        df["units_sold"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["customer_id", "date"]
    )

    # -----------------------------
    # Basic Metrics
    # -----------------------------

    total_customers = (
        df["customer_id"].nunique()
    )

    daily_customers = (
        df.groupby(
            df["date"].dt.date
        )["customer_id"]
        .nunique()
        .mean()
    )

    # -----------------------------
    # Purchase Frequency
    # -----------------------------

    customer_frequency = (
        df.groupby("customer_id")["receipt_id"]
        .nunique()
    )

    avg_purchases = (
        customer_frequency.mean()
        if len(customer_frequency)
        else 0
    )

    repeat_customers = (
        customer_frequency > 1
    ).sum()

    repeat_rate = (
        repeat_customers / total_customers * 100
        if total_customers > 0
        else 0
    )

    max_purchases = (
        customer_frequency.max()
        if len(customer_frequency)
        else 0
    )

    # -----------------------------
    # Customer Revenue
    # -----------------------------

    customer_revenue = (
        df.groupby("customer_id")["revenue"]
        .sum()
    )

    avg_customer_value = (
        customer_revenue.mean()
        if len(customer_revenue)
        else 0
    )

    # -----------------------------
    # Customer SLV
    # -----------------------------

    customer_stats = (
        df.groupby("customer_id")
        .agg(
            revenue=("revenue", "sum"),
            orders=("receipt_id", "nunique"),
            first_purchase=("date", "min"),
            last_purchase=("date", "max")
        )
    )

    # Average Order Value
    customer_stats["avg_order_value"] = (
        customer_stats["revenue"]
        / customer_stats["orders"].replace(0, 1)
    )

    # Customer lifespan
    customer_stats["lifespan_days"] = (
        customer_stats["last_purchase"]
        - customer_stats["first_purchase"]
    ).dt.days

    # Avoid zero-day lifespan
    customer_stats["lifespan_days"] = (
        customer_stats["lifespan_days"]
        .clip(lower=1)
    )

    # Purchase frequency per day
    customer_stats["purchase_frequency"] = (
        customer_stats["orders"]
        / customer_stats["lifespan_days"]
    )

    # Expected lifetime
    expected_lifetime_days = 365

    # SLV
    customer_stats["slv"] = (
        customer_stats["avg_order_value"]
        * customer_stats["purchase_frequency"]
        * expected_lifetime_days
    )

    customer_stats["slv"] = (
        customer_stats["slv"]
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
        .round(2)
    )

    # SLV values for chart
    slv_values = customer_stats["slv"]

    # Overall SLV metrics
    avg_slv = (
        slv_values.mean()
        if len(slv_values)
        else 0
    )

    median_slv = (
        slv_values.median()
        if len(slv_values)
        else 0
    )

    max_slv = (
        slv_values.max()
        if len(slv_values)
        else 0
    )

    # -----------------------------
    # Top Customers
    # -----------------------------

    top_customers = (
        df.groupby("customer_id")
        .agg(
            revenue=("revenue", "sum"),
            order_count=("receipt_id", "nunique"),
            units=("units_sold", "sum")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    top_customer_revenue = (
        top_customers["revenue"].iloc[0]
        if not top_customers.empty
        else 0
    )

    # -----------------------------
    # Monthly New Customers
    # -----------------------------

    first_purchase = (
        df.groupby("customer_id")["date"]
        .min()
        .dt.to_period("M")
    )

    monthly_new = (
        first_purchase
        .value_counts()
        .sort_index()
    )

    avg_monthly_new = (
        monthly_new.mean()
        if len(monthly_new)
        else 0
    )

    max_monthly_new = (
        monthly_new.max()
        if len(monthly_new)
        else 0
    )

    # -----------------------------
    # Total Revenue
    # -----------------------------

    total_revenue = df["revenue"].sum()

    # -----------------------------
    # Business Health
    # -----------------------------

    health_metrics = {

        "Repeat Rate":
            round(repeat_rate, 2),

        "Avg Purchases":
            round(avg_purchases, 2),

        "Avg Revenue/Customer":
            round(avg_customer_value, 2),

        "Daily Customers":
            round(daily_customers, 2)
    }

    # -----------------------------
    # Return
    # -----------------------------

    return {

        "total_customers":
            total_customers,

        "daily_customers":
            round(daily_customers, 2),

        "avg_purchases":
            round(avg_purchases, 2),

        "repeat_customers":
            int(repeat_customers),

        "repeat_rate":
            round(repeat_rate, 2),

        "max_purchases":
            int(max_purchases),

        "top_customers":
            top_customers,

        "top_customer_revenue":
            round(top_customer_revenue, 2),

        "avg_customer_value":
            round(avg_customer_value, 2),

        # -------------------------
        # SLV
        # -------------------------

        "slv_values":
            slv_values,

        "customer_slv":
            customer_stats,

        "avg_slv":
            round(avg_slv, 2),

        "median_slv":
            round(median_slv, 2),

        "max_slv":
            round(max_slv, 2),

        # -------------------------
        # Existing metrics
        # -------------------------

        "monthly_new":
            monthly_new,

        "avg_monthly_new":
            round(avg_monthly_new, 2),

        "max_monthly_new":
            int(max_monthly_new),

        "customer_frequency":
            customer_frequency,

        "health_metrics":
            health_metrics,

        "total_revenue":
            round(total_revenue, 2)
    }


def _empty_customer_figure(param):
    pass


def create_customer_frequency_chart(customer_frequency):
    """1. Customer Purchase Frequency Distribution"""

    if customer_frequency is None or customer_frequency.empty:
        return _empty_customer_figure(
            "No customer frequency data available"
        )

    # Create segments
    bins = [0, 1, 3, 5, 10, 100]
    labels = ['1-time', '2-3', '4-5', '6-10', '10+']

    customer_segments = pd.cut(
        customer_frequency,
        bins=bins,
        labels=labels
    )

    seg_dist = (
        customer_segments
        .value_counts()
        .reindex(labels, fill_value=0)
    )

    df = seg_dist.reset_index()
    df.columns = ['segment', 'count']

    fig = px.bar(
        df,
        x='segment',
        y='count',
        labels={
            'segment': 'Number of Purchases',
            'count': 'Number of Customers'
        },
        color='count',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Customer Purchase Frequency',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Number of Purchases',
        yaxis_title='Number of Customers',

        showlegend=False,
        coloraxis_showscale=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_traces(
        texttemplate='%{y}',
        textposition='outside',
        textfont=dict(
            color='white',
            size=10
        ),

        marker_line_color='white',
        marker_line_width=0.5,

        hovertemplate=(
            '<b>%{x}</b><br>'
            'Customers: %{y:,}'
            '<extra></extra>'
        )
    )

    return fig

def create_top_customers_chart(top_customers):
    """2. Top Customers by Revenue"""

    if top_customers is None or top_customers.empty:
        return _empty_customer_figure(
            "No customer data available"
        )

    df = top_customers.copy()

    if "customer_id" not in df.columns:
        df = df.reset_index()

    # Limit to top 10
    df = (
        df.sort_values('revenue', ascending=False)
        .head(10)
        .copy()
    )

    df["customer_label"] = df["customer_id"].astype(str)

    fig = px.bar(
        df,
        x="revenue",
        y="customer_label",
        orientation="h",
        color="revenue",
        color_continuous_scale="Greens",
        labels={
            "revenue": "Revenue (₹)",
            "customer_label": ""
        }
    )

    fig.update_layout(
        height=400,
        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        title=dict(
            text="Top 10 Customers by Revenue",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        xaxis_title="Revenue (₹)",
        yaxis_title="",

        showlegend=False,
        coloraxis_showscale=False,

        margin=dict(
            l=70,
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
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white'),
        tickprefix='₹',
        tickformat=',.0f'
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white'),
        autorange="reversed"
    )

    fig.update_traces(
        texttemplate='₹%{x:,.0f}',
        textposition='outside',

        textfont=dict(
            color='white',
            size=10
        ),

        marker_line_color='white',
        marker_line_width=0.5,

        hovertemplate=(
            '<b>Customer: %{y}</b><br>'
            'Revenue: ₹%{x:,.0f}'
            '<extra></extra>'
        )
    )

    return fig

def create_clv_chart(clv_values):
    """3. Customer Lifetime Value Distribution"""

    if clv_values is None or len(clv_values) == 0:
        return create_empty_figure("No CLV data available")

    # Accept Series, list, or numpy array
    clv_values = pd.Series(clv_values).dropna()

    # Keep only valid positive values
    clv_values = clv_values[clv_values >= 0]

    if clv_values.empty:
        return create_empty_figure("No valid CLV data available")

    fig = px.histogram(
        clv_values,
        nbins=50,
        labels={
            'value': 'CLV (₹)',
            'count': 'Number of Customers'
        },
        color_discrete_sequence=['#764ba2']
    )

    mean_clv = clv_values.mean()

    fig.add_vline(
        x=mean_clv,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"Avg: ₹{mean_clv:,.0f}",
        annotation_position="top right",
        annotation_font=dict(
            color="#ef4444",
            size=10
        )
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Customer Lifetime Value Distribution',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Customer Lifetime Value (₹)',
        yaxis_title='Number of Customers',

        showlegend=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white'),
        tickprefix='₹',
        tickformat=',.0f'
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_traces(
        marker_line_color='white',
        marker_line_width=0.5,
        hovertemplate=(
            'CLV: ₹%{x:,.0f}<br>'
            'Customers: %{y:,}'
            '<extra></extra>'
        )
    )

    return fig

def create_customer_acquisition_chart(monthly_new):
    """4. Monthly New Customer Acquisition"""

    if monthly_new is None or monthly_new.empty:
        return _empty_customer_figure(
            "No customer acquisition data available"
        )

    df = monthly_new.reset_index()
    df.columns = ['month', 'new_customers']

    df['month'] = df['month'].astype(str)

    fig = px.line(
        df,
        x='month',
        y='new_customers',
        markers=True,
        labels={
            'month': 'Month',
            'new_customers': 'New Customers'
        },
        color_discrete_sequence=['#f59e0b']
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Monthly New Customer Acquisition',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Month',
        yaxis_title='New Customers',

        hovermode='x unified',
        showlegend=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickangle=45,
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_traces(
        line=dict(
            width=3,
            color='#f59e0b'
        ),

        marker=dict(
            size=8,
            color='#f59e0b',
            line=dict(
                color='white',
                width=1
            )
        ),

        hovertemplate=(
            '<b>%{x}</b><br>'
            'New Customers: %{y:,}'
            '<extra></extra>'
        )
    )

    return fig

def create_health_metrics_chart(health_metrics):
    """5. Business Health Metrics"""

    if not health_metrics:
        return _empty_customer_figure(
            "No business health metrics available"
        )

    df = pd.DataFrame({
        'metric': list(health_metrics.keys()),
        'value': list(health_metrics.values())
    })

    # Sort highest first
    df = df.sort_values(
        'value',
        ascending=False
    )

    fig = px.bar(
        df,
        x='value',
        y='metric',
        orientation='h',
        labels={
            'value': 'Score',
            'metric': ''
        },
        color='value',
        color_continuous_scale='Teal'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Business Health Metrics',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Score',
        yaxis_title='',

        showlegend=False,
        coloraxis_showscale=False,

        margin=dict(
            l=80,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        range=[0, 1],
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        autorange='reversed',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    # Target line
    fig.add_vline(
        x=0.5,
        line_dash="dash",
        line_color="#ef4444",

        annotation_text="Target (0.5)",

        annotation_position="top right",

        annotation_font=dict(
            color="#ef4444",
            size=10
        )
    )

    fig.update_traces(
        texttemplate='%{x:.2f}',
        textposition='outside',

        textfont=dict(
            color='white',
            size=10
        ),

        marker_line_color='white',
        marker_line_width=0.5,

        hovertemplate=(
            '<b>%{y}</b><br>'
            'Score: %{x:.2f}'
            '<extra></extra>'
        )
    )

    return fig