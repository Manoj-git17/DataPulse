"""
DataPulse - Relational Database Models.

Defines:
- dim_customers: Customer dimension table
- dim_products: Product dimension table
- fact_sales: Sales fact table
- users: Application user accounts

Compatible with PostgreSQL and SQLite via SQLAlchemy.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class CustomerDimension(Base):
    """
    Customer Dimension Table (dim_customers).
    Stores unique attributes of buyers.
    """

    __tablename__ = "dim_customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    customer_email = Column(String(200), nullable=True)
    customer_region = Column(String(50), nullable=False, index=True)

    sales = relationship(
        "SalesFact",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<CustomerDimension "
            f"id={self.customer_id} name={self.customer_name}>"
        )


class ProductDimension(Base):
    """
    Product Dimension Table (dim_products).
    Stores catalog and pricing attributes of items sold.
    """

    __tablename__ = "dim_products"

    product_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)

    sales = relationship(
        "SalesFact",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ProductDimension "
            f"id={self.product_id} name={self.product_name}>"
        )


class SalesFact(Base):
    """
    Sales Fact Table (fact_sales).
    Stores transactional records joined to customer and product dimensions.
    """

    __tablename__ = "fact_sales"

    order_id = Column(String(50), primary_key=True, index=True)
    order_date = Column(DateTime, nullable=False, index=True)

    customer_id = Column(
        String(50),
        ForeignKey("dim_customers.customer_id"),
        nullable=False,
        index=True,
    )

    product_id = Column(
        String(50),
        ForeignKey("dim_products.product_id"),
        nullable=False,
        index=True,
    )

    # Quantities and financial attributes
    quantity = Column(Integer, nullable=False)
    discount_percent = Column(Float, default=0.0)
    gross_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    estimated_cogs = Column(Float, nullable=False)
    estimated_profit = Column(Float, nullable=False)
    profit_margin_pct = Column(Float, default=0.0)

    # Transaction attributes
    payment_method = Column(String(50), nullable=False)
    order_status = Column(String(50), nullable=False, index=True)

    customer = relationship(
        "CustomerDimension",
        back_populates="sales",
    )

    product = relationship(
        "ProductDimension",
        back_populates="sales",
    )

    def __repr__(self) -> str:
        return (
            f"<SalesFact "
            f"order={self.order_id} net_amount={self.net_amount}>"
        )


# Composite indexes for analytical queries
Index(
    "idx_sales_date_customer",
    SalesFact.order_date,
    SalesFact.customer_id,
)

Index(
    "idx_sales_status_profit",
    SalesFact.order_status,
    SalesFact.estimated_profit,
)


class User(Base):
    """
    Application user accounts for DataPulse authentication.

    Passwords must be stored as secure password hashes,
    never as plain text.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name = Column(String(100), nullable=False)

    hashed_password = Column(String(255), nullable=False)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"