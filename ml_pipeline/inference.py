"""
Inference Pipeline Engine for CropForecastLK
Defines the deployable pipeline class with full encapsulation.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import xgboost as xgb
from ml_pipeline.config import CROP_NAME_MAPPING

class CropForecastInferencePipeline:
    """
    Production-ready inference pipeline for CropForecastLK.
    Accepts raw user agricultural inputs, maps historical lag context,
    encodes categorical variables, and predicts harvest production and yield.
    """
    def __init__(
        self,
        model: xgb.XGBRegressor,
        target_encodings: Dict[str, Dict[str, float]],
        global_target_mean: float,
        crop_to_category: Dict[str, str],
        historical_stats: Dict[str, Dict[str, float]],
        feature_cols: List[str]
    ):
        self.model = model
        self.target_encodings = target_encodings
        self.global_target_mean = global_target_mean
        self.crop_to_category = crop_to_category
        self.historical_stats = historical_stats
        self.feature_cols = feature_cols

    def _normalize_crop(self, crop: str) -> str:
        clean = crop.strip().lower()
        return CROP_NAME_MAPPING.get(clean, crop.strip())

    def _get_historical_context(self, district: str, crop: str, season: str) -> Dict[str, float]:
        key = f"{district.strip()}|{crop.strip()}|{season.strip().capitalize()}"
        if key in self.historical_stats:
            return self.historical_stats[key]
        
        # Fallback to crop-season level
        crop_season_key = f"*|{crop.strip()}|{season.strip().capitalize()}"
        if crop_season_key in self.historical_stats:
            return self.historical_stats[crop_season_key]
        
        # Global fallback
        return {
            "prod_lag": self.global_target_mean * 0.5,
            "yield_lag": 5.0,
            "extent_lag": 50.0,
            "extent_roll_mean": 50.0,
            "extent_roll_std": 10.0
        }

    def predict_one(
        self,
        district: str,
        season: str,
        crop: str,
        extent_ha: float,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Runs single-record agricultural prediction."""
        norm_crop = self._normalize_crop(crop)
        norm_season = season.strip().capitalize()
        norm_district = district.strip()
        extent_val = max(0.0, float(extent_ha))
        
        # Determine category
        category = self.crop_to_category.get(norm_crop, "Other")
        
        # Season binary
        season_maha = 1 if norm_season.lower() == "maha" else 0
        
        # Historical context
        hist = self._get_historical_context(norm_district, norm_crop, norm_season)
        
        # Target encodings
        dist_enc = self.target_encodings["District"].get(norm_district, self.global_target_mean)
        crop_enc = self.target_encodings["Crop"].get(norm_crop, self.global_target_mean)
        cat_enc = self.target_encodings["CropCategory"].get(category, self.global_target_mean)
        
        # Build feature vector
        row = {
            "Extent": extent_val,
            "Season_Maha": season_maha,
            "Production_Lag_1Y": hist.get("prod_lag", 100.0),
            "Yield_Lag_1Y": hist.get("yield_lag", 5.0),
            "Extent_Lag_1Y": hist.get("extent_lag", extent_val),
            "Extent_RollMean_3Y": hist.get("extent_roll_mean", extent_val),
            "Extent_RollStd_3Y": hist.get("extent_roll_std", 5.0),
            "District_TargetEnc": dist_enc,
            "Crop_TargetEnc": crop_enc,
            "CropCategory_TargetEnc": cat_enc
        }
        
        X = pd.DataFrame([row])[self.feature_cols]
        raw_pred = float(self.model.predict(X)[0])
        
        # Production cannot be negative; if extent is 0, production is 0
        predicted_prod = 0.0 if extent_val == 0 else max(0.0, raw_pred)
        predicted_yield = 0.0 if extent_val == 0 else predicted_prod / extent_val
        
        lower_bound = max(0.0, predicted_prod * 0.85)
        upper_bound = predicted_prod * 1.15
        
        return {
            "district": norm_district,
            "season": norm_season,
            "crop": norm_crop,
            "crop_category": category,
            "extent_ha": extent_val,
            "predicted_production_mt": round(predicted_prod, 2),
            "predicted_yield_mt_per_ha": round(predicted_yield, 2),
            "confidence_interval": {
                "lower_mt": round(lower_bound, 2),
                "upper_mt": round(upper_bound, 2)
            }
        }

    def predict_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a list of prediction requests."""
        return [self.predict_one(**item) for item in items]
