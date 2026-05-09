"use client";

import React, { useState } from "react";
import { Cpu, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { BeamModule } from "./special/modules/BeamModule";
import { PedagogicalStepsView } from "./PedagogicalStepsView";
import { MemorialHtmlView } from "./MemorialHtmlView";

interface BeamLabViewProps {
  apiBaseUrl: string;
  onGoBack?: () => void;
}

export function BeamLabView({ apiBaseUrl }: BeamLabViewProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [useClassical, setUseClassical] = useState(true);
  const [showFullMemorial, setShowFullMemorial] = useState(false);

  const [beamParams, setBeamParams] = useState({
    L: 6.0, b: 0.20, h: 0.50, q: 20.0, fck: 30, caa: 2, coverCm: 3.0,
    gammaF: 1.4, redistributionDelta: 0.90, nElements: 40,
    includeSelfWeight: true, pointLoads: [] as any[],
    distributedLoads: [] as any[], leftSupport: "pinned", rightSupport: "pinned",
    L_left: 0.0, L_right: 0.0, leftK: 10000, rightK: 10000, asymmetric_offset: 0.0
  });

  const calculate = async () => {
    setLoading(true);
    const url = `${apiBaseUrl}/calculate/beam`;
    const totalL = (Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0) + (Number(beamParams.L_right) || 0);
    const supports = [];
    
    if (beamParams.leftSupport !== "free") {
      supports.push({ 
        x: beamParams.L_left, 
        type: beamParams.leftSupport === "spring" ? "spring" : (beamParams.leftSupport === "fixed" ? "fixed" : "pinned"), 
        k_vertical: beamParams.leftK 
      });
    }
    if (beamParams.rightSupport !== "free") {
      supports.push({ 
        x: (Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0), 
        type: beamParams.rightSupport === "spring" ? "spring" : (beamParams.rightSupport === "fixed" ? "fixed" : "pinned"), 
        k_vertical: beamParams.rightK 
      });
    }

    const body = { 
      ...beamParams, 
      L: totalL, 
      supports, 
      distributed_loads: beamParams.distributedLoads.length > 0 
        ? beamParams.distributedLoads 
        : [{ x_start: 0, x_end: totalL, q_start: beamParams.q, q_end: beamParams.q }], 
      point_loads: beamParams.pointLoads, 
      n_elements: beamParams.nElements, 
      include_self_weight: beamParams.includeSelfWeight 
    };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Erro ao calcular viga:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 py-4 max-w-7xl mx-auto px-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Vigas <span className="text-amber-500 italic">Lab</span></h2>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Mestre Structural Intelligence v5.0 • Dimensionamento NBR 6118</p>
        </div>
      </div>

      <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-2xl">
        <BeamModule 
          beamParams={beamParams} 
          setBeamParams={setBeamParams} 
          result={result} 
          loading={loading} 
          calculate={calculate} 
          useClassical={useClassical} 
          setUseClassical={setUseClassical} 
          setShowFullMemorial={setShowFullMemorial} 
        />
        
        <AnimatePresence>
          {result?.pedagogical_steps && !showFullMemorial && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-8">
              <PedagogicalStepsView steps={result.pedagogical_steps} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {showFullMemorial && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/90 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50 rounded-t-3xl">
              <h3 className="font-black text-xl text-slate-900">Memorial de Cálculo • NBR 6118</h3>
              <button onClick={() => setShowFullMemorial(false)} className="px-4 py-2 bg-slate-900 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-slate-800 transition-colors">Fechar</button>
            </div>
            <div className="flex-1 overflow-y-auto p-8 bg-[#fdfdfd]">
               <MemorialHtmlView htmlContent={result?.pedagogical_steps_html || result?.memorial_html || "<p>Memorial em processamento...</p>"} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
