"""
API v1 Router Registration
"""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, predict, analytics

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predict.router, tags=["Forecasting"])
api_router.include_router(analytics.router, tags=["Analytics"])
