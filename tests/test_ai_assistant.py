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


def test_ai_legitimate_revenue_queries_still_work(assistant):
    variations = [
        "What is our net revenue?",
        "Show me total profit and margin",
        "What are our business KPIs?",
        "What is the average order value?",
    ]
    for q in variations:
        res = assistant.ask(q)
        assert res["intent"] == "EXECUTIVE_KPIS", f"Failed for query: {q}"
        assert res["sql_query"] is not None
        assert "fact_sales" in res["sql_query"]
        assert res["data"]["total_net_revenue"] > 1_000_000.0


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


def test_ai_unsupported_query_returns_error_and_suggestions(assistant):
    unsupported_queries = [
        "What is the weather in Delhi?",
        "Who is the President of India?",
        "Tell me a joke",
        "xyz123abc",
    ]
    for q in unsupported_queries:
        res = assistant.ask(q)
        assert res["intent"] == "UNSUPPORTED_QUERY", f"Expected UNSUPPORTED_QUERY for '{q}', got {res['intent']}"
        assert res["sql_query"] is None, "Unsupported query should not generate SQL"
        assert res["data"] is None, "Unsupported query should not return revenue/sales data"
        assert "cannot answer" in res["answer"].lower() or "unsupported" in res["answer"].lower()
        assert "sample" in res["insights"].lower() or "supported" in res["insights"].lower()


def test_ai_destructive_operations_blocked(assistant):
    destructive_queries = [
        "DELETE FROM fact_sales",
        "DROP TABLE dim_customers",
        "TRUNCATE table fact_sales",
        "ALTER TABLE fact_sales DROP COLUMN net_amount",
    ]
    for q in destructive_queries:
        res = assistant.ask(q)
        assert res["intent"] == "UNSUPPORTED_QUERY"
        assert res["sql_query"] is None
        assert res["data"] is None
        assert "destructive" in res["answer"].lower() or "not permitted" in res["answer"].lower()


def test_ai_empty_query_rejected(assistant):
    res = assistant.ask("   ")
    assert res["intent"] == "UNSUPPORTED_QUERY"
    assert res["sql_query"] is None
    assert "please ask a question" in res["answer"].lower()


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
    assert data["intent"] == "EXECUTIVE_KPIS"
    assert "sql_query" in data
    assert "answer" in data
    assert "insights" in data


def test_api_ai_ask_unsupported_endpoint(client):
    payload = {"question": "How to make a chocolate cake?"}
    res = client.post("/api/ai/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "UNSUPPORTED_QUERY"
    assert data["sql_query"] is None
    assert data["data"] is None
    assert "cannot answer" in data["answer"].lower()
