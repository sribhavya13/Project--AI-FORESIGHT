

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')


def calculate_wape(actual, predicted):
    return np.sum(np.abs(actual - predicted)) / np.sum(np.abs(actual)) * 100


def calculate_metrics(actual, predicted):
    return {
        'MAE': mean_absolute_error(actual, predicted),
        'RMSE': np.sqrt(mean_squared_error(actual, predicted)),
        'WAPE': calculate_wape(actual, predicted),
        'MAPE': np.mean(np.abs((actual - predicted) / actual)) * 100 if (actual != 0).all() else float('inf')
    }


def create_features(df, target_col='units_sold'):
    df = df.copy()
    df = df.sort_values(['sku_id', 'date'])

    for lag in [1, 3, 7, 14, 21, 28]:
        df[f'lag_{lag}'] = df.groupby('sku_id')[target_col].shift(lag)

    for window in [7, 14, 28]:
        df[f'rolling_mean_{window}'] = df.groupby('sku_id')[target_col].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
        df[f'rolling_std_{window}'] = df.groupby('sku_id')[target_col].transform(
            lambda x: x.rolling(window, min_periods=1).std()
        )

    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    return df


def compare_models(df, sku_id, target_col='units_sold'):
    print(f"📊 Training ML models for SKU: {sku_id}")

    df_features = create_features(df)
    df_sku = df_features[df_features['sku_id'] == sku_id].dropna()

    feature_cols = ['lag_1', 'lag_3', 'lag_7', 'lag_14', 'lag_21', 'lag_28',
                    'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_28',
                    'rolling_std_7', 'rolling_std_14', 'rolling_std_28',
                    'day_of_week', 'month', 'quarter', 'week_of_year', 'is_weekend']

    X = df_sku[feature_cols]
    y = df_sku[target_col]

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # XGBoost
    print("Training XGBoost...")
    model = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train, verbose=False)
    y_pred = model.predict(X_test_scaled)
    metrics = calculate_metrics(y_test, y_pred)
    print(f"   XGBoost WAPE: {metrics['WAPE']:.2f}%")
    results['XGBoost'] = {'model': model, 'y_pred': y_pred, 'metrics': metrics, 'scaler': scaler}

    # LightGBM
    print("Training LightGBM...")
    model = LGBMRegressor(n_estimators=200, learning_rate=0.1, num_leaves=31, random_state=42, verbose=-1, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    metrics = calculate_metrics(y_test, y_pred)
    print(f"   LightGBM WAPE: {metrics['WAPE']:.2f}%")
    results['LightGBM'] = {'model': model, 'y_pred': y_pred, 'metrics': metrics, 'scaler': scaler}

    # Random Forest
    print("Training Random Forest...")
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    metrics = calculate_metrics(y_test, y_pred)
    print(f"   Random Forest WAPE: {metrics['WAPE']:.2f}%")
    results['RandomForest'] = {'model': model, 'y_pred': y_pred, 'metrics': metrics, 'scaler': scaler}

    # Prophet
    print("Training Prophet...")
    sku_data = df[df['sku_id'] == sku_id][['date', target_col]].copy()
    sku_data.columns = ['ds', 'y']
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, changepoint_prior_scale=0.05)
    model.fit(sku_data)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    prophet_pred = forecast[forecast['ds'].isin(df_sku['date'])]['yhat'].values[:len(y_test)]

    if len(prophet_pred) > 0:
        metrics = calculate_metrics(y_test.values, prophet_pred[:len(y_test)])
        print(f"   Prophet WAPE: {metrics['WAPE']:.2f}%")
        results['Prophet'] = {'model': model, 'y_pred': prophet_pred, 'metrics': metrics}

    print("✅ All ML models trained!")
    return results, feature_cols, scaler


def get_best_model(results):
    best_model = None
    best_wape = float('inf')

    for name, result in results.items():
        if 'metrics' in result and 'WAPE' in result['metrics']:
            if result['metrics']['WAPE'] < best_wape:
                best_wape = result['metrics']['WAPE']
                best_model = name

    return best_model, best_wape