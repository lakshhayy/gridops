# Carbon-Aware Load Shedding

## Context
The grid's carbon intensity fluctuates. When the grid is "dirty" (high coal usage), we should aggressively reduce load. Currently, `CARBON_INTENSITY` is a hardcoded constant.

## Requirements
1. **API & Service**: Update the backend to accept an optional `grid_carbon_intensity` (float) parameter.
2. **Optimizer Logic**: 
   - Accept `grid_carbon_intensity` in the calculation payload. 
   - If provided, use it instead of the default 0.82.
   - **Auto-Shedding Rule**: If `grid_carbon_intensity` > 0.90, ensure the `reduction_factor` is **at least 0.20** (20%), regardless of what the user requested.

## Edge Cases
- If `grid_carbon_intensity` is missing, default to 0.82.
- If the user requests 50% shedding (0.5) and the grid is dirty, keep 0.5 (since 0.5 > 0.2). Do not downgrade it.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`