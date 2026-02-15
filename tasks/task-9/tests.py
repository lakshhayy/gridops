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

def test_structural_solar_field():
    """STRUCTURAL: Verify 'solar_generation_kw' field exists in model."""
    assert "solar_generation_kw" in SimulationRequest.model_fields

def test_structural_export_rate():
    """STRUCTURAL: Verify the 4.50 export rate constant exists in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "4.5" in content, "Export credit rate 4.5 not found"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_solar_reduces_cost():
    """FAIL_TO_PASS: Verify solar generation reduces the cost estimate."""
    # Case 1: No Solar
    res_no_solar = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.0, "solar_generation_kw": 0.0
    })
    
    # Case 2: 5000 kW Solar
    res_solar = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.0, "solar_generation_kw": 5000.0
    })
    
    assert res_solar.json()["cost_estimate"] < res_no_solar.json()["cost_estimate"]

def test_grid_export_credit():
    """FAIL_TO_PASS: Verify negative net load results in an export credit (low cost)."""
    # Force negative load: Base Load is 28500. Solar is 30000.
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0, 
        "solar_generation_kw": 30000.0
    })
    # Cost should be significantly lower than the standard ~300k.
    assert res.json()["cost_estimate"] < 10000.0

def test_carbon_footprint_floor():
    """FAIL_TO_PASS: Carbon footprint should be 0 if exporting energy, not negative."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0, 
        "solar_generation_kw": 40000.0
    })
    assert res.json()["carbon_footprint"] == 0.0

# ==========================================
# REGRESSION TESTS
# ==========================================

def test_regression_zero_solar():
    """PASS_TO_PASS: 0 solar generation should maintain standard billing."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.0, "solar_generation_kw": 0.0
    })
    assert 280000 < res.json()["cost_estimate"] < 320000