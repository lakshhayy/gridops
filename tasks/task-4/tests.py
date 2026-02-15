import pytest
import ast
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../optimizer'))
from main import app, SimulationRequest

client = TestClient(app)

# ==========================================
# STRUCTURAL TESTS (The "Traps")
# ==========================================

def test_structural_request_has_pf():
    """STRUCTURAL: Verify 'power_factor' field exists in model."""
    assert "power_factor" in SimulationRequest.model_fields

def test_structural_pf_constants():
    """STRUCTURAL: Verify the 0.90 and 0.95 thresholds exist in code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "0.9" in content, "Penalty threshold 0.90 not found"
    assert "0.95" in content, "Rebate threshold 0.95 not found"

def test_structural_stability_cap():
    """STRUCTURAL: Verify the stability cap of 0.6 exists."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "0.6" in content, "Stability cap 0.6 not found for low PF"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_low_pf_penalty():
    """FAIL_TO_PASS: PF 0.80 should increase cost by 10%."""
    # Base calculation (approx): 28500 * Rate
    # With PF 0.80 (0.10 drop), multiplier is 1.10
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "power_factor": 0.80
    })
    data = res.json()
    
    # Normal cost is ~300,000. With 10% penalty, should be ~330,000
    assert data["cost_estimate"] > 320000.0, "Penalty not applied correctly"

def test_high_pf_rebate():
    """FAIL_TO_PASS: PF 1.0 should decrease cost by 2.5%."""
    # Gain is 0.05. Rebate is half of that -> 2.5% discount.
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "power_factor": 1.0
    })
    data = res.json()
    
    # Normal cost ~310,000 (blended rate). Discounted should be lower.
    # We verify it's CHEAPER than the standard run
    standard_res = client.post("/calculate", json={
        "ac_setpoint": 22.0, "reduction_factor": 0.0, "power_factor": 0.9
    })
    assert data["cost_estimate"] < standard_res.json()["cost_estimate"]

def test_stability_penalty():
    """FAIL_TO_PASS: Very low PF (0.7) should cap stability score at 0.6."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "power_factor": 0.7
    })
    assert res.json()["grid_stability_score"] <= 0.6

# ==========================================
# REGRESSION TESTS (PASS_TO_PASS)
# ==========================================

def test_regression_default_pf():
    """PASS_TO_PASS: Missing PF should default to 0.90 (No change)."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0
    })
    assert res.status_code == 200