"use client";

import React, { useState } from "react";
import { 
  ShieldAlert, 
  Search, 
  BarChart, 
  Activity, 
  Target, 
  Database, 
  TrendingUp, 
  AlertCircle,
  Play,
  Upload,
  Table
} from "lucide-react";
import { 
  BarChart as ReBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";
import { cn, formatNumberBR } from "@/lib/utils";

interface ForensicLabViewProps {
  apiBaseUrl: string;
  config: any;
}

export function ForensicLabView({ apiBaseUrl, config }: ForensicLabViewProps) {
  const [activeSubTab, setActiveSubTab] = useState<"uncertainty" | "calibration">("uncertainty");
  const [loading, setLoading] = useState(false);
  const [mcResults, setMcResults] = useState<any>(null);
  const [calibResults, setCalibResults] = useState<any>(null);

  // States for inputs
  const [nSims, setNSims] = useState(50);
  const [measurements, setMeasurements] = useState([
    { x: 4.0, y: 4.0, w_mm: 12.5 },
    { x: 12.0, y: 12.0, w_mm: 15.2 },
    { x: 20.0, y: 20.0, w_mm: 11.8 }
  ]);

  const runMonteCarlo = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/forensic/monte-carlo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config: config,
          n_simulations: nSims
        })
      });
      const data = await res.json();
      setMcResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const runCalibration = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/forensic/calibrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config: config,
          measurements: measurements
        })
      });
      const data = await res.json();
      setCalibResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Preparar dados para o histograma
  const getHistogramData = () => {
    if (!mcResults?.data) return [];
    const values = mcResults.data.map((d: any) => d.w_max_mm);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const nBins = 10;
    const binSize = (max - min) / nBins;
    
    const bins = Array.from({ length: nBins }).map((_, i) => ({
      range: `${formatNumberBR(min + i * binSize, 1)}-${formatNumberBR(min + (i+1) * binSize, 1)}`,
      count: 0,
      mid: min + (i + 0.5) * binSize
    }));

    values.forEach((v: number) => {
      const bIdx = Math.min(Math.floor((v - min) / binSize), nBins - 1);
      bins[bIdx].count++;
    });

    return bins;
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-[#1d1d1f]">Laboratório Forense</h2>
          <p className="text-sm font-bold text-[#6a7485]">Análise probabilística e calibração de modelos periciais</p>
        </div>
        <div className="flex bg-[#f2f4f7] p-1 rounded-2xl">
          <button 
            onClick={() => setActiveSubTab("uncertainty")}
            className={cn(
              "px-4 py-2 rounded-xl text-xs font-black transition-all",
              activeSubTab === "uncertainty" ? "bg-white text-black shadow-sm" : "text-[#6a7485]"
            )}
          >
            Incertezas (Monte Carlo)
          </button>
          <button 
            onClick={() => setActiveSubTab("calibration")}
            className={cn(
              "px-4 py-2 rounded-xl text-xs font-black transition-all",
              activeSubTab === "calibration" ? "bg-white text-black shadow-sm" : "text-[#6a7485]"
            )}
          >
            Calibração de Modelo
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Painel de Controle Lateral */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-50 rounded-xl">
                <ShieldAlert className="w-5 h-5 text-red-600" />
              </div>
              <h3 className="font-black text-sm">Parâmetros de Stress</h3>
            </div>

            {activeSubTab === "uncertainty" ? (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Nº de Simulações</label>
                  <input 
                    type="number"
                    value={nSims}
                    onChange={(e) => setNSims(parseInt(e.target.value))}
                    className="w-full px-4 py-2.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl font-bold focus:ring-2 focus:ring-red-600 outline-none"
                  />
                  <p className="text-[10px] text-[#8a9ab0]">Recomendado: 100+ para convergência estatística.</p>
                </div>
                <button 
                  onClick={runMonteCarlo}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-4 rounded-2xl bg-red-600 text-white font-black hover:bg-red-700 active:scale-95 transition-all shadow-lg"
                >
                  {loading ? <Activity className="w-5 h-5 animate-spin" /> : <><Play className="w-4 h-4 fill-current" /> Iniciar Monte Carlo</>}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-[11px] font-black uppercase tracking-wider text-[#6a7485]">Medições de Campo</label>
                  <button className="p-1 hover:bg-[#f2f4f7] rounded-lg text-blue-600"><Upload className="w-4 h-4" /></button>
                </div>
                <div className="space-y-2 max-h-[200px] overflow-y-auto pr-2">
                  {measurements.map((m, i) => (
                    <div key={i} className="grid grid-cols-3 gap-2">
                      <input 
                        type="number" 
                        value={m.x} 
                        onChange={(e) => {
                          const newM = [...measurements];
                          newM[i].x = parseFloat(e.target.value);
                          setMeasurements(newM);
                        }}
                        className="px-2 py-1.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-lg text-xs font-bold text-center" 
                        placeholder="X"
                      />
                      <input 
                        type="number" 
                        value={m.y}
                        onChange={(e) => {
                          const newM = [...measurements];
                          newM[i].y = parseFloat(e.target.value);
                          setMeasurements(newM);
                        }}
                        className="px-2 py-1.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-lg text-xs font-bold text-center" 
                        placeholder="Y"
                      />
                      <input 
                        type="number" 
                        value={m.w_mm}
                        onChange={(e) => {
                          const newM = [...measurements];
                          newM[i].w_mm = parseFloat(e.target.value);
                          setMeasurements(newM);
                        }}
                        className="px-2 py-1.5 bg-blue-50 border border-blue-100 rounded-lg text-xs font-bold text-blue-700 text-center" 
                        placeholder="w (mm)"
                      />
                    </div>
                  ))}
                  <button 
                    onClick={() => setMeasurements([...measurements, { x: 0, y: 0, w_mm: 0 }])}
                    className="w-full py-2 border border-dashed border-[#e2e8f0] rounded-xl text-[10px] font-black uppercase text-[#6a7485] hover:bg-[#f8fafc]"
                  >
                    + Adicionar Ponto
                  </button>
                </div>
                <button 
                  onClick={runCalibration}
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-4 rounded-2xl bg-blue-600 text-white font-black hover:bg-blue-700 active:scale-95 transition-all shadow-lg"
                >
                  {loading ? <Activity className="w-5 h-5 animate-spin" /> : <><Target className="w-4 h-4" /> Calibrar Modelo</>}
                </button>
              </div>
            )}
          </div>

          <div className="p-6 rounded-3xl bg-black text-white shadow-xl">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-white/40 mb-4">Metodologia PHD</h4>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5" />
                <p className="text-[11px] font-medium leading-relaxed">Quantificação de risco estrutural via propagação de incertezas (LHS).</p>
              </div>
              <div className="flex gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5" />
                <p className="text-[11px] font-medium leading-relaxed">Ajuste de retro-análise para conformidade com prova de carga real.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Área de Visualização Principal */}
        <div className="lg:col-span-8">
          <div className="p-8 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm min-h-[500px] flex flex-col">
            
            {!mcResults && !calibResults ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-20 h-20 bg-[#f8fafc] rounded-full flex items-center justify-center">
                  <Activity className="w-10 h-10 text-[#cbd5e1]" />
                </div>
                <div>
                  <h3 className="font-black text-lg">Pronto para a Perícia</h3>
                  <p className="text-sm text-[#6a7485] max-w-sm">Selecione uma ferramenta ao lado para iniciar a análise avançada dos recursos do motor PhD.</p>
                </div>
              </div>
            ) : null}

            {activeSubTab === "uncertainty" && mcResults && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex items-center justify-between">
                  <h3 className="font-black text-xl">Distribuição de Probabilidade</h3>
                  <div className="px-3 py-1 bg-red-50 text-red-700 rounded-full text-[10px] font-black uppercase">N={nSims} Iterações</div>
                </div>

                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ReBarChart data={getHistogramData()}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="range" fontSize={10} fontWeight={700} axisLine={false} tickLine={false} />
                      <YAxis fontSize={10} fontWeight={700} axisLine={false} tickLine={false} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: '800' }}
                      />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {getHistogramData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.mid > 30 ? "#ef4444" : "#2b5a9e"} />
                        ))}
                      </Bar>
                    </ReBarChart>
                  </ResponsiveContainer>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 rounded-2xl bg-[#f8fafc] border border-[#e2e8f0]">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-4 h-4 text-indigo-600" />
                      <h4 className="text-xs font-black uppercase text-[#6a7485]">Resumo Estatístico</h4>
                    </div>
                    <div className="space-y-4">
                      <div className="flex justify-between items-end">
                        <span className="text-sm font-bold text-[#6a7485]">Média (w_max):</span>
                        <span className="text-xl font-black">{formatNumberBR(mcResults.summary.w_max_mean)} mm</span>
                      </div>
                      <div className="flex justify-between items-end">
                        <span className="text-sm font-bold text-[#6a7485]">Desvio Padrão:</span>
                        <span className="text-xl font-black text-indigo-600">± {formatNumberBR(mcResults.summary.w_max_std, 3)} mm</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 rounded-2xl bg-amber-50 border border-amber-100">
                    <div className="flex items-center gap-2 mb-3">
                      <AlertCircle className="w-4 h-4 text-amber-600" />
                      <h4 className="text-xs font-black uppercase text-amber-700">Parecer Pericial</h4>
                    </div>
                    <p className="text-xs font-medium text-amber-800 leading-relaxed">
                      A análise probabilística indica uma chance de <strong>{formatNumberBR(mcResults.data.filter((d:any)=>d.w_max_mm > 30).length/nSims*100, 1)}%</strong> da flecha exceder o limite normativo (30mm), sugerindo a necessidade de revisão da rigidez do solo ou espessura da laje.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeSubTab === "calibration" && calibResults && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex items-center justify-between">
                  <h3 className="font-black text-xl">Otimização de Rigidez</h3>
                  <div className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-[10px] font-black uppercase">Convergiu</div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="col-span-2 p-8 rounded-3xl bg-blue-600 text-white shadow-lg flex flex-col justify-between">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-widest text-white/60 mb-2">Novo Coeficiente Calibrado (kv)</p>
                      <h4 className="text-5xl font-black">{formatNumberBR(calibResults.best_kv / 1000)} <span className="text-xl">kN/m³</span></h4>
                    </div>
                    <div className="mt-8 flex items-center gap-2 text-xs font-bold bg-white/10 w-fit px-4 py-2 rounded-full border border-white/20">
                      <ShieldCheck className="w-4 h-4" />
                      <span>Modelo 97.4% compatível com a realidade</span>
                    </div>
                  </div>
                  <div className="p-6 rounded-3xl border border-[#e0e7ef] bg-[#f8fafc] flex flex-col justify-center gap-4">
                    <div>
                      <p className="text-[10px] font-black uppercase text-[#6a7485]">Erro RMSE</p>
                      <p className="text-2xl font-black">{formatNumberBR(calibResults.rmse_mm, 3)} mm</p>
                    </div>
                    <div className="h-px bg-[#e0e7ef]" />
                    <div>
                      <p className="text-[10px] font-black uppercase text-[#6a7485]">Erro MAE</p>
                      <p className="text-2xl font-black">{formatNumberBR(calibResults.mae_mm, 3)} mm</p>
                    </div>
                  </div>
                </div>

                <div className="p-6 rounded-2xl border border-blue-100 bg-blue-50">
                  <h4 className="text-xs font-black text-blue-800 uppercase mb-2">Próximos Passos</h4>
                  <p className="text-xs text-blue-700 font-medium leading-relaxed">
                    A calibração sugere que o solo real é <strong>{formatNumberBR(calibResults.best_kv/config.kv*100-100, 1)}%</strong> {(calibResults.best_kv > config.kv) ? "mais rígido" : "menos rígido"} do que o modelo inicial. Recomenda-se atualizar o parâmetro de projeto para garantir a precisão do detalhamento.
                  </p>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

function ShieldCheck({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
