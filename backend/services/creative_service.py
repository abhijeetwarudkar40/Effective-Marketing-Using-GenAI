"""
Creative Studio service — generates 3 local PIL marketing banners based on campaign context.
"""

import io
import base64
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image

BASE_DIR = Path(__file__).resolve().parents[2]
CREATIVE_DIR = BASE_DIR / "data" / "generated_creatives"
CREATIVE_DIR.mkdir(parents=True, exist_ok=True)

# In-memory store for currently approved creative by campaign ID
_approved_creatives: Dict[str, Dict[str, Any]] = {}


def generate_banners_api(ctx: Dict[str, Any], option: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Generates 3 unique banner designs using ui.creative_studio.create_banner.
    If option is specified (1, 2, or 3), generates only that option.
    Returns list of options with base64 encoded PNG data and metadata.
    """
    from ui.creative_studio import create_banner

    normalized_ctx = {
        "customer_id": str(ctx.get("customer_id") or "C000001").strip(),
        "segment": str(ctx.get("primary_segment") or ctx.get("segment") or "Premium High-Value").strip(),
        "product": str(ctx.get("product_name") or ctx.get("product") or "Personal Loan").strip(),
        "objective": str(ctx.get("campaign_objective") or ctx.get("objective") or "Cross-Sell").strip(),
        "headline": str(ctx.get("headline") or ctx.get("subject") or "Discover Tailored Banking Solutions").strip(),
        "body": str(ctx.get("email_body") or ctx.get("body") or "").strip(),
        "cta": str(ctx.get("cta") or ctx.get("call_to_action") or "Explore Now").strip(),
    }

    target_options = [option] if option in (1, 2, 3) else [1, 2, 3]

    results = []
    for opt in target_options:
        image, metadata = create_banner(normalized_ctx, opt)

        # Save to buffer and convert to base64
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        img_bytes = buf.getvalue()
        b64_str = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

        results.append({
            "option": opt,
            "image_base64": b64_str,
            "metadata": metadata,
        })

    return results


def approve_banner_api(campaign_id: str, option_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves approved creative to disk and in memory for campaign delivery.
    """
    image_b64 = option_data.get("image_base64", "")
    metadata = option_data.get("metadata", {})
    creative_id = metadata.get("creative_id", f"CR-{campaign_id}")

    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]

    img_bytes = base64.b64decode(image_b64)
    file_path = CREATIVE_DIR / f"campaign_{campaign_id}_creative.png"
    file_path.write_bytes(img_bytes)

    # Also save by creative_id
    alt_path = CREATIVE_DIR / f"{creative_id}.png"
    alt_path.write_bytes(img_bytes)

    # Store in memory cache
    _approved_creatives[str(campaign_id)] = {
        "creative_id": creative_id,
        "campaign_id": campaign_id,
        "file_path": str(file_path),
        "image_bytes": img_bytes,
        "metadata": metadata,
    }

    # Update SQLite database
    try:
        import finora_db
        c = finora_db.conn()
        c.execute("""
            INSERT INTO creative_assets (campaign_id, creative_id, option_no, path, sha256, approval_status, created_at)
            VALUES (?, ?, ?, ?, ?, 'APPROVED', datetime('now'))
        """, (
            campaign_id,
            creative_id,
            option_data.get("option", 1),
            str(file_path),
            metadata.get("sha256", ""),
        ))
        c.commit()
        c.close()
    except Exception as e:
        print(f"Error logging creative asset: {e}")

    return {
        "status": "APPROVED",
        "creative_id": creative_id,
        "campaign_id": campaign_id,
        "file_path": str(file_path),
        "metadata": metadata,
    }


def get_approved_creative_bytes(campaign_id: str) -> Tuple[bytes, str]:
    """
    Retrieves approved image bytes for a campaign to attach in email.
    """
    cached = _approved_creatives.get(str(campaign_id))
    if cached and cached.get("image_bytes"):
        return cached["image_bytes"], cached.get("file_path", "")

    # Check file on disk
    file_path = CREATIVE_DIR / f"campaign_{campaign_id}_creative.png"
    if file_path.exists():
        img_bytes = file_path.read_bytes()
        return img_bytes, str(file_path)

    # Check any creative file
    files = list(CREATIVE_DIR.glob("*.png"))
    if files:
        latest = max(files, key=lambda f: f.stat().st_mtime)
        return latest.read_bytes(), str(latest)

    return None, ""
