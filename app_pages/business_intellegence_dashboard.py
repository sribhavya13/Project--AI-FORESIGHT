import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

from utility.business_intellegence_util import calculate_bi_metrics, create_kpi_card, create_revenue_trend, \
    create_sales_by_category, create_top_products, create_daily_sales_distribution, create_monthly_trend, \
    create_channel_distribution

warnings.filterwarnings('ignore')

import api


@st.cache_data(ttl=3600)
def load_bi_data():
    """Load all data for BI dashboard"""
    try:
        daily_sales = pd.DataFrame(api.get_daily_sales())
        sku = pd.DataFrame(api.get_skus())
        inventory = pd.DataFrame(api.get_inventary())

        # Convert dates
        daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

        return daily_sales, sku, inventory
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def show_bi_dashboard():
    """Display Business Intelligence Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.05);
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📊 Business Intelligence Dashboard</h1>
        <p style='color: rgba(255,255,255,0.8) !important; margin: 8px 0 0 0;'>
            Power BI Style Analytics & Insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # LOAD DATA
    # ============================================================

    with st.spinner("Loading data..."):
        daily_sales, sku, inventory = load_bi_data()

    if daily_sales.empty:
        st.error("No data available. Please check your data source.")
        return

    # ============================================================
    # FILTERS (Power BI Style)
    # ============================================================

    st.markdown("### 🔍 Filters")
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
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Date range
        min_date = daily_sales['date'].min()
        max_date = daily_sales['date'].max()
        date_range = st.date_input(
            "📅 Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        # Category filter
        if 'category' in daily_sales.columns:
            categories = ['All'] + sorted(daily_sales['category'].dropna().unique().tolist())
            selected_category = st.selectbox("📂 Category", categories)
        else:
            selected_category = 'All'

    with col3:
        # Channel filter
        if 'channel' in daily_sales.columns:
            channels = ['All'] + sorted(daily_sales['channel'].dropna().unique().tolist())
            selected_channel = st.selectbox("📡 Channel", channels)
        else:
            selected_channel = 'All'

    with col4:
        # Aggregation period
        period = st.selectbox("📈 Period", ['Daily', 'Weekly', 'Monthly'])

    # ============================================================
    # APPLY FILTERS
    # ============================================================

    df_filtered = daily_sales.copy()

    # Date filter
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['date'] >= pd.to_datetime(date_range[0])) &
            (df_filtered['date'] <= pd.to_datetime(date_range[1]))
            ]

    # Category filter
    if selected_category != 'All' and 'category' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['category'] == selected_category]

    # Channel filter
    if selected_channel != 'All' and 'channel' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['channel'] == selected_channel]

    # ============================================================
    # KPIs (Power BI Style)
    # ============================================================

    metrics = calculate_bi_metrics(df_filtered)

    st.markdown("### 📈 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_kpi_card("Total Revenue", f"₹{metrics.get('total_revenue', 0):,.0f}", icon="💰")

    with col2:
        create_kpi_card("Total Units", f"{metrics.get('total_units', 0):,}", icon="📦")

    with col3:
        create_kpi_card("Avg Order Value", f"₹{metrics.get('avg_order_value', 0):,.0f}", icon="🛒")

    with col4:
        create_kpi_card("Unique SKUs", f"{metrics.get('unique_skus', 0):,}", icon="🏷️")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        create_kpi_card("Revenue (Last 30d)", f"₹{metrics.get('revenue_last_30', 0):,.0f}", icon="📊")

    with col6:
        create_kpi_card("Units (Last 30d)", f"{metrics.get('units_last_30', 0):,}", icon="📦")

    with col7:
        avg_daily = metrics.get('avg_daily_revenue', 0)
        create_kpi_card("Avg Daily Revenue", f"₹{avg_daily:,.0f}", icon="📈")

    with col8:
        customers = metrics.get('unique_customers', 0)
        create_kpi_card("Unique Customers", f"{customers:,}", icon="👥")

    st.divider()

    # ============================================================
    # CHARTS (Power BI Style Layout)
    # ============================================================

    # Row 1: Revenue Trend (full width)
    st.markdown("### 📊 Revenue Analysis")

    fig_revenue = create_revenue_trend(df_filtered, period)
    st.plotly_chart(fig_revenue, use_container_width=True)

    # Row 2: Two charts side by side
    col1, col2 = st.columns(2)

    with col1:
        fig_category = create_sales_by_category(df_filtered)
        st.plotly_chart(fig_category, use_container_width=True)

    with col2:
        fig_products = create_top_products(df_filtered)
        st.plotly_chart(fig_products, use_container_width=True)

    # Row 3: Two more charts
    col1, col2 = st.columns(2)

    with col1:
        fig_monthly = create_monthly_trend(df_filtered)
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col2:
        fig_channel = create_channel_distribution(df_filtered)
        st.plotly_chart(fig_channel, use_container_width=True)

    # Row 4: Heatmap (full width)
    st.markdown("### 🌡️ Sales Distribution")
    fig_heatmap = create_daily_sales_distribution(df_filtered)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # ============================================================
    # DATA TABLE (Power BI Style)
    # ============================================================

    st.markdown("### 📋 Data Explorer")

    # Summary table
    if not df_filtered.empty:
        summary = df_filtered.groupby('date').agg({
            'units_sold': 'sum',
            'revenue': 'sum'
        }).reset_index().tail(30)

        summary['revenue'] = summary['revenue'].apply(lambda x: f"₹{x:,.0f}")
        summary['units_sold'] = summary['units_sold'].apply(lambda x: f"{x:,}")

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                'date': 'Date',
                'units_sold': 'Units Sold',
                'revenue': 'Revenue'
            }
        )

    # ============================================================
    # FOOTER
    # ============================================================

    st.caption(f"""
    **Project FORESIGHT** | Business Intelligence Dashboard  
    Data updated: {datetime.now().strftime('%B %d, %Y %H:%M')} | {len(df_filtered):,} records
    """)
