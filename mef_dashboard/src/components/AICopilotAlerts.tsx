"use client";

import React from "react";
import { Cpu, AlertTriangle, CheckCircle, Info, Sparkles } from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";

interface AICopilotAlertsProps {
  diagnosis?: string[];
  efficiencyScore?: number;
  masterOpinion?: string;
  optimizationSuggestion?: {
    suggestedB: number;
    suggestedH: number;
    suggestedFck: number;
    weightReduction: number;
    explanation: string;
  };
}

export default function AICopilotAlerts({ 
  diagnosis = [], 
  efficiencyScore = 100,
  masterOpinion,
  optimizationSuggestion
}: AICopilotAlertsProps) {
  if (!diagnosis || diagnosis.length === 0) {
    return (
      <div className="p-6 rounded-3xl border border-slate-200 bg-white shadow-sm flex flex-col items-center justify-center text-center space-y-3">
        <Sparkles className="w-8 h-8 text-blue-400 opacity-20" />
        <p className="text-xs font-bold text-slate-400">Nenhum diagnóstico AI disponível no momento.</p>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-white/5 bg-[#1a1c1e] p-6 shadow-2xl text-white overflow-hidden relative">
      {/* Background Glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-3xl -mr-16 -mt-16 rounded-full" />
      
      <div className="flex items-center justify-between mb-6 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-xl border border-blue-500/30">
            <Cpu className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-black italic tracking-tight">AI Structural Copilot</h3>
            <p className="text-[10px] font-bold text-blue-300/60 uppercase tracking-widest">M5-PhD Optimization Engine</p>
          </div>
        </div>
      </div>

      <div className="space-y-4 relative z-10">
        {/* Sugestão de Otimização (Generative Design) */}
        {optimizationSuggestion && (
          <div className="p-5 rounded-2xl border-2 border-blue-500/50 bg-blue-500/10 shadow-[0_0_20px_rgba(59,130,246,0.2)] animate-in fade-in slide-in-from-bottom-2">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-blue-400 fill-blue-400/20" />
              <span className="text-[10px] font-black uppercase tracking-widest text-blue-400">Generative Suggestion</span>
            </div>
            <p className="text-sm font-black italic text-white mb-4 leading-tight">
              "{optimizationSuggestion.explanation}"
            </p>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-2 bg-white/5 rounded-xl border border-white/10 text-center">
                <p className="text-[8px] font-black text-slate-400 uppercase">Seção Sugerida</p>
                <p className="text-sm font-black">{optimizationSuggestion.suggestedB}x{optimizationSuggestion.suggestedH} cm</p>
              </div>
              <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-center">
                <p className="text-[8px] font-black text-emerald-400 uppercase">Redução de Peso</p>
                <p className="text-sm font-black text-emerald-400">-{formatNumberBR(optimizationSuggestion.weightReduction, 1)}%</p>
              </div>
            </div>
            <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-[10px] font-black uppercase tracking-widest transition-all active:scale-95 shadow-lg shadow-blue-600/20">
              Aplicar Otimização
            </button>
          </div>
        )}

        {masterOpinion && (
          <div className={cn(
            "p-5 rounded-2xl border-2 transition-all bg-red-600/20 border-red-600/50 shadow-[0_0_15px_rgba(220,38,38,0.2)]",
            masterOpinion.includes("REVISÃO") && "animate-pulse"
          )}>
            <div className="flex gap-3">
              <div className="shrink-0">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-red-400 mb-1">Parecer Técnico Forense</p>
                <p className="text-sm font-black leading-tight text-white italic">
                  "{masterOpinion}"
                </p>
              </div>
            </div>
          </div>
        )}

        {diagnosis.map((text, i) => {
          const isWarning = text.includes("⚠️") || text.includes("🚨");
          const isError = text.includes("❌");
          const isSuccess = text.includes("✅") || text.includes("💡");

          return (
            <div 
              key={i} 
              className={cn(
                "p-4 rounded-2xl border transition-all hover:scale-[1.02]",
                isError ? "bg-red-500/10 border-red-500/20" : 
                isWarning ? "bg-red-500/20 border-red-500/30 animate-pulse" : 
                "bg-white/5 border-white/10"
              )}
            >
              <div className="flex gap-3">
                <div className="shrink-0 mt-0.5">
                  {isError ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
                   isWarning ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
                   isSuccess ? <CheckCircle className="w-4 h-4 text-emerald-400" /> :
                   <Info className="w-4 h-4 text-blue-400" />}
                </div>
                <p className="text-xs font-bold leading-relaxed opacity-90">
                  {text.replace(/[⚠️🚨❌✅💡🔍]/g, '').trim()}
                </p>
              </div>
            </div>
          );
        })}

        <div className="pt-4 mt-2 border-t border-white/10">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="font-bold opacity-60 uppercase tracking-widest text-[9px]">Structural Efficiency</span>
            <span className="font-black text-blue-400">{efficiencyScore}%</span>
          </div>
          <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden shadow-inner">
            <div 
              className="h-full bg-gradient-to-r from-blue-600 to-emerald-400 transition-all duration-1000" 
              style={{ width: `${efficiencyScore}%` }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}
