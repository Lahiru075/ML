"""
Global Configuration and Constants for CropForecastLK
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "researchData.xlsx"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_highland_crops.csv"
FEATURED_DATA_PATH = DATA_DIR / "processed" / "engineered_features.parquet"
FEATURED_CSV_PATH = DATA_DIR / "processed" / "engineered_features.csv"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
PIPELINE_PATH = ARTIFACTS_DIR / "crop_forecaster_pipeline.joblib"
METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
OPTUNA_PARAMS_PATH = ARTIFACTS_DIR / "optuna_study_best_params.json"

# Modeling Seeds & Targets
RANDOM_SEED = 42
TARGET_PRODUCTION = "Production"
TARGET_YIELD = "Crop_Yield"

# Highland Focus Districts
HIGHLAND_DISTRICTS = [
    "Nuwara Eliya",
    "Badulla",
    "Kandy",
    "Matale",
    "Moneragala"
]

# Highland Priority Staple Crops
HIGHLAND_CROPS = [
    "Potato",
    "Maize",
    "Kurakkan",
    "Green Gram",
    "Chili",
    "Sweet Potato",
    "Cassava"
]

# Canonical Crop Name Normalization Map
CROP_NAME_MAPPING = {
    "potatoes": "Potato",
    "sweet potatoes": "Sweet Potato",
    "manioc": "Cassava",
    "chillies": "Chili",
    "chilli": "Chili",
    "finger millet": "Kurakkan"
}

# Temporal Split Boundaries
TRAIN_MAX_YEAR = 2017
VAL_MAX_YEAR = 2020
TEST_MIN_YEAR = 2021
