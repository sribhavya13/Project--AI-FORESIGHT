# utility/demand_forecasting_util.py
# Updated - No LSTM, uses Prophet + Random Forest + Linear

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

import api


# ============================================================
# MODEL LOADING FUNCTIONS
# ============================================================

@st.cache_resource
def load_prophet_model():
    """Load Prophet model"""
    try:
        with open('models/prophet_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"❌ Error loading Prophet model: {e}")
        return None


@st.cache_resource
def load_random_forest_model():
    """Load Random Forest model"""
    try:
        with open('models/random_forest_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"❌ Error loading Random Forest model: {e}")
        return None


@st.cache_resource
def load_linear_model():
    """Load Linear model"""
    try:
        with open('models/linear_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"❌ Error loading Linear model: {e}")
        return None


@st.cache_resource
def load_scaler():
    """Load sklearn scaler"""
    try:
        with open('models/sklearn_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return scaler
    except Exception as e:
        return None


@st.cache_resource
def load_metadata():
    """Load forecast metadata"""
    try:
        with open('models/forecast_metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        return metadata
    except:
        return None


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_forecast_data():
    """Load data for forecasting"""
    daily_sales = api.get_daily_sales()

    if isinstance(daily_sales, pd.DataFrame):
        daily_sales = daily_sales.copy()
    elif isinstance(daily_sales, list):
        daily_sales = pd.DataFrame(daily_sales)
    else:
        daily_sales = pd.DataFrame()

    if not daily_sales.empty and 'date' in daily_sales.columns:
        daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')

    return daily_sales


# ============================================================
# METRICS CALCULATION
# ============================================================

def calculate_forecast_metrics(daily_sales):
    """Calculate forecasting dashboard metrics"""

    if daily_sales is None or daily_sales.empty:
        return {
            'total_days': 0,
            'total_units': 0,
            'total_revenue': 0,
            'avg_daily_units': 0,
            'avg_daily_revenue': 0,
            'max_daily_units': 0,
            'min_daily_units': 0,
            'total_skus': 0
        }

    df = daily_sales.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['units_sold'] = pd.to_numeric(df['units_sold'], errors='coerce')

    if 'revenue' in df.columns:
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    else:
        df['revenue'] = 0

    df = df.dropna(subset=['date', 'units_sold'])

    if df.empty:
        return {
            'total_days': 0,
            'total_units': 0,
            'total_revenue': 0,
            'avg_daily_units': 0,
            'avg_daily_revenue': 0,
            'max_daily_units': 0,
            'min_daily_units': 0,
            'total_skus': 0
        }

    return {
        'total_days': df['date'].dt.date.nunique(),
        'total_units': df['units_sold'].sum(),
        'total_revenue': df['revenue'].sum(),
        'avg_daily_units': df['units_sold'].mean(),
        'avg_daily_revenue': df['revenue'].mean(),
        'max_daily_units': df['units_sold'].max(),
        'min_daily_units': df['units_sold'].min(),
        'total_skus': df['sku_id'].nunique() if 'sku_id' in df.columns else 0
    }


# ============================================================
# FORECAST FUNCTIONS
# ============================================================

def make_prophet_forecast(model, historical_data, periods=30):
    """Generate future predictions using Prophet model."""
    if model is None:
        return None

    try:
        future = model.make_future_dataframe(periods=periods, freq='D')
        forecast = model.predict(future)
        return forecast
    except Exception as e:
        print(f"Prophet forecast error: {e}")
        return None


def make_random_forest_forecast(model, scaler, sku_data, feature_cols, periods=30):
    """Generate future predictions using Random Forest model."""
    if model is None:
        return None

    try:
        # Get last 30 days
        last_30 = sku_data.tail(30)

        # Prepare features for last 30 days
        X = last_30[feature_cols]

        # Scale features
        if scaler:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X

        # Predict next 30 days (one step at a time)
        predictions = []
        current_X = X_scaled[-1:].copy()

        for _ in range(periods):
            pred = model.predict(current_X)[0]
            predictions.append(pred)

            # Update features for next prediction
            # (simplified - shift features)
            current_X = np.roll(current_X, -1)
            current_X[0, -1] = pred

        return np.array(predictions)
    except Exception as e:
        print(f"Random Forest forecast error: {e}")
        return None


def make_linear_forecast(model, scaler, sku_data, feature_cols, periods=30):
    """Generate future predictions using Linear model."""
    if model is None:
        return None

    try:
        # Get last 30 days
        last_30 = sku_data.tail(30)

        # Prepare features
        X = last_30[feature_cols]

        # Scale features
        if scaler:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X

        # Predict
        predictions = model.predict(X_scaled)

        # If predictions are shorter than periods, pad with last value
        if len(predictions) < periods:
            predictions = list(predictions) + [predictions[-1]] * (periods - len(predictions))
        else:
            predictions = predictions[:periods]

        return np.array(predictions)
    except Exception as e:
        print(f"Linear model forecast error: {e}")
        return None


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df):
    """Create features for sklearn models"""
    df = df.copy()

    # Date features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # Lag features
    for lag in [7, 14, 21, 30]:
        df[f'units_sold_lag_{lag}'] = df['units_sold'].shift(lag)

    # Rolling statistics
    for window in [7, 14, 30]:
        df[f'units_sold_rolling_mean_{window}'] = df['units_sold'].rolling(window).mean()
        df[f'units_sold_rolling_std_{window}'] = df['units_sold'].rolling(window).std()

    return df


def get_feature_cols():
    """Return feature columns for sklearn models"""
    return [
        'day_of_week', 'month', 'quarter', 'year', 'is_weekend',
        'units_sold_lag_7', 'units_sold_lag_14', 'units_sold_lag_21', 'units_sold_lag_30',
        'units_sold_rolling_mean_7', 'units_sold_rolling_mean_14', 'units_sold_rolling_mean_30',
        'units_sold_rolling_std_7', 'units_sold_rolling_std_14', 'units_sold_rolling_std_30'
    ]


# ============================================================
# CHART FUNCTIONS
# ============================================================

def create_prophet_chart(forecast, historical):
    """Prophet forecast chart with black theme."""

    BLACK = "#000000"
    WHITE = "#FFFFFF"
    GRID = "rgba(255,255,255,0.08)"
    MUTED = "#9CA3AF"

    if forecast is None or forecast.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No Prophet forecast data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=15, color=MUTED)
        )
        fig.update_layout(
            height=500,
            paper_bgcolor=BLACK,
            plot_bgcolor=BLACK,
            font=dict(color=WHITE)
        )
        return fig

    historical = historical.copy()
    forecast = forecast.copy()

    historical["ds"] = pd.to_datetime(historical["ds"], errors="coerce")
    forecast["ds"] = pd.to_datetime(forecast["ds"], errors="coerce")

    historical = historical.dropna(subset=["ds"])
    forecast = forecast.dropna(subset=["ds"])

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=historical["ds"],
        y=historical["y"],
        mode="lines",
        name="Historical",
        line=dict(color="#6366F1", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.15)",
        hovertemplate=(
            "<b>Historical</b><br>"
            "Date: %{x|%d %b %Y}<br>"
            "Demand: %{y:,.0f} units"
            "<extra></extra>"
        )
    ))

    # Confidence Interval
    if "yhat_upper" in forecast.columns and "yhat_lower" in forecast.columns:
        fig.add_trace(go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            mode="lines",
            line=dict(color="rgba(244,63,94,0.35)", width=1),
            showlegend=False,
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(244,63,94,0.15)",
            line=dict(color="rgba(244,63,94,0.35)", width=1),
            name="Confidence Interval",
            hoverinfo="skip"
        ))

    # Prophet Forecast
    fig.add_trace(go.Scatter(
        x=forecast["ds"],
        y=forecast["yhat"],
        mode="lines+markers",
        name="Prophet Forecast",
        line=dict(color="#FB7185", width=3),
        marker=dict(size=6, color="#FB7185"),
        hovertemplate=(
            "<b>Prophet Forecast</b><br>"
            "Date: %{x|%d %b %Y}<br>"
            "Demand: %{y:,.0f} units"
            "<extra></extra>"
        )
    ))

    # Forecast Start
    if not historical.empty and not forecast.empty:
        forecast_start = forecast["ds"].min()
        fig.add_vline(
            x=forecast_start,
            line_dash="dash",
            line_width=1.5,
            line_color="rgba(255,255,255,0.35)"
        )
        fig.add_annotation(
            x=forecast_start,
            y=1,
            xref="x",
            yref="paper",
            text="Forecast Start",
            showarrow=False,
            font=dict(size=10, color=MUTED)
        )

    # Average KPI
    avg_value = forecast["yhat"].mean()
    fig.add_annotation(
        x=0.98, y=0.97,
        xref="paper", yref="paper",
        xanchor="right", yanchor="top",
        showarrow=False,
        text=(
            f"<b>PROPHET OUTLOOK</b><br><br>"
            f"Average: <b>{avg_value:,.0f}</b> units"
        ),
        font=dict(size=11, color=WHITE),
        bgcolor="#000000",
        bordercolor="rgba(255,255,255,0.15)",
        borderwidth=1,
        borderpad=10
    )

    fig.update_layout(
        height=520,
        paper_bgcolor=BLACK,
        plot_bgcolor=BLACK,
        template="plotly_dark",
        title=dict(
            text="<b>Prophet Demand Outlook</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=21, color=WHITE)
        ),
        xaxis=dict(
            title=dict(text="<b>Date</b>", font=dict(size=13, color=WHITE)),
            tickfont=dict(color="#D1D5DB"),
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor="rgba(255,255,255,0.2)"
        ),
        yaxis=dict(
            title=dict(text="<b>Demand (Units)</b>", font=dict(size=13, color=WHITE)),
            tickfont=dict(color="#D1D5DB"),
            tickformat=",",
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor="rgba(255,255,255,0.2)",
            rangemode="tozero"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="center", x=0.5,
            font=dict(size=12, color=WHITE),
            bgcolor="rgba(0,0,0,0.8)"
        ),
        font=dict(family="Arial, sans-serif", color=WHITE),
        margin=dict(l=75, r=50, t=95, b=70),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#111111",
            bordercolor="#444444",
            font=dict(color=WHITE)
        )
    )

    return fig


