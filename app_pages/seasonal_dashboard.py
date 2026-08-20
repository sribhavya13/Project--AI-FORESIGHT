import streamlit as st
import pandas as pd
import warnings

from utility.seasonal_util import calculate_seasonality_metrics, create_monthly_revenue_chart, \
    create_monthly_units_chart, create_seasonal_pie_chart, create_dow_chart, create_season_category_chart

warnings.filterwarnings('ignore')

import api

sku = pd.DataFrame(api.get_skus())
daily_sales = api.get_daily_sales()

daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")

if 'season' not in daily_sales.columns:
        daily_sales['season'] = daily_sales['date'].dt.month.map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })

daily_sales_with_cat = daily_sales.copy()

daily_sales_with_cat['category'] = (
    daily_sales_with_cat['category'].fillna('Unknown')
)
metrics = calculate_seasonality_metrics(daily_sales)

def show_seasonality_dashboard():
    """Display Seasonality Dashboard with 9 KPIs"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #34d399 0%, #059669 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📅 Seasonality Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Analyze seasonal patterns, monthly trends, and day-of-week performance
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
            "🏆 Peak Month",
            metrics['peak_month'],
            help="Month with highest revenue"
        )

    with col2:
        st.metric(
            "🌤️ Peak Season",
            metrics['peak_season'],
            help="Season with highest revenue"
        )

    with col3:
        st.metric(
            "📅 Best Day",
            metrics['best_day'],
            help="Day of week with highest revenue"
        )

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "📉 Worst Day",
            metrics['worst_day'],
            help="Day of week with lowest revenue"
        )

    with col5:
        st.metric(
            "💰 Avg Monthly Revenue",
            f"₹{metrics['avg_monthly_revenue']:,.0f}",
            help="Average revenue per month"
        )

    with col6:
        st.metric(
            "📦 Avg Monthly Units",
            f"{metrics['avg_monthly_units']:,.0f}",
            help="Average units sold per month"
        )

    # Row 3
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "📊 Total Revenue",
            f"₹{metrics['total_revenue']:,.0f}",
            help="Total revenue across all periods"
        )

    with col8:
        st.metric(
            "📦 Total Units",
            f"{metrics['total_units']:,.0f}",
            help="Total units sold across all periods"
        )

    with col9:
        # Calculate peak month share
        peak_revenue = \
        metrics['monthly_metrics'][metrics['monthly_metrics']['month_name'] == metrics['peak_month']]['revenue'].iloc[0]
        peak_share = (peak_revenue / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0
        st.metric(
            "📈 Peak Month Share",
            f"{peak_share:.1f}%",
            help="Percentage of total revenue in peak month"
        )

    fig1 = create_monthly_revenue_chart(metrics['monthly_metrics'])
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_monthly_units_chart(metrics['monthly_metrics'])
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_seasonal_pie_chart(metrics['seasonal_metrics'])
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = create_dow_chart(metrics['dow_metrics'])
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = create_season_category_chart(metrics['season_cat'])
    st.plotly_chart(fig5, use_container_width=True)




