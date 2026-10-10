"""
DataPulse - Data Ingestion Module.
Responsible for reading raw data sources into Pandas DataFrames with metadata logging.
"""

from pathlib import Path
from typing import Optional
import pandas as pd


def load_raw_sales_data(filepath: str | Path) -> pd.DataFrame:
    """
    Load raw sales CSV into a Pandas DataFrame and display file metadata.

    Args:
        filepath: Relative or absolute path to the CSV file.

    Returns:
        pd.DataFrame: Raw loaded sales data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found at: {path.resolve()}")

    if path.stat().st_size == 0:
        raise ValueError(f"File is empty: {path.resolve()}")

    df = pd.read_csv(path)

    mem_usage_kb = df.memory_usage(deep=True).sum() / 1024

    print("=" * 60)
    print("DATAPULSE INGESTION REPORT")
    print("=" * 60)
    print(f"File Source     : {path.name}")
    print(f"Total Rows      : {len(df):,}")
    print(f"Total Columns   : {len(df.columns)}")
    print(f"Memory Usage    : {mem_usage_kb:.2f} KB")
    print(f"Columns Detected: {list(df.columns)}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    sample_path = Path("data/raw/sales_data_raw.csv")
    df_raw = load_raw_sales_data(sample_path)
    print("\nSample Preview (First 3 Rows):")
    print(df_raw.head(3).to_string())
