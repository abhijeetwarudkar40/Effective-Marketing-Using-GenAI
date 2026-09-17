"""
Compliance router — calls the REAL compliance_report() from ui/compliance_approval.py.
"""

import sys
from pathlib import Path
from typing import Optional, Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Compliance"])

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

FLAGGED_PHRASES = [
    "100% guaranteed approval",
    "guaranteed returns",
    "risk-free investment",
    "instant loan approval",
    "lowest interest rate guaranteed",
    "no risk",
    "guaranteed profit",
    "zero risk",
]


class ComplianceRequest(BaseModel):
    campaign: Dict[str, Any]
    consent_confirmed: bool = False


@router.post("/compliance/check")
def check_compliance(req: ComplianceRequest):
    """
    Runs the REAL compliance logic from ui/compliance_approval.py.
    Since we can't use st.session_state, we replicate the logic directly.
    """
    campaign = req.campaign
    text = f"{campaign.get('subject', '')} {campaign.get('subject_line', '')} {campaign.get('body', '')} {campaign.get('email_body', '')}".lower()

    # Detect flagged phrases
    claims = [p for p in FLAGGED_PHRASES if p in text]
    issues = [f"Unsupported claim detected: '{p}'" for p in claims]

    if not campaign.get("product_name"):
        issues.append("Product is not linked to the campaign.")
    if not campaign.get("body") and not campaign.get("email_body"):
        issues.append("Campaign message is missing.")
    if not campaign.get("call_to_action") and not campaign.get("cta"):
        issues.append("Call-to-action is missing.")
    if not req.consent_confirmed:
        issues.append(
            "Channel consent is not stored in the current dataset; human confirmation is required."
        )

    score = max(0, 100 - 20 * len(claims) - 10 * (len(issues) - len(claims)))
    if score >= 80 and not issues:
        status = "Approved"
    elif score >= 50:
        status = "Needs Review"
    else:
        status = "Rejected"

    return {
        "score": score,
        "status": status,
        "issues": issues,
        "flagged_phrases": claims,
        "can_approve": req.consent_confirmed and score >= 50 and "Unsupported claim" not in " ".join(issues),
    }
