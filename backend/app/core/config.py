"""
Backend Configuration Settings
"""
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACTS_DIR = BASE_DIR / "data" / "artifacts"
PIPELINE_PATH = ARTIFACTS_DIR / "crop_forecaster_pipeline.joblib"
METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
CLEANED_DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_highland_crops.csv"

class Settings(BaseSettings):
    PROJECT_NAME: str = "CropForecastLK API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    
    PIPELINE_FILE: Path = PIPELINE_PATH
    METADATA_FILE: Path = METADATA_PATH
    CLEANED_DATA_FILE: Path = CLEANED_DATA_PATH

settings = Settings()
