from datetime import timedelta

import numpy as np
import pandas as pd
import streamlit as st

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import plotly.express as px
import plotly.graph_objects as go

import api


# ============================================================
# GLOBAL CHART STYLE
# ============================================================

CHART_BG = "#000000"
PLOT_BG = "#0a0a0a"
TEXT_COLOR = "#ffffff"
GRID_COLOR = "rgba(255,255,255,0.06)"

COLORS = {
    "primary": "#667eea",
    "purple": "#764ba2",
    "green": "#34d399",
    "red": "#ef4444",
    "orange": "#f59e0b",
    "blue": "#60a5fa",
    "pink": "#fb7185",
    "gray": "#9ca3af"
}


def apply_chart_style(fig, height=350):
    """
    Apply common dark/black styling to Plotly charts.
    """

    fig.update_layout(
        height=height,
        template="plotly_dark",

        # Black background
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=CHART_BG,

        # White text
        font=dict(
            color=TEXT_COLOR,
            family="Arial, sans-serif",
            size=12
        ),

        # Centered title
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(
                color=TEXT_COLOR,
                size=18
            )
        ),

        # Margins
        margin=dict(
            l=60,
            r=30,
            t=70,
            b=50
        ),

        # Legend
        legend=dict(
            font=dict(color=TEXT_COLOR),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    # Axis styling
    fig.update_xaxes(
        color=TEXT_COLOR,
        tickfont=dict(color=TEXT_COLOR),
        title_font=dict(color=TEXT_COLOR),
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR
    )

    fig.update_yaxes(
        color=TEXT_COLOR,
        tickfont=dict(color=TEXT_COLOR),
        title_font=dict(color=TEXT_COLOR),
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR
    )

    return fig


# ============================================================
# LOAD CHURN DATA
# ============================================================

@st.cache_data
def load_churn_data():
    """
    Load data for churn prediction.
    """

    daily_sales = api.get_daily_sales()

    if isinstance(daily_sales, list):
        daily_sales = pd.DataFrame(daily_sales)

    if "date" in daily_sales.columns:
        daily_sales["date"] = pd.to_datetime(
            daily_sales["date"],
            errors="coerce"
        )

    return daily_sales


# ============================================================
# PREPARE CHURN DATA
# ============================================================

def prepare_churn_data(daily_sales, rfm):
    """
    Prepare customer-level data for churn prediction.
    """

    daily_sales = daily_sales.copy()
    rfm = rfm.copy()

    if daily_sales.empty:
        return pd.DataFrame()

    current_date = daily_sales["date"].max()

    cutoff_date = current_date - timedelta(days=90)

    # --------------------------------------------------------
    # Last purchase
    # --------------------------------------------------------

    last_purchase = (
        daily_sales
        .groupby("customer_id")["date"]
        .max()
        .reset_index()
    )

    last_purchase["churn"] = (
        last_purchase["date"] < cutoff_date
    ).astype(int)

    # --------------------------------------------------------
    # Merge RFM
    # --------------------------------------------------------

    churn_data = rfm.merge(
        last_purchase[
            ["customer_id", "churn"]
        ],
        on="customer_id",
        how="left"
    )

    churn_data["churn"] = (
        churn_data["churn"]
        .fillna(1)
        .astype(int)
    )

    # --------------------------------------------------------
    # Customer features
    # --------------------------------------------------------

    customer_features = (
        daily_sales
        .groupby("customer_id")
        .agg({
            "receipt_id": "count",
            "revenue": ["sum", "mean", "std"],
            "units_sold": "sum"
        })
        .round(2)
    )

    customer_features.columns = [
        "total_transactions",
        "total_spent",
        "avg_spend",
        "spend_std",
        "total_quantity"
    ]

    customer_features = (
        customer_features
        .reset_index()
    )

    # --------------------------------------------------------
    # Merge features
    # --------------------------------------------------------

    churn_data = churn_data.merge(
        customer_features,
        on="customer_id",
        how="left"
    )

    churn_data = churn_data.fillna(0)

    return churn_data


# ============================================================
# TRAIN CHURN MODEL
# ============================================================

def train_churn_model(churn_data):
    """
    Train Random Forest churn prediction model.
    """

    feature_cols = [
        "recency",
        "frequency",
        "monetary",
        "total_transactions",
        "total_spent",
        "avg_spend",
        "spend_std",
        "total_quantity"
    ]

    feature_cols = [
        col
        for col in feature_cols
        if col in churn_data.columns
    ]

    if not feature_cols:
        raise ValueError(
            "No valid churn features found."
        )

    X = churn_data[feature_cols].copy()
    y = churn_data["churn"].copy()

    # --------------------------------------------------------
    # Make sure both classes exist
    # --------------------------------------------------------

    if len(y.unique()) < 2:

        churn_data["churn"] = (
            churn_data["recency"]
            >
            churn_data["recency"].quantile(0.7)
        ).astype(int)

        y = churn_data["churn"]

    if len(y.unique()) < 2:
        raise ValueError(
            "Churn data contains only one class."
        )

    # --------------------------------------------------------
    # Train / Test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    # --------------------------------------------------------
    # Scale
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight="balanced"
    )

    clf.fit(
        X_train_scaled,
        y_train
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    y_pred = clf.predict(
        X_test_scaled
    )

    if clf.n_classes_ == 2:

        y_proba = clf.predict_proba(
            X_test_scaled
        )[:, 1]

    else:

        y_proba = np.zeros(
            len(y_pred)
        )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": clf.feature_importances_
    }).sort_values(
        "importance",
        ascending=False
    )

    return (
        clf,
        scaler,
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
        y_pred,
        y_proba,
        importance_df,
        feature_cols
    )


