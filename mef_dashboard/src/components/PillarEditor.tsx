"use client";

import React from 'react';
import { Plus, Trash2, MapPin, Weight } from 'lucide-react';

export interface Pillar {
  id: string;
  x: number;
  y: number;
  p_kN: number;
  bx?: number;
  by?: number;
  support_type?: "pinned" | "fixed" | "spring";
  k_spring?: number;
}

interface PillarEditorProps {
  pillars: Pillar[];
  setPillars: React.Dispatch<React.SetStateAction<Pillar[]>>;
}

export const PillarEditor: React.FC<PillarEditorProps> = ({ pillars, setPillars }) => {
  
  const addPillar = () => {
    const newId = `P${(pillars.length + 1).toString().padStart(2, '0')}`;
    setPillars([...pillars, { id: newId, x: 5.0, y: 5.0, p_kN: 1500.0 }]);
  };

  const removePillar = (index: number) => {
    setPillars(pillars.filter((_, i) => i !== index));
  };

  const updatePillar = (index: number, field: 'x' | 'y' | 'p_kN', value: number) => {
    const newPillars = [...pillars];
    newPillars[index] = { ...newPillars[index], [field]: value };
    setPillars(newPillars);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-lg">Locação e Cargas de Pilares</h3>
        <button 
          onClick={addPillar}
          className="flex items-center gap-2 px-3 py-1.5 bg-blue-600/10 text-apple-blue rounded-full text-xs font-bold hover:bg-blue-600/20 transition-all"
        >
          <Plus className="w-3.5 h-3.5" /> ADICIONAR PILAR
        </button>
      </div>

      <div className="max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
        <table className="w-full text-left border-separate border-spacing-y-2">
          <thead>
            <tr className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
              <th className="pb-2 pl-4">ID</th>
              <th className="pb-2">X (m)</th>
              <th className="pb-2">Y (m)</th>
              <th className="pb-2">Carga (kN)</th>
              <th className="pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {pillars.map((pillar, index) => (
              <tr key={index} className="bg-white/40 backdrop-blur-sm rounded-xl overflow-hidden group transition-all hover:bg-white/60">
                <td className="py-3 pl-4 font-bold text-sm rounded-l-xl border-y border-l border-white/40">{pillar.id}</td>
                <td className="py-3 border-y border-white/40">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3 h-3 text-slate-600 opacity-50" />
                    <input 
                      type="number" 
                      value={pillar.x} 
                      onChange={(e) => updatePillar(index, 'x', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </div>
                </td>
                <td className="py-3 border-y border-white/40">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3 h-3 text-slate-600 opacity-50" />
                    <input 
                      type="number" 
                      value={pillar.y} 
                      onChange={(e) => updatePillar(index, 'y', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </div>
                </td>
                <td className="py-3 border-y border-white/40">
                  <div className="flex items-center gap-2">
                    <Weight className="w-3 h-3 text-apple-blue opacity-50" />
                    <input 
                      type="number" 
                      value={pillar.p_kN} 
                      onChange={(e) => updatePillar(index, 'p_kN', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-20 text-sm focus:ring-0 font-bold text-apple-blue"
                    />
                  </div>
                </td>
                <td className="py-3 pr-4 text-right rounded-r-xl border-y border-r border-white/40">
                  <button 
                    onClick={() => removePillar(index)}
                    className="p-1.5 text-red-500/40 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
