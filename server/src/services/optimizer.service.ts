import axios from 'axios';

// Interface matching the Python Pydantic model
interface SimulationParams {
  ac_setpoint: number;
  reduction_factor: number;
  enable_incentives: boolean;
}

interface SimulationResult {
  projected_kwh: number;
  cost_estimate: number;
  carbon_footprint: number;
  comfort_index: number;
  grid_stability_score: number;
}

export class OptimizerService {
  private readonly baseUrl: string;

  constructor() {
    // Docker networking: 'optimizer' is the service name in docker-compose
    this.baseUrl = process.env.OPTIMIZER_URL || 'http://optimizer:8000';
  }

  async runSimulation(params: SimulationParams): Promise<SimulationResult> {
    try {
      const response = await axios.post<SimulationResult>(
        `${this.baseUrl}/calculate`, 
        params,
        { timeout: 5000 }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error(`Optimizer Service Error: ${error.message}`);
        throw new Error(`Calculation engine unavailable: ${error.code}`);
      }
      throw error;
    }
  }
}

export const optimizerService = new OptimizerService();
