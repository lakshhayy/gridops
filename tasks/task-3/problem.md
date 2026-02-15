# Grid Frequency Response (Ancillary Services)

## Context
Grid stability relies on maintaining a frequency of 50 Hz. If frequency drops below **49.8 Hz**, it indicates a severe supply shortage. In this scenario, large consumers must immediately shed load to prevent a blackout.

## Requirements
1. **API & Service**: Update the backend to accept an optional `grid_frequency` (float) parameter.
2. **Optimizer Logic**:
   - Accept `grid_frequency` in the payload (default: 50.0).
   - **Emergency Rule**: If `grid_frequency` < 49.8 Hz, the system must enter **Emergency Mode**:
     - Force `reduction_factor` to **0.50** (50%), ignoring the user's `reduction_factor`.
     - This override happens *before* any other calculations.

## Edge Cases
- If `grid_frequency` is 49.8 or higher, use the user's requested reduction.
- If `grid_frequency` is missing, default to 50.0 Hz (Healthy).

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`