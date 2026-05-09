import React from "react";
import { Zap, Wind, Layers3 } from "lucide-react";
import { formatNumberBR, cn } from "../utils";
import { Result } from "../types";

interface GeotechnicalModuleProps {
  activeTab: "stability" | "retaining_wall";
  windParams: any;
  setWindParams: React.Dispatch<React.SetStateAction<any>>;
  retainingWallParams: any;
  setRetainingWallParams: React.Dispatch<React.SetStateAction<any>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
}

export function GeotechnicalModule({
  activeTab,
  windParams,
  setWindParams,
  retainingWallParams,
  setRetainingWallParams,
  result,
  loading,
  calculate
}: GeotechnicalModuleProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="space-y-6">
        {activeTab === "stability" ? (
          <div className="space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Parâmetros do Edifício</p>
            <div>
              <label className="text-xs font-bold text-[#667085]">V0 (Velocidade Básica) [m/s]</label>
              <input type="number" value={windParams.v0} onChange={(e) => setWindParams({ ...windParams, v0: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-bold text-[#667085]">Altura Total [m]</label>
                <input type="number" value={windParams.height} onChange={(e) => setWindParams({ ...windParams, height: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">Largura X [m]</label>
                <input type="number" value={windParams.width_x} onChange={(e) => setWindParams({ ...windParams, width_x: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Parâmetros do Muro</p>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-bold text-[#667085]">Altura H [m]</label>
                <input type="number" value={retainingWallParams.h_wall} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, h_wall: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">Base B [m]</label>
                <input type="number" value={retainingWallParams.b_base} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, b_base: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-bold text-[#667085]">φ Solo [°]</label>
                <input type="number" value={retainingWallParams.phi_soil} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, phi_soil: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">γ Solo [kN/m³]</label>
                <input type="number" value={retainingWallParams.gamma_soil} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, gamma_soil: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
            </div>
          </div>
        )}

        <button onClick={calculate} disabled={loading} className="w-full flex items-center justify-center gap-2 rounded-2xl bg-black py-4 font-black text-white hover:bg-[#1d2939] transition-all disabled:opacity-50">
          {loading ? "Calculando..." : <><Zap size={18} /> Dimensionar</>}
        </button>
      </div>

      <div className="lg:col-span-2 space-y-6">
        {result && (
          <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
            <h3 className="font-black text-xl text-[#101828] mb-6">
              {activeTab === "stability" ? "Estabilidade Global (Gamma-Z)" : "Estabilidade do Muro"}
            </h3>

            {activeTab === "stability" ? (
              <div className="space-y-6">
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 rounded-2xl bg-teal-50 border border-teal-100">
                       <p className="text-xs font-bold text-teal-700 uppercase">Coeficiente γz</p>
                       <p className="text-3xl font-black text-teal-900">{formatNumberBR(result.summary?.gamma_z ?? 1.10, 3)}</p>
                       <p className={cn(
                         "mt-2 text-[10px] font-black uppercase px-2 py-0.5 rounded-full inline-block",
                         (result.summary?.gamma_z ?? 1.10) <= 1.1 ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                       )}>
                         {(result.summary?.gamma_z ?? 1.10) <= 1.1 ? "Edifício de Nós Fixos" : "Edifício de Nós Móveis"}
                       </p>
                    </div>
                    <div className="p-5 rounded-2xl bg-teal-50 border border-teal-100">
                       <p className="text-xs font-bold text-teal-700 uppercase">Pressão do Vento (Topo)</p>
                       <p className="text-3xl font-black text-teal-900">{formatNumberBR(result.summary?.wind_pressure_kPa ?? 0, 2)} kPa</p>
                    </div>
                 </div>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100">
                  <p className="text-xs font-bold text-teal-700 uppercase">Segurança Tombamento (FS_t)</p>
                  <p className="mt-2 text-3xl font-black text-teal-900">{formatNumberBR(result.summary?.fs_tomb, 2)}</p>
                  <p className="text-[10px] font-bold text-teal-600 mt-1">Mínimo NBR: 1.50</p>
                </div>
                <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100">
                  <p className="text-xs font-bold text-teal-700 uppercase">Segurança Deslizamento (FS_d)</p>
                  <p className="mt-2 text-3xl font-black text-teal-900">{formatNumberBR(result.summary?.fs_desl, 2)}</p>
                  <p className="text-[10px] font-bold text-teal-600 mt-1">Mínimo NBR: 1.50</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
