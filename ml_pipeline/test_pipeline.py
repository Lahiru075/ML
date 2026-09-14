"""
Unit and Integration Tests for CropForecastLK ML Pipeline
"""
import pytest
import numpy as np
import pandas as pd
import joblib

from ml_pipeline.preprocessing import clean_numeric_string, parse_harvest_year, handle_biological_anomalies
from ml_pipeline.config import PIPELINE_PATH, METADATA_PATH, HIGHLAND_DISTRICTS, HIGHLAND_CROPS

def test_clean_numeric_string():
    assert clean_numeric_string("4,986.0") == 4986.0
    assert clean_numeric_string("12.5") == 12.5
    assert np.isnan(clean_numeric_string("-"))
    assert np.isnan(clean_numeric_string("n.a."))
    assert np.isnan(clean_numeric_string(""))

def test_parse_harvest_year():
    assert parse_harvest_year("2000/2001") == 2001
    assert parse_harvest_year("2003/2004") == 2004
    assert parse_harvest_year("2015") == 2015
    assert parse_harvest_year(2022) == 2022

def test_biological_anomaly_correction():
    df_sample = pd.DataFrame([
        {"District": "Kandy", "Season": "Maha", "Crop": "Potato", "Extent": 0.0, "Production": 150.0},
        {"District": "Kandy", "Season": "Yala", "Crop": "Potato", "Extent": 10.0, "Production": 0.0}
    ])
    df_fixed = handle_biological_anomalies(df_sample)
    # Extent=0, Production>0 should be set to NaN
    assert np.isnan(df_fixed.loc[0, "Production"])
    # Extent>0, Production=0 should remain 0
    assert df_fixed.loc[1, "Production"] == 0.0

def test_serialized_pipeline_inference():
    assert PIPELINE_PATH.exists(), f"Pipeline artifact missing at {PIPELINE_PATH}"
    pipeline = joblib.load(PIPELINE_PATH)
    
    # Test Highland crops
    for dist in HIGHLAND_DISTRICTS:
        for crop in HIGHLAND_CROPS[:3]:
            res = pipeline.predict_one(district=dist, season="Maha", crop=crop, extent_ha=100.0)
            assert res["predicted_production_mt"] >= 0.0
            assert res["predicted_yield_mt_per_ha"] >= 0.0
            assert res["confidence_interval"]["lower_mt"] <= res["confidence_interval"]["upper_mt"]

def test_zero_extent_prediction():
    pipeline = joblib.load(PIPELINE_PATH)
    res = pipeline.predict_one(district="Nuwara Eliya", season="Maha", crop="Potato", extent_ha=0.0)
    assert res["predicted_production_mt"] == 0.0
    assert res["predicted_yield_mt_per_ha"] == 0.0
