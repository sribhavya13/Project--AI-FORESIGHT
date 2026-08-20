import streamlit as st
import pandas as pd
import warnings

from utility.recommendation_util import generate_recommendations, create_priority_chart, create_category_chart, \
    create_impact_chart, create_action_chart

warnings.filterwarnings('ignore')

import api

daily_sales = pd.DataFrame(api.get_daily_sales())
sku = pd.DataFrame(api.get_skus())

daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

rec_df, high_risk_skus, high_overstock, top_cat, peak_season = generate_recommendations(
    daily_sales, sku
)

def show_recommendations():
    """Display Executive Recommendation Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>💡 Executive Recommendations</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Actionable insights and strategic recommendations
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
        st.metric("📋 Total Recommendations", f"{len(rec_df)}")

    with col2:
        st.metric("🔴 High Priority", f"{len(rec_df[rec_df['priority'] == 1])}")

    with col3:
        total_value = 0
        if len(high_risk_skus) > 0:
            total_value += high_risk_skus['stock_value'].sum()
        if len(high_overstock) > 0:
            total_value += high_overstock['stock_value'].sum()
        st.metric("💰 Value at Risk", f"₹{total_value:,.0f}")

    col4, col5, col6 = st.columns(3)

    with col4:
        categories = rec_df['category'].nunique()
        st.metric("📊 Categories", f"{categories}")

    with col5:
        unique_actions = rec_df['action'].nunique()
        st.metric("🎯 Action Types", f"{unique_actions}")

    with col6:
        recovery = total_value * 0.3
        st.metric("💵 Potential Recovery", f"₹{recovery:,.0f}")

    col7, col8, col9 = st.columns(3)

    with col7:
        stockout_count = len(high_risk_skus) if len(high_risk_skus) > 0 else 0
        st.metric("⚠️ Stockout Risk", f"{stockout_count} SKUs")

    with col8:
        overstock_count = len(high_overstock) if len(high_overstock) > 0 else 0
        st.metric("📦 Overstock", f"{overstock_count} SKUs")

    with col9:
        st.metric("🏷️ Top Category", f"{top_cat if top_cat != 'N/A' else 'N/A'}")

    st.divider()

    fig1 = create_priority_chart(rec_df)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_category_chart(rec_df)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_impact_chart(rec_df)
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = create_action_chart(rec_df)
    st.plotly_chart(fig4, use_container_width=True)

