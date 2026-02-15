import pytest
import ast
import json
from fastapi.testclient import TestClient
import sys
import os

# Setup path to import optimizer
sys.path.append(os.path.join(os.path.dirname(__file__), '../../optimizer'))
from main import app, SimulationRequest

client = TestClient(app)

# ==========================================
# 🏗️ STRUCTURAL TESTS (4 Tests - 66%)
# ==========================================

def test_structural_request_model_has_timestamp():
    """STRUCTURAL: Verify SimulationRequest model has a 'timestamp' field."""
    fields = SimulationRequest.model_fields
    assert "timestamp" in fields, "SimulationRequest model is missing the 'timestamp' field"

def test_structural_datetime_import():
    """STRUCTURAL: Verify 'datetime' is imported in main.py logic."""
    with open("optimizer/main.py", "r") as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'datetime':
            imports.append('datetime')
        elif isinstance(node, ast.Import) and any(n.name == 'datetime' for n in node.names):
            imports.append('datetime')
            
    assert len(imports) > 0, "The 'datetime' module is not imported in main.py"

def test_structural_tariff_constants():
    """STRUCTURAL: Verify new pricing constants (14.50, 6.50) are present in source."""
    with open("optimizer/main.py", "r") as f:
        content = f.read()
    
    assert "14.5" in content, "Peak rate constant (14.50) not found in optimizer/main.py"
    assert "6.5" in content, "Off-peak rate constant (6.50) not found in optimizer/main.py"

def test_structural_backend_service_interface():
    """STRUCTURAL: Verify Node.js service interface includes timestamp."""
    with open("server/src/services/optimizer.service.ts", "r") as f:
        ts_content = f.read()
    
    assert "timestamp" in ts_content, \
        "optimizer.service.ts interface was not updated to accept a timestamp"

# ==========================================
# 🧪 BEHAVIORAL TESTS (FAIL_TO_PASS) (2 Tests)
# ==========================================

def test_peak_pricing_logic():
    """FAIL_TO_PASS: Verify 16:00 timestamp triggers Peak pricing (14.50 INR)."""
    # 16:00 is Peak Hours
    # We use ac_setpoint=22.0 to ensure 0% thermal savings, so cost = Base Load * Rate
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0, 
        "timestamp": "2024-06-15T16:00:00"
    })
    assert res.status_code == 200
    data = res.json()
    
    # Calculation: 28500 kWh * 14.50 = 413,250
    assert 413000 < data["cost_estimate"] < 414000, \
        f"Peak pricing failed. Expected ~413,250, got {data['cost_estimate']}"

def test_off_peak_pricing_logic():
    """FAIL_TO_PASS: Verify 04:00 timestamp triggers Off-Peak pricing (6.50 INR)."""
    # 04:00 is Off-Peak
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0, 
        "timestamp": "2024-06-15T04:00:00"
    })
    assert res.status_code == 200
    data = res.json()
    
    # Calculation: 28500 kWh * 6.50 = 185,250
    assert 185000 < data["cost_estimate"] < 186000, \
        f"Off-Peak pricing failed. Expected ~185,250, got {data['cost_estimate']}"

# ==========================================
# ✅ REGRESSION TESTS (PASS_TO_PASS) (1 Test)
# ==========================================

def test_regression_no_timestamp_defaults():
    """PASS_TO_PASS: Verify system defaults to Standard rates if timestamp is missing."""
    res = client.post("/calculate", json={
        "ac_setpoint": 22.0, 
        "reduction_factor": 0.0
        # No timestamp provided
    })
    assert res.status_code == 200
    data = res.json()
    # Standard Rate (10.00) -> 285,000
    assert 284000 < data["cost_estimate"] < 286000, \
        f"Default/Fallback pricing failed. Expected ~285,000, got {data['cost_estimate']}"