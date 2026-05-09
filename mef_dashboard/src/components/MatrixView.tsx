"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Grid3X3, Zap, Cpu, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

export function MatrixView() {
  const [matrix, setMatrix] = useState<number[][]>([]);
  const [assembling, setAssembling] = useState(false);
  const size = 8;

  useEffect(() => {
    // Generate empty matrix
    const empty = Array(size).fill(0).map(() => Array(size).fill(0));
    setMatrix(empty);
  }, []);

  const simulateAssembly = () => {
    setAssembling(true);
    let count = 0;
    const interval = setInterval(() => {
      setMatrix(prev => {
        const next = [...prev.map(row => [...row])];
        const r = Math.floor(Math.random() * size);
        const c = Math.floor(Math.random() * size);
        next[r][c] = Math.random() * 1000;
        return next;
      });
      count++;
      if (count > 40) {
        clearInterval(interval);
        setAssembling(false);
      }
    }, 50);
  };

  return (
    <div className="rounded-[2.5rem] bg-slate-100/60 border border-slate-200 backdrop-blur-xl p-8 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-10">
        <Grid3X3 className="w-32 h-32 text-blue-500" />
      </div>

      <div className="relative z-10 space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <span className="text-blue-500">$[K]$</span> Matriz de Rigidez Global
            </h3>
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">
              Montagem Matricial via MEF
            </p>
          </div>
          <button 
            onClick={simulateAssembly}
            disabled={assembling}
            className="px-6 py-2 rounded-xl bg-blue-600/10 border border-blue-500/30 text-blue-600 text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 hover:text-white transition-all disabled:opacity-50"
          >
            {assembling ? "Processando..." : "Simular Montagem"}
          </button>
        </div>

        <div className="grid grid-cols-8 gap-1.5 p-4 rounded-2xl bg-white/80 border border-slate-200 font-mono">
          {matrix.map((row, r) => (
            row.map((val, c) => (
              <motion.div
                key={`${r}-${c}`}
                initial={false}
                animate={{ 
                  backgroundColor: val > 0 ? "rgba(59, 130, 246, 0.2)" : "rgba(255, 255, 255, 0.02)",
                  borderColor: val > 0 ? "rgba(59, 130, 246, 0.4)" : "rgba(255, 255, 255, 0.05)"
                }}
                className={cn(
                  "h-10 flex items-center justify-center rounded-lg border text-[8px] transition-colors",
                  val > 0 ? "text-blue-600" : "text-slate-800"
                )}
              >
                {val > 0 ? val.toFixed(0) : "0"}
              </motion.div>
            ))
          ))}
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="p-4 rounded-2xl bg-white/5 border border-slate-200 space-y-2">
            <div className="flex items-center gap-2 text-slate-500">
              <Zap className="w-3 h-3" />
              <span className="text-[9px] font-black uppercase tracking-widest">Graus de Liberdade</span>
            </div>
            <p className="text-lg font-black text-slate-900">2.450 <span className="text-[10px] text-slate-600">DOF</span></p>
          </div>
          <div className="p-4 rounded-2xl bg-white/5 border border-slate-200 space-y-2">
            <div className="flex items-center gap-2 text-slate-500">
              <Cpu className="w-3 h-3" />
              <span className="text-[9px] font-black uppercase tracking-widest">Banda da Matriz</span>
            </div>
            <p className="text-lg font-black text-slate-900">142 <span className="text-[10px] text-slate-600">BW</span></p>
          </div>
          <div className="p-4 rounded-2xl bg-white/5 border border-slate-200 space-y-2">
            <div className="flex items-center gap-2 text-slate-500">
              <Activity className="w-3 h-3" />
              <span className="text-[9px] font-black uppercase tracking-widest">Condicionamento</span>
            </div>
            <p className="text-lg font-black text-slate-900">1.2e-4 <span className="text-[10px] text-slate-600">κ</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
