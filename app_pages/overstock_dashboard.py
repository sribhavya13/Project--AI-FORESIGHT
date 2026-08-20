import streamlit as st
import pandas as pd
from datetime import timedelta
import warnings

from utility.overstock_util import calculate_overstock_risk, calculate_overstock_metrics, \
    create_overstock_distribution_chart, create_high_overstock_category_chart, create_weeks_of_stock_histogram, \
    create_overstock_value_chart, create_risk_quadrant_chart
from utility.stock_out_util import calculate_stockout_risk

warnings.filterwarnings('ignore')

import api

@st.cache_data(ttl=3600)
def load_data():
    sku = pd.DataFrame(api.get_skus())
    daily_sales = api.get_daily_sales()
    inventory = pd.DataFrame(api.get_inventary())

    return sku, daily_sales, inventory


sku, daily_sales, inventory = load_data()


daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")

daily_sales_with_cat = daily_sales.copy()

daily_sales_with_cat['category'] = (
    daily_sales_with_cat['category'].fillna('Unknown')
)

last_30_days = daily_sales[daily_sales['date'] >= daily_sales['date'].max() - timedelta(days=30)]
sku_sales = last_30_days.groupby('sku_id')['units_sold'].sum().reset_index()
sku_sales.columns = ['sku_id', 'units_sold']

inventory_analysis = inventory.merge(sku, on='sku_id', how='left')
inventory_analysis['category'] = inventory_analysis['category'].fillna('Unknown')
inventory_analysis['stock_value'] = inventory_analysis['stock_on_hand'] * inventory_analysis['unit_price']


risk_analysis = inventory_analysis.merge(sku_sales, on='sku_id', how='left')
risk_analysis['units_sold'] = risk_analysis['units_sold'].fillna(0)

print("5. Before stockout calculation")
risk_analysis['stockout_risk'], risk_analysis['stock_cover'] = zip(
        *risk_analysis.apply(calculate_stockout_risk, axis=1)
    )
print("6. Stockout calculation completed")
risk_analysis['overstock_risk'], risk_analysis['weeks_of_stock'] = zip(
        *risk_analysis.apply(calculate_overstock_risk, axis=1)
    )
print("7. Overstock calculation completed")
risk_metrics = calculate_overstock_metrics(risk_analysis)
print("8. Metrics calculated")
print("Keys =", risk_metrics.keys())
def show_overstock_dashboard():
    """Display Overstock Dashboard with 9 KPIs"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📦 Overstock Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Identify products with excess inventory and dead stock
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
            "📊 Total SKUs",
            f"{risk_metrics['total_skus']:,}",
            help="Total number of SKUs analyzed"
        )

    with col2:
        st.metric(
            "🔴 HIGH Overstock",
            f"{risk_metrics['high_overstock']}",
            delta="Markdown Needed" if risk_metrics['high_overstock'] > 0 else "None",
            help="SKUs with > 12 weeks of stock"
        )

    with col3:
        st.metric(
            "🟡 MEDIUM Overstock",
            f"{risk_metrics['medium_overstock']}",
            help="SKUs with 8-12 weeks of stock"
        )

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "🟢 LOW Overstock",
            f"{risk_metrics['low_overstock']}",
            help="SKUs with 5-8 weeks of stock"
        )

    with col5:
        st.metric(
            "✅ NONE Overstock",
            f"{risk_metrics['none_overstock']}",
            help="SKUs with < 5 weeks of stock (Healthy)"
        )

    with col6:
        high_pct = (risk_metrics['high_overstock'] / risk_metrics['total_skus'] * 100) if risk_metrics[
                                                                                              'total_skus'] > 0 else 0
        st.metric(
            "📊 High Overstock %",
            f"{high_pct:.1f}%",
            delta="Below 10% is Safe" if high_pct < 10 else "Above Threshold",
            help="Percentage of SKUs with HIGH overstock"
        )

    # Row 3
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "💰 Overstock Value",
            f"₹{risk_metrics['high_overstock_value']:,.0f}",
            help="Total inventory value of HIGH overstock SKUs"
        )

    with col8:
        st.metric(
            "📈 Avg Weeks of Stock",
            f"{risk_metrics['avg_weeks_of_stock']:.1f}",
            help="Average weeks of stock across all SKUs"
        )

    with col9:
        st.metric(
            "💀 Dead Stock SKUs",
            f"{risk_metrics['zero_sales']}",
            delta="Clear Out!" if risk_metrics['zero_sales'] > 0 else "None",
            help="SKUs with zero sales in last 30 days"
        )

    st.divider()


    fig1 = create_overstock_distribution_chart(risk_analysis)
    st.plotly_chart(fig1, use_container_width=True)


    fig2 = create_high_overstock_category_chart(risk_analysis)
    st.plotly_chart(fig2, use_container_width=True)


    fig3 = create_weeks_of_stock_histogram(risk_analysis)
    st.plotly_chart(fig3, use_container_width=True)





    fig4 = create_overstock_value_chart(risk_analysis)
    st.plotly_chart(fig4, use_container_width=True)


    fig5 = create_risk_quadrant_chart(risk_analysis)
    st.plotly_chart(fig5, use_container_width=True)





