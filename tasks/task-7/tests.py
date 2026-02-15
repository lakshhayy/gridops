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

def test_structural_humidity_field():
    """STRUCTURAL: Verify 'relative_humidity' field exists in model."""
    assert "relative_humidity" in SimulationRequest.model_fields

def test_structural_humidity_threshold():
    """STRUCTURAL: Verify the 60% humidity threshold exists in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "60" in content, "Humidity threshold 60.0 not found in code"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_high_humidity_increases_load():
    """FAIL_TO_PASS: Verify 90% humidity results in higher consumption than 60%."""
    # 26C setpoint (4 degree delta)
    # Case 1: Standard Humidity (60%)
    res_low = client.post("/calculate", json={
        "ac_setpoint": 26.0, 
        "reduction_factor": 0.0, 
        "relative_humidity": 60.0
    })
    
    # Case 2: High Humidity (90%)
    res_high = client.post("/calculate", json={
        "ac_setpoint": 26.0, 
        "reduction_factor": 0.0, 
        "relative_humidity": 90.0
    })
    
    # High humidity should result in higher projected_kwh due to efficiency drop
    assert res_high.json()["projected_kwh"] > res_low.json()["projected_kwh"]

def test_humidity_below_threshold_no_impact():
    """FAIL_TO_PASS: Verify humidity <= 60% uses base efficiency."""
    res_40 = client.post("/calculate", json={
        "ac_setpoint": 26.0, 
        "reduction_factor": 0.0, 
        "relative_humidity": 40.0
    })
    res_60 = client.post("/calculate", json={
        "ac_setpoint": 26.0, 
        "reduction_factor": 0.0, 
        "relative_humidity": 60.0
    })
    assert res_40.json()["projected_kwh"] == res_60.json()["projected_kwh"]

# ==========================================
# REGRESSION TESTS
# ==========================================

def test_regression_default_humidity():
    """PASS_TO_PASS: Verify missing humidity defaults to standard behavior."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0
    })
    assert res.status_code == 200