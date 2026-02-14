import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { api } from '../../lib/api';
import { Loader2, Zap } from 'lucide-react';

interface SimulationInput {
  acTemp: number;
  reductionPercent: number;
  incentives: boolean;
}

export const SimulationForm = ({ onResult }: { onResult: (data: any) => void }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit } = useForm<SimulationInput>({
    defaultValues: { acTemp: 24, reductionPercent: 10, incentives: false }
  });

  const onSubmit = async (data: SimulationInput) => {
    try {
      setIsLoading(true);
      // Convert string inputs to numbers (common HTML form gotcha)
      const payload = {
        ...data,
        acTemp: Number(data.acTemp),
        reductionPercent: Number(data.reductionPercent)
      };
      
      const response = await api.post('/simulation/run', payload);
      onResult(response.data);
    } catch (error) {
      console.error("Simulation failed:", error);
      alert("Failed to run simulation. Check console for details.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
          <Zap size={20} />
        </div>
        <h2 className="text-xl font-semibold text-slate-800">Control Parameters</h2>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            HVAC Setpoint (°C)
          </label>
          <input
            type="number"
            {...register('acTemp')}
            className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 outline-none"
            min={16} max={30} step={0.5}
          />
          <p className="text-xs text-slate-500 mt-1">Recommended: 24°C (BEE Standard)</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Load Shedding (%)
          </label>
          <input
            type="range"
            {...register('reductionPercent')}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            min={0} max={50}
          />
        </div>

        <div className="flex items-center gap-2">
          <input 
            type="checkbox" 
            {...register('incentives')} 
            className="w-4 h-4 text-blue-600 rounded"
          />
          <label className="text-sm font-medium text-slate-700">
            Enable DR Incentives
          </label>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center items-center py-2.5 px-4 bg-slate-900 text-white rounded-md hover:bg-slate-800 transition-colors disabled:opacity-50"
        >
          {isLoading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
          {isLoading ? 'Calculating...' : 'Run Simulation'}
        </button>
      </form>
    </div>
  );
};