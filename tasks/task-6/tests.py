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

def test_structural_battery_fields():
    """STRUCTURAL: Verify battery fields exist in model."""
    fields = SimulationRequest.model_fields
    assert "battery_capacity" in fields
    assert "current_charge" in fields

def test_structural_arbitrage_thresholds():
    """STRUCTURAL: Verify the 9.0 and 12.0 tariff thresholds exist."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    assert "9.0" in content, "Charge threshold 9.0 not found"
    assert "12.0" in content, "Discharge threshold 12.0 not found"

# ==========================================
# BEHAVIORAL TESTS (FAIL_TO_PASS)
# ==========================================

def test_battery_charge_logic():
    """FAIL_TO_PASS: Off-peak (6.50 INR) should trigger CHARGING (Increase Load)."""
    # 4 AM is Off-Peak (< 9.0 INR). Battery should charge.
    # Battery 50kWh @ 0.5C = 25kW charging load.
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "timestamp": "2024-06-15T04:00:00", # Off-peak
        "battery_capacity": 50.0,
        "current_charge": 50.0
    })
    data = res.json()
    
    # Base Load (28500) + Charge Load (25) = 28525
    # Just verify it is HIGHER than base load
    assert data["projected_kwh"] > 28500.0, "Battery did not increase load during charge cycle"

def test_battery_discharge_logic():
    """FAIL_TO_PASS: Peak (14.50 INR) should trigger DISCHARGING (Decrease Load)."""
    # 16:00 is Peak (> 12.0 INR). Battery should discharge.
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "timestamp": "2024-06-15T16:00:00", # Peak
        "battery_capacity": 50.0,
        "current_charge": 50.0
    })
    data = res.json()
    
    # Base Load (28500) - Discharge (25) = 28475
    assert data["projected_kwh"] < 28500.0, "Battery did not decrease load during discharge cycle"

# ==========================================
# REGRESSION TESTS
# ==========================================

def test_regression_no_battery():
    """PASS_TO_PASS: No battery capacity should behave normally."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0,
        "reduction_factor": 0.0,
        "battery_capacity": 0.0
    })
    data = res.json()
    assert 28400 < data["projected_kwh"] < 28600