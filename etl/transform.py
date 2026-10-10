"""
DataPulse - Data Transformation Module (ETL 'T' Layer).
Applies data cleansing, missing value imputation, type casting,
and financial feature engineering on validated sales data.
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.ingest import load_raw_sales_data
from etl.validate import validate_sales_data


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and standardize text columns."""
    df = df.copy()
    text_cols = ["customer_name", "customer_region", "product_name", "category", "payment_method", "order_status"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute non-critical missing values with standard fallbacks.
    - Missing email is imputed with a synthetic address based on customer_id.
    - Missing region falls back to 'Unknown'.
    """
    df = df.copy()

    # Impute missing email
    missing_email_mask = df["customer_email"].isna() | (df["customer_email"].astype(str).str.strip() == "")
    df.loc[missing_email_mask, "customer_email"] = (
        df.loc[missing_email_mask, "customer_id"].str.lower() + "@placeholder.datapulse.internal"
    )

    # Impute region fallback if any
    if "customer_region" in df.columns:
        df["customer_region"] = df["customer_region"].fillna("Unknown")

    return df


def parse_and_enrich_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse order_date into ISO datetime and extract analytical calendar dimensions.
    """
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Calendar dimensions for temporal SQL queries and dashboard filters
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_month_name"] = df["order_date"].dt.strftime("%B")
    df["order_quarter"] = df["order_date"].dt.quarter
    df["order_day_name"] = df["order_date"].dt.day_name()

    return df


def engineer_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer core revenue and profitability metrics:
    - gross_amount = unit_price * quantity
    - discount_amount = gross_amount * discount_percent
    - net_amount = gross_amount - discount_amount
    - estimated_cogs = unit_price * 0.65 * quantity (standard 65% cost of goods sold model)
    - estimated_profit = net_amount - estimated_cogs
    - profit_margin_pct = (estimated_profit / net_amount) * 100
    """
    df = df.copy()

    df["gross_amount"] = (df["unit_price"] * df["quantity"]).round(2)
    df["discount_amount"] = (df["gross_amount"] * df["discount_percent"]).round(2)
    df["net_amount"] = (df["gross_amount"] - df["discount_amount"]).round(2)

    # Cost of Goods Sold (COGS) model: 65% base production/procurement cost
    df["estimated_cogs"] = (df["unit_price"] * 0.65 * df["quantity"]).round(2)
    df["estimated_profit"] = (df["net_amount"] - df["estimated_cogs"]).round(2)

    # Margin percentage safe division
    df["profit_margin_pct"] = np.where(
        df["net_amount"] > 0,
        ((df["estimated_profit"] / df["net_amount"]) * 100).round(2),
        0.0
    )

    return df


def transform_sales_data(valid_df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete end-to-end transformation pipeline for validated records.
    """
    df = clean_text_columns(valid_df)
    df = impute_missing_values(df)
    df = parse_and_enrich_dates(df)
    df = engineer_financial_features(df)
    return df


def run_etl_pipeline(
    raw_path: str | Path = "data/raw/sales_data_raw.csv",
    processed_dir: str | Path = "data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Runs the full Phase 2 & 3 pipeline:
    Load -> Validate -> Transform -> Export clean and quarantine CSVs.
    """
    raw_df = load_raw_sales_data(raw_path)
    val_result = validate_sales_data(raw_df)
    val_result.print_summary()

    transformed_df = transform_sales_data(val_result.valid_df)

    out_dir = Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    clean_file = out_dir / "sales_clean.csv"
    quarantine_file = out_dir / "sales_quarantine.csv"

    transformed_df.to_csv(clean_file, index=False)
    val_result.quarantine_df.to_csv(quarantine_file, index=False)

    total_revenue = transformed_df["net_amount"].sum()
    total_profit = transformed_df["estimated_profit"].sum()
    avg_order_value = transformed_df["net_amount"].mean()

    print("\n" + "=" * 60)
    print("DATAPULSE TRANSFORMATION SUMMARY")
    print("=" * 60)
    print(f"Clean Records Exported      : {len(transformed_df)} -> {clean_file.name}")
    print(f"Quarantined Records Exported: {len(val_result.quarantine_df)} -> {quarantine_file.name}")
    print(f"Total Gross Revenue         : INR {transformed_df['gross_amount'].sum():,.2f}")
    print(f"Total Net Revenue           : INR {total_revenue:,.2f}")
    print(f"Total Estimated Profit      : INR {total_profit:,.2f}")
    print(f"Average Order Value (AOV)   : INR {avg_order_value:,.2f}")
    print(f"Enriched Features Added     : ['order_year', 'order_month', 'order_quarter',")
    print(f"                               'gross_amount', 'discount_amount', 'net_amount',")
    print(f"                               'estimated_cogs', 'estimated_profit', 'profit_margin_pct']")
    print("=" * 60)

    return transformed_df, val_result.quarantine_df


if __name__ == "__main__":
    run_etl_pipeline()
