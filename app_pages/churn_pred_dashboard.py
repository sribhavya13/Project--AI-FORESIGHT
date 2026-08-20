import streamlit as st
import pandas as pd
from sklearn.metrics import  accuracy_score, precision_score,recall_score, f1_score
import warnings

from utility.churn_pred_util import load_churn_data, prepare_churn_data, train_churn_model, \
    create_churn_distribution_chart,create_churn_risk_chart, create_roc_curve_chart, create_confusion_matrix_chart, \
    create_feature_importance_chart
from utility.customer_segmentation_util import calculate_rfm

warnings.filterwarnings('ignore')

daily_sales = load_churn_data()
daily_sales['date'] = pd.to_datetime(daily_sales['date'], errors='coerce')
rfm, rfm_clean = calculate_rfm(daily_sales)
churn_data = prepare_churn_data(daily_sales, rfm)


def show_churn_prediction():
    """Display Churn Prediction Dashboard"""

    # Header
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    '>
        <h1 style='color: white !important; margin: 0; font-size: 2rem;'>⚠️ Churn Prediction</h1>
        <p style='color: rgba(255,255,255,0.9) !important; margin: 8px 0 0 0;'>
            Random Forest Classification Model
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Training churn prediction model..."):
        clf, scaler, X_train_scaled, X_test_scaled, y_train, y_test, y_pred, y_proba, importance_df, feature_cols = train_churn_model(
            churn_data)

    churn_rate = churn_data['churn'].mean()
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

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
        st.metric("⚠️ Churn Rate", f"{churn_rate:.1%}")

    with col2:
        st.metric("📊 Accuracy", f"{accuracy:.1%}")

    with col3:
        st.metric("🎯 F1 Score", f"{f1:.1%}")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("📈 Precision", f"{precision:.1%}")

    with col5:
        st.metric("📉 Recall", f"{recall:.1%}")

    with col6:
        total_customers = len(churn_data)
        st.metric("👥 Total Customers", f"{total_customers:,}")

    col7, col8, col9 = st.columns(3)

    with col7:
        high_risk = len(churn_data[churn_data['churn'] == 1]) if 'churn' in churn_data.columns else 0
        st.metric("🔴 High Risk", f"{high_risk:,}")

    with col8:
        top_feature = importance_df['feature'].iloc[0] if not importance_df.empty else 'N/A'
        st.metric("🏆 Top Predictor", top_feature)

    with col9:
        churned = len(churn_data[churn_data['churn'] == 0]) if 'churn' in churn_data.columns else 0
        st.metric("🟢 Not Churned", f"{churned:,}")

    st.divider()

    fig1 = create_churn_distribution_chart(churn_data)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = create_feature_importance_chart(importance_df)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = create_confusion_matrix_chart(y_test, y_pred)
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = create_roc_curve_chart(y_test, y_proba)
    st.plotly_chart(fig4, use_container_width=True)



    fig5 = create_churn_risk_chart(churn_data)
    st.plotly_chart(fig5, use_container_width=True)






