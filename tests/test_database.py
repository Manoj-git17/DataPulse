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
from db.connection import normalize_database_url, get_database_url


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


def test_normalize_database_url_legacy_postgres():
    legacy_url = "postgres://user:pass@neon.tech:5432/datapulse?sslmode=require"
    normalized = normalize_database_url(legacy_url)
    assert normalized == "postgresql://user:pass@neon.tech:5432/datapulse?sslmode=require"


def test_normalize_database_url_preserves_valid_urls():
    pg_url = "postgresql://user:pass@localhost:5432/datapulse"
    assert normalize_database_url(pg_url) == pg_url

    sqlite_url = "sqlite:///data/datapulse.db"
    assert normalize_database_url(sqlite_url) == sqlite_url


def test_get_database_url_normalizes_env_legacy_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://neon_user:neon_pass@ep-cool.neon.tech/neondb")
    url = get_database_url()
    assert url == "postgresql://neon_user:neon_pass@ep-cool.neon.tech/neondb"


def test_postgresql_url_parsing_offline():
    """Verify that PostgreSQL URLs parse accurately offline without requiring a paid service."""
    from sqlalchemy.engine import make_url

    parsed = make_url(normalize_database_url("postgres://app_user:secret_pwd@db.neon.tech:5432/datapulse_prod"))
    assert parsed.drivername == "postgresql"
    assert parsed.username == "app_user"
    assert parsed.password == "secret_pwd"
    assert parsed.host == "db.neon.tech"
    assert parsed.port == 5432
    assert parsed.database == "datapulse_prod"
