"""
DataPulse - Relational Database Models (Star Schema).
Defines dimension tables (dim_customers, dim_products) and the central fact table (fact_sales).
Compatible with PostgreSQL and SQLite via SQLAlchemy.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CustomerDimension(Base):
    """
    Customer Dimension Table (dim_customers)
    Stores unique attributes of buyers.
    """
    __tablename__ = "dim_customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    customer_email = Column(String(200), nullable=True)
    customer_region = Column(String(50), nullable=False, index=True)

    # Relationships
    sales = relationship("SalesFact", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CustomerDimension id={self.customer_id} name={self.customer_name}>"


class ProductDimension(Base):
    """
    Product Dimension Table (dim_products)
    Stores catalog and pricing attributes of items sold.
    """
    __tablename__ = "dim_products"

    product_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)

    # Relationships
    sales = relationship("SalesFact", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProductDimension id={self.product_id} name={self.product_name}>"


class SalesFact(Base):
    """
    Sales Fact Table (fact_sales)
    Stores transactional event records, joined to customer and product dimensions.
    """
    __tablename__ = "fact_sales"

    order_id = Column(String(50), primary_key=True, index=True)
    order_date = Column(DateTime, nullable=False, index=True)
    customer_id = Column(String(50), ForeignKey("dim_customers.customer_id"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("dim_products.product_id"), nullable=False, index=True)

    # Quantities and financials
    quantity = Column(Integer, nullable=False)
    discount_percent = Column(Float, default=0.0)
    gross_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    estimated_cogs = Column(Float, nullable=False)
    estimated_profit = Column(Float, nullable=False)
    profit_margin_pct = Column(Float, default=0.0)

    # Dimensional attributes on fact
    payment_method = Column(String(50), nullable=False)
    order_status = Column(String(50), nullable=False, index=True)

    # Relationships
    customer = relationship("CustomerDimension", back_populates="sales")
    product = relationship("ProductDimension", back_populates="sales")

    def __repr__(self) -> str:
        return f"<SalesFact order={self.order_id} net_amount={self.net_amount}>"


# Composite indexes for high-performance analytical queries
Index("idx_sales_date_customer", SalesFact.order_date, SalesFact.customer_id)
Index("idx_sales_status_profit", SalesFact.order_status, SalesFact.estimated_profit)
