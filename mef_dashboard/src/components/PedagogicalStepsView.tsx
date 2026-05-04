"use client";

import React, { useMemo, useState } from "react";
import { AlertTriangle, BookOpen, CheckCircle2, ChevronDown, Info } from "lucide-react";
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
  OK: "border-emerald-200 bg-emerald-50 text-emerald-700",
  ALERTA: "border-red-700 bg-red-600 text-white shadow-md shadow-red-500/30",
  INFO: "border-sky-200 bg-sky-50 text-sky-700",
};

const statusIcons = {
  OK: CheckCircle2,
  ALERTA: AlertTriangle,
  INFO: Info,
};

function MathBlock({ math }: { math?: string }) {
  if (!math) return null;

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white px-3 py-2">
      <BlockMath
        math={math}
        renderError={() => (
          <code className="block whitespace-pre-wrap text-xs font-bold text-rose-700">{math}</code>
        )}
      />
    </div>
  );
}

function StepCard({ step, index }: { step: PedagogicalStep; index: number }) {
  const [open, setOpen] = useState(true);
  const status = step.status ?? "INFO";
  const StatusIcon = statusIcons[status];

  return (
    <article className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left"
      >
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-xs font-black text-white">
            {index + 1}
          </div>
          <div className="min-w-0">
            <h4 className="truncate text-sm font-black text-slate-950">{step.title}</h4>
            {step.norm_ref && <p className="mt-0.5 truncate text-[11px] font-semibold text-slate-500">{step.norm_ref}</p>}
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {status === "ALERTA" && step.norm_ref && (
            <span className="hidden sm:inline-block text-[10px] font-semibold text-slate-500 mr-1">
              Ref: {step.norm_ref.split('-')[0].trim()}
            </span>
          )}
          <span className={cn(
            "inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[10px] font-black uppercase tracking-wider", 
            statusStyles[status],
            status === "ALERTA" && "animate-pulse"
          )}>
            <StatusIcon className={cn("h-3 w-3", status === "ALERTA" ? "text-white" : "text-rose-600")} />
            {status}
          </span>
          <ChevronDown className={cn("h-4 w-4 text-slate-400 transition-transform", open && "rotate-180")} />
        </div>
      </button>

      {open ? (
        <div className="space-y-3 border-t border-slate-100 px-4 py-4">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wider text-slate-400">Formula geral</p>
            <MathBlock math={step.formula_latex} />
          </div>
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wider text-slate-400">Substituicao numerica</p>
            <MathBlock math={step.substitution_latex} />
          </div>
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wider text-slate-400">Resultado</p>
            <MathBlock math={step.result_latex} />
          </div>
          {step.opinion ? (
            <div className={cn(
              "rounded-2xl border p-4 shadow-sm",
              status === "ALERTA" 
                ? "border-rose-200 bg-rose-50 text-rose-900 ring-1 ring-rose-500/10" 
                : "border-emerald-200 bg-emerald-50 text-emerald-900"
            )}>
              <p className="mb-1 text-[10px] font-black uppercase tracking-wider">Parecer sobre o resultado final</p>
              <p className="text-sm font-bold leading-relaxed whitespace-pre-line">{step.opinion}</p>
            </div>
          ) : null}
          {step.explanation ? <p className="text-xs font-semibold leading-relaxed text-slate-600 whitespace-pre-line">{step.explanation}</p> : null}
        </div>
      ) : null}
    </article>
  );
}

export function PedagogicalStepsView({ blackboard }: PedagogicalStepsViewProps) {
  const steps = useMemo(() => blackboard?.steps ?? [], [blackboard]);

  if (steps.length === 0) return null;

  return (
    <section className="space-y-4 rounded-3xl border border-amber-200 bg-amber-50/50 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-amber-200 bg-white px-3 py-1 text-[10px] font-black uppercase tracking-widest text-amber-700">
            <BookOpen className="h-3.5 w-3.5" />
            Engine MESTRE
          </div>
          <h3 className="text-lg font-black text-slate-950">{blackboard?.title ?? "Roteiro didatico passo a passo"}</h3>
          <p className="mt-1 text-xs font-semibold text-slate-600">
            Cada etapa mostra formula, substituicao e resultado para uso em aula.
          </p>
        </div>
        <span className="rounded-full bg-slate-950 px-3 py-1 text-[10px] font-black uppercase tracking-wider text-white">
          {steps.length} passos
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
