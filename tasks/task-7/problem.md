# Humidity-Dependent Load Optimization

## Context
The current thermodynamic model only considers dry-bulb temperature. In high-humidity environments, HVAC systems must work harder to remove moisture (latent heat), which increases energy consumption even if the temperature setpoint is unchanged.

## Requirements
1. **Optimizer Logic**: Update `optimizer/main.py` to accept an optional `relative_humidity` (float, 0-100, default: 60.0).
2. **Efficiency Rule**:
   - The base `THERMAL_COEFF` (0.085) assumes a relative humidity of 60% or less.
   - For every 1% of humidity above **60%**, the system efficiency drops by 1%.
   - **Formula**: `effective_coeff = THERMAL_COEFF / (1 + (max(0, humidity - 60) * 0.01))`.
3. **API Integration**: Update the Node.js backend (`server/src/services/optimizer.service.ts` and `server/src/routes/simulation.routes.ts`) to accept and pass `relativeHumidity` to the optimizer.

## Edge Cases
- If `relative_humidity` is missing or ≤ 60.0, use the base `THERMAL_COEFF` (0.085).
- Input must be capped between 0 and 100.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`