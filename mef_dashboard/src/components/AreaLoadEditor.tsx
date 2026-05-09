"use client";

import React from 'react';
import { Plus, Trash2, Zap } from 'lucide-react';

export interface AreaLoad {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  q_kN: number;
}

interface AreaLoadEditorProps {
  areaLoads: AreaLoad[];
  setAreaLoads: React.Dispatch<React.SetStateAction<AreaLoad[]>>;
}

export const AreaLoadEditor: React.FC<AreaLoadEditorProps> = ({ areaLoads, setAreaLoads }) => {
  
  const addAreaLoad = () => {
    setAreaLoads([...areaLoads, { x_min: 5.0, y_min: 5.0, x_max: 10.0, y_max: 10.0, q_kN: 5.0 }]);
  };

  const removeAreaLoad = (index: number) => {
    setAreaLoads(areaLoads.filter((_, i) => i !== index));
  };

  const updateAreaLoad = (index: number, field: keyof AreaLoad, value: number) => {
    const newLoads = [...areaLoads];
    newLoads[index] = { ...newLoads[index], [field]: value };
    setAreaLoads(newLoads);
  };

  return (
    <div className="space-y-4 pt-6 border-t border-slate-100">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-lg text-slate-800">Cargas de Área (Sobrecargas Extra)</h3>
          <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tight">Distribuição Retangular</p>
        </div>
        <button 
          onClick={addAreaLoad}
          className="flex items-center gap-2 px-3 py-1.5 bg-indigo-500/10 text-indigo-600 rounded-full text-xs font-bold hover:bg-indigo-500/20 transition-all border border-indigo-200"
        >
          <Plus className="w-3.5 h-3.5" /> ADICIONAR CARGA
        </button>
      </div>

      <div className="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
        {areaLoads.length === 0 ? (
          <div className="py-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
            <p className="text-xs text-slate-600 font-medium">Nenhuma carga de área adicional definida.</p>
          </div>
        ) : (
          <table className="w-full text-left border-separate border-spacing-y-2">
            <thead>
              <tr className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
                <th className="pb-2 pl-4">#</th>
                <th className="pb-2">X Mín (m)</th>
                <th className="pb-2">Y Mín (m)</th>
                <th className="pb-2">X Máx (m)</th>
                <th className="pb-2">Y Máx (m)</th>
                <th className="pb-2">q (kN/m²)</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {areaLoads.map((load, index) => (
                <tr key={index} className="bg-white/40 backdrop-blur-sm rounded-xl overflow-hidden group transition-all hover:bg-white/60">
                  <td className="py-3 pl-4 font-bold text-sm rounded-l-xl border-y border-l border-white/40 text-indigo-400">
                    <Zap className="w-3 h-3 inline mr-1" />
                    {index + 1}
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={load.x_min} 
                      onChange={(e) => updateAreaLoad(index, 'x_min', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={load.y_min} 
                      onChange={(e) => updateAreaLoad(index, 'y_min', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={load.x_max} 
                      onChange={(e) => updateAreaLoad(index, 'x_max', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={load.y_max} 
                      onChange={(e) => updateAreaLoad(index, 'y_max', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={load.q_kN} 
                      onChange={(e) => updateAreaLoad(index, 'q_kN', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-20 text-sm focus:ring-0 font-bold text-indigo-600"
                    />
                  </td>
                  <td className="py-3 pr-4 text-right rounded-r-xl border-y border-r border-white/40">
                    <button 
                      onClick={() => removeAreaLoad(index)}
                      className="p-1.5 text-red-500/40 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
