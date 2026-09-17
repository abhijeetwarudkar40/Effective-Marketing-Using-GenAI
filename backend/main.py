"""
BankWise AI — FastAPI Backend
Bridges the existing Python business logic to the new React frontend.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ─── Ensure the project root is on sys.path so existing modules are importable ───
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load .env (GEMINI_API_KEY, GMAIL credentials, etc.)
load_dotenv(ROOT / ".env")

# Initialise the SQLite database (idempotent)
import finora_db  # noqa: E402  (after sys.path is set)

# ─── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(
    title="BankWise AI API",
    description="AI-Powered Banking Marketing Intelligence Platform",
    version="1.0.0",
)

# ─── CORS — allow the Vite dev server (port 5173) and any localhost ───────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
from backend.routers import (  # noqa: E402
    customers,
    segments,
    recommendations,
    campaigns,
    creative,
    compliance,
    approval,
    delivery,
    analytics,
    ab_testing,
)

for r in [
    customers.router,
    segments.router,
    recommendations.router,
    campaigns.router,
    creative.router,
    compliance.router,
    approval.router,
    delivery.router,
    analytics.router,
    ab_testing.router,
]:
    app.include_router(r, prefix="/api")
    app.include_router(r)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "BankWise AI API"}
