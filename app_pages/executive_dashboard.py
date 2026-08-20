"""
EXECUTIVE DASHBOARD - RetailPulse AI
Complete Dashboard with all metrics and charts
"""
from textwrap import dedent

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings

from utility.executive_dashboard import create_monthly_revenue_chart

warnings.filterwarnings('ignore')

import api


# ============================================
# DATA LOADING
# ============================================

@st.cache_data
def load_data():
    """Load all required data"""

    product_summary = api.get_product_summary()
    sales_summary = api.get_sales_summary()

    sku = pd.DataFrame(api.get_skus())
    daily_sales = pd.DataFrame(api.get_daily_sales())

    # Convert date
    daily_sales["date"] = pd.to_datetime(
        daily_sales["date"],
        errors="coerce"
    )

    # Make sure category exists
    if "category" not in daily_sales.columns:
        daily_sales["category"] = "Unknown"
    else:
        daily_sales["category"] = (
            daily_sales["category"].fillna("Unknown")
        )

    # Daily KPI dataframe
    daily = (
        daily_sales
        .groupby("date")
        .agg({
            "units_sold": "sum",
            "revenue": "sum",
            "unit_price": "mean"
        })
        .reset_index()
    )

    daily.columns = [
        "date",
        "units_sold",
        "revenue",
        "avg_price"
    ]

    # Daily category dataframe
    daily_category = (
        daily_sales
        .groupby(["date", "category"])
        .agg({
            "units_sold": "sum",
            "revenue": "sum",
            "unit_price": "mean"
        })
        .reset_index()
    )

    daily_category.columns = [
        "date",
        "category",
        "units_sold",
        "revenue",
        "avg_price"
    ]

    return {
        "sku": sku,
        "daily_sales": daily_sales,
        "daily_sales_with_cat": daily_sales,
        "daily": daily,
        "daily_category": daily_category,
        "product_summary": product_summary,
        "sales_summary": sales_summary
    }
# ============================================
# METRICS CALCULATION
# ============================================

def calculate_metrics(daily, daily_sales_with_cat):
    """Calculate all dashboard metrics"""

    total_revenue = daily['revenue'].sum()
    total_units = daily['units_sold'].sum()
    total_skus = daily_sales_with_cat['sku_id'].nunique()
    avg_order_value = total_revenue / len(daily) if len(daily) > 0 else 0

    # Monthly metrics
    daily['month_year'] = daily['date'].dt.to_period('M')
    monthly_rev = daily.groupby('month_year')['revenue'].sum()
    avg_monthly_revenue = monthly_rev.mean() if len(monthly_rev) > 0 else 0

    # Growth
    if len(monthly_rev) >= 2:
        first = monthly_rev.iloc[0]
        last = monthly_rev.iloc[-1]
        revenue_growth = ((last - first) / first * 100) if first != 0 else 0
    else:
        revenue_growth = 0

    # Date range
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


# ============================================
# CHART FUNCTIONS
# ============================================

