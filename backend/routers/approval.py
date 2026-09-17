"""
Approval router — calls finora_db functions to approve / send campaigns for review.
"""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Approval"])

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


class ReviewRequest(BaseModel):
    notes: str = ""


class ApproveRequest(BaseModel):
    compliance_score: Optional[int] = None
    notes: str = "Human-in-the-loop approval granted"


@router.post("/campaigns/{campaign_id}/review")
def send_for_review(campaign_id: int, req: ReviewRequest):
    """Mark a campaign as 'Needs Review' in SQLite."""
    try:
        import finora_db
        finora_db.update_status(campaign_id, "Needs Review")
        finora_db.log_approval(campaign_id, "Sent for Review", req.notes)
        return {"message": "Campaign sent for human review.", "campaign_id": campaign_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/approve")
def approve_campaign(campaign_id: int, req: ApproveRequest):
    """Approve a campaign — mirrors the existing Streamlit compliance & approval page."""
    try:
        import finora_db, sqlite3
        # Update compliance score if provided
        if req.compliance_score is not None:
            c = finora_db.conn()
            c.execute(
                "UPDATE campaigns SET compliance_score=? WHERE id=?",
                (req.compliance_score, campaign_id),
            )
            c.commit()
            c.close()

        finora_db.update_status(campaign_id, "Approved")
        finora_db.log_approval(campaign_id, "Approved", req.notes)
        return {"message": "Campaign approved.", "campaign_id": campaign_id, "status": "Approved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/status")
def get_campaign_status(campaign_id: int):
    """Get a single campaign's status from SQLite."""
    import finora_db
    all_campaigns = finora_db.campaigns()
    campaign = next((c for c in all_campaigns if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"campaign": campaign}
