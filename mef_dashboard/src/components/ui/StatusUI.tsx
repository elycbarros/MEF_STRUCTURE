"use client";

import React from "react";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

export type RiskSeverity = "green" | "yellow" | "red";

export function RiskBadge({ severity }: { severity: RiskSeverity }) {
  const configs = {
    green: { bg: "bg-green-100", text: "text-green-700", label: "Baixo Risco", icon: CheckCircle2 },
    yellow: { bg: "bg-yellow-100", text: "text-yellow-700", label: "Atenção", icon: AlertTriangle },
    red: { bg: "bg-red-100", text: "text-red-700", label: "Crítico", icon: XCircle },
  };

  const { bg, text, label, icon: Icon } = configs[severity] || configs.yellow;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-black uppercase ${bg} ${text}`}>
      <Icon className="h-3.5 w-3.5" />
      {label}
    </span>
  );
}

export function RiskDot({ severity }: { severity: RiskSeverity }) {
  const colors = {
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    red: "bg-red-500",
  };
  return <div className={`h-2 w-2 rounded-full ${colors[severity] || "bg-gray-400"}`} />;
}

export function MetricPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[#e2e8f0] bg-[#f8fafc] p-2 text-center">
      <p className="text-[10px] font-bold uppercase tracking-wider text-[#64748b]">{label}</p>
      <p className="mt-0.5 text-sm font-black text-[#1e293b]">{value}</p>
    </div>
  );
}
