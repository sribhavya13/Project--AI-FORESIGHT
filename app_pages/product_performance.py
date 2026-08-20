import streamlit as st
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import api
from utility.product_performance_util import (
    create_top_products_chart,
    create_price_distribution_chart,
    create_product_scatter_chart,
    create_top_units_chart,
    create_category_performance_chart
)

daily_sales = pd.DataFrame(api.get_daily_sales())
print(daily_sales.columns)
sku = pd.DataFrame(api.get_skus())

if not daily_sales.empty and 'date' in daily_sales.columns:
    daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")
    daily_sales = daily_sales.dropna(subset=["date"])

if not daily_sales.empty and 'sku_id' in daily_sales.columns and 'sku_id' in sku.columns:
    sku_cols = ['sku_id', 'sku_name', 'category', 'subcategory']
    sku_cols = [col for col in sku_cols if col in sku.columns]
    daily_sales = daily_sales.merge(sku[sku_cols], on='sku_id', how='left')

if not daily_sales.empty and 'unit_price' in daily_sales.columns:
    prices = daily_sales['unit_price'].dropna()
else:
    prices = pd.Series([0])

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        margin: 8px 0 0 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
    }
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.5);
    }
    .stats-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.3);
        padding: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 1rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def show_product_performance():
    """Display Product Performance Dashboard"""

    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>📦 Product Performance Dashboard</h1>
        <p>Comprehensive product analysis and performance metrics</p>
    </div>
    """, unsafe_allow_html=True)

    top_products = pd.DataFrame()
    concentration = 0

    if not daily_sales.empty and 'sku_id' in daily_sales.columns:
        top_products = daily_sales.groupby('sku_id').agg(
            units_sold=('units_sold', 'sum'),
            revenue=('revenue', 'sum')
        ).sort_values('revenue', ascending=False)

        top10 = top_products.head(10)

        if daily_sales['revenue'].sum() > 0:
            concentration = (top10['revenue'].sum() / daily_sales['revenue'].sum()) * 100
        else:
            concentration = 0
    else:
        top_products = pd.DataFrame()
        concentration = 0

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
        # ✅ Total SKUs from SKU master (not daily_sales)
        if not sku.empty:
            total_skus = sku['sku_id'].nunique()
        else:
            total_skus = len(top_products)
        st.metric(
            label="📦 Total SKUs",
            value=f"{total_skus:,}"
        )

    with col2:
        st.metric(
            label="🎯 Top 10 Concentration",
            value=f"{concentration:.1f}%"
        )

    with col3:
        # FIX: Safe access to top product
        if not top_products.empty:
            top_sku = str(top_products.index[0])
        else:
            top_sku = "N/A"
        st.metric(
            label="🏆 Best Selling SKU",
            value=top_sku
        )

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        if not top_products.empty:
            top_revenue = f"₹{top_products['revenue'].iloc[0]:,.0f}"
        else:
            top_revenue = "₹0"
        st.metric(
            label="💰 Top Product Revenue",
            value=top_revenue
        )

    with col5:
        if not top_products.empty:
            avg_revenue = f"₹{top_products['revenue'].mean():,.0f}"
        else:
            avg_revenue = "₹0"
        st.metric(
            label="📊 Avg Product Revenue",
            value=avg_revenue
        )

    with col6:
        if not top_products.empty:
            median_revenue = f"₹{top_products['revenue'].median():,.0f}"
        else:
            median_revenue = "₹0"
        st.metric(
            label="📈 Median Product Revenue",
            value=median_revenue
        )

    # Row 3
    col7, col8, col9 = st.columns(3)

    with col7:
        if not prices.empty:
            max_price = f"₹{prices.max():,.2f}"
        else:
            max_price = "₹0.00"
        st.metric(
            label="⬆️ Highest Price",
            value=max_price
        )

    with col8:
        if not prices.empty:
            min_price = f"₹{prices.min():,.2f}"
        else:
            min_price = "₹0.00"
        st.metric(
            label="⬇️ Lowest Price",
            value=min_price
        )

    with col9:
        if not daily_sales.empty and 'sku_id' in daily_sales.columns:
            total_products = daily_sales['sku_id'].nunique()
        else:
            total_products = 0
        st.metric(
            label="📋 Total Products",
            value=f"{total_products:,}"
        )

    st.markdown("---")

    fig1 = create_top_products_chart(daily_sales, top_n=10)
    st.plotly_chart(fig1, use_container_width=True)

    fig3 = create_price_distribution_chart(daily_sales)
    st.plotly_chart(fig3, use_container_width=True)

    # ============================================
    # CHARTS ROW 2
    # ============================================


    fig2 = create_product_scatter_chart(daily_sales)
    st.plotly_chart(fig2, use_container_width=True)

# ============================================
# CHARTS ROW 3
# ============================================

    fig4 = create_top_units_chart(daily_sales, top_n=10)
    st.plotly_chart(fig4, use_container_width=True)

    # fig5 = create_category_performance_chart(daily_sales)
    # st.plotly_chart(fig5, use_container_width=True)
    #





