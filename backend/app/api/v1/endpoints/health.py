"""
Health Check Endpoint
"""
from fastapi import APIRouter
from backend.app.schemas.prediction import HealthResponse
from backend.app.core.config import settings
from backend.app.core.model_loader import model_loader

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    meta = model_loader.metadata
    test_metrics = meta.get("holdout_test_metrics", {})
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        model_loaded=model_loader.is_loaded,
        model_name=meta.get("model_name"),
        champion_r2=test_metrics.get("R2"),
        champion_rmse=test_metrics.get("RMSE")
    )
