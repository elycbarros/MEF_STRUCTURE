"use client";

import React from "react";
import { CheckCircle2, StretchHorizontal, Zap } from "lucide-react";
import { formatNumberBR } from "@/lib/utils";
import { SupportLocationSection } from "./SupportLocationSection";
import { HoleEditor } from "./HoleEditor";

interface GuidedGeometryViewProps {
  mode: "academic" | "professional" | null;
  systemType: "laje" | "radier";
  setSystemType: (v: "laje" | "radier") => void;
  ignorePillars: boolean;
  setIgnorePillars: React.Dispatch<React.SetStateAction<boolean>>;
  pillars: any[];
  addPillar: () => void;
  removePillar: (index: number) => void;
  updatePillar: (index: number, key: string, value: any) => void;
  restoreSamplePillars: () => void;
  lineSupports: any[];
  addLineSupport: () => void;
  removeLineSupport: (index: number) => void;
  updateLineSupport: (index: number, key: string, value: any) => void;
  holes: any[];
  setHoles: React.Dispatch<React.SetStateAction<any[]>>;
  applyGuidedPreset: () => void;
  analysisMode: "guided" | "manual";
  kvConfidence: number;
  setKvConfidence: (v: number) => void;
  kvSource: string;
  updateKvSource: (v: any) => void;
  params: any;
  updateParam: (k: any, v: number) => void;
  numPavimentos: number;
  setNumPavimentos: (v: number) => void;
  estimateLoads: () => void;
  KV_SOURCE_OPTIONS: any[];
  runAnalysis: () => void;
  loading: boolean;
}

