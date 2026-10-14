"""
DataPulse - FastAPI Analytical Backend.
Exposes RESTful endpoints for business intelligence KPIs, monthly trends,
regional breakdowns, and consolidated dashboard payloads.
Cost: ₹0 (Free, Open-Source ASGI).
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.connection import get_engine, get_database_url
from db.analytics import (
    get_executive_kpis,
    get_monthly_trends,
    get_regional_breakdown,
    get_top_products,
    get_customer_clv,
    get_payment_method_breakdown,
    get_full_analytics_dashboard,
)
from ai.assistant import DataPulseAIAssistant, SAMPLE_QUESTIONS
from backend.auth import router as auth_router, get_current_user


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="DataPulse Analytics API",
    description=(
        "High-performance backend API powering the "
        "DataPulse Intelligent Analytics Platform."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Authentication routes: register, login, me, logout
app.include_router(auth_router)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

def get_cors_configuration() -> Tuple[List[str], bool]:
    """Parse CORS_ORIGINS and configure credentials safely."""
    raw = os.getenv("CORS_ORIGINS", "*").strip()

    origins = (
        ["*"]
        if not raw or raw == "*"
        else [origin.strip() for origin in raw.split(",") if origin.strip()]
    )

    if not origins:
        origins = ["*"]

    allow_credentials = "*" not in origins

    return origins, allow_credentials


cors_origins, allow_creds = get_cors_configuration()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# PUBLIC ENDPOINTS
# These endpoints do not require authentication.
# --------------------------------------------------

@app.get("/", tags=["General"])
def read_root() -> Dict[str, Any]:
    """Welcome endpoint providing platform status and documentation links."""
    return {
        "platform": "DataPulse — Intelligent Data Engineering & Analytics Platform",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_endpoints": [
            "/api/health",
            "/api/dashboard",
            "/api/kpis",
            "/api/trends",
            "/api/regional",
            "/api/products",
            "/api/customers",
            "/api/payment-methods",
            "/api/ai/suggestions",
            "/api/ai/ask",
        ],
    }


@app.get("/api/health", tags=["Monitoring"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint verifying database connectivity."""
    engine = get_engine()

    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        db_status = "connected"

    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": db_status,
            "dialect": engine.dialect.name,
            "url": str(engine.url),
        },
    }


# --------------------------------------------------
# PROTECTED ANALYTICS ENDPOINTS
# A valid access token is required for every endpoint.
# --------------------------------------------------

@app.get(
    "/api/dashboard",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_dashboard() -> Dict[str, Any]:
    """Consolidated payload consumed directly by the React dashboard."""
    try:
        return get_full_analytics_dashboard()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard data: {str(e)}",
        )


@app.get(
    "/api/kpis",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_kpis() -> Dict[str, Any]:
    """Executive summary KPIs."""
    return get_executive_kpis()


@app.get(
    "/api/trends",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_trends() -> List[Dict[str, Any]]:
    """Monthly time-series revenue and cumulative trends."""
    return get_monthly_trends()


@app.get(
    "/api/regional",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_regional() -> List[Dict[str, Any]]:
    """Regional performance breakdown."""
    return get_regional_breakdown()


@app.get(
    "/api/products",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_products(
    limit: int = Query(5, ge=1, le=50),
) -> List[Dict[str, Any]]:
    """Top products ranked by delivered revenue."""
    return get_top_products(limit=limit)


@app.get(
    "/api/customers",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_customers(
    limit: int = Query(10, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """Customer lifetime value rankings."""
    return get_customer_clv(limit=limit)


@app.get(
    "/api/payment-methods",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
def get_payment_methods() -> List[Dict[str, Any]]:
    """Payment method adoption and cancellation metrics."""
    return get_payment_method_breakdown()


# --------------------------------------------------
# PROTECTED AI ASSISTANT ENDPOINTS
# --------------------------------------------------

class AIQueryRequest(BaseModel):
    question: str


@app.get(
    "/api/ai/suggestions",
    tags=["AI Assistant"],
    dependencies=[Depends(get_current_user)],
)
def get_ai_suggestions() -> List[str]:
    """Return pre-built analytical question prompts for the UI."""
    return SAMPLE_QUESTIONS


@app.post(
    "/api/ai/ask",
    tags=["AI Assistant"],
    dependencies=[Depends(get_current_user)],
)
def ask_ai_assistant(payload: AIQueryRequest) -> Dict[str, Any]:
    """
    Process natural-language business queries and return analytical answers.
    """
    assistant = DataPulseAIAssistant()
    return assistant.ask(payload.question)


# --------------------------------------------------
# DEVELOPMENT SERVER
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )