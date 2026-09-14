"""
Model Loader Singleton for CropForecastLK
Loads the serialized inference pipeline and metadata once at startup into memory.
"""
import json
import time
import joblib
from typing import Optional, Dict, Any
from backend.app.core.config import settings

class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _pipeline = None
    _metadata: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load_artifacts(self) -> None:
        """Loads joblib pipeline and metadata JSON into RAM."""
        if self._pipeline is None:
            if not settings.PIPELINE_FILE.exists():
                raise FileNotFoundError(f"ML Pipeline artifact not found at {settings.PIPELINE_FILE}")
            
            t0 = time.time()
            print(f"Loading CropForecastLK pipeline from {settings.PIPELINE_FILE}...")
            self._pipeline = joblib.load(settings.PIPELINE_FILE)
            load_time = time.time() - t0
            print(f"Pipeline successfully loaded into RAM in {load_time:.2f}s.")
            
        if self._metadata is None and settings.METADATA_FILE.exists():
            with open(settings.METADATA_FILE, "r") as f:
                self._metadata = json.load(f)

    @property
    def pipeline(self):
        if self._pipeline is None:
            self.load_artifacts()
        return self._pipeline

    @property
    def metadata(self) -> Dict[str, Any]:
        if self._metadata is None:
            self.load_artifacts()
        return self._metadata or {}

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

model_loader = ModelLoader()
