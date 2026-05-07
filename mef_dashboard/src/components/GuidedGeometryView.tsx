"use client";

import React from "react";
import { CheckCircle2, StretchHorizontal, Zap, Box, Activity } from "lucide-react";
import { formatNumberBR, cn } from "@/lib/utils";
import { SupportLocationSection } from "./SupportLocationSection";
import { HoleEditor } from "./HoleEditor";
import { AreaLoadEditor } from "./AreaLoadEditor";

interface GuidedGeometryViewProps {
  mode: "academic" | "professional" | null;
  systemType: "laje" | "radier";
  setSystemType: (v: "laje" | "radier") => void;
  slabType: "solid" | "ribbed" | "hollow_core" | "prestressed";
  setSlabType: (v: "solid" | "ribbed" | "hollow_core" | "prestressed") => void;
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
  setLineSupports?: React.Dispatch<React.SetStateAction<any[]>>;
  holes: any[];
  setHoles: React.Dispatch<React.SetStateAction<any[]>>;
  areaLoads: any[];
  setAreaLoads: React.Dispatch<React.SetStateAction<any[]>>;
  updateAreaLoad?: (index: number, key: string, value: any) => void;
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
  showLoadToast?: boolean;
  KV_SOURCE_OPTIONS: any[];
  runAnalysis: () => void;
  loading: boolean;
  b_nerv: number;
  setBNerv: (v: number) => void;
  dist_nerv: number;
  setDistNerv: (v: number) => void;
  h_mesa: number;
  setHMesa: (v: number) => void;
  area_voids: number;
  setAreaVoids: (v: number) => void;
  p_force: number;
  setPForce: (v: number) => void;
  ecc: number;
  setEcc: (v: number) => void;
  fillerType: "ceramic" | "eps";
  setFillerType: (v: "ceramic" | "eps") => void;
}

