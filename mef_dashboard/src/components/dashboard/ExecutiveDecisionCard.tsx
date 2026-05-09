"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle, XCircle, ArrowRight, Activity, ShieldCheck, Target } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ExecutiveDecisionProps {
  decision: {
    executive_label?: string;
    decision_status?: string;
    go_no_go?: "go" | "hold" | "no_go" | string;
    main_recommendation?: string;
    next_step?: string;
    first_priority_action?: string;
    alert_count?: number;
    restriction_count?: number;
    blocking_count?: number;
    pressure_ratio?: number;
    punching_ratio?: number;
    settlement_ratio?: number;
    kv_confidence?: number;
  };
  isLaje?: boolean;
}

export function ExecutiveDecisionCard({ decision, isLaje = false }: ExecutiveDecisionProps) {
  const isGo = decision.go_no_go === "go_preliminar" || decision.go_no_go === "go";
  const isHold = decision.go_no_go === "hold" || decision.go_no_go === "conditional_go";
  const isNoGo = decision.go_no_go === "no_go" || decision.go_no_go === "estudar_alternativa";

  const statusConfig = isGo
    ? {
        icon: CheckCircle2,
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/30",
        glow: "shadow-[0_0_20px_rgba(16,185,129,0.15)]",
        label: "STATUS: LIBERADO",
      }
    : isHold
    ? {
        icon: AlertTriangle,
        color: "text-amber-400",
        bg: "bg-amber-500/10",
        border: "border-amber-500/30",
        glow: "shadow-[0_0_20px_rgba(245,158,11,0.15)]",
        label: "STATUS: REVISÃO REQUERIDA",
      }
    : {
        icon: XCircle,
        color: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        glow: "shadow-[0_0_20px_rgba(239,68,68,0.15)]",
        label: "STATUS: CRÍTICO",
      };

  const Icon = statusConfig.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "relative overflow-hidden rounded-[2.5rem] border p-8 shadow-2xl backdrop-blur-3xl transition-all duration-500",
        statusConfig.border,
        statusConfig.glow,
        "bg-[#0a0a0c]/60"
      )}
    >
      {/* Structural Decoration */}
      <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
         <ShieldCheck className="w-32 h-32" />
      </div>

      <div className="relative z-10">
        <div className="flex items-start justify-between gap-6 mb-8">
          <div className="flex items-center gap-5">
            <div className={cn("rounded-[1.25rem] p-4 border", statusConfig.bg, statusConfig.border)}>
              <Icon className={cn("h-8 w-8", statusConfig.color)} />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className={cn("text-[10px] font-black uppercase tracking-[0.2em]", statusConfig.color)}>
                  {statusConfig.label}
                </span>
                <div className="w-1.5 h-1.5 rounded-full animate-pulse bg-current" />
              </div>
              <h3 className="text-2xl font-black text-white tracking-tight leading-none">
                {decision.executive_label || "Auditoria em Processo"}
              </h3>
            </div>
          </div>
          
          <div className="hidden sm:flex flex-col items-end gap-2">
            {decision.blocking_count ? (
              <div className="bg-red-500/10 text-red-400 border border-red-500/20 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">
                {decision.blocking_count} BLOQUEIOS_MEF
              </div>
            ) : null}
            {decision.restriction_count ? (
              <div className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest">
                {decision.restriction_count} ALERTAS_NORMATIVOS
              </div>
            ) : null}
          </div>
        </div>

        <div className="grid gap-10 md:grid-cols-2">
          <div className="space-y-6">
            <div className="p-6 rounded-[2rem] bg-white/[0.02] border border-white/5">
              <div className="flex items-center gap-2 mb-3">
                 <Target className="w-3.5 h-3.5 text-blue-400" />
                 <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Parecer de Engenharia</p>
              </div>
              <p className="text-sm font-bold leading-relaxed text-slate-300">
                {decision.main_recommendation || "Aguardando síntese do motor de inferência..."}
              </p>
            </div>
            
            <div className="flex items-start gap-4 rounded-[2rem] bg-blue-600/5 p-6 border border-blue-500/10 group hover:bg-blue-600/10 transition-colors">
              <div className="mt-1 rounded-xl bg-blue-600 p-2 shadow-lg shadow-blue-600/20 group-hover:scale-110 transition-transform">
                <ArrowRight className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-1">Diretriz Prioritária</p>
                <p className="text-sm font-black text-white">
                  {decision.first_priority_action || decision.next_step || "Nenhuma ação corretiva mapeada."}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-[2rem] bg-black/40 p-8 border border-white/5 space-y-6">
             <div className="flex items-center justify-between">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Vectores de Performance</p>
                <Activity className="w-3 h-3 text-slate-600" />
             </div>
             <div className="grid grid-cols-2 gap-y-6 gap-x-8">
                <MiniMetric label={isLaje ? "FLECHA_MAX" : "PRESSÃO_SOLO"} value={isLaje ? (decision.settlement_ratio ? `${(decision.settlement_ratio * 100).toFixed(1)}%` : "0.0%") : (decision.pressure_ratio ? `${(decision.pressure_ratio * 100).toFixed(1)}%` : "0.0%")} status={isGo ? "ok" : "warn"} />
                <MiniMetric label="PUNÇÃO_LU" value={decision.punching_ratio ? `${(decision.punching_ratio * 100).toFixed(1)}%` : "0.0%"} status={isGo ? "ok" : "warn"} />
                <MiniMetric label={isLaje ? "FISSURA_EL" : "RECALQUE_REL"} value={decision.settlement_ratio ? `${(decision.settlement_ratio * 100).toFixed(1)}%` : "0.0%"} status={isGo ? "ok" : "warn"} />
                <MiniMetric label="CONF_SOLVER" value={decision.kv_confidence ? `${(decision.kv_confidence * 100).toFixed(0)}%` : "99%"} status="ok" />
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function MiniMetric({ label, value, status = "ok" }: { label: string; value: string; status?: "ok" | "warn" | "fail" }) {
  return (
    <div className="space-y-1">
      <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{label}</p>
      <div className="flex items-end gap-2">
         <p className="text-xl font-black text-white tracking-tighter">{value}</p>
         <div className={cn(
            "w-1 h-1 rounded-full mb-1.5",
            status === "ok" ? "bg-emerald-500" : status === "warn" ? "bg-amber-500" : "bg-red-500"
         )} />
      </div>
    </div>
  );
}
