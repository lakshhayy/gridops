# Battery Energy Storage System (BESS) Arbitrage

## Context
Commercial buildings use batteries to lower costs by "Arbitrage": charging when electricity is cheap and discharging when it is expensive.

## Requirements
1. **API & Service**: Accept `battery_capacity` (kWh) and `current_charge` (%).
2. **Optimizer Logic**:
   - Default `battery_capacity` = 0.0 (No battery).
   - **Arbitrage Logic**:
     - **Charge Mode**: If `current_tariff` < 9.0 INR:
       - The battery charges at max rate (assume 0.5C rate).
       - **ADD** this energy to the `final_load`.
     - **Discharge Mode**: If `current_tariff` > 12.0 INR:
       - The battery discharges.
       - **SUBTRACT** this energy from the `final_load`.
     - **Idle Mode**: Otherwise, do nothing.

## Technical Constraints
- Max Charge/Discharge Rate = `battery_capacity * 0.5`.
- Ensure `final_load` never drops below 0 (even if battery discharge > building load).

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`