def create_revenue_trend_chart(daily_sales):
    """Daily Revenue Trend Chart"""

    if daily_sales is None or len(daily_sales) == 0:
        return create_empty_figure("No revenue data available")

    daily_sales = daily_sales.copy()

    # Make sure date is datetime
    daily_sales["date"] = pd.to_datetime(
        daily_sales["date"],
        errors="coerce"
    )

    daily_sales = daily_sales.dropna(subset=["date"])

    # Aggregate daily revenue
    daily_rev = (
        daily_sales
        .groupby("date")["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    fig = px.line(
        daily_rev,
        x="date",
        y="revenue",
        title="Daily Revenue Trend",
        labels={
            "revenue": "Revenue (₹)",
            "date": "Date"
        },
        color_discrete_sequence=["#667eea"]
    )

    # Average revenue line
    avg_revenue = daily_rev["revenue"].mean()

    fig.add_hline(
        y=avg_revenue,
        line_dash="dash",
        line_color="#34d399",
        annotation_text=f"Avg: ₹{avg_revenue:,.0f}",
        annotation_position="bottom right",
        annotation_font=dict(
            color="white",
            size=12
        )
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
            text="Daily Revenue Trend",
            x=0.5,
            xanchor="center",
            y=0.95,
            yanchor="top",
            font=dict(
                color="white",
                size=20
            )
        ),

        # All general text
        font=dict(
            family="Arial",
            size=12,
            color="white"
        ),

        xaxis=dict(
            title=dict(
                text="Date",
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

            # Horizontal scrollbar / range slider
            rangeslider=dict(
                visible=True,
                bgcolor="#1a1f2b",
                bordercolor="#667eea",
                borderwidth=1,
                thickness=0.12
            ),

            # Range selector buttons
            rangeselector=dict(
                bgcolor="#1a1f2b",
                activecolor="#667eea",
                bordercolor="#667eea",
                font=dict(
                    color="white"
                ),
                buttons=[
                    dict(
                        count=7,
                        label="7D",
                        step="day",
                        stepmode="backward"
                    ),
                    dict(
                        count=30,
                        label="30D",
                        step="day",
                        stepmode="backward"
                    ),
                    dict(
                        count=90,
                        label="90D",
                        step="day",
                        stepmode="backward"
                    ),
                    dict(
                        step="all",
                        label="ALL"
                    )
                ]
            )
        ),

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

        hovermode="x unified",

        showlegend=False,

        margin=dict(
            l=60,
            r=30,
            t=70,
            b=40
        )
    )

    # =====================================================
    # LINE STYLE
    # =====================================================

    fig.update_traces(
        line=dict(
            color="#667eea",
            width=2.5
        ),

        hovertemplate=(
            "<b>Date:</b> %{x|%d %b %Y}"
            "<br><b>Revenue:</b> ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )

    return fig


def create_units_sold_chart(daily_sales):
    """Daily Units Sold Trend Chart"""

    if daily_sales is None or len(daily_sales) == 0:
        return create_empty_figure("No units data available")

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


def create_units_sold_chart(daily_sales):
    """Daily Units Sold Trend Chart"""

    if daily_sales is None or len(daily_sales) == 0:
        return create_empty_figure("No units data available")

    daily_sales = daily_sales.copy()

    # Make sure date is datetime
    daily_sales["date"] = pd.to_datetime(
        daily_sales["date"],
        errors="coerce"
    )

    daily_sales = daily_sales.dropna(subset=["date"])

    # Aggregate daily units
    daily_units = (
        daily_sales
        .groupby("date")["units_sold"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    fig = px.line(
        daily_units,
        x="date",
        y="units_sold",
        title="Daily Units Sold",
        labels={
            "units_sold": "Units Sold",
            "date": "Date"
        },
        color_discrete_sequence=["#f59e0b"]
    )

    # Average units line
    avg_units = daily_units["units_sold"].mean()

    fig.add_hline(
        y=avg_units,
        line_dash="dash",
        line_color="#34d399",
        annotation_text=f"Avg: {avg_units:,.0f}",
        annotation_position="bottom right",
        annotation_font=dict(
            color="white",
            size=12
        )
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
            text="Daily Units Sold",
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
                text="Date",
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
                bordercolor="#f59e0b",
                borderwidth=1,
                thickness=0.12
            ),

            # Quick date selection
            rangeselector=dict(
                bgcolor="#1a1f2b",
                activecolor="#f59e0b",
                bordercolor="#f59e0b",

                font=dict(
                    color="white"
                ),

                buttons=[
                    dict(
                        count=7,
                        label="7D",
                        step="day",
                        stepmode="backward"
                    ),

                    dict(
                        count=30,
                        label="30D",
                        step="day",
                        stepmode="backward"
                    ),

                    dict(
                        count=90,
                        label="90D",
                        step="day",
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
                text="Units Sold",
                font=dict(
                    color="white",
                    size=13
                )
            ),

            tickfont=dict(
                color="white"
            ),

            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.3)"
        ),

        hovermode="x unified",

        showlegend=False,

        margin=dict(
            l=60,
            r=30,
            t=70,
            b=40
        )
    )

    # =====================================================
    # LINE
    # =====================================================

    fig.update_traces(
        line=dict(
            color="#f59e0b",
            width=2.5
        ),

        hovertemplate=(
            "<b>Date:</b> %{x|%d %b %Y}"
            "<br><b>Units Sold:</b> %{y:,.0f}"
            "<extra></extra>"
        )
    )

    return fig


def create_category_revenue_chart(daily_category):
    """Category Revenue Horizontal Bar Chart"""

    if daily_category is None or len(daily_category) == 0:
        return create_empty_figure("No category data available")

    daily_category = daily_category.copy()

    # Make sure required columns exist
    if "category" not in daily_category.columns or "revenue" not in daily_category.columns:
        return create_empty_figure("Category or revenue data unavailable")

    # Remove missing categories
    daily_category["category"] = (
        daily_category["category"]
        .fillna("Unknown")
        .astype(str)
    )

    # Make revenue numeric
    daily_category["revenue"] = pd.to_numeric(
        daily_category["revenue"],
        errors="coerce"
    ).fillna(0)

    # Aggregate revenue by category
    cat_rev = (
        daily_category
        .groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .reset_index()
    )

    if cat_rev.empty:
        return create_empty_figure("No category revenue available")

    # =====================================================
    # CHART
    # =====================================================

    fig = px.bar(
        cat_rev,
        x="revenue",
        y="category",
        orientation="h",
        title="Revenue by Category (Top 8)",
        labels={
            "revenue": "Revenue (₹)",
            "category": "Category"
        },
        color="revenue",
        color_continuous_scale="Purples"
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
            text="Revenue by Category (Top 8)",
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

        # =================================================
        # Y AXIS
        # =================================================

        yaxis=dict(

            title=dict(
                text="",
                font=dict(
                    color="white"
                )
            ),

            tickfont=dict(
                color="white",
                size=12
            ),

            gridcolor="rgba(255,255,255,0.05)",

            # Highest category at top
            autorange="reversed"
        ),

        showlegend=False,

        coloraxis_showscale=False,

        margin=dict(
            l=80,
            r=80,
            t=70,
            b=50
        )
    )

    # =====================================================
    # BAR STYLE
    # =====================================================

    fig.update_traces(

        texttemplate="₹%{x:,.0f}",

        textposition="outside",

        textfont=dict(
            color="white",
            size=11
        ),

        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Revenue: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )

    return fig


def create_monthly_growth_chart(monthly_rev):
    """Monthly Revenue Growth Chart"""

    if monthly_rev is None or len(monthly_rev) < 2:
        return create_empty_figure("Not enough data for growth chart")

    # Calculate month-over-month growth
    growth = monthly_rev.pct_change() * 100

    df = growth.reset_index()

    df["month_year"] = df["month_year"].astype(str)

    df.columns = ["month_year", "growth"]

    df = df.dropna()

    if df.empty:
        return create_empty_figure("No growth data available")

    # Green for positive, red for negative
    colors = [
        "#34d399" if x >= 0 else "#f87171"
        for x in df["growth"]
    ]

    # =====================================================
    # CHART
    # =====================================================

    fig = px.bar(
        df,
        x="month_year",
        y="growth",
        title="Monthly Revenue Growth (%)",
        labels={
            "growth": "Growth (%)",
            "month_year": "Month"
        }
    )

    fig.update_traces(
        marker_color=colors,

        # Value shown above/below bars
        texttemplate="%{y:.1f}%",

        textposition="outside",

        textfont=dict(
            color="white",
            size=11
        ),

        hovertemplate=(
            "<b>Month:</b> %{x}"
            "<br><b>Growth:</b> %{y:.2f}%"
            "<extra></extra>"
        )
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
            text="Monthly Revenue Growth (%)",
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
                bordercolor="#667eea",
                borderwidth=1,
                thickness=0.12
            ),

            # Quick selection
            rangeselector=dict(
                bgcolor="#1a1f2b",
                activecolor="#667eea",
                bordercolor="#667eea",

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
                text="Growth (%)",
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

            ticksuffix="%"
        ),

        showlegend=False,

        margin=dict(
            l=60,
            r=40,
            t=70,
            b=50
        )
    )

    # =====================================================
    # ZERO LINE
    # =====================================================

    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="rgba(255,255,255,0.4)",
        line_width=1
    )

    return fig


def create_empty_figure(message):
    """Create empty figure with centered title and white text"""

    fig = go.Figure()

    fig.add_annotation(
        text=message,
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

        # Center title
        title=dict(
            text=message,
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                color="white"
            )
        ),

        # All text white
        font=dict(
            size=12,
            color="white"
        ),

        # Horizontal scrollbar
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bgcolor="#1a1d24",
                bordercolor="#667eea",
                borderwidth=1
            ),
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
            gridcolor="rgba(255,255,255,0.05)"
        ),

        yaxis=dict(
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
            gridcolor="rgba(255,255,255,0.05)"
        ),

        margin=dict(
            l=40,
            r=20,
            t=60,
            b=70
        )
    )

    return fig


