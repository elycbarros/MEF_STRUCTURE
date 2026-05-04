"use client";

import React from "react";
import { Info, HelpCircle, Layers, Zap, AlertTriangle, BookOpen } from "lucide-react";
import { motion } from "framer-motion";
import { BlockMath } from "react-katex";

export default function ISETheoryView() {
  return (
    <section className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm overflow-hidden">
      <div className="flex items-start gap-4 mb-8">
        <div className="p-3 rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200">
          <BookOpen className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Fundamentos de Interação Solo-Estrutura (ISE)</h2>
          <p className="text-sm font-medium text-slate-500 mt-1">Conceitos didáticos para Auditoria Forense e Análise de Rigidez</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Modelo Elástico */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-black">01</span>
            <h3 className="font-black text-slate-800 uppercase text-xs tracking-widest">Modelo de Apoio Elástico (Winkler)</h3>
          </div>
          <div className="p-6 rounded-2xl bg-blue-50/50 border border-blue-100 leading-relaxed text-sm text-slate-700">
            <p className="mb-4">
              Neste modelo, o solo é substituído por uma série de <strong>molas independentes</strong> que se deformam proporcionalmente à carga aplicada.
            </p>
            <div className="bg-white p-4 rounded-xl border border-blue-100 mb-4 shadow-sm">
               <p className="text-[10px] font-black text-blue-600 uppercase mb-2">Formulação Fundamental:</p>
               <BlockMath math="k = \frac{q}{w}" />
               <p className="text-[10px] text-slate-400 mt-2 italic text-center">Onde: k = Coeficiente de mola | q = Pressão | w = Deformação</p>
            </div>
            <ul className="space-y-2 list-none">
              <li className="flex gap-2"><Zap className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" /> <strong>Vantagem:</strong> Permite simular a redistribuição de esforços devido à flexibilidade do solo.</li>
              <li className="flex gap-2"><AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" /> <strong>Limitação:</strong> Não considera a continuidade do solo (molas não interagem entre si).</li>
            </ul>
          </div>
        </div>

        {/* Modelo Livre Balanço */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-xs font-black">02</span>
            <h3 className="font-black text-slate-800 uppercase text-xs tracking-widest">Modelo em Livre Balanço (Cantilever)</h3>
          </div>
          <div className="p-6 rounded-2xl bg-slate-50/50 border border-slate-100 leading-relaxed text-sm text-slate-700">
            <p className="mb-4">
              Associado a estruturas de contenção (cortinas) onde a restrição do solo é desprezada na região superior, exigindo análise de <strong>engaste na base</strong>.
            </p>
            <div className="bg-white p-4 rounded-xl border border-slate-100 mb-4 shadow-sm">
               <p className="text-[10px] font-black text-slate-600 uppercase mb-2">Comportamento Mecânico:</p>
               <div className="flex justify-between items-center px-4">
                  <div className="text-center">
                    <p className="text-[10px] text-slate-400">Topo</p>
                    <p className="text-xs font-bold text-slate-900">Deslocável</p>
                  </div>
                  <div className="h-px w-8 bg-slate-200" />
                  <div className="text-center">
                    <p className="text-[10px] text-slate-400">Base</p>
                    <p className="text-xs font-bold text-slate-900">Rígida</p>
                  </div>
               </div>
            </div>
            <ul className="space-y-2 list-none">
              <li className="flex gap-2"><Zap className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" /> Ideal para cortinas e estacas em solos muito moles.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Seção Adicional: Aplicações Profissionais */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="p-5 rounded-2xl bg-emerald-50/30 border border-emerald-100">
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-emerald-600" />
            <h4 className="text-xs font-black text-emerald-800 uppercase">Fundações Superficiais</h4>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-600">Sapatas e Radiers são modelados com coeficientes de recalque (k) que simulam a rigidez do meio elástico sob a base, permitindo o cálculo de recalques diferenciais.</p>
        </div>
        <div className="p-5 rounded-2xl bg-amber-50/30 border border-amber-100">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <h4 className="text-xs font-black text-amber-800 uppercase">Fundações Profundas</h4>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-600">Estacas são representadas como barras discretas no pórtico unifilar, apoiadas em molas ao longo do fuste e na ponta, baseando-se nas camadas de solo.</p>
        </div>
        <div className="p-5 rounded-2xl bg-indigo-50/30 border border-indigo-100">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-indigo-600" />
            <h4 className="text-xs font-black text-indigo-800 uppercase">Estabilidade Global</h4>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-600">A consideração da ISE pode impactar significativamente o coeficiente <strong>γz</strong> e o efeito P-Delta, tornando a análise da estabilidade do edifício mais rigorosa.</p>
        </div>
      </div>

      {/* Resumo Comparativo */}
      <div className="mt-8">
        <h3 className="font-black text-slate-800 uppercase text-xs tracking-widest mb-6 px-1 flex items-center gap-2">
          Resumo Comparativo
          <div className="h-px flex-1 bg-slate-100" />
        </h3>
        <div className="overflow-hidden rounded-2xl border border-slate-200">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="p-4 text-[11px] font-black text-slate-400 uppercase tracking-wider">Característica</th>
                <th className="p-4 text-[11px] font-black text-blue-600 uppercase tracking-wider">Apoio Elástico (Mola)</th>
                <th className="p-4 text-[11px] font-black text-slate-900 uppercase tracking-wider">Livre (Balanço)</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              <tr className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                <td className="p-4 font-bold text-slate-900">Restrição do Solo</td>
                <td className="p-4 text-slate-600">Considerada via coeficiente de recalque (kₛ)</td>
                <td className="p-4 text-slate-600">Desprezada ou baixa perto da superfície</td>
              </tr>
              <tr className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                <td className="p-4 font-bold text-slate-900">Simulação do Solo</td>
                <td className="p-4 text-slate-600">Molas discretas, lineares/não lineares</td>
                <td className="p-4 text-slate-600">Estrutura sem suporte lateral</td>
              </tr>
              <tr className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                <td className="p-4 font-bold text-slate-900">Deformações</td>
                <td className="p-4 text-slate-600">Menores (devido ao suporte do solo)</td>
                <td className="p-4 text-slate-600">Maiores (livre para rotacionar/deslocar)</td>
              </tr>
              <tr className="hover:bg-slate-50/50 transition-colors">
                <td className="p-4 font-bold text-slate-900">Aplicação Típica</td>
                <td className="p-4 text-slate-600">Sapatas, estacas (curvas p-y), radiers</td>
                <td className="p-4 text-slate-600">Cortinas de contenção, estacas curtas</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
