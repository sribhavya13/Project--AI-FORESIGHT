# app_pages/demand_forecasting.py
# Updated - No LSTM, uses Prophet + Random Forest + Linear

import streamlit as st
import pandas as pd
import numpy as np
import warnings

from utility.demand_forecasting_util import (
    load_forecast_data,
    load_prophet_model,
    load_random_forest_model,
    load_linear_model,
    load_scaler,
    load_metadata,
    calculate_forecast_metrics,
    make_prophet_forecast,
    make_random_forest_forecast,
    make_linear_forecast,
    create_features,
    get_feature_cols,
    create_prophet_chart,
    create_comparison_chart,
    create_accuracy_chart
)

warnings.filterwarnings("ignore")

# ============================================================
# LOAD DATA AND MODELS
# ============================================================

daily_sales = load_forecast_data()
prophet_model = load_prophet_model()
rf_model = load_random_forest_model()
linear_model = load_linear_model()
scaler = load_scaler()
metadata = load_metadata()
metrics = calculate_forecast_metrics(daily_sales)
feature_cols = get_feature_cols()

# ============================================================
# PREPARE HISTORICAL DATA
# ============================================================

if daily_sales is not None and not daily_sales.empty:
    daily_sales["date"] = pd.to_datetime(daily_sales["date"], errors="coerce")
    daily_sales["units_sold"] = pd.to_numeric(daily_sales["units_sold"], errors="coerce")
    daily_sales = daily_sales.dropna(subset=["date", "units_sold"])

    historical_data = (
        daily_sales
        .groupby("date")["units_sold"]
        .sum()
        .reset_index()
    )
    historical_data.columns = ["ds", "y"]
    historical_data = historical_data.sort_values("ds")
else:
    historical_data = pd.DataFrame(columns=["ds", "y"])


# ============================================================
# DASHBOARD
# ============================================================

