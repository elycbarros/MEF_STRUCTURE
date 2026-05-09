import React from "react";
import { Zap, Search, Box } from "lucide-react";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";

interface FoundationModuleProps {
  activeTab: "footing" | "spt";
  footingParams: any;
  setFootingParams: React.Dispatch<React.SetStateAction<any>>;
  sptData: any[];
  setSptData: React.Dispatch<React.SetStateAction<any[]>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
}

export function FoundationModule({
  activeTab,
  footingParams,
  setFootingParams,
  sptData,
  setSptData,
  result,
  loading,
  calculate
}: FoundationModuleProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6">
        {activeTab === "footing" ? (
          <div className="space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Parâmetros da Sapata</p>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-bold text-[#667085]">Nd [kN]</label>
                <input type="number" value={footingParams.Nd} onChange={(e) => setFootingParams({ ...footingParams, Nd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">σ adm [kPa]</label>
                <input type="number" value={footingParams.sigma_adm} onChange={(e) => setFootingParams({ ...footingParams, sigma_adm: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-bold text-[#667085]">ap [m]</label>
                <input type="number" value={footingParams.ap} onChange={(e) => setFootingParams({ ...footingParams, ap: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">bp [m]</label>
                <input type="number" value={footingParams.bp} onChange={(e) => setFootingParams({ ...footingParams, bp: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
              <input type="number" value={footingParams.fck} onChange={(e) => setFootingParams({ ...footingParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Sondagem SPT</p>
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {sptData.map((layer, idx) => (
                <div key={idx} className="flex gap-2 items-center bg-white p-2 rounded-xl border border-slate-100">
                  <span className="text-[10px] font-black w-8">{layer.depth_m}m</span>
                  <input type="number" value={layer.nspt} onChange={(e) => {
                    const newSpt = [...sptData];
                    newSpt[idx].nspt = Number(e.target.value);
                    setSptData(newSpt);
                  }} className="w-16 rounded-lg border border-[#e0e7ef] p-1 text-xs font-bold text-center" />
                  <input type="text" value={layer.soil_type} onChange={(e) => {
                    const newSpt = [...sptData];
                    newSpt[idx].soil_type = e.target.value;
                    setSptData(newSpt);
                  }} className="flex-1 rounded-lg border border-[#e0e7ef] p-1 text-xs font-medium" />
                </div>
              ))}
            </div>
          </div>
        )}

        <button onClick={calculate} disabled={loading} className="w-full flex items-center justify-center gap-2 rounded-2xl bg-black py-4 font-black text-white hover:bg-[#1d2939] transition-all disabled:opacity-50">
          {loading ? "Calculando..." : <><Zap size={18} /> Analisar</>}
        </button>
      </div>

      <div className="lg:col-span-2 space-y-6">
        {result && (
          <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
            <h3 className="font-black text-xl text-[#101828] mb-6">
              {activeTab === "footing" ? "Dimensionamento da Sapata" : "Interpretação Geotécnica"}
            </h3>

            {activeTab === "footing" ? (
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                  <p className="text-xs font-bold text-[#667085] uppercase">Dimensões (a × b)</p>
                  <p className="mt-2 text-2xl font-black">{formatNumberBR(result.summary?.a_m)} × {formatNumberBR(result.summary?.b_m)} m</p>
                </div>
                <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                  <p className="text-xs font-bold text-[#667085] uppercase">Espessura (h)</p>
                  <p className="mt-2 text-2xl font-black">{formatNumberBR(result.summary?.h_m)} m</p>
                </div>
                <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                  <p className="text-xs font-bold text-[#667085] uppercase">Pressão Real</p>
                  <p className="mt-2 text-2xl font-black">{formatNumberBR(result.summary?.sigma_real_kPa)} kPa</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                 <p className="text-sm font-bold text-slate-600">O solo foi analisado metro a metro. Abaixo as conclusões para assentamento superficial.</p>
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
                       <p className="text-xs font-bold text-blue-700 uppercase">Tensão Admissível Estimada</p>
                       <p className="text-2xl font-black text-blue-900">{formatNumberBR(result.summary?.sigma_adm_estimada_kPa ?? 0)} kPa</p>
                    </div>
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100">
                       <p className="text-xs font-bold text-emerald-700 uppercase">Cota de Assentamento</p>
                       <p className="text-2xl font-black text-emerald-900">{formatNumberBR(result.summary?.cota_assentamento_m ?? 1.5, 1)} m</p>
                    </div>
                 </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
