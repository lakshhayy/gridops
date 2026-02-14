import { Router, Request, Response } from 'express';
import { optimizerService } from '../services/optimizer.service';
import { db } from '../db'; // We will create this next
import { simulationLogs } from '../db/schema';
import { z } from 'zod';

const router = Router();

// Validation schema
const SimulationSchema = z.object({
  acTemp: z.number().min(16).max(32),
  reductionPercent: z.number().min(0).max(100),
  incentives: z.boolean().optional()
});

router.post('/run', async (req: Request, res: Response) => {
  try {
    const payload = SimulationSchema.parse(req.body);

    const result = await optimizerService.runSimulation({
      ac_setpoint: payload.acTemp,
      reduction_factor: payload.reductionPercent / 100,
      enable_incentives: payload.incentives || false
    });

    // Async logging (fire and forget)
    db.insert(simulationLogs).values({
      user_id: 'demo-user',
      ac_setpoint: payload.acTemp,
      reduction_factor: payload.reductionPercent / 100,
      projected_savings_inr: result.cost_estimate,
      carbon_reduction_kg: result.carbon_footprint,
      comfort_score: result.comfort_index
    }).then(() => console.log('Simulation logged to DB')).catch(err => console.error('DB Log failed', err));

    res.json(result);

  } catch (error) {
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid parameters', details: error.errors });
    } else {
      console.error(error);
      res.status(503).json({ error: 'Simulation service currently unavailable' });
    }
  }
});

export default router;