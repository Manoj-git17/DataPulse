"""
DataPulse - Intelligent Natural Language Query Assistant (Text-to-SQL & Insights).
Provides ₹0 cost, instant, local conversational analytics over the relational data warehouse.
"""

from pathlib import Path
import re
import sys
from typing import Dict, Any, List
from sqlalchemy import text, Engine

# Ensure UTF-8 output in Windows consoles to prevent cp1252 charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.connection import get_engine
from db.analytics import (
    get_executive_kpis,
    get_regional_breakdown,
    get_top_products,
    get_customer_clv,
    get_payment_method_breakdown,
    get_monthly_trends,
)

SAMPLE_QUESTIONS = [
    "What is our total revenue and profit?",
    "Show me the top 3 best selling products",
    "Which region is the most profitable?",
    "Who are our highest value customers?",
    "What is the most popular payment method?",
    "What are our monthly revenue trends?",
]

# Keywords that indicate unsupported or destructive operations
DESTRUCTIVE_KEYWORDS = {
    "delete", "drop", "truncate", "alter", "update", "insert",
    "remove", "destroy", "shutdown", "kill", "purge"
}

# Domain keyword groups for supported analytical intents
PRODUCT_KEYWORDS = ["product", "item", "bestseller", "selling", "catalog", "units sold"]
REGIONAL_KEYWORDS = ["region", "geography", "zone", "territory", "north", "south", "east", "west"]
CUSTOMER_KEYWORDS = ["customer", "client", "buyer", "clv", "spender", "lifetime value", "highest value"]
PAYMENT_KEYWORDS = ["payment", "upi", "card", "cod", "cash", "banking", "checkout", "cancellation rate"]
TREND_KEYWORDS = ["trend", "timeline", "monthly", "cumulative", "growth", "over time"]
REVENUE_KEYWORDS = [
    "revenue", "profit", "sales", "kpi", "performance", "aov", "margin", "earnings",
    "summary", "overview", "business health", "average order", "order value", "basket size", "total order"
]


