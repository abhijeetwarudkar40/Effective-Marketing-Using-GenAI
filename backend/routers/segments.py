"""
Segments router — reads from existing customer_segments.csv.
"""

from pathlib import Path
import pandas as pd
from fastapi import APIRouter

router = APIRouter(tags=["Segments"])

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED = BASE_DIR / "data" / "processed"


def _load_segments() -> pd.DataFrame:
    for name in ("customer_segments.csv", "segments.csv"):
        path = PROCESSED / name
        if path.exists():
            try:
                return pd.read_csv(path)
            except Exception:
                pass
    return pd.DataFrame()


@router.get("/segments")
def get_segments():
    df = _load_segments()
    if df.empty:
        return {"segments": [], "total_customers": 0}

    seg_col = "primary_segment" if "primary_segment" in df.columns else "segment"
    if seg_col not in df.columns:
        return {"segments": [], "total_customers": 0}

    total = len(df)
    counts = df[seg_col].value_counts()

    segments = []
    for seg_name, count in counts.items():
        pct = round(count / total * 100, 1)
        # Gather characteristic columns if available
        seg_df = df[df[seg_col] == seg_name]
        top_persona = ""
        top_risk = ""
        top_product = ""
        if "customer_persona" in df.columns:
            vc = seg_df["customer_persona"].value_counts()
            top_persona = vc.index[0] if not vc.empty else ""
        if "retention_risk" in df.columns:
            vc = seg_df["retention_risk"].value_counts()
            top_risk = vc.index[0] if not vc.empty else ""

        segments.append({
            "segment": seg_name,
            "count": int(count),
            "percentage": pct,
            "top_persona": str(top_persona),
            "top_retention_risk": str(top_risk),
            "top_product": str(top_product),
        })

    # Persona distribution
    persona_dist = []
    if "customer_persona" in df.columns:
        for p, c in df["customer_persona"].value_counts().items():
            persona_dist.append({"persona": str(p), "count": int(c)})

    # Retention risk distribution
    risk_dist = []
    if "retention_risk" in df.columns:
        for r, c in df["retention_risk"].value_counts().items():
            risk_dist.append({"risk": str(r), "count": int(c)})

    # Targeting priority distribution
    priority_dist = []
    if "genai_targeting_priority" in df.columns:
        for r, c in df["genai_targeting_priority"].value_counts().items():
            priority_dist.append({"priority": str(r), "count": int(c)})

    return {
        "segments": segments,
        "total_customers": total,
        "persona_distribution": persona_dist,
        "risk_distribution": risk_dist,
        "priority_distribution": priority_dist,
    }
