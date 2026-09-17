"""
Campaign service — bridge that makes generate_campaign() work without st.session_state.

When called from FastAPI, st.session_state is not available.
This module monkey-patches it with a simple dict before calling the real generator.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# ── Minimal session state shim ────────────────────────────────────────────────

class _FakeSessionState(dict):
    """Behaves like st.session_state for read/write access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def get(self, key, default=None):
        return super().get(key, default)

    def pop(self, key, default=None):
        return super().pop(key, default)


_session = _FakeSessionState()


def patch_streamlit():
    """Replace st.session_state with our shim so campaign_studio.py can run."""
    try:
        import streamlit as st
        st.session_state = _session
    except Exception:
        pass


def generate_campaign_api(
    customer_id: str,
    product: str,
    language: str = "English",
    tone: str = "Professional",
) -> Dict[str, Any]:
    """
    Calls the real generate_campaign() and captures A/B variants.
    Returns: {"primary": {...}, "variant_a": {...}, "variant_b": {...}}
    """
    patch_streamlit()
    _session.clear()

    from ui.campaign_studio import generate_campaign
    primary = generate_campaign(customer_id, product, language, tone)

    # A/B variants were stored in session_state by generate_campaign
    ab = _session.get("gemini_ab_variants") or {}
    variant_a = ab.get("variant_a", {})
    variant_b = ab.get("variant_b", {})

    return {
        "primary": primary or {},
        "variant_a": variant_a,
        "variant_b": variant_b,
    }
