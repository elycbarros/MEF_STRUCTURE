import React from "react";
import { Zap, Activity, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";
import { ElegantTooltip } from "../../ui/ElegantTooltip";
import { FiberSectionMap } from "../../FiberSectionMap";

interface ColumnModuleProps {
  colParams: any;
  setColParams: React.Dispatch<React.SetStateAction<any>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
}

export function ColumnModule({
  colParams,
  setColParams,
  result,
  loading,
  calculate
}: ColumnModuleProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Inputs Column */}
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria do Pilar</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">b [m]</label>
              <input type="number" value={colParams.b} onChange={(e) => setColParams({ ...colParams, b: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">h [m]</label>
              <input type="number" value={colParams.h} onChange={(e) => setColParams({ ...colParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div>
            <label className="text-xs font-bold text-[#667085]">Carga de Cálculo (Nd) [kN]</label>
            <input type="number" value={colParams.Nd} onChange={(e) => setColParams({ ...colParams, Nd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Mxd [kNm]</label>
              <input type="number" value={colParams.Mxd} onChange={(e) => setColParams({ ...colParams, Mxd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Myd [kNm]</label>
              <input type="number" value={colParams.Myd} onChange={(e) => setColParams({ ...colParams, Myd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div>
            <label className="text-xs font-bold text-[#667085]">Altura Livre (Lf) [m]</label>
            <input type="number" value={colParams.L_free} onChange={(e) => setColParams({ ...colParams, L_free: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <ElegantTooltip content="Resistência característica do concreto à compressão.">
                <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
              </ElegantTooltip>
              <input type="number" value={colParams.fck} onChange={(e) => setColParams({ ...colParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">CAA</label>
              <input type="number" min={1} max={4} value={colParams.caa} onChange={(e) => setColParams({ ...colParams, caa: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
        </div>

        <button
          onClick={calculate}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 rounded-2xl bg-black py-4 font-black text-white hover:bg-[#1d2939] active:scale-95 transition-all disabled:opacity-50"
        >
          {loading ? "Calculando..." : <><Zap size={18} /> Dimensionar</>}
        </button>
      </div>

      {/* Results Column */}
      <div className="lg:col-span-2 space-y-6">
        {result && (
          <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-black text-xl text-[#101828]">Análise do Pilar</h3>
              <span className="px-3 py-1 bg-[#f2f4f7] rounded-full text-[10px] font-black uppercase text-[#667085]">Fiber Model - NBR 6118</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-bold text-[#667085] uppercase">Armadura Final (As)</p>
                  <p className="text-3xl font-black text-emerald-600">
                    {formatNumberBR(result.design?.As_final_cm2 ?? result.as_bottom_cm2)} 
                    <span className="text-sm font-bold text-[#8a9ab0]"> cm²</span>
                  </p>
                </div>
                <div>
                  <p className="text-xs font-bold text-[#667085] uppercase">Índice de Esbeltez (λ)</p>
                  <p className="text-3xl font-black">{formatNumberBR(result.design?.slenderness?.lambda_x ?? 0, 1)}</p>
                </div>
                <div className="rounded-2xl bg-[#f9fafb] p-6 space-y-3 border border-[#f2f4f7]">
                  <p className="text-sm font-bold">Status do Pilar</p>
                  <span className={cn(
                    "text-[10px] px-2 py-0.5 rounded-full font-black",
                    (result.design?.status || result.summary?.overall_status) === "OK" ? "bg-emerald-100 text-emerald-700" : "bg-red-600 text-white animate-pulse"
                  )}>
                    {result.design?.status || result.summary?.overall_status || "PENDENTE"}
                  </span>
                  <p className="text-xs text-[#667085]">Pilar verificado via Integração Numérica (Modelo de Fibras). Considera efeitos de 2ª ordem locais.</p>
                </div>
              </div>

              {result.summary?.fiber_results?.fibers && (
                <div className="col-span-1">
                  <FiberSectionMap 
                    fibers={result.summary.fiber_results.fibers} 
                    b={colParams.b} 
                    h={colParams.h} 
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
