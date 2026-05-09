import React from "react";
import { Plus, Trash2, Zap, Ruler, ShieldCheck, Activity, BookOpen } from "lucide-react";
import { motion } from "framer-motion";
import { formatNumberBR, cn, normalizeBeamDiagram } from "../utils";
import { BeamParams, Result } from "../types";
import { BeamLoadReactionChart } from "../components/BeamLoadReactionChart";
import { ElegantTooltip } from "../../ui/ElegantTooltip";
import EffortDiagrams from "../../EffortDiagrams";

interface BeamModuleProps {
  beamParams: BeamParams;
  setBeamParams: React.Dispatch<React.SetStateAction<BeamParams>>;
  result: Result | null;
  loading: boolean;
  calculate: () => void;
  useClassical: boolean;
  setUseClassical: (val: boolean) => void;
  setShowFullMemorial: (val: boolean) => void;
}

export function BeamModule({
  beamParams,
  setBeamParams,
  result,
  loading,
  calculate,
  useClassical,
  setUseClassical,
  setShowFullMemorial
}: BeamModuleProps) {
  const totalLength = (Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0) + (Number(beamParams.L_right) || 0);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Inputs Column */}
      <div className="space-y-6">
        <div className="space-y-3">
          <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria da viga</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Vão Central (L) [m]</label>
              <input type="number" step="0.1" value={beamParams.L} onChange={(e) => setBeamParams({ ...beamParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Largura (bw) [m]</label>
              <input type="number" step="0.01" value={beamParams.b} onChange={(e) => setBeamParams({ ...beamParams, b: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs font-bold text-[#667085]">Altura (h) [m]</label>
              <input type="number" step="0.01" value={beamParams.h} onChange={(e) => setBeamParams({ ...beamParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
            <div>
              <label className="text-xs font-bold text-[#667085]">Carga q [kN/m]</label>
              <input type="number" value={beamParams.q} onChange={(e) => setBeamParams({ ...beamParams, q: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Cargas Distribuídas</p>
            <button
              type="button"
              onClick={() => {
                const id = `QD${beamParams.distributedLoads.length + 1}`;
                setBeamParams({
                  ...beamParams,
                  distributedLoads: [...beamParams.distributedLoads, { id, x_start: 0, x_end: totalLength, q_start: 10, q_end: 10 }]
                });
              }}
              className="flex items-center gap-1 text-[10px] font-black text-blue-600 hover:text-blue-700"
            >
              <Plus size={12} /> ADICIONAR
            </button>
          </div>
          {beamParams.distributedLoads.length > 0 && (
            <div className="space-y-2">
              {beamParams.distributedLoads.map((dl, idx) => (
                <div key={dl.id} className="grid grid-cols-1 gap-2 p-3 rounded-xl border border-slate-100 bg-white">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[9px] font-bold text-[#667085]">Início [m]</label>
                      <input type="number" value={dl.x_start} onChange={(e) => {
                        const newList = [...beamParams.distributedLoads];
                        newList[idx].x_start = Number(e.target.value);
                        setBeamParams({ ...beamParams, distributedLoads: newList });
                      }} className="w-full p-1 border rounded text-xs" />
                    </div>
                    <div>
                      <label className="text-[9px] font-bold text-[#667085]">Fim [m]</label>
                      <input type="number" value={dl.x_end} onChange={(e) => {
                        const newList = [...beamParams.distributedLoads];
                        newList[idx].x_end = Number(e.target.value);
                        setBeamParams({ ...beamParams, distributedLoads: newList });
                      }} className="w-full p-1 border rounded text-xs" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[9px] font-bold text-[#667085]">q Início [kN/m]</label>
                      <input type="number" value={dl.q_start} onChange={(e) => {
                        const newList = [...beamParams.distributedLoads];
                        newList[idx].q_start = Number(e.target.value);
                        setBeamParams({ ...beamParams, distributedLoads: newList });
                      }} className="w-full p-1 border rounded text-xs" />
                    </div>
                    <div>
                      <label className="text-[9px] font-bold text-[#667085]">q Fim [kN/m]</label>
                      <input type="number" value={dl.q_end} onChange={(e) => {
                        const newList = [...beamParams.distributedLoads];
                        newList[idx].q_end = Number(e.target.value);
                        setBeamParams({ ...beamParams, distributedLoads: newList });
                      }} className="w-full p-1 border rounded text-xs" />
                    </div>
                  </div>
                  <button onClick={() => {
                    setBeamParams({ ...beamParams, distributedLoads: beamParams.distributedLoads.filter((_, i) => i !== idx) });
                  }} className="text-red-500 text-xs self-end">Remover</button>
                </div>
              ))}
            </div>
          )}
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
        <div className="flex items-center gap-4 mb-2">
          <button
            onClick={() => setUseClassical(true)}
            className={cn(
              "flex-1 rounded-xl py-3 text-xs font-black uppercase tracking-widest transition-all",
              useClassical ? "bg-slate-900 text-white shadow-lg" : "bg-white text-slate-400 border border-slate-200 hover:bg-slate-50"
            )}
          >
            Método Clássico
          </button>
          <button
            onClick={() => setUseClassical(false)}
            className={cn(
              "flex-1 rounded-xl py-3 text-xs font-black uppercase tracking-widest transition-all",
              !useClassical ? "bg-blue-600 text-white shadow-lg" : "bg-white text-slate-400 border border-slate-200 hover:bg-slate-50"
            )}
          >
            Motor MEF (Finitos)
          </button>
        </div>

        <BeamLoadReactionChart beamParams={beamParams} result={result || {}} useClassical={useClassical} />

        {result && (
          <div className="space-y-6">
             <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Summary Cards */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl bg-white p-5 border border-slate-100 shadow-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Esforços</p>
                    <Zap size={14} className="text-blue-400" />
                  </div>
                  <p className="text-2xl font-black text-blue-900 leading-none">
                    {formatNumberBR(result.summary?.max_moment_kNm || result.max_moment_kNm, 1)}
                    <span className="ml-1 text-xs font-bold text-blue-500 uppercase">kNm</span>
                  </p>
                  <p className="mt-1 text-[10px] font-bold text-blue-400">Momento Fletor Máx (ELU)</p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="rounded-2xl bg-white p-5 border border-slate-100 shadow-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Armadura (As)</p>
                    <ShieldCheck size={14} className="text-emerald-400" />
                  </div>
                  <p className="text-2xl font-black text-emerald-900 leading-none">
                    {formatNumberBR(result.design?.flexure_bottom?.As_cm2 || result.summary?.as_bottom_cm2, 2)}
                    <span className="ml-1 text-xs font-bold text-emerald-500 uppercase">cm²</span>
                  </p>
                  <p className="mt-1 text-[10px] font-bold text-emerald-400">Taxa de Aço Calculada</p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="rounded-2xl bg-white p-5 border border-slate-100 shadow-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Dutibilidade</p>
                    <Activity size={14} className="text-slate-400" />
                  </div>
                  <p className="text-2xl font-black text-slate-900 leading-none">
                    {formatNumberBR(result.design?.flexure_bottom?.x_d, 2)}
                  </p>
                  <p className="mt-1 text-[10px] font-bold text-slate-400">Domínio {result.design?.flexure_bottom?.domain || "2"}</p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="rounded-2xl bg-slate-900 p-5 border border-slate-800 shadow-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Equilíbrio</p>
                    <div className={cn("h-2 w-2 rounded-full", Math.abs(result.summary?.residual_kN ?? 0) < 0.1 ? "bg-emerald-400" : "bg-rose-400")} />
                  </div>
                  <p className="text-2xl font-black text-white leading-none">
                    {formatNumberBR(Math.abs(result.summary?.residual_kN ?? 0), 3)}
                    <span className="ml-1 text-xs font-bold text-slate-500 uppercase">kN</span>
                  </p>
                  <button onClick={() => setShowFullMemorial(true)} className="mt-2 text-[9px] font-black uppercase text-blue-400 hover:text-blue-300 transition-colors">
                    Ver Memorial PDF
                  </button>
                </motion.div>
             </div>

             <div className="rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm overflow-hidden">
                <EffortDiagrams 
                  data={normalizeBeamDiagram(useClassical ? result.classical_diagrams : result.diagrams)} 
                  title={`Diagramas de Esforços (${useClassical ? 'Clássico' : 'MEF'})`}
                />
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
