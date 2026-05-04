"use client";

import React from "react";
import { motion } from "framer-motion";
import { BlockMath } from "react-katex";
import { Info, Target, Zap, AlertCircle } from "lucide-react";

export default function RedistributionTheoryCard() {
  return (
    <div className="rounded-3xl border border-amber-200 bg-amber-50/30 p-8 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-xl bg-amber-600 text-white shadow-lg shadow-amber-100">
          <Target className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-xl font-black text-slate-900 tracking-tight">Redistribuição de Esforços ($\delta$)</h3>
          <p className="text-[11px] font-bold text-amber-700 uppercase tracking-widest">NBR 6118:2023 - Item 14.7.4</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <p className="text-sm leading-relaxed text-slate-700 font-medium">
            A redistribuição de momentos é um recurso que aproveita a <strong>ductilidade</strong> do concreto armado para reduzir os picos de momentos negativos nos apoios, transferindo parte desses esforços para o vão.
          </p>

          <div className="bg-white p-4 rounded-2xl border border-amber-100 shadow-sm">
            <p className="text-[10px] font-black text-amber-600 uppercase mb-3">Equação de Ajuste:</p>
            <BlockMath math="M_{design} = \delta \cdot M_{elastic}" />
            <div className="mt-3 space-y-1">
              <p className="text-[11px] text-slate-500 flex justify-between"><span>$\delta$ (Coef. de Redistribuição)</span> <span className="font-bold text-slate-900">0.75 a 1.00</span></p>
              <p className="text-[11px] text-slate-500 flex justify-between"><span>Redução máxima permitida</span> <span className="font-bold text-rose-600">25%</span></p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-5 rounded-2xl bg-white border border-slate-100 space-y-3">
            <div className="flex items-start gap-3">
              <Zap className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-black text-slate-900 uppercase">Por que usar?</p>
                <p className="text-[11px] text-slate-500 leading-relaxed">Evita o congestionamento de armaduras nos apoios e permite um dimensionamento mais econômico e equilibrado da viga.</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-black text-slate-900 uppercase">Atenção à Ductilidade</p>
                <p className="text-[11px] text-slate-500 leading-relaxed">Para reduzir o momento ($\delta < 1$), a linha neutra ($\xi$) deve ser baixa. Se $\xi > 0.45$, a redistribuição é proibida pela norma.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-amber-100">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-2 w-2 rounded-full bg-amber-400" />
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Resumo Técnico</p>
        </div>
        <p className="text-[11px] text-slate-500 italic leading-relaxed">
          "A redistribuição linear com plasticidade limitada permite que a estrutura 'escolha' o caminho mais eficiente para os esforços, desde que as seções críticas tenham capacidade de rotação plástica suficiente."
        </p>
      </div>
    </div>
  );
}
