"""
Customers router — reads from existing processed CSVs.
"""

import math
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Query

router = APIRouter(tags=["Customers"])

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED = BASE_DIR / "data" / "processed"


def _load_customers() -> pd.DataFrame:
    """Load the richest available customer file."""
    for name in ("customer_segments.csv", "customers.csv", "customer_360.csv"):
        path = PROCESSED / name
        if path.exists():
            try:
                return pd.read_csv(path)
            except Exception:
                pass
    return pd.DataFrame()


@router.get("/customers")
def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
):
    df = _load_customers()
    if df.empty:
        return {"customers": [], "total": 0, "page": page, "pages": 0}

    # Normalise column names
    if "primary_segment" in df.columns and "segment" not in df.columns:
        df["segment"] = df["primary_segment"]

    # Search filter
    if search:
        mask = df["customer_id"].astype(str).str.contains(search, case=False, na=False)
        for col in ("customer_persona", "segment", "primary_segment"):
            if col in df.columns:
                mask |= df[col].astype(str).str.contains(search, case=False, na=False)
        df = df[mask]

    # Segment filter
    if segment and segment != "All":
        seg_col = "primary_segment" if "primary_segment" in df.columns else "segment"
        if seg_col in df.columns:
            df = df[df[seg_col].astype(str) == segment]

    total = len(df)
    pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    chunk = df.iloc[start:end]

    # Select safe columns (no PII beyond customer_id)
    safe_cols = [c for c in [
        "customer_id", "primary_segment", "segment", "customer_persona",
        "retention_risk", "cross_sell_opportunity", "genai_targeting_priority",
        "preferred_channel", "consent_status",
    ] if c in chunk.columns]

    records = chunk[safe_cols].fillna("").to_dict(orient="records")
    return {"customers": records, "total": total, "page": page, "pages": pages}


@router.get("/customers/segments-list")
def get_segment_options():
    """Return the unique segment values for the filter dropdown."""
    df = _load_customers()
    if df.empty:
        return {"segments": []}
    col = "primary_segment" if "primary_segment" in df.columns else "segment"
    if col not in df.columns:
        return {"segments": []}
    segs = sorted(df[col].dropna().astype(str).unique().tolist())
    return {"segments": segs}


@router.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    df = _load_customers()
    if df.empty:
        return {"customer": None}
    row = df[df["customer_id"].astype(str) == customer_id]
    if row.empty:
        return {"customer": None}
    return {"customer": row.iloc[0].fillna("").to_dict()}
