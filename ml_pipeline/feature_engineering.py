"""
Feature Engineering Module for CropForecastLK
Implements domain yield ratios, temporal lags, rolling statistics,
and smoothed target encodings with strict data leakage prevention.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from ml_pipeline.config import (
    PROCESSED_DATA_PATH,
    FEATURED_DATA_PATH,
    FEATURED_CSV_PATH,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR,
    TEST_MIN_YEAR,
    TARGET_PRODUCTION,
    TARGET_YIELD
)

def compute_yield_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates Crop_Yield (MT/Ha) with safe division."""
    df_out = df.copy()
    # Safe division where Extent > 0
    safe_mask = df_out["Extent"] > 0
    df_out[TARGET_YIELD] = 0.0
    df_out.loc[safe_mask, TARGET_YIELD] = (
        df_out.loc[safe_mask, TARGET_PRODUCTION] / df_out.loc[safe_mask, "Extent"]
    )
    return df_out

def compute_temporal_lags_and_rolling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes 1-Year lags and 3-Year rolling statistics partitioned by
    [District, Crop, Season] ordered by harvest Year.
    """
    df_out = df.copy()
    df_out = df_out.sort_values(by=["District", "Crop", "Season", "Year"]).reset_index(drop=True)
    
    group_cols = ["District", "Crop", "Season"]
    grouped = df_out.groupby(group_cols)
    
    # 1-Year Lags
    df_out["Production_Lag_1Y"] = grouped[TARGET_PRODUCTION].shift(1)
    df_out["Yield_Lag_1Y"] = grouped[TARGET_YIELD].shift(1)
    df_out["Extent_Lag_1Y"] = grouped["Extent"].shift(1)
    
    # 3-Year Rolling Statistics
    df_out["Extent_RollMean_3Y"] = (
        grouped["Extent"].rolling(window=3, min_periods=1).mean().reset_index(level=[0, 1, 2], drop=True)
    )
    df_out["Extent_RollStd_3Y"] = (
        grouped["Extent"].rolling(window=3, min_periods=1).std().reset_index(level=[0, 1, 2], drop=True).fillna(0.0)
    )
    
    # Impute missing initial lag values using cohort median, then crop median
    for col in ["Production_Lag_1Y", "Yield_Lag_1Y", "Extent_Lag_1Y"]:
        cohort_med = df_out.groupby(group_cols)[col].transform("median")
        df_out[col] = df_out[col].fillna(cohort_med)
        
        crop_med = df_out.groupby("Crop")[col].transform("median")
        df_out[col] = df_out[col].fillna(crop_med)
        df_out[col] = df_out[col].fillna(0.0)
        
    return df_out

def compute_target_encodings(
    df: pd.DataFrame,
    smoothing: float = 10.0,
    train_max_year: int = TRAIN_MAX_YEAR
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]], float]:
    """
    Computes smoothed target encodings using training set records ONLY (<= train_max_year)
    to strictly prevent forward temporal data leakage.
    Formula: S_i = (n * mean_cat + m * mean_global) / (n + m)
    """
    df_out = df.copy()
    train_mask = df_out["Year"] <= train_max_year
    df_train = df_out[train_mask]
    
    global_mean = float(df_train[TARGET_PRODUCTION].mean())
    encoding_maps = {}
    
    for cat_col in ["District", "Crop", "CropCategory"]:
        stats = df_train.groupby(cat_col)[TARGET_PRODUCTION].agg(["count", "mean"])
        smoothed = (stats["count"] * stats["mean"] + smoothing * global_mean) / (stats["count"] + smoothing)
        mapping = smoothed.to_dict()
        encoding_maps[cat_col] = mapping
        
        # Map to full dataframe with global_mean as unseen fallback
        encoded_col_name = f"{cat_col}_TargetEnc"
        df_out[encoded_col_name] = df_out[cat_col].map(mapping).fillna(global_mean)
        
    return df_out, encoding_maps, global_mean

def build_feature_dataset(
    input_path: Optional[Path] = None,
    output_parquet: Optional[Path] = None,
    output_csv: Optional[Path] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Runs the full feature engineering pipeline."""
    in_file = input_path or PROCESSED_DATA_PATH
    out_parquet = output_parquet or FEATURED_DATA_PATH
    out_csv = output_csv or FEATURED_CSV_PATH
    
    print(f"Loading cleaned data from {in_file}...")
    df = pd.read_csv(in_file)
    
    # 1. Compute Yield Ratio
    print("Computing agronomic Crop_Yield ratio...")
    df = compute_yield_ratio(df)
    
    # 2. Compute Temporal Lags & Rolling Window Statistics
    print("Engineering 1-Year lags and 3-Year rolling cultivation statistics...")
    df = compute_temporal_lags_and_rolling(df)
    
    # 3. Binary Season Encoding
    df["Season_Maha"] = (df["Season"].str.lower() == "maha").astype(int)
    
    # 4. Out-of-fold Smoothed Target Encodings
    print("Computing smoothed historical target encodings on training partition...")
    df, enc_maps, global_mean = compute_target_encodings(df)
    
    # 5. Log-transform Production for stabilized variance analysis
    df["Log_Production"] = np.log1p(df[TARGET_PRODUCTION].clip(lower=0))
    
    # Metadata dictionary for production inference pipeline
    feature_meta = {
        "global_mean_production": global_mean,
        "target_encodings": enc_maps,
        "feature_columns": [
            "Extent",
            "Season_Maha",
            "Production_Lag_1Y",
            "Yield_Lag_1Y",
            "Extent_Lag_1Y",
            "Extent_RollMean_3Y",
            "Extent_RollStd_3Y",
            "District_TargetEnc",
            "Crop_TargetEnc",
            "CropCategory_TargetEnc"
        ],
        "target_production": TARGET_PRODUCTION,
        "target_yield": TARGET_YIELD
    }
    
    # Save datasets
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    df.to_csv(out_csv, index=False)
    print(f"Feature dataset saved to Parquet: {out_parquet} and CSV: {out_csv}")
    print(f"Feature matrix shape: {df.shape}")
    
    return df, feature_meta

if __name__ == "__main__":
    df_feat, meta = build_feature_dataset()
    print("Sample feature matrix:")
    print(df_feat[["District", "Crop", "Season", "Year", "Extent", "Crop_Yield", "Production_Lag_1Y", "District_TargetEnc"]].head())