# ============================================================
# 1. CHURN DISTRIBUTION
# ============================================================

def create_churn_distribution_chart(churn_data):
    """
    Churn Distribution - Donut Chart.
    """

    if churn_data is None or churn_data.empty:
        return go.Figure()

    churn_dist = (
        churn_data["churn"]
        .value_counts()
        .sort_index()
    )

    labels = []

    values = []

    for churn_value, count in churn_dist.items():

        if int(churn_value) == 0:
            labels.append("Not Churned")
        else:
            labels.append("Churned")

        values.append(count)

    fig = px.pie(
        values=values,
        names=labels,
        hole=0.55,
        color=labels,
        color_discrete_map={
            "Not Churned": COLORS["green"],
            "Churned": COLORS["red"]
        }
    )

    fig.update_layout(
        title=dict(
            text="Churn Distribution",
            x=0.5,
            xanchor="center",
            font=dict(
                color="white",
                size=18
            )
        )
    )

    apply_chart_style(
        fig,
        height=380
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",

        textfont=dict(
            color="white",
            size=12
        ),

        marker=dict(
            line=dict(
                color="#000000",
                width=2
            )
        ),

        hovertemplate=(
            "<b>%{label}</b>"
            "<br>Customers: %{value:,}"
            "<br>Share: %{percent}"
            "<extra></extra>"
        )
    )

    return fig


# ============================================================
# 2. FEATURE IMPORTANCE
# ============================================================

