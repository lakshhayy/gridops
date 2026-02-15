import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../optimizer'))
from main import app, SimulationRequest

client = TestClient(app)

# ==========================================
#  STRUCTURAL TESTS
# ==========================================

def test_structural_request_has_voltage():
    """STRUCTURAL: Verify 'grid_voltage' field exists."""
    assert "grid_voltage" in SimulationRequest.model_fields

def test_structural_surge_threshold():
    """STRUCTURAL: Verify 255V threshold exists in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "255" in content, "Surge threshold 255V not found"

def test_structural_brownout_threshold():
    """STRUCTURAL: Verify 200V threshold exists in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "200" in content, "Brownout threshold 200V not found"

# ==========================================
#  BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_surge_protection_shutdown():
    """FAIL_TO_PASS: Voltage 260V should force 100% shutdown (0 kWh)."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "grid_voltage": 260.0
    })
    data = res.json()
    
    # 100% reduction means projected_kwh should be 0.0
    assert data["projected_kwh"] == 0.0, "Surge protection failed to cut power"
    assert data["grid_stability_score"] == 0.0, "Stability score should be 0 on surge"

def test_brownout_protection_min_shedding():
    """FAIL_TO_PASS: Voltage 190V should force 50% shedding."""
    # User asks for 0%, but brownout forces 50%
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "grid_voltage": 190.0
    })
    data = res.json()
    
    # 28500 * 0.5 = 14250
    assert data["projected_kwh"] <= 14250.0, "Brownout protection failed to shed 50%"

# ==========================================
#  REGRESSION TESTS (PASS_TO_PASS)
# ==========================================

def test_regression_normal_voltage():
    """PASS_TO_PASS: 230V should operate normally."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "grid_voltage": 230.0
    })
    data = res.json()
    assert 28400 < data["projected_kwh"] < 28600