export function GuidedGeometryView({
  mode,
  systemType,
  setSystemType,
  ignorePillars,
  setIgnorePillars,
  pillars,
  addPillar,
  removePillar,
  updatePillar,
  restoreSamplePillars,
  lineSupports,
  addLineSupport,
  removeLineSupport,
  updateLineSupport,
  holes,
  setHoles,
  applyGuidedPreset,
  analysisMode,
  kvConfidence,
  setKvConfidence,
  kvSource,
  updateKvSource,
  params,
  updateParam,
  numPavimentos,
  setNumPavimentos,
  estimateLoads,
  KV_SOURCE_OPTIONS,
  runAnalysis,
  loading
}: GuidedGeometryViewProps) {
  
  const parseLocaleNumberInput = (val: string): number | null => {
    const clean = val.replace(",", ".");
    const n = parseFloat(clean);
    return isFinite(n) ? n : null;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => setSystemType("laje")}
          className={`flex items-center gap-3 p-4 rounded-2xl border transition ${
            systemType === "laje" ? "border-black bg-black text-white" : "bg-white text-gray-600 hover:bg-gray-50"
          }`}
        >
          <StretchHorizontal className="h-5 w-5" />
          <div className="text-left">
            <p className="font-black text-sm">Laje Isolada</p>
            <p className={`text-xs ${systemType === "laje" ? "text-gray-300" : "text-gray-400"}`}>Apoios discretos e elásticos</p>
          </div>
        </button>
        <button
          onClick={() => setSystemType("radier")}
          className={`flex items-center gap-3 p-4 rounded-2xl border transition ${
            systemType === "radier" ? "border-black bg-black text-white" : "bg-white text-gray-600 hover:bg-gray-50"
          }`}
        >
          <CheckCircle2 className="h-5 w-5" />
          <div className="text-left">
            <p className="font-black text-sm">Radier Isolado</p>
            <p className={`text-xs ${systemType === "radier" ? "text-gray-300" : "text-gray-400"}`}>Fundação direta sobre solo</p>
          </div>
        </button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-black">Geometria e Solo</h2>
      </div>

      {/* Toggle Ignorar Pilares — inline no Modo Guiado */}
      <div className={`flex flex-wrap items-center justify-between gap-4 rounded-2xl border p-4 transition ${
        ignorePillars
          ? "border-[#e5e7eb] bg-[#f9fafb]"
          : "border-[#d1fae5] bg-[#f0fdf4]"
      }`}>
        <div className="flex items-center gap-3">
          <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${
            ignorePillars ? "bg-[#e5e7eb]" : "bg-[#dcfce7]"
          }`}>
            <StretchHorizontal className={`h-4 w-4 ${ignorePillars ? "text-[#9ca3af]" : "text-[#166534]"}`} />
          </div>
          <div>
            <p className="text-sm font-black text-[#1f2937]">
              {ignorePillars ? "Pilares ignorados no cálculo" : "Pilares incluídos no cálculo"}
            </p>
            <p className="mt-0.5 text-xs font-semibold text-[#667085]">
              {ignorePillars
                ? "Somente carga distribuída. Ative para incluir os pilares cadastrados."
                : `${pillars.length} pilar${pillars.length !== 1 ? "es" : ""} cadastrado${pillars.length !== 1 ? "s" : ""} — cargas concentradas ativas.`}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setIgnorePillars((v) => !v)}
          className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors focus:outline-none ${
            ignorePillars ? "bg-[#d1d5db]" : "bg-[#111827]"
          }`}
          aria-label={ignorePillars ? "Ativar pilares" : "Ignorar pilares"}
        >
          <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
            ignorePillars ? "translate-x-1" : "translate-x-6"
          }`} />
        </button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#dfe5ef] bg-[#f8fafc] p-4">
        <div>
          <p className="text-sm font-black text-[#1f2937]">Parâmetros editáveis</p>
          <p className="mt-1 text-xs font-semibold text-[#667085]">O modo guiado preenche, mas você pode ajustar tudo antes do cálculo.</p>
        </div>
        <button
          type="button"
          onClick={applyGuidedPreset}
          disabled={analysisMode === "manual"}
          className="inline-flex items-center gap-2 rounded-xl bg-[#0f766e] px-4 py-2 text-sm font-black text-white hover:bg-[#0d5f59] disabled:cursor-not-allowed disabled:bg-[#94a3b8]"
        >
          <CheckCircle2 className="h-4 w-4" />
          Aplicar preset
        </button>
      </div>

      {mode === "academic" && (
        <section className="rounded-2xl border-2 border-black/5 bg-white p-6 shadow-sm mb-6">
          <h3 className="text-[10px] font-black uppercase tracking-widest text-[#4d5360] mb-4">Escolha o Elemento Isolado</h3>
          <div className="flex gap-4">
            {[
              { id: "laje", label: "Laje Isolada", description: "Cálculo de laje sobre apoios discretos (pilares)." },
              { id: "radier", label: "Radier Isolado", description: "Cálculo de placa sobre base elástica (Winkler)." }
            ].map((type) => (
              <button
                key={type.id}
                type="button"
                onClick={() => setSystemType(type.id as any)}
                className={`flex-1 p-4 rounded-2xl border-2 text-left transition-all ${
                  systemType === type.id 
                  ? "border-black bg-black text-white shadow-lg scale-[1.02]" 
                  : "border-[#dfe5ef] bg-[#fafbfd] text-[#111827] hover:border-black/20"
                }`}
              >
                <p className="font-black text-sm">{type.label}</p>
                <p className={`text-[10px] mt-1 font-bold ${systemType === type.id ? "text-white/70" : "text-[#667085]"}`}>
                  {type.description}
                </p>
              </button>
            ))}
          </div>
        </section>
      )}

      {!(mode === "academic" && systemType === "laje") && (
        <section className="rounded-2xl border border-[#dfe5ef] bg-white p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Origem do kv</h3>
              <p className="mt-1 text-xs font-semibold text-[#667085]">A confiabilidade do coeficiente de reação vertical entra no diagnóstico de viabilidade.</p>
            </div>
            <span className={`rounded-full px-3 py-1 text-xs font-black uppercase ${kvConfidence >= 0.7 ? "bg-[#dcfce7] text-[#166534]" : kvConfidence >= 0.45 ? "bg-[#fef3c7] text-[#92400e]" : "bg-[#fee2e2] text-[#991b1b]"}`}>
              confiança {formatNumberBR(kvConfidence * 100, 0)}%
            </span>
          </div>
          <div className="mt-4 grid gap-3 lg:grid-cols-5">
            {KV_SOURCE_OPTIONS.map((option) => {
              const active = kvSource === option.id;
              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => updateKvSource(option.id)}
                  className={`rounded-2xl border p-3 text-left transition ${
                    active ? "border-[#0f766e] bg-[#ecfdf5]" : "border-[#dfe5ef] bg-[#fafbfd] hover:border-[#9aa7ba]"
                  }`}
                >
                  <p className="text-sm font-black text-[#111827]">{option.label}</p>
                  <p className="mt-1 text-xs font-semibold text-[#667085]">{option.description}</p>
                </button>
              );
            })}
          </div>
          <label className="mt-4 block text-xs font-bold uppercase tracking-wider text-[#6a7080]">Ajuste fino da confiança</label>
          <input
            type="range"
            min={0.2}
            max={1}
            step={0.05}
            value={kvConfidence}
            onChange={(e) => setKvConfidence(Number(e.target.value))}
            className="mt-2 w-full accent-[#0f766e]"
          />
        </section>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {[
          { key: "Lx", label: "Comprimento Lx (m)", min: 10, max: 100, step: 0.1 },
          { key: "Ly", label: "Largura Ly (m)", min: 10, max: 100, step: 0.1 },
          { key: "h", label: "Espessura h (m)", min: 0.3, max: 2.5, step: 0.05 },
          { key: "kv", label: "Módulo kv (kN/m³)", min: 5000, max: 250000, step: 100 },
          { key: "sigma_adm_kPa", label: "Tensão admissível σadm (kPa)", min: 25, max: 800, step: 5 },
          { key: "q", label: "Carga distribuída q (kN/m²)", min: 1, max: 500, step: 1 },
          { key: "fck", label: "fck (MPa)", min: 20, max: 80, step: 1 },
        ].map((item) => {
          const key = item.key as any;
          return (
            <div key={item.key} className="rounded-2xl border border-[#eceef3] bg-white p-4">
              <label className="block text-xs font-bold uppercase tracking-wider text-[#6a7080]">{item.label}</label>
              <input
                type="range"
                min={item.min}
                max={item.max}
                step={item.step}
                value={params[key]}
                onChange={(e) => updateParam(key, Number(e.target.value))}
                className={`mt-3 w-full accent-[#0071e3] ${mode === "academic" && key === "kv" && systemType === "laje" ? "opacity-20 pointer-events-none" : ""}`}
              />
              <input
                type="text"
                inputMode="decimal"
                value={params[key]}
                step={item.step}
                onChange={(e) => {
                  const parsed = parseLocaleNumberInput(e.target.value);
                  if (parsed !== null) updateParam(key, parsed);
                }}
                className="mt-3 w-full rounded-xl border border-[#d9dfe9] px-3 py-2 text-sm font-semibold"
              />
              {key === "q" && (
                <div className="mt-3 rounded-lg bg-[#f8fafc] p-3 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-[#6a7080]">Pavimentos:</span>
                    <input 
                      type="number" 
                      min={1} 
                      max={20} 
                      value={numPavimentos} 
                      onChange={(e) => setNumPavimentos(Number(e.target.value))} 
                      className="w-16 rounded border px-2 py-1 text-xs" 
                    />
                  </div>
                  <button
                    type="button"
                    onClick={estimateLoads}
                    className="w-full rounded bg-[#e2e8f0] py-1.5 text-xs font-bold text-[#334155] hover:bg-[#cbd5e1] transition"
                  >
                    Estimar Carga (NBR 6120)
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <SupportLocationSection
        pillars={pillars}
        addPillar={addPillar}
        removePillar={removePillar}
        updatePillar={updatePillar}
        restoreSamplePillars={restoreSamplePillars}
        lineSupports={lineSupports}
        addLineSupport={addLineSupport}
        removeLineSupport={removeLineSupport}
        updateLineSupport={updateLineSupport}
        systemType={systemType}
        params={params}
      />

      <div className="mt-10 border-t pt-10">
        <HoleEditor holes={holes} setHoles={setHoles} />
      </div>

      {mode === "academic" && (
        <div className="mt-12 flex justify-center pb-8">
          <button
            type="button"
            onClick={runAnalysis}
            disabled={loading}
            className="group relative flex items-center gap-3 rounded-2xl bg-[#0071e3] px-10 py-5 text-lg font-black text-white shadow-[0_20px_40px_rgba(0,113,227,0.3)] transition-all hover:bg-[#0062c7] hover:scale-105 active:scale-95 disabled:opacity-60 disabled:hover:scale-100"
          >
            <div className={`flex h-8 w-8 items-center justify-center rounded-full bg-white/20 ${loading ? "animate-pulse" : "group-hover:rotate-12 transition-transform"}`}>
              <Zap className="h-5 w-5" />
            </div>
            <span>{loading ? "Processando Análise..." : "Calcular Projeto"}</span>
          </button>
        </div>
      )}
    </div>
  );
}
