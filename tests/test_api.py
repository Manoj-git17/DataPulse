"""
DataPulse - Tests for FastAPI Backend.
Uses FastAPI TestClient for end-to-end HTTP endpoint validation.
Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


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


def test_get_kpis(client):
    response = client.get("/api/kpis")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 148
    assert data["total_net_revenue"] > 1_000_000.0


def test_get_trends(client):
    response = client.get("/api/trends")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_regional(client):
    response = client.get("/api/regional")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_get_products_with_limit(client):
    response = client.get("/api/products?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_dashboard_payload(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "monthly_trends" in data
    assert "regional_breakdown" in data
    assert "top_products" in data
    assert "payment_methods" in data
