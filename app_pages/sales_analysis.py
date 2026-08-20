import streamlit as st
import pandas as pd

import api
from utility.sales_analysis_util import create_sales_by_day_chart, create_store_performance_chart, \
    create_weekly_sales_trend, create_quarterly_sales_chart, create_order_value_distribution

sku = pd.DataFrame(api.get_skus())

daily_sales = pd.DataFrame(api.get_daily_sales())
print("daily_sales columns:", daily_sales.columns.tolist())
print("daily_sales shape:", daily_sales.shape)
daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")

daily_sales = daily_sales.groupby(['date', 'store_id']).agg({
    'revenue': 'sum',
    'units_sold': 'sum',
    'unit_price': 'mean',
    'sku_id': 'nunique'
}).reset_index()


daily_sales['day_name'] = daily_sales['date'].dt.day_name()
daily_sales['month'] = daily_sales['date'].dt.month
daily_sales['quarter'] = daily_sales['date'].dt.quarter
daily_sales['week'] = daily_sales['date'].dt.isocalendar().week
daily_sales['month_year'] = daily_sales['date'].dt.to_period('M')

# Calculate metrics
total_revenue = daily_sales['revenue'].sum()
total_orders = len(daily_sales)
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

sales_by_day = daily_sales.groupby('day_name')['revenue'].sum().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)
peak_sales_value = sales_by_day.max()

store_sales = (
    daily_sales.groupby("store_id")["revenue"]
    .sum()
    .sort_values(ascending=False)
)
best_store = store_sales.index[0]
best_store_revenue = store_sales.iloc[0]

def show_sales_analytics():
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
            .customer-block {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                padding: 1.2rem;
                border-radius: 12px;
                border-left: 4px solid #f59e0b;
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

    st.markdown("""
           <div class='main-header'>
               <h1>💰 Sales Analytics Dashboard</h1>
               <p>Comprehensive sales analysis and performance metrics</p>
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
            label="💰 Total Sales",
            value=f"₹{total_revenue:,.0f}"
        )

    with col2:
        st.metric(
            label="🧾 Total Orders",
            value=f"{len(daily_sales):,}"
        )

    with col3:
        st.metric(
            label="💵 Average Order Value",
            value=f"₹{avg_order_value:,.2f}"
        )

    # ==============================
    # SALES SUMMARY ROW 2
    # ==============================

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            label="📅 Peak Sales Day",
            value=str(sales_by_day.idxmax())
        )

    with col5:
        st.metric(
            label="🏬 Best Store",
            value=f"Store {store_sales.index[0]}"
        )

    with col6:
        st.metric(
            label="📦 Total SKUs Sold",
            value=f"{daily_sales['sku_id'].nunique():,}"
        )

    # ==============================
    # SALES SUMMARY ROW 3
    # ==============================

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            label="📈 Highest Sales Day Revenue",
            value=f"₹{sales_by_day.max():,.0f}"
        )

    with col8:
        st.metric(
            label="🏪 Total Stores",
            value=f"{daily_sales['store_id'].nunique():,}"
        )

    with col9:
        st.metric(
            label="📊 Total Transactions",
            value=f"{len(daily_sales):,}"
        )
    st.markdown("---")


    fig1 = create_sales_by_day_chart(daily_sales)
    st.plotly_chart(fig1, use_container_width=True)


    fig2 = create_store_performance_chart(daily_sales)
    st.plotly_chart(fig2, use_container_width=True)






    fig3 = create_weekly_sales_trend(daily_sales)
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = create_quarterly_sales_chart(daily_sales)
    st.plotly_chart(fig4, use_container_width=True)


    fig5 = create_order_value_distribution(daily_sales)
    st.plotly_chart(fig5, use_container_width=True)

