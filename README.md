# GridOps

**GridOps** is a facility energy management and decision-support system. It integrates real-time telemetry with a Python-based physics engine to simulate the impact of load-shedding policies on building thermal comfort and operational costs.

## Architecture

The system follows a microservices pattern:

- **Core API (Node.js/TypeScript):** Handles data ingestion, user management, and orchestration.
- **Optimizer (Python/FastAPI):** Performs thermodynamic calculations and cost modelling.
- **Frontend (React/Vite):** Admin dashboard for policy simulation and monitoring.
- **PostgreSQL:** Time-series data persistence.

## Development

### Prerequisites
- Docker & Docker Compose
- Node.js 20+

### Quick Start

1. Start the infrastructure:
   ```bash
   docker-compose up --build