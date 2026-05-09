"use client";

import React from "react";
import { CheckCircle2, StretchHorizontal, Zap, Box, Activity, Layers, Binary, Shield, Settings2, Target, RotateCcw } from "lucide-react";
import { formatNumberBR, cn } from "@/lib/utils";
import { SupportLocationSection } from "./SupportLocationSection";
import { HoleEditor } from "./HoleEditor";
import { AreaLoadEditor } from "./AreaLoadEditor";

interface GuidedGeometryViewProps {
  mode: "academic" | "professional" | null;
  systemType: "laje" | "radier";
  setSystemType: (v: "laje" | "radier") => void;
  slabType: "solid" | "ribbed" | "hollow_core" | "prestressed" | "trussed";
  setSlabType: (v: "solid" | "ribbed" | "hollow_core" | "prestressed" | "trussed") => void;
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
    <div className="space-y-10">
      {/* System Selector Header */}
      <div className="flex flex-col md:flex-row items-stretch gap-6">
        <div
          className={cn(
             "flex-1 flex items-center gap-6 p-8 rounded-[2.5rem] border transition-all",
             systemType === "radier" 
               ? "bg-white/[0.03] border-slate-200" 
               : "bg-blue-600 border-blue-500 shadow-2xl shadow-blue-600/20"
          )}
        >
          <div className={cn("p-4 rounded-2xl", systemType === "laje" ? "bg-white/20 text-white" : "bg-blue-600/20 text-blue-600")}>
             <Layers className="h-6 w-6" />
          </div>
          <div className="text-left">
            <p className="font-black text-lg tracking-tight text-white">{systemType === "radier" ? "Radier Isolado" : "Laje Elevada"}</p>
            <p className={cn("text-[10px] font-black uppercase tracking-[0.2em] mt-1", systemType === "laje" ? "text-slate-700" : "text-blue-600/80")}>
              {systemType === "radier" ? "Fundação Direta MEF" : "Placa sobre Apoios Discretos"}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3 bg-white/[0.02] p-2 rounded-[2.5rem] border border-slate-200 backdrop-blur-xl">
          {[
            { id: 'house', label: 'Residencial' },
            { id: 'shed', label: 'Industrial' },
            { id: 'building', label: 'Multi-Pav' },
            { id: 'special', label: 'Especial' }
          ].map(type => (
            <button
              key={type.id}
              className={cn(
                "px-6 py-4 text-[10px] font-black uppercase tracking-widest rounded-2xl transition-all",
                (params as any).building_type === type.id 
                  ? "bg-white/10 text-slate-900 border border-slate-200 shadow-xl" 
                  : "text-slate-500 hover:text-slate-300"
              )}
              onClick={() => updateParam("building_type" as any, type.id as any)}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

      {/* Seletor de Tipo de Laje */}
      {systemType === "laje" && (
        <div className="space-y-6">
          <div className="flex items-center gap-4 px-2">
             <div className="w-1.5 h-6 bg-blue-500 rounded-full" />
             <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Tipologia da Seção Transversal</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { id: "solid", label: "Maciça", desc: "Monolítica" },
              { id: "ribbed", label: "Nervurada", desc: "Bidirecional" },
              { id: "hollow_core", label: "Alveolar", desc: "Pré-Moldada" },
              { id: "prestressed", label: "Protendida", desc: "Pós-Tração" },
              { id: "trussed", label: "Treliçada", desc: "Semi-Pronta" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setSlabType(t.id as any)}
                className={cn(
                  "p-6 rounded-[2rem] border transition-all text-left group",
                  slabType === t.id 
                    ? "border-blue-500 bg-blue-600/10 shadow-lg shadow-blue-600/5" 
                    : "border-slate-200 bg-white/[0.01] hover:bg-white/[0.03]"
                )}
              >
                <p className={cn("text-[10px] font-black uppercase tracking-widest mb-1", slabType === t.id ? "text-blue-600" : "text-slate-500 group-hover:text-slate-600")}>{t.label}</p>
                <p className="text-[10px] text-slate-600 font-bold tracking-tight">{t.desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Toggle Logic Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={cn(
           "flex items-center justify-between p-8 rounded-[2.5rem] border transition-all",
           ignorePillars ? "border-slate-200 bg-white/[0.01]" : "border-emerald-500/20 bg-emerald-500/5"
        )}>
          <div className="flex items-center gap-6">
            <div className={cn("p-4 rounded-2xl", ignorePillars ? "bg-white/5 text-slate-500" : "bg-emerald-500/10 text-emerald-600")}>
               <StretchHorizontal className="h-6 w-6" />
            </div>
            <div>
              <p className="font-black text-slate-900 tracking-tight">Status de Carregamento</p>
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-500 mt-1">
                 {ignorePillars ? "Apenas Carga Distribuída" : `${pillars.length} Ponto(s) de Concentração`}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setIgnorePillars((v) => !v)}
            className={cn(
               "relative inline-flex h-8 w-14 items-center rounded-full transition-all focus:outline-none",
               ignorePillars ? "bg-white/10" : "bg-emerald-600"
            )}
          >
            <span className={cn(
               "inline-block h-6 w-6 transform rounded-full bg-white shadow-xl transition-all",
               ignorePillars ? "translate-x-1" : "translate-x-7"
            )} />
          </button>
        </div>

        <div className="flex items-center justify-between p-8 rounded-[2.5rem] border border-slate-200 bg-white/[0.01]">
          <div className="flex items-center gap-6">
            <div className="p-4 rounded-2xl bg-teal-500/10 text-teal-400">
               <Settings2 className="h-6 w-6" />
            </div>
            <div>
              <p className="font-black text-slate-900 tracking-tight">Preset de Inteligência</p>
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-500 mt-1">Sincronização com NBR 6120</p>
            </div>
          </div>
          <button
            type="button"
            onClick={applyGuidedPreset}
            disabled={analysisMode === "manual"}
            className="p-4 rounded-2xl bg-teal-600 text-white hover:bg-teal-500 transition-all shadow-xl shadow-teal-600/20 disabled:opacity-20"
          >
            <RotateCcw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Geotechnical Intelligence (Radier only) */}
      {systemType === "radier" && (
        <section className="p-8 rounded-[2.5rem] border border-slate-200 bg-white/[0.01] space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                 <Shield className="h-5 w-5 text-emerald-600" />
                 <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Qualificação Geotécnica</h3>
              </div>
              <div className={cn(
                 "px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest border",
                 kvConfidence >= 0.7 ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/20" : "bg-amber-500/10 text-amber-600 border-amber-500/20"
              )}>
                 CONFIANÇA: {formatNumberBR(kvConfidence * 100, 0)}%
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-5">
              {KV_SOURCE_OPTIONS.map((option) => {
                const active = kvSource === option.id;
                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => updateKvSource(option.id)}
                    className={cn(
                       "p-5 rounded-[1.5rem] border transition-all text-left group",
                       active ? "bg-emerald-500/10 border-emerald-500/30 shadow-lg" : "bg-white/50 border-slate-200 hover:border-slate-200"
                    )}
                  >
                    <p className={cn("text-[10px] font-black uppercase tracking-widest mb-1", active ? "text-emerald-600" : "text-slate-500 group-hover:text-slate-600")}>{option.label}</p>
                    <p className="text-[10px] text-slate-600 font-bold leading-tight">{option.description}</p>
                  </button>
                );
              })}
            </div>

            <div className="space-y-4">
               <div className="flex justify-between items-center px-1">
                  <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Fine-Tuning de Confiabilidade</p>
                  <p className="text-[10px] font-mono text-emerald-600">{kvConfidence.toFixed(2)}</p>
               </div>
               <input
                 type="range"
                 min={0.2}
                 max={1}
                 step={0.05}
                 value={kvConfidence}
                 onChange={(e) => setKvConfidence(Number(e.target.value))}
                 className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-emerald-500"
               />
            </div>
          </section>
      )}

      {/* Engineering Inputs Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         {/* Dimensions & Main Params */}
         <div className="space-y-6">
            <div className="flex items-center gap-4 px-2 mb-6">
               <Target className="h-4 w-4 text-blue-600" />
               <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Geometria & Domínio</h3>
            </div>
            <div className="grid gap-6">
              {[
                { key: "Lx", label: "Comprimento Lx", unit: "m", min: 10, max: 100, step: 0.1 },
                { key: "Ly", label: "Largura Ly", unit: "m", min: 10, max: 100, step: 0.1 },
                { key: "h", label: "Espessura h", unit: "m", min: 0.1, max: 2.5, step: 0.05 },
                { key: "fck", label: "Resistência fck", unit: "MPa", min: 20, max: 80, step: 1 },
              ].map((item) => (
                <div key={item.key} className="p-6 rounded-[2rem] bg-white/[0.01] border border-slate-200 group hover:border-slate-200 transition-colors">
                  <div className="flex justify-between items-center mb-4">
                    <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 group-hover:text-slate-600 transition-colors">{item.label}</p>
                    <div className="flex items-center gap-2">
                       <input 
                         type="text"
                         value={params[item.key as any]}
                         onChange={(e) => {
                           const parsed = parseLocaleNumberInput(e.target.value);
                           if (parsed !== null) updateParam(item.key as any, parsed);
                         }}
                         className="w-16 bg-transparent text-right font-black text-slate-900 text-sm focus:outline-none"
                       />
                       <span className="text-[10px] font-black text-slate-700">{item.unit}</span>
                    </div>
                  </div>
                  <input
                    type="range"
                    min={item.min}
                    max={item.max}
                    step={item.step}
                    value={params[item.key as any]}
                    onChange={(e) => updateParam(item.key as any, Number(e.target.value))}
                    className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                </div>
              ))}
            </div>
         </div>

         {/* Loading & Specific Params */}
         <div className="space-y-6">
            <div className="flex items-center gap-4 px-2 mb-6">
               <Zap className="h-4 w-4 text-amber-600" />
               <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Carregamento & Solo</h3>
            </div>
            <div className="grid gap-6">
               {systemType === "radier" && (
                 <>
                   {[
                     { key: "kv", label: "Módulo kv", unit: "kN/m³", min: 5000, max: 250000, step: 100 },
                     { key: "sigma_adm_kPa", label: "Tensão Adm σadm", unit: "kPa", min: 25, max: 800, step: 5 },
                   ].map((item) => (
                    <div key={item.key} className="p-6 rounded-[2rem] bg-white/[0.01] border border-slate-200 group hover:border-slate-200 transition-colors">
                      <div className="flex justify-between items-center mb-4">
                        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 group-hover:text-slate-600 transition-colors">{item.label}</p>
                        <div className="flex items-center gap-2">
                          <input 
                            type="text"
                            value={params[item.key as any]}
                            onChange={(e) => {
                              const parsed = parseLocaleNumberInput(e.target.value);
                              if (parsed !== null) updateParam(item.key as any, parsed);
                            }}
                            className="w-20 bg-transparent text-right font-black text-slate-900 text-sm focus:outline-none"
                          />
                          <span className="text-[10px] font-black text-slate-700">{item.unit}</span>
                        </div>
                      </div>
                      <input
                        type="range"
                        min={item.min}
                        max={item.max}
                        step={item.step}
                        value={params[item.key as any]}
                        onChange={(e) => updateParam(item.key as any, Number(e.target.value))}
                        className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-blue-500"
                      />
                    </div>
                   ))}
                 </>
               )}

               <div className="p-8 rounded-[2rem] bg-white/[0.01] border border-slate-200 space-y-6">
                  <div className="flex justify-between items-center">
                    <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Carga Distribuída (q)</p>
                    <div className="flex items-center gap-2">
                       <input 
                         type="text"
                         value={params.q}
                         onChange={(e) => {
                           const parsed = parseLocaleNumberInput(e.target.value);
                           if (parsed !== null) updateParam("q" as any, parsed);
                         }}
                         className="w-16 bg-transparent text-right font-black text-slate-900 text-sm focus:outline-none"
                       />
                       <span className="text-[10px] font-black text-slate-700">kN/m²</span>
                    </div>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={500}
                    step={1}
                    value={params.q}
                    onChange={(e) => updateParam("q" as any, Number(e.target.value))}
                    className="w-full h-1 bg-white/5 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />

                  <div className="p-6 rounded-2xl bg-white/80 border border-slate-200 space-y-4">
                     <div className="flex items-center justify-between">
                        <p className="text-[9px] font-black uppercase tracking-[0.2em] text-slate-600">Iteração Multi-Pav</p>
                        <input 
                          type="number" 
                          min={1} 
                          max={20} 
                          value={numPavimentos} 
                          onChange={(e) => setNumPavimentos(Number(e.target.value))} 
                          className="w-12 bg-transparent text-right font-black text-blue-600 text-xs outline-none" 
                        />
                     </div>
                     <button
                       type="button"
                       onClick={estimateLoads}
                       className="w-full py-3 rounded-xl bg-white/5 text-[9px] font-black uppercase tracking-widest text-slate-600 hover:bg-white/10 hover:text-slate-900 transition-all border border-slate-200"
                     >
                       Estimar Carga (NBR 6120)
                     </button>
                     
                     {showLoadToast && (
                       <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-[9px] font-black text-emerald-600 tracking-widest uppercase animate-in zoom-in">
                         <CheckCircle2 className="h-3 w-3" />
                         Sync Completo
                       </div>
                     )}
                  </div>
               </div>
            </div>
         </div>
      </div>

      {/* Advanced Section Inputs (Ribbed, Prestressed etc) */}
      {systemType === "laje" && slabType !== "solid" && (
        <section className="p-10 rounded-[2.5rem] bg-emerald-600/5 border border-emerald-500/10 space-y-8">
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-4">
                <Box className="h-5 w-5 text-emerald-600" />
                <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Arquitetura de Seção Discreta</h3>
             </div>
             <div className="text-[9px] font-black text-emerald-500/60 uppercase tracking-widest border border-emerald-500/20 px-3 py-1 rounded-full">
                NBR 6118 COMPLIANT
             </div>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3">
            {slabType === "ribbed" && (
              <>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Largura Nervura (bw)</p>
                  <input 
                    type="number" step="0.01" value={b_nerv} 
                    onChange={(e) => setBNerv(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Dist. entre Eixos</p>
                  <input 
                    type="number" step="0.05" value={dist_nerv} 
                    onChange={(e) => setDistNerv(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Espessura Mesa (hf)</p>
                  <input 
                    type="number" step="0.01" value={h_mesa} 
                    onChange={(e) => setHMesa(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
              </>
            )}
            
            {slabType === "hollow_core" && (
              <>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Área de Vazios (m²/m)</p>
                  <input 
                    type="number" step="0.005" value={area_voids} 
                    onChange={(e) => setAreaVoids(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Protensão (kN/m)</p>
                  <input 
                    type="number" step="10" value={p_force} 
                    onChange={(e) => setPForce(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
              </>
            )}

            {slabType === "prestressed" && (
              <>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Força de Ancoragem (kN/m)</p>
                  <input 
                    type="number" step="10" value={p_force} 
                    onChange={(e) => setPForce(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
                <div className="space-y-3">
                  <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">Excentricidade (ep)</p>
                  <input 
                    type="number" step="0.01" value={ecc} 
                    onChange={(e) => setEcc(Number(e.target.value))}
                    className="w-full bg-white/80 rounded-xl border border-slate-200 px-4 py-3 text-sm font-black text-slate-900 focus:border-emerald-500 outline-none transition-all"
                  />
                </div>
              </>
            )}
          </div>
        </section>
      )}

      {/* Spatial Distribution Section */}
      <div className="space-y-6">
        <div className="flex items-center gap-4 px-2">
           <Binary className="h-4 w-4 text-blue-600" />
           <h3 className="font-black text-slate-900 uppercase text-[10px] tracking-[0.3em]">Distribuição Espacial de Cargas</h3>
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
      </div>

      {/* Editor Sections */}
      <div className="mt-12 space-y-12 border-t border-slate-200 pt-12">
        <HoleEditor holes={holes} setHoles={setHoles} slabType={slabType} />
        <AreaLoadEditor areaLoads={areaLoads} setAreaLoads={setAreaLoads} />
      </div>

      {/* Execution Button */}
      {mode === "academic" && (
        <div className="mt-20 flex justify-center pb-12">
          <button
            type="button"
            onClick={runAnalysis}
            disabled={loading}
            className="group relative flex items-center gap-6 rounded-[2.5rem] bg-blue-600 px-16 py-8 text-xl font-black text-white shadow-[0_30px_60px_rgba(37,99,235,0.4)] transition-all hover:bg-blue-500 hover:scale-105 active:scale-95 disabled:opacity-20"
          >
            <div className={cn(
               "flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20",
               loading ? "animate-spin" : "group-hover:rotate-12 transition-transform"
            )}>
              <Zap className="h-6 w-6" />
            </div>
            <div className="text-left">
               <span className="block tracking-tight">{loading ? "Solving Systems..." : "Calcular Modelo MEF"}</span>
               <span className="block text-[10px] font-black uppercase tracking-[0.3em] opacity-60">High Performance Compute</span>
            </div>
          </button>
        </div>
      )}
    </div>
  );
}