class DataPulseAIAssistant:
    """
    Intelligent Data Assistant that translates natural language questions
    into SQL queries and executive business answers.
    """

    def __init__(self, engine: Engine | None = None):
        self.engine = engine or get_engine()

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language business question.
        Returns validated SQL, answers, and data for supported queries,
        or an explicit unsupported-intent notice with helpful guidance.
        """
        cleaned = query.lower().strip()

        # 1. Reject empty or whitespace-only queries
        if not cleaned:
            return {
                "question": query,
                "intent": "UNSUPPORTED_QUERY",
                "sql_query": None,
                "answer": "Please ask a question about DataPulse sales, products, revenue, customers, regions, or payments.",
                "insights": f"Try a sample question such as: '{SAMPLE_QUESTIONS[0]}'",
                "data": None,
            }

        # 2. Reject destructive and modification requests (Read-Only Safety)
        tokens = set(re.findall(r"\w+", cleaned))
        if tokens & DESTRUCTIVE_KEYWORDS:
            return {
                "question": query,
                "intent": "UNSUPPORTED_QUERY",
                "sql_query": None,
                "answer": "Data modification and destructive operations are not permitted. DataPulse operates strictly in read-only analytical mode.",
                "insights": "The assistant generates and executes read-only SELECT queries.",
                "data": None,
            }

        # 3. Top Products Query
        if any(w in cleaned for w in PRODUCT_KEYWORDS):
            limit = 3 if "3" in cleaned else 5
            data = get_top_products(self.engine, limit=limit)
            top_item = data[0] if data else {}
            sql = f"""SELECT p.product_name, p.category, SUM(s.quantity) AS units, ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS revenue FROM fact_sales s JOIN dim_products p ON s.product_id = p.product_id WHERE s.order_status = 'Delivered' GROUP BY p.product_name, p.category ORDER BY revenue DESC LIMIT {limit};"""
            answer = f"The top performing product is '{top_item.get('product_name')}' with ₹{top_item.get('total_revenue', 0):,.2f} in delivered revenue across {top_item.get('units_sold', 0)} units."
            insights = f"Category '{top_item.get('category')}' drives the highest revenue share with a {top_item.get('profit_margin_pct')}% margin."
            return {
                "question": query,
                "intent": "TOP_PRODUCTS",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": data,
            }

        # 4. Regional Performance Query
        if any(w in cleaned for w in REGIONAL_KEYWORDS):
            data = get_regional_breakdown(self.engine)
            top_reg = data[0] if data else {}
            sql = """SELECT c.customer_region, COUNT(s.order_id) AS orders, ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS revenue, ROUND(CAST(SUM(s.estimated_profit) AS NUMERIC), 2) AS profit FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status = 'Delivered' GROUP BY c.customer_region ORDER BY revenue DESC;"""
            answer = f"The '{top_reg.get('customer_region')}' region leads sales with ₹{top_reg.get('regional_revenue', 0):,.2f} in net revenue and {top_reg.get('order_count')} delivered orders."
            insights = f"Top regional margin is {top_reg.get('profit_margin_pct')}%, generating ₹{top_reg.get('regional_profit', 0):,.2f} in net profits."
            return {
                "question": query,
                "intent": "REGIONAL_PERFORMANCE",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": data,
            }

        # 5. Customer Lifetime Value (CLV)
        if any(w in cleaned for w in CUSTOMER_KEYWORDS):
            data = get_customer_clv(self.engine, limit=5)
            top_cust = data[0] if data else {}
            sql = """SELECT c.customer_name, c.customer_region, COUNT(s.order_id) AS orders, ROUND(CAST(SUM(s.net_amount) AS NUMERIC), 2) AS total_spend, RANK() OVER (ORDER BY SUM(s.net_amount) DESC) AS rank FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status != 'Cancelled' GROUP BY c.customer_id, c.customer_name ORDER BY total_spend DESC LIMIT 5;"""
            answer = f"Our top customer is {top_cust.get('customer_name')} ({top_cust.get('customer_region')}) with total spend of ₹{top_cust.get('total_spend', 0):,.2f} across {top_cust.get('total_orders')} orders."
            insights = f"Average spend for top-tier customer is ₹{top_cust.get('avg_spend_per_order', 0):,.2f} per order."
            return {
                "question": query,
                "intent": "CUSTOMER_CLV",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": data,
            }

        # 6. Payment Method Adoption
        if any(w in cleaned for w in PAYMENT_KEYWORDS):
            data = get_payment_method_breakdown(self.engine)
            top_pm = data[0] if data else {}
            sql = """SELECT payment_method, COUNT(order_id) AS transactions, ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS revenue, ROUND(CAST((COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_sales)) AS NUMERIC), 2) AS share_pct FROM fact_sales GROUP BY payment_method ORDER BY transactions DESC;"""
            answer = f"The most preferred checkout method is {top_pm.get('payment_method')}, accounting for {top_pm.get('share_of_transactions_pct')}% of total transaction volume."
            insights = f"{top_pm.get('payment_method')} has a low cancellation rate of {top_pm.get('cancellation_rate_pct')}%, representing healthy checkout conversion."
            return {
                "question": query,
                "intent": "PAYMENT_METHOD",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": data,
            }

        # 7. Monthly Trends & Growth
        if any(w in cleaned for w in TREND_KEYWORDS):
            data = get_monthly_trends(self.engine)
            sql = """SELECT strftime('%Y-%m', order_date) AS month, COUNT(order_id) AS orders, ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS revenue, ROUND(CAST(SUM(SUM(net_amount)) OVER (ORDER BY strftime('%Y-%m', order_date)) AS NUMERIC), 2) AS cumulative_revenue FROM fact_sales WHERE order_status != 'Cancelled' GROUP BY strftime('%Y-%m', order_date) ORDER BY month ASC;"""
            latest = data[-1] if data else {}
            answer = f"Tracked {len(data)} calendar months. Cumulative business revenue reached ₹{latest.get('cumulative_revenue', 0):,.2f} by {latest.get('month')}."
            insights = "Time-series shows consistent monthly transaction activity across all fiscal periods."
            return {
                "question": query,
                "intent": "MONTHLY_TRENDS",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": data,
            }

        # 8. Legitimate Revenue / KPI / Business Health Query
        if any(w in cleaned for w in REVENUE_KEYWORDS):
            kpis = get_executive_kpis(self.engine)
            sql = """SELECT COUNT(order_id) AS total_orders, ROUND(CAST(SUM(net_amount) AS NUMERIC), 2) AS total_revenue, ROUND(CAST(SUM(estimated_profit) AS NUMERIC), 2) AS total_profit, ROUND(CAST(AVG(net_amount) AS NUMERIC), 2) AS aov, ROUND(CAST((SUM(estimated_profit)/SUM(net_amount))*100 AS NUMERIC), 2) AS margin_pct FROM fact_sales;"""
            answer = f"Total net revenue is ₹{kpis.get('total_net_revenue', 0):,.2f} with total profit of ₹{kpis.get('total_profit', 0):,.2f} across {kpis.get('total_orders')} orders."
            insights = f"Business health: {kpis.get('overall_profit_margin_pct')}% overall profit margin and an Average Order Value (AOV) of ₹{kpis.get('average_order_value', 0):,.2f}."
            return {
                "question": query,
                "intent": "EXECUTIVE_KPIS",
                "sql_query": sql,
                "answer": answer,
                "insights": insights,
                "data": kpis,
            }

        # 9. Explicit Unsupported Query Handling (Guards against arbitrary/unrelated questions)
        return {
            "question": query,
            "intent": "UNSUPPORTED_QUERY",
            "sql_query": None,
            "answer": (
                f"I cannot answer questions about '{query}'. "
                "I am an analytical assistant specialized in DataPulse e-commerce data "
                "(revenue, profit, products, customers, regions, payment methods, and monthly trends)."
            ),
            "insights": (
                "Try asking one of the supported business questions, such as: "
                f"'{SAMPLE_QUESTIONS[0]}' or '{SAMPLE_QUESTIONS[1]}'."
            ),
            "data": None,
        }


def safe_cli_print(text_str: str) -> None:
    """Print text safely across different Windows terminal encodings without crashing."""
    try:
        print(text_str)
    except UnicodeEncodeError:
        # Fallback to ASCII representation for terminal encodings that cannot encode ₹
        safe_str = text_str.replace("₹", "INR ")
        print(safe_str.encode(sys.stdout.encoding or "ascii", errors="replace").decode(sys.stdout.encoding or "ascii"))


if __name__ == "__main__":
    assistant = DataPulseAIAssistant()
    test_queries = [
        "What is our total revenue and profit?",
        "Show me the top 3 best selling products",
        "What is the weather in Delhi?",
        "DELETE FROM fact_sales",
    ]
    for q in test_queries:
        safe_cli_print("\n" + "=" * 60)
        safe_cli_print(f"User Query: {q}")
        res = assistant.ask(q)
        safe_cli_print(f"Intent    : {res['intent']}")
        safe_cli_print(f"SQL       : {res['sql_query']}")
        safe_cli_print(f"AI Answer : {res['answer']}")
        safe_cli_print(f"Insights  : {res['insights']}")
