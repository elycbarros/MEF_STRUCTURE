import React from "react";
import { Zap, BookOpen } from "lucide-react";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";

interface ReservoirModuleProps {
  resParams: any;
  setResParams: React.Dispatch<React.SetStateAction<any>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
  setShowFullMemorial: (val: boolean) => void;
}

export function ReservoirModule({
  resParams,
  setResParams,
  result,
  loading,
  calculate,
  setShowFullMemorial
}: ReservoirModuleProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria do Reservatório</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Largura (L) [m]</label>
              <input type="number" value={resParams.L} onChange={(e) => setResParams({ ...resParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Altura (H) [m]</label>
              <input type="number" value={resParams.H} onChange={(e) => setResParams({ ...resParams, H: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div>
            <label className="text-xs font-bold text-[#667085]">Espessura da Parede (t) [cm]</label>
            <input type="number" value={resParams.t} onChange={(e) => setResParams({ ...resParams, t: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
          </div>
          <div>
            <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
            <input type="number" value={resParams.fck} onChange={(e) => setResParams({ ...resParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
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
              <h3 className="font-black text-xl text-[#101828]">Resultados do Reservatório</h3>
              <button onClick={() => setShowFullMemorial(true)} className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-[10px] font-black uppercase">
                <BookOpen size={12} /> Memorial Pedagógico
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100">
                <p className="text-xs font-bold text-blue-700 uppercase">Momento Máximo</p>
                <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.summary?.m_max_kNm || 0, 1)} <span className="text-sm">kNm/m</span></p>
              </div>
              <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100">
                <p className="text-xs font-bold text-blue-700 uppercase">Armadura Base</p>
                <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.summary?.as_base_cm2 || 0, 2)} <span className="text-sm">cm²/m</span></p>
              </div>
              <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100">
                <p className="text-xs font-bold text-blue-700 uppercase">Status</p>
                <p className="mt-2 text-sm font-black">{result.summary?.status || "OK"}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
