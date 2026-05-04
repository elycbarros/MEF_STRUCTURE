"use client";

import React from "react";
import { 
  CheckCircle2, 
  StretchHorizontal, 
  Box, 
  Cpu, 
  Waves,
  Search,
  ArrowRight,
  ClipboardCheck,
  GraduationCap,
  Layers3,
  Share2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { getAcademicBacklogProgress } from "@/components/AcademicBacklogView";
import type { AcademicTabId } from "@/hooks/useProjectState";

interface AcademicDashboardProps {
  setActiveTab: (tab: AcademicTabId) => void;
  setSystemType: (type: "radier" | "laje") => void;
}

export function AcademicDashboard({ setActiveTab, setSystemType }: AcademicDashboardProps) {
  const backlogProgress = React.useMemo(() => getAcademicBacklogProgress(), []);

  const cards = [
    {
      id: "radier",
      label: "RADIER",
      subLabel: "Módulo Acadêmico",
      description: "Análise de placas sobre base elástica (Winkler). Ideal para fundações diretas.",
      icon: CheckCircle2,
      accent: "bg-blue-500",
      onClick: () => {
        setSystemType("radier");
        setActiveTab("geometria");
      }
    },
    {
      id: "laje",
      label: "LAJE",
      subLabel: "Módulo Acadêmico",
      description: "Cálculo de lajes isoladas sobre apoios discretos ou vigas rígidas.",
      icon: StretchHorizontal,
      accent: "bg-emerald-500",
      onClick: () => {
        setSystemType("laje");
        setActiveTab("geometria");
      }
    },
    {
      id: "vigacross",
      label: "VIGA CROSS",
      subLabel: "Método de Hardy Cross",
      description: "Análise de vigas contínuas através da distribuição de momentos. Foco pedagógico no passo-a-passo.",
      icon: Share2,
      accent: "bg-indigo-600",
      onClick: () => setActiveTab("vigacross")
    },
    {
      id: "especiais",
      label: "ESPECIAIS",
      subLabel: "Reservatórios / Piscinas",
      description: "Dimensionamento de contenções hidráulicas e elementos enterrados.",
      icon: Waves,
      accent: "bg-cyan-500",
      onClick: () => setActiveTab("especiais")
    },
    {
      id: "vigas",
      label: "VIGAS",
      subLabel: "Dimensionamento",
      description: "Cálculo de armaduras longitudinais e transversais (NBR 6118).",
      icon: Box,
      accent: "bg-amber-500",
      onClick: () => setActiveTab("vigas")
    },
    {
      id: "pilar",
      label: "PILAR",
      subLabel: "Dimensionamento",
      description: "Análise de esbeltez e dimensionamento à flexo-compressão normal.",
      icon: Cpu,
      accent: "bg-rose-500",
      onClick: () => setActiveTab("pilares_isolados")
    }
  ];

  return (
    <div className="space-y-8 py-4">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Ambiente de Aprendizagem</h3>
          <h2 className="mt-1 text-3xl font-black text-slate-900">Mestre Structural Lab</h2>
        </div>
        <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Trilha pedagogica</p>
              <p className="mt-1 text-xl font-black text-slate-950">{backlogProgress.progress}%</p>
            </div>
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white">
              <GraduationCap className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${backlogProgress.progress}%` }} />
          </div>
          <button
            type="button"
            onClick={() => setActiveTab("backlog")}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-black text-white transition hover:bg-blue-700"
          >
            Abrir backlog <ClipboardCheck className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card) => (
          <button
            key={card.id}
            onClick={card.onClick}
            className="group relative flex flex-col text-left p-6 h-64 rounded-[2rem] border border-slate-100 bg-white shadow-sm transition-all hover:shadow-2xl hover:-translate-y-2 overflow-hidden"
          >
            {/* Background Accent Decor */}
            <div className={cn(
              "absolute -right-4 -top-4 h-24 w-24 rounded-full opacity-[0.03] transition-all group-hover:scale-150 group-hover:opacity-[0.08]",
              card.accent
            )} />

            <div className={cn(
              "mb-6 flex h-14 w-14 items-center justify-center rounded-2xl text-white shadow-lg transition-transform group-hover:scale-110",
              card.accent
            )}>
              <card.icon className="h-7 w-7" />
            </div>

            <div className="flex-1">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">{card.subLabel}</p>
              <h3 className="text-xl font-black text-slate-900">{card.label}</h3>
              <p className="mt-3 text-xs font-semibold leading-relaxed text-slate-500 line-clamp-3">
                {card.description}
              </p>
            </div>

            <div className="mt-4 flex items-center gap-2 text-[10px] font-black uppercase tracking-wider text-slate-900 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0">
              Acessar Módulo <ArrowRight className="h-3 w-3" />
            </div>
          </button>
        ))}
      </div>

      {/* Footer Info */}
      <div className="rounded-3xl border border-dashed border-slate-200 p-8 text-center bg-slate-50/50">
        <Layers3 className="mx-auto mb-3 h-6 w-6 text-slate-400" />
        <p className="text-xs font-bold text-slate-400">
          Selecione um elemento para iniciar a análise acadêmica detalhada.
          <br />
          Os módulos utilizam as prescrições da <span className="text-slate-900">NBR 6118:2023</span>.
        </p>
      </div>
    </div>
  );
}
