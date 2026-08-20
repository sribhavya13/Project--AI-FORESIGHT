import streamlit as st
import pandas as pd
import warnings

from utility.inventory_opt_utils import calculate_inventory_metrics, create_stockout_risk_chart, \
    create_days_of_stock_chart, create_reorder_chart, create_overstock_chart, create_reorder_table

warnings.filterwarnings('ignore')

import api

sku = pd.DataFrame(api.get_skus())
daily_sales = pd.DataFrame(api.get_daily_sales())
inventory = pd.DataFrame(api.get_inventary())

daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')


def show_inventory_optimization():
    """Display Inventory Optimization Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📦 Inventory Optimization</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Stockout Risk + Reorder Recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)



    if inventory.empty:
        st.error("❌ No inventory data available.")
        return

    # Calculate metrics
    inventory_analysis, reorder_recs, overstock_skus = calculate_inventory_metrics(daily_sales, inventory, sku)

    # ============================================
    # 9 KPI CARDS - 3x3 Grid
    # ============================================

    total_skus = len(inventory_analysis)
    high_risk = len(inventory_analysis[inventory_analysis['stockout_risk'] == 'HIGH'])
    medium_risk = len(inventory_analysis[inventory_analysis['stockout_risk'] == 'MEDIUM'])
    low_risk = len(inventory_analysis[inventory_analysis['stockout_risk'] == 'LOW'])
    none_risk = len(inventory_analysis[inventory_analysis['stockout_risk'] == 'NONE'])
    reorder_count = len(reorder_recs)
    overstock_count = len(overstock_skus)
    avg_days = inventory_analysis['days_of_stock'].mean()
    total_stock_value = inventory_analysis['stock_value'].sum()

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
        st.metric("📦 Total SKUs", f"{total_skus:,}")

    with col2:
        st.metric("🔴 High Risk", f"{high_risk}", delta="Urgent" if high_risk > 0 else "None")

    with col3:
        st.metric("🟡 Medium Risk", f"{medium_risk}")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("📦 Reorder Needed", f"{reorder_count}")

    with col5:
        st.metric("📦 Overstocked", f"{overstock_count}")

    with col6:
        st.metric("📈 Avg Days of Stock", f"{avg_days:.1f}")

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric("🟢 Low Risk", f"{low_risk}")

    with col8:
        st.metric("✅ None Risk", f"{none_risk}")

    with col9:
        st.metric("💰 Stock Value", f"₹{total_stock_value:,.0f}")

    st.divider()


    fig1 = create_stockout_risk_chart(inventory_analysis)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_days_of_stock_chart(inventory_analysis)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_reorder_chart(reorder_recs)
    st.plotly_chart(fig3, use_container_width=True)


    # ============================================
    # CHARTS ROW 2 - 2 Charts + Summary
    # ============================================

    fig4 = create_overstock_chart(overstock_skus)
    st.plotly_chart(fig4, use_container_width=True)


    st.divider()

    # ============================================
    # REORDER TABLE
    # ============================================

    create_reorder_table(reorder_recs)