"""
FastAPI Application Entry Point with modern Lifespan Context Manager
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.model_loader import model_loader
from backend.app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-loads the serialized ML pipeline into memory for sub-50ms inference."""
    try:
        model_loader.load_artifacts()
    except Exception as e:
        print(f"Warning: Could not load ML pipeline during startup: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sri Lanka Highland Crops Production Forecasting & Agricultural Intelligence Microservice",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to CropForecastLK Intelligence Microservice",
        "documentation": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }

# Register API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
