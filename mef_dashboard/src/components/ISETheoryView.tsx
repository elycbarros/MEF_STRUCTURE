"use client";

import React from "react";
import { Info, HelpCircle, Layers, Zap, AlertTriangle, BookOpen, Binary, Target, Database } from "lucide-react";
import { motion } from "framer-motion";
import { BlockMath } from "react-katex";
import { cn } from "@/lib/utils";

export default function ISETheoryView() {
  return (
    <section className="p-10 rounded-[3rem] bg-slate-100/60 border border-slate-200 shadow-2xl backdrop-blur-xl overflow-hidden relative group">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 p-12 opacity-[0.02] pointer-events-none group-hover:opacity-[0.05] transition-opacity">
         <Binary className="w-64 h-64" />
      </div>

      <div className="flex items-start gap-6 mb-12 relative z-10">
        <div className="p-4 rounded-2xl bg-blue-600/10 border border-blue-500/20 text-blue-600 shadow-lg shadow-blue-600/10">
          <BookOpen className="w-8 h-8" />
        </div>
        <div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tighter">Fundamentos de Interação Solo-Estrutura (ISE)</h2>
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mt-2">Corpus Teórico para Auditoria Forense & Engenharia de Rigidez</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-16 relative z-10">
        {/* Modelo Elástico */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 border border-blue-500/20 flex items-center justify-center text-[10px] font-black font-mono">01</div>
            <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.2em]">Modelo de Apoio Elástico (Winkler)</h3>
          </div>
          <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-slate-200 leading-relaxed text-sm text-slate-600 group/card hover:border-blue-500/30 transition-colors">
            <p className="mb-6 leading-relaxed">
              Discretização cinemática onde o maciço é substituído por uma rede de <strong>molas independentes</strong>. A rigidez é governada pela Lei de Hooke local.
            </p>
            <div className="bg-white/80 p-6 rounded-2xl border border-blue-500/10 mb-6 shadow-xl relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
               <p className="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-4">Equação de Estado Local:</p>
               <div className="text-slate-900 scale-110 py-2">
                 <BlockMath math="k_s = \frac{\sigma}{\delta}" />
               </div>
               <p className="text-[9px] text-slate-500 mt-4 italic text-center font-mono">kₛ: Coeficiente de Recalque | σ: Tensão de Contato | δ: Deformação</p>
            </div>
            <ul className="space-y-3 list-none">
              <li className="flex gap-3 text-xs"><Zap className="w-4 h-4 text-emerald-500 shrink-0" /> <span className="opacity-80"><strong className="text-slate-900">Eficiência:</strong> Otimização matricial via [K] em banda.</span></li>
              <li className="flex gap-3 text-xs"><AlertTriangle className="h-4 w-4 text-amber-500 shrink-0" /> <span className="opacity-80"><strong className="text-slate-900">Boundary:</strong> Limitação de continuidade (Paradoxo de Winkler).</span></li>
            </ul>
          </div>
        </div>

        {/* Modelo Livre Balanço */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-500/10 text-slate-600 border border-slate-500/20 flex items-center justify-center text-[10px] font-black font-mono">02</div>
            <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.2em]">Modelo em Livre Balanço (Cantilever)</h3>
          </div>
          <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-slate-200 leading-relaxed text-sm text-slate-600 group/card hover:border-slate-500/30 transition-colors">
            <p className="mb-6 leading-relaxed">
              Abordagem simplificada para elementos onde a restrição lateral é nula ou desprezível. Foco em <strong>estabilidade por engaste basal</strong>.
            </p>
            <div className="bg-white/80 p-6 rounded-2xl border border-slate-200 mb-6 shadow-xl space-y-4">
               <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Diagrama de Rigidez:</p>
               <div className="flex justify-between items-center px-6 py-2">
                  <div className="text-center">
                    <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest mb-1">Topo</p>
                    <p className="text-xs font-black text-slate-900">Livre (Δ)</p>
                  </div>
                  <div className="h-[1px] flex-1 mx-4 bg-gradient-to-r from-transparent via-slate-700 to-transparent relative">
                     <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-slate-500/20 border border-slate-500/50" />
                  </div>
                  <div className="text-center">
                    <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest mb-1">Base</p>
                    <p className="text-xs font-black text-slate-900">Fixed (0)</p>
                  </div>
               </div>
            </div>
            <ul className="space-y-3 list-none">
              <li className="flex gap-3 text-xs"><Target className="w-4 h-4 text-slate-500 shrink-0" /> <span className="opacity-80">Ideal para verificações de <strong>Primeira Ordem</strong> em contenções.</span></li>
            </ul>
          </div>
        </div>
      </div>

      {/* Seção Adicional: Aplicações de Engenharia */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16 relative z-10">
        {[
          { icon: Layers, title: "Fundações Superficiais", text: "Radiers modelados via MEF em casca sobre base elástica (Spring-Bed).", color: "blue" },
          { icon: Target, title: "Fundações Profundas", text: "Modelagem de estacas via barras discretas com molas laterais e de ponta.", color: "amber" },
          { icon: Zap, title: "Estabilidade Global", text: "Impacto direto no coeficiente γz e efeitos de Segunda Ordem (P-Delta).", color: "emerald" }
        ].map((item, i) => (
          <div key={i} className="p-6 rounded-[2rem] bg-white/[0.02] border border-slate-200 hover:bg-white/[0.04] transition-all group/item">
            <div className={cn("flex items-center gap-3 mb-4", `text-${item.color}-400`)}>
              <item.icon className="w-5 h-5 group-hover/item:scale-110 transition-transform" />
              <h4 className="text-[10px] font-black uppercase tracking-widest">{item.title}</h4>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-500 group-hover/item:text-slate-600 transition-colors">{item.text}</p>
          </div>
        ))}
      </div>

      {/* Resumo Comparativo */}
      <div className="mt-12 relative z-10">
        <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em] mb-8 px-2 flex items-center gap-4">
          Matriz de Comparação Técnica
          <div className="h-[1px] flex-1 bg-gradient-to-r from-white/10 to-transparent" />
        </h3>
        <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white/50 backdrop-blur-xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/[0.02] border-b border-slate-200">
                <th className="p-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Atributo</th>
                <th className="p-6 text-[10px] font-black text-blue-600 uppercase tracking-widest">Apoio Elástico (Winkler)</th>
                <th className="p-6 text-[10px] font-black text-slate-900 uppercase tracking-widest">Livre (Cantilever)</th>
              </tr>
            </thead>
            <tbody className="text-xs">
              {[
                { attr: "Modelagem Cinemática", col1: "Coeficiente de Recalque (kₛ)", col2: "Grau de Liberdade Pleno" },
                { attr: "Representação Física", col2: "Unifilar em Balanço", col1: "Molas Discretas de Winkler" },
                { attr: "Rigidez Relativa", col1: "Solo provê suporte contínuo", col2: "Foco em rigidez do material" },
                { attr: "Auditoria Forense", col1: "Verificação de P-Delta Real", col2: "Análise de Estabilidade Local" }
              ].map((row, i) => (
                <tr key={i} className="border-b border-slate-200 hover:bg-white/[0.02] transition-all group/row">
                  <td className="p-6 font-black text-slate-500 text-[10px] uppercase tracking-wider">{row.attr}</td>
                  <td className="p-6 text-slate-600 font-medium group-hover/row:text-blue-200 transition-colors">{row.col1}</td>
                  <td className="p-6 text-slate-600 font-medium group-hover/row:text-slate-900 transition-colors">{row.col2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
