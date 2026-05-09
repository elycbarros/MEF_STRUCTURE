"use client";

import React, { useMemo } from "react";
import { AlertTriangle, BookOpen, CheckCircle2, Info, ChevronRight } from "lucide-react";
import { BlockMath } from "react-katex";
import { cn } from "@/lib/utils";

export type PedagogicalStepStatus = "OK" | "ALERTA" | "INFO";

export interface PedagogicalStep {
  id: string;
  title: string;
  formula_latex?: string;
  substitution_latex?: string;
  result_latex?: string;
  norm_ref?: string;
  explanation?: string;
  opinion?: string;
  status?: PedagogicalStepStatus;
}

export interface PedagogicalBlackboard {
  mode?: string;
  element?: string;
  title?: string;
  summary?: Record<string, unknown>;
  steps?: PedagogicalStep[];
}

interface PedagogicalStepsViewProps {
  blackboard?: PedagogicalBlackboard | null;
}

const statusStyles: Record<PedagogicalStepStatus, string> = {
  OK: "border-emerald-500/20 bg-emerald-500/10 text-emerald-600",
  ALERTA: "border-red-500/30 bg-red-600 text-white shadow-[0_0_20px_rgba(239,68,68,0.2)]",
  INFO: "border-blue-500/20 bg-blue-500/10 text-blue-600",
};

const statusIcons = {
  OK: CheckCircle2,
  ALERTA: AlertTriangle,
  INFO: Info,
};

function MathBlock({ math }: { math?: string }) {
  if (!math) return null;

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white/80 px-6 py-6 group-hover:border-blue-500/30 transition-all shadow-inner">
      <div className="text-slate-900 [&_.katex]:text-slate-900">
        <BlockMath
          math={math}
          renderError={() => (
            <code className="block whitespace-pre-wrap text-xs font-bold text-rose-400">{math}</code>
          )}
        />
      </div>
    </div>
  );
}

function StepCard({ step, index }: { step: PedagogicalStep; index: number }) {
  const status = step.status ?? "INFO";
  const StatusIcon = statusIcons[status];

  return (
    <article className="rounded-[2rem] border border-slate-200 bg-white shadow-xl overflow-hidden group hover:border-blue-500/30 transition-all">
      <div className="flex w-full items-center justify-between gap-4 px-6 py-5 bg-slate-50 border-b border-slate-200">
        <div className="flex min-w-0 items-center gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-blue-600 border border-blue-500 text-sm font-black text-white shadow-lg shadow-blue-600/20">
            {index + 1}
          </div>
          <div className="min-w-0">
            <h4 className="truncate text-base font-black text-slate-900 tracking-tight">{step.title}</h4>
            {step.norm_ref && <p className="mt-1 truncate text-[10px] font-black uppercase tracking-widest text-slate-500">{step.norm_ref}</p>}
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <span className={cn(
            "inline-flex items-center gap-1.5 rounded-full border px-4 py-1.5 text-[10px] font-black uppercase tracking-wider transition-all", 
            statusStyles[status],
            status === "ALERTA" && "animate-pulse"
          )}>
            <StatusIcon className={cn("h-4 w-4", status === "ALERTA" ? "text-white" : status === "OK" ? "text-emerald-600" : "text-blue-600")} />
            {status}
          </span>
        </div>
      </div>

      <div className="p-8 space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-4">
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">01. Formulação Geral</p>
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 shadow-inner group-hover:border-blue-500/20 transition-colors">
              <MathBlock math={step.formula_latex} />
            </div>
          </div>
          <div className="space-y-4">
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">02. Desenvolvimento Numérico</p>
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 shadow-inner group-hover:border-blue-500/20 transition-colors">
              <MathBlock math={step.substitution_latex} />
            </div>
          </div>
          <div className="space-y-4">
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-600">03. Verificação de Estado</p>
            <div className="bg-blue-600/5 p-6 rounded-2xl border border-blue-500/20 shadow-inner group-hover:bg-blue-600/10 transition-all">
              <MathBlock math={step.result_latex} />
            </div>
          </div>
        </div>

        <div className={cn(
          "rounded-3xl border p-8 shadow-2xl backdrop-blur-md relative overflow-hidden",
          status === "ALERTA" 
            ? "border-red-500/30 bg-red-600 text-white" 
            : "border-emerald-500/30 bg-emerald-500/5 text-slate-900"
        )}>
          {status === "ALERTA" && <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-red-700 -z-10" />}
          <div className="flex items-center gap-3 mb-4">
            <Info className={cn("h-5 w-5", status === "ALERTA" ? "text-white" : status === "OK" ? "text-emerald-600" : "text-blue-600")} />
            <p className={cn("text-[10px] font-black uppercase tracking-[0.3em]", status === "ALERTA" ? "text-white/70" : "text-slate-500")}>Parecer Técnico de Auditoria</p>
          </div>
          <p className="text-sm font-black leading-relaxed whitespace-pre-line tracking-tight">{step.opinion || step.explanation}</p>
        </div>

        {step.explanation && step.opinion && (
          <div className="pt-6 border-t border-slate-100">
            <p className="text-xs font-medium leading-relaxed text-slate-500 whitespace-pre-line italic">
              Nota explicativa: {step.explanation}
            </p>
          </div>
        )}
      </div>
    </article>
  );
}

export function PedagogicalStepsView({ blackboard }: PedagogicalStepsViewProps) {
  const steps = useMemo(() => blackboard?.steps ?? [], [blackboard]);

  if (steps.length === 0) return null;

  return (
    <section className="space-y-6 rounded-[2.5rem] border border-slate-200 bg-slate-100/40 backdrop-blur-xl p-8 shadow-2xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-600/20 rounded-2xl flex items-center justify-center border border-blue-500/30">
            <BookOpen className="text-blue-600 h-6 w-6" />
          </div>
          <div>
            <div className="inline-flex items-center gap-2 rounded-lg bg-blue-600 text-white px-2.5 py-0.5 text-[9px] font-black uppercase tracking-[0.2em] mb-1.5">
              ENGINE MESTRE
            </div>
            <h3 className="text-2xl font-black text-slate-900 tracking-tight">{blackboard?.title ?? "Roteiro didático passo a passo"}</h3>
            <p className="mt-1 text-xs font-black text-slate-600 uppercase tracking-widest">
              Cada etapa mostra formula, substituicao e resultado para uso em aula.
            </p>
          </div>
        </div>
        <span className="rounded-2xl bg-white/5 border border-slate-200 px-5 py-2.5 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
          {steps.length} PASSOS DISPONÍVEIS
        </span>
      </div>

      <div className="space-y-3">
        {steps.map((step, index) => (
          <StepCard key={step.id} step={step} index={index} />
        ))}
      </div>
    </section>
  );
}

export default PedagogicalStepsView;
