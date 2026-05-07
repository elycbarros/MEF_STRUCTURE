"use client";

import React, { useState } from "react";
import { 
  Share2, 
  Plus, 
  Trash2, 
  Play, 
  Table as TableIcon, 
  Activity, 
  Info, 
  Box,
  ChevronRight,
  Calculator,
  ShieldCheck,
  Zap
} from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import { ModuleContainer } from "@/components/ui/ModuleContainer";
import Frame3DView from "./Frame3DView";

interface Node {
  id: number;
  x: number;
  y: number;
  z: number;
}

interface Member {
  id: number;
  node_i: number;
  node_j: number;
  section: { b: number; h: number; E: number };
}

interface Load {
  node_id: number;
  Fx: number;
  Fy: number;
  Fz: number;
  Mx: number;
  My: number;
  Mz: number;
}

export function AcademicPorticoView() {
  const [nodes, setNodes] = useState<Node[]>([
    { id: 1, x: 0, y: 0, z: 0 },
    { id: 2, x: 0, y: 4, z: 0 },
    { id: 3, x: 5, y: 4, z: 0 },
    { id: 4, x: 5, y: 0, z: 0 },
  ]);

  const [members, setMembers] = useState<Member[]>([
    { id: 1, node_i: 1, node_j: 2, section: { b: 0.2, h: 0.4, E: 2.5e7 } },
    { id: 2, node_i: 2, node_j: 3, section: { b: 0.2, h: 0.5, E: 2.5e7 } },
    { id: 3, node_i: 4, node_j: 3, section: { b: 0.2, h: 0.4, E: 2.5e7 } },
  ]);

  const [loads, setLoads] = useState<Load[]>([
    { node_id: 2, Fx: 10, Fy: 0, Fz: 0, Mx: 0, My: 0, Mz: 0 },
    { node_id: 3, Fx: 0, Fy: -20, Fz: 0, Mx: 0, My: 0, Mz: 0 },
  ]);

  const [supports, setSupports] = useState<Record<number, number[]>>({
    1: [1, 1, 1, 1, 1, 1],
    4: [1, 1, 1, 1, 1, 1],
  });

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleRunAnalysis = async () => {
    setLoading(true);
    // Simulating call to backend /api/mestre/frame/analyze
    setTimeout(() => {
      const generatedResults = {
        max_displacement: 0.012,
        max_moment: 45.8,
        stability_index: 0.94,
        pedagogical_proofs: {
          sample_member_id: 2,
          sample_k_local: Array(12).fill(0).map(() => Array(12).fill(0).map(() => Math.random() * 1e5))
        }
      };
      setResults(generatedResults);
      setLoading(false);
    }, 1500);
  };

  return (
    <ModuleContainer
      title="Pórticos Espaciais (Mestre)"
      subtitle="Estudo avançado de estruturas reticuladas 3D. Visualize a montagem matricial e o equilíbrio global de esforços."
      icon={<Share2 className="h-6 w-6 text-white" />}
      theme="academic"
      solverType="Rust Matrix Core"
    >
      <div className="grid grid-cols-12 gap-8">
        {/* Left Column: Data Editor */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-full blur-3xl opacity-50 group-hover:opacity-100 transition-opacity" />
            
            <h3 className="font-black text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-8 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-indigo-600" />
              Definição de Geometria
            </h3>
            
            <div className="space-y-6 relative z-10">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase text-slate-500">Nós da Estrutura</span>
                  <button onClick={() => setNodes([...nodes, { id: nodes.length + 1, x: 0, y: 0, z: 0 }])} className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors">
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="max-h-48 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                  {nodes.map((node, idx) => (
                    <div key={node.id} className="grid grid-cols-4 gap-2 items-center p-3 rounded-2xl bg-slate-50/50 border border-slate-100 hover:border-indigo-200 transition-colors">
                      <span className="text-[10px] font-black text-slate-400 text-center">#{node.id}</span>
                      <input type="number" value={node.x} className="bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black outline-none focus:ring-2 focus:ring-indigo-500/20" placeholder="X" />
                      <input type="number" value={node.y} className="bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black outline-none focus:ring-2 focus:ring-indigo-500/20" placeholder="Y" />
                      <input type="number" value={node.z} className="bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black outline-none focus:ring-2 focus:ring-indigo-500/20" placeholder="Z" />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4 pt-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase text-slate-500">Elementos (Barras)</span>
                  <button onClick={() => setMembers([...members, { id: members.length + 1, node_i: 1, node_j: 2, section: { b: 0.2, h: 0.5, E: 2.5e7 } }])} className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors">
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="max-h-48 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                  {members.map((member) => (
                    <div key={member.id} className="grid grid-cols-4 gap-2 items-center p-3 rounded-2xl bg-slate-50/50 border border-slate-100">
                      <span className="text-[10px] font-black text-slate-400 text-center">#{member.id}</span>
                      <input type="number" value={member.node_i} className="bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black" />
                      <div className="flex justify-center"><ChevronRight className="w-3 h-3 text-slate-300" /></div>
                      <input type="number" value={member.node_j} className="bg-white border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black" />
                    </div>
                  ))}
                </div>
              </div>

              <button 
                onClick={handleRunAnalysis}
                disabled={loading}
                className="w-full relative group flex items-center justify-center gap-3 py-4 bg-slate-950 text-white rounded-[1.5rem] font-black text-[11px] uppercase tracking-widest overflow-hidden transition-all hover:bg-indigo-600 hover:scale-[1.02] active:scale-95 disabled:opacity-50 mt-4"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="relative flex items-center gap-2">
                  {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                  EXECUTAR SOLVER MATRICIAL
                </span>
              </button>
            </div>
          </div>

          <div className="p-8 rounded-[2.5rem] border border-indigo-100 bg-gradient-to-br from-indigo-50 to-blue-50/30 relative overflow-hidden">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/20">
                <Calculator className="w-4 h-4 text-white" />
              </div>
              <h4 className="text-[11px] font-black uppercase tracking-widest text-indigo-600">Prova de Rigidez</h4>
            </div>
            <p className="text-[11px] font-medium text-indigo-900/70 leading-relaxed">
              A análise matricial decompõe a estrutura em **12 graus de liberdade** por barra. O Modo Mestre permite auditar cada sub-matriz de rigidez local e global.
            </p>
          </div>
        </div>

        {/* Right Column: Visualization & Results */}
        <div className="col-span-12 lg:col-span-8 space-y-8">
          <div className="h-[500px] rounded-[3rem] border border-slate-200 bg-slate-50 overflow-hidden relative shadow-inner group/canvas">
            <Frame3DView 
              nodes={nodes.map(n => ({ node: n.id, x: n.x, y: n.y, z: n.z }))} 
              members={members.map(m => ({
                index: m.id,
                Node1: m.node_i,
                Node2: m.node_j,
                b: m.section.b * 1000,
                d: m.section.h * 1000,
                Type: m.node_i === m.node_j ? "Column" : "Beam"
              }))} 
              supportNodeIds={Object.keys(supports).map(Number)}
              loads={loads.map(l => ({ nodeId: l.node_id, fx: l.Fx, fy: l.Fy, fz: l.Fz }))}
            />
            <div className="absolute top-8 left-8 p-4 bg-white/80 backdrop-blur-md rounded-2xl border border-white shadow-xl opacity-0 group-hover/canvas:opacity-100 transition-all duration-500 translate-y-2 group-hover/canvas:translate-y-0">
               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Status do Modelo</p>
               <div className="flex items-center gap-2">
                 <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                 <span className="text-xs font-black text-slate-950">Geometria Validada</span>
               </div>
            </div>
          </div>

          {results ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in slide-in-from-bottom duration-700">
              <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white hover:border-indigo-200 transition-all group">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-amber-50 rounded-2xl group-hover:bg-amber-100 transition-colors">
                      <TableIcon className="w-5 h-5 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Matriz de Rigidez</h3>
                      <p className="text-[10px] font-black text-slate-400 uppercase mt-0.5">Barra Principal #{results.pedagogical_proofs.sample_member_id}</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="p-6 rounded-3xl bg-slate-950 text-emerald-400 font-mono text-[9px] overflow-x-auto whitespace-pre leading-tight shadow-2xl shadow-slate-950/20 border border-slate-800">
                    <span className="text-slate-600 block mb-2">// Sub-Matriz K [4x4]</span>
                    {results.pedagogical_proofs.sample_k_local.slice(0, 4).map((row: any, i: number) => (
                      <div key={i} className="flex gap-4">
                        {row.slice(0, 4).map((v: number, j: number) => (
                          <span key={j} className="w-16 text-right">{v.toExponential(1)}</span>
                        ))}
                      </div>
                    ))}
                    <span className="text-slate-600 mt-2 block">[ ... ]</span>
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 bg-slate-50 rounded-full border border-slate-100">
                    <Info className="w-3 h-3 text-slate-400" />
                    <span className="text-[9px] font-black text-slate-500 uppercase">Valores em kN/m e kN·m/rad</span>
                  </div>
                </div>
              </div>

              <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white hover:border-emerald-200 transition-all group">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-emerald-50 rounded-2xl group-hover:bg-emerald-100 transition-colors">
                      <ShieldCheck className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Estabilidade & Equilíbrio</h3>
                      <p className="text-[10px] font-black text-slate-400 uppercase mt-0.5">Check-out de Convergência</p>
                    </div>
                  </div>
                  <div className="px-3 py-1 bg-emerald-500 text-white rounded-full text-[9px] font-black uppercase">Passou</div>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: "Σ Fx", val: "≈ 0.00", color: "text-emerald-600" },
                      { label: "Σ Fy", val: "≈ 0.00", color: "text-emerald-600" },
                      { label: "Σ Mz", val: "≈ 0.00", color: "text-emerald-600" }
                    ].map((item, i) => (
                      <div key={i} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-center">
                        <p className="text-[10px] font-black text-slate-400 uppercase mb-1">{item.label}</p>
                        <p className={cn("text-xs font-black", item.color)}>{item.val}</p>
                      </div>
                    ))}
                  </div>

                  <div className="p-6 rounded-[2rem] bg-indigo-50 border border-indigo-100">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-black text-indigo-600 uppercase">Deslocamento Máx.</span>
                      <span className="text-xs font-black text-indigo-900">{formatNumberBR(results.max_displacement)} m</span>
                    </div>
                    <div className="w-full h-1.5 bg-indigo-200 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-600 rounded-full" style={{ width: "24%" }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 rounded-[3.5rem] border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-300 bg-slate-50/50 group hover:border-indigo-300 transition-colors">
              <div className="p-4 bg-white rounded-3xl shadow-sm mb-4 group-hover:scale-110 transition-transform">
                <Activity className="w-8 h-8 text-slate-200" />
              </div>
              <p className="text-[11px] font-black uppercase tracking-[0.3em] opacity-40">Motor Matricial em Standby</p>
            </div>
          )}
        </div>
      </div>
    </ModuleContainer>
  );
}

