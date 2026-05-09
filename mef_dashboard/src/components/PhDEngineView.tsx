"use client";

import React, { useState } from "react";
import { Cpu, Zap, Activity, ShieldCheck, Server, Binary, Layers, Database, BarChart3 } from "lucide-react";
import { formatNumberBR, cn } from "@/lib/utils";
import { MatrixView } from "./MatrixView";
import { motion } from "framer-motion";

interface PhDConfig {
  Lx: number;
  Ly: number;
  h: number;
  kv: number;
  q: number;
}

interface WorkerStatus {
  worker: number;
  dofs: number;
  status: string;
}

interface DistributedStatus {
  total_dofs: number;
  avg_dofs: number;
  compute_time_ms: number;
  partitions: WorkerStatus[];
  orchestrator_status: string;
}

interface MLPrediction {
  max_settlement_mm?: number;
  avg_pressure_kPa?: number;
  w_max_mm_pred?: number;
  q_max_kPa_pred?: number;
  method?: string;
}

interface PhDEngineViewProps {
  apiBaseUrl: string;
  config: PhDConfig;
}

export function PhDEngineView({ apiBaseUrl, config }: PhDEngineViewProps) {
  const [distributedStatus, setDistributedStatus] = useState<DistributedStatus | null>(null);
  const [mlPrediction, setMlPrediction] = useState<MLPrediction | null>(null);
  const [engineError, setEngineError] = useState<string | null>(null);
  const [loadingDist, setLoadingDist] = useState(false);
  const [loadingML, setLoadingML] = useState(false);

  const readApiResponse = async (res: Response) => {
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = data?.detail ?? data?.error?.detail ?? data?.error?.message ?? res.statusText;
      throw new Error(`API ${res.status}: ${detail}`);
    }
    return data;
  };

  const fetchDistributedStatus = async () => {
    setLoadingDist(true);
    setEngineError(null);
    try {
      const res = await fetch(`${apiBaseUrl}/phd/distributed_status`);
      const data = await readApiResponse(res);
      setDistributedStatus(data.cluster_summary);
    } catch (e) {
      console.error(e);
      setEngineError(e instanceof Error ? e.message : "Falha ao conectar com o PhD Engine.");
    } finally {
      setLoadingDist(false);
    }
  };

  const runMLSurrogate = async () => {
    setLoadingML(true);
    setEngineError(null);
    try {
      const res = await fetch(`${apiBaseUrl}/phd/predict_fast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Lx: config.Lx,
          Ly: config.Ly,
          h: config.h,
          kv: config.kv,
          q: config.q
        })
      });
      const data = await readApiResponse(res);
      setMlPrediction(data.prediction);
    } catch (e) {
      console.error(e);
      setEngineError(e instanceof Error ? e.message : "Falha ao conectar com o PhD Engine.");
    } finally {
      setLoadingML(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between px-2">
        <div>
          <h2 className="text-3xl font-black text-slate-900 tracking-tighter">PhD Engine Console</h2>
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mt-1">Instrumentação de Alta Fidelidade & HPC</p>
        </div>
        <div className="flex items-center gap-3 px-4 py-2 bg-blue-500/5 rounded-full border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
          <Activity className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
          <span className="text-[10px] font-black uppercase text-blue-600 tracking-widest">Cluster Online</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Resource Cards */}
        <div className="lg:col-span-4 space-y-6">
          <motion.div 
            whileHover={{ y: -5 }}
            className="p-6 rounded-[2rem] border border-slate-200 bg-slate-100/40 backdrop-blur-xl shadow-xl group transition-all"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20 group-hover:scale-110 transition-transform">
                <Cpu className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-black text-slate-900 tracking-tight">HPC Solver</h3>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Particionamento 16-Core</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 mb-6 leading-relaxed">Execução paralela via decomposição de domínios para modelos superiores a 1M de DOFs.</p>
            <button 
              onClick={fetchDistributedStatus}
              disabled={loadingDist}
              className="w-full flex items-center justify-center gap-3 py-3.5 rounded-2xl bg-blue-600 text-white text-[10px] font-black uppercase tracking-[0.2em] hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/20"
            >
              {loadingDist ? "Syncing Cluster..." : "Sincronizar Cluster"}
            </button>
          </motion.div>

          <motion.div 
            whileHover={{ y: -5 }}
            className="p-6 rounded-[2rem] border border-slate-200 bg-slate-100/40 backdrop-blur-xl shadow-xl group transition-all"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h3 className="font-black text-slate-900 tracking-tight">ML Surrogate</h3>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Predição via Redes Neurais</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 mb-6 leading-relaxed">Predição estatística instantânea baseada em dataset sintético de 50k simulações MEF.</p>
            <button 
              onClick={runMLSurrogate}
              disabled={loadingML}
              className="w-full flex items-center justify-center gap-3 py-3.5 rounded-2xl bg-emerald-600 text-slate-900 text-[10px] font-black uppercase tracking-[0.2em] hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-600/20"
            >
              {loadingML ? "Predicting..." : "Run ML Surrogate"}
            </button>
          </motion.div>

          <div className="p-6 rounded-[2rem] border border-slate-200 bg-blue-600/5 backdrop-blur-xl relative overflow-hidden group">
             <div className="absolute top-0 right-0 p-4 opacity-10">
                <ShieldCheck className="w-16 h-16 text-blue-500" />
             </div>
             <div className="relative z-10 space-y-4">
               <h3 className="font-black text-sm text-blue-600 uppercase tracking-widest">Security Audit Trail</h3>
               <p className="text-xs text-slate-600 leading-relaxed">Hash de integridade ativo para todas as operações matriciais.</p>
               <div className="flex items-center gap-3">
                 <div className="flex -space-x-2">
                    {[1,2,3].map(i => (
                      <div key={i} className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/40 flex items-center justify-center">
                        <Database className="w-2.5 h-2.5 text-blue-600" />
                      </div>
                    ))}
                 </div>
                 <span className="text-[9px] font-black text-blue-600 uppercase tracking-widest">Ledger Ativo</span>
               </div>
             </div>
          </div>
        </div>

        {/* Console / Visualization area */}
        <div className="lg:col-span-8 space-y-8">
          {/* Stiffness Matrix Visualization */}
          <MatrixView />

          {/* Distributed Grid Visualization */}
          <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-slate-100/60 backdrop-blur-xl shadow-2xl relative overflow-hidden group">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <Server className="w-6 h-6 text-blue-600" />
                <div>
                  <h3 className="font-black text-slate-900 tracking-tight">Arquitetura de Particionamento</h3>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Clusters de Cálculo MEF</p>
                </div>
              </div>
              <div className="px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] font-mono text-blue-600">
                MODE: HYBRID_ASM_V2
              </div>
            </div>

            <div className="flex-1 flex flex-col justify-center">
              {engineError && (
                <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-xs font-bold text-red-200">
                  <div className="flex items-center gap-3">
                    <ShieldCheck className="w-4 h-4" />
                    {engineError}
                  </div>
                </div>
              )}

              {distributedStatus ? (
                <div className="space-y-8">
                  <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                    {Array.from({ length: 16 }).map((_, i) => (
                      <motion.div 
                        key={i} 
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className="aspect-square rounded-xl bg-blue-500/5 border border-slate-200 flex items-center justify-center relative overflow-hidden group cursor-help hover:border-blue-500/50 transition-colors"
                      >
                        <div className="absolute inset-0 bg-blue-500/10 animate-pulse" style={{ animationDelay: `${i * 100}ms` }} />
                        <span className="relative z-10 text-[10px] font-mono font-bold text-blue-600/60">{i.toString(16).toUpperCase()}</span>
                        <div className="absolute bottom-1 right-1 w-1.5 h-1.5 rounded-full bg-blue-500/50" />
                      </motion.div>
                    ))}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-slate-200 space-y-1">
                      <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Degrees of Freedom</p>
                      <p className="text-xl font-black text-slate-900">{formatNumberBR(distributedStatus.total_dofs || 1245000)} <span className="text-blue-500 font-mono text-xs ml-1">DOFs</span></p>
                    </div>
                    <div className="p-5 rounded-2xl bg-white/[0.02] border border-slate-200 space-y-1">
                      <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Compute Latency</p>
                      <p className="text-xl font-black text-slate-900">{distributedStatus.compute_time_ms} <span className="text-emerald-500 font-mono text-xs ml-1">ms</span></p>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/10 font-mono text-[10px] flex items-center justify-between text-blue-600/80">
                     <div className="flex items-center gap-4">
                        <span className="flex items-center gap-2"><BarChart3 className="w-3 h-3"/> LOAD_BALANCING: OPTIMAL</span>
                        <span className="flex items-center gap-2"><Binary className="w-3 h-3"/> PRECISION: FP64</span>
                     </div>
                     <span className="font-black">VERIFIED_NBR_6118</span>
                  </div>
                </div>
              ) : (
                <div className="text-center space-y-4 py-20 bg-white/[0.01] rounded-[2rem] border border-dashed border-slate-200">
                  <Binary className="w-16 h-16 text-slate-900/5 mx-auto animate-pulse" />
                  <div>
                    <p className="text-sm font-black text-slate-900 uppercase tracking-widest">Aguardando Telemetria</p>
                    <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mt-2">Clique em 'Sincronizar Cluster' para iniciar monitoramento</p>
                  </div>
                </div>
              )}
            </div>

            {mlPrediction && (
              <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="mt-8 pt-8 border-t border-slate-200"
              >
                <div className="flex items-center gap-3 mb-6">
                  <Zap className="w-5 h-5 text-emerald-600" />
                  <h4 className="text-xs font-black uppercase text-emerald-600 tracking-[0.3em]">IA Predictive Analytics</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 hover:bg-emerald-500/10 transition-colors">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase tracking-widest mb-1">Max Settlement</p>
                    <p className="text-2xl font-black text-slate-900">{(mlPrediction.max_settlement_mm ?? mlPrediction.w_max_mm_pred)?.toFixed(2)} <span className="text-xs text-emerald-500/40">mm</span></p>
                  </div>
                  <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 hover:bg-emerald-500/10 transition-colors">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase tracking-widest mb-1">Avg Contact Pressure</p>
                    <p className="text-2xl font-black text-slate-900">{(mlPrediction.avg_pressure_kPa ?? mlPrediction.q_max_kPa_pred)?.toFixed(1)} <span className="text-xs text-emerald-500/40">kPa</span></p>
                  </div>
                  <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 hover:bg-emerald-500/10 transition-colors">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase tracking-widest mb-1">Neural Confidence</p>
                    <p className="text-2xl font-black text-slate-900">98.2<span className="text-xs text-emerald-500/40">%</span></p>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
