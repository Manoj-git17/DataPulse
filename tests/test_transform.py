"""
DataPulse - Tests for Data Transformation Engine.
Run with: pytest
"""

import pytest
import pandas as pd
from etl.transform import (
    clean_text_columns,
    impute_missing_values,
    parse_and_enrich_dates,
    engineer_financial_features,
    transform_sales_data,
)


@pytest.fixture
def raw_sample_row():
    return pd.DataFrame([{
        "order_id": "ORD-2024001",
        "order_date": "2024-03-15",
        "customer_id": "CUST-101",
        "customer_name": "  Aarav Sharma  ",
        "customer_email": "",
        "customer_region": " North ",
        "product_id": "PROD-001",
        "product_name": " Headphones ",
        "category": "Electronics",
        "unit_price": 2000.00,
        "quantity": 2,
        "discount_percent": 0.10,
        "total_amount": 3600.00,
        "payment_method": "UPI",
        "order_status": "Delivered",
    }])


def test_clean_text_columns(raw_sample_row):
    df_cleaned = clean_text_columns(raw_sample_row)
    assert df_cleaned.loc[0, "customer_name"] == "Aarav Sharma"
    assert df_cleaned.loc[0, "customer_region"] == "North"
    assert df_cleaned.loc[0, "product_name"] == "Headphones"


def test_impute_missing_email(raw_sample_row):
    df_imputed = impute_missing_values(raw_sample_row)
    assert df_imputed.loc[0, "customer_email"] == "cust-101@placeholder.datapulse.internal"


def test_parse_and_enrich_dates(raw_sample_row):
    df_dated = parse_and_enrich_dates(raw_sample_row)
    assert df_dated.loc[0, "order_year"] == 2024
    assert df_dated.loc[0, "order_month"] == 3
    assert df_dated.loc[0, "order_quarter"] == 1
    assert df_dated.loc[0, "order_day_name"] == "Friday"


def test_engineer_financial_features(raw_sample_row):
    df_finance = engineer_financial_features(raw_sample_row)
    # unit_price = 2000, quantity = 2
    # gross = 4000
    # discount = 4000 * 0.10 = 400
    # net = 3600
    # cogs = 2000 * 0.65 * 2 = 2600
    # profit = 3600 - 2600 = 1000
    assert df_finance.loc[0, "gross_amount"] == 4000.00
    assert df_finance.loc[0, "discount_amount"] == 400.00
    assert df_finance.loc[0, "net_amount"] == 3600.00
    assert df_finance.loc[0, "estimated_cogs"] == 2600.00
    assert df_finance.loc[0, "estimated_profit"] == 1000.00
    assert round(df_finance.loc[0, "profit_margin_pct"], 2) == round((1000.00 / 3600.00) * 100, 2)


def test_full_transform_pipeline(raw_sample_row):
    transformed = transform_sales_data(raw_sample_row)
    assert len(transformed) == 1
    assert transformed.loc[0, "customer_name"] == "Aarav Sharma"
    assert "estimated_profit" in transformed.columns
    assert "order_quarter" in transformed.columns
