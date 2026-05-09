import React from "react";
import { Zap, BookOpen } from "lucide-react";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";

interface SpecificElementsModuleProps {
  activeTab: string;
  corbelParams: any;
  setCorbelParams: React.Dispatch<React.SetStateAction<any>>;
  gerberParams: any;
  setGerberParams: React.Dispatch<React.SetStateAction<any>>;
  deepBeamParams: any;
  setDeepBeamParams: React.Dispatch<React.SetStateAction<any>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
  setShowFullMemorial: (val: boolean) => void;
}

export function SpecificElementsModule({
  activeTab,
  corbelParams,
  setCorbelParams,
  gerberParams,
  setGerberParams,
  deepBeamParams,
  setDeepBeamParams,
  result,
  loading,
  calculate,
  setShowFullMemorial
}: SpecificElementsModuleProps) {
  const getParams = () => {
    if (activeTab === "corbel") return { params: corbelParams, setParams: setCorbelParams, title: "Consolo Curto" };
    if (activeTab === "gerber_tooth") return { params: gerberParams, setParams: setGerberParams, title: "Dente Gerber" };
    return { params: deepBeamParams, setParams: setDeepBeamParams, title: "Viga Parede" };
  };

  const { params, setParams, title } = getParams();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Parâmetros de {title}</p>
          {activeTab === "corbel" && (
            <>
              <div>
                <label className="text-xs font-bold text-[#667085]">Fd [kN]</label>
                <input type="number" value={params.fd_kN} onChange={(e) => setParams({ ...params, fd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">a (Distância) [m]</label>
                <input type="number" value={params.a_dist} onChange={(e) => setParams({ ...params, a_dist: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">d (Efetivo) [m]</label>
                <input type="number" value={params.d_eff} onChange={(e) => setParams({ ...params, d_eff: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </>
          )}
          {activeTab === "gerber_tooth" && (
            <>
              <div>
                <label className="text-xs font-bold text-[#667085]">Vd [kN]</label>
                <input type="number" value={params.vd_kN} onChange={(e) => setParams({ ...params, vd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">Hd [kN]</label>
                <input type="number" value={params.hd_kN} onChange={(e) => setParams({ ...params, hd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                 <div>
                    <label className="text-xs font-bold text-[#667085]">d [m]</label>
                    <input type="number" value={params.d_eff} onChange={(e) => setParams({ ...params, d_eff: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                 </div>
                 <div>
                    <label className="text-xs font-bold text-[#667085]">b [m]</label>
                    <input type="number" value={params.b_width} onChange={(e) => setParams({ ...params, b_width: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                 </div>
              </div>
            </>
          )}
          {activeTab === "deep_beam" && (
            <>
              <div className="grid grid-cols-2 gap-2">
                 <div>
                    <label className="text-xs font-bold text-[#667085]">Vão L [m]</label>
                    <input type="number" value={params.L} onChange={(e) => setParams({ ...params, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                 </div>
                 <div>
                    <label className="text-xs font-bold text-[#667085]">Altura H [m]</label>
                    <input type="number" value={params.h} onChange={(e) => setParams({ ...params, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                 </div>
              </div>
            </>
          )}
          <div>
            <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
            <input type="number" value={params.fck} onChange={(e) => setParams({ ...params, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
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
              <h3 className="font-black text-xl text-[#101828] uppercase">{title}</h3>
              <button onClick={() => setShowFullMemorial(true)} className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-[10px] font-black uppercase">
                <BookOpen size={12} /> Memorial
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                <p className="text-xs font-bold text-[#667085] uppercase">Armadura (As)</p>
                <p className="mt-2 text-2xl font-black text-emerald-600">
                  {formatNumberBR(result.summary?.as_cm2 || result.summary?.as_tirante_cm2 || 0, 2)} 
                  <span className="text-sm text-[#8a9ab0]"> cm²</span>
                </p>
              </div>
              <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                <p className="text-xs font-bold text-[#667085] uppercase">Status de Biela</p>
                <span className={cn(
                  "mt-3 inline-flex rounded-full px-2 py-1 text-[10px] font-black",
                  (result.summary?.status === "OK" || result.summary?.status_biela === "OK") ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700 animate-pulse"
                )}>
                  {result.summary?.status || result.summary?.status_biela || "VERIFICAR"}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
