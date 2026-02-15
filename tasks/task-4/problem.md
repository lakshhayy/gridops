# Power Factor Correction (Penalties & Rebates)

## Context
Commercial electricity bills include surcharges for low "Power Factor" (PF), a measure of electrical efficiency. A PF below 0.90 strains the grid, while a PF above 0.95 aids it.

## Requirements
1. **API & Service**: Update the backend to accept an optional `power_factor` (float, 0.1 to 1.0).
2. **Optimizer Logic**:
   - Default `power_factor` to **0.90** (Neutral).
   - Calculate `base_cost` normally.
   - **Penalty Rule**: If `power_factor` < 0.90:
     - Increase cost by **1% for every 0.01 drop** below 0.90.
     - Formula: `Multiplier = 1 + (0.90 - pf)`.
   - **Rebate Rule**: If `power_factor` > 0.95:
     - Decrease cost by **0.5% for every 0.01 rise** above 0.95.
     - Formula: `Multiplier = 1 - ((pf - 0.95) * 0.5)`.
3. **Grid Stability**:
   - If `power_factor` < 0.85, limit `grid_stability_score` to a maximum of **0.6** (Unstable).

## Edge Cases
- PF of 0.90 to 0.95 results in no change (Multiplier 1.0).
- PF cannot exceed 1.0 or be negative.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`