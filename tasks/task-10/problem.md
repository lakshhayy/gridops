# Maintenance Mode & Equipment Health Monitoring

## Context
Facility managers must occasionally take HVAC systems offline for maintenance. Additionally, as equipment ages, its thermodynamic efficiency (compressor performance) degrades.

## Requirements
1. **Optimizer Logic**: Update `optimizer/main.py` to accept two new optional parameters:
   - `maintenance_mode` (boolean, default: False)
   - `compressor_health` (float, 0.0 to 1.0, default: 1.0)
2. **Maintenance Override**:
   - If `maintenance_mode` is True, trigger a **Hard Shutdown**.
   - Force `effective_reduction` to **1.0** (100% shedding).
   - Set `comfort_index` to **0.0** (Building uninhabitable).
3. **Health-Based Efficiency**:
   - Equipment wear reduces cooling power.
   - Multiply the `effective_coeff` by the `compressor_health` value.
   - **Formula**: `final_coeff = effective_coeff * payload.compressor_health`.
4. **API Integration**: Update the Node.js backend to support these new fields.

## Edge Cases
- If `maintenance_mode` is True, safety takes priority over all other factors (carbon, frequency, etc.).
- `compressor_health` of 1.0 means perfect efficiency; 0.5 means 50% efficiency.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`