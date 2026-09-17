"""
Campaigns router.

POST /api/campaigns/generate  — calls the REAL generate_campaign() from campaign_studio.py
GET  /api/campaigns            — all campaigns from SQLite
GET  /api/campaigns/context    — campaign context data for the UI dropdowns
PUT  /api/campaigns/{id}       — edit/update a campaign
"""

import sys
from pathlib import Path
from typing import Optional, Any, Dict

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Campaigns"])

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
PROCESSED = BASE_DIR / "data" / "processed"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_context() -> pd.DataFrame:
    path = PROCESSED / "campaign_context.csv"
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


def _load_campaign_content() -> pd.DataFrame:
    path = PROCESSED / "campaign_content.csv"
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


def _load_recs() -> pd.DataFrame:
    path = PROCESSED / "customer_recommendations.csv"
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


def _load_product_catalog() -> list:
    cat_path = BASE_DIR / "data" / "raw" / "products.csv"
    prods = []
    if cat_path.exists():
        try:
            pdf = pd.read_csv(cat_path)
            if "product_name" in pdf.columns:
                prods = pdf["product_name"].dropna().astype(str).tolist()
        except Exception:
            pass
    if not prods:
        prods = [
            "Personal Loan", "Premium Banking", "Term Insurance",
            "Rewards Credit Card", "Mutual Fund Plan", "Home Loan",
            "Savings Account", "Recurring Deposit", "Fixed Deposit"
        ]
    return prods


# ── Request/Response Models ────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    customer_id: str
    product: str
    language: str = "English"
    tone: str = "Professional"


class UpdateCampaignRequest(BaseModel):
    subject: Optional[str] = None
    headline: Optional[str] = None
    email_body: Optional[str] = None
    cta: Optional[str] = None
    sms: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/campaigns/context")
def get_campaign_context(customer_id: Optional[str] = None, product: Optional[str] = None):
    """Return customer list and MULTIPLE recommended products with rich per-product context."""
    df = _load_context()
    recs_df = _load_recs()
    catalog = _load_product_catalog()

    customers = []
    if not df.empty and "customer_id" in df.columns:
        customers = sorted(df["customer_id"].dropna().astype(str).str.strip().unique().tolist())
    elif not recs_df.empty and "customer_id" in recs_df.columns:
        customers = sorted(recs_df["customer_id"].dropna().astype(str).str.strip().unique().tolist())

    if customer_id:
        cid = str(customer_id).strip()
        cust_recs = pd.DataFrame()
        if not recs_df.empty and "customer_id" in recs_df.columns:
            cust_recs = recs_df[recs_df["customer_id"].astype(str).str.strip() == cid]

        cust_ctx_rows = pd.DataFrame()
        if not df.empty and "customer_id" in df.columns:
            cust_ctx_rows = df[df["customer_id"].astype(str).str.strip() == cid]

        # Collect recommended products first (sorted by rank/score)
        rec_products = []
        context_by_product = {}

        if not cust_recs.empty:
            for _, r in cust_recs.iterrows():
                pname = str(r.get("product_name", "")).strip()
                if pname and pname not in rec_products:
                    rec_products.append(pname)
                    context_by_product[pname] = {
                        "customer_id": cid,
                        "product_name": pname,
                        "primary_segment": r.get("primary_segment", "Active Customer"),
                        "customer_persona": r.get("customer_persona", "Customer"),
                        "retention_risk": r.get("retention_risk", "Low Risk"),
                        "cross_sell_opportunity": r.get("cross_sell_opportunity", "Moderate Opportunity"),
                        "recommendation_reason": r.get("recommendation_reason", "Affinity match based on profile"),
                        "recommendation_score": r.get("recommendation_score", 0.7),
                        "recommendation_confidence": r.get("recommendation_confidence", "High"),
                        "campaign_objective": r.get("campaign_objective", "Cross-Sell"),
                    }

        if not cust_ctx_rows.empty:
            for _, r in cust_ctx_rows.iterrows():
                pname = str(r.get("product_name", "")).strip()
                if pname and pname not in rec_products:
                    rec_products.append(pname)
                if pname and pname not in context_by_product:
                    context_by_product[pname] = r.fillna("").to_dict()

        # Combine: Recommended products first, then remaining catalog items
        all_products = list(rec_products)
        for cat_item in catalog:
            if cat_item not in all_products:
                all_products.append(cat_item)

        # Active selected context
        selected_prod = product or (all_products[0] if all_products else "Personal Loan")
        active_ctx = context_by_product.get(selected_prod)
        if not active_ctx:
            # Fallback to base customer context with this product
            base = cust_ctx_rows.iloc[0].fillna("").to_dict() if not cust_ctx_rows.empty else (
                cust_recs.iloc[0].fillna("").to_dict() if not cust_recs.empty else {}
            )
            active_ctx = dict(base)
            active_ctx["product_name"] = selected_prod

        return {
            "customers": customers,
            "products": all_products,
            "recommended_products": rec_products,
            "context_by_product": context_by_product,
            "context": active_ctx,
        }

    # All products globally
    all_global_products = list(dict.fromkeys(catalog + (df["product_name"].dropna().astype(str).tolist() if "product_name" in df.columns else [])))
    return {"customers": customers, "products": all_global_products}


