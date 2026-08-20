import streamlit as st
import pandas as pd
import warnings

from utility.promo_util import process_promotion_data, calculate_promotion_metrics, create_promo_revenue_chart, \
    create_promo_type_chart, create_promo_target_chart, create_promo_avg_order_chart, create_promo_discount_distribution

warnings.filterwarnings('ignore')

import api

sku = pd.DataFrame(api.get_skus())
daily_sales = api.get_daily_sales()

promotions = pd.DataFrame(api.get_promotion())

daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")

daily_sales_with_cat = daily_sales.copy()

daily_sales_with_cat['category'] = (
    daily_sales_with_cat['category'].fillna('Unknown')
)

promo_sales, non_promo_sales, has_promo_file = process_promotion_data(daily_sales, promotions)
metrics = calculate_promotion_metrics(promo_sales, non_promo_sales, daily_sales, promotions)


def show_promotion_dashboard():
    """Display Promotion Dashboard with 9 KPIs"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>🎯 Promotion Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Analyze promotion effectiveness and impact on sales
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
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📋 Total Promotions",
            f"{metrics['total_promotions']}",
            help="Total number of promotions in the system"
        )

    with col2:
        st.metric(
            "🟢 Active Promotions",
            f"{metrics['active_promotions']}",
            delta="Live" if metrics['active_promotions'] > 0 else "None",
            help="Currently active promotions"
        )

    with col3:
        st.metric(
            "📊 Avg Discount",
            f"{metrics['avg_discount']:.1f}%",
            help="Average discount percentage across all promotions"
        )

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "💰 Promo Revenue",
            f"₹{metrics['promo_revenue']:,.0f}",
            help="Revenue from promotional sales"
        )

    with col5:
        st.metric(
            "📦 Promo Orders",
            f"{metrics['promo_orders']:,}",
            help="Number of orders with promotion"
        )

    with col6:
        st.metric(
            "📊 Promo Share",
            f"{metrics['promo_share']:.1f}%",
            help="Percentage of total revenue from promotions"
        )

    # Row 3
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "💵 Promo Avg",
            f"₹{metrics['promo_avg']:,.2f}",
            help="Average order value with promotion"
        )

    with col8:
        st.metric(
            "📈 Lift",
            f"{metrics['lift']:.1f}%",
            delta="Effective" if metrics['lift'] > 10 else "Moderate",
            help="Percentage increase in order value due to promotion"
        )

    with col9:
        st.metric(
            "📈 Total Revenue",
            f"₹{metrics['total_revenue']:,.0f}",
            help="Total revenue from all sales"
        )

    fig1 = create_promo_revenue_chart(metrics)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_promo_type_chart(promotions)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_promo_target_chart(promotions)
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = create_promo_avg_order_chart(metrics)
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = create_promo_discount_distribution(promotions)
    st.plotly_chart(fig5, use_container_width=True)



# ============================================


