import streamlit as st
import pandas as pd
from pathlib import Path


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"


# ============================================================
# CSV DATA
# ============================================================

# @st.cache_data(ttl=3600)
# def get_sales():
#
#     return pd.read_csv(
#         DATASET_DIR / "sale.csv"
#     )


@st.cache_data(ttl=3600)
def get_daily_sales():

    df = pd.read_csv(
        DATASET_DIR / "daily_sale.csv"
    )

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


@st.cache_data(ttl=3600)
def get_stores():

    df = pd.read_csv(
        DATASET_DIR / "store.csv"
    )

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


@st.cache_data(ttl=3600)
def get_inventary():

    df = pd.read_csv(
        DATASET_DIR / "inventory.csv"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


@st.cache_data(ttl=3600)
def get_customer():

    df = pd.read_csv(
        DATASET_DIR / "customer.csv"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


def get_customer_summary() -> dict:
    """Generate customer summary metrics from customer DataFrame"""

    df = get_customer()

    if df.empty:
        return {}

    summary = {}

    # Total customers
    summary["total_customers"] = len(df)

    # Active customers
    if "status" in df.columns:

        summary["active_customers"] = len(
            df[df["status"].astype(str).str.lower() == "active"]
        )

    elif "last_purchase_date" in df.columns:

        cutoff_date = (
            pd.Timestamp.now()
            - pd.Timedelta(days=90)
        )

        df["last_purchase_date"] = pd.to_datetime(
            df["last_purchase_date"],
            errors="coerce"
        )

        summary["active_customers"] = len(
            df[df["last_purchase_date"] >= cutoff_date]
        )

    else:

        summary["active_customers"] = len(df)

    # New customers - last 30 days
    if "signup_date" in df.columns:

        cutoff_date = (
            pd.Timestamp.now()
            - pd.Timedelta(days=30)
        )

        df["signup_date"] = pd.to_datetime(
            df["signup_date"],
            errors="coerce"
        )

        summary["new_customers"] = len(
            df[df["signup_date"] >= cutoff_date]
        )

    elif "registration_date" in df.columns:

        cutoff_date = (
            pd.Timestamp.now()
            - pd.Timedelta(days=30)
        )

        df["registration_date"] = pd.to_datetime(
            df["registration_date"],
            errors="coerce"
        )

        summary["new_customers"] = len(
            df[df["registration_date"] >= cutoff_date]
        )

    else:

        summary["new_customers"] = 0

    # Average order value / CLV
    if "total_spent" in df.columns:

        summary["avg_order_value"] = (
            df["total_spent"].mean()
        )

        summary["clv"] = (
            df["total_spent"].mean()
        )

    elif "purchase_amount" in df.columns:

        summary["avg_order_value"] = (
            df["purchase_amount"].mean()
        )

        summary["clv"] = (
            df["purchase_amount"].mean()
        )

    else:

        summary["avg_order_value"] = 0.0
        summary["clv"] = 0.0

    # Repeat purchase rate
    if "order_count" in df.columns:

        repeat_customers = len(
            df[df["order_count"] > 1]
        )

        summary["repeat_rate"] = (
            repeat_customers / len(df)
            if len(df) > 0
            else 0
        )

    elif "total_orders" in df.columns:

        repeat_customers = len(
            df[df["total_orders"] > 1]
        )

        summary["repeat_rate"] = (
            repeat_customers / len(df)
            if len(df) > 0
            else 0
        )

    else:

        summary["repeat_rate"] = 0.0

    # Region
    if "region" in df.columns or "country" in df.columns:

        region_col = (
            "region"
            if "region" in df.columns
            else "country"
        )

        region_values = (
            df[region_col]
            .dropna()
        )

        if not region_values.empty:
            summary["top_region"] = (
                region_values.mode().iloc[0]
            )
        else:
            summary["top_region"] = "N/A"

    # Gender
    if "gender" in df.columns:

        summary["gender_distribution"] = (
            df["gender"]
            .value_counts()
            .to_dict()
        )

    return summary


@st.cache_data(ttl=3600)
def get_promotion():

    df = pd.read_csv(
        DATASET_DIR / "promotions.csv"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


@st.cache_data(ttl=3600)
def get_sales_summary():

    df = get_daily_sales()

    if df.empty:

        return {
            "total_records": 0,
            "start_date": None,
            "end_date": None,
            "unique_skus": 0,
        }

    # Normalize date column
    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # Get valid dates
    if "date" in df.columns:

        valid_dates = (
            df["date"]
            .dropna()
        )

    else:

        valid_dates = pd.Series(dtype="datetime64[ns]")

    if len(valid_dates) > 0:

        start_date = (
            valid_dates
            .min()
            .strftime("%Y-%m-%d")
        )

        end_date = (
            valid_dates
            .max()
            .strftime("%Y-%m-%d")
        )

    else:

        start_date = None
        end_date = None

    return {

        "total_records": len(df),

        "start_date": start_date,

        "end_date": end_date,

        "unique_skus": (
            df["sku_id"].nunique()
            if "sku_id" in df.columns
            else 0
        ),
    }


@st.cache_data(ttl=3600)
def get_skus():

    df = pd.read_csv(
        DATASET_DIR / "skus.csv"
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


@st.cache_data(ttl=3600)
def get_sales_metrics():

    df = get_daily_sales()

    if df.empty:
        return {
            "total_revenue": 0,
            "total_units": 0,
            "total_orders": 0,
            "total_skus": 0,
            "total_stores": 0,
            "total_customers": 0,
            "avg_order_value": 0,
        }

    total_orders = (
        df["receipt_id"].nunique()
        if "receipt_id" in df.columns
        else 0
    )

    return {

        "total_revenue": (
            df["revenue"].sum()
            if "revenue" in df.columns
            else 0
        ),

        "total_units": (
            df["units_sold"].sum()
            if "units_sold" in df.columns
            else 0
        ),

        "total_orders": total_orders,

        "total_skus": (
            df["sku_id"].nunique()
            if "sku_id" in df.columns
            else 0
        ),

        "total_stores": (
            df["store_id"].nunique()
            if "store_id" in df.columns
            else 0
        ),

        "total_customers": (
            df["customer_id"].nunique()
            if "customer_id" in df.columns
            else 0
        ),

        "avg_order_value": (
            df["revenue"].sum() / total_orders
            if total_orders > 0
            else 0
        ),
    }


@st.cache_data(ttl=3600)
def get_monthly_sales():

    df = get_daily_sales()

    return (
        df.groupby(
            ["year", "month"],
            as_index=False
        )
        .agg(
            revenue=("revenue", "sum"),
            units_sold=("units_sold", "sum")
        )
        .sort_values(
            ["year", "month"]
        )
    )


@st.cache_data(ttl=3600)
def get_category_revenue():

    df = get_daily_sales()

    return (
        df.groupby(
            "category",
            as_index=False
        )
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )


@st.cache_data(ttl=3600)
def get_product_summary():

    sku = get_skus()
    stores = get_stores()

    return {

        "total_skus": (
            sku["sku_id"].nunique()
        ),

        "categories": (
            sku["category"].nunique()
        ),

        "stores": (
            stores["store_id"].nunique()
        ),
    }