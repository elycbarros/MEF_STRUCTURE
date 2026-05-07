"use client";

import React from 'react';
import { Plus, Trash2, Maximize, Minimize } from 'lucide-react';

export interface Hole {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

interface HoleEditorProps {
  holes: Hole[];
  setHoles: React.Dispatch<React.SetStateAction<Hole[]>>;
  slabType?: string;
}

export const HoleEditor: React.FC<HoleEditorProps> = ({ holes, setHoles, slabType = "solid" }) => {
  
  const addHole = () => {
    setHoles([...holes, { x_min: 2.0, y_min: 2.0, x_max: 4.0, y_max: 4.0 }]);
  };

  const removeHole = (index: number) => {
    setHoles(holes.filter((_, i) => i !== index));
  };

  const updateHole = (index: number, field: keyof Hole, value: number) => {
    const newHoles = [...holes];
    newHoles[index] = { ...newHoles[index], [field]: value };
    setHoles(newHoles);
  };

  const getSlabWarning = () => {
    if (slabType === "hollow_core") {
      return {
        title: "RESTRIÇÃO NORMATIVA: Laje Alveolar",
        text: "NBR 14861: Proibido seccionar almas longitudinais. Furos devem ser limitados à largura dos alvéolos (eixos neutros) e não devem exceder 1/3 da largura da placa sem reforço estrutural.",
        color: "text-red-700 bg-red-50 border-red-200"
      };
    }
    if (slabType === "prestressed") {
      return {
        title: "AÇÃO CRÍTICA: Laje Protendida",
        text: "RISCO DE MORTE: Proibido executar furos sem mapeamento radiográfico ou eletromagnético dos cabos de protensão. O corte de uma cordoalha pode causar colapso progressivo imediato.",
        color: "text-white bg-red-600 border-red-800 shadow-lg animate-pulse"
      };
    }
    if (slabType === "ribbed") {
      return {
        title: "GUARDREIO TÉCNICO: Laje Nervurada",
        text: "NBR 6118 §13.2.5: Furos devem situar-se preferencialmente na mesa (zona de tração). O corte de nervuras exige viga de reforço ou análise de redistribuição de esforços.",
        color: "text-blue-700 bg-blue-50 border-blue-200"
      };
    }
    if (slabType === "trussed") {
      return {
        title: "LIMITAÇÃO EXECUTIVA: Laje Treliçada",
        text: "NBR 14859: Furos não podem interromper as vigotas treliçadas principais. Aberturas maiores que a distância entre eixos (e) exigem interrupção com reforço de viga transversal.",
        color: "text-emerald-700 bg-emerald-50 border-emerald-200"
      };
    }
    return null;
  };

  const warning = getSlabWarning();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-lg text-slate-800">Furos e Aberturas</h3>
          <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tight">Geometria Retangular</p>
        </div>
        <button 
          onClick={addHole}
          className="flex items-center gap-2 px-3 py-1.5 bg-orange-500/10 text-orange-600 rounded-full text-xs font-bold hover:bg-orange-500/20 transition-all border border-orange-200"
        >
          <Plus className="w-3.5 h-3.5" /> ADICIONAR FURO
        </button>
      </div>

      {warning && (
        <div className={`p-3 rounded-xl border text-[11px] font-bold ${warning.color} flex flex-col gap-0.5`}>
          <span className="uppercase tracking-wide opacity-80">{warning.title}</span>
          <span className="opacity-90">{warning.text}</span>
        </div>
      )}

      <div className="max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
        {holes.length === 0 ? (
          <div className="py-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
            <p className="text-xs text-slate-400 font-medium">Nenhuma abertura definida para este modelo.</p>
          </div>
        ) : (
          <table className="w-full text-left border-separate border-spacing-y-2">
            <thead>
              <tr className="text-[10px] font-black text-apple-muted uppercase tracking-widest">
                <th className="pb-2 pl-4">#</th>
                <th className="pb-2">X Mín (m)</th>
                <th className="pb-2">Y Mín (m)</th>
                <th className="pb-2">X Máx (m)</th>
                <th className="pb-2">Y Máx (m)</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {holes.map((hole, index) => (
                <tr key={index} className="bg-white/40 backdrop-blur-sm rounded-xl overflow-hidden group transition-all hover:bg-white/60">
                  <td className="py-3 pl-4 font-bold text-sm rounded-l-xl border-y border-l border-white/40 text-slate-400">{index + 1}</td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={hole.x_min} 
                      onChange={(e) => updateHole(index, 'x_min', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={hole.y_min} 
                      onChange={(e) => updateHole(index, 'y_min', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={hole.x_max} 
                      onChange={(e) => updateHole(index, 'x_max', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 border-y border-white/40">
                    <input 
                      type="number" 
                      value={hole.y_max} 
                      onChange={(e) => updateHole(index, 'y_max', parseFloat(e.target.value))}
                      className="bg-transparent border-none w-16 text-sm focus:ring-0 font-medium"
                    />
                  </td>
                  <td className="py-3 pr-4 text-right rounded-r-xl border-y border-r border-white/40">
                    <button 
                      onClick={() => removeHole(index)}
                      className="p-1.5 text-apple-red/40 hover:text-apple-red transition-colors"
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
