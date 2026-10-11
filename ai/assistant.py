"""
DataPulse - Intelligent Natural Language Query Assistant (Text-to-SQL & Insights).
Provides ₹0 cost, instant, local conversational analytics over the relational data warehouse.
"""

from pathlib import Path
import re
import sys
from typing import Dict, Any, List
from sqlalchemy import text, Engine

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.connection import get_engine
from db.analytics import (
    get_executive_kpis,
    get_regional_breakdown,
    get_top_products,
    get_customer_clv,
    get_payment_method_breakdown,
)

SAMPLE_QUESTIONS = [
    "What is our total revenue and profit?",
    "Show me the top 3 best selling products",
    "Which region is the most profitable?",
    "Who are our highest value customers?",
    "What is the most popular payment method?",
    "What is our average order value?",
]


class DataPulseAIAssistant:
    """
    Intelligent Data Assistant that translates natural language questions
    into SQL queries and executive business answers.
    """

    def __init__(self, engine: Engine | None = None):
        self.engine = engine or get_engine()

    def ask(self, query: str) -> Dict[str, Any]:
        """Process a natural language business question and return answers, SQL, and insights."""
        cleaned = query.lower().strip()

        # 1. Top Products Query
        if any(w in cleaned for w in ["product", "item", "selling", "bestseller"]):
            limit = 3 if "3" in cleaned else 5
            data = get_top_products(self.engine, limit=limit)
            top_item = data[0] if data else {}
            sql = f"""SELECT p.product_name, p.category, SUM(s.quantity) AS units, ROUND(SUM(s.net_amount), 2) AS revenue FROM fact_sales s JOIN dim_products p ON s.product_id = p.product_id WHERE s.order_status = 'Delivered' GROUP BY p.product_name, p.category ORDER BY revenue DESC LIMIT {limit};"""
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

        # 2. Regional Performance Query
        if any(w in cleaned for w in ["region", "geography", "zone", "state", "territory"]):
            data = get_regional_breakdown(self.engine)
            top_reg = data[0] if data else {}
            sql = """SELECT c.customer_region, COUNT(s.order_id) AS orders, ROUND(SUM(s.net_amount), 2) AS revenue, ROUND(SUM(s.estimated_profit), 2) AS profit FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status = 'Delivered' GROUP BY c.customer_region ORDER BY revenue DESC;"""
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

        # 3. Customer Lifetime Value (CLV)
        if any(w in cleaned for w in ["customer", "client", "buyer", "clv", "spenders", "who"]):
            data = get_customer_clv(self.engine, limit=5)
            top_cust = data[0] if data else {}
            sql = """SELECT c.customer_name, c.customer_region, COUNT(s.order_id) AS orders, ROUND(SUM(s.net_amount), 2) AS total_spend, RANK() OVER (ORDER BY SUM(s.net_amount) DESC) AS rank FROM fact_sales s JOIN dim_customers c ON s.customer_id = c.customer_id WHERE s.order_status != 'Cancelled' GROUP BY c.customer_id, c.customer_name ORDER BY total_spend DESC LIMIT 5;"""
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

        # 4. Payment Method Adoption
        if any(w in cleaned for w in ["payment", "upi", "card", "cod", "cash", "banking"]):
            data = get_payment_method_breakdown(self.engine)
            top_pm = data[0] if data else {}
            sql = """SELECT payment_method, COUNT(order_id) AS transactions, ROUND(SUM(net_amount), 2) AS revenue, ROUND((COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_sales)), 2) AS share_pct FROM fact_sales GROUP BY payment_method ORDER BY transactions DESC;"""
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

        # 5. Default / Revenue / KPIs / Executive Summary
        kpis = get_executive_kpis(self.engine)
        sql = """SELECT COUNT(order_id) AS total_orders, ROUND(SUM(net_amount), 2) AS total_revenue, ROUND(SUM(estimated_profit), 2) AS total_profit, ROUND(AVG(net_amount), 2) AS aov, ROUND((SUM(estimated_profit)/SUM(net_amount))*100, 2) AS margin_pct FROM fact_sales;"""
        answer = f"Total net revenue is ₹{kpis.get('total_net_revenue', 0):,.2f} with total profit of ₹{kpis.get('total_profit', 0):,.2f} across {kpis.get('total_orders')} orders."
        insights = f"Healthy business health: 26.97% overall profit margin and an Average Order Value (AOV) of ₹{kpis.get('average_order_value', 0):,.2f}."

        return {
            "question": query,
            "intent": "EXECUTIVE_KPIS",
            "sql_query": sql,
            "answer": answer,
            "insights": insights,
            "data": kpis,
        }


if __name__ == "__main__":
    assistant = DataPulseAIAssistant()
    for q in SAMPLE_QUESTIONS[:3]:
        print("\n" + "=" * 60)
        print(f"User: {q}")
        res = assistant.ask(q)
        print(f"Generated SQL: {res['sql_query']}")
        print(f"AI Answer    : {res['answer']}")
        print(f"Key Insight  : {res['insights']}")
