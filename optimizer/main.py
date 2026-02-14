import logging
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import numpy as np

# Configure structured logging for container observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gridops-optimizer")

app = FastAPI(
    title="GridOps Optimization Engine",
    version="1.0.0",
    docs_url="/docs"
)

# --- Domain Models ---

class SimulationRequest(BaseModel):
    ac_setpoint: float = Field(..., ge=16.0, le=32.0, description="Target HVAC temperature in Celsius")
    reduction_factor: float = Field(..., ge=0.0, le=1.0, description="Load shedding percentage (0-1)")
    enable_incentives: bool = Field(default=False, description="Apply DISCOM demand response rebates")

class SimulationResponse(BaseModel):
    projected_kwh: float
    cost_estimate: float
    carbon_footprint: float
    comfort_index: float
    grid_stability_score: float

# --- Physics Constants (Delhi NCR Region) ---
# Baseline assumes a 50,000 sqft commercial facility
BASE_LOAD_KWH = 28500.0  
THERMAL_COEFF = 0.085    # ~8.5% energy delta per degree C (ASHRAE approximation)
CARBON_INTENSITY = 0.82  # kgCO2/kWh (Grid India average)
PEAK_TARIFF = 12.50      # INR/kWh
OFF_PEAK_TARIFF = 8.50   # INR/kWh

@app.get("/health")
async def health_check():
    """K8s/Docker health probe endpoint."""
    return {"status": "healthy", "service": "optimizer"}

@app.post("/calculate", response_model=SimulationResponse)
async def calculate_impact(payload: SimulationRequest):
    try:
        logger.info(f"Processing simulation for setpoint: {payload.ac_setpoint}C")

        # 1. Thermal Load Calculation
        # Using simplified Degree-Day method. Baseline assumed at 22C.
        # Physics: Q = U * A * Delta T
        delta_t = max(0, payload.ac_setpoint - 22.0)
        
        # Non-linear savings curve (diminishing returns > 26C)
        # Using numpy for efficient calculation
        thermal_savings_pct = np.tanh(delta_t * THERMAL_COEFF)
        
        # 2. Load Shedding Impact
        shedding_savings = BASE_LOAD_KWH * payload.reduction_factor
        thermal_savings = BASE_LOAD_KWH * thermal_savings_pct
        
        total_savings_kwh = thermal_savings + shedding_savings
        final_load = max(0, BASE_LOAD_KWH - total_savings_kwh)

        # 3. Financial Modeling
        # Blended rate assumption (60% peak / 40% off-peak)
        blended_rate = (PEAK_TARIFF * 0.6) + (OFF_PEAK_TARIFF * 0.4)
        base_cost = final_load * blended_rate
        
        dr_rebate = 5000.0 if payload.enable_incentives else 0.0
        final_cost = max(0, base_cost - dr_rebate)

        # 4. Comfort Index Calculation (ASHRAE 55 simplified)
        # 1.0 = Perfect, 0.0 = Uninhabitable
        comfort_penalty = 0.0
        
        if payload.ac_setpoint > 24.0:
            # Exponential penalty for high temps
            comfort_penalty += ((payload.ac_setpoint - 24.0) ** 1.5) * 0.08
            
        if payload.reduction_factor > 0.15:
            # Linear penalty for aggressive shedding
            comfort_penalty += (payload.reduction_factor - 0.15) * 2.5
            
        comfort_score = max(0.1, 1.0 - comfort_penalty)

        return {
            "projected_kwh": round(float(final_load), 2),
            "cost_estimate": round(float(final_cost), 2),
            "carbon_footprint": round(float(final_load * CARBON_INTENSITY), 2),
            "comfort_index": round(float(comfort_score), 3),
            "grid_stability_score": round(0.85 + (payload.reduction_factor * 0.15), 3)
        }

    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Optimization engine computation error"
        )