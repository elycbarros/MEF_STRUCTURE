"use client";

import React from "react";
import { 
  PlugZap, 
  Gauge, 
  RefreshCw, 
  Link2, 
  Zap, 
  RotateCcw 
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MainHeaderProps {
  selectedMode: "academic" | "professional" | null;
  setSelectedMode: (mode: any) => void;
  systemType: "radier" | "laje";
  setSystemType: (type: "radier" | "laje") => void;
  checkApiConnection: () => void;
  apiChecking: boolean;
  runOptimization: () => void;
  runAnalysis: () => void;
  runFrameAnalysis: () => void;
  loading: boolean;
  apiBaseUrl: string;
  apiOnline: boolean | null;
  statusMessage: string;
  optLogs: any[];
  activeTab: string;
  setActiveTab: (tab: any) => void;
}

export function MainHeader({
  selectedMode,
  setSelectedMode,
  systemType,
  setSystemType,
  checkApiConnection,
  apiChecking,
  runOptimization,
  runAnalysis,
  runFrameAnalysis,
  loading,
  apiBaseUrl,
  apiOnline,
  statusMessage,
  optLogs,
  activeTab,
  setActiveTab
}: MainHeaderProps) {
  const isProfessional = selectedMode === "professional";

  return (
    <header className={cn(
      "rounded-[40px] border p-8 transition-all duration-700 shadow-2xl",
      isProfessional 
        ? "bg-[#16191f] border-white/5 shadow-blue-900/10" 
        : "bg-white border-slate-200 shadow-slate-200/50"
    )}>
      <div className="flex flex-wrap items-center justify-between gap-8">
        <div className="space-y-3">
          <div className="flex items-center gap-4">
            <h1 className={cn(
              "flex items-center gap-3 text-3xl font-black tracking-tighter",
              isProfessional ? "text-white" : "text-slate-900"
            )}>
              Engine {isProfessional ? "UFO" : "MESTRE"}
              <span className={cn(
                "rounded-xl px-3 py-1 text-[10px] font-black uppercase tracking-widest",
                isProfessional ? "bg-blue-600 text-white" : "bg-blue-100 text-blue-700"
              )}>
                {isProfessional ? "Forense" : "Acadêmico"}
              </span>
            </h1>
            
            <div className="flex items-center gap-2">
              {selectedMode === "academic" && activeTab !== "dashboard" && (
                <button 
                  onClick={() => setActiveTab("dashboard")}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition shadow-lg"
                >
                  <Gauge className="h-4 w-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">Painel</span>
                </button>
              )}

              <button 
                onClick={() => setSelectedMode(null)}
                className={cn(
                  "p-2 rounded-xl transition-all hover:scale-110",
                  isProfessional ? "bg-white/5 text-white/40 hover:text-white" : "bg-slate-100 text-slate-400 hover:text-slate-900"
                )}
                title="Mudar Engine"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {isProfessional && (
              <div className="flex overflow-hidden rounded-xl border border-white/5 bg-white/5 p-1">
                <button
                  onClick={() => setSystemType("radier")}
                  className={cn(
                    "rounded-lg px-4 py-1.5 text-[10px] font-black uppercase transition-all",
                    systemType === "radier" ? "bg-white text-blue-600 shadow-sm" : "text-white/40 hover:text-white"
                  )}
                >
                  Radier
                </button>
                <button
                  onClick={() => setSystemType("laje")}
                  className={cn(
                    "rounded-lg px-4 py-1.5 text-[10px] font-black uppercase transition-all",
                    systemType === "laje" ? "bg-white text-blue-600 shadow-sm" : "text-white/40 hover:text-white"
                  )}
                >
                  Laje
                </button>
              </div>
            )}
            <p className={cn(
              "text-xs font-bold",
              isProfessional ? "text-white/40" : "text-slate-500"
            )}>
              {isProfessional 
                ? (systemType === "radier" ? "Placas sobre solo elástico (Winkler)" : "Placas sobre apoios discretos")
                : "Didática e dimensionamento assistido (NBR 6118)"}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <button
            type="button"
            onClick={checkApiConnection}
            disabled={apiChecking}
            className={cn(
              "inline-flex items-center gap-3 rounded-2xl px-6 py-3 text-sm font-black transition-all hover:scale-105 active:scale-95 disabled:opacity-60",
              isProfessional ? "bg-white/5 border border-white/10 text-white" : "bg-slate-100 text-slate-600"
            )}
          >
            <PlugZap className={cn("h-4 w-4", apiChecking && "animate-pulse")} />
            {apiChecking ? "Check..." : "API Connect"}
          </button>

          {isProfessional && (
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={runOptimization}
                disabled={loading}
                className="inline-flex items-center gap-3 rounded-2xl bg-teal-600 px-6 py-3 text-sm font-black text-white shadow-lg shadow-teal-900/20 transition-all hover:scale-105 hover:bg-teal-500"
              >
                <Gauge className={cn("h-4 w-4", loading && "animate-pulse")} />
                Auto-Design
              </button>
              <button
                type="button"
                onClick={runAnalysis}
                disabled={loading}
                className="inline-flex items-center gap-3 rounded-2xl bg-white px-6 py-3 text-sm font-black text-black transition-all hover:scale-105"
              >
                <Zap className={cn("h-4 w-4", loading && "animate-pulse")} />
                Run MEF
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-4 text-[10px] font-black uppercase tracking-[0.2em]">
        <div className={cn(
          "flex items-center gap-2 rounded-full px-4 py-2 border",
          isProfessional ? "bg-white/5 border-white/5 text-white/50" : "bg-slate-50 border-slate-100 text-slate-400"
        )}>
          <span className="opacity-50">Base:</span> {apiBaseUrl}
        </div>
        <div className={cn(
          "flex items-center gap-2 rounded-full px-4 py-2",
          apiOnline === null ? "bg-slate-100 text-slate-400" : apiOnline ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
        )}>
          <div className={cn("h-1.5 w-1.5 rounded-full", apiOnline === null ? "bg-slate-400" : apiOnline ? "bg-green-500" : "bg-red-500")} />
          {apiOnline === null ? "Unknown" : apiOnline ? "API Online" : "API Offline"}
        </div>
        <div className={cn(
          "flex items-center gap-2 rounded-full px-4 py-2",
          isProfessional ? "bg-blue-500/10 text-blue-400" : "bg-blue-50 text-blue-600"
        )}>
          {statusMessage}
        </div>
      </div>
    </header>
  );
}
