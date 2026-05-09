"use client";

import React from "react";
import { CheckCircle2, Clock, AlertTriangle, XCircle, ExternalLink, Activity, Binary } from "lucide-react";
import { cn } from "@/lib/utils";

interface Solution {
  id: string;
  nome: string;
  maturidade: "implementado" | "orientativo" | "planejado" | "fora_do_escopo";
  viabilidade: string;
  quando_estudar: string;
  disponivel: boolean;
}

interface SolutionComparatorProps {
  solutions: Solution[];
  nota?: string;
}

const MATURIDADE_CONFIG = {
  implementado: {
    label: "MODELO_VALIDADO",
    icon: CheckCircle2,
    color: "text-emerald-600",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  orientativo: {
    label: "MODELO_DIDÁTICO",
    icon: Clock,
    color: "text-blue-600",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  planejado: {
    label: "ALPHA_BUILD",
    icon: AlertTriangle,
    color: "text-amber-600",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  fora_do_escopo: {
    label: "DEPRECATED_SOLVER",
    icon: XCircle,
    color: "text-slate-500",
    bg: "bg-slate-500/5",
    border: "border-slate-200",
  },
};

function viabilidadeColor(v: string): string {
  const vl = v.toLowerCase();
  if (vl.includes("viável preliminarmente") || vl.includes("alternativa madura")) return "text-emerald-600";
  if (vl.includes("alertas") || vl.includes("reserva") || vl.includes("estudar")) return "text-amber-600";
  if (vl.includes("restrições") || vl.includes("não liberado")) return "text-red-600";
  if (vl.includes("alternativa") || vl.includes("fora")) return "text-slate-500";
  return "text-slate-900";
}

export function SolutionComparator({ solutions, nota }: SolutionComparatorProps) {
  return (
    <div className="space-y-6">
      {/* Tabela desktop */}
      <div className="hidden md:block overflow-hidden rounded-[2rem] border border-slate-200 bg-white/50 backdrop-blur-xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/[0.02] border-b border-slate-200">
              <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Solução Estrutural</th>
              <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Maturidade Solver</th>
              <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Viabilidade Normativa</th>
              <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">Observações do Motor</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {solutions.map((s) => {
              const cfg = MATURIDADE_CONFIG[s.maturidade];
              const Icon = cfg.icon;
              return (
                <tr key={s.id} className={cn(
                   "transition-colors group",
                   s.disponivel ? "bg-white/[0.01] hover:bg-white/[0.03]" : "opacity-40 grayscale"
                )}>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                       <p className="font-black text-sm text-slate-900 tracking-tight">{s.nome}</p>
                       {s.disponivel && (
                         <span className="text-[8px] font-black px-2 py-0.5 rounded-full bg-blue-600/20 text-blue-600 border border-blue-500/30 tracking-widest animate-pulse">
                           LIVE
                         </span>
                       )}
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className={cn(
                       "inline-flex items-center gap-2 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border",
                       cfg.bg, cfg.color, cfg.border
                    )}>
                      <Icon className="h-3 w-3" />
                      {cfg.label}
                    </span>
                  </td>
                  <td className={cn("px-6 py-5 font-black text-xs uppercase tracking-wider", viabilidadeColor(s.viabilidade))}>
                    {s.viabilidade}
                  </td>
                  <td className="px-6 py-5 text-[10px] text-slate-500 font-bold leading-relaxed max-w-xs group-hover:text-slate-600 transition-colors">
                    {s.quando_estudar}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Cards mobile */}
      <div className="md:hidden space-y-4">
        {solutions.map((s) => {
          const cfg = MATURIDADE_CONFIG[s.maturidade];
          const Icon = cfg.icon;
          return (
            <div key={s.id} className={cn(
               "p-6 rounded-[2rem] border transition-all",
               cfg.border,
               s.disponivel ? "bg-white/80 shadow-xl" : "bg-white/50 opacity-50 grayscale"
            )}>
              <div className="flex items-start justify-between gap-4 mb-4">
                <p className="font-black text-sm text-slate-900 tracking-tight">{s.nome}</p>
                <span className={cn(
                   "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border",
                   cfg.bg, cfg.color, cfg.border, "shrink-0"
                )}>
                  <Icon className="h-3 w-3" />
                  {cfg.label}
                </span>
              </div>
              <p className={cn("text-xs font-black uppercase tracking-widest mb-2", viabilidadeColor(s.viabilidade))}>{s.viabilidade}</p>
              <p className="text-[10px] text-slate-500 font-bold leading-relaxed">{s.quando_estudar}</p>
            </div>
          );
        })}
      </div>

      {/* Nota de escopo */}
      {nota && (
        <div className="flex items-start gap-4 p-5 rounded-[1.5rem] bg-blue-600/5 border border-blue-500/10 text-[10px] font-bold text-blue-600/80 leading-relaxed uppercase tracking-widest">
          <Binary className="h-4 w-4 shrink-0 mt-0.5 opacity-50" />
          <span>{nota}</span>
        </div>
      )}
    </div>
  );
}
