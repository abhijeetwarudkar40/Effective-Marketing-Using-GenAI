"""
Delivery router — calls the REAL _send_email() and _send_sms() from campaign_delivery.py.
Integrates approved creative images from Creative Studio.
"""

import sys
import base64
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Delivery"])

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


class EmailRequest(BaseModel):
    campaign_id: int
    campaign: Dict[str, Any]
    recipient: str
    image_base64: Optional[str] = None


class SmsRequest(BaseModel):
    campaign_id: int
    campaign: Dict[str, Any]
    recipient: str


@router.post("/campaigns/{campaign_id}/send-email")
def send_email(campaign_id: int, req: EmailRequest):
    """
    Calls the REAL _send_email() from ui/campaign_delivery.py.
    Gmail SMTP sending using .env credentials with embedded creative banner.
    """
    try:
        from backend.services.campaign_service import patch_streamlit
        from backend.services.creative_service import get_approved_creative_bytes
        import streamlit as st

        patch_streamlit()

        # Check if an approved creative image is available
        img_bytes = None
        creative_dir = BASE_DIR / "data" / "generated_creatives"
        creative_dir.mkdir(parents=True, exist_ok=True)

        if req.image_base64:
            b64_clean = req.image_base64.split(",", 1)[1] if "," in req.image_base64 else req.image_base64
            img_bytes = base64.b64decode(b64_clean)
            # Persist to disk so subsequent sends also have it
            try:
                (creative_dir / f"campaign_{campaign_id}_creative.png").write_bytes(img_bytes)
                (creative_dir / "latest_creative.png").write_bytes(img_bytes)
            except Exception as fe:
                print(f"Error saving creative to disk: {fe}")
        else:
            img_bytes, _ = get_approved_creative_bytes(str(campaign_id))

        if img_bytes:
            st.session_state["approved_creative"] = img_bytes
        else:
            st.session_state.pop("approved_creative", None)

        from ui.campaign_delivery import _send_email
        status, message = _send_email(req.recipient.strip(), req.campaign, image_bytes=img_bytes)

        import finora_db
        finora_db.log_delivery(campaign_id, "Email", req.recipient.strip(), status, message)

        return {
            "status": status,
            "message": message,
            "image_attached": bool(img_bytes),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/send-sms")
def send_sms(campaign_id: int, req: SmsRequest):
    """
    Calls the REAL _send_sms() from ui/campaign_delivery.py.
    SMS is currently simulated (dry run).
    """
    try:
        from ui.campaign_delivery import _send_sms, _get_generated_sms
        sms_text = _get_generated_sms(req.campaign)
        status, message = _send_sms(req.recipient.strip(), sms_text)

        import finora_db
        finora_db.log_delivery(campaign_id, "SMS", req.recipient.strip(), status, message)

        return {"status": status, "message": message, "sms_text": sms_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/approved-creative")
def get_approved_creative(campaign_id: int):
    """Get the approved banner creative for a campaign."""
    from backend.services.creative_service import get_approved_creative_bytes
    img_bytes, path = get_approved_creative_bytes(str(campaign_id))
    if not img_bytes:
        return {"has_creative": False, "image_base64": None}
    b64 = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
    return {"has_creative": True, "image_base64": b64, "file_path": path}


@router.get("/deliveries")
def get_deliveries():
    """All delivery logs from SQLite."""
    import finora_db
    return {"deliveries": finora_db.deliveries()}
