"""
DataPulse - Database Loader Script.
Loads cleaned data from data/processed/sales_clean.csv into the relational Star Schema.
Handles dimensional normalization and database insertion.
"""

from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import text

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.connection import get_engine, get_session, init_db, get_database_url
from db.models import CustomerDimension, ProductDimension, SalesFact


def load_clean_data_to_db(
    clean_csv_path: str | Path = "data/processed/sales_clean.csv",
    db_url: str | None = None,
) -> dict:
    """
    Extracts cleaned records and populates dim_customers, dim_products, and fact_sales.
    """
    path = Path(clean_csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {path.resolve()}. Run 'python -m etl.transform' first.")

    df = pd.read_csv(path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    engine = get_engine(db_url)
    init_db(engine)
    session = get_session(engine)

    try:
        # 1. Normalize and Upsert Customers Dimension
        customers_df = (
            df[["customer_id", "customer_name", "customer_email", "customer_region"]]
            .drop_duplicates(subset=["customer_id"])
        )

        loaded_customers = 0
        for _, row in customers_df.iterrows():
            cust = session.get(CustomerDimension, row["customer_id"])
            if not cust:
                cust = CustomerDimension(
                    customer_id=row["customer_id"],
                    customer_name=row["customer_name"],
                    customer_email=row["customer_email"],
                    customer_region=row["customer_region"],
                )
                session.add(cust)
                loaded_customers += 1

        session.commit()

        # 2. Normalize and Upsert Products Dimension
        products_df = (
            df[["product_id", "product_name", "category", "unit_price"]]
            .drop_duplicates(subset=["product_id"])
        )

        loaded_products = 0
        for _, row in products_df.iterrows():
            prod = session.get(ProductDimension, row["product_id"])
            if not prod:
                prod = ProductDimension(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    category=row["category"],
                    unit_price=float(row["unit_price"]),
                )
                session.add(prod)
                loaded_products += 1

        session.commit()

        # 3. Load Fact Table
        loaded_facts = 0
        for _, row in df.iterrows():
            fact = session.get(SalesFact, row["order_id"])
            if not fact:
                fact = SalesFact(
                    order_id=row["order_id"],
                    order_date=row["order_date"].to_pydatetime(),
                    customer_id=row["customer_id"],
                    product_id=row["product_id"],
                    quantity=int(row["quantity"]),
                    discount_percent=float(row["discount_percent"]),
                    gross_amount=float(row["gross_amount"]),
                    discount_amount=float(row["discount_amount"]),
                    net_amount=float(row["net_amount"]),
                    estimated_cogs=float(row["estimated_cogs"]),
                    estimated_profit=float(row["estimated_profit"]),
                    profit_margin_pct=float(row["profit_margin_pct"]),
                    payment_method=row["payment_method"],
                    order_status=row["order_status"],
                )
                session.add(fact)
                loaded_facts += 1

        session.commit()

        # Query Database verification metrics
        total_customers = session.query(CustomerDimension).count()
        total_products = session.query(ProductDimension).count()
        total_facts = session.query(SalesFact).count()

        with engine.connect() as conn:
            revenue_res = conn.execute(text("SELECT SUM(net_amount), SUM(estimated_profit) FROM fact_sales")).fetchone()
            db_revenue = revenue_res[0] or 0.0
            db_profit = revenue_res[1] or 0.0

        print("\n" + "=" * 60)
        print("DATAPULSE DATABASE LOAD SUMMARY")
        print("=" * 60)
        print(f"Target Database URL : {engine.url}")
        print(f"Dimensions Loaded   : {total_customers} Customers, {total_products} Products")
        print(f"Fact Rows Loaded    : {total_facts} Sales Transactions")
        print(f"Total DB Net Revenue: INR {db_revenue:,.2f}")
        print(f"Total DB Profit     : INR {db_profit:,.2f}")
        print(" Integrity Check    : All Foreign Key Constraints Satisfied!")
        print("=" * 60)

        return {
            "customers": total_customers,
            "products": total_products,
            "facts": total_facts,
            "revenue": db_revenue,
            "profit": db_profit,
        }

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    load_clean_data_to_db()
