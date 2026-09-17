"""
Creative Studio router — generates 3 marketing banner designs & handles banner approval.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.creative_service import generate_banners_api, approve_banner_api

router = APIRouter(tags=["Creative Studio"])


class GenerateCreativeRequest(BaseModel):
    customer_id: Optional[str] = "C000001"
    primary_segment: Optional[str] = "Premium High-Value"
    product_name: Optional[str] = "Personal Loan"
    campaign_objective: Optional[str] = "Engagement"
    headline: Optional[str] = "Explore Tailored Banking Solutions"
    email_body: Optional[str] = ""
    cta: Optional[str] = "Explore Now"
    option: Optional[int] = None


class ApproveCreativeRequest(BaseModel):
    campaign_id: str
    option: int
    image_base64: str
    metadata: Dict[str, Any]


@router.post("/creative/generate")
@router.get("/creative/generate")
def generate_creatives(
    req: Optional[GenerateCreativeRequest] = None,
    customer_id: Optional[str] = "C000001",
    primary_segment: Optional[str] = "Premium High-Value",
    product_name: Optional[str] = "Personal Loan",
    campaign_objective: Optional[str] = "Cross-Sell",
    headline: Optional[str] = "Discover Tailored Banking Solutions",
    cta: Optional[str] = "Explore Now",
    option: Optional[int] = None,
):
    """Generate 3 unique marketing banners (or single option) based on campaign context."""
    try:
        if req:
            ctx = req.model_dump()
            opt = req.option
        else:
            ctx = {
                "customer_id": customer_id,
                "primary_segment": primary_segment,
                "product_name": product_name,
                "campaign_objective": campaign_objective,
                "headline": headline,
                "cta": cta,
            }
            opt = option

        banners = generate_banners_api(ctx, option=opt)
        return {"banners": banners}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/creative/approve")
def approve_creative(req: ApproveCreativeRequest):
    """Approve a selected creative banner and persist it for email embedding."""
    try:
        result = approve_banner_api(req.campaign_id, {
            "option": req.option,
            "image_base64": req.image_base64,
            "metadata": req.metadata,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
