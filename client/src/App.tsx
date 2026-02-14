import { useState } from 'react';
import { SimulationForm } from './features/simulation/SimulationForm';
import { ResultsView } from './features/simulation/ResultsView';

function App() {
  const [results, setResults] = useState(null);

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 px-6 py-4">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <div className="w-3 h-3 bg-emerald-500 rounded-full" />
          GridOps
          <span className="text-xs bg-slate-100 px-2 py-0.5 rounded text-slate-500 font-normal">v1.0</span>
        </h1>
      </nav>

      <main className="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4">
          <SimulationForm onResult={setResults} />
        </div>
        <div className="lg:col-span-8">
          <ResultsView data={results} />
        </div>
      </main>
    </div>
  );
}

export default App;