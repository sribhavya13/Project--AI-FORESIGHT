import streamlit as st
import pandas as pd
from datetime import datetime
import warnings

import api
from utility.inventary_dashboard_util import calculate_inventory_metrics, create_inventory_value_chart, \
    create_inventory_units_chart, create_stock_value_per_sku_chart, create_inventory_distribution_chart


warnings.filterwarnings('ignore')

sku = pd.DataFrame(api.get_skus())
inventory = pd.DataFrame(api.get_inventary())


# Keep only required SKU columns
sku = sku[
    [
        'sku_id',
        'sku_name',
        'category',
        'subcategory',
        'unit_price',
        'cost_price',
        'brand'
    ]
]


# Merge once only
inventory_analysis = inventory.merge(
    sku,
    on='sku_id',
    how='left'
)


# Fix missing values
inventory_analysis['category'] = (
    inventory_analysis['category']
    .fillna('Unknown')
)

inventory_analysis['unit_price'] = (
    pd.to_numeric(
        inventory_analysis['unit_price'],
        errors='coerce'
    )
    .fillna(0)
)


inventory_analysis['stock_on_hand'] = (
    pd.to_numeric(
        inventory_analysis['stock_on_hand'],
        errors='coerce'
    )
    .fillna(0)
)


# Calculate stock value
inventory_analysis['stock_value'] = (
    inventory_analysis['stock_on_hand']
    *
    inventory_analysis['unit_price']
)
# ADD HERE
inventory_analysis['last_restock_date'] = pd.to_datetime(
    inventory_analysis['last_restock_date'],
    errors='coerce'
)

inventory_analysis['lead_time_days'] = (
    datetime.now() -
    inventory_analysis['last_restock_date']
).dt.days

inventory_analysis['lead_time_days'] = (
    inventory_analysis['lead_time_days']
    .fillna(0)
)




inv_by_category = inventory_analysis.groupby('category').agg({
        'stock_on_hand': 'sum',
        'stock_value': 'sum',
        'sku_id': 'nunique'
    }).reset_index()
inv_by_category.columns = ['category', 'total_units', 'stock_value', 'sku_count']
inv_by_category['stock_value_per_sku'] = inv_by_category['stock_value'] / inv_by_category['sku_count']
metrics = calculate_inventory_metrics(inventory_analysis)
def show_inventory_dashboard():
    """Display Inventory Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📦 Inventory Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Real-time inventory monitoring and analysis
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

    st.markdown("### 📊 CATEGORY METRICS")

    # Row 1: 3 columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total SKUs", f"{metrics['total_skus']:,}")
    with col2:
        st.metric("Total Stock Value", f"₹{metrics['total_stock_value']:,.0f}")
    with col3:
        st.metric("Avg Stock per SKU", f"{metrics['avg_stock_on_hand']:.0f} units")

    # Row 2: 3 columns
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Median Stock per SKU", f"{metrics['median_stock_on_hand']:.0f} units")
    with col5:
        st.metric("Max Stock Value", f"₹{metrics['max_stock_value']:,.0f}")
    with col6:
        st.metric("Avg Reorder Point", f"{metrics['avg_reorder_point']:.1f} days")

    # Row 3: 2 columns
    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric("Min Reorder Point", f"{metrics['min_reorder_point']} days")
    with col8:
        st.metric("Max Reorder Point", f"{metrics['max_reorder_point']} days")
    with col9:
        risk_skus = metrics['stockout_risk_count']
        st.metric("⚠️ At Risk SKUs", f"{risk_skus}", delta="Needs Attention" if risk_skus > 0 else "OK")

    fig1 = create_inventory_value_chart(inv_by_category)
    st.plotly_chart(fig1, width="stretch")

    fig2 = create_inventory_units_chart(inv_by_category)
    st.plotly_chart(fig2, width="stretch")

    fig3 = create_stock_value_per_sku_chart(inv_by_category)
    st.plotly_chart(fig3, width="stretch")

    fig4 = create_inventory_distribution_chart(inventory_analysis)
    st.plotly_chart(fig4, width="stretch")

