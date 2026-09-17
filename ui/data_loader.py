import pandas as pd
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    path = PROCESSED_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def load_processed_data(filename: str) -> pd.DataFrame:
    """Backward-compatible generic loader used by older UI pages."""
    return load_csv(filename)


def load_customers() -> pd.DataFrame:
    for filename in ("customers.csv", "customer_segments.csv", "customer_360.csv"):
        df = load_csv(filename)
        if not df.empty:
            return df
    return pd.DataFrame()


def load_products() -> pd.DataFrame:
    for filename in ("products.csv", "product_catalog.csv"):
        df = load_csv(filename)
        if not df.empty:
            return df
    return pd.DataFrame()


def load_recommendations() -> pd.DataFrame:
    return load_csv("customer_recommendations.csv")


def load_customer_recommendations() -> pd.DataFrame:
    return load_recommendations()


def load_campaign_content() -> pd.DataFrame:
    return load_csv("campaign_content.csv")


def load_ab_variants() -> pd.DataFrame:
    return load_csv("campaign_ab_variants.csv")


def load_campaign_ab_variants() -> pd.DataFrame:
    return load_ab_variants()


def load_campaign_analytics() -> pd.DataFrame:
    return load_csv("campaign_analytics.csv")


def load_ab_summary() -> pd.DataFrame:
    return load_csv("campaign_ab_summary.csv")


def load_segments() -> pd.DataFrame:
    for filename in (
        "customer_segments.csv",
        "segments.csv",
        "customer_rfm_segments.csv",
    ):
        df = load_csv(filename)
        if not df.empty:
            return df
    return pd.DataFrame()


def ensure_segments(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    if "primary_segment" not in result.columns:
        if "segment" in result.columns:
            result["primary_segment"] = result["segment"]
        elif "customer_segment" in result.columns:
            result["primary_segment"] = result["customer_segment"]

    if "segment" not in result.columns:
        if "primary_segment" in result.columns:
            result["segment"] = result["primary_segment"]
        else:
            result["segment"] = "Unclassified"

    return result


def get_customer(customer_id):
    df = load_customers()
    if df.empty or "customer_id" not in df.columns:
        return None
    result = df[df["customer_id"].astype(str) == str(customer_id)]
    return result.iloc[0] if not result.empty else None


def get_campaign(customer_id):
    df = load_ab_variants()
    if df.empty or "customer_id" not in df.columns:
        return None
    result = df[df["customer_id"].astype(str) == str(customer_id)]
    return result.iloc[0] if not result.empty else None


def get_campaign_analytics(customer_id):
    df = load_campaign_analytics()
    if df.empty or "customer_id" not in df.columns:
        return None
    result = df[df["customer_id"].astype(str) == str(customer_id)]
    return result.iloc[0] if not result.empty else None
