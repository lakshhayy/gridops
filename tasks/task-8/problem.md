# Occupancy-Based Dynamic Comfort Index

## Context
Fixed comfort penalties don't reflect actual building usage. A high temperature or aggressive load shedding is more acceptable when the building is nearly empty than when it is at full capacity.

## Requirements
1. **Optimizer Logic**: Update `optimizer/main.py` to accept an optional `occupancy_count` (integer, default: 20).
2. **Comfort Adjustments**:
   - **Low Occupancy (< 10 people)**: Users are less likely to notice load shedding. Reduce the `reduction_factor` comfort penalty by **50%**.
   - **High Occupancy (> 50 people)**: Density increases heat perception. **Double** the `ac_setpoint` comfort penalty.
3. **API Integration**: Update the Node.js backend (`server/src/services/optimizer.service.ts` and `server/src/routes/simulation.routes.ts`) to accept and pass `occupancyCount` to the optimizer.

## Edge Cases
- If `occupancy_count` is between 10 and 50, use the standard comfort calculation.
- Ensure `occupancy_count` is non-negative.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`