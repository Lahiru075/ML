"""
Pydantic Schemas for Agricultural Prediction and Analytics
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    district: str = Field(..., json_schema_extra={"example": "Nuwara Eliya"}, description="Sri Lankan administrative district")
    season: str = Field(..., json_schema_extra={"example": "Maha"}, description="Agricultural cultivation season ('Maha' or 'Yala')")
    crop: str = Field(..., json_schema_extra={"example": "Potato"}, description="Crop name to forecast")
    extent_ha: float = Field(..., ge=0.0, json_schema_extra={"example": 150.0}, description="Cultivated land area in Hectares")
    year: Optional[int] = Field(default=None, json_schema_extra={"example": 2024}, description="Harvest year")

class ConfidenceInterval(BaseModel):
    lower_mt: float = Field(..., description="Estimated lower bound production in MT")
    upper_mt: float = Field(..., description="Estimated upper bound production in MT")

class PredictionResponse(BaseModel):
    district: str
    season: str
    crop: str
    crop_category: str
    extent_ha: float
    predicted_production_mt: float
    predicted_yield_mt_per_ha: float
    confidence_interval: ConfidenceInterval

class BatchPredictionRequest(BaseModel):
    items: List[PredictionRequest]

class BatchPredictionResponse(BaseModel):
    total_processed: int
    predictions: List[PredictionResponse]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    model_name: Optional[str] = None
    champion_r2: Optional[float] = None
    champion_rmse: Optional[float] = None
