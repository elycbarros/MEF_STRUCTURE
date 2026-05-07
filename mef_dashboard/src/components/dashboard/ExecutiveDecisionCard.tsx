"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle, XCircle, ArrowRight } from "lucide-react";
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
        color: "text-apple-green",
        bg: "bg-apple-green/10",
        border: "border-apple-green/20",
        label: "LIBERADO PARA ESTUDO",
      }
    : isHold
    ? {
        icon: AlertTriangle,
        color: "text-apple-orange",
        bg: "bg-apple-orange/10",
        border: "border-apple-orange/20",
        label: "REVISÃO NECESSÁRIA",
      }
    : {
        icon: XCircle,
        color: "text-apple-red",
        bg: "bg-apple-red/10",
        border: "border-apple-red/20",
        label: "NÃO RECOMENDADO",
      };

  const Icon = statusConfig.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "relative overflow-hidden rounded-apple border p-6 shadow-apple glass",
        statusConfig.border
      )}
    >
      {/* Background decoration */}
      <div className={cn("absolute -right-8 -top-8 h-32 w-32 rounded-full blur-3xl opacity-20", statusConfig.bg)} />

      <div className="relative z-10">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={cn("rounded-full p-2", statusConfig.bg)}>
              <Icon className={cn("h-6 w-6", statusConfig.color)} />
            </div>
            <div>
              <span className={cn("text-[10px] font-black uppercase tracking-widest", statusConfig.color)}>
                {statusConfig.label}
              </span>
              <h3 className="text-xl font-black text-apple-text">
                {decision.executive_label || "Sem Diagnóstico"}
              </h3>
            </div>
          </div>
          
          <div className="hidden sm:flex gap-2">
            {decision.blocking_count ? (
              <div className="bg-apple-red/10 text-apple-red px-2 py-1 rounded-md text-[10px] font-bold">
                {decision.blocking_count} BLOQUEIOS
              </div>
            ) : null}
            {decision.restriction_count ? (
              <div className="bg-apple-orange/10 text-apple-orange px-2 py-1 rounded-md text-[10px] font-bold">
                {decision.restriction_count} RESTRIÇÕES
              </div>
            ) : null}
          </div>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <p className="text-[11px] font-bold text-apple-muted uppercase tracking-wider">Recomendação Principal</p>
              <p className="mt-1 text-sm font-medium leading-relaxed text-apple-text/80">
                {decision.main_recommendation || "Execute a análise para obter recomendações."}
              </p>
            </div>
            
            <div className="flex items-start gap-3 rounded-apple-inner bg-apple-bg/50 p-4 border border-black/5">
              <div className="mt-1 rounded-full bg-apple-blue p-1">
                <ArrowRight className="h-3 w-3 text-white" />
              </div>
              <div>
                <p className="text-[11px] font-bold text-apple-muted uppercase tracking-wider">Próxima Ação</p>
                <p className="mt-1 text-sm font-bold text-apple-text">
                  {decision.first_priority_action || decision.next_step || "Nenhuma ação imediata pendente."}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-apple-inner bg-white/40 p-4 border border-white/40 space-y-3">
             <p className="text-[11px] font-bold text-apple-muted uppercase tracking-wider">Métricas Chave</p>
             <div className="grid grid-cols-2 gap-4">
                <MiniMetric label={isLaje ? "Flecha" : "Pressão"} value={isLaje ? (decision.settlement_ratio ? `${(decision.settlement_ratio * 100).toFixed(1)}%` : "N/D") : (decision.pressure_ratio ? `${(decision.pressure_ratio * 100).toFixed(1)}%` : "N/D")} />
                <MiniMetric label="Punção" value={decision.punching_ratio ? `${(decision.punching_ratio * 100).toFixed(1)}%` : "N/D"} />
                <MiniMetric label={isLaje ? "Efeito (L/d)" : "Recalque"} value={decision.settlement_ratio ? `${(decision.settlement_ratio * 100).toFixed(1)}%` : "N/D"} />
                <MiniMetric label="Confiança" value={decision.kv_confidence ? `${(decision.kv_confidence * 100).toFixed(0)}%` : "N/D"} />
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] font-semibold text-apple-muted">{label}</p>
      <p className="text-sm font-black text-apple-text">{value}</p>
    </div>
  );
}
