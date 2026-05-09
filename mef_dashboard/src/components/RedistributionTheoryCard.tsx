"use client";

import React from "react";
import { motion } from "framer-motion";
import { BlockMath } from "react-katex";
import { Info, Target, Zap, AlertCircle } from "lucide-react";

export default function RedistributionTheoryCard() {
  return (
    <div className="rounded-[2.5rem] border border-slate-200 bg-white/80 p-10 shadow-2xl backdrop-blur-xl relative overflow-hidden group">
      {/* Decoration */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-amber-500/5 blur-[80px] rounded-full group-hover:bg-amber-500/10 transition-colors" />
      
      <div className="flex items-center gap-6 mb-10 relative z-10">
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 shadow-lg shadow-amber-500/10">
          <Target className="w-8 h-8" />
        </div>
        <div>
          <h3 className="text-2xl font-black text-slate-900 tracking-tighter uppercase">Redistribuição de Esforços (<span className="font-serif">δ</span>)</h3>
          <p className="text-[10px] font-black text-amber-500/60 uppercase tracking-[0.3em] mt-2">NBR 6118:2023 — ITEM 14.7.4 | DUCTILIDADE LIMITADA</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 relative z-10">
        <div className="space-y-8">
          <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-slate-200 leading-relaxed">
            <p className="text-sm text-slate-600 leading-relaxed font-medium">
              A redistribuição de momentos é um recurso que aproveita a <strong className="text-slate-900">ductilidade</strong> do concreto armado para reduzir os picos de momentos negativos nos apoios, transferindo parte desses esforços para o vão.
            </p>
          </div>

          <div className="bg-white/60 p-8 rounded-[2rem] border border-amber-500/10 shadow-2xl relative overflow-hidden group/formula">
             <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-amber-500/50 to-transparent" />
             <p className="text-[9px] font-black text-amber-500 uppercase tracking-widest mb-6">Equação de Ajuste de Rigidez:</p>
             <div className="scale-110 py-4 text-slate-900">
               <BlockMath math="M_{design} = \delta \cdot M_{elastic}" />
             </div>
             <div className="mt-8 space-y-3 font-mono">
               <div className="flex justify-between items-center text-[11px] border-b border-slate-200 pb-2">
                 <span className="text-slate-500 uppercase tracking-wider">Coef. de Redistribuição (δ)</span>
                 <span className="font-black text-slate-900">0.75 — 1.00</span>
               </div>
               <div className="flex justify-between items-center text-[11px] border-b border-slate-200 pb-2">
                 <span className="text-slate-500 uppercase tracking-wider">Redução Máxima Permitida</span>
                 <span className="font-black text-rose-500">25.0%</span>
               </div>
             </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="p-8 rounded-[2.5rem] bg-white/[0.02] border border-slate-200 space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
                <Zap className="w-4 h-4 text-emerald-600" />
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-900 uppercase tracking-widest mb-2">Vantagem Forense</p>
                <p className="text-[11px] text-slate-500 leading-relaxed uppercase tracking-wide">Evita o congestionamento de armaduras nos apoios e permite um dimensionamento mais econômico e equilibrado da seção.</p>
              </div>
            </div>

            <div className="flex items-start gap-4 pt-6 border-t border-slate-200">
              <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center shrink-0">
                <AlertCircle className="w-4 h-4 text-rose-400" />
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-900 uppercase tracking-widest mb-2">Restrição Normativa</p>
                <p className="text-[11px] text-slate-500 leading-relaxed uppercase tracking-wide">Para $\delta < 1$, a linha neutra ($\xi$) deve ser controlada. Se $\xi > 0.45$, a redistribuição é proibida por falta de reserva de ductilidade.</p>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-amber-500/5 border border-amber-500/10">
            <p className="text-[10px] text-amber-500/60 italic leading-relaxed font-mono uppercase tracking-widest text-center">
              "A estrutura escolhe o caminho de menor rigidez relativa via redistribuição plástica limitada."
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
