"use client";

import React, { useState } from "react";
import { Cpu, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ColumnModule } from "./special/modules/ColumnModule";
import { PedagogicalStepsView } from "./PedagogicalStepsView";
import { MemorialHtmlView } from "./MemorialHtmlView";

interface ColumnLabViewProps {
  apiBaseUrl: string;
  onGoBack?: () => void;
}

export function ColumnLabView({ apiBaseUrl }: ColumnLabViewProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [showFullMemorial, setShowFullMemorial] = useState(false);

  const [colParams, setColParams] = useState({ 
    b: 0.40, h: 0.40, Nd: 1200, Mxd: 40, Myd: 15, L_free: 3.0, fck: 25, caa: 2 
  });

  const calculate = async () => {
    setLoading(true);
    const url = `${apiBaseUrl}/calculate/column`;
    const body = { 
      ...colParams, 
      Nd_kN: colParams.Nd, 
      Mxd_kNm: colParams.Mxd, 
      Myd_kNm: colParams.Myd, 
      n_floors_for_shortening: 10 
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
      console.error("Erro ao calcular pilar:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 py-4 max-w-7xl mx-auto px-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Pilares <span className="text-rose-500 italic">Lab</span></h2>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Mestre Structural Intelligence v5.0 • Dimensionamento NBR 6118</p>
        </div>
      </div>

      <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-2xl">
        <ColumnModule 
          colParams={colParams} 
          setColParams={setColParams} 
          result={result} 
          loading={loading} 
          calculate={calculate} 
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