export function GuidedGeometryView({
  mode,
  systemType,
  setSystemType,
  slabType,
  setSlabType,
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
  setLineSupports,
  holes,
  setHoles,
  areaLoads,
  setAreaLoads,
  updateAreaLoad,
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
  showLoadToast,
  KV_SOURCE_OPTIONS,
  runAnalysis,
  loading,
  b_nerv,
  setBNerv,
  dist_nerv,
  setDistNerv,
  h_mesa,
  setHMesa,
  area_voids,
  setAreaVoids,
  p_force,
  setPForce,
  ecc,
  setEcc,
  fillerType,
  setFillerType
}: GuidedGeometryViewProps) {
  
  const parseLocaleNumberInput = (val: string): number | null => {
    const clean = val.replace(",", ".");
    const n = parseFloat(clean);
    return isFinite(n) ? n : null;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4">
        <div
          className={`flex items-center gap-3 p-4 rounded-2xl border ${
            systemType === "radier" ? "border-black bg-black text-white" : "border-blue-600 bg-blue-600 text-white"
          }`}
        >
          <CheckCircle2 className="h-5 w-5" />
          <div className="text-left">
            <p className="font-black text-sm">{systemType === "radier" ? "Radier Isolado" : "Laje Elevada"}</p>
            <p className="text-xs opacity-80">
              {systemType === "radier" ? "Fundação direta sobre solo" : "Placa sobre apoios discretos"}
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-black">{systemType === "radier" ? "Geometria e Solo" : "Geometria da Placa"}</h2>
        
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
          {[
            { id: 'house', label: 'Sobrado/Casa' },
            { id: 'shed', label: 'Galpão' },
            { id: 'building', label: 'Prédio Baixo' },
            { id: 'special', label: 'Especial' }
          ].map(type => (
            <button
              key={type.id}
              className={cn(
                "px-3 py-1.5 text-[10px] font-black uppercase tracking-wider rounded-lg transition-all",
                (params as any).building_type === type.id 
                  ? "bg-white text-blue-600 shadow-sm" 
                  : "text-slate-500 hover:text-slate-700"
              )}
              onClick={() => updateParam("building_type" as any, type.id as any)}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Seletor de Tipo de Laje (Apenas se systemType === "laje") */}
      {systemType === "laje" && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { id: "solid", label: "Maciça", desc: "Concreto Armado" },
            { id: "ribbed", label: "Nervurada", desc: "Com Cubetas" },
            { id: "hollow_core", label: "Alveolar", desc: "Protendida" },
            { id: "prestressed", label: "Protendida", desc: "Cordoalhas" },
            { id: "trussed", label: "Treliçada", desc: "Vigotas" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setSlabType(t.id as any)}
              className={cn(
                "p-4 rounded-2xl border-2 transition-all text-left",
                slabType === t.id 
                  ? "border-blue-600 bg-blue-50" 
                  : "border-slate-100 hover:border-slate-200 bg-white"
              )}
            >
              <p className={cn("text-xs font-black uppercase", slabType === t.id ? "text-blue-700" : "text-slate-500")}>{t.label}</p>
              <p className="text-[10px] text-slate-400 font-medium">{t.desc}</p>
            </button>
          ))}
        </div>
      )}

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


      {systemType === "radier" && (
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

      {systemType === "laje" && slabType !== "solid" && (
        <section className="rounded-2xl border-2 border-emerald-100 bg-emerald-50/20 p-5 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-emerald-600" />
              <h3 className="text-sm font-black uppercase tracking-wider text-emerald-800">
                Engenharia de Seção: {
                  slabType === "ribbed" ? "Nervurada" : 
                  slabType === "hollow_core" ? "Alveolar" : 
                  slabType === "trussed" ? "Treliçada" : "Protendida"
                }
              </h3>
            </div>
            <span className="text-[10px] font-black uppercase bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">NBR 6118 / 14859</span>
          </div>
          
          <div className="grid gap-5 md:grid-cols-3">
            {slabType === "ribbed" && (
              <>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500 flex items-center gap-1">
                    <Box className="h-3 w-3" /> Largura Nervura (m)
                  </label>
                  <input 
                    type="number" step="0.01" value={b_nerv} 
                    onChange={(e) => setBNerv(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                  <p className="text-[9px] text-slate-400 font-medium italic">Largura da base da nervura (bw)</p>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Dist. entre Eixos (m)</label>
                  <input 
                    type="number" step="0.05" value={dist_nerv} 
                    onChange={(e) => setDistNerv(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                  <p className="text-[9px] text-slate-400 font-medium italic">Espaçamento entre nervuras</p>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Espessura Mesa (m)</label>
                  <input 
                    type="number" step="0.01" value={h_mesa} 
                    onChange={(e) => setHMesa(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                  <p className="text-[9px] text-slate-400 font-medium italic">Capa superior de concreto (hf)</p>
                </div>
              </>
            )}
            
            {slabType === "hollow_core" && (
              <>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Área de Vazios (m²/m)</label>
                  <input 
                    type="number" step="0.005" value={area_voids} 
                    onChange={(e) => setAreaVoids(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Força Protensão (kN/m)</label>
                  <input 
                    type="number" step="10" value={p_force} 
                    onChange={(e) => setPForce(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                </div>
              </>
            )}

            {slabType === "prestressed" && (
              <>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500 flex items-center gap-1">
                    <Activity className="h-3 w-3" /> Força Protensão (kN/m)
                  </label>
                  <input 
                    type="number" step="10" value={p_force} 
                    onChange={(e) => setPForce(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                  <p className="text-[9px] text-slate-400 font-medium italic">Força de ancoragem efetiva</p>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Excentricidade (m)</label>
                  <input 
                    type="number" step="0.01" value={ecc} 
                    onChange={(e) => setEcc(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                  <p className="text-[9px] text-slate-400 font-medium italic">Distância do cabo ao CG</p>
                </div>
              </>
            )}

            {slabType === "trussed" && (
              <>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Tipo Enchimento</label>
                  <select 
                    value={fillerType} 
                    onChange={(e) => setFillerType(e.target.value as any)}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  >
                    <option value="ceramic">Cerâmica (Lajota)</option>
                    <option value="eps">EPS (Isopor)</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Dist. Vigotas (m)</label>
                  <input 
                    type="number" step="0.01" value={dist_nerv} 
                    onChange={(e) => setDistNerv(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-500">Largura Vigota (m)</label>
                  <input 
                    type="number" step="0.01" value={b_nerv} 
                    onChange={(e) => setBNerv(Number(e.target.value))}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-bold focus:border-emerald-500 outline-none shadow-sm transition-all focus:ring-2 focus:ring-emerald-100"
                  />
                </div>
              </>
            )}
          </div>
        </section>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        {[
          { key: "Lx", label: "Comprimento Lx (m)", min: 10, max: 100, step: 0.1 },
          { key: "Ly", label: "Largura Ly (m)", min: 10, max: 100, step: 0.1 },
          { key: "h", label: "Espessura h (m)", min: 0.1, max: 2.5, step: 0.05 },
          ...(systemType === "radier" ? [
            { key: "kv", label: "Módulo kv (kN/m³)", min: 5000, max: 250000, step: 100 },
            { key: "sigma_adm_kPa", label: "Tensão admissível σadm (kPa)", min: 25, max: 800, step: 5 },
          ] : []),
          { key: "q", label: systemType === "radier" ? "Carga distribuída q (kN/m²)" : "Sobrecarga distribuída q (kN/m²)", min: 1, max: 500, step: 1 },
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
                className="mt-3 w-full accent-[#0071e3]"
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
                  
                  {showLoadToast && (
                    <div className="mt-2 animate-in fade-in slide-in-from-top-1 duration-300">
                      <div className="flex items-center gap-2 rounded-lg bg-[#dcfce7] px-3 py-1.5 text-[10px] font-black text-[#166534] border border-[#bbf7d0]">
                        <CheckCircle2 className="h-3 w-3" />
                        CARGAS APLICADAS COM SUCESSO
                      </div>
                    </div>
                  )}
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
        setLineSupports={setLineSupports}
        systemType={systemType}
        params={params}
        holes={holes}
        areaLoads={areaLoads}
        updateAreaLoad={updateAreaLoad}
        slabType={slabType}
      />

      <div className="mt-10 border-t pt-10 space-y-10">
        <HoleEditor holes={holes} setHoles={setHoles} slabType={slabType} />
        <AreaLoadEditor areaLoads={areaLoads} setAreaLoads={setAreaLoads} />
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
