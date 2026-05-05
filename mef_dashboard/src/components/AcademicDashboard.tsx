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
  Layers,
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
      subLabel: "Parede de Concreto",
      description: "Dimensionamento de paredes estruturais, escadas e elementos especiais.",
      icon: Layers,
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
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between mb-12">
        <div className="relative">
          <div className="absolute -left-4 top-0 h-full w-1 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full" />
          <h3 className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400 pl-4">Engineered Education</h3>
          <h2 className="mt-1 text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-slate-900 to-slate-600 tracking-tighter pl-4">
            Mestre Structural Lab
          </h2>
        </div>
        
        <div className="w-full max-w-sm rounded-[2rem] border border-white/50 bg-white/40 backdrop-blur-xl p-6 shadow-[0_8px_32px_0_rgba(0,0,0,0.05)]">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div className="space-y-1">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Trilha Pedagógica</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black text-slate-950">{backlogProgress.progress}%</span>
                <span className="text-[10px] font-black text-slate-400 uppercase">Concluído</span>
              </div>
            </div>
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/20">
              <GraduationCap className="h-7 w-7" />
            </div>
          </div>
          
          <div className="h-2.5 overflow-hidden rounded-full bg-slate-200/50 p-[2px]">
            <div 
              className="h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 shadow-[0_0_12px_rgba(37,99,235,0.4)] transition-all duration-1000 ease-out" 
              style={{ width: `${backlogProgress.progress}%` }} 
            />
          </div>
          
          <button
            type="button"
            onClick={() => setActiveTab("backlog")}
            className="mt-6 inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-slate-950 px-6 py-3 text-[11px] font-black uppercase tracking-widest text-white transition-all hover:bg-slate-800 hover:scale-[1.02] active:scale-95 shadow-xl shadow-black/10"
          >
            Explorar Backlog <ClipboardCheck className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {cards.map((card) => (
          <button
            key={card.id}
            onClick={card.onClick}
            className="group relative flex flex-col text-left p-8 h-72 rounded-[2.5rem] border border-white/40 bg-white/70 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] transition-all hover:shadow-[0_20px_48px_0_rgba(31,38,135,0.12)] hover:-translate-y-3 overflow-hidden"
          >
            {/* Glossy Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
            
            {/* Background Accent Glow */}
            <div className={cn(
              "absolute -right-8 -top-8 h-48 w-48 rounded-full blur-[64px] opacity-0 transition-all duration-500 group-hover:opacity-20",
              card.accent
            )} />

            <div className={cn(
              "mb-8 flex h-16 w-16 items-center justify-center rounded-[1.25rem] text-white shadow-lg transition-all duration-500 group-hover:scale-110 group-hover:rotate-3",
              card.accent
            )}>
              <card.icon className="h-8 w-8" />
            </div>

            <div className="flex-1">
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-2">{card.subLabel}</p>
              <h3 className="text-2xl font-black text-slate-900 leading-tight">{card.label}</h3>
              <p className="mt-4 text-[13px] font-medium leading-relaxed text-slate-500/90 line-clamp-3">
                {card.description}
              </p>
            </div>

            <div className="mt-6 flex items-center gap-3 text-[11px] font-black uppercase tracking-widest text-slate-950 group-hover:translate-x-1 transition-transform">
              <span className="relative">
                Acessar Módulo
                <div className="absolute -bottom-1 left-0 h-[2px] w-0 bg-slate-950 transition-all duration-300 group-hover:w-full" />
              </span>
              <ArrowRight className="h-4 w-4" />
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
