"""
Recommendations router — reads from existing customer_recommendations.csv.
"""

import math
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Query

router = APIRouter(tags=["Recommendations"])

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED = BASE_DIR / "data" / "processed"


def _load_recs() -> pd.DataFrame:
    path = PROCESSED / "customer_recommendations.csv"
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


@router.get("/recommendations")
def get_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    customer_id: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
):
    df = _load_recs()
    if df.empty:
        return {"recommendations": [], "total": 0, "page": page, "pages": 0}

    if customer_id:
        df = df[df["customer_id"].astype(str) == customer_id]
    if product and product != "All":
        df = df[df["product_name"].astype(str) == product]

    total = len(df)
    pages = max(1, math.ceil(total / page_size))
    chunk = df.iloc[(page - 1) * page_size: page * page_size]

    display_cols = [c for c in [
        "customer_id", "product_name", "recommendation_score",
        "recommendation_confidence", "recommendation_reason", "campaign_objective",
    ] if c in chunk.columns]

    records = chunk[display_cols].fillna("").to_dict(orient="records")
    return {"recommendations": records, "total": total, "page": page, "pages": pages}


@router.get("/recommendations/products-list")
def get_product_options():
    df = _load_recs()
    if df.empty or "product_name" not in df.columns:
        return {"products": []}
    products = sorted(df["product_name"].dropna().astype(str).unique().tolist())
    return {"products": products}


@router.get("/recommendations/summary")
def get_recommendations_summary():
    df = _load_recs()
    if df.empty:
        return {"total": 0, "customers": 0, "products": 0, "product_distribution": []}

    dist = []
    if "product_name" in df.columns:
        for p, c in df["product_name"].value_counts().items():
            dist.append({"product": str(p), "count": int(c)})

    return {
        "total": len(df),
        "customers": int(df["customer_id"].nunique()) if "customer_id" in df.columns else 0,
        "products": int(df["product_name"].nunique()) if "product_name" in df.columns else 0,
        "product_distribution": dist,
    }


@router.get("/recommendations/{customer_id}")
def get_customer_recommendations(customer_id: str):
    df = _load_recs()
    if df.empty or "customer_id" not in df.columns:
        return {"recommendations": []}
    recs = df[df["customer_id"].astype(str) == customer_id]
    display_cols = [c for c in [
        "product_name", "recommendation_score", "recommendation_confidence",
        "recommendation_reason", "campaign_objective",
    ] if c in recs.columns]
    return {"recommendations": recs[display_cols].fillna("").to_dict(orient="records")}
