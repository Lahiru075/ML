"""
Data Ingestion Module for CropForecastLK
Reads raw Excel census records, validates schema, and profiles data health.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
from ml_pipeline.config import RAW_DATA_PATH

EXPECTED_COLUMNS = [
    "District",
    "Season",
    "CropCategory",
    "Crop",
    "Year",
    "Extent",
    "Production"
]

def load_raw_data(filepath: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Loads raw Excel dataset into a pandas DataFrame."""
    if not filepath.exists():
        raise FileNotFoundError(f"Raw data file not found at {filepath}")
    
    print(f"Loading raw agricultural census dataset from: {filepath}...")
    df = pd.read_excel(filepath, engine="openpyxl")
    print(f"Successfully loaded {len(df):,} records with columns: {list(df.columns)}")
    return df

def validate_schema(df: pd.DataFrame) -> bool:
    """Validates that all expected agricultural census columns exist."""
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing mandatory columns in raw dataset: {missing_cols}")
    return True

def audit_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates an initial data profiling audit report."""
    validate_schema(df)
    
    audit = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "districts_count": df["District"].nunique(),
        "seasons": df["Season"].value_counts().to_dict(),
        "crop_categories_count": df["CropCategory"].nunique(),
        "crops_count": df["Crop"].nunique(),
        "year_min": str(df["Year"].min()),
        "year_max": str(df["Year"].max()),
        "missing_values_per_col": df.isnull().sum().to_dict(),
        "sample_dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    return audit

if __name__ == "__main__":
    df_raw = load_raw_data()
    audit = audit_raw_data(df_raw)
    print("\n--- RAW DATA AUDIT ---")
    for k, v in audit.items():
        print(f"{k}: {v}")
