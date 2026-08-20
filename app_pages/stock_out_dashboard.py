import streamlit as st
import pandas as pd
from datetime import timedelta
import warnings

import api
from utility.stock_out_util import calculate_stockout_risk, calculate_risk_metrics, create_risk_distribution_chart, \
    create_high_risk_category_chart, create_stock_cover_histogram, create_risk_value_chart, create_risk_scatter_chart

warnings.filterwarnings('ignore')

sku = pd.DataFrame(api.get_skus())
daily_sales = api.get_daily_sales()
inventory = pd.DataFrame(api.get_inventary())
daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")

daily_sales_with_cat = daily_sales.copy()

daily_sales_with_cat['category'] = (
    daily_sales_with_cat['category'].fillna('Unknown')
)

last_30_days = daily_sales[daily_sales['date'] >= daily_sales['date'].max() - timedelta(days=30)]
sku_sales = last_30_days.groupby('sku_id')['units_sold'].sum().reset_index()
sku_sales.columns = ['sku_id', 'units_sold']

# Merge with SKU
inventory_analysis = inventory.merge(sku, on='sku_id', how='left')
inventory_analysis['category'] = inventory_analysis['category'].fillna('Unknown')
inventory_analysis['stock_value'] = inventory_analysis['stock_on_hand'] * inventory_analysis['unit_price']

risk_analysis = inventory_analysis.merge(sku_sales, on='sku_id', how='left')
risk_analysis['units_sold'] = risk_analysis['units_sold'].fillna(0)

risk_analysis['stockout_risk'], risk_analysis['stock_cover'] = zip(
        *risk_analysis.apply(calculate_stockout_risk, axis=1)
    )

risk_metrics = calculate_risk_metrics(risk_analysis)


def show_stockout_risk():
    """Display Stockout Risk Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>⚠️ Stockout Risk Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Identify products at risk of running out of stock
        </p>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("### 📊 CATEGORY METRICS")

    # Row 1: 3 columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "📊 Total SKUs Analyzed",
            f"{risk_metrics['total_skus']:,}",
            help="Total number of SKUs evaluated for stockout risk"
        )
    with col2:
        st.metric(
            "🔴 HIGH Risk SKUs",
            f"{risk_metrics['high_risk']}",
            delta="Urgent" if risk_metrics['high_risk'] > 0 else "None",
            help="SKUs with stock cover ≤ 30% of lead time demand"
        )
    with col3:
        st.metric(
            "🟡 MEDIUM Risk SKUs",
            f"{risk_metrics['medium_risk']}",
            help="SKUs with stock cover between 30% and 60% of lead time demand"
        )

    # Row 2: 3 columns
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(
            "🟢 LOW Risk SKUs",
            f"{risk_metrics['low_risk']}",
            help="SKUs with stock cover between 60% and 100% of lead time demand"
        )
    with col5:
        st.metric(
            "✅ NONE Risk SKUs",
            f"{risk_metrics['none_risk']}",
            help="SKUs with stock cover > 100% of lead time demand (Safe)"
        )
    with col6:
        st.metric(
            "💀 Critical SKUs",
            f"{risk_metrics.get('critical_skus', 0)}",
            delta="⚠️ Urgent" if risk_metrics.get('critical_skus', 0) > 0 else "OK",
            help="SKUs with zero stock (stock_on_hand = 0)"
        )

    # Row 3: 2 columns
    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric(
            "💰 At-Risk Value",
            f"₹{risk_metrics['high_risk_value']:,.0f}",
            help="Total inventory value of HIGH risk SKUs"
        )
    with col8:
        st.metric(
            "📈 Avg Stock Cover",
            f"{risk_metrics['avg_stock_cover']:.2f}",
            help="Average stock cover (days of demand) across all SKUs"
        )
    with col9:
        risk_percent = (risk_metrics['high_risk'] / risk_metrics['total_skus'] * 100) if risk_metrics[
                                                                                             'total_skus'] > 0 else 0
        st.metric(
            "📊 High Risk %",
            f"{risk_percent:.1f}%",
            delta="Below 15% is Safe" if risk_percent < 15 else "Above Threshold",
            help="Percentage of SKUs at HIGH stockout risk"
        )

    fig1 = create_risk_distribution_chart(risk_analysis)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_high_risk_category_chart(risk_analysis)
    st.plotly_chart(fig2, width="stretch")

    fig3 = create_stock_cover_histogram(risk_analysis)
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = create_risk_value_chart(risk_analysis)
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = create_risk_scatter_chart(risk_analysis)
    st.plotly_chart(fig5, use_container_width=True)