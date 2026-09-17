"""
A/B Testing router — reads from processed campaign_ab_variants.csv and campaign_analytics.csv.
"""

import sys
from pathlib import Path

import pandas as pd
from fastapi import APIRouter

router = APIRouter(tags=["A/B Testing"])

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
PROCESSED = BASE_DIR / "data" / "processed"


def _safe_csv(name: str) -> pd.DataFrame:
    path = PROCESSED / name
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


@router.get("/ab-testing/summary")
def get_ab_summary():
    """Summary from campaign_ab_summary.csv."""
    df = _safe_csv("campaign_ab_summary.csv")
    if df.empty:
        return {"summary": []}
    return {"summary": df.fillna("").to_dict(orient="records")}


@router.get("/ab-testing/analytics")
def get_ab_analytics():
    """Aggregated A/B analytics from campaign_analytics.csv."""
    df = _safe_csv("campaign_analytics.csv")
    if df.empty:
        return {
            "a_wins": 0, "b_wins": 0, "ties": 0,
            "winning_variant": "N/A", "top_strategy": "N/A",
            "avg_score_a": 0.0, "avg_score_b": 0.0, "score_gap": 0.0,
            "objectives": [], "products": [],
        }

    a_wins = int((df.get("winning_variant", pd.Series(dtype=str)) == "A").sum())
    b_wins = int((df.get("winning_variant", pd.Series(dtype=str)) == "B").sum())
    ties = int((df.get("winning_variant", pd.Series(dtype=str)) == "Tie").sum())

    winning = "A" if a_wins > b_wins else ("B" if b_wins > a_wins else "Tie")
    top_strategy = "N/A"
    if "winning_strategy" in df.columns and not df["winning_strategy"].empty:
        vc = df["winning_strategy"].value_counts()
        top_strategy = str(vc.index[0]) if not vc.empty else "N/A"

    avg_a = float(pd.to_numeric(df.get("variant_a_score", 0), errors="coerce").fillna(0).mean())
    avg_b = float(pd.to_numeric(df.get("variant_b_score", 0), errors="coerce").fillna(0).mean())

    objectives = []
    if "campaign_objective" in df.columns:
        for obj, cnt in df["campaign_objective"].value_counts().items():
            objectives.append({"objective": str(obj), "count": int(cnt)})

    products = []
    if "product_name" in df.columns:
        for p, c in df["product_name"].value_counts().head(10).items():
            products.append({"product": str(p), "count": int(c)})

    return {
        "a_wins": a_wins,
        "b_wins": b_wins,
        "ties": ties,
        "winning_variant": winning,
        "top_strategy": top_strategy,
        "avg_score_a": round(avg_a, 2),
        "avg_score_b": round(avg_b, 2),
        "score_gap": round(abs(avg_a - avg_b), 2),
        "objectives": objectives,
        "products": products,
        "total": len(df),
    }


@router.get("/ab-testing/variants")
def get_ab_variants(page: int = 1, page_size: int = 20):
    """Paginated variant records."""
    df = _safe_csv("campaign_ab_variants.csv")
    if df.empty:
        return {"variants": [], "total": 0}
    total = len(df)
    chunk = df.iloc[(page - 1) * page_size: page * page_size]
    return {"variants": chunk.fillna("").to_dict(orient="records"), "total": total}
