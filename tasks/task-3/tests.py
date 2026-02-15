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

def test_structural_request_has_frequency():
    """STRUCTURAL: Verify 'grid_frequency' field exists in model."""
    assert "grid_frequency" in SimulationRequest.model_fields

def test_structural_frequency_threshold_constant():
    """STRUCTURAL: Verify the 49.8 Hz threshold appears in the code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "49.8" in content, "Frequency threshold 49.8 not found in code"

def test_structural_backend_interface_update():
    """STRUCTURAL: Verify TypeScript interface accepts frequency."""
    with open("server/src/services/optimizer.service.ts", "r") as f:
        content = f.read()
    assert "grid_frequency" in content, "Service interface missing grid_frequency"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_emergency_mode_activation():
    """FAIL_TO_PASS: Frequency of 49.7Hz must trigger 50% shedding."""
    # User asks for 0% reduction, but grid is dying (49.7Hz)
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, 
        "reduction_factor": 0.0, 
        "grid_frequency": 49.7
    })
    data = res.json()
    
    # Logic: Base Load (28500) * (1 - 0.5) = 14250
    # Allow for some thermal savings variance, but it must be huge.
    assert data["projected_kwh"] < 15000.0, \
        f"Emergency shedding failed. Expected < 15000, got {data['projected_kwh']}"

def test_emergency_mode_overrides_user():
    """FAIL_TO_PASS: Even if user wants 10%, emergency forces 50%."""
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, 
        "reduction_factor": 0.1, 
        "grid_frequency": 49.7
    })
    data = res.json()
    assert data["projected_kwh"] < 15000.0

# ==========================================
# REGRESSION TESTS (PASS_TO_PASS)
# ==========================================

def test_regression_normal_frequency():
    """PASS_TO_PASS: 50.0 Hz should respect user input."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,  # No thermal savings
        "reduction_factor": 0.0,
        "grid_frequency": 50.0
    })
    data = res.json()
    # Should be full load ~28500
    assert 28400 < data["projected_kwh"] < 28600