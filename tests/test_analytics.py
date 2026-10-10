"""
DataPulse - Tests for Analytical SQL Queries.
Run with: pytest
"""

import pytest
from db.connection import get_engine
from db.analytics import (
    get_executive_kpis,
    get_monthly_trends,
    get_regional_breakdown,
    get_top_products,
    get_customer_clv,
    get_payment_method_breakdown,
    get_full_analytics_dashboard,
)


@pytest.fixture(scope="module")
def db_engine():
    return get_engine()


def test_executive_kpis(db_engine):
    kpis = get_executive_kpis(db_engine)
    assert kpis["total_orders"] == 148
    assert kpis["delivered_orders"] > 0
    assert kpis["total_net_revenue"] > 1_000_000.0
    assert kpis["total_profit"] > 0.0
    assert kpis["overall_profit_margin_pct"] > 0.0


def test_monthly_trends(db_engine):
    trends = get_monthly_trends(db_engine)
    assert len(trends) > 0
    first = trends[0]
    assert "month" in first
    assert "monthly_revenue" in first
    assert "cumulative_revenue" in first
    # Cumulative revenue should be >= first month's revenue
    assert trends[-1]["cumulative_revenue"] >= first["monthly_revenue"]


def test_regional_breakdown(db_engine):
    regions = get_regional_breakdown(db_engine)
    region_names = {r["customer_region"] for r in regions}
    assert {"North", "South", "East", "West"}.issubset(region_names)

    # Verify descending sort
    revenues = [r["regional_revenue"] for r in regions]
    assert revenues == sorted(revenues, reverse=True)


def test_top_products(db_engine):
    top_3 = get_top_products(db_engine, limit=3)
    assert len(top_3) == 3
    assert top_3[0]["total_revenue"] >= top_3[1]["total_revenue"]


def test_customer_clv(db_engine):
    clv_list = get_customer_clv(db_engine, limit=5)
    assert len(clv_list) == 5
    assert clv_list[0]["customer_rank"] == 1
    assert clv_list[0]["total_spend"] >= clv_list[-1]["total_spend"]


def test_payment_methods(db_engine):
    methods = get_payment_method_breakdown(db_engine)
    assert len(methods) > 0
    total_pct = sum(m["share_of_transactions_pct"] for m in methods)
    # Check that percentages sum close to 100%
    assert 99.0 <= total_pct <= 101.0


def test_full_dashboard_payload(db_engine):
    dashboard = get_full_analytics_dashboard(db_engine)
    required_keys = {"kpis", "monthly_trends", "regional_breakdown", "top_products", "top_customers", "payment_methods"}
    assert required_keys.issubset(dashboard.keys())
