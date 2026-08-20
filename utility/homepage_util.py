"""
HOMEPAGE UTILITY - Complete Home Page
"""
import pandas as pd
import streamlit as st
from datetime import datetime
import api


def show_home():

    def safe_dict(value):

        if isinstance(value, dict):
            return value

        return {}

    # ============================
    # DICTIONARY/API DATA
    # ============================

    product_summary = safe_dict(
        api.get_product_summary()
    )

    sales_summary = safe_dict(
        api.get_sales_summary()
    )

    metrics = safe_dict(
        api.get_sales_metrics()
    )

    # ============================
    # DATAFRAME DATA
    # ============================

    customers = api.get_customer()

    if customers is None:
        customers = pd.DataFrame()

    elif isinstance(customers, dict):

        if "results" in customers:
            customers = pd.DataFrame(
                customers["results"]
            )
        else:
            customers = pd.DataFrame(
                [customers]
            )

    elif isinstance(customers, list):

        customers = pd.DataFrame(
            customers
        )


    daily_sales = api.get_daily_sales()

    if daily_sales is None:
        daily_sales = pd.DataFrame()

    elif isinstance(daily_sales, dict):

        if "results" in daily_sales:
            daily_sales = pd.DataFrame(
                daily_sales["results"]
            )
        else:
            daily_sales = pd.DataFrame(
                [daily_sales]
            )

    elif isinstance(daily_sales, list):

        daily_sales = pd.DataFrame(
            daily_sales
        )

    # Debug prints (remove in production)
    print("Product Summary:", product_summary)
    print("Sales Summary:", sales_summary)
    print("Metrics:", metrics)

    # Company Header
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
    </style>
    <div class='main-header'>
        <h1>🚀 RetailPulse AI Analytics Platform</h1>
        <p>AI-Powered Retail Analytics • Demand Forecasting • Customer Insights • Inventory Optimization</p>
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

    # ============================================
    # KEY METRICS WITH SAFE ACCESS
    # ============================================

    col1, col2, col3, col4 = st.columns(4)

    if metrics and isinstance(metrics, dict):
        with col1:
            st.metric(
                "💰 Total Revenue",
                f"₹{metrics.get('total_revenue', 0):,.0f}"
            )

        with col2:
            st.metric(
                "📦 Total Units Sold",
                f"{metrics.get('total_units', 0):,}"
            )

        with col3:
            st.metric(
                "🧾 Total Orders",
                f"{metrics.get('total_orders', 0):,}"
            )

        with col4:
            st.metric(
                "💵 Avg Order Value",
                f"₹{metrics.get('avg_order_value', 0):,.2f}"
            )

    # Second row

    st.markdown("")

    col5, col6, col7, col8 = st.columns(4)

    if metrics and isinstance(metrics, dict):

        with col5:
            st.metric(
                "👥 Total Customers",
                f"{metrics.get('total_customers', 0):,}"
            )

        with col6:
            st.metric(
                "🏷️ Total SKUs",
                f"{metrics.get('total_skus', 0):,}"
            )

        with col7:
            st.metric(
                "🏪 Total Stores",
                f"{metrics.get('total_stores', 0):,}"
            )

        with col8:
            st.metric(
                "📅 Analysis Year",
                f"{metrics.get('year', '2024')}"
            )


    else:

        with col1:
            st.metric(
                "💰 Total Revenue",
                "₹0"
            )

        with col2:
            st.metric(
                "📦 Total Units Sold",
                "0"
            )

        with col3:
            st.metric(
                "🧾 Total Orders",
                "0"
            )

        with col4:
            st.metric(
                "💵 Avg Order Value",
                "₹0.00"
            )

        with col5:
            st.metric(
                "👥 Total Customers",
                "0"
            )

        with col6:
            st.metric(
                "🏷️ Total SKUs",
                "0"
            )

        with col7:
            st.metric(
                "🏪 Total Stores",
                "0"
            )

        with col8:
            st.metric(
                "📅 Analysis Year",
                "N/A"
            )

        st.warning(
            "⚠️ Unable to load sales metrics. Check Django API connection."
        )

    st.markdown("---")

    # ============================================
    # PLATFORM FEATURES
    # ============================================

    st.subheader("🌟 Platform Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-box'>
            <h4>📊 Analytics & Insights</h4>
            <ul>
                <li>Real-time Business Intelligence</li>
                <li>Sales & Revenue Analytics</li>
                <li>Product & Category Performance</li>
                <li>Customer Behavior Analysis</li>
                <li>Inventory Health Monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-box'>
            <h4>🤖 AI & Machine Learning</h4>
            <ul>
                <li>Demand Forecasting (Prophet + LSTM)</li>
                <li>Customer Segmentation (KMeans + RFM)</li>
                <li>Churn Prediction (Random Forest)</li>
                <li>Inventory Optimization</li>
                <li>Stockout Risk Detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-box'>
            <h4>📈 Business Impact</h4>
            <ul>
                <li>25% Reduction in Stockouts</li>
                <li>30% Less Overstock</li>
                <li>15% Increase in Revenue</li>
                <li>20% Customer Retention</li>
                <li>₹5M+ Working Capital Freed</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ============================================
    # TECHNOLOGY STACK
    # ============================================

    st.subheader("🛠️ Technology Stack")

    tech_col1, tech_col2, tech_col3 = st.columns(3)

    with tech_col1:
        st.markdown("""
        **📊 Frontend**
        - Streamlit
        - Plotly
        - Matplotlib
        - Seaborn
        """)

    with tech_col2:
        st.markdown("""
        **🧠 Machine Learning**
        - Prophet
        - XGBoost
        - LightGBM
        - Scikit-learn
        - TensorFlow
        """)

    with tech_col3:
        st.markdown("""
        **📦 Backend**
        - Python
        - Pandas
        - NumPy
        - Django
        - PostgreSQL
        """)

    st.markdown("---")

    # ============================================
    # QUICK ACCESS
    # ============================================

    st.subheader("🚀 Quick Access Dashboards")

    quick_buttons = [
        ("📊 Executive Dashboard", "executive"),
        ("📈 Sales Analytics", "sales"),
        ("📦 Inventory Dashboard", "inventory"),
        ("⚠️ Stockout Risk", "stockout"),
        ("🤖 ML Performance", "ml_performance"),
        ("📊 Business Intelligence", "bi")
    ]

    for i in range(0, len(quick_buttons), 3):
        cols = st.columns(3)
        for j, (label, page) in enumerate(quick_buttons[i:i + 3]):
            with cols[j]:
                if st.button(label, use_container_width=True):
                    st.session_state.page = page
                    st.rerun()

    # ============================================
    # COMPANY DETAILS
    # ============================================

    with st.expander("🏢 Company Details", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **📍 Address**

            RetailPulse AI Analytics
            Zidio Data Science Division
            Innovation Hub, Tech Park
            Bangalore, India - 560001
            """)

        with col2:
            st.markdown("""
            **📧 Contact**

            Email: analytics@retailpulse.ai
            Phone: +91-80-1234-5678
            Website: www.retailpulse.ai
            """)

    # ============================================
    # DATA SUMMARY WITH SAFE ACCESS
    # ============================================

    with st.expander("📊 Data Summary", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Sales Data**")

            # Safe access with fallback values
            if sales_summary and isinstance(sales_summary, dict):
                st.write(f"- Total Records: {sales_summary.get('total_records', 0):,}")
                st.write(
                    f"- Date Range: {sales_summary.get('start_date', 'N/A')} to {sales_summary.get('end_date', 'N/A')}")
                st.write(f"- Unique SKUs: {sales_summary.get('unique_skus', 0):,}")
            else:
                st.write("- Total Records: N/A")
                st.write("- Date Range: N/A")
                st.write("- Unique SKUs: N/A")

        with col2:
            st.markdown("**Product Data**")

            # Safe access with fallback values
            if product_summary and isinstance(product_summary, dict):
                st.write(f"- Total SKUs: {product_summary.get('total_skus', 0):,}")
                st.write(f"- Categories: {product_summary.get('categories', 0):,}")
                st.write(f"- Stores: {product_summary.get('stores', 0):,}")
            else:
                st.write("- Total SKUs: N/A")
                st.write("- Categories: N/A")
                st.write("- Stores: N/A")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Customer Data**")

            # -----------------------------
            # Customer data
            # -----------------------------
            if customers is not None and not customers.empty:

                total_customers = len(customers)

                # Active customers
                if "customer_id" in daily_sales.columns:
                    active_customers = daily_sales["customer_id"].dropna().nunique()
                else:
                    active_customers = 0

                # New customers
                new_customers = 0

                if "created_at" in customers.columns:
                    customer_dates = pd.to_datetime(
                        customers["created_at"],
                        errors="coerce"
                    )

                    cutoff_date = pd.Timestamp.today() - pd.Timedelta(days=30)

                    new_customers = (
                        customer_dates.ge(cutoff_date)
                        .sum()
                    )

                # Top region
                top_region = "N/A"

                if "region" in customers.columns:

                    region_counts = (
                        customers["region"]
                        .dropna()
                        .value_counts()
                    )

                    if not region_counts.empty:
                        top_region = region_counts.index[0]

                st.write(
                    f"- Total Customers: {total_customers:,}"
                )

                st.write(
                    f"- Active Customers: {active_customers:,}"
                )

                st.write(
                    f"- New Customers (30 days): {new_customers:,}"
                )

                st.write(
                    f"- Top Region: {top_region}"
                )

            else:

                st.write("- Total Customers: N/A")
                st.write("- Active Customers: N/A")
                st.write("- New Customers (30 days): N/A")
                st.write("- Top Region: N/A")

        with col4:
            st.markdown("**Customer Behavior**")

            if (
                    customers is not None
                    and not customers.empty
                    and daily_sales is not None
                    and not daily_sales.empty
            ):

                # -----------------------------
                # Average Order Value
                # -----------------------------
                if (
                        "revenue" in daily_sales.columns
                        and "receipt_id" in daily_sales.columns
                ):

                    order_revenue = (
                        daily_sales
                        .groupby("receipt_id")["revenue"]
                        .sum()
                    )

                    avg_order_value = (
                        order_revenue.mean()
                        if not order_revenue.empty
                        else 0
                    )

                else:
                    avg_order_value = 0

                # -----------------------------
                # Customer Lifetime Value
                # -----------------------------
                if (
                        "customer_id" in daily_sales.columns
                        and "revenue" in daily_sales.columns
                ):

                    customer_revenue = (
                        daily_sales
                        .dropna(subset=["customer_id"])
                        .groupby("customer_id")["revenue"]
                        .sum()
                    )

                    customer_lifetime_value = (
                        customer_revenue.mean()
                        if not customer_revenue.empty
                        else 0
                    )

                else:
                    customer_lifetime_value = 0

                # -----------------------------
                # Repeat Purchase Rate
                # -----------------------------
                repeat_purchase_rate = 0

                if (
                        "customer_id" in daily_sales.columns
                        and "receipt_id" in daily_sales.columns
                ):

                    customer_orders = (
                        daily_sales
                        .dropna(subset=["customer_id"])
                        .groupby("customer_id")["receipt_id"]
                        .nunique()
                    )

                    if not customer_orders.empty:

                        repeat_customers = (
                                customer_orders >= 2
                        ).sum()

                        total_purchasing_customers = (
                                customer_orders > 0
                        ).sum()

                        if total_purchasing_customers > 0:
                            repeat_purchase_rate = (
                                    repeat_customers
                                    / total_purchasing_customers
                            )

                # -----------------------------
                # Gender Distribution
                # -----------------------------
                gender_pct = {}

                if "gender" in customers.columns:
                    gender_pct = (
                        customers["gender"]
                        .dropna()
                        .value_counts(normalize=True)
                        .mul(100)
                        .round(1)
                        .to_dict()
                    )

                # -----------------------------
                # Display
                # -----------------------------
                st.write(
                    f"- Avg. Order Value: "
                    f"${avg_order_value:,.2f}"
                )

                st.write(
                    f"- Customer Lifetime Value: "
                    f"${customer_lifetime_value:,.2f}"
                )

                st.write(
                    f"- Repeat Purchase Rate: "
                    f"{repeat_purchase_rate:.1%}"
                )

                if gender_pct:

                    dist_str = ", ".join(
                        f"{k}: {v:.1f}%"
                        for k, v in gender_pct.items()
                    )

                    st.write(
                        f"- Gender Distribution: {dist_str}"
                    )

                else:

                    st.write(
                        "- Gender Distribution: N/A"
                    )

            else:

                st.write("- Avg. Order Value: N/A")
                st.write("- Customer Lifetime Value: N/A")
                st.write("- Repeat Purchase Rate: N/A")
                st.write("- Gender Distribution: N/A")
    # ============================================
    # FOOTER
    # ============================================

    st.markdown(f"""
    <div class='footer'>
        <p>© 2024 RetailPulse AI Analytics Platform | Powered by Zidio Data Science</p>
        <p style='font-size: 11px;'>Built with ❤️ using Streamlit, Python, and AI</p>
        <p style='font-size: 11px; color: #999;'>Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)