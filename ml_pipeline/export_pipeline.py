"""
Pipeline Serialization and Artifact Export Module for CropForecastLK
Encapsulates end-to-end inference logic, fits champion estimator on Train+Val,
benchmarks on holdout Test set, and serializes production joblib artifact.
"""
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from typing import Dict, Any, List, Optional

from ml_pipeline.config import (
    PROCESSED_DATA_PATH,
    FEATURED_DATA_PATH,
    ARTIFACTS_DIR,
    PIPELINE_PATH,
    METADATA_PATH,
    OPTUNA_PARAMS_PATH,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR,
    TEST_MIN_YEAR,
    TARGET_PRODUCTION,
    TARGET_YIELD,
    RANDOM_SEED,
    HIGHLAND_DISTRICTS,
    HIGHLAND_CROPS
)
from ml_pipeline.evaluate import evaluate_predictions
from ml_pipeline.inference import CropForecastInferencePipeline

FEATURE_COLS = [
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
]

def export_champion_pipeline() -> Dict[str, Any]:
    """Fits champion model on Train+Val, tests on holdout Test, and exports joblib pipeline."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load feature dataset
    df = pd.read_parquet(FEATURED_DATA_PATH)
    
    # Load Optuna best params
    if OPTUNA_PARAMS_PATH.exists():
        with open(OPTUNA_PARAMS_PATH, "r") as f:
            opt_data = json.load(f)
            best_params = opt_data.get("best_params", {})
    else:
        best_params = {
            "n_estimators": 250,
            "max_depth": 7,
            "learning_rate": 0.08,
            "subsample": 0.85,
            "colsample_bytree": 0.85
        }
        
    best_params["random_state"] = RANDOM_SEED
    best_params["n_jobs"] = -1
    
    # Splits
    trainval_mask = df["Year"] <= VAL_MAX_YEAR
    test_mask = df["Year"] >= TEST_MIN_YEAR
    
    X_trainval = df.loc[trainval_mask, FEATURE_COLS]
    y_trainval = df.loc[trainval_mask, TARGET_PRODUCTION]
    
    X_test = df.loc[test_mask, FEATURE_COLS]
    y_test = df.loc[test_mask, TARGET_PRODUCTION]
    
    print(f"Training champion model on Train+Val ({len(X_trainval):,} records) with params:")
    print(best_params)
    
    champion_model = xgb.XGBRegressor(**best_params)
    t0 = time.time()
    champion_model.fit(X_trainval, y_trainval)
    train_duration = time.time() - t0
    
    # Benchmark on Holdout Test Set (2021-2025)
    test_preds = champion_model.predict(X_test)
    test_metrics = evaluate_predictions(y_test, test_preds)
    print(f"\nChampion Model Final Holdout Test Metrics (2021-2025):")
    for k, v in test_metrics.items():
        print(f"  {k}: {v}")
        
    # Feature importances
    feature_importances = dict(zip(FEATURE_COLS, [round(float(x), 4) for x in champion_model.feature_importances_]))
    
    # Build crop to category lookup
    crop_cat_df = df[["Crop", "CropCategory"]].drop_duplicates()
    crop_to_cat = dict(zip(crop_cat_df["Crop"], crop_cat_df["CropCategory"]))
    
    # Compute historical lag/extent lookup per [District, Crop, Season]
    stats_dict = {}
    grouped = df.groupby(["District", "Crop", "Season"])
    for (dist, crp, ssn), grp in grouped:
        key = f"{dist}|{crp}|{ssn}"
        stats_dict[key] = {
            "prod_lag": float(grp[TARGET_PRODUCTION].iloc[-1]),
            "yield_lag": float(grp[TARGET_YIELD].iloc[-1]),
            "extent_lag": float(grp["Extent"].iloc[-1]),
            "extent_roll_mean": float(grp["Extent"].tail(3).mean()),
            "extent_roll_std": float(grp["Extent"].tail(3).std() or 0.0)
        }
        
    # Crop-season fallback
    cs_grouped = df.groupby(["Crop", "Season"])
    for (crp, ssn), grp in cs_grouped:
        key = f"*|{crp}|{ssn}"
        stats_dict[key] = {
            "prod_lag": float(grp[TARGET_PRODUCTION].median()),
            "yield_lag": float(grp[TARGET_YIELD].median()),
            "extent_lag": float(grp["Extent"].median()),
            "extent_roll_mean": float(grp["Extent"].median()),
            "extent_roll_std": float(grp["Extent"].std() or 0.0)
        }
        
    # Target encodings computed on training partition
    train_df = df[df["Year"] <= TRAIN_MAX_YEAR]
    global_mean = float(train_df[TARGET_PRODUCTION].mean())
    target_enc_maps = {}
    for col in ["District", "Crop", "CropCategory"]:
        c_stats = train_df.groupby(col)[TARGET_PRODUCTION].agg(["count", "mean"])
        smoothed = (c_stats["count"] * c_stats["mean"] + 10.0 * global_mean) / (c_stats["count"] + 10.0)
        target_enc_maps[col] = smoothed.to_dict()
        
    # Build complete inference pipeline object
    pipeline = CropForecastInferencePipeline(
        model=champion_model,
        target_encodings=target_enc_maps,
        global_target_mean=global_mean,
        crop_to_category=crop_to_cat,
        historical_stats=stats_dict,
        feature_cols=FEATURE_COLS
    )
    
    # Serialize pipeline
    joblib.dump(pipeline, PIPELINE_PATH)
    print(f"Serialized inference pipeline saved to: {PIPELINE_PATH}")
    
    # Save comprehensive model metadata
    all_districts = sorted(df["District"].unique().tolist())
    all_crops = sorted(df["Crop"].unique().tolist())
    all_seasons = ["Maha", "Yala"]
    
    metadata = {
        "model_name": "CropForecastLK XGBoost Regressor",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "training_duration_seconds": round(train_duration, 2),
        "trainval_records": len(X_trainval),
        "test_records": len(X_test),
        "best_hyperparameters": best_params,
        "holdout_test_metrics": test_metrics,
        "feature_importances": feature_importances,
        "supported_districts": all_districts,
        "highland_districts": HIGHLAND_DISTRICTS,
        "supported_crops": all_crops,
        "highland_crops": HIGHLAND_CROPS,
        "supported_seasons": all_seasons,
        "input_features": FEATURE_COLS
    }
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata exported to: {METADATA_PATH}")
    return metadata

if __name__ == "__main__":
    export_champion_pipeline()