def show_demand_forecasting():
    """Display Demand Forecasting Dashboard."""

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    ">
        <h1 style="color: white !important; margin: 0; font-size: 2rem;">
        📈 Demand Forecasting
        </h1>
        <p style="color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;">
        Prophet + Random Forest + Linear Model - Using Pre-trained Models
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # DATA CHECK
    # ========================================================

    if daily_sales is None or daily_sales.empty:
        st.error("No sales data available for forecasting.")
        return

    if historical_data.empty:
        st.error("Historical sales data is empty.")
        return

    # ========================================================
    # STYLING
    # ========================================================

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

    # ========================================================
    # KPI ROWS
    # ========================================================

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Total Days", f"{metrics['total_days']:,}")
    with col2:
        st.metric("📦 Total Units Sold", f"{metrics['total_units']:,}")
    with col3:
        st.metric("💰 Total Revenue", f"₹{metrics['total_revenue']:,.0f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("📊 Avg Daily Units", f"{metrics['avg_daily_units']:.0f}")
    with col5:
        st.metric("💵 Avg Daily Revenue", f"₹{metrics['avg_daily_revenue']:,.0f}")
    with col6:
        st.metric("📈 Max Daily Units", f"{metrics['max_daily_units']:,}")

    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric("📉 Min Daily Units", f"{metrics['min_daily_units']:,}")
    with col8:
        st.metric("🏷️ Total SKUs", f"{metrics['total_skus']:,}")
    with col9:
        loaded_models = sum([prophet_model is not None, rf_model is not None, linear_model is not None])
        st.metric("✅ Models Loaded", f"{loaded_models}/3")

    st.divider()

    # ========================================================
    # FORECAST SETTINGS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Forecast Settings")
        forecast_periods = st.slider("📅 Forecast Period (Days)", 7, 90, 30, 7)

        model_choice = st.selectbox(
            "Select Model",
            ["Prophet", "Random Forest", "Linear Model", "Both (Comparison)"],
            help="Choose which model to use"
        )

    with col2:
        st.subheader("🤖 Model Information")
        if metadata:
            st.markdown(f"""
            **Model Information**
            - **Trained:** {metadata.get('train_date', 'N/A')}
            - **Data Points:** {metadata.get('data_points', 'N/A')}
            - **Average Daily:** {metrics['avg_daily_units']:.0f} units
            """)
        else:
            st.info("Model metadata is not available.")

    # ========================================================
    # MODEL AVAILABILITY CHECK
    # ========================================================

    if model_choice == "Prophet" and prophet_model is None:
        st.error("Prophet model is not available.")
        return
    elif model_choice == "Random Forest" and rf_model is None:
        st.error("Random Forest model is not available.")
        return
    elif model_choice == "Linear Model" and linear_model is None:
        st.error("Linear Model is not available.")
        return

    # ========================================================
    # GENERATE BUTTON
    # ========================================================

    generate_forecast = st.button("🚀 Generate Forecast", use_container_width=True, type="primary")

    if not generate_forecast:
        st.info("Select a model and forecast period, then click **Generate Forecast**.")
        return

    st.divider()

    # ========================================================
    # VARIABLES
    # ========================================================

    prophet_forecast = None
    rf_forecast = None
    linear_forecast = None
    prophet_values = None
    rf_values = None
    linear_values = None

    # ========================================================
    # GENERATE PROPHET FORECAST
    # ========================================================

    if model_choice in ["Prophet", "Both (Comparison)"] and prophet_model is not None:
        with st.spinner("Generating Prophet forecast..."):
            try:
                prophet_forecast = make_prophet_forecast(prophet_model, historical_data, forecast_periods)
                if prophet_forecast is not None and not prophet_forecast.empty:
                    prophet_values = prophet_forecast.tail(forecast_periods)["yhat"].to_numpy(dtype=float)
            except Exception as e:
                st.error(f"Prophet forecast failed: {e}")

    # ========================================================
    # GENERATE RANDOM FOREST FORECAST
    # ========================================================

    if model_choice in ["Random Forest", "Both (Comparison)"] and rf_model is not None:
        with st.spinner("Generating Random Forest forecast..."):
            try:
                # Create features for the data
                df_features = create_features(daily_sales)
                # Use a sample SKU with enough data
                sample_sku = None
                for sku in daily_sales['sku_id'].unique():
                    if len(daily_sales[daily_sales['sku_id'] == sku]) >= 60:
                        sample_sku = sku
                        break

                if sample_sku:
                    sku_data = df_features[df_features['sku_id'] == sample_sku].sort_values('date')
                    rf_forecast = make_random_forest_forecast(rf_model, scaler, sku_data, feature_cols,
                                                              forecast_periods)
                    if rf_forecast is not None:
                        rf_values = np.array(rf_forecast).flatten()
            except Exception as e:
                st.error(f"Random Forest forecast failed: {e}")

    # ========================================================
    # GENERATE LINEAR FORECAST
    # ========================================================

    if model_choice in ["Linear Model", "Both (Comparison)"] and linear_model is not None:
        with st.spinner("Generating Linear forecast..."):
            try:
                df_features = create_features(daily_sales)
                sample_sku = None
                for sku in daily_sales['sku_id'].unique():
                    if len(daily_sales[daily_sales['sku_id'] == sku]) >= 60:
                        sample_sku = sku
                        break

                if sample_sku:
                    sku_data = df_features[df_features['sku_id'] == sample_sku].sort_values('date')
                    linear_forecast = make_linear_forecast(linear_model, scaler, sku_data, feature_cols,
                                                           forecast_periods)
                    if linear_forecast is not None:
                        linear_values = np.array(linear_forecast).flatten()
            except Exception as e:
                st.error(f"Linear forecast failed: {e}")

    # ========================================================
    # PROPHET RESULTS
    # ========================================================

    if model_choice in ["Prophet", "Both (Comparison)"] and prophet_values is not None and len(prophet_values) > 0:
        st.subheader("📊 Prophet Forecast")

        fig_prophet = create_prophet_chart(prophet_forecast, historical_data)
        st.plotly_chart(fig_prophet, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Avg Daily", f"{prophet_values.mean():,.0f}")
        with col2:
            st.metric("📦 Total", f"{prophet_values.sum():,.0f}")
        with col3:
            st.metric("📉 Min", f"{prophet_values.min():,.0f}")
        with col4:
            st.metric("📈 Max", f"{prophet_values.max():,.0f}")

    # ========================================================
    # RANDOM FOREST RESULTS
    # ========================================================

    if model_choice in ["Random Forest", "Both (Comparison)"] and rf_values is not None and len(rf_values) > 0:
        st.subheader("📊 Random Forest Forecast")

        # Create a simple chart for RF
        fig_rf = create_comparison_chart(None, rf_values, None, forecast_periods)
        fig_rf.update_layout(title="<b>Random Forest Demand Forecast</b>")
        st.plotly_chart(fig_rf, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Avg Daily", f"{rf_values.mean():,.0f}")
        with col2:
            st.metric("📦 Total", f"{rf_values.sum():,.0f}")
        with col3:
            st.metric("📉 Min", f"{rf_values.min():,.0f}")
        with col4:
            st.metric("📈 Max", f"{rf_values.max():,.0f}")

    # ========================================================
    # LINEAR RESULTS
    # ========================================================

    if model_choice in ["Linear Model", "Both (Comparison)"] and linear_values is not None and len(linear_values) > 0:
        st.subheader("📊 Linear Model Forecast")

        fig_linear = create_comparison_chart(None, None, linear_values, forecast_periods)
        fig_linear.update_layout(title="<b>Linear Model Demand Forecast</b>")
        st.plotly_chart(fig_linear, use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Avg Daily", f"{linear_values.mean():,.0f}")
        with col2:
            st.metric("📦 Total", f"{linear_values.sum():,.0f}")
        with col3:
            st.metric("📉 Min", f"{linear_values.min():,.0f}")
        with col4:
            st.metric("📈 Max", f"{linear_values.max():,.0f}")

    # ========================================================
    # COMPARISON CHART
    # ========================================================

    if model_choice == "Both (Comparison)":
        if (prophet_values is not None and len(prophet_values) > 0 and
                rf_values is not None and len(rf_values) > 0 and
                linear_values is not None and len(linear_values) > 0):

            st.divider()
            st.subheader("📊 Model Comparison: Prophet vs Random Forest vs Linear")

            fig_comparison = create_comparison_chart(prophet_values, rf_values, linear_values, forecast_periods)
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Ensemble
            min_len = min(len(prophet_values), len(rf_values), len(linear_values))
            ensemble = (prophet_values[:min_len] + rf_values[:min_len] + linear_values[:min_len]) / 3

            st.subheader("🤝 Ensemble Forecast")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Ensemble Avg", f"{ensemble.mean():,.0f}")
            with col2:
                st.metric("📦 Ensemble Total", f"{ensemble.sum():,.0f}")
            with col3:
                st.metric("📉 Ensemble Min", f"{ensemble.min():,.0f}")
            with col4:
                st.metric("📈 Ensemble Max", f"{ensemble.max():,.0f}")
        else:
            st.warning("Unable to generate comparison. Not all models produced valid forecasts.")