import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings

from utility.customer_segmentation_util import load_customer_data, calculate_rfm, calculate_rfm_scores, \
    segment_customers, perform_kmeans, create_segment_chart, create_cluster_chart, create_rfm_scatter, \
    create_cluster_radar

warnings.filterwarnings('ignore')

import api

daily_sales = load_customer_data()
daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')
rfm, rfm_clean = calculate_rfm(daily_sales)
rfm = calculate_rfm_scores(rfm)
rfm = segment_customers(rfm)

rfm, optimal_k, inertia, silhouette_scores = perform_kmeans(rfm)



def show_customer_segmentation():
    """Display Customer Segmentation Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>👥 Customer Segmentation</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            RFM Analysis + KMeans Clustering
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
        st.metric("👥 Total Customers", f"{len(rfm):,}")

    with col2:
        st.metric("📊 Segments", f"{rfm['segment'].nunique()}")

    with col3:
        st.metric("🔢 Clusters", f"{optimal_k}")

    col4, col5, col6 = st.columns(3)

    with col4:
        top_segment = rfm['segment'].value_counts().index[0]
        st.metric("🏆 Top Segment", top_segment)

    with col5:
        avg_frequency = rfm['frequency'].mean()
        st.metric("📈 Avg Frequency", f"{avg_frequency:.1f}")

    with col6:
        avg_monetary = rfm['monetary'].mean()
        st.metric("💰 Avg Monetary", f"₹{avg_monetary:,.0f}")

    col7, col8, col9 = st.columns(3)

    with col7:
        avg_recency = rfm['recency'].mean()
        st.metric("📅 Avg Recency", f"{avg_recency:.0f} days")

    with col8:
        champions = len(rfm[rfm['segment'] == 'Champions'])
        st.metric("⭐ Champions", f"{champions:,}")

    with col9:
        lost = len(rfm[rfm['segment'] == 'Lost'])
        st.metric("💀 Lost Customers", f"{lost:,}")

    st.divider()




    fig1 = create_segment_chart(rfm)
    st.plotly_chart(fig1,use_container_width=True )


    fig2 = create_cluster_chart(rfm)
    st.plotly_chart(fig2,use_container_width=True)

    fig3 = create_rfm_scatter(rfm)
    st.plotly_chart(fig3,use_container_width=True)

    fig4 = create_cluster_radar(rfm)
    st.plotly_chart(fig4,use_container_width=True)