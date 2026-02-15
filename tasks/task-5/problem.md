# Voltage Safety Protection (Surge & Brownout)

## Context
Standard grid voltage is 230V. Extreme deviations can damage the HVAC equipment. The system needs a "Safety Trip" mechanism.

## Requirements
1. **API & Service**: Update the backend to accept an optional `grid_voltage` (float).
2. **Optimizer Logic**:
   - Default `grid_voltage` to **230.0** V.
   - **Surge Protection (> 255V)**:
     - If voltage exceeds 255V, the system must trigger a **Safety Trip**.
     - Force `reduction_factor` to **1.0** (100% shutdown).
     - Set `grid_stability_score` to **0.0** (Critical Instability).
   - **Brownout Protection (< 200V)**:
     - If voltage drops below 200V, motors are at risk.
     - Force `reduction_factor` to be **at least 0.5** (50%).
     - Do not lower it if the user requested more (e.g., 0.8 stays 0.8).

## Edge Cases
- 230V input should behave normally.
- Surge takes priority over everything else.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`
