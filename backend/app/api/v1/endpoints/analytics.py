"""
Historical Analytics & Summary Endpoints
Serves pre-aggregated data and model performance telemetry to frontend Recharts widgets.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query
from backend.app.core.config import settings
from backend.app.core.model_loader import model_loader
from ml_pipeline.config import HIGHLAND_DISTRICTS, HIGHLAND_CROPS

router = APIRouter()
_df_cache: Optional[pd.DataFrame] = None

def get_cleaned_data() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        if settings.CLEANED_DATA_FILE.exists():
            _df_cache = pd.read_csv(settings.CLEANED_DATA_FILE)
        else:
            _df_cache = pd.DataFrame()
    return _df_cache

@router.get("/analytics/summary")
def get_analytics_summary() -> Dict[str, Any]:
    """Returns top-level KPIs for the overview dashboard."""
    df = get_cleaned_data()
    if df.empty:
        return {}
    
    total_records = len(df)
    total_prod = float(df["Production"].sum())
    total_extent = float(df["Extent"].sum())
    avg_yield = round(total_prod / total_extent, 2) if total_extent > 0 else 0.0
    
    return {
        "total_historical_records": total_records,
        "total_production_mt": round(total_prod, 2),
        "total_extent_ha": round(total_extent, 2),
        "national_mean_yield_mt_per_ha": avg_yield,
        "year_min": int(df["Year"].min()),
        "year_max": int(df["Year"].max()),
        "total_districts": int(df["District"].nunique()),
        "total_crops": int(df["Crop"].nunique())
    }

@router.get("/analytics/districts")
def get_districts():
    """Returns unique districts with highland classification."""
    df = get_cleaned_data()
    districts = sorted(df["District"].unique().tolist()) if not df.empty else HIGHLAND_DISTRICTS
    return [
        {"name": d, "is_highland": d in HIGHLAND_DISTRICTS}
        for d in districts
    ]

@router.get("/analytics/crops")
def get_crops():
    """Returns list of crops with categories and highland priority flag."""
    df = get_cleaned_data()
    if df.empty:
        return []
    crop_meta = df[["Crop", "CropCategory"]].drop_duplicates().sort_values(by="Crop")
    return [
        {
            "crop": row["Crop"],
            "category": row["CropCategory"],
            "is_highland_staple": row["Crop"] in HIGHLAND_CROPS
        }
        for _, row in crop_meta.iterrows()
    ]

@router.get("/analytics/historical")
def get_historical_trends(
    district: str = Query(..., example="Nuwara Eliya"),
    crop: str = Query(..., example="Potato")
):
    """Returns historical production & yield time-series for a selected district and crop."""
    df = get_cleaned_data()
    if df.empty:
        return []
    
    filtered = df[(df["District"].str.lower() == district.strip().lower()) & 
                  (df["Crop"].str.lower() == crop.strip().lower())].copy()
    
    if filtered.empty:
        return []
        
    filtered = filtered.sort_values(by="Year")
    filtered["Crop_Yield"] = (filtered["Production"] / filtered["Extent"].replace(0, pd.NA)).fillna(0.0)
    
    records = []
    for year, grp in filtered.groupby("Year"):
        maha_row = grp[grp["Season"] == "Maha"]
        yala_row = grp[grp["Season"] == "Yala"]
        
        maha_prod = float(maha_row["Production"].iloc[0]) if not maha_row.empty else 0.0
        yala_prod = float(yala_row["Production"].iloc[0]) if not yala_row.empty else 0.0
        maha_yield = round(float(maha_row["Crop_Yield"].iloc[0]), 2) if not maha_row.empty else 0.0
        yala_yield = round(float(yala_row["Crop_Yield"].iloc[0]), 2) if not yala_row.empty else 0.0
        
        records.append({
            "year": int(year),
            "maha_production_mt": round(maha_prod, 2),
            "yala_production_mt": round(yala_prod, 2),
            "total_production_mt": round(maha_prod + yala_prod, 2),
            "maha_yield": maha_yield,
            "yala_yield": yala_yield
        })
    return records

@router.get("/analytics/benchmarks")
def get_model_benchmarks():
    """Returns model metadata, benchmarking scorecard, and feature importance."""
    meta = model_loader.metadata
    return meta
