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
  return (
    <header className="rounded-3xl border border-white/60 bg-white/70 p-6 shadow-[0_10px_28px_rgba(0,0,0,0.05)]">
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="flex items-center gap-2 text-3xl font-black tracking-tight">
              Engine {selectedMode === "academic" ? "MESTRE" : "UFO"}
              <span className={`rounded-lg px-2 py-0.5 text-[10px] font-black uppercase ${selectedMode === "academic" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"}`}>
                {selectedMode === "academic" ? "Acadêmico" : "Forense"}
              </span>
              
              {selectedMode === "academic" && activeTab !== "dashboard" && (
                <button 
                  onClick={() => setActiveTab("dashboard")}
                  className="ml-2 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition shadow-lg"
                  title="Voltar ao Painel"
                >
                  <Gauge className="h-4 w-4" />
                  <span className="text-[10px] font-black uppercase">Painel</span>
                </button>
              )}

              <button 
                onClick={() => setSelectedMode(null)}
                className="ml-2 p-1.5 rounded-lg text-[#666a73] hover:bg-black/5 hover:text-[#0071e3] transition"
                title="Mudar Engine"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            </h1>
            {selectedMode !== "academic" && (
              <div className="flex overflow-hidden rounded-lg border border-black/5 bg-black/5 p-0.5">
                <button
                  onClick={() => setSystemType("radier")}
                  className={cn(
                    "px-3 py-1 text-[10px] font-black uppercase transition",
                    systemType === "radier" ? "bg-white text-[#0071e3] shadow-sm" : "text-[#666a73] hover:text-[#1d1d1f]"
                  )}
                >
                  Radier
                </button>
                <button
                  onClick={() => setSystemType("laje")}
                  className={cn(
                    "px-3 py-1 text-[10px] font-black uppercase transition",
                    systemType === "laje" ? "bg-white text-[#0071e3] shadow-sm" : "text-[#666a73] hover:text-[#1d1d1f]"
                  )}
                >
                  Laje
                </button>
              </div>
            )}
          </div>
          {selectedMode !== "academic" && (
            <p className="mt-1 text-sm font-medium text-[#666a73]">
              {systemType === "radier" 
                ? "Análise de placas sobre solo elástico (Winkler)" 
                : "Análise de placas sobre apoios discretos e vigas"}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={checkApiConnection}
            disabled={apiChecking}
            className="inline-flex items-center gap-2 rounded-xl border border-[#0071e3]/20 bg-[#0071e3]/10 px-4 py-2 text-sm font-bold text-[#0071e3] transition hover:bg-[#0071e3]/15 disabled:opacity-60"
          >
            <PlugZap className="h-4 w-4" />
            {apiChecking ? "Verificando..." : "Testar API"}
          </button>
          {selectedMode !== "academic" && (
            <>
              <button
                type="button"
                onClick={runOptimization}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-[#0f766e] px-4 py-2 text-sm font-bold text-white shadow-[0_10px_24px_rgba(15,118,110,0.28)] transition hover:bg-[#0d645e] disabled:opacity-60"
              >
                <Gauge className={`h-4 w-4 ${loading ? "animate-pulse" : ""}`} />
                {loading ? "Otimizando..." : "Auto-Dimensionar"}
              </button>
              <button
                type="button"
                onClick={runAnalysis}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl border border-black/10 bg-white px-4 py-2 text-sm font-black text-black transition hover:bg-black/5 disabled:opacity-60"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                {loading ? "Processando..." : "Análise Rápida"}
              </button>
              <button
                type="button"
                onClick={runFrameAnalysis}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl border-2 border-[#6366f1] bg-[#6366f1]/5 px-4 py-2 text-sm font-bold text-[#6366f1] transition hover:bg-[#6366f1]/10 disabled:opacity-60"
              >
                <Link2 className={`h-4 w-4 ${loading ? "animate-pulse" : ""}`} />
                {loading ? "Unificando..." : "Análise Global"}
              </button>
            </>
          )}
          
          {selectedMode !== "academic" && (
            <button
              type="button"
              onClick={runAnalysis}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl bg-[#0071e3] px-4 py-2 text-sm font-bold text-white shadow-[0_10px_24px_rgba(0,113,227,0.28)] transition hover:bg-[#0062c7] disabled:opacity-60"
            >
              <Zap className={`h-4 w-4 ${loading ? "animate-pulse" : ""}`} />
              {loading ? "Calculando..." : systemType === "laje" ? "Análise MEF Lajes" : "Análise MEF Radier"}
            </button>
          )}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
        <span className="rounded-full bg-white px-3 py-1 font-semibold text-[#5f6470]">API: {apiBaseUrl}</span>
        <span
          className={`rounded-full px-3 py-1 font-semibold ${
            apiOnline === null
              ? "bg-[#f0f2f6] text-[#5f6470]"
              : apiOnline
                ? "bg-[#e6f9ef] text-[#1f8f56]"
                : "bg-[#ffecec] text-[#c52626]"
          }`}
        >
          {apiOnline === null ? "Conexão não testada" : apiOnline ? "API online" : "API offline"}
        </span>
        <span className="rounded-full bg-[#fff7e8] px-3 py-1 font-semibold text-[#9a6d00]">{statusMessage}</span>
      </div>
      {optLogs.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          {optLogs.map((log, i) => (
            <span key={i} className={`rounded-md px-2 py-1 font-medium ${log.success ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
              h={log.h}m: {log.success ? "OK" : `Falha (${log.reasons.join(", ")})`}
            </span>
          ))}
        </div>
      )}
    </header>
  );
}