# ============================================
# MAIN DASHBOARD
# ============================================

def show_executive_dashboard():
    """Display Executive Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📈 Executive Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Real-time business intelligence and key performance indicators
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # LOAD DATA
    # ============================================

    data = load_data()

    if data['daily'] is None or len(data['daily']) == 0:
        st.error("❌ No data available. Please check your data source.")
        if st.button("🔄 Retry Loading"):
            st.cache_data.clear()
            st.rerun()
        return

    # ============================================
    # CALCULATE METRICS
    # ============================================

    metrics = calculate_metrics(data['daily'], data['daily_sales_with_cat'])

    # ============================================
    # KPI ROW 1
    # ============================================

    st.markdown("""
                      <style>

                      /* Metric card */
                      [data-testid="stMetric"] {
                          background-color: white;
                          border: 1px solid #3b3b3b;
                          border-radius: 10px;
                          padding: 10px;
                          text-align: center;
                      }

                      /* Metric label */
                      [data-testid="stMetricLabel"] {
                          justify-content: center;
                      }

                      [data-testid="stMetricLabel"] p {
                          font-size: 12px !important;
                          font-weight: 500 !important;
                      }

                      /* Metric value */
                      [data-testid="stMetricValue"] {
                          font-size: 22px !important;
                          font-weight: 700 !important;
                      }

                      /* Reduce spacing */
                      div[data-testid="stMetric"] > div {
                          padding: 0 !important;
                          margin: 0 !important;
                      }

                      </style>
                      """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Total Revenue", f"₹{metrics['total_revenue']:,.0f}")

    with col2:
        st.metric("📦 Total Units Sold", f"{metrics['total_units']:,.0f}")

    with col3:
        st.metric("📊 Total SKUs", f"{metrics['total_skus']:,}")

    # ============================================
    # KPI ROW 2
    # ============================================

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("💵 Avg Order Value", f"₹{metrics['avg_order_value']:,.2f}")

    with col5:
        st.metric("📅 Avg Monthly Revenue", f"₹{metrics['avg_monthly_revenue']:,.0f}")

    with col6:
        delta_color = "normal" if metrics['revenue_growth'] >= 0 else "inverse"
        st.metric("📈 Revenue Growth", f"{metrics['revenue_growth']:.1f}%", delta_color=delta_color)

    # ============================================
    # KPI ROW 3
    # ============================================

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric("⏳ Analysis Period", f"{metrics['days']} Days")

    with col8:
        start = metrics.get('start_date')
        st.metric("📅 Start Date", start.strftime("%Y-%m-%d") if pd.notna(start) else "N/A")

    with col9:
        end = metrics.get('end_date')
        st.metric("📅 End Date", end.strftime("%Y-%m-%d") if pd.notna(end) else "N/A")

    st.divider()

    # ============================================
    # CHARTS
    # ============================================

    # Chart 1: Revenue Trend
    fig1 = create_revenue_trend_chart(data['daily_sales'])
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    # Chart 2: Units Sold Trend
    fig2 = create_units_sold_chart(data['daily_sales'])
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # Chart 3: Monthly Revenue
    fig3 = create_monthly_revenue_chart(metrics['monthly_rev'])
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    # Chart 4: Category Revenue
    fig4 = create_category_revenue_chart(data['daily_category'])
    st.plotly_chart(fig4, use_container_width=True)
    st.divider()

    # Chart 5: Monthly Growth
    fig5 = create_monthly_growth_chart(metrics['monthly_rev'])
    st.plotly_chart(fig5, use_container_width=True)



    # ============================================
    # FOOTER
    # ============================================

    st.caption(f"""
        **RetailPulse AI** | Executive Dashboard  
        Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by Zidio Data Science
        """)