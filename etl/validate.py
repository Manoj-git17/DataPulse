"""
DataPulse - Data Validation Engine.
Performs schema validation, null checks, range constraints, and anomaly detection on sales data.
"""

from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import List, Dict, Any, Set
import pandas as pd

# Allow direct script execution from repository root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


REQUIRED_COLUMNS: Set[str] = {
    "order_id", "order_date", "customer_id", "customer_name", "customer_email",
    "customer_region", "product_id", "product_name", "category", "unit_price",
    "quantity", "discount_percent", "total_amount", "payment_method", "order_status"
}

VALID_STATUSES: Set[str] = {"Delivered", "Shipped", "Processing", "Cancelled", "Returned"}
VALID_PAYMENT_METHODS: Set[str] = {"UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"}


@dataclass
class ValidationIssue:
    row_index: int
    order_id: str
    column: str
    issue_type: str
    description: str
    severity: str = "ERROR"  # "ERROR" = quarantine, "WARNING" = log only


@dataclass
class ValidationResult:
    total_records: int
    valid_records_count: int
    anomalous_records_count: int
    warnings_count: int
    issues: List[ValidationIssue] = field(default_factory=list)
    valid_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    quarantine_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    def print_summary(self) -> None:
        print("\n" + "=" * 60)
        print("DATAPULSE DATA VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Rows Checked : {self.total_records}")
        print(f"Valid Rows Passed  : {self.valid_records_count}")
        print(f"Quarantined Rows   : {self.anomalous_records_count}")
        print(f"Warnings Logged    : {self.warnings_count}")
        print("-" * 60)

        if self.issues:
            print("Detected Issues Breakdown:")
            for issue in self.issues:
                print(f"  [{issue.severity}] Row {issue.row_index} (Order: {issue.order_id}) -> {issue.column}: {issue.description}")
        else:
            print(" All validation checks passed successfully!")
        print("=" * 60)


def validate_sales_schema(df: pd.DataFrame) -> None:
    """Validate that all mandatory columns exist in the DataFrame."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Schema Validation Failed: Missing required columns: {sorted(list(missing))}")


def validate_sales_data(df: pd.DataFrame) -> ValidationResult:
    """
    Run data engineering validation checks on the raw sales DataFrame.
    Identifies schema issues, negative amounts, invalid status codes, and nulls.
    Separates clean records from quarantined anomalies.
    """
    validate_sales_schema(df)

    issues: List[ValidationIssue] = []
    quarantine_indices = set()

    for idx, row in df.iterrows():
        order_id = str(row.get("order_id", f"ROW_{idx}"))

        # 1. Primary key null checks (Critical)
        for key_col in ["order_id", "product_id", "customer_id"]:
            if pd.isna(row.get(key_col)) or str(row.get(key_col)).strip() == "":
                issues.append(ValidationIssue(
                    row_index=idx,
                    order_id=order_id,
                    column=key_col,
                    issue_type="MISSING_PRIMARY_KEY",
                    description=f"Critical key '{key_col}' is null or empty.",
                    severity="ERROR",
                ))
                quarantine_indices.add(idx)

        # 2. Optional field completeness check (Warning)
        if pd.isna(row.get("customer_email")) or str(row.get("customer_email")).strip() == "":
            issues.append(ValidationIssue(
                row_index=idx,
                order_id=order_id,
                column="customer_email",
                issue_type="MISSING_EMAIL",
                description="Customer email is missing (imputed in Phase 3).",
                severity="WARNING",
            ))

        # 3. Numeric constraints (Positive unit price & quantity)
        qty = row.get("quantity")
        if pd.notna(qty):
            try:
                qty_val = float(qty)
                if qty_val <= 0:
                    issues.append(ValidationIssue(
                        row_index=idx,
                        order_id=order_id,
                        column="quantity",
                        issue_type="NON_POSITIVE_QUANTITY",
                        description=f"Quantity must be greater than 0 (Found: {qty_val}).",
                        severity="ERROR",
                    ))
                    quarantine_indices.add(idx)
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    row_index=idx,
                    order_id=order_id,
                    column="quantity",
                    issue_type="INVALID_NUMERIC",
                    description=f"Quantity cannot be parsed as number (Found: {qty}).",
                    severity="ERROR",
                ))
                quarantine_indices.add(idx)

        price = row.get("unit_price")
        if pd.notna(price):
            try:
                price_val = float(price)
                if price_val <= 0:
                    issues.append(ValidationIssue(
                        row_index=idx,
                        order_id=order_id,
                        column="unit_price",
                        issue_type="NON_POSITIVE_PRICE",
                        description=f"Unit price must be positive (Found: {price_val}).",
                        severity="ERROR",
                    ))
                    quarantine_indices.add(idx)
            except (ValueError, TypeError):
                issues.append(ValidationIssue(
                    row_index=idx,
                    order_id=order_id,
                    column="unit_price",
                    issue_type="INVALID_NUMERIC",
                    description=f"Unit price cannot be parsed as number (Found: {price}).",
                    severity="ERROR",
                ))
                quarantine_indices.add(idx)

        # 4. Status and Enum constraints
        status = str(row.get("order_status", "")).strip()
        if status not in VALID_STATUSES:
            issues.append(ValidationIssue(
                row_index=idx,
                order_id=order_id,
                column="order_status",
                issue_type="INVALID_ENUM",
                description=f"Status '{status}' not in allowed set: {sorted(list(VALID_STATUSES))}.",
                severity="ERROR",
            ))
            quarantine_indices.add(idx)

        # 5. Payment method constraint
        payment = str(row.get("payment_method", "")).strip()
        if payment not in VALID_PAYMENT_METHODS:
            issues.append(ValidationIssue(
                row_index=idx,
                order_id=order_id,
                column="payment_method",
                issue_type="INVALID_PAYMENT_METHOD",
                description=f"Payment method '{payment}' not in allowed set.",
                severity="ERROR",
            ))
            quarantine_indices.add(idx)

    # Separate clean dataset from quarantined anomaly dataset
    valid_df = df.drop(index=list(quarantine_indices)).copy().reset_index(drop=True)
    quarantine_df = df.loc[list(quarantine_indices)].copy().reset_index(drop=True)

    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]

    return ValidationResult(
        total_records=len(df),
        valid_records_count=len(valid_df),
        anomalous_records_count=len(quarantine_df),
        warnings_count=len(warnings),
        issues=issues,
        valid_df=valid_df,
        quarantine_df=quarantine_df,
    )


if __name__ == "__main__":
    from etl.ingest import load_raw_sales_data
    raw_df = load_raw_sales_data("data/raw/sales_data_raw.csv")
    result = validate_sales_data(raw_df)
    result.print_summary()
