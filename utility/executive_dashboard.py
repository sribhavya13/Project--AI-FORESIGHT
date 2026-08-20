"""
EXECUTIVE DASHBOARD - Utility Functions
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def calculate_metrics(daily, daily_sales_with_cat):
    """Calculate all dashboard metrics"""

    total_revenue = daily['revenue'].sum()
    total_units = daily['units_sold'].sum()
    total_skus = daily_sales_with_cat['sku_id'].nunique()
    avg_order_value = total_revenue / len(daily) if len(daily) > 0 else 0

    daily['month_year'] = daily['date'].dt.to_period('M')
    monthly_rev = daily.groupby('month_year')['revenue'].sum()
    avg_monthly_revenue = monthly_rev.mean() if len(monthly_rev) > 0 else 0

    if len(monthly_rev) >= 2:
        first = monthly_rev.iloc[0]
        last = monthly_rev.iloc[-1]
        revenue_growth = ((last - first) / first * 100) if first != 0 else 0
    else:
        revenue_growth = 0

    start_date = daily['date'].min()
    end_date = daily['date'].max()
    days = (end_date - start_date).days

    return {
        'total_revenue': total_revenue,
        'total_units': total_units,
        'total_skus': total_skus,
        'avg_order_value': avg_order_value,
        'avg_monthly_revenue': avg_monthly_revenue,
        'revenue_growth': revenue_growth,
        'monthly_rev': monthly_rev,
        'start_date': start_date,
        'end_date': end_date,
        'days': days
    }


def create_revenue_trend_chart(daily_sales):
    """Daily Revenue Trend Chart"""

    daily_rev = daily_sales.groupby('date')['revenue'].sum().reset_index()

    fig = px.line(
        daily_rev,
        x='date',
        y='revenue',
        title='Daily Revenue Trend',
        labels={'revenue': 'Revenue (₹)', 'date': 'Date'},
        color_discrete_sequence=['#667eea']
    )

    avg_revenue = daily_rev['revenue'].mean()
    fig.add_hline(
        y=avg_revenue,
        line_dash="dash",
        line_color="#34d399",
        annotation_text=f"Avg: ₹{avg_revenue:,.0f}",
        annotation_position="bottom right"
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        xaxis_title="Date",
        yaxis_title="Revenue (₹)",
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(size=12, color='white')
    )

    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', tickprefix='₹', tickformat=',.0f')
    fig.update_traces(line=dict(width=2))

    return fig


def create_units_sold_chart(daily_sales):
    """Daily Units Sold Trend Chart"""

    daily_units = daily_sales.groupby('date')['units_sold'].sum().reset_index()

    fig = px.line(
        daily_units,
        x='date',
        y='units_sold',
        title='Daily Units Sold',
        labels={'units_sold': 'Units Sold', 'date': 'Date'},
        color_discrete_sequence=['#f59e0b']
    )

    avg_units = daily_units['units_sold'].mean()
    fig.add_hline(
        y=avg_units,
        line_dash="dash",
        line_color="#34d399",
        annotation_text=f"Avg: {avg_units:,.0f}",
        annotation_position="bottom right"
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        xaxis_title="Date",
        yaxis_title="Units Sold",
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(size=12, color='white')
    )

    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_traces(line=dict(width=2))

    return fig


def create_monthly_revenue_chart(monthly_rev):
    """Monthly Revenue Bar Chart"""

    if monthly_rev is None or len(monthly_rev) == 0:
        return create_empty_figure("No monthly revenue data available")

    df = monthly_rev.reset_index().copy()

    # Convert month to string
    df["month_year"] = df["month_year"].astype(str)

    # Make revenue numeric
    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce"
    ).fillna(0)

    # =====================================================
    # CHART
    # =====================================================

    fig = px.bar(
        df,
        x="month_year",
        y="revenue",
        title="Monthly Revenue",
        labels={
            "revenue": "Revenue (₹)",
            "month_year": "Month"
        },
        color="revenue",
        color_continuous_scale="Greens"
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        height=450,

        template="plotly_dark",

        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",

        # Center title
        title=dict(
            text="Monthly Revenue",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                color="white",
                size=20
            )
        ),

        # All text white
        font=dict(
            family="Arial",
            size=12,
            color="white"
        ),

        # =================================================
        # X AXIS
        # =================================================

        xaxis=dict(

            title=dict(
                text="Month",
                font=dict(
                    color="white",
                    size=13
                )
            ),

            tickfont=dict(
                color="white"
            ),

            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.3)",

            # Scrollbar
            rangeslider=dict(
                visible=True,
                bgcolor="#1a1f2b",
                bordercolor="#22c55e",
                borderwidth=1,
                thickness=0.12
            ),

            # Quick selection
            rangeselector=dict(
                bgcolor="#1a1f2b",
                activecolor="#22c55e",
                bordercolor="#22c55e",

                font=dict(
                    color="white"
                ),

                buttons=[
                    dict(
                        count=6,
                        label="6M",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(
                        count=12,
                        label="1Y",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(
                        count=24,
                        label="2Y",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(
                        step="all",
                        label="ALL"
                    )
                ]
            )
        ),

        # =================================================
        # Y AXIS
        # =================================================

        yaxis=dict(

            title=dict(
                text="Revenue (₹)",
                font=dict(
                    color="white",
                    size=13
                )
            ),

            tickfont=dict(
                color="white"
            ),

            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.3)",

            tickprefix="₹",
            tickformat=",.0f"
        ),

        showlegend=False,

        coloraxis_showscale=False,

        margin=dict(
            l=70,
            r=50,
            t=70,
            b=60
        )
    )

    # =====================================================
    # BAR STYLE
    # =====================================================

    fig.update_traces(

        texttemplate="₹%{y:,.0f}",

        textposition="outside",

        textfont=dict(
            color="white",
            size=11
        ),

        hovertemplate=(
            "<b>Month:</b> %{x}"
            "<br><b>Revenue:</b> ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )

    return fig


def create_category_revenue_chart(daily_category):
    """Category Revenue Horizontal Bar Chart"""

    cat_rev = daily_category.groupby('category')['revenue'].sum().sort_values(ascending=False).head(8).reset_index()

    fig = px.bar(
        cat_rev,
        x='revenue',
        y='category',
        orientation='h',
        title='Revenue by Category (Top 8)',
        labels={'revenue': 'Revenue (₹)', 'category': 'Category'},
        color='revenue',
        color_continuous_scale='Purples'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        xaxis_title="Revenue (₹)",
        yaxis_title="",
        showlegend=False,
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(size=12, color='white')
    )

    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', tickprefix='₹', tickformat=',.0f')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', autorange='reversed')
    fig.update_traces(texttemplate='₹%{x:,.0f}', textposition='outside', textfont=dict(color='white', size=10))

    return fig


def create_monthly_growth_chart(monthly_rev):
    """Monthly Revenue Growth Chart"""

    growth = monthly_rev.pct_change() * 100
    df = growth.reset_index()
    df['month_year'] = df['month_year'].astype(str)
    df.columns = ['month_year', 'growth']
    df = df.dropna()

    colors = ['#34d399' if x >= 0 else '#f87171' for x in df['growth']]

    fig = px.bar(
        df,
        x='month_year',
        y='growth',
        title='Monthly Revenue Growth (%)',
        labels={'growth': 'Growth (%)', 'month_year': 'Month'}
    )

    fig.update_traces(marker_color=colors)

    fig.update_layout(
        height=400,
        template='plotly_dark',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        xaxis_title="Month",
        yaxis_title="Growth (%)",
        showlegend=False,
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(size=12, color='white')
    )

    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.3)", line_width=1)
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside', textfont=dict(color='white', size=10))

    return fig