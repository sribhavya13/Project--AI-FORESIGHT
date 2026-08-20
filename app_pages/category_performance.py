import streamlit as st
import pandas as pd
from utility.category_performance_util import  create_category_revenue_chart, \
    create_category_units_chart, create_avg_sku_revenue_chart, create_category_quarter_chart, \
    create_revenue_vs_units_chart
import api


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
    .stats-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
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

sku = pd.DataFrame(api.get_skus())
daily_sales = pd.DataFrame(api.get_daily_sales())
print(daily_sales.columns)
daily_sales_with_cat = daily_sales.copy()

daily_sales_with_cat['category'] = (
    daily_sales_with_cat['category'].fillna('Unknown')
)

category_metrics = daily_sales_with_cat.groupby('category').agg({
    'revenue': 'sum',
    'units_sold': 'sum',
    'sku_id': 'nunique'
}).reset_index()

category_metrics.columns = ['category', 'revenue', 'units_sold', 'sku_count']
category_metrics['avg_sku_revenue'] = category_metrics['revenue'] / category_metrics['sku_count']
category_metrics['revenue_per_unit'] = category_metrics['revenue'] / category_metrics['units_sold']

total_revenue = daily_sales['revenue'].sum()

top_category = category_metrics.loc[category_metrics['revenue'].idxmax(), 'category']
top_revenue = category_metrics['revenue'].max()
top_share = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
total_skus = category_metrics['sku_count'].sum()
avg_skus = category_metrics['sku_count'].mean()
most_diverse = category_metrics.loc[category_metrics['sku_count'].idxmax(), 'category']
most_profitable = category_metrics.loc[category_metrics['avg_sku_revenue'].idxmax(), 'category']
def show_category_performance():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
        '>
            <h1 style='color: white !important; margin: 0; font-size: 2rem;'>📊 Category Performance Dashboard</h1>
            <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
                Comprehensive category analysis and performance metrics
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
        st.metric("Total Categories", f"{len(category_metrics)}")
    with col2:
        st.metric("Top Category", top_category)
    with col3:
        st.metric("Top Category Revenue", f"₹{top_revenue:,.0f}")

    # Row 2: 3 columns
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Top Category Share", f"{top_share:.1f}%")
    with col5:
        st.metric("Total SKUs", f"{total_skus:,}")
    with col6:
        st.metric("Avg SKUs per Category", f"{avg_skus:.0f}")

    # Row 3: 2 columns
    col7, col8 = st.columns(2)
    with col7:
        st.metric("🌿 Most Diverse", most_diverse)
    with col8:
        st.metric("💰 Most Profitable", most_profitable)

    st.divider()

    fig1 = create_category_revenue_chart(category_metrics)
    st.plotly_chart(fig1, width="stretch")

    fig2 = create_category_units_chart(category_metrics)
    st.plotly_chart(fig2, width="stretch")

    fig3 = create_avg_sku_revenue_chart(category_metrics)
    st.plotly_chart(fig3, width="stretch")

    fig4 = create_category_quarter_chart(daily_sales)
    st.plotly_chart(fig4, width="stretch")

    fig5 = create_revenue_vs_units_chart(category_metrics)
    st.plotly_chart(fig5, width="stretch")


