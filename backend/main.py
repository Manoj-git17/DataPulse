"""
DataPulse - FastAPI Analytical Backend.
Exposes RESTful endpoints for business intelligence KPIs, monthly trends,
regional breakdowns, and consolidated dashboard payloads.
Cost: ₹0 (Free, Open-Source ASGI).
"""

from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(
    title="DataPulse Analytics API",
    description="High-performance backend API powering the DataPulse Intelligent Analytics Platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for React frontend (Vite default: http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
def read_root() -> Dict[str, Any]:
    """Welcome endpoint providing platform status and interactive documentation links."""
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
        ],
    }


@app.get("/api/health", tags=["Monitoring"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint verifying database connectivity."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text_query := __import__("sqlalchemy").text("SELECT 1"))
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


@app.get("/api/dashboard", tags=["Analytics"])
def get_dashboard() -> Dict[str, Any]:
    """Consolidated payload consumed directly by the React dashboard."""
    try:
        return get_full_analytics_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")


@app.get("/api/kpis", tags=["Analytics"])
def get_kpis() -> Dict[str, Any]:
    """Executive summary KPIs (orders, revenue, profit, average order value)."""
    return get_executive_kpis()


@app.get("/api/trends", tags=["Analytics"])
def get_trends() -> List[Dict[str, Any]]:
    """Monthly time-series revenue and cumulative trends."""
    return get_monthly_trends()


@app.get("/api/regional", tags=["Analytics"])
def get_regional() -> List[Dict[str, Any]]:
    """Regional performance breakdown."""
    return get_regional_breakdown()


@app.get("/api/products", tags=["Analytics"])
def get_products(limit: int = Query(5, ge=1, le=50)) -> List[Dict[str, Any]]:
    """Top products ranked by delivered revenue."""
    return get_top_products(limit=limit)


@app.get("/api/customers", tags=["Analytics"])
def get_customers(limit: int = Query(10, ge=1, le=100)) -> List[Dict[str, Any]]:
    """Customer lifetime value (CLV) rankings."""
    return get_customer_clv(limit=limit)


@app.get("/api/payment-methods", tags=["Analytics"])
def get_payment_methods() -> List[Dict[str, Any]]:
    """Payment method adoption and cancellation metrics."""
    return get_payment_method_breakdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
