import streamlit as st
import pandas as pd
import warnings

from utility.customer_insight_util import calculate_customer_metrics, create_customer_frequency_chart, \
    create_top_customers_chart, create_clv_chart, create_customer_acquisition_chart, create_health_metrics_chart

warnings.filterwarnings('ignore')

import api

daily_sales = pd.DataFrame(api.get_daily_sales())

daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

metrics = calculate_customer_metrics(daily_sales)
def show_customer_insights():
    """Display Customer & Business Insights Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>👥 Customer & Business Insights</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Comprehensive customer analytics and business health metrics
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
            "Average SLV",
            f"₹{metrics['avg_slv']:,.0f}"
        )

    with col2:
        st.metric(
            "Median SLV",
            f"₹{metrics['median_slv']:,.0f}"
        )

    with col3:
        st.metric(
            "Highest SLV",
            f"₹{metrics['max_slv']:,.0f}"
        )

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("💰 Top Customer", f"₹{metrics['top_customer_revenue']:,.0f}")

    with col5:
        st.metric("📈 Avg Customer Value", f"₹{metrics['avg_customer_value']:,.0f}")

    with col6:
        st.metric("🆕 Avg Monthly New", f"{metrics['avg_monthly_new']:.0f}")

    # Row 3
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric("📊 Total Revenue", f"₹{metrics['total_revenue']:,.0f}")

    with col8:
        st.metric("🏆 Max Purchases", f"{metrics['max_purchases']}")

    with col9:
        st.metric("📅 Daily Customers", f"{metrics['daily_customers']:.0f}")

    st.divider()

    fig1 = create_customer_frequency_chart(metrics['customer_frequency'])
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_top_customers_chart(metrics['top_customers'])
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_clv_chart(metrics["slv_values"])
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = create_customer_acquisition_chart(metrics['monthly_new'])
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = create_health_metrics_chart(metrics['health_metrics'])
    st.plotly_chart(fig5, use_container_width=True)