def create_feature_importance_chart(importance_df):
    """
    Top 10 Churn Predictors.
    """

    if (
        importance_df is None
        or importance_df.empty
    ):
        return go.Figure()

    data = importance_df.head(10).copy()

    fig = px.bar(
        data,
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale=[
            "#312e81",
            "#667eea",
            "#a78bfa"
        ]
    )

    fig.update_layout(
        title=dict(
            text="Top 10 Churn Predictors",
            x=0.5,
            xanchor="center"
        ),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(
            l=130,
            r=40,
            t=70,
            b=50
        )
    )

    apply_chart_style(
        fig,
        height=400
    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_traces(
        texttemplate="%{x:.3f}",
        textposition="outside",
        textfont=dict(
            color="white",
            size=11
        ),

        marker_line_width=0
    )

    return fig


# ============================================================
# 3. CONFUSION MATRIX
# ============================================================

def create_confusion_matrix_chart(
    y_test,
    y_pred
):
    """
    Confusion Matrix Heatmap.
    """

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    fig = px.imshow(
        cm,

        x=[
            "Not Churned",
            "Churned"
        ],

        y=[
            "Not Churned",
            "Churned"
        ],

        text_auto=True,

        color_continuous_scale=[
            "#0a0a0a",
            "#312e81",
            "#667eea"
        ]
    )

    fig.update_layout(
        title=dict(
            text="Confusion Matrix",
            x=0.5,
            xanchor="center"
        ),

        coloraxis_colorbar=dict(
            tickfont=dict(
                color="white"
            )
        )
    )

    apply_chart_style(
        fig,
        height=380
    )

    fig.update_traces(
        textfont=dict(
            color="white",
            size=18
        ),

        hovertemplate=(
            "Actual: %{y}"
            "<br>Predicted: %{x}"
            "<br>Count: %{z}"
            "<extra></extra>"
        )
    )

    return fig


# ============================================================
# 4. ROC CURVE
# ============================================================

def create_roc_curve_chart(
    y_test,
    y_proba
):
    """
    ROC Curve.
    """

    fig = go.Figure()

    # Check that both classes exist
    if len(np.unique(y_test)) < 2:

        fig.add_annotation(
            text="ROC Curve requires both churn classes",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                color="white",
                size=14
            )
        )

        apply_chart_style(
            fig,
            height=380
        )

        return fig

    fpr, tpr, _ = roc_curve(
        y_test,
        y_proba
    )

    roc_auc = auc(
        fpr,
        tpr
    )

    # ROC
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"ROC Curve (AUC = {roc_auc:.3f})",

            line=dict(
                color=COLORS["primary"],
                width=3
            ),

            hovertemplate=(
                "False Positive Rate: %{x:.3f}"
                "<br>True Positive Rate: %{y:.3f}"
                "<extra></extra>"
            )
        )
    )

    # Random classifier
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random Classifier",

            line=dict(
                color="#888888",
                dash="dash",
                width=1
            )
        )
    )

    fig.update_layout(
        title=dict(
            text="ROC Curve",
            x=0.5,
            xanchor="center"
        ),

        xaxis=dict(
            title="False Positive Rate",
            range=[0, 1]
        ),

        yaxis=dict(
            title="True Positive Rate",
            range=[0, 1]
        )
    )

    apply_chart_style(
        fig,
        height=380
    )

    return fig


# ============================================================
# 5. CHURN RISK DISTRIBUTION
# ============================================================

def create_churn_risk_chart(churn_data):
    """
    Churn Risk Distribution - Histogram.
    """

    if (
        churn_data is None
        or churn_data.empty
    ):
        return go.Figure()

    data = churn_data.copy()

    if "churn_probability" not in data.columns:

        # Better fallback:
        # use churn class instead of random values
        data["churn_probability"] = (
            data["churn"]
            .astype(float)
        )

    fig = px.histogram(
        data,
        x="churn_probability",
        nbins=30,
        color_discrete_sequence=[
            COLORS["orange"]
        ]
    )

    fig.update_layout(
        title=dict(
            text="Churn Risk Distribution",
            x=0.5,
            xanchor="center"
        ),

        showlegend=False,

        xaxis=dict(
            title="Churn Probability",
            range=[0, 1]
        ),

        yaxis=dict(
            title="Number of Customers"
        )
    )

    apply_chart_style(
        fig,
        height=380
    )

    fig.update_traces(
        marker=dict(
            color=COLORS["orange"],
            line=dict(
                color="#000000",
                width=1
            )
        )
    )

    return fig


# ============================================================
# 6. HIGH RISK CUSTOMERS
# ============================================================

