"""
DataPulse - Tests for AI Conversational Data Assistant.
Run with: pytest
"""

import pytest
from fastapi.testclient import TestClient
from ai.assistant import DataPulseAIAssistant, SAMPLE_QUESTIONS
from backend.main import app


@pytest.fixture(scope="module")
def assistant():
    return DataPulseAIAssistant()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_ai_revenue_intent(assistant):
    res = assistant.ask("What is our total revenue and profit?")
    assert res["intent"] == "EXECUTIVE_KPIS"
    assert "SELECT" in res["sql_query"]
    assert "revenue" in res["answer"].lower()
    assert res["data"]["total_orders"] == 148


def test_ai_top_products_intent(assistant):
    res = assistant.ask("Show me top 3 products")
    assert res["intent"] == "TOP_PRODUCTS"
    assert "LIMIT 3" in res["sql_query"]
    assert len(res["data"]) == 3


def test_ai_regional_intent(assistant):
    res = assistant.ask("Which region has the highest sales?")
    assert res["intent"] == "REGIONAL_PERFORMANCE"
    assert "South" in res["answer"]


def test_ai_customer_intent(assistant):
    res = assistant.ask("Who are our top customers?")
    assert res["intent"] == "CUSTOMER_CLV"
    assert "orders" in res["answer"]


def test_ai_payment_intent(assistant):
    res = assistant.ask("What is our most popular payment method?")
    assert res["intent"] == "PAYMENT_METHOD"
    assert "UPI" in res["answer"]


def test_api_ai_suggestions(client):
    res = client.get("/api/ai/suggestions")
    assert res.status_code == 200
    suggestions = res.json()
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0


def test_api_ai_ask_endpoint(client):
    payload = {"question": "What is our total revenue?"}
    res = client.post("/api/ai/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "sql_query" in data
    assert "answer" in data
    assert "insights" in data
