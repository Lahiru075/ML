"""
Prediction Endpoints for Single and Batch Inferences
"""
from fastapi import APIRouter, HTTPException
from backend.app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse
)
from backend.app.core.model_loader import model_loader

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict_harvest(request: PredictionRequest):
    """
    Forecasting endpoint: Predicts seasonal production (MT) and crop yield (MT/Ha)
    based on district, season, crop, and cultivated extent.
    """
    try:
        pipeline = model_loader.pipeline
        result = pipeline.predict_one(
            district=request.district,
            season=request.season,
            crop=request.crop,
            extent_ha=request.extent_ha,
            year=request.year
        )
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch_harvest(request: BatchPredictionRequest):
    """
    Batch forecasting endpoint for multiple agricultural scenarios.
    """
    try:
        pipeline = model_loader.pipeline
        results = pipeline.predict_batch([item.model_dump() for item in request.items])
        return BatchPredictionResponse(
            total_processed=len(results),
            predictions=[PredictionResponse(**r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch inference error: {str(e)}")
