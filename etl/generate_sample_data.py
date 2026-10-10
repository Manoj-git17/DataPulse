"""
DataPulse - Synthetic Sales Data Generator.
Generates realistic retail sales transactions for development, testing, and validation.
Cost: ₹0 (Pure Python standard library / Random).
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Fix seed for reproducible development data
random.seed(42)

REGIONS = ["North", "South", "East", "West"]
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
ORDER_STATUSES = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"]

PRODUCTS = [
    ("PROD-001", "Noise-Cancelling Wireless Headphones", "Electronics", 2999.00),
    ("PROD-002", "Ergonomic Mechanical Keyboard", "Electronics", 4500.00),
    ("PROD-003", "Ultra-HD 4K Monitor 27-inch", "Electronics", 18500.00),
    ("PROD-004", "Stainless Steel Water Bottle 1L", "Home & Kitchen", 650.00),
    ("PROD-005", "Ergonomic Mesh Office Chair", "Furniture", 8900.00),
    ("PROD-006", "Adjustable Standing Desk Converter", "Furniture", 11200.00),
    ("PROD-007", "Organic Arabica Coffee Beans 500g", "Groceries", 750.00),
    ("PROD-008", "High-Speed USB-C Hub 7-in-1", "Electronics", 1899.00),
    ("PROD-009", "Yoga & Workout Fitness Mat", "Fitness", 1200.00),
    ("PROD-010", "Smart LED Desk Lamp with Dimmer", "Home & Kitchen", 1499.00),
]

CUSTOMERS = [
    ("CUST-101", "Aarav Sharma", "aarav.sharma@example.com", "North"),
    ("CUST-102", "Diya Patel", "diya.patel@example.com", "West"),
    ("CUST-103", "Rohan Iyer", "rohan.iyer@example.com", "South"),
    ("CUST-104", "Ananya Chatterjee", "ananya.c@example.com", "East"),
    ("CUST-105", "Vikram Malhotra", "vikram.m@example.com", "North"),
    ("CUST-106", "Pooja Hegde", "pooja.h@example.com", "South"),
    ("CUST-107", "Kabir Mehta", "kabir.mehta@example.com", "West"),
    ("CUST-108", "Sneha Rao", "sneha.rao@example.com", "South"),
    ("CUST-109", "Arjun Sen", "arjun.sen@example.com", "East"),
    ("CUST-110", "Priya Verma", "priya.v@example.com", "North"),
]


def generate_sales_data(output_path: Path, num_records: int = 150) -> Path:
    """Generate sample sales CSV with realistic records and controlled edge cases."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start_date = datetime(2024, 1, 1)

    records = []

    for i in range(1, num_records + 1):
        order_id = f"ORD-{2024000 + i}"
        days_offset = random.randint(0, 180)
        order_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")

        cust_id, cust_name, cust_email, cust_region = random.choice(CUSTOMERS)
        prod_id, prod_name, category, unit_price = random.choice(PRODUCTS)

        quantity = random.choices([1, 2, 3, 4, 5, 8], weights=[40, 30, 15, 8, 5, 2])[0]
        discount = random.choice([0.0, 0.05, 0.10, 0.15, 0.20])
        total_amount = round(unit_price * quantity * (1.0 - discount), 2)
        payment_method = random.choice(PAYMENT_METHODS)
        status = random.choices(ORDER_STATUSES, weights=[65, 15, 10, 6, 4])[0]

        records.append({
            "order_id": order_id,
            "order_date": order_date,
            "customer_id": cust_id,
            "customer_name": cust_name,
            "customer_email": cust_email,
            "customer_region": cust_region,
            "product_id": prod_id,
            "product_name": prod_name,
            "category": category,
            "unit_price": unit_price,
            "quantity": quantity,
            "discount_percent": discount,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "order_status": status,
        })

    # Intentionally inject 3 controlled anomalies to test data validation rules
    # 1. Missing customer email
    records[12]["customer_email"] = ""
    # 2. Negative quantity anomaly
    records[45]["quantity"] = -2
    records[45]["total_amount"] = -5998.00
    # 3. Invalid order status
    records[78]["order_status"] = "UNKNOWN_STATE"

    fieldnames = [
        "order_id", "order_date", "customer_id", "customer_name", "customer_email",
        "customer_region", "product_id", "product_name", "category", "unit_price",
        "quantity", "discount_percent", "total_amount", "payment_method", "order_status"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} sales records at: {output_path}")
    return output_path


if __name__ == "__main__":
    dataset_file = Path("data/raw/sales_data_raw.csv")
    generate_sales_data(dataset_file)
