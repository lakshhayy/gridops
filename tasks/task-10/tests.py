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

def test_structural_maintenance_fields():
    """STRUCTURAL: Verify maintenance and health fields exist in model."""
    assert "maintenance_mode" in SimulationRequest.model_fields
    assert "compressor_health" in SimulationRequest.model_fields

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_maintenance_mode_shutdown():
    """FAIL_TO_PASS: Maintenance mode must force 0 load and 0 comfort."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0, 
        "maintenance_mode": True
    })
    data = res.json()
    assert data["projected_kwh"] == 0.0
    assert data["comfort_index"] == 0.0

def test_equipment_health_efficiency_drop():
    """FAIL_TO_PASS: Lower compressor health should result in higher energy consumption."""
    # Healthy Compressor (1.0)
    res_healthy = client.post("/calculate", json={
        "ac_setpoint": 26.0, "reduction_factor": 0.0, "compressor_health": 1.0
    })
    
    # Failing Compressor (0.7)
    res_failing = client.post("/calculate", json={
        "ac_setpoint": 26.0, "reduction_factor": 0.0, "compressor_health": 0.7
    })
    
    # A failing compressor is less efficient at saving energy, resulting in higher consumption
    assert res_failing.json()["projected_kwh"] > res_healthy.json()["projected_kwh"]

# ==========================================
# REGRESSION TESTS
# ==========================================

def test_regression_normal_operation():
    """PASS_TO_PASS: Verify standard operation with default health/maintenance."""
    res = client.post("/calculate", json={
        "ac_setpoint": 24.0, "reduction_factor": 0.0
    })
    assert res.status_code == 200