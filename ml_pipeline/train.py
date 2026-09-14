"""
Model Benchmarking, Cross-Validation, and Optuna Tuning Module
Benchmarks 5 algorithms (Ridge, Random Forest, CatBoost, LightGBM, XGBoost)
across chronological splits and optimizes champion model via Optuna.
"""
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import optuna

from ml_pipeline.config import (
    FEATURED_DATA_PATH,
    FEATURED_CSV_PATH,
    RANDOM_SEED,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR,
    TEST_MIN_YEAR,
    TARGET_PRODUCTION,
    OPTUNA_PARAMS_PATH
)
from ml_pipeline.evaluate import evaluate_predictions, print_benchmark_table

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

def load_feature_splits() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads feature dataset and performs strict chronological splitting."""
    if FEATURED_DATA_PATH.exists():
        df = pd.read_parquet(FEATURED_DATA_PATH)
    else:
        df = pd.read_csv(FEATURED_CSV_PATH)
        
    df_train = df[df["Year"] <= TRAIN_MAX_YEAR].copy()
    df_val = df[(df["Year"] > TRAIN_MAX_YEAR) & (df["Year"] <= VAL_MAX_YEAR)].copy()
    df_test = df[df["Year"] >= TEST_MIN_YEAR].copy()
    
    print(f"Data Split Summary:")
    print(f"  Train Set (<= {TRAIN_MAX_YEAR}): {len(df_train):,} records")
    print(f"  Val Set   ({TRAIN_MAX_YEAR + 1}-{VAL_MAX_YEAR}): {len(df_val):,} records")
    print(f"  Test Set  (>= {TEST_MIN_YEAR}): {len(df_test):,} records")
    
    return df_train, df_val, df_test

def get_candidate_models() -> Dict[str, Any]:
    """Returns a dictionary of candidate models for multi-model benchmarking."""
    return {
        "Ridge Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", Ridge(alpha=10.0, random_state=RANDOM_SEED))
        ]),
        "Random Forest": RandomForestRegressor(
            n_estimators=120,
            max_depth=12,
            min_samples_split=5,
            random_state=RANDOM_SEED,
            n_jobs=-1
        ),
        "CatBoost": CatBoostRegressor(
            iterations=250,
            depth=6,
            learning_rate=0.08,
            random_seed=RANDOM_SEED,
            verbose=0
        ),
        "LightGBM": lgb.LGBMRegressor(
            n_estimators=250,
            max_depth=7,
            learning_rate=0.08,
            random_state=RANDOM_SEED,
            verbose=-1,
            n_jobs=-1
        ),
        "XGBoost": xgb.XGBRegressor(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
    }

def benchmark_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> Tuple[Dict[str, Dict[str, float]], str, Any]:
    """Fits each candidate model and records evaluation metrics on validation set."""
    models = get_candidate_models()
    benchmark_scores = {}
    best_model_name = None
    best_rmse = float("inf")
    best_fitted_model = None
    
    print("\nStarting 5-Model Comparative Benchmarking on Validation Set...")
    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        fit_time = time.time() - t0
        
        preds = model.predict(X_val)
        scores = evaluate_predictions(y_val, preds)
        scores["Fit_Time_Sec"] = round(fit_time, 2)
        benchmark_scores[name] = scores
        print(f"[{name}] RMSE: {scores['RMSE']:.2f} | MAE: {scores['MAE']:.2f} | R²: {scores['R2']:.4f} | Time: {fit_time:.2f}s")
        
        if scores["RMSE"] < best_rmse:
            best_rmse = scores["RMSE"]
            best_model_name = name
            best_fitted_model = model
            
    print(f"\nChampion Candidate: {best_model_name} (Validation RMSE: {best_rmse:.2f})")
    return benchmark_scores, best_model_name, best_fitted_model

def run_timeseries_cv(
    X_full: pd.DataFrame,
    y_full: pd.Series,
    n_splits: int = 5
) -> Dict[str, float]:
    """Runs 5-Fold TimeSeriesSplit cross validation to test stability across temporal regimes."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmse_scores = []
    r2_scores = []
    
    for fold, (train_idx, test_idx) in enumerate(tscv.split(X_full)):
        X_tr, y_tr = X_full.iloc[train_idx], y_full.iloc[train_idx]
        X_te, y_te = X_full.iloc[test_idx], y_full.iloc[test_idx]
        
        model = xgb.XGBRegressor(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.08,
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)
        metrics = evaluate_predictions(y_te, preds)
        rmse_scores.append(metrics["RMSE"])
        r2_scores.append(metrics["R2"])
        print(f"TimeSeries Fold {fold + 1}: Train={len(train_idx)}, Test={len(test_idx)} -> RMSE: {metrics['RMSE']:.2f}, R²: {metrics['R2']:.4f}")
        
    return {
        "mean_cv_rmse": float(np.mean(rmse_scores)),
        "std_cv_rmse": float(np.std(rmse_scores)),
        "mean_cv_r2": float(np.mean(r2_scores))
    }

def run_optuna_study(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_trials: int = 35
) -> Dict[str, Any]:
    """Executes an Optuna hyperparameter optimization study on champion XGBoost model."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    print(f"\nLaunching Optuna Optimization Study ({n_trials} Trials)...")
    
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 150, 400, step=50),
            "max_depth": trial.suggest_int("max_depth", 4, 9),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-2, 5.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-2, 10.0, log=True),
            "random_state": RANDOM_SEED,
            "n_jobs": -1
        }
        
        reg = xgb.XGBRegressor(**params)
        reg.fit(X_train, y_train)
        preds = reg.predict(X_val)
        val_rmse = np.sqrt(np.mean((np.clip(preds, 0, None) - y_val.values) ** 2))
        return val_rmse

    sampler = optuna.samplers.TPESampler(seed=RANDOM_SEED)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    
    print(f"Optuna Study Complete. Best Trial RMSE: {study.best_value:.2f}")
    print(f"Optimal Hyperparameters: {study.best_params}")
    
    # Save best parameters to JSON
    OPTUNA_PARAMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OPTUNA_PARAMS_PATH, "w") as f:
        json.dump({
            "best_val_rmse": float(study.best_value),
            "best_params": study.best_params,
            "n_trials": n_trials
        }, f, indent=2)
        
    return study.best_params

if __name__ == "__main__":
    df_train, df_val, df_test = load_feature_splits()
    
    X_train = df_train[FEATURE_COLS]
    y_train = df_train[TARGET_PRODUCTION]
    
    X_val = df_val[FEATURE_COLS]
    y_val = df_val[TARGET_PRODUCTION]
    
    X_test = df_test[FEATURE_COLS]
    y_test = df_test[TARGET_PRODUCTION]
    
    # 1. Benchmarking
    benchmark_scores, best_model, champion = benchmark_models(X_train, y_train, X_val, y_val)
    print_benchmark_table(benchmark_scores)
    
    # 2. TimeSeries CV
    print("\nRunning TimeSeries Cross-Validation...")
    X_trainval = pd.concat([X_train, X_val])
    y_trainval = pd.concat([y_train, y_val])
    cv_res = run_timeseries_cv(X_trainval, y_trainval)
    print("TimeSeries CV Summary:", cv_res)
    
    # 3. Optuna Study
    best_params = run_optuna_study(X_train, y_train, X_val, y_val, n_trials=35)
