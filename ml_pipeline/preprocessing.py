"""
Data Preprocessing & Sanitization Pipeline for CropForecastLK
Handles regex string parsing, aggregate filtering, cohort median imputation,
and biological anomaly correction.
"""
import re
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from ml_pipeline.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    CROP_NAME_MAPPING,
    TARGET_PRODUCTION
)
from ml_pipeline.data_ingestion import load_raw_data

def clean_numeric_string(val) -> float:
    """Converts comma-formatted or placeholder strings to clean floats."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str.lower() in ["-", "n.a.", "nan", "", "none", "nil", "na"]:
        return np.nan
    clean_str = re.sub(r"[^\d.]", "", val_str)
    try:
        return float(clean_str)
    except ValueError:
        return np.nan

def parse_harvest_year(val) -> int:
    """Extracts standard integer harvest year from single or split strings (e.g., '2000/2001' -> 2001)."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if "/" in s:
        parts = s.split("/")
        return int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else int(parts[0])
    nums = re.findall(r"\d+", s)
    return int(nums[0]) if nums else np.nan

def filter_aggregate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Removes national/island summary rows and aggregate season rows."""
    aggregates = ["island total", "national total", "total", "all districts"]
    df_clean = df[~df["District"].astype(str).str.lower().str.strip().isin(aggregates)].copy()
    df_clean = df_clean[df_clean["Season"].astype(str).str.lower().str.strip() != "total"].copy()
    return df_clean

def normalize_categories_and_crops(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes string casing, strips trailing spaces, and standardizes crop names."""
    df_out = df.copy()
    for col in ["District", "Season", "CropCategory", "Crop"]:
        df_out[col] = df_out[col].astype(str).str.strip()
    
    # Capitalize Season to canonical 'Maha' or 'Yala'
    df_out["Season"] = df_out["Season"].str.capitalize()
    
    # Standardize crop naming using config mapping
    def map_crop(crop_name: str) -> str:
        lower_name = crop_name.lower().strip()
        return CROP_NAME_MAPPING.get(lower_name, crop_name)
    
    df_out["Crop"] = df_out["Crop"].apply(map_crop)
    return df_out

def handle_biological_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Addresses agricultural anomalies:
    1. Extent == 0 and Production > 0 is biologically impossible; set Production to NaN for imputation.
    2. Extent > 0 and Production == 0 is valid crop failure; preserved as 0.
    """
    df_out = df.copy()
    impossible_mask = (df_out["Extent"] == 0) & (df_out["Production"] > 0)
    anomalies_count = impossible_mask.sum()
    if anomalies_count > 0:
        print(f"Correcting {anomalies_count} impossible biological anomalies (Extent=0, Production>0)...")
        df_out.loc[impossible_mask, "Production"] = np.nan
    return df_out

def impute_cohort_medians(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputes missing Extent and Production using localized domain medians:
    1. Median of [District, Crop, Season] cohort
    2. Fallback to global median of [Crop, Season]
    3. Fallback to global median of [Crop]
    4. Fallback to 0.0
    """
    df_out = df.copy()
    
    for col in ["Extent", "Production"]:
        # Level 1: [District, Crop, Season]
        cohort_med = df_out.groupby(["District", "Crop", "Season"])[col].transform("median")
        df_out[col] = df_out[col].fillna(cohort_med)
        
        # Level 2: [Crop, Season]
        crop_season_med = df_out.groupby(["Crop", "Season"])[col].transform("median")
        df_out[col] = df_out[col].fillna(crop_season_med)
        
        # Level 3: [Crop]
        crop_med = df_out.groupby("Crop")[col].transform("median")
        df_out[col] = df_out[col].fillna(crop_med)
        
        # Level 4: Fallback to 0.0
        df_out[col] = df_out[col].fillna(0.0)
        
    return df_out

def run_preprocessing_pipeline(
    raw_path: Optional[Path] = None,
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """Executes the full Phase 2 data cleaning pipeline and saves results."""
    raw_file = raw_path or RAW_DATA_PATH
    out_file = output_path or PROCESSED_DATA_PATH
    
    print(f"Starting Phase 2 Preprocessing Pipeline...")
    df_raw = load_raw_data(raw_file)
    
    # 1. Filter aggregate summary rows
    print("Filtering national aggregates and double-counted 'Total' season rows...")
    df_filtered = filter_aggregate_rows(df_raw)
    
    # 2. Parse numerical values and harvest years
    print("Parsing numeric strings and standardizing harvest years...")
    df_filtered["Year"] = df_filtered["Year"].apply(parse_harvest_year).astype(int)
    df_filtered["Extent"] = df_filtered["Extent"].apply(clean_numeric_string)
    df_filtered["Production"] = df_filtered["Production"].apply(clean_numeric_string)
    
    # 3. Normalize crop and category strings
    print("Standardizing crop taxonomies and categorical casing...")
    df_norm = normalize_categories_and_crops(df_filtered)
    
    # 4. Handle biological anomalies
    df_anomaly_fixed = handle_biological_anomalies(df_norm)
    
    # 5. Cohort-based median imputation
    print("Applying hierarchical cohort median imputation...")
    df_clean = impute_cohort_medians(df_anomaly_fixed)
    
    # Sort chronologically and by hierarchy
    df_clean = df_clean.sort_values(by=["District", "Crop", "Season", "Year"]).reset_index(drop=True)
    
    # Ensure directory exists and save
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(out_file, index=False)
    print(f"Cleaned dataset saved successfully to {out_file} ({len(df_clean):,} records).")
    
    return df_clean

if __name__ == "__main__":
    df_cleaned = run_preprocessing_pipeline()
    print("Sample cleaned records:")
    print(df_cleaned.head())
