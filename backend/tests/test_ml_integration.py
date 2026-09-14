"""
Integration Tests for ML Model Loader and Inference Performance
"""
import time
import pytest
from backend.app.core.model_loader import model_loader

def test_singleton_model_loader_latency():
    """Verifies that model inference completes in sub-50ms."""
    pipeline = model_loader.pipeline
    assert pipeline is not None
    
    # Warmup
    pipeline.predict_one("Nuwara Eliya", "Maha", "Potato", 100.0)
    
    # Measure latency across 20 inferences
    start_time = time.time()
    n_runs = 20
    for _ in range(n_runs):
        pipeline.predict_one("Badulla", "Yala", "Maize", 75.0)
    total_time = time.time() - start_time
    avg_latency_ms = (total_time / n_runs) * 1000.0
    
    print(f"\nAverage Model Inference Latency: {avg_latency_ms:.2f}ms")
    # Sub-50ms target as specified in architecture
    assert avg_latency_ms < 50.0, f"Latency exceeded 50ms: {avg_latency_ms:.2f}ms"

def test_metadata_attributes():
    meta = model_loader.metadata
    assert "model_name" in meta
    assert "holdout_test_metrics" in meta
    assert "feature_importances" in meta
    assert "highland_districts" in meta
    assert "highland_crops" in meta
