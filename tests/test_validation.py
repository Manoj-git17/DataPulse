"""
DataPulse - Tests for Data Validation Engine.
Run with: pytest
"""

import pytest
import pandas as pd
from etl.validate import validate_sales_data, validate_sales_schema


@pytest.fixture
def sample_valid_record():
    return {
        "order_id": "ORD-9999",
        "order_date": "2024-03-01",
        "customer_id": "CUST-101",
        "customer_name": "Aarav Sharma",
        "customer_email": "aarav.sharma@example.com",
        "customer_region": "North",
        "product_id": "PROD-001",
        "product_name": "Wireless Headphones",
        "category": "Electronics",
        "unit_price": 2999.00,
        "quantity": 2,
        "discount_percent": 0.10,
        "total_amount": 5398.20,
        "payment_method": "UPI",
        "order_status": "Delivered",
    }


def test_valid_data_passes(sample_valid_record):
    df = pd.DataFrame([sample_valid_record])
    result = validate_sales_data(df)

    assert result.total_records == 1
    assert result.valid_records_count == 1
    assert result.anomalous_records_count == 0
    assert len(result.issues) == 0


def test_missing_required_column_raises():
    df = pd.DataFrame([{"order_id": "ORD-1", "quantity": 1}])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_sales_schema(df)


def test_negative_quantity_is_quarantined(sample_valid_record):
    record = sample_valid_record.copy()
    record["quantity"] = -3
    df = pd.DataFrame([record])

    result = validate_sales_data(df)
    assert result.valid_records_count == 0
    assert result.anomalous_records_count == 1
    assert any(i.issue_type == "NON_POSITIVE_QUANTITY" for i in result.issues)


def test_invalid_order_status_is_quarantined(sample_valid_record):
    record = sample_valid_record.copy()
    record["order_status"] = "FLYING_TO_MARS"
    df = pd.DataFrame([record])

    result = validate_sales_data(df)
    assert result.valid_records_count == 0
    assert result.anomalous_records_count == 1
    assert any(i.issue_type == "INVALID_ENUM" for i in result.issues)


def test_missing_email_generates_warning_only(sample_valid_record):
    record = sample_valid_record.copy()
    record["customer_email"] = ""
    df = pd.DataFrame([record])

    result = validate_sales_data(df)
    # Email is non-critical for transaction validity, so row is kept in valid_df
    assert result.valid_records_count == 1
    assert result.anomalous_records_count == 0
    assert result.warnings_count == 1
