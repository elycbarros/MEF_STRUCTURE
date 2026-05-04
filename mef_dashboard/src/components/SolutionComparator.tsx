"use client";

import React from "react";
import { CheckCircle2, Clock, AlertTriangle, XCircle, ExternalLink } from "lucide-react";

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
    label: "Implementado",
    icon: CheckCircle2,
    color: "text-apple-green",
    bg: "bg-apple-green/10",
    border: "border-apple-green/20",
  },
  orientativo: {
    label: "Orientativo",
    icon: Clock,
    color: "text-apple-blue",
    bg: "bg-apple-blue/10",
    border: "border-apple-blue/20",
  },
  planejado: {
    label: "Planejado",
    icon: AlertTriangle,
    color: "text-yellow-600",
    bg: "bg-yellow-50",
    border: "border-yellow-200",
  },
  fora_do_escopo: {
    label: "Fora do escopo",
    icon: XCircle,
    color: "text-apple-muted",
    bg: "bg-apple-bg/30",
    border: "border-black/5",
  },
};

function viabilidadeColor(v: string): string {
  const vl = v.toLowerCase();
  if (vl.includes("viável preliminarmente") || vl.includes("alternativa madura")) return "text-apple-green";
  if (vl.includes("alertas") || vl.includes("reserva") || vl.includes("estudar")) return "text-yellow-600";
  if (vl.includes("restrições") || vl.includes("não liberado")) return "text-orange-500";
  if (vl.includes("alternativa") || vl.includes("fora")) return "text-apple-muted";
  return "text-apple-text";
}

export function SolutionComparator({ solutions, nota }: SolutionComparatorProps) {
  return (
    <div className="space-y-3">
      {/* Tabela desktop */}
      <div className="hidden md:block overflow-hidden rounded-apple-inner border border-black/5">
        <table className="w-full text-sm text-left">
          <thead className="bg-apple-bg/50">
            <tr>
              <th className="px-4 py-3 text-[10px] font-black text-apple-muted uppercase tracking-wide">Solução</th>
              <th className="px-4 py-3 text-[10px] font-black text-apple-muted uppercase tracking-wide">Maturidade</th>
              <th className="px-4 py-3 text-[10px] font-black text-apple-muted uppercase tracking-wide">Viabilidade</th>
              <th className="px-4 py-3 text-[10px] font-black text-apple-muted uppercase tracking-wide">Quando Estudar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-black/5">
            {solutions.map((s) => {
              const cfg = MATURIDADE_CONFIG[s.maturidade];
              const Icon = cfg.icon;
              return (
                <tr key={s.id} className={s.disponivel ? "bg-white" : "bg-apple-bg/10"}>
                  <td className="px-4 py-3 font-bold text-apple-text">
                    {s.nome}
                    {s.disponivel && (
                      <span className="ml-2 text-[9px] font-black px-1.5 py-0.5 rounded-full bg-apple-green/10 text-apple-green">
                        ATIVO
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold ${cfg.bg} ${cfg.color} border ${cfg.border}`}>
                      <Icon className="h-3 w-3" />
                      {cfg.label}
                    </span>
                  </td>
                  <td className={`px-4 py-3 font-bold text-sm ${viabilidadeColor(s.viabilidade)}`}>
                    {s.viabilidade}
                  </td>
                  <td className="px-4 py-3 text-[11px] text-apple-muted leading-relaxed">
                    {s.quando_estudar}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Cards mobile */}
      <div className="md:hidden space-y-3">
        {solutions.map((s) => {
          const cfg = MATURIDADE_CONFIG[s.maturidade];
          const Icon = cfg.icon;
          return (
            <div key={s.id} className={`p-4 rounded-xl border ${cfg.border} ${s.disponivel ? "bg-white" : "bg-apple-bg/20"}`}>
              <div className="flex items-start justify-between gap-2">
                <p className="font-bold text-sm text-apple-text">{s.nome}</p>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${cfg.bg} ${cfg.color} border ${cfg.border} shrink-0`}>
                  <Icon className="h-3 w-3" />
                  {cfg.label}
                </span>
              </div>
              <p className={`text-sm font-bold mt-1 ${viabilidadeColor(s.viabilidade)}`}>{s.viabilidade}</p>
              <p className="text-[11px] text-apple-muted mt-1 leading-relaxed">{s.quando_estudar}</p>
            </div>
          );
        })}
      </div>

      {/* Nota de escopo */}
      {nota && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-apple-bg/30 border border-black/5 text-[11px] text-apple-muted">
          <ExternalLink className="h-3.5 w-3.5 shrink-0 mt-0.5" />
          <span>{nota}</span>
        </div>
      )}
    </div>
  );
}
