# app_pages/forecast_dashboard.py
# Updated to use new metrics calculation

import streamlit as st
import pandas as pd
from datetime import timedelta
import warnings

from utility.forecast_util import (
    simple_forecast,
    get_forecast_for_sku,
    create_forecast_chart,
    create_confidence_chart,
    create_category_forecast,
    create_accuracy_chart,
    get_model_metrics
)

warnings.filterwarnings('ignore')

import api

daily_sales = pd.DataFrame(api.get_daily_sales())
daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")


def show_forecast_dashboard():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
        '>
            <h1 style='color: white !important; margin: 0; font-size: 2rem;'>🔮 Forecast Dashboard</h1>
            <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
                Demand forecasting using <strong>Machine Learning</strong> models
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        [data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #3b3b3b;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
        }
        [data-testid="stMetricLabel"] {
            justify-content: center;
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            font-weight: 500 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 22px !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetric"] > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Forecast Settings
    st.subheader("🎯 Forecast Settings")

    c1, c2, c3 = st.columns([2, 2, 1])

    all_skus = sorted(daily_sales["sku_id"].unique())

    with c1:
        sku_search = st.text_input("🔍 Search SKU", placeholder="Type SKU...")

        if sku_search:
            filtered_skus = [sku for sku in all_skus if sku_search.lower() in str(sku).lower()]
        else:
            filtered_skus = all_skus

        if not filtered_skus:
            st.warning("No SKU found.")
            st.stop()

        selected_sku = st.selectbox("Select SKU", filtered_skus)

    with c2:
        horizon = st.slider("📅 Forecast Horizon (Days)", 7, 90, 30, 7)

    with c3:
        st.metric("Available SKUs", len(all_skus))

    st.divider()

    # Forecast
    sku_historical = daily_sales[daily_sales["sku_id"] == selected_sku].sort_values("date")

    if len(sku_historical) < 30:
        st.warning(f"Only {len(sku_historical)} days available.")
        last_date = sku_historical["date"].max()
        forecast_dates = pd.date_range(last_date + timedelta(days=1), periods=horizon)
        forecast_values = simple_forecast(sku_historical["units_sold"], horizon)
        results = None
    else:
        with st.spinner("Generating forecast..."):
            output = get_forecast_for_sku(daily_sales, selected_sku, horizon)

        if output is None:
            st.error("Forecast generation failed.")
            st.stop()

        results, best_model, forecast_dates, forecast_values, best_wape = output

    # Forecast Chart
    fig = create_forecast_chart(
        sku_historical,
        forecast_dates,
        forecast_values,
        selected_sku
    )
    st.plotly_chart(fig, use_container_width=True)

    # Confidence Chart
    fig4 = create_confidence_chart()
    st.plotly_chart(fig4, use_container_width=True)

    # Category Forecast
    fig5 = create_category_forecast(daily_sales)
    st.plotly_chart(fig5, use_container_width=True)

    # Accuracy Chart - Now uses real data, no CSV
    fig6 = create_accuracy_chart(daily_sales, selected_sku)
    st.plotly_chart(fig6, use_container_width=True)