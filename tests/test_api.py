"""
DataPulse - Tests for FastAPI Backend.
Uses FastAPI TestClient for end-to-end HTTP endpoint validation.
Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app, get_cors_configuration


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "DataPulse" in data["platform"]
    assert data["status"] == "online"
    assert "/docs" in data["docs_url"]


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "connected"


def test_get_kpis(client, auth_headers):
    response = client.get("/api/kpis", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 148
    assert data["total_net_revenue"] > 1_000_000.0


def test_get_trends(client, auth_headers):
    response = client.get("/api/trends", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_regional(client, auth_headers):
    response = client.get("/api/regional", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_get_products_with_limit(client, auth_headers):
    response = client.get("/api/products?limit=3", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_dashboard_payload(client, auth_headers):
    response = client.get("/api/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "monthly_trends" in data
    assert "regional_breakdown" in data
    assert "top_products" in data
    assert "payment_methods" in data


def test_analytics_endpoints_require_auth(client):
    """Verify that unauthenticated requests to protected endpoints return 401."""
    endpoints = [
        "/api/kpis",
        "/api/trends",
        "/api/regional",
        "/api/products?limit=3",
        "/api/dashboard",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
        assert response.json()["detail"] == "Authentication required or session expired."


def test_cors_configuration_defaults(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    origins, allow_creds = get_cors_configuration()
    assert origins == ["*"]
    assert allow_creds is False


def test_cors_configuration_explicit_origins(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://datapulse.vercel.app, http://localhost:5173")
    origins, allow_creds = get_cors_configuration()
    assert origins == ["https://datapulse.vercel.app", "http://localhost:5173"]
    assert allow_creds is True


def test_cors_options_preflight(client):
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/dashboard", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_cors_configuration_empty_values(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " , , ")
    origins, allow_creds = get_cors_configuration()

    assert origins == ["*"]
    assert allow_creds is False
