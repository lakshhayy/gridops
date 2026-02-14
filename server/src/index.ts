import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import simulationRoutes from './routes/simulation.routes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('tiny'));

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'online', service: 'gridops-api', version: '1.0.0' });
});

// Routes
app.use('/api/v1/simulation', simulationRoutes);

app.listen(PORT, () => {
  console.log(`🚀 GridOps API running on port ${PORT}`);
});