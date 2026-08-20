from datetime import datetime
import warnings

import streamlit as st

from app_pages.business_intellegence_dashboard import show_bi_dashboard
from app_pages.category_performance import show_category_performance
from app_pages.churn_pred_dashboard import show_churn_prediction
from app_pages.customer_insight_dashboard import show_customer_insights
from app_pages.customer_segmentation_dashboard import show_customer_segmentation
from app_pages.demand_forecasting_dashboard import show_demand_forecasting
from app_pages.executive_dashboard import show_executive_dashboard
from app_pages.forecast_dashboard import show_forecast_dashboard
from app_pages.inventary_dashboard import show_inventory_dashboard
from app_pages.inventary_optimization_dashboard import show_inventory_optimization
from app_pages.ml_performance_dashboard import show_ml_performance
from app_pages.overstock_dashboard import show_overstock_dashboard
from app_pages.product_performance import show_product_performance
from app_pages.promo_dashboard import show_promotion_dashboard
from app_pages.recommendation_dashboard import show_recommendations
from app_pages.sales_analysis import show_sales_analytics
from app_pages.seasonal_dashboard import show_seasonality_dashboard
from app_pages.stock_out_dashboard import show_stockout_risk
from utility.homepage_util import show_home

st.set_page_config(
    page_title="RetailPulse AI Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

warnings.filterwarnings('ignore')

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        margin: 10px 0 0 0;
        font-size: 1.2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }
    .company-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .company-banner h2 {
        color: white !important;
    }
    .company-banner p {
        color: rgba(255,255,255,0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='text-align: center; '>
    <h2 style='color: #667eea; margin: 0;'>📊 RetailPulse</h2>
    <p style='color: #666; margin: 0; font-size: 12px;'>AI Analytics Platform</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

pages = {
    "🏠 Home": "home",
    "📈 Executive Dashboard": "executive",
    "💰 Sales Analytics": "sales",
    "📦 Product Performance": "products",
    "📊 Category Performance": "categories",
    "📦 Inventory Dashboard": "inventory",
    "⚠️ Stockout Risk": "stockout",
    "📦 Overstock Dashboard": "overstock",
    "🎯 Promotion Dashboard": "promotion",
    "📅 Seasonality Dashboard": "seasonality",
    "🔮 Forecast Dashboard": "forecast",
    "👥 Customer Insights": "customers",
    "💡 Recommendations": "recommendations",
    "🤖 ML Performance": "ml_performance",
    "📈 Demand Forecasting": "forecasting",
    "👥 Customer Segmentation": "segmentation",
    "⚠️ Churn Prediction": "churn",
    "📦 Inventory Optimization": "inventory_opt",
    "📊 Business Intelligence": "bi"
}

# Create navigation with icons
selected_page = st.sidebar.radio(
    "Navigate to:",
    list(pages.keys()),
    index=0
)
page_key = pages[selected_page]

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='text-align: center; font-size: 12px; color: #666;'>
    <p>RetailPulse AI v2.0</p>
    <p>Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    <p style='margin-top: 10px;'>📧 analytics@retailpulse.ai</p>
</div>
""", unsafe_allow_html=True)

if page_key == "home":
    show_home()

elif page_key == "executive":
    show_executive_dashboard()

elif page_key == "sales":
    show_sales_analytics()

elif page_key == "products":
    show_product_performance()

elif page_key == "categories":
    show_category_performance()

elif page_key == "inventory":
    show_inventory_dashboard()

elif page_key == "stockout":
    show_stockout_risk()

elif page_key == "seasonality":
    show_seasonality_dashboard()

elif page_key == "overstock":
    show_overstock_dashboard()

elif page_key == "promotion":
    show_promotion_dashboard()

elif page_key == "forecast":
    show_forecast_dashboard()

elif page_key == "customers":
    show_customer_insights()

elif page_key == "recommendations":
    show_recommendations()

elif page_key == "forecasting":
    show_demand_forecasting()

elif page_key == "segmentation":
    show_customer_segmentation()

elif page_key == "churn":
    show_churn_prediction()

elif page_key == "inventory_opt":
    show_inventory_optimization()

elif page_key == "ml_performance":
    show_ml_performance()

elif page_key == "bi":
    show_bi_dashboard()




