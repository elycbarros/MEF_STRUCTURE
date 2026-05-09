"use client";

import React from "react";
import { BlockMath, InlineMath } from "react-katex";
import { Download, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface MemorialHtmlViewProps {
  blackboard: any;
  onClose: () => void;
  onDownloadPdf?: () => void;
}

export function MemorialHtmlView({ blackboard, onClose, onDownloadPdf }: MemorialHtmlViewProps) {
  if (!blackboard || !blackboard.steps) return null;

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-white overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* Header Fixo */}
      <header className="flex items-center justify-between px-8 py-4 border-b border-slate-100 bg-white/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={onClose}
            className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-all active:scale-95 mr-2"
          >
            <X size={16} />
            Voltar
          </button>
          <div className="bg-amber-500 p-2 rounded-xl text-slate-900 shadow-lg shadow-amber-500/20 hidden sm:block">
            <FileText size={24} />
          </div>
          <div>
            <h2 className="text-sm md:text-xl font-black text-slate-900 leading-none">{blackboard.title || "Memorial de Cálculo"}</h2>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Engine MESTRE • NBR 6118:2023</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onDownloadPdf ?? (() => window.print())}
            className="flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-2xl text-[10px] sm:text-sm font-black hover:bg-slate-800 transition-all active:scale-95 shadow-xl shadow-slate-900/20"
          >
            <Download size={18} />
            <span className="hidden sm:inline">Salvar em PDF</span>
            <span className="sm:hidden uppercase tracking-tighter">PDF</span>
          </button>
        </div>
      </header>

      {/* Conteúdo do Memorial */}
      <div className="flex-1 overflow-y-auto bg-slate-50 p-8 lg:p-12">
        <div className="max-w-4xl mx-auto space-y-12">
          {/* Capa / Identificação */}
          <div className="bg-white rounded-[40px] p-12 shadow-sm border border-slate-100 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full -mr-32 -mt-32 blur-3xl" />
            <div className="relative z-10">
              <h1 className="text-4xl font-black text-slate-900 mb-8 leading-tight">
                Memória de Cálculo <br/>
                <span className="text-amber-600">Pedagógica Detalhada</span>
              </h1>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-8 border-y border-slate-100">
                <div>
                  <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Disciplina</p>
                  <p className="text-sm font-bold text-slate-900">Concreto Armado</p>
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Motor</p>
                  <p className="text-sm font-bold text-slate-900">Engine MESTRE</p>
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Professor</p>
                  <p className="text-sm font-bold text-slate-900">Libânio (Acadêmico)</p>
                </div>
                <div>
                  <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Data</p>
                  <p className="text-sm font-bold text-slate-900">{new Date().toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Passos do Cálculo */}
          <div className="space-y-8">
            {blackboard.steps.map((step: any, index: number) => (
              <section key={index} className="group relative">
                {/* Linha Conectora Vertical */}
                {index !== blackboard.steps.length - 1 && (
                  <div className="absolute left-[23px] top-12 bottom-0 w-px bg-slate-200 group-hover:bg-amber-300 transition-colors" />
                )}
                
                <div className="flex gap-6 items-start">
                  {/* Número do Passo */}
                  <div className="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white border-2 border-slate-100 text-sm font-black text-slate-900 shadow-sm group-hover:border-amber-400 group-hover:bg-amber-50 transition-all">
                    {index + 1}
                  </div>

                  {/* Conteúdo do Passo */}
                  <div className="flex-1 bg-white rounded-3xl p-8 shadow-sm border border-slate-100 hover:shadow-md transition-all">
                    <div className="flex justify-between items-start mb-6">
                      <h3 className="text-lg font-black text-slate-900">{step.title}</h3>
                      <span className="bg-slate-50 text-slate-600 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-tighter">
                        {step.norm_ref || "NBR 6118"}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                      <div className="space-y-6">
                        <p className="text-sm font-medium text-slate-600 leading-relaxed italic">
                          "{step.explanation}"
                        </p>
                        
                        {step.opinion && (
                          <div className={cn(
                            "p-4 rounded-2xl border text-xs font-bold leading-relaxed",
                            step.status === "ALERTA" ? "bg-rose-50 border-rose-100 text-rose-700" : "bg-emerald-50 border-emerald-100 text-emerald-700"
                          )}>
                            {step.opinion}
                          </div>
                        )}
                      </div>

                      <div className="space-y-4">
                        {step.formula_latex && (
                          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                            <p className="text-[9px] font-black text-slate-600 uppercase tracking-widest mb-2">Equação Geral</p>
                            <div className="text-lg overflow-x-auto">
                              <BlockMath math={step.formula_latex} />
                            </div>
                          </div>
                        )}
                        {step.substitution_latex && (
                          <div className="p-4 bg-amber-50/50 rounded-2xl border border-amber-100">
                            <p className="text-[9px] font-black text-amber-700 uppercase tracking-widest mb-2">Desenvolvimento Numérico</p>
                            <div className="text-lg overflow-x-auto text-amber-900">
                              <BlockMath math={step.substitution_latex} />
                            </div>
                          </div>
                        )}
                        {step.result_latex && (
                          <div className="p-4 bg-slate-900 rounded-2xl border border-slate-800 shadow-xl shadow-slate-900/10">
                            <p className="text-[9px] font-black text-white/40 uppercase tracking-widest mb-2">Resultado Final</p>
                            <div className="text-xl text-white overflow-x-auto font-black [&_.katex]:text-white">
                              <BlockMath math={step.result_latex} />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            ))}
          </div>

          {/* Rodapé do Memorial */}
          <footer className="text-center py-12 border-t border-slate-200">
            <p className="text-sm font-black text-slate-600 uppercase tracking-widest">Fim do Memorial de Cálculo</p>
            <p className="text-xs font-bold text-slate-300 mt-2">Documento gerado automaticamente pelo Engine MESTRE v4.0</p>
          </footer>
        </div>
      </div>
    </div>
  );
}
