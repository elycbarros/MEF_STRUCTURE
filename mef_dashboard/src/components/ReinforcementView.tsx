"use client";

import React from "react";
import { CheckCircle2, Cpu } from "lucide-react";
import { formatNumberBR, cn } from "@/lib/utils";
import { formatBoolean, formatMaybeNumber } from "@/lib/formatters";

interface RebarCardProps {
  title: string;
  required: number | null;
  adopted: number | null;
  suggestion?: string;
  detail?: string;
}

function RebarCard({ title, required, adopted, suggestion, detail }: RebarCardProps) {
  const note = suggestion ?? detail;
  const ratio = required && adopted ? adopted / required : null;
  const ok = ratio !== null ? ratio >= 1.0 : null;
  return (
    <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-xl relative overflow-hidden group hover:border-blue-500/30 transition-all duration-300">
      <div className={`absolute top-0 right-0 w-24 h-24 blur-3xl -z-10 transition-colors ${ok ? 'bg-emerald-500/5' : 'bg-rose-500/5'}`} />
      <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 group-hover:text-blue-600 transition-colors">{title}</p>
      <div className="mt-4 flex items-baseline gap-2">
         <p className="text-3xl font-black text-slate-900 font-mono">{adopted !== null ? formatNumberBR(adopted) : "--"}</p>
         <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">cm²/m</span>
      </div>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mt-1">Requisito: {required !== null ? formatNumberBR(required) : "--"} cm²/m</p>
      {ratio !== null && (
        <div className={`mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${ok ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          η = {ratio.toFixed(2)} — {ok ? "Atende" : "Revisar"}
        </div>
      )}
      {note && <p className="text-[10px] text-slate-500 mt-4 italic font-mono uppercase tracking-tighter leading-tight border-t border-slate-100 pt-4">{note}</p>}
    </div>
  );
}

function numberOr(v: unknown, fallback: number): number | null {
  const n = Number(v);
  return isFinite(n) ? n : (isFinite(fallback) ? fallback : null);
}

interface ReinforcementViewProps {
  flexure: any;
  punching: any;
  service: any;
  guidance: any;
  notes: string[];
  criticalZones: any[];
  serviceChecks: any;
}

export function ReinforcementView({
  flexure,
  punching,
  service,
  guidance,
  notes,
  criticalZones,
  serviceChecks
}: ReinforcementViewProps) {
  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tighter">Módulo de Armadura do Radier</h2>
          <p className="mt-2 text-xs font-black uppercase tracking-[0.2em] text-slate-400">
            Resumo de flexão, mínimos, sugestões comerciais, punção e fissuração.
          </p>
        </div>
        <div className="flex items-center gap-3 px-4 py-2 bg-slate-900 rounded-2xl border border-slate-800 shadow-xl">
           <Cpu className="w-4 h-4 text-blue-400" />
           <span className="text-[10px] font-black uppercase tracking-widest text-white">REBAR ENGINE ACTIVE</span>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <RebarCard
          title="X inferior"
          required={numberOr(flexure.Asx_bottom_req_max_cm2_m, NaN)}
          adopted={numberOr(flexure.Asx_bottom_adot_max_cm2_m, NaN)}
          detail={String(flexure.sugestao_x_inf ?? "--")}
        />
        <RebarCard
          title="X superior"
          required={numberOr(flexure.Asx_top_req_max_cm2_m, NaN)}
          adopted={numberOr(flexure.Asx_top_adot_max_cm2_m, NaN)}
          detail={String(flexure.sugestao_x_sup ?? "--")}
        />
        <RebarCard
          title="Y inferior"
          required={numberOr(flexure.Asy_bottom_req_max_cm2_m, NaN)}
          adopted={numberOr(flexure.Asy_bottom_adot_max_cm2_m, NaN)}
          detail={String(flexure.sugestao_y_inf ?? "--")}
        />
        <RebarCard
          title="Y superior"
          required={numberOr(flexure.Asy_top_req_max_cm2_m, NaN)}
          adopted={numberOr(flexure.Asy_top_adot_max_cm2_m, NaN)}
          detail={String(flexure.sugestao_y_sup ?? "--")}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-[2rem] border border-slate-200 bg-white/80 p-6 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">Armadura mínima</h3>
          <p className="mt-4 text-3xl font-black text-slate-900 font-mono">
            {formatMaybeNumber(flexure.As_min_face_cm2_m)}
            <span className="ml-2 text-[10px] font-black uppercase tracking-widest text-slate-900/20">cm²/m / face</span>
          </p>
          <p className="mt-2 text-[10px] font-black uppercase tracking-widest text-slate-900/20">
            Total mínimo: {formatMaybeNumber(flexure.As_min_total_cm2_m)} cm²/m
          </p>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white/80 p-6 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">Punção</h3>
          <p className="mt-4 text-3xl font-black text-slate-900 font-mono">
            η = {formatMaybeNumber(punching.ratio_max)}
          </p>
          <p className="mt-2 text-[10px] font-black uppercase tracking-widest text-slate-900/20">
            Local crítico: <span className="text-slate-700">{String(punching.critical_local ?? "--")}</span> | Status: <span className={punching.atende ? "text-emerald-400" : "text-rose-400"}>{formatBoolean(punching.atende)}</span>
          </p>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white/80 p-6 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">Fissuração</h3>
          <div className="mt-4 space-y-1">
            <p className="text-sm font-black text-slate-900 font-mono">
              <span className="text-slate-900/20 mr-2">X:</span> {formatMaybeNumber(service.wk_x_max_mm ?? serviceChecks.wk_x_max_mm)} <span className="text-[10px]">mm</span>
            </p>
            <p className="text-sm font-black text-slate-900 font-mono">
              <span className="text-slate-900/20 mr-2">Y:</span> {formatMaybeNumber(service.wk_y_max_mm ?? serviceChecks.wk_y_max_mm)} <span className="text-[10px]">mm</span>
            </p>
          </div>
          <p className="mt-2 text-[10px] font-black uppercase tracking-widest text-slate-900/20">
            Limite Normativo: {formatMaybeNumber(service.wk_limit_mm ?? serviceChecks.wk_limit_mm)} mm
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[2rem] border border-slate-200 bg-white/80 p-8 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 mb-4">Diretrizes de detalhamento</h3>
          <ul className="space-y-3">
            {[
              { label: "Inferior", text: String(guidance.armadura_inferior ?? "distribuir nas duas direções conforme momentos positivos") },
              { label: "Superior", text: String(guidance.armadura_superior ?? "reforçar sobre pilares, bordas e momentos negativos") },
              { label: "Locais", text: String(guidance.reforcos_locais ?? "avaliar punção, bordas e aberturas") },
            ].map((item) => (
              <li key={item.label} className="flex gap-4">
                <span className="text-[10px] font-black uppercase tracking-widest text-blue-400 w-20 shrink-0">{item.label}</span>
                <span className="text-sm font-black text-slate-700 leading-relaxed uppercase tracking-widest text-[10px]">{item.text}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-[2rem] border border-blue-500/20 bg-blue-500/5 p-8 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400 mb-4">Observações do módulo</h3>
          <ul className="space-y-3">
            {(notes.length ? notes : [
              "Definir faixas, ancoragens, emendas e reforços no detalhamento executivo.",
              "Sugestões comerciais são preliminares e devem ser revisadas pelo responsável técnico.",
            ]).map((note) => (
              <li key={note} className="flex gap-3">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                <span className="text-[10px] font-black text-slate-500 leading-relaxed uppercase tracking-widest">{note}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {criticalZones.length > 0 && (
        <div className="rounded-[2rem] border border-slate-200 bg-white/80 p-8 backdrop-blur-xl shadow-2xl">
          <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 mb-6">Faixas críticas para detalhamento</h3>
          <div className="grid gap-4 lg:grid-cols-3">
            {criticalZones.map((zone, idx) => (
              <div key={`critical-zone-${idx}`} className="rounded-2xl border border-slate-200 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-4 mb-2">
                  <p className="text-[10px] font-black text-slate-900 uppercase tracking-widest">{String(zone.zone ?? "Região")}</p>
                  <span className={`rounded-full px-2 py-0.5 text-[9px] font-black uppercase tracking-widest ${String(zone.priority) === "alta" ? "bg-rose-500/20 text-rose-400" : "bg-amber-500/20 text-amber-400"}`}>
                    {String(zone.priority ?? "média")}
                  </span>
                </div>
                <p className="text-[10px] font-black text-slate-400 leading-relaxed uppercase tracking-widest">{String(zone.guidance ?? "")}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
