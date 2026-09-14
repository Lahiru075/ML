"""
Evaluation and Metrics Diagnostics Module for CropForecastLK
Computes RMSE, MAE, R², and MAPE, and provides regression diagnostic utilities.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def compute_mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-5) -> float:
    """Computes Mean Absolute Percentage Error (MAPE) ignoring near-zero actuals."""
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    valid_mask = np.abs(y_true_arr) > epsilon
    if not np.any(valid_mask):
        return 0.0
    return float(np.mean(np.abs((y_true_arr[valid_mask] - y_pred_arr[valid_mask]) / y_true_arr[valid_mask])) * 100.0)

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes a comprehensive dictionary of standard regression metrics."""
    y_true_arr = np.asarray(y_true).ravel()
    # Non-negative clip for physical production quantities
    y_pred_clipped = np.clip(np.asarray(y_pred).ravel(), 0.0, None)
    
    rmse = float(np.sqrt(mean_squared_error(y_true_arr, y_pred_clipped)))
    mae = float(mean_absolute_error(y_true_arr, y_pred_clipped))
    r2 = float(r2_score(y_true_arr, y_pred_clipped))
    mape = compute_mape(y_true_arr, y_pred_clipped)
    
    return {
        "RMSE": round(rmse, 4),
        "MAE": round(mae, 4),
        "R2": round(r2, 4),
        "MAPE": round(mape, 2)
    }

def print_benchmark_table(results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Formats benchmark dictionary into a clean comparison DataFrame."""
    df_results = pd.DataFrame.from_dict(results, orient="index")
    df_results = df_results.sort_values(by="RMSE", ascending=True)
    print("\n=======================================================")
    print("           MODEL BENCHMARKING SCORECARD                ")
    print("=======================================================")
    print(df_results.to_string())
    print("=======================================================\n")
    return df_results
