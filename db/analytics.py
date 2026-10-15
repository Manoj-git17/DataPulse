"""
DataPulse - Analytical Query Engine.
Executes business intelligence SQL queries across PostgreSQL and SQLite.
Provides structured metrics for CLI reporting, FastAPI, and React dashboards.
"""

from decimal import Decimal
from pathlib import Path
import sys
from typing import Dict, List, Any
from sqlalchemy import text, Engine

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.connection import get_engine


def is_postgres(engine: Engine) -> bool:
    """Detect whether connected engine is PostgreSQL."""
    return engine.dialect.name == "postgresql"


def _clean_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Decimal values to float for unified cross-database JSON serialization."""
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


def get_executive_kpis(engine: Engine | None = None) -> Dict[str, Any]:
    """Calculate core high-level KPIs across all transactions."""
    eng = engine or get_engine()
    sql = text("""
        SELECT 
            COUNT(order_id) AS total_orders,
            SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
            ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS total_net_revenue,
            ROUND(CAST(SUM(estimated_profit) AS NUMERIC), 2) AS total_profit,
            ROUND(CAST(AVG(net_amount) AS NUMERIC), 2) AS average_order_value,
            ROUND(CAST((SUM(estimated_profit) / NULLIF(SUM(net_amount), 0)) * 100 AS NUMERIC), 2) AS overall_profit_margin_pct
        FROM fact_sales
    """)
    with eng.connect() as conn:
        row = conn.execute(sql).mappings().fetchone()
        return _clean_row(dict(row)) if row else {}


def get_monthly_trends(engine: Engine | None = None) -> List[Dict[str, Any]]:
    """Monthly revenue and order trend with cumulative revenue."""
    eng = engine or get_engine()
    # Support both SQLite and PostgreSQL date formatting
    date_expr = "TO_CHAR(order_date, 'YYYY-MM')" if is_postgres(eng) else "strftime('%Y-%m', order_date)"

    sql = text(f"""
        SELECT 
            {date_expr} AS month,
            COUNT(order_id) AS orders_count,
            ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS monthly_revenue,
            ROUND(CAST(SUM(estimated_profit) AS NUMERIC), 2) AS monthly_profit,
            ROUND(CAST(SUM(SUM(net_amount)) OVER (ORDER BY {date_expr}) AS NUMERIC), 2) AS cumulative_revenue
        FROM fact_sales
        WHERE order_status != 'Cancelled'
        GROUP BY {date_expr}
        ORDER BY month ASC
    """)
    with eng.connect() as conn:
        return [_clean_row(dict(row)) for row in conn.execute(sql).mappings().fetchall()]


def get_regional_breakdown(engine: Engine | None = None) -> List[Dict[str, Any]]:
    """Regional revenue, profit, and margin performance."""
    eng = engine or get_engine()
    sql = text("""
        SELECT 
            c.customer_region,
            COUNT(s.order_id) AS order_count,
            ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS regional_revenue,
            ROUND(CAST(SUM(s.estimated_profit) AS NUMERIC), 2) AS regional_profit,
            ROUND(CAST(AVG(s.net_amount) AS NUMERIC), 2) AS avg_order_value,
            ROUND(CAST((SUM(s.estimated_profit) / NULLIF(SUM(s.net_amount), 0)) * 100 AS NUMERIC), 2) AS profit_margin_pct
        FROM fact_sales s
        JOIN dim_customers c ON s.customer_id = c.customer_id
        WHERE s.order_status = 'Delivered'
        GROUP BY c.customer_region
        ORDER BY regional_revenue DESC
    """)
    with eng.connect() as conn:
        return [_clean_row(dict(row)) for row in conn.execute(sql).mappings().fetchall()]


def get_top_products(engine: Engine | None = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Top products ranked by net delivered revenue."""
    eng = engine or get_engine()
    sql = text(f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            SUM(s.quantity) AS units_sold,
            ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_revenue,
            ROUND(CAST(SUM(s.estimated_profit) AS NUMERIC), 2) AS total_profit,
            ROUND(CAST((SUM(s.estimated_profit) / NULLIF(SUM(s.net_amount), 0)) * 100 AS NUMERIC), 2) AS profit_margin_pct
        FROM fact_sales s
        JOIN dim_products p ON s.product_id = p.product_id
        WHERE s.order_status = 'Delivered'
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT {limit}
    """)
    with eng.connect() as conn:
        return [_clean_row(dict(row)) for row in conn.execute(sql).mappings().fetchall()]


def get_customer_clv(engine: Engine | None = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Customer lifetime spend and frequency."""
    eng = engine or get_engine()
    sql = text(f"""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.customer_region,
            COUNT(s.order_id) AS total_orders,
            ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_spend,
            ROUND(CAST(AVG(s.net_amount) AS NUMERIC), 2) AS avg_spend_per_order,
            RANK() OVER (ORDER BY SUM(s.net_amount) DESC) AS customer_rank
        FROM fact_sales s
        JOIN dim_customers c ON s.customer_id = c.customer_id
        WHERE s.order_status != 'Cancelled'
        GROUP BY c.customer_id, c.customer_name, c.customer_region
        ORDER BY customer_rank ASC
        LIMIT {limit}
    """)
    with eng.connect() as conn:
        return [_clean_row(dict(row)) for row in conn.execute(sql).mappings().fetchall()]


def get_payment_method_breakdown(engine: Engine | None = None) -> List[Dict[str, Any]]:
    """Payment method adoption and cancellation metrics."""
    eng = engine or get_engine()
    sql = text("""
        SELECT 
            payment_method,
            COUNT(order_id) AS total_transactions,
            ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS total_revenue,
            ROUND(CAST((COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_sales)) AS NUMERIC), 2) AS share_of_transactions_pct,
            ROUND(CAST((SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(order_id)) AS NUMERIC), 2) AS cancellation_rate_pct
        FROM fact_sales
        GROUP BY payment_method
        ORDER BY total_transactions DESC
    """)
    with eng.connect() as conn:
        return [_clean_row(dict(row)) for row in conn.execute(sql).mappings().fetchall()]


def get_full_analytics_dashboard(engine: Engine | None = None) -> Dict[str, Any]:
    """Aggregate all analytical queries into a consolidated payload."""
    eng = engine or get_engine()
    return {
        "kpis": get_executive_kpis(eng),
        "monthly_trends": get_monthly_trends(eng),
        "regional_breakdown": get_regional_breakdown(eng),
        "top_products": get_top_products(eng, limit=5),
        "top_customers": get_customer_clv(eng, limit=5),
        "payment_methods": get_payment_method_breakdown(eng),
    }


def print_cli_report(engine: Engine | None = None) -> None:
    """Print an executive analytics briefing to the terminal."""
    data = get_full_analytics_dashboard(engine)
    kpis = data["kpis"]

    print("=" * 65)
    print("DATAPULSE EXECUTIVE ANALYTICS REPORT")
    print("=" * 65)
    print(f"Total Transactions : {kpis['total_orders']}")
    print(f"Delivered Orders   : {kpis['delivered_orders']}")
    print(f"Total Net Revenue  : INR {kpis['total_net_revenue']:,.2f}")
    print(f"Total Net Profit   : INR {kpis['total_profit']:,.2f}")
    print(f"Average Order Value: INR {kpis['average_order_value']:,.2f}")
    print(f"Profit Margin      : {kpis['overall_profit_margin_pct']:.2f}%")
    print("-" * 65)

    print("Regional Revenue Leaders:")
    for reg in data["regional_breakdown"]:
        print(f"  * {reg['customer_region']:<8} : INR {reg['regional_revenue']:>10,.2f} | Profit: INR {reg['regional_profit']:>9,.2f} ({reg['profit_margin_pct']}%)")

    print("-" * 65)
    print("Top 3 Products by Delivered Revenue:")
    for idx, prod in enumerate(data["top_products"][:3], 1):
        print(f"  {idx}. {prod['product_name']:<35} | INR {prod['total_revenue']:>10,.2f} ({prod['units_sold']} units)")
    print("=" * 65)


if __name__ == "__main__":
    print_cli_report()
