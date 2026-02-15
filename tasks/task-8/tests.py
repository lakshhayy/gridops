import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../optimizer'))
from main import app, SimulationRequest

client = TestClient(app)

# ==========================================
# STRUCTURAL TESTS
# ==========================================

def test_structural_occupancy_field():
    """STRUCTURAL: Verify 'occupancy_count' field exists in model."""
    assert "occupancy_count" in SimulationRequest.model_fields

def test_structural_occupancy_thresholds():
    """STRUCTURAL: Verify the 10 and 50 thresholds exist in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "10" in content and "50" in content, "Occupancy thresholds 10 or 50 not found"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_low_occupancy_comfort_bonus():
    """FAIL_TO_PASS: Low occupancy (< 10) should result in a higher comfort score for aggressive shedding."""
    # Case 1: Standard Occupancy (20)
    res_std = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.4, "occupancy_count": 20
    })
    
    # Case 2: Low Occupancy (5)
    res_low = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.4, "occupancy_count": 5
    })
    
    assert res_low.json()["comfort_index"] > res_std.json()["comfort_index"], \
        "Comfort bonus for low occupancy not applied"

def test_high_occupancy_comfort_penalty():
    """FAIL_TO_PASS: High occupancy (> 50) should result in a lower comfort score for high temperature."""
    # Case 1: Standard Occupancy (20)
    res_std = client.post("/calculate", json={
        "ac_setpoint": 28.0, "reduction_factor": 0.0, "occupancy_count": 20
    })
    
    # Case 2: High Occupancy (60)
    res_high = client.post("/calculate", json={
        "ac_setpoint": 28.0, "reduction_factor": 0.0, "occupancy_count": 60
    })
    
    assert res_high.json()["comfort_index"] < res_std.json()["comfort_index"], \
        "Comfort penalty for high occupancy not applied"

# ==========================================
# REGRESSION TESTS
# ==========================================

def test_regression_normal_occupancy():
    """PASS_TO_PASS: Default occupancy (20) should maintain original behavior."""
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, "reduction_factor": 0.1
    })
    assert res.status_code == 200