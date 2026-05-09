import React from "react";
import { Zap, BookOpen } from "lucide-react";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";

interface StairModuleProps {
  stairParams: any;
  setStairParams: React.Dispatch<React.SetStateAction<any>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
  setShowFullMemorial: (val: boolean) => void;
}

export function StairModule({
  stairParams,
  setStairParams,
  result,
  loading,
  calculate,
  setShowFullMemorial
}: StairModuleProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria e Carga</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Vão (L) [m]</label>
              <input type="number" value={stairParams.L} onChange={(e) => setStairParams({ ...stairParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Altura (H) [m]</label>
              <input type="number" value={stairParams.H} onChange={(e) => setStairParams({ ...stairParams, H: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Largura [m]</label>
              <input type="number" value={stairParams.width} onChange={(e) => setStairParams({ ...stairParams, width: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Carga q [kN/m²]</label>
              <input type="number" value={stairParams.q} onChange={(e) => setStairParams({ ...stairParams, q: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Espessura [cm]</label>
              <input type="number" value={stairParams.t} onChange={(e) => setStairParams({ ...stairParams, t: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
              <input type="number" value={stairParams.fck} onChange={(e) => setStairParams({ ...stairParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
        </div>

        <button onClick={calculate} disabled={loading} className="w-full flex items-center justify-center gap-2 rounded-2xl bg-black py-4 font-black text-white hover:bg-[#1d2939] transition-all disabled:opacity-50">
          {loading ? "Calculando..." : <><Zap size={18} /> Dimensionar</>}
        </button>
      </div>

      <div className="lg:col-span-2 space-y-6">
        {result && (
          <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-black text-xl text-[#101828]">Resultados da Escada</h3>
              <button onClick={() => setShowFullMemorial(true)} className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-[10px] font-black uppercase">
                <BookOpen size={12} /> Memorial Pedagógico
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                <p className="text-xs font-bold text-[#667085] uppercase">Momento Máximo</p>
                <p className="mt-2 text-2xl font-black text-amber-600">
                  {formatNumberBR(result.summary?.Mk || result.summary?.m_max_kNm || 0, 2)} 
                  <span className="text-sm text-[#8a9ab0]"> kNm/m</span>
                </p>
              </div>
              <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                <p className="text-xs font-bold text-[#667085] uppercase">Armadura principal</p>
                <p className="mt-2 text-2xl font-black text-emerald-600">{formatNumberBR(result.summary?.As_cm2_m || 0)} <span className="text-sm text-[#8a9ab0]">cm²/m</span></p>
              </div>
              <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                <p className="text-xs font-bold text-[#667085] uppercase">Status</p>
                <span className={cn(
                  "mt-3 inline-flex rounded-full px-2 py-1 text-[10px] font-black",
                  result.summary?.status === "ATENDE" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700 animate-pulse"
                )}>
                  {result.summary?.status || "OK"}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
