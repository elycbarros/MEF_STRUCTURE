"use client";

import React from "react";
import { cn, formatNumberBR } from "@/lib/utils";
import { ShieldCheck, Info, HelpCircle, Download, ChevronRight } from "lucide-react";

interface ModuleContainerProps {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  theme: "academic" | "professional";
  children: React.ReactNode;
  auditResult?: any;
  onExport?: () => void;
  onBimExport?: () => void;
  solverType?: "Rust Core" | "WebAssembly" | "Analytic (JS)";
  optimizationSuggestion?: {
    suggestedB: number;
    suggestedH: number;
    suggestedFck: number;
    weightReduction: number;
    explanation: string;
  };
}

export function ModuleContainer({
  title,
  subtitle,
  icon,
  theme,
  children,
  auditResult,
  onExport,
  onBimExport,
  solverType = "Analytic (JS)",
  optimizationSuggestion
}: ModuleContainerProps) {
  const isProfessional = theme === "professional";

  return (
    <div className={cn(
      "min-h-screen transition-colors duration-700 p-6 md:p-10",
      isProfessional ? "bg-[#0f1115] text-white" : "bg-[#f8f9fa] text-[#1d1d1f]"
    )}>
      {/* Header Unificado */}
      <div className={cn(
        "relative mb-8 overflow-hidden rounded-[40px] p-10 shadow-2xl transition-all",
        isProfessional 
          ? "bg-[#16191f] border border-white/5 shadow-blue-900/10" 
          : "bg-white border border-slate-200 shadow-slate-200/50"
      )}>
        {/* Efeito Visual de Contexto */}
        <div className={cn(
          "absolute -right-20 -top-20 h-80 w-80 rounded-full blur-[120px] opacity-30 transition-colors",
          isProfessional ? "bg-blue-600" : "bg-blue-300"
        )} />

        <div className="relative z-10 flex flex-col justify-between gap-8 lg:flex-row lg:items-center">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={cn(
                "flex h-12 w-12 items-center justify-center rounded-2xl shadow-lg transition-transform hover:scale-110",
                isProfessional ? "bg-blue-600" : "bg-blue-500"
              )}>
                {icon}
              </div>
              <div className="flex flex-col">
                <span className={cn(
                  "text-[10px] font-black uppercase tracking-[0.3em]",
                  isProfessional ? "text-blue-400" : "text-blue-600"
                )}>
                  {isProfessional ? "STRUCTURAL PRO ENGINE" : "MESTRE ACADEMIC LAB"}
                </span>
                <h1 className={cn(
                  "text-4xl font-black tracking-tighter",
                  isProfessional ? "text-white" : "text-slate-900"
                )}>
                  {title}
                </h1>
              </div>
            </div>
            <p className={cn(
              "max-w-2xl text-lg font-medium leading-relaxed",
              isProfessional ? "text-white/60" : "text-slate-500"
            )}>
              {subtitle}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className={cn(
              "flex items-center gap-3 rounded-2xl border px-5 py-3 backdrop-blur-md",
              isProfessional ? "border-white/10 bg-white/5" : "border-slate-200 bg-slate-50"
            )}>
              <div className={cn(
                "h-2 w-2 animate-pulse rounded-full",
                solverType === "Rust Core" ? "bg-orange-500" : "bg-green-500"
              )} />
              <span className={cn(
                "text-xs font-black uppercase tracking-widest",
                isProfessional ? "text-white/70" : "text-slate-600"
              )}>
                {solverType}
              </span>
            </div>

            {onBimExport && (
              <button 
                onClick={onBimExport}
                className={cn(
                  "flex items-center gap-3 rounded-2xl px-6 py-3 font-black transition-all hover:scale-105 active:scale-95 border",
                  isProfessional 
                    ? "border-blue-500/30 bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 shadow-lg shadow-blue-900/20" 
                    : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                )}
              >
                <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                Exportar BIM (IFC)
              </button>
            )}

            {onExport && (
              <button 
                onClick={onExport}
                className={cn(
                  "flex items-center gap-3 rounded-2xl px-6 py-3 font-black transition-all hover:scale-105 active:scale-95",
                  isProfessional ? "bg-white text-black" : "bg-[#1d1d1f] text-white"
                )}
              >
                <Download className="h-4 w-4" />
                Memorial HTML
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Conteúdo do Módulo */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
        {children}
      </div>

      {/* Auditoria IA (Padronizada) */}
      {auditResult && (
        <div className={cn(
          "mt-12 overflow-hidden rounded-[40px] border p-10 transition-all",
          isProfessional 
            ? "border-blue-900/30 bg-blue-900/5 backdrop-blur-xl" 
            : "border-blue-100 bg-blue-50/50"
        )}>
          <div className="flex items-center gap-6">
            <div className={cn(
              "flex h-16 w-16 items-center justify-center rounded-2xl shadow-xl",
              isProfessional ? "bg-blue-600 shadow-blue-600/40" : "bg-blue-500 shadow-blue-500/20"
            )}>
              <ShieldCheck className="h-9 w-9 text-white" />
            </div>
            <div>
              <p className={cn(
                "text-[10px] font-black uppercase tracking-[0.3em]",
                isProfessional ? "text-blue-400" : "text-blue-600"
              )}>
                M5-PhD Structural Intelligence
              </p>
              <h3 className={cn(
                "text-3xl font-black",
                isProfessional ? "text-white" : "text-slate-900"
              )}>
                Auditoria de Engenharia
              </h3>
            </div>
          </div>
          
          <div className="mt-10 grid grid-cols-1 gap-10 md:grid-cols-3">
            {/* Parecer Técnico */}
            <div className="space-y-4">
              <p className={cn(
                "text-[10px] font-black uppercase tracking-[0.2em]",
                isProfessional ? "text-blue-400/60" : "text-[#6a7485]"
              )}>
                Parecer Técnico Ph.D.
              </p>
              <div className={cn(
                "rounded-3xl p-6 transition-all min-h-[140px] flex items-center",
                isProfessional ? "bg-white/5 border border-white/5" : "bg-white border border-blue-100"
              )}>
                <p className={cn(
                  "text-lg font-bold leading-relaxed",
                  isProfessional ? "text-white" : "text-[#1d1d1f]"
                )}>
                  {auditResult.advice}
                </p>
              </div>
            </div>

            {/* Otimização Gerativa */}
            <div className="space-y-4">
              <p className={cn(
                "text-[10px] font-black uppercase tracking-[0.2em]",
                isProfessional ? "text-blue-400/60" : "text-[#6a7485]"
              )}>
                Sugestão de Otimização (Generative)
              </p>
              {optimizationSuggestion ? (
                <div className={cn(
                  "rounded-3xl p-6 border-2 transition-all relative overflow-hidden group",
                  isProfessional 
                    ? "bg-blue-600/10 border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.2)]" 
                    : "bg-blue-50 border-blue-200"
                )}>
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-3">
                      <ShieldCheck className="h-4 w-4 text-blue-500" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-blue-500">M5-PhD Insight</span>
                    </div>
                    <p className={cn(
                      "text-sm font-black italic leading-tight mb-4",
                      isProfessional ? "text-blue-100" : "text-blue-900"
                    )}>
                      "{optimizationSuggestion.explanation}"
                    </p>
                    <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                      <div>
                        <p className="text-[8px] font-black uppercase opacity-60">Redução Estimada</p>
                        <p className="text-xl font-black text-emerald-400">-{formatNumberBR(optimizationSuggestion.weightReduction, 1)}%</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[8px] font-black uppercase opacity-60">Seção Ideal</p>
                        <p className="text-sm font-black">{optimizationSuggestion.suggestedB}x{optimizationSuggestion.suggestedH} cm</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className={cn(
                  "rounded-3xl p-6 border border-dashed flex flex-col items-center justify-center text-center space-y-2 opacity-50 h-[140px]",
                  isProfessional ? "border-white/20" : "border-slate-300"
                )}>
                   <p className="text-[10px] font-black uppercase tracking-widest">Nenhuma otimização necessária</p>
                   <p className="text-[8px] font-bold">A seção atual já opera em eficiência máxima.</p>
                </div>
              )}
            </div>

            {/* Ações Recomendadas */}
            <div className="space-y-4">
              <p className={cn(
                "text-[10px] font-black uppercase tracking-[0.2em]",
                isProfessional ? "text-blue-400/60" : "text-[#6a7485]"
              )}>
                Ações Recomendadas
              </p>
              <div className="flex flex-col gap-3">
                {auditResult.actions?.map((action: string, i: number) => (
                  <div key={i} className={cn(
                    "flex items-center gap-4 rounded-2xl border p-4 transition-all hover:scale-[1.02]",
                    isProfessional 
                      ? "border-blue-900/40 bg-blue-900/20 text-blue-200" 
                      : "border-blue-100 bg-blue-50/50 text-blue-900"
                  )}>
                    <ChevronRight className="h-5 w-5 shrink-0" />
                    <span className="text-sm font-black">{action}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
