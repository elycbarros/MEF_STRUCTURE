"use client";

import React from "react";
import { Cpu, AlertTriangle, CheckCircle, Info, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface AICopilotAlertsProps {
  diagnosis?: string[];
  efficiencyScore?: number;
  masterOpinion?: string;
}

export default function AICopilotAlerts({ 
  diagnosis = [], 
  efficiencyScore = 100,
  masterOpinion 
}: AICopilotAlertsProps) {
  if (!diagnosis || diagnosis.length === 0) {
    return (
      <div className="p-6 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm flex flex-col items-center justify-center text-center space-y-3">
        <Sparkles className="w-8 h-8 text-indigo-400 opacity-20" />
        <p className="text-xs font-bold text-[#8a9ab0]">Nenhum diagnóstico AI disponível no momento.</p>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-[#e0e7ef] bg-[#1a1c1e] p-6 shadow-xl text-white overflow-hidden relative">
      {/* Background Glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-3xl -mr-16 -mt-16 rounded-full" />
      
      <div className="flex items-center justify-between mb-6 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-500/30">
            <Cpu className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-lg font-black italic tracking-tight">AI Structural Copilot</h3>
            <p className="text-[10px] font-bold text-indigo-300/60 uppercase tracking-widest">Diagnóstico em Tempo Real</p>
          </div>
        </div>
      </div>

      <div className="space-y-4 relative z-10">
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
                   <Info className="w-4 h-4 text-indigo-400" />}
                </div>
                <p className="text-sm font-medium leading-relaxed opacity-90">
                  {text.replace(/[⚠️🚨❌✅💡🔍]/g, '').trim()}
                </p>
              </div>
            </div>
          );
        })}

        <div className="pt-4 mt-2 border-t border-white/10">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="font-bold opacity-60">Score de Eficiência Estrutural</span>
            <span className="font-black text-indigo-400">{efficiencyScore}%</span>
          </div>
          <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-1000" 
              style={{ width: `${efficiencyScore}%` }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}