@router.post("/campaigns/generate")
def generate_campaign_endpoint(req: GenerateRequest):
    """
    Calls the REAL generate_campaign() via the backend service shim.
    Returns primary campaign + A/B variants from a single Gemini call.
    """
    try:
        from backend.services.campaign_service import generate_campaign_api
        result = generate_campaign_api(
            customer_id=req.customer_id,
            product=req.product,
            language=req.language,
            tone=req.tone,
        )

        primary = result.get("primary") or {}
        if not primary:
            raise HTTPException(status_code=500, detail="Campaign generation returned empty result")

        # Save to SQLite
        import finora_db
        campaign_id = finora_db.save_campaign(primary, status="Generated")
        primary["campaign_id"] = campaign_id

        return {
            "campaign": primary,
            "campaign_id": campaign_id,
            "variant_a": result.get("variant_a", {}),
            "variant_b": result.get("variant_b", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/campaigns")
def get_campaigns():
    """All campaigns from SQLite."""
    import finora_db
    return {"campaigns": finora_db.campaigns()}


@router.get("/campaigns/ab-variants/{customer_id}")
def get_ab_variants(customer_id: str):
    """Get A/B variants from the processed CSV for a customer."""
    path = PROCESSED / "campaign_ab_variants.csv"
    if not path.exists():
        return {"variant_a": None, "variant_b": None}
    try:
        df = pd.read_csv(path)
        rows = df[df["customer_id"].astype(str) == customer_id]
        if rows.empty:
            return {"variant_a": None, "variant_b": None}
        row = rows.iloc[0].fillna("").to_dict()
        # Reconstruct variant dicts from flattened columns
        variant_a = {k.replace("variant_a_", ""): v for k, v in row.items() if k.startswith("variant_a_")}
        variant_b = {k.replace("variant_b_", ""): v for k, v in row.items() if k.startswith("variant_b_")}
        return {"variant_a": variant_a, "variant_b": variant_b}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, req: UpdateCampaignRequest):
    """Update campaign fields (edit in the React UI)."""
    import finora_db, sqlite3
    try:
        c = finora_db.conn()
        updates: list = []
        values: list = []
        if req.subject is not None:
            updates.append("subject=?")
            values.append(req.subject)
        if req.email_body is not None:
            updates.append("body=?")
            values.append(req.email_body)
        if not updates:
            return {"message": "No fields to update"}
        values.append(campaign_id)
        c.execute(f"UPDATE campaigns SET {', '.join(updates)} WHERE id=?", values)
        c.commit()
        c.close()
        return {"message": "Campaign updated", "campaign_id": campaign_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
