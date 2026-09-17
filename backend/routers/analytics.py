"""
Analytics router — reads from SQLite + processed CSVs for dashboard KPIs.
"""

import sys
from pathlib import Path

import pandas as pd
from fastapi import APIRouter

router = APIRouter(tags=["Analytics"])

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


@router.get("/analytics/summary")
def get_analytics_summary():
    """Platform-wide KPI summary for the dashboard."""
    import finora_db

    # SQLite data
    db_campaigns = finora_db.campaigns()
    db_deliveries = finora_db.deliveries()

    # CSV data
    customers_df = _safe_csv("customer_segments.csv")
    recs_df = _safe_csv("customer_recommendations.csv")
    ab_df = _safe_csv("campaign_ab_variants.csv")

    total_customers = int(customers_df["customer_id"].nunique()) \
        if "customer_id" in customers_df.columns else 0

    active_segments = int(customers_df["primary_segment"].nunique()) \
        if "primary_segment" in customers_df.columns else 0

    total_recs = len(recs_df)

    # Campaign stats from SQLite
    total_campaigns = len(db_campaigns)
    approved = sum(1 for c in db_campaigns if c.get("status") == "Approved")
    sent = sum(1 for d in db_deliveries if d.get("status") in ("SENT", "DRY_RUN_SIMULATED"))

    # Status distribution
    status_dist = {}
    for c in db_campaigns:
        s = c.get("status", "Unknown")
        status_dist[s] = status_dist.get(s, 0) + 1

    # Segment distribution from CSV
    seg_dist = []
    if "primary_segment" in customers_df.columns:
        for seg, cnt in customers_df["primary_segment"].value_counts().items():
            seg_dist.append({"segment": str(seg), "count": int(cnt)})

    # Product distribution from recommendations
    prod_dist = []
    if "product_name" in recs_df.columns:
        for p, c in recs_df["product_name"].value_counts().head(10).items():
            prod_dist.append({"product": str(p), "count": int(c)})

    # A/B analytics
    ab_summary = {}
    ab_analytics = _safe_csv("campaign_analytics.csv")
    if not ab_analytics.empty:
        if "winning_variant" in ab_analytics.columns:
            vc = ab_analytics["winning_variant"].value_counts()
            ab_summary["a_wins"] = int(vc.get("A", 0))
            ab_summary["b_wins"] = int(vc.get("B", 0))
            ab_summary["ties"] = int(vc.get("Tie", 0))
        if "winning_strategy" in ab_analytics.columns:
            vc2 = ab_analytics["winning_strategy"].value_counts()
            ab_summary["top_strategy"] = str(vc2.index[0]) if not vc2.empty else "N/A"

    return {
        "total_customers": total_customers,
        "active_segments": active_segments,
        "total_recommendations": total_recs,
        "total_campaigns": total_campaigns,
        "approved_campaigns": approved,
        "messages_sent": sent,
        "ab_variants": len(ab_df),
        "delivery_records": len(db_deliveries),
        "campaign_status_distribution": status_dist,
        "segment_distribution": seg_dist,
        "product_distribution": prod_dist,
        "ab_summary": ab_summary,
    }


@router.get("/analytics/campaigns")
def get_campaign_analytics():
    """Detailed campaign analytics from SQLite."""
    import finora_db
    campaigns = finora_db.campaigns()
    deliveries = finora_db.deliveries()

    # Segment-wise campaign count
    seg_campaign = {}
    for c in campaigns:
        seg = c.get("segment", "Unknown") or "Unknown"
        seg_campaign[seg] = seg_campaign.get(seg, 0) + 1

    # Channel-wise delivery count
    channel_dist = {}
    for d in deliveries:
        ch = d.get("channel", "Unknown") or "Unknown"
        channel_dist[ch] = channel_dist.get(ch, 0) + 1

    return {
        "campaigns": campaigns,
        "deliveries": deliveries,
        "segment_campaign_distribution": seg_campaign,
        "channel_distribution": channel_dist,
    }
