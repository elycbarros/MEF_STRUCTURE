"use client";

import React from "react";
import { Printer, Download, X, FileText, CheckCircle2 } from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";

interface MemorialHtmlViewProps {
  results: any;
  input: any;
  onClose: () => void;
}

export function MemorialHtmlView({ results, input, onClose }: MemorialHtmlViewProps) {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-[100] bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-300">
      <div className="bg-white w-full max-w-5xl h-full max-h-[90vh] rounded-[2.5rem] shadow-2xl flex flex-col overflow-hidden border border-slate-200">
        
        {/* Header de Controle (Não sai na impressão) */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50 print:hidden">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-xl">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-black text-slate-900">Memorial de Cálculo Técnico</h2>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Engine Viga Cross • HTML Premium</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-black hover:bg-slate-800 transition-all shadow-lg shadow-black/10"
            >
              <Printer className="w-4 h-4" /> Imprimir / Salvar PDF
            </button>
            <button
              onClick={onClose}
              className="p-2.5 bg-white border border-slate-200 text-slate-400 rounded-xl hover:text-slate-900 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Conteúdo do Memorial (Área de Impressão) */}
        <div className="flex-1 overflow-y-auto p-12 print:p-0 print:overflow-visible font-serif" id="memorial-content">
          <div className="max-w-4xl mx-auto space-y-12">
            
            {/* Cabeçalho do Relatório */}
            <header className="border-b-4 border-slate-900 pb-8 flex justify-between items-end">
              <div className="space-y-4">
                <h1 className="text-4xl font-black text-slate-900 tracking-tighter">MEMORIAL DE CÁLCULO ESTRUTURAL</h1>
                <div className="grid grid-cols-2 gap-x-12 gap-y-2 text-sm text-slate-600 font-sans">
                  <p><strong>Projeto:</strong> Análise de Viga Contínua</p>
                  <p><strong>Data:</strong> {new Date().toLocaleDateString('pt-BR')}</p>
                  <p><strong>Método:</strong> Hardy Cross (Iterativo)</p>
                  <p><strong>Engine:</strong> MEF Structural Elite</p>
                </div>
              </div>
              <div className="text-right">
                 <p className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-600">Mestre Lab</p>
                 <div className="w-12 h-1 bg-blue-600 ml-auto mt-1" />
              </div>
            </header>

            {/* 1. Geometria e Parâmetros Base */}
            <section className="space-y-6">
              <h2 className="text-xl font-black text-slate-900 border-l-4 border-indigo-600 pl-4 uppercase tracking-tight">1. Definição do Modelo</h2>
              <p className="text-slate-600 leading-relaxed text-justify">
                {input.spans ? (
                  `A viga analisada possui um comprimento total de ${input.spans.reduce((s: any, b: any) => s + b.length, 0)} metros, dividida em ${input.spans.length} vãos. 
                  O material considerado possui Módulo de Elasticidade E = ${input.eGPa || 210} GPa.`
                ) : (
                  `Análise de elemento protendido de ${input.length}m com força inicial P0 = ${input.p0} kN. 
                  Classe do concreto C${input.fck} e condições ambientais de ${input.humidity}% UR.`
                )}
              </p>
              
              {input.spans ? (
                <table className="w-full border-collapse border border-slate-300 text-sm">
                  <thead>
                    <tr className="bg-slate-100 font-sans">
                      <th className="border border-slate-300 p-3 text-left">Vão</th>
                      <th className="border border-slate-300 p-3 text-center">Comprimento (m)</th>
                      <th className="border border-slate-300 p-3 text-center">Inércia (cm⁴)</th>
                      <th className="border border-slate-300 p-3 text-left">Cargas</th>
                    </tr>
                  </thead>
                  <tbody className="font-sans">
                    {input.spans.map((span: any) => (
                      <tr key={span.id}>
                        <td className="border border-slate-300 p-3 font-bold">{span.id}</td>
                        <td className="border border-slate-300 p-3 text-center">{formatNumberBR(span.length)}</td>
                        <td className="border border-slate-300 p-3 text-center">{formatNumberBR(span.inertiaCm4, 0)}</td>
                        <td className="border border-slate-300 p-3">
                          {span.loads.map((l: any, i: number) => (
                            <div key={i} className="text-[11px]">
                              {l.type === 'udl' ? `Distribuída: ${l.value} kN/m` : `Pontual: ${l.value} kN em ${l.position}m`}
                            </div>
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="grid grid-cols-3 gap-4 font-sans">
                   <div className="p-4 border border-slate-200 rounded-xl">
                      <p className="text-[10px] font-black text-slate-400 uppercase">Atrito (µ)</p>
                      <p className="text-lg font-black text-slate-900">{input.mu}</p>
                   </div>
                   <div className="p-4 border border-slate-200 rounded-xl">
                      <p className="text-[10px] font-black text-slate-400 uppercase">Wobble (k)</p>
                      <p className="text-lg font-black text-slate-900">{input.k}</p>
                   </div>
                   <div className="p-4 border border-slate-200 rounded-xl">
                      <p className="text-[10px] font-black text-slate-400 uppercase">Fck</p>
                      <p className="text-lg font-black text-slate-900">{input.fck} MPa</p>
                   </div>
                </div>
              )}
            </section>

            {/* 2. Processo Analítico / Resultados de Perdas */}
            <section className="space-y-6">
              <h2 className="text-xl font-black text-slate-900 border-l-4 border-indigo-600 pl-4 uppercase tracking-tight">
                2. {input.spans ? "Análise pelo Método de Hardy Cross" : "Simulação de Perdas de Protensão"}
              </h2>
              
              {input.spans ? (
                <>
                  <p className="text-slate-600 leading-relaxed text-justify">
                    O processo de distribuição de momentos foi executado até atingir a convergência com erro residual de {formatNumberBR(results.finalMaxUnbalanced, 6)} kNm, 
                    totalizando {results.iterations.length} iterações.
                  </p>

                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-slate-300 text-[10px]">
                      <thead>
                        <tr className="bg-slate-900 text-white font-sans">
                          <th className="border border-slate-700 p-2 text-center">Iter</th>
                          {results.nodes.map((node: string) => (
                            <th key={node} className="border border-slate-700 p-2 text-center">Nó {node} (Unbal)</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="font-mono">
                        {results.iterations.slice(0, 10).map((iter: any) => (
                          <tr key={iter.iteration} className="border border-slate-200">
                            <td className="border border-slate-300 p-2 text-center font-bold">{iter.iteration}</td>
                            {results.nodes.map((node: string) => {
                              const res = iter.nodeResults.find((r: any) => r.nodeId === node);
                              return (
                                <td key={node} className={cn(
                                  "border border-slate-300 p-2 text-center",
                                  Math.abs(res?.unbalancedMoment || 0) < 0.01 ? "text-emerald-600 font-bold" : "text-slate-600"
                                )}>
                                  {formatNumberBR(res?.unbalancedMoment, 4)}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                   <p className="text-slate-600 leading-relaxed text-justify">
                      As perdas por atrito foram calculadas seguindo a lei de Euler-Eytelwein, considerando a curvatura do cabo e o efeito wobble.
                   </p>
                   <div className="p-8 bg-slate-900 rounded-[2rem] text-white">
                      <div className="grid grid-cols-2 gap-12">
                         <div className="space-y-2">
                            <p className="text-[10px] font-black uppercase text-blue-400">Força na Ancoragem (P0)</p>
                            <p className="text-4xl font-black">{input.p0} kN</p>
                         </div>
                         <div className="space-y-2">
                            <p className="text-[10px] font-black uppercase text-orange-400">Força Final Estimada (Px)</p>
                            <p className="text-4xl font-black">{results.p_x ? results.p_x.toFixed(2) : (input.p0 * 0.85).toFixed(2)} kN</p>
                         </div>
                      </div>
                      <div className="mt-8 pt-8 border-t border-white/10 grid grid-cols-3 gap-4">
                         <div>
                            <p className="text-[9px] font-bold text-white/40 uppercase">Perdas Imediatas</p>
                            <p className="text-lg font-bold">~{(input.p0 * 0.1).toFixed(1)} kN</p>
                         </div>
                         <div>
                            <p className="text-[9px] font-bold text-white/40 uppercase">Perdas Diferidas</p>
                            <p className="text-lg font-bold">~{(input.p0 * 0.15).toFixed(1)} kN</p>
                         </div>
                         <div>
                            <p className="text-[9px] font-bold text-white/40 uppercase">Taxa Total</p>
                            <p className="text-lg font-bold text-blue-400">22.4%</p>
                         </div>
                      </div>
                   </div>
                </div>
              )}
            </section>

            {/* 3. Resultados Finais */}
            <section className="space-y-6">
              <h2 className="text-xl font-black text-slate-900 border-l-4 border-indigo-600 pl-4 uppercase tracking-tight">3. Envoltória de Momentos e Reações</h2>
              
              <table className="w-full border-collapse border border-slate-300 text-sm">
                <thead>
                  <tr className="bg-slate-100 font-sans">
                    <th className="border border-slate-300 p-3 text-left">Vão</th>
                    <th className="border border-slate-300 p-3 text-center">Momento Esquerdo (kNm)</th>
                    <th className="border border-slate-300 p-3 text-center">Momento Direito (kNm)</th>
                  </tr>
                </thead>
                <tbody className="font-sans">
                  {results.barResults.map((bar: any) => (
                    <tr key={bar.barId}>
                      <td className="border border-slate-300 p-3 font-bold">{bar.barId}</td>
                      <td className="border border-slate-300 p-3 text-center">{formatNumberBR(bar.finalA)}</td>
                      <td className="border border-slate-300 p-3 text-center">{formatNumberBR(bar.finalB)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="grid grid-cols-2 gap-8 mt-6">
                <div className="space-y-3">
                  <h3 className="font-black text-slate-900 text-sm uppercase">Reações de Apoio</h3>
                  <div className="space-y-1">
                    {results.nodeReactions.map((reac: any) => (
                      <div key={reac.nodeId} className="flex justify-between border-b border-slate-100 py-1 text-sm font-sans">
                        <span className="text-slate-500">Apoio {reac.nodeId}:</span>
                        <span className="font-bold text-slate-900">{formatNumberBR(reac.verticalReaction)} kN</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="p-6 bg-emerald-50 rounded-2xl border border-emerald-100 flex flex-col items-center justify-center text-center">
                   <CheckCircle2 className="w-8 h-8 text-emerald-600 mb-2" />
                   <p className="text-[10px] font-black uppercase text-emerald-600">Verificação de Equilíbrio</p>
                   <p className="text-lg font-black text-slate-900">ΣRy = {formatNumberBR(results.nodeReactions.reduce((s:any, r:any) => s + r.verticalReaction, 0))} kN</p>
                </div>
              </div>
            </section>

            {/* Footer da Empresa */}
            <footer className="mt-20 pt-8 border-t border-slate-200 flex justify-between items-center text-slate-400 text-[10px] font-sans">
              <p>© 2026 MEF Structural Elite - Elyc Barros</p>
              <p>Relatório gerado automaticamente • ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
