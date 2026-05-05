"use client";

import React from "react";
import { 
  Wind, 
  Activity, 
  BarChart3, 
  Info, 
  Zap, 
  AlertCircle, 
  CheckCircle2,
  TrendingUp,
  Box,
  MoveRight,
  Maximize2
} from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";

interface WindStabilityViewProps {
  params: {
    v0: number;
    altura_total: number;
    largura: number;
    profundidade: number;
    step: number;
    categoria: number;
    classe: string;
    s1: number;
    s3: number;
    is_dynamic: boolean;
    f1: number;
    zeta: number;
    total_p_kN: number;
  };
  onParamChange: (key: string, value: any) => void;
  onRunAnalysis: () => void;
  results: any;
  stabilityResults: any;
  loading: boolean;
}

export function WindStabilityView({
  params,
  onParamChange,
  onRunAnalysis,
  results,
  stabilityResults,
  loading
}: WindStabilityViewProps) {
  const summary = results?.summary;
  const profile = results?.profile || [];
  const stability = stabilityResults;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-in fade-in duration-500">
      {/* Sidebar de Parâmetros */}
      <div className="lg:col-span-4 space-y-6">
        <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#f0f4f8] rounded-xl">
              <Wind className="w-5 h-5 text-[#2b5a9e]" />
            </div>
            <h3 className="text-lg font-black text-[#1a1c1e]">Configuração de Vento</h3>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">V₀ (m/s)</label>
                <input
                  type="number"
                  value={params.v0}
                  onChange={(e) => onParamChange("v0", parseFloat(e.target.value))}
                  className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold focus:ring-2 focus:ring-[#2b5a9e] outline-none transition-all"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Passo (m)</label>
                <input
                  type="number"
                  value={params.step}
                  onChange={(e) => onParamChange("step", parseFloat(e.target.value))}
                  className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold focus:ring-2 focus:ring-[#2b5a9e] outline-none transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Categoria</label>
                <select
                  value={params.categoria}
                  onChange={(e) => onParamChange("categoria", parseInt(e.target.value))}
                  className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold outline-none"
                >
                  {[1, 2, 3, 4, 5].map(v => <option key={v} value={v}>Categoria {v}</option>)}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Classe</label>
                <select
                  value={params.classe}
                  onChange={(e) => onParamChange("classe", e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold outline-none"
                >
                  {["A", "B", "C"].map(v => <option key={v} value={v}>Classe {v}</option>)}
                </select>
              </div>
            </div>

            <div className="pt-4 border-t border-dashed border-[#e2e8f0]">
              <div className="flex items-center justify-between mb-4">
                <label className="text-sm font-black text-[#1a1c1e]">Análise Dinâmica</label>
                <button
                  onClick={() => onParamChange("is_dynamic", !params.is_dynamic)}
                  className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none",
                    params.is_dynamic ? "bg-[#2b5a9e]" : "bg-[#e2e8f0]"
                  )}
                >
                  <span
                    className={cn(
                      "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                      params.is_dynamic ? "translate-x-6" : "translate-x-1"
                    )}
                  />
                </button>
              </div>

              {params.is_dynamic && (
                <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">f₁ (Hz)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={params.f1}
                        onChange={(e) => onParamChange("f1", parseFloat(e.target.value))}
                        className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold outline-none"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Zeta (ζ)</label>
                      <input
                        type="number"
                        step="0.005"
                        value={params.zeta}
                        onChange={(e) => onParamChange("zeta", parseFloat(e.target.value))}
                        className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-dashed border-[#e2e8f0]">
              <div className="space-y-1.5">
                <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Peso Total P (kN)</label>
                <input
                  type="number"
                  value={params.total_p_kN}
                  onChange={(e) => onParamChange("total_p_kN", parseFloat(e.target.value))}
                  className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold outline-none"
                />
                <p className="text-[10px] text-[#8a9ab0]">Utilizado para o cálculo de estabilidade global (Gamma-Z).</p>
              </div>
            </div>

            <button
              onClick={onRunAnalysis}
              disabled={loading}
              className="w-full py-4 mt-4 bg-[#1a1c1e] text-white rounded-2xl font-black flex items-center justify-center gap-2 hover:bg-[#2d3135] disabled:opacity-50 transition-all shadow-lg"
            >
              {loading ? (
                <Activity className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Zap className="w-5 h-5 fill-current" />
                  <span>Calcular Vento + Estabilidade</span>
                </>
              )}
            </button>
          </div>
        </div>

        {stability && (
          <div className={cn(
            "rounded-3xl border p-6 shadow-sm transition-colors",
            stability.is_stable ? "bg-[#f0fdf4] border-[#bcf0da]" : "bg-[#fef2f2] border-[#fecaca]"
          )}>
            <div className="flex items-center gap-3 mb-4">
              {stability.is_stable ? (
                <CheckCircle2 className="w-6 h-6 text-[#1f8f56]" />
              ) : (
                <AlertCircle className="w-6 h-6 text-[#c52626]" />
              )}
              <h3 className="text-lg font-black text-[#1a1c1e]">Estabilidade Global</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-sm font-bold text-[#6a7485]">Fator γz:</span>
                <span className={cn(
                  "text-2xl font-black",
                  stability.gamma_z > 1.3 ? "text-[#c52626]" : stability.gamma_z > 1.1 ? "text-[#b45309]" : "text-[#1f8f56]"
                )}>
                  {formatNumberBR(stability.gamma_z, 3)}
                </span>
              </div>

              <div className="bg-white/50 rounded-2xl p-4 space-y-2 border border-white/50">
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-[#6a7485]">P-Delta Iterações:</span>
                  <span className="text-[#1a1c1e]">{stability.p_delta_iterations}</span>
                </div>
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-[#6a7485]">Conforto (Aceleração):</span>
                  <span className={cn(
                    "px-2 py-0.5 rounded-full text-[10px]",
                    stability.comfort_status === "CONFORTO" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                  )}>
                    {stability.comfort_status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Área de Resultados Principal */}
      <div className="lg:col-span-8 space-y-6">
        {summary ? (
          <>
            <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm overflow-hidden">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#f0f4f8] rounded-xl">
                    <Activity className="w-5 h-5 text-[#2b5a9e]" />
                  </div>
                  <h3 className="text-lg font-black text-[#1a1c1e]">Perfil de Pressão Dinâmica (q)</h3>
                </div>
                <div className="text-[10px] font-black text-[#6a7485] uppercase tracking-wider bg-[#f8fafc] px-3 py-1 rounded-full border border-[#e2e8f0]">
                  Pressão vs Altura
                </div>
              </div>
              
              <div className="flex items-end gap-1 h-[200px] w-full px-4 border-l-2 border-b-2 border-[#f0f4f8] relative">
                {profile.map((lvl: any, idx: number) => (
                  <div 
                    key={idx}
                    className="flex-1 bg-[#2b5a9e] hover:bg-[#3b82f6] transition-all rounded-t-sm group relative"
                    style={{ height: `${(lvl.q_Pa / Math.max(...profile.map((p: any) => p.q_Pa))) * 100}%` }}
                  >
                    <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-[#1a1c1e] text-white text-[10px] py-1.5 px-2.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 font-black shadow-xl">
                      {formatNumberBR(lvl.z, 1)}m: {formatNumberBR(lvl.q_Pa)} Pa
                    </div>
                  </div>
                ))}
                
                {/* Grid horizontal Lines */}
                <div className="absolute top-0 left-0 w-full border-t border-dashed border-[#f1f5f9] -z-10" style={{ top: '25%' }} />
                <div className="absolute top-0 left-0 w-full border-t border-dashed border-[#f1f5f9] -z-10" style={{ top: '50%' }} />
                <div className="absolute top-0 left-0 w-full border-t border-dashed border-[#f1f5f9] -z-10" style={{ top: '75%' }} />
              </div>
              <div className="flex justify-between mt-4 text-[10px] font-black text-[#6a7485] px-2">
                <span>Cota 0.0m</span>
                <span>Cota {formatNumberBR(params.altura_total, 1)}m</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-wider text-[#6a7485] mb-1">Força Total</p>
                <p className="text-3xl font-black text-[#1a1c1e]">{formatNumberBR(summary.total_force_kN)} <span className="text-sm font-bold text-[#8a9ab0]">kN</span></p>
                <div className="mt-4 flex items-center gap-2 text-xs font-bold text-[#1f8f56]">
                  <TrendingUp className="w-3 h-3" />
                  <span>Resultante em X/Y</span>
                </div>
              </div>
              <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-wider text-[#6a7485] mb-1">Momento na Base</p>
                <p className="text-3xl font-black text-[#1a1c1e]">{formatNumberBR(summary.base_moment_kNm)} <span className="text-sm font-bold text-[#8a9ab0]">kNm</span></p>
                <div className="mt-4 flex items-center gap-2 text-xs font-bold text-[#2b5a9e]">
                  <BarChart3 className="w-3 h-3" />
                  <span>Tombamento total</span>
                </div>
              </div>
              <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-wider text-[#6a7485] mb-1">Pressão Máxima</p>
                <p className="text-3xl font-black text-[#1a1c1e]">{formatNumberBR(summary.max_q_Pa)} <span className="text-sm font-bold text-[#8a9ab0]">Pa</span></p>
                <div className="mt-4 flex items-center gap-2 text-xs font-bold text-[#6a7485]">
                  <Info className="w-3 h-3" />
                  <span>Topo da edificação</span>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-[#e0e7ef] bg-white overflow-hidden shadow-sm">
              <div className="p-6 border-b border-[#e0e7ef] flex items-center justify-between bg-[#f8fafc]">
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-[#2b5a9e]" />
                  <h3 className="text-lg font-black text-[#1a1c1e]">Perfil de Forças por Nível</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-bold text-[#6a7485]">Coef. Arrasto Cf:</span>
                  <span className="px-3 py-1 bg-white border border-[#e2e8f0] rounded-full text-xs font-black text-[#1a1c1e]">
                    {formatNumberBR(results.geometry?.cf)}
                  </span>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#f1f5f9]">
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">Z (m)</th>
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">S2</th>
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">Vk (m/s)</th>
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">q (Pa)</th>
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">Área (m²)</th>
                      <th className="px-6 py-3 text-[10px] font-black uppercase tracking-wider text-[#6a7485] border-b border-[#e2e8f0]">Força (kN)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#e2e8f0]">
                    {profile.map((level: any, i: number) => (
                      <tr key={i} className="hover:bg-[#f8fafc] transition-colors group">
                        <td className="px-6 py-4 text-sm font-black text-[#1a1c1e]">{formatNumberBR(level.z, 1)}</td>
                        <td className="px-6 py-4 text-sm font-bold text-[#64748b]">{formatNumberBR(level.s2, 3)}</td>
                        <td className="px-6 py-4 text-sm font-bold text-[#64748b]">{formatNumberBR(level.vk_m_s)}</td>
                        <td className="px-6 py-4 text-sm font-bold text-[#2b5a9e]">{formatNumberBR(level.q_Pa, 1)}</td>
                        <td className="px-6 py-4 text-sm font-bold text-[#64748b]">{formatNumberBR(level.area_m2, 1)}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-black text-[#1a1c1e] min-w-[60px]">{formatNumberBR(level.f_total_kN)}</span>
                            <div className="flex-1 h-2 bg-[#f1f5f9] rounded-full overflow-hidden min-w-[80px]">
                              <div 
                                className="h-full bg-[#2b5a9e] rounded-full group-hover:bg-[#3b82f6] transition-all"
                                style={{ width: `${(level.f_total_kN / summary.max_force_level_kN) * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="h-[600px] rounded-3xl border border-dashed border-[#cbd5e1] flex flex-col items-center justify-center text-center p-12 bg-[#f8fafc]">
            <div className="p-6 bg-white rounded-full shadow-sm mb-6">
              <Wind className="w-12 h-12 text-[#94a3b8]" />
            </div>
            <h3 className="text-xl font-black text-[#1a1c1e] mb-2">Aguardando Análise</h3>
            <p className="text-[#64748b] max-w-sm">
              Configure os parâmetros de vento ao lado e execute o cálculo para visualizar o perfil de forças e estabilidade global.
            </p>
            <div className="mt-8 flex gap-3">
              <div className="px-4 py-2 bg-white border border-[#e2e8f0] rounded-xl flex items-center gap-2 shadow-sm">
                <Box className="w-4 h-4 text-[#2b5a9e]" />
                <span className="text-xs font-bold text-[#475569]">NBR 6123</span>
              </div>
              <div className="px-4 py-2 bg-white border border-[#e2e8f0] rounded-xl flex items-center gap-2 shadow-sm">
                <Maximize2 className="w-4 h-4 text-[#2b5a9e]" />
                <span className="text-xs font-bold text-[#475569]">Gama-Z</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
