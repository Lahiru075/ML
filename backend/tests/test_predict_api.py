"""
Unit Tests for FastAPI Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "documentation" in data

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["champion_r2"] is not None

def test_single_prediction_valid():
    payload = {
        "district": "Nuwara Eliya",
        "season": "Maha",
        "crop": "Potato",
        "extent_ha": 150.0,
        "year": 2024
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Nuwara Eliya"
    assert data["predicted_production_mt"] > 0
    assert data["predicted_yield_mt_per_ha"] > 0
    assert "confidence_interval" in data

def test_single_prediction_zero_extent():
    payload = {
        "district": "Badulla",
        "season": "Yala",
        "crop": "Maize",
        "extent_ha": 0.0
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_production_mt"] == 0.0
    assert data["predicted_yield_mt_per_ha"] == 0.0

def test_batch_prediction():
    payload = {
        "items": [
            {"district": "Nuwara Eliya", "season": "Maha", "crop": "Potato", "extent_ha": 100.0},
            {"district": "Badulla", "season": "Yala", "crop": "Maize", "extent_ha": 50.0}
        ]
    }
    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_processed"] == 2
    assert len(data["predictions"]) == 2

def test_analytics_summary():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_historical_records"] > 0
    assert data["total_districts"] > 0

def test_analytics_districts_and_crops():
    res_dist = client.get("/api/v1/analytics/districts")
    assert res_dist.status_code == 200
    assert len(res_dist.json()) >= 5
    
    res_crops = client.get("/api/v1/analytics/crops")
    assert res_crops.status_code == 200
    assert len(res_crops.json()) >= 10
