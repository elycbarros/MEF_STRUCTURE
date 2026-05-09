"use client";

import React from "react";
import { 
  PlugZap, 
  Gauge, 
  RefreshCw, 
  Link2, 
  Zap, 
  RotateCcw,
  Cpu,
  ShieldAlert,
  Database,
  Layers,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

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
  secondaryTabs?: { id: string, label: string, icon: any }[];
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
  setActiveTab,
  secondaryTabs = []
}: MainHeaderProps) {
  const isProfessional = selectedMode === "professional";

  return (
    <header className={cn(
      "rounded-[2.5rem] border p-8 transition-all duration-700 relative overflow-hidden group",
      "bg-slate-100/60 border-slate-200 backdrop-blur-xl shadow-2xl shadow-black/40"
    )}>
      {/* Decorative Gradient Glow */}
      <div className="absolute -top-24 -left-24 w-64 h-64 bg-blue-600/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-purple-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 flex flex-wrap items-center justify-between gap-8">
        <div className="space-y-4">
          <div className="flex items-center gap-6">
            <div className="flex flex-col">
              <div className="flex items-center gap-3">
                <h1 className="text-4xl font-black tracking-tighter text-slate-900">
                  Structural <span className="text-blue-500">{isProfessional ? "Engine" : "Mestre"}</span>
                </h1>
                <span className={cn(
                  "rounded-full px-4 py-1 text-[9px] font-black uppercase tracking-[0.2em] border",
                  isProfessional 
                    ? "bg-blue-600/10 border-blue-600/30 text-blue-600" 
                    : "bg-emerald-600/10 border-emerald-600/30 text-emerald-600"
                )}>
                  {isProfessional ? "Forense High-Tier" : "Pedagogical Lab"}
                </span>
              </div>
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mt-1 ml-1">
                Structural Intelligence Suite v24.4.1
              </p>
            </div>
            
            <div className="h-10 w-px bg-white/5 mx-2" />

            <div className="flex items-center gap-3">
              <button 
                onClick={() => setSelectedMode(null)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white/5 border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-white/10 transition-all hover:scale-105 active:scale-95 group"
                title="Mudar Engine"
              >
                <RotateCcw className="h-4 w-4 group-hover:-rotate-90 transition-transform duration-500" />
                <span className="text-[9px] font-black uppercase tracking-widest">Alternar</span>
              </button>

              <div className="h-8 w-px bg-slate-200 mx-1" />

              {/* Secondary Navigation */}
              <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-50/50 border border-slate-200">
                <span className="text-[7px] font-black uppercase tracking-[0.3em] text-slate-400 ml-2 mr-3">Engine Utilities:</span>
                {secondaryTabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        "flex items-center gap-2 px-3 py-1.5 rounded-xl transition-all",
                        isActive 
                          ? "bg-white text-blue-600 shadow-sm border border-slate-200" 
                          : "text-slate-500 hover:text-slate-900 hover:bg-white/50"
                      )}
                    >
                      <Icon className="h-3 w-3" />
                      <span className="text-[8px] font-black uppercase tracking-widest">{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {selectedMode === "academic" && activeTab !== "dashboard" && (
                <button 
                  onClick={() => setActiveTab("dashboard")}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-blue-600 text-white hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/20"
                >
                  <Gauge className="h-4 w-4" />
                  <span className="text-[9px] font-black uppercase tracking-widest">Painel</span>
                </button>
              )}
            </div>
          </div>

        </div>

        <div className="flex items-center gap-4">
          {/* Action Hub */}
          <div className="flex items-center gap-3 p-2 rounded-[2rem] bg-white/5 border border-slate-200 backdrop-blur-xl">
            <button
              type="button"
              onClick={checkApiConnection}
              disabled={apiChecking}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-6 py-3 text-[10px] font-black uppercase tracking-widest transition-all",
                apiOnline ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" : "bg-white/5 text-slate-700 border border-slate-200"
              )}
            >
              <PlugZap className={cn("h-4 w-4", apiChecking && "animate-pulse")} />
              {apiChecking ? "Syncing..." : "API Hub"}
            </button>

            {isProfessional && (
              <>
                <button
                  type="button"
                  onClick={runOptimization}
                  disabled={loading}
                  className="flex items-center gap-3 rounded-2xl bg-gradient-to-br from-blue-700 to-blue-900 px-6 py-3 text-[10px] font-black uppercase tracking-widest text-slate-900 shadow-xl shadow-blue-900/20 hover:scale-105 active:scale-95 transition-all"
                >
                  <Cpu className={cn("h-4 w-4", loading && "animate-spin-slow")} />
                  Optimization
                </button>
                <button
                  type="button"
                  onClick={runAnalysis}
                  disabled={loading}
                  className="flex items-center gap-3 rounded-2xl bg-white px-7 py-3 text-[10px] font-black uppercase tracking-widest text-black hover:bg-blue-50 hover:scale-105 active:scale-95 transition-all shadow-2xl"
                >
                  <Zap className={cn("h-4 w-4", loading && "animate-pulse")} />
                  Solve MEF
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Real-time Telemetry Bar */}
      <div className="mt-8 flex flex-wrap items-center gap-4 text-[9px] font-black uppercase tracking-[0.2em] relative z-10">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/80 border border-slate-200 text-slate-500">
          <Database className="w-3 h-3 opacity-30" />
          <span className="opacity-60">Core:</span> {apiBaseUrl}
        </div>
        
        <div className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-lg border",
          apiOnline === null ? "bg-slate-900 border-slate-200 text-slate-600" 
            : apiOnline ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-600" 
            : "bg-red-500/5 border-red-500/20 text-red-600"
        )}>
          <div className={cn("h-1.5 w-1.5 rounded-full", apiOnline === null ? "bg-slate-600" : apiOnline ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-red-500")} />
          {apiOnline === null ? "Status: Unknown" : apiOnline ? "Engine Online" : "Engine Offline"}
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/5 border border-blue-500/20 text-blue-600">
          <Activity className="w-3 h-3 animate-pulse" />
          {statusMessage}
        </div>

        <div className="flex-1" />

        <div className="hidden lg:flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/5 border border-slate-200 text-slate-500">
          <ShieldAlert className="w-3 h-3" />
          <span>Normative Check: NBR 6118:2023 Active</span>
        </div>
      </div>
    </header>
  );
}
