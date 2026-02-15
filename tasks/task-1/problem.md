# Dynamic Time-of-Use (TOU) Tariff Integration

## Context
The current `GridOps` optimization engine relies on static constants for energy pricing (fixed at 12.50 INR). In real-world utility scenarios, tariffs are dynamic based on peak-load times. 

## Requirements
Modify the system to support a Time-of-Use (TOU) pricing model.

1. **Optimizer Logic**: Update the Python engine (`optimizer/main.py`) to parse an ISO 8601 `timestamp` and apply:
   - **Peak (14:00-20:00)**: 14.50 INR/kWh
   - **Standard (08:00-14:00, 20:00-23:00)**: 10.00 INR/kWh
   - **Off-Peak (23:00-08:00)**: 6.50 INR/kWh
   
2. **API Integration**: Update the Node.js backend (`server/src/routes/simulation.routes.ts` and `server/src/services/optimizer.service.ts`) to accept a `simulationTime` field from the client and pass it to the optimizer.

## Edge Cases
- **Missing Timestamp**: If no timestamp is provided, the system must default to "Standard" rates (10.00 INR/kWh) or the current server time logic.
- **Invalid Format**: The system should handle standard ISO strings.

## files_to_change
- `optimizer/main.py`
- `server/src/services/optimizer.service.ts`
- `server/src/routes/simulation.routes.ts`