def create_comparison_chart(prophet_vals, rf_vals, linear_vals, periods=30):
    """Compare Prophet, Random Forest, and Linear forecasts"""

    BLACK = "#000000"
    WHITE = "#FFFFFF"
    GRID = "rgba(255,255,255,0.08)"

    fig = go.Figure()

    # Check if we have data
    has_prophet = prophet_vals is not None and len(prophet_vals) > 0
    has_rf = rf_vals is not None and len(rf_vals) > 0
    has_linear = linear_vals is not None and len(linear_vals) > 0

    if not (has_prophet or has_rf or has_linear):
        fig.add_annotation(
            text="No forecast data available for comparison",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=15, color="#9CA3AF")
        )
        fig.update_layout(
            height=500,
            paper_bgcolor=BLACK,
            plot_bgcolor=BLACK,
            font=dict(color=WHITE)
        )
        return fig

    days = np.arange(1, periods + 1)

    # Prophet
    if has_prophet:
        prophet_vals = np.asarray(prophet_vals, dtype=float).flatten()[:periods]
        fig.add_trace(go.Scatter(
            x=days[:len(prophet_vals)],
            y=prophet_vals,
            mode="lines+markers",
            name="Prophet",
            line=dict(color="#818CF8", width=3),
            marker=dict(size=6, color="#818CF8"),
            hovertemplate=(
                "<b>Prophet</b><br>"
                "Day: %{x}<br>"
                "Demand: %{y:,.0f} units"
                "<extra></extra>"
            )
        ))

    # Random Forest
    if has_rf:
        rf_vals = np.asarray(rf_vals, dtype=float).flatten()[:periods]
        fig.add_trace(go.Scatter(
            x=days[:len(rf_vals)],
            y=rf_vals,
            mode="lines+markers",
            name="Random Forest",
            line=dict(color="#34D399", width=3),
            marker=dict(size=6, color="#34D399"),
            hovertemplate=(
                "<b>Random Forest</b><br>"
                "Day: %{x}<br>"
                "Demand: %{y:,.0f} units"
                "<extra></extra>"
            )
        ))

    # Linear
    if has_linear:
        linear_vals = np.asarray(linear_vals, dtype=float).flatten()[:periods]
        fig.add_trace(go.Scatter(
            x=days[:len(linear_vals)],
            y=linear_vals,
            mode="lines+markers",
            name="Linear Model",
            line=dict(color="#FBBF24", width=3),
            marker=dict(size=6, color="#FBBF24"),
            hovertemplate=(
                "<b>Linear Model</b><br>"
                "Day: %{x}<br>"
                "Demand: %{y:,.0f} units"
                "<extra></extra>"
            )
        ))

    # Ensemble (if all three available)
    if has_prophet and has_rf and has_linear:
        min_len = min(len(prophet_vals), len(rf_vals), len(linear_vals))
        ensemble = (prophet_vals[:min_len] + rf_vals[:min_len] + linear_vals[:min_len]) / 3
        fig.add_trace(go.Scatter(
            x=days[:min_len],
            y=ensemble,
            mode="lines+markers",
            name="Ensemble Average",
            line=dict(color="#F472B6", width=3, dash="dash"),
            marker=dict(size=6, color="#F472B6"),
            hovertemplate=(
                "<b>Ensemble</b><br>"
                "Day: %{x}<br>"
                "Demand: %{y:,.0f} units"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        height=500,
        paper_bgcolor=BLACK,
        plot_bgcolor=BLACK,
        template="plotly_dark",
        title=dict(
            text="<b>Demand Forecast Comparison</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=20, color=WHITE)
        ),
        xaxis=dict(
            title=dict(text="<b>Forecast Day</b>", font=dict(size=13, color=WHITE)),
            tickfont=dict(color="#D1D5DB"),
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor="rgba(255,255,255,0.2)"
        ),
        yaxis=dict(
            title=dict(text="<b>Forecast Demand (Units)</b>", font=dict(size=13, color=WHITE)),
            tickfont=dict(color="#D1D5DB"),
            tickformat=",",
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor="rgba(255,255,255,0.2)",
            rangemode="tozero"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="center", x=0.5,
            font=dict(size=12, color=WHITE),
            bgcolor="rgba(0,0,0,0.8)"
        ),
        font=dict(family="Arial, sans-serif", color=WHITE),
        margin=dict(l=75, r=50, t=90, b=70),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#111111",
            bordercolor="#444444",
            font=dict(color=WHITE)
        )
    )

    return fig


def create_accuracy_chart(metrics):
    """Create accuracy comparison chart"""

    if metrics is None or metrics.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No accuracy data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=15, color="#9CA3AF")
        )
        fig.update_layout(
            height=400,
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font=dict(color="white")
        )
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=metrics['Model'],
        y=metrics['MAE'],
        marker_color=['#818CF8', '#34D399', '#FBBF24'],
        text=metrics['MAE'].round(2),
        textposition='outside',
        textfont=dict(color='white', size=11),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'MAE: %{y:.2f} units'
            '<extra></extra>'
        )
    ))

    fig.update_layout(
        height=400,
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        template="plotly_dark",
        title=dict(
            text="<b>Model Accuracy Comparison (MAE)</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=18, color="white")
        ),
        xaxis=dict(
            title=dict(text="<b>Model</b>", font=dict(color="white")),
            tickfont=dict(color="#D1D5DB"),
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title=dict(text="<b>MAE (units)</b>", font=dict(color="white")),
            tickfont=dict(color="#D1D5DB"),
            gridcolor="rgba(255,255,255,0.08)",
            rangemode="tozero"
        ),
        showlegend=False,
        font=dict(color="white"),
        margin=dict(l=50, r=50, t=70, b=50)
    )

    # Target line
    fig.add_hline(
        y=2.5,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text="Target: 2.5 units",
        annotation_position="top right",
        annotation_font=dict(color="#EF4444", size=10)
    )

    return fig