def create_high_risk_customers_table(
    churn_data
):
    """
    High Risk Customers Table.
    """

    if (
        churn_data is None
        or churn_data.empty
    ):
        st.info(
            "No customer churn data available."
        )
        return

    data = churn_data.copy()

    if "churn_probability" not in data.columns:

        data["churn_probability"] = (
            data["churn"]
            .astype(float)
        )

    high_risk = (
        data
        .nlargest(
            10,
            "churn_probability"
        )
    )

    rows_html = ""

    for _, row in high_risk.iterrows():

        customer_id = str(
            row.get(
                "customer_id",
                "N/A"
            )
        )

        recency = float(
            row.get(
                "recency",
                0
            )
        )

        frequency = float(
            row.get(
                "frequency",
                0
            )
        )

        probability = float(
            row.get(
                "churn_probability",
                0
            )
        )

        if probability > 0.7:

            risk_color = COLORS["red"]

        elif probability > 0.4:

            risk_color = COLORS["orange"]

        else:

            risk_color = COLORS["green"]

        rows_html += f"""
        <div style="
            display:grid;
            grid-template-columns:
                1.4fr 1fr 1fr 1fr;
            padding:10px 12px;
            border-radius:7px;
            background:
                rgba(255,255,255,0.03);
            border:
                1px solid
                rgba(255,255,255,0.05);
            margin-bottom:6px;
        ">

            <div style="
                color:white;
                overflow:hidden;
                text-overflow:ellipsis;
            ">
                {customer_id[:12]}
            </div>

            <div style="
                color:rgba(255,255,255,0.65);
            ">
                {recency:.0f}d
            </div>

            <div style="
                color:rgba(255,255,255,0.65);
            ">
                {frequency:.0f}x
            </div>

            <div style="
                color:{risk_color};
                font-weight:700;
            ">
                {probability:.1%}
            </div>

        </div>
        """

    st.markdown(
        f"""
        <div style="
            background:#050505;
            border:
                1px solid
                rgba(255,255,255,0.10);
            padding:1.2rem;
            border-radius:12px;
            border-left:
                4px solid {COLORS["red"]};
        ">

            <h4 style="
                color:{COLORS["red"]};
                text-align:center;
                margin-top:0;
                margin-bottom:18px;
            ">
                ⚠️ HIGH RISK CUSTOMERS
            </h4>

            <div style="
                display:grid;
                grid-template-columns:
                    1.4fr 1fr 1fr 1fr;
                padding:8px 12px;
                color:
                    rgba(255,255,255,0.4);
                font-size:0.75rem;
                text-transform:uppercase;
            ">

                <div>Customer</div>
                <div>Recency</div>
                <div>Frequency</div>
                <div>Risk</div>

            </div>

            {rows_html}

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 7. MODEL PERFORMANCE CARD
# ============================================================

def create_churn_summary_card(
    y_test,
    y_pred
):
    """
    Model performance summary.
    """

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    st.markdown(
        f"""
        <div style="
            background:#050505;
            border:
                1px solid
                rgba(255,255,255,0.10);
            padding:1.2rem;
            border-radius:12px;
            border-left:
                4px solid {COLORS["primary"]};
        ">

            <h4 style="
                color:{COLORS["primary"]};
                text-align:center;
                margin-top:0;
                margin-bottom:18px;
            ">
                📊 MODEL PERFORMANCE
            </h4>

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:10px;
            ">

                <div style="
                    text-align:center;
                    padding:12px;
                    background:
                        rgba(255,255,255,0.03);
                    border-radius:8px;
                ">
                    <div style="
                        font-size:0.7rem;
                        color:
                            rgba(255,255,255,0.4);
                    ">
                        Accuracy
                    </div>

                    <div style="
                        font-size:1.5rem;
                        font-weight:700;
                        color:{COLORS["green"]};
                    ">
                        {accuracy:.1%}
                    </div>
                </div>


                <div style="
                    text-align:center;
                    padding:12px;
                    background:
                        rgba(255,255,255,0.03);
                    border-radius:8px;
                ">
                    <div style="
                        font-size:0.7rem;
                        color:
                            rgba(255,255,255,0.4);
                    ">
                        Precision
                    </div>

                    <div style="
                        font-size:1.5rem;
                        font-weight:700;
                        color:{COLORS["primary"]};
                    ">
                        {precision:.1%}
                    </div>
                </div>


                <div style="
                    text-align:center;
                    padding:12px;
                    background:
                        rgba(255,255,255,0.03);
                    border-radius:8px;
                ">
                    <div style="
                        font-size:0.7rem;
                        color:
                            rgba(255,255,255,0.4);
                    ">
                        Recall
                    </div>

                    <div style="
                        font-size:1.5rem;
                        font-weight:700;
                        color:{COLORS["orange"]};
                    ">
                        {recall:.1%}
                    </div>
                </div>


                <div style="
                    text-align:center;
                    padding:12px;
                    background:
                        rgba(255,255,255,0.03);
                    border-radius:8px;
                ">
                    <div style="
                        font-size:0.7rem;
                        color:
                            rgba(255,255,255,0.4);
                    ">
                        F1 Score
                    </div>

                    <div style="
                        font-size:1.5rem;
                        font-weight:700;
                        color:{COLORS["pink"]};
                    ">
                        {f1:.1%}
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 8. RECOMMENDATIONS
# ============================================================

def create_recommendations_card():
    """
    Churn prevention recommendations.
    """

    st.markdown(
        f"""
        <div style="
            background:#050505;
            border:
                1px solid
                rgba(255,255,255,0.10);
            padding:1.2rem;
            border-radius:12px;
            border-left:
                4px solid {COLORS["orange"]};
        ">

            <h4 style="
                color:{COLORS["orange"]};
                text-align:center;
                margin-top:0;
                margin-bottom:18px;
            ">
                🎯 PREVENTION RECOMMENDATIONS
            </h4>


            <div style="
                font-size:0.9rem;
                color:
                    rgba(255,255,255,0.85);
            ">

                <div style="
                    padding:8px 0;
                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.05);
                ">
                    🎯
                    <b>Re-engagement Campaigns</b>
                    <br>

                    <span style="
                        font-size:0.8rem;
                        color:
                            rgba(255,255,255,0.5);
                    ">
                        Target customers with
                        recency greater than 60 days.
                    </span>
                </div>


                <div style="
                    padding:8px 0;
                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.05);
                ">
                    📧
                    <b>Email Marketing</b>
                    <br>

                    <span style="
                        font-size:0.8rem;
                        color:
                            rgba(255,255,255,0.5);
                    ">
                        Exclusive discounts for
                        high-risk customers.
                    </span>
                </div>


                <div style="
                    padding:8px 0;
                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.05);
                ">
                    📱
                    <b>Push Notifications</b>
                    <br>

                    <span style="
                        font-size:0.8rem;
                        color:
                            rgba(255,255,255,0.5);
                    ">
                        Product recommendations
                        based on previous purchases.
                    </span>
                </div>


                <div style="
                    padding:8px 0;
                    border-bottom:
                        1px solid
                        rgba(255,255,255,0.05);
                ">
                    💰
                    <b>Loyalty Rewards</b>
                    <br>

                    <span style="
                        font-size:0.8rem;
                        color:
                            rgba(255,255,255,0.5);
                    ">
                        Points for repeat purchases
                        and VIP tiers.
                    </span>
                </div>


                <div style="
                    padding:8px 0;
                ">
                    🔄
                    <b>Win-Back Campaigns</b>
                    <br>

                    <span style="
                        font-size:0.8rem;
                        color:
                            rgba(255,255,255,0.5);
                    ">
                        Special welcome-back
                        discounts for lost customers.
                    </span>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )