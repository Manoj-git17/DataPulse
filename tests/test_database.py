"""
DataPulse - Tests for Database Layer & Models.
Uses in-memory SQLite database for zero-overhead, ultra-fast test execution.
Run with: pytest
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, CustomerDimension, ProductDimension, SalesFact
from db.load_data import load_clean_data_to_db


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session, engine
    session.close()


def test_models_creation(memory_db):
    session, engine = memory_db

    # Add a sample customer
    customer = CustomerDimension(
        customer_id="CUST-TEST",
        customer_name="Test Customer",
        customer_email="test@example.com",
        customer_region="North",
    )
    # Add a sample product
    product = ProductDimension(
        product_id="PROD-TEST",
        product_name="Test Widget",
        category="Testing",
        unit_price=100.0,
    )
    session.add(customer)
    session.add(product)
    session.commit()

    # Query back
    saved_cust = session.get(CustomerDimension, "CUST-TEST")
    saved_prod = session.get(ProductDimension, "PROD-TEST")

    assert saved_cust is not None
    assert saved_cust.customer_name == "Test Customer"
    assert saved_prod is not None
    assert saved_prod.unit_price == 100.0


def test_load_clean_data_pipeline(tmp_path):
    test_db_file = tmp_path / "test_datapulse.db"
    test_db_url = f"sqlite:///{test_db_file.resolve()}"

    stats = load_clean_data_to_db(clean_csv_path="data/processed/sales_clean.csv", db_url=test_db_url)

    assert stats["customers"] == 10
    assert stats["products"] == 10
    assert stats["facts"] == 148
    assert stats["revenue"] > 0
