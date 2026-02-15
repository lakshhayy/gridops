import pytest
import ast
from fastapi.testclient import TestClient
import sys
import os

# Add optimizer path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../optimizer'))
from main import app, SimulationRequest

client = TestClient(app)

# ==========================================
# 🏗️ STRUCTURAL TESTS (4 Tests)
# ==========================================

def test_structural_simulation_request_has_carbon():
    """STRUCTURAL: Verify 'grid_carbon_intensity' field exists in model."""
    assert "grid_carbon_intensity" in SimulationRequest.model_fields

def test_structural_auto_shedding_threshold_exists():
    """STRUCTURAL: Verify the 0.9 threshold logic exists in the code."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    # We look for the threshold number in the code text
    assert "0.9" in content, "Threshold 0.9 not found in source code"

def test_structural_min_shedding_value_exists():
    """STRUCTURAL: Verify the 0.2 (20%) minimum shedding value exists."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "0.2" in content, "Minimum shedding 0.2 not found in source code"

def test_structural_backend_interface_update():
    """STRUCTURAL: Verify TypeScript interface accepts carbon intensity."""
    with open("server/src/services/optimizer.service.ts", "r") as f:
        content = f.read()
    assert "grid_carbon_intensity" in content, "Service interface missing grid_carbon_intensity"

# ==========================================
# 🧪 BEHAVIORAL TESTS (FAIL_TO_PASS) (2 Tests)
# ==========================================

def test_carbon_override_logic_dirty_grid():
    """FAIL_TO_PASS: Dirty grid (>0.9) should enforce min 0.2 reduction."""
    # User asks for 0% reduction, but grid is dirty (0.95)
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, 
        "reduction_factor": 0.0, 
        "grid_carbon_intensity": 0.95
    })
    data = res.json()
    
    # Logic: Base Load (28500) * (1 - 0.2) = 22800
    # Thermal savings from 24C (approx 15-20%) will lower it further.
    # We just need to check it is SIGNIFICANTLY lower than baseline.
    assert data["projected_kwh"] < 26000.0, \
        f"Auto-shedding failed. Expected < 26000, got {data['projected_kwh']}"

def test_carbon_override_respects_higher_user_input():
    """FAIL_TO_PASS: If user asks for 0.5 and grid is dirty, keep 0.5 (don't lower to 0.2)."""
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, 
        "reduction_factor": 0.5, 
        "grid_carbon_intensity": 0.95
    })
    data = res.json()
    
    # Should stay at ~50% reduction
    # 28500 * 0.5 = 14250 (ignoring thermal savings)
    assert data["projected_kwh"] < 15000.0, \
        f"User input overridden incorrectly. Expected < 15000, got {data['projected_kwh']}"

# ==========================================
# ✅ REGRESSION TESTS (PASS_TO_PASS) (1 Test)
# ==========================================

def test_regression_clean_grid_defaults():
    """PASS_TO_PASS: Clean grid should respect user input exactly."""
    # Use 22.0C setpoint to remove thermal noise (0 savings)
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0,
        "grid_carbon_intensity": 0.50 # Clean
    })
    data = res.json()
    # Should be exactly Base Load (28500)
    assert 28400 < data["projected_kwh"] < 28600, \
        f"Clean grid regression failed. Expected ~28500, got {data['projected_kwh']}"