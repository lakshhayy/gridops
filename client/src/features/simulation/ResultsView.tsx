import { Leaf, DollarSign, Thermometer } from 'lucide-react';

interface ResultData {
  projected_kwh: number;
  cost_estimate: number;
  carbon_footprint: number;
  comfort_index: number;
}

export const ResultsView = ({ data }: { data: ResultData | null }) => {
  if (!data) {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-slate-50 rounded-lg border border-dashed border-slate-300">
        <p className="text-slate-500">Configure parameters to generate a forecast.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard 
        label="Est. Cost (INR)" 
        value={`₹${data.cost_estimate.toLocaleString()}`} 
        icon={<DollarSign className="text-emerald-600" />} 
        bg="bg-emerald-50"
      />
      <StatCard 
        label="Carbon Footprint" 
        value={`${data.carbon_footprint} kg`} 
        icon={<Leaf className="text-green-600" />} 
        bg="bg-green-50"
      />
      <StatCard 
        label="Comfort Score" 
        value={(data.comfort_index * 100).toFixed(1) + '%'} 
        icon={<Thermometer className="text-orange-600" />} 
        bg="bg-orange-50"
      />
    </div>
  );
};

const StatCard = ({ label, value, icon, bg }: any) => (
  <div className="p-4 bg-white rounded-lg shadow-sm border border-slate-100">
    <div className={`w-10 h-10 ${bg} rounded-full flex items-center justify-center mb-3`}>
      {icon}
    </div>
    <p className="text-sm text-slate-500 font-medium">{label}</p>
    <p className="text-2xl font-bold text-slate-900">{value}</p>
  </div>
);