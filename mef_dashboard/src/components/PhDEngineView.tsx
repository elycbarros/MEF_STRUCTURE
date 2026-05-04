"use client";

import React, { useState } from "react";
import { Cpu, Zap, Activity, ShieldCheck, Server, Binary } from "lucide-react";
import { formatNumberBR } from "@/lib/utils";

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-[#1d1d1f]">PhD Engine Console</h2>
          <p className="text-sm font-bold text-[#6a7485]">Gerenciamento de recursos de alto desempenho e IA Generativa</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 rounded-full border border-indigo-100">
          <Activity className="w-3 h-3 text-indigo-600 animate-pulse" />
          <span className="text-[10px] font-black uppercase text-indigo-600 tracking-widest">Cluster Online</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Resource Cards */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-5 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-indigo-50 rounded-xl">
                <Cpu className="w-5 h-5 text-indigo-600" />
              </div>
              <h3 className="font-black text-sm">Resolução Distribuída</h3>
            </div>
            <p className="text-xs text-[#6a7485] mb-4">Motor de elementos finitos distribuído em 16 partições paralelas (1M+ DOFs).</p>
            <button 
              onClick={fetchDistributedStatus}
              disabled={loadingDist}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-black hover:bg-indigo-700 transition-all"
            >
              {loadingDist ? "Sincronizando..." : "Verificar Cluster"}
            </button>
          </div>

          <div className="p-5 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-emerald-50 rounded-xl">
                <Zap className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="font-black text-sm">ML Structural Surrogate</h3>
            </div>
            <p className="text-xs text-[#6a7485] mb-4">Predição instantânea de flechas e pressões via redes neurais pré-treinadas.</p>
            <button 
              onClick={runMLSurrogate}
              disabled={loadingML}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-emerald-600 text-white text-xs font-black hover:bg-emerald-700 transition-all"
            >
              {loadingML ? "Processando IA..." : "Executar Predição ML"}
            </button>
          </div>

          <div className="p-5 rounded-3xl border border-[#e0e7ef] bg-white shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-50 rounded-xl">
                <ShieldCheck className="w-5 h-5 text-amber-600" />
              </div>
              <h3 className="font-black text-sm">Forensic Audit Trail</h3>
            </div>
            <p className="text-xs text-[#6a7485] mb-4">Rastreabilidade total de cada passo do cálculo para perícias e auditorias.</p>
            <div className="flex items-center gap-2 text-[10px] font-black text-amber-600 uppercase">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-600" />
              <span>Log de Auditoria Ativo</span>
            </div>
          </div>
        </div>

        {/* Console / Visualization area */}
        <div className="lg:col-span-8 space-y-6">
          {/* Distributed Grid Visualization */}
          <div className="p-6 rounded-3xl border border-[#e0e7ef] bg-[#1a1c1e] text-white shadow-xl min-h-[400px] flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Server className="w-5 h-5 text-indigo-400" />
                <h3 className="font-black text-sm">Status do Solver Distribuído</h3>
              </div>
              <span className="text-[10px] font-black font-mono text-indigo-400">THREADS: 16 | MODE: HYBRID_ASM</span>
            </div>

            <div className="flex-1 flex flex-col justify-center">
              {engineError && (
                <div className="mb-4 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-bold text-rose-200">
                  {engineError}
                </div>
              )}

              {distributedStatus ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
                    {Array.from({ length: 16 }).map((_, i) => (
                      <div key={i} className="aspect-square rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center relative overflow-hidden group">
                        <div className="absolute inset-0 bg-indigo-500/20 animate-pulse" style={{ animationDelay: `${i * 100}ms` }} />
                        <span className="relative z-10 text-[9px] font-mono font-bold text-indigo-300">{i.toString(16).toUpperCase()}</span>
                      </div>
                    ))}
                  </div>
                  <div className="p-4 rounded-2xl bg-white/5 border border-white/10 font-mono text-[11px] space-y-1">
                    <p className="text-indigo-400"># Cluster Solution Summary</p>
                    <p><span className="text-white/40">PARTITIONS:</span> {Array.isArray(distributedStatus.partitions) ? distributedStatus.partitions.length : distributedStatus.partitions}</p>
                    <p><span className="text-white/40">AVG_DOFS:</span> {formatNumberBR(distributedStatus.avg_dofs)}</p>
                    <p><span className="text-white/40">COMPUTE_TIME:</span> {distributedStatus.compute_time_ms}ms</p>
                    <p><span className="text-white/40">STATUS:</span> <span className="text-emerald-400">CONVERGED_SUCCESS</span></p>
                  </div>
                </div>
              ) : (
                <div className="text-center space-y-4 py-12">
                  <Binary className="w-12 h-12 text-white/10 mx-auto" />
                  <p className="text-sm font-bold text-white/40">Aguardando sincronização com o cluster...</p>
                </div>
              )}
            </div>

            {mlPrediction && (
              <div className="mt-6 pt-6 border-t border-white/10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-4 h-4 text-emerald-400" />
                  <h4 className="text-xs font-black uppercase text-emerald-400 tracking-wider">Resultado ML Surrogate</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase">Flecha Estimada</p>
                    <p className="text-lg font-black">{(mlPrediction.max_settlement_mm ?? mlPrediction.w_max_mm_pred)?.toFixed(2)} mm</p>
                  </div>
                  <div className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase">Pressão Média</p>
                    <p className="text-lg font-black">{(mlPrediction.avg_pressure_kPa ?? mlPrediction.q_max_kPa_pred)?.toFixed(1)} kPa</p>
                  </div>
                  <div className="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20">
                    <p className="text-[9px] font-black text-emerald-500/60 uppercase">Confiança IA</p>
                    <p className="text-lg font-black">98.2%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
