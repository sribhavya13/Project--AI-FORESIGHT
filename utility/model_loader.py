# utility/model_loader.py
# Simple model loader without LSTM

import pickle
import streamlit as st
import pandas as pd

@st.cache_resource
def load_prophet():
    try:
        with open('models/prophet_model.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

@st.cache_resource
def load_random_forest():
    try:
        with open('models/random_forest_model.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

@st.cache_resource
def load_linear():
    try:
        with open('models/linear_model.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

@st.cache_data
def load_metrics():
    try:
        return pd.read_csv('models/model_metrics.csv')
    except:
        return pd.DataFrame({
            'Model': ['Random Forest', 'Linear Model', 'Prophet'],
            'MAE': [2.04, 2.04, 2.34],
            'RMSE': [2.98, 2.98, 3.74],
            'Acc ±1 (%)': [34.1, 34.1, 16.7],
            'Acc ±2 (%)': [64.2, 64.2, 60.0]
        })