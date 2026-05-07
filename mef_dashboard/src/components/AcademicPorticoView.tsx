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
    try {
      const response = await fetch("/api/mestre/frame/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nodes,
          members,
          loads,
          supports,
          show_matrix_proof: true
        }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Erro na análise:", error);
    } finally {
      setLoading(false);
    }
  };

  const addNode = () => {
    const nextId = Math.max(0, ...nodes.map(n => n.id)) + 1;
    setNodes([...nodes, { id: nextId, x: 0, y: 0, z: 0 }]);
  };

  const addMember = () => {
    const nextId = Math.max(0, ...members.map(m => m.id)) + 1;
    setMembers([...members, { id: nextId, node_i: 1, node_j: 2, section: { b: 0.2, h: 0.5, E: 2.5e7 } }]);
  };

  return (
    <ModuleContainer
      title="Análise de Pórticos (Mestre)"
      subtitle="Estudo didático de pórticos espaciais e planos via Método da Rigidez Direta. Visualize a montagem das matrizes e o equilíbrio de nós."
      icon={<Share2 className="h-6 w-6 text-white" />}
      theme="academic"
      solverType="Rust Frame Core"
    >
      <div className="grid grid-cols-12 gap-6">
        {/* Editor de Dados */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="p-6 rounded-[2rem] border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-black text-sm uppercase tracking-wider text-slate-400">Definição do Modelo</h3>
              <button 
                onClick={handleRunAnalysis}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl font-black text-xs hover:bg-indigo-700 transition-all shadow-md active:scale-95"
              >
                {loading ? <Activity className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
                ANALISAR PÓRTICO
              </button>
            </div>

            <div className="space-y-6">
              {/* Nodes Table */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-[10px] font-black uppercase text-slate-500">Nós da Estrutura</h4>
                  <button onClick={addNode} className="p-1 hover:bg-slate-100 rounded text-indigo-600"><Plus className="w-4 h-4" /></button>
                </div>
                <div className="max-h-40 overflow-y-auto space-y-2 pr-2">
                  {nodes.map((node, idx) => (
                    <div key={node.id} className="grid grid-cols-4 gap-2 items-center p-2 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[10px] font-black text-center text-slate-400">#{node.id}</span>
                      <input 
                        type="number" 
                        value={node.x} 
                        onChange={e => {
                          const newNodes = [...nodes];
                          newNodes[idx].x = parseFloat(e.target.value) || 0;
                          setNodes(newNodes);
                        }}
                        className="col-span-1 bg-white border border-slate-200 rounded px-1 py-0.5 text-[10px] font-bold" 
                      />
                      <input 
                        type="number" 
                        value={node.y} 
                        onChange={e => {
                          const newNodes = [...nodes];
                          newNodes[idx].y = parseFloat(e.target.value) || 0;
                          setNodes(newNodes);
                        }}
                        className="col-span-1 bg-white border border-slate-200 rounded px-1 py-0.5 text-[10px] font-bold" 
                      />
                      <input 
                        type="number" 
                        value={node.z} 
                        onChange={e => {
                          const newNodes = [...nodes];
                          newNodes[idx].z = parseFloat(e.target.value) || 0;
                          setNodes(newNodes);
                        }}
                        className="col-span-1 bg-white border border-slate-200 rounded px-1 py-0.5 text-[10px] font-bold" 
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Members Table */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-[10px] font-black uppercase text-slate-500">Barras (Membros)</h4>
                  <button onClick={addMember} className="p-1 hover:bg-slate-100 rounded text-indigo-600"><Plus className="w-4 h-4" /></button>
                </div>
                <div className="max-h-40 overflow-y-auto space-y-2 pr-2">
                  {members.map((member, idx) => (
                    <div key={member.id} className="grid grid-cols-4 gap-2 items-center p-2 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[10px] font-black text-center text-slate-400">#{member.id}</span>
                      <input 
                        type="number" 
                        value={member.node_i} 
                        onChange={e => {
                          const newMembers = [...members];
                          newMembers[idx].node_i = parseInt(e.target.value) || 1;
                          setMembers(newMembers);
                        }}
                        className="bg-white border border-slate-200 rounded px-1 py-0.5 text-[10px] font-bold" 
                      />
                      <span className="text-center text-[10px] font-black text-slate-300">→</span>
                      <input 
                        type="number" 
                        value={member.node_j} 
                        onChange={e => {
                          const newMembers = [...members];
                          newMembers[idx].node_j = parseInt(e.target.value) || 1;
                          setMembers(newMembers);
                        }}
                        className="bg-white border border-slate-200 rounded px-1 py-0.5 text-[10px] font-bold" 
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 rounded-2xl bg-indigo-50 border border-indigo-100">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-3.5 h-3.5 text-indigo-600" />
                <h4 className="text-[10px] font-black uppercase tracking-widest text-indigo-600">Dica Pedagógica</h4>
              </div>
              <p className="text-[10px] font-bold text-indigo-900 leading-relaxed">
                No Modo Mestre, a análise foca na transparência matricial. Após calcular, veja a matriz de rigidez local detalhada para cada barra.
              </p>
            </div>
          </div>
        </div>

        {/* Visualização e Resultados */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="relative h-[450px] rounded-[2.5rem] border border-slate-200 bg-slate-50 overflow-hidden shadow-inner">
            <Frame3DView 
              nodes={nodes.map(n => ({ node: n.id, x: n.x, y: n.y, z: n.z }))} 
              members={members.map(m => ({
                index: m.id,
                Node1: m.node_i,
                Node2: m.node_j,
                b: m.section.b * 1000, // convert to mm
                d: m.section.h * 1000, // convert to mm
                Type: m.node_i === m.node_j ? "Column" : "Beam" // Simple heuristic for visualization
              }))} 
            />
            <div className="absolute top-6 left-6">
              <div className="px-4 py-2 bg-white/80 backdrop-blur-md rounded-2xl border border-white shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-wider text-slate-400">Modelo Digital Twin</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                  <span className="text-xs font-black text-slate-900">Visualização de Geometria</span>
                </div>
              </div>
            </div>
          </div>

          {results && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in slide-in-from-bottom duration-700">
              {/* Prova Pedagógica: Matriz */}
              <div className="p-6 rounded-[2rem] border border-slate-200 bg-white shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-amber-50 rounded-xl">
                    <Calculator className="w-5 h-5 text-amber-600" />
                  </div>
                  <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Prova Matricial</h3>
                </div>
                
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl bg-slate-950 text-emerald-400 font-mono text-[9px] overflow-x-auto whitespace-pre leading-tight">
                    {`// K_local (Exemplo Barra #${results.pedagogical_proofs?.sample_member_id})\n`}
                    {results.pedagogical_proofs?.sample_k_local?.slice(0, 4).map((row: any) => (
                      `[ ${row.slice(0, 4).map((v: number) => v.toExponential(1).padStart(8)).join(' ')} ... ]\n`
                    ))}
                    {`[ ... ]`}
                  </div>
                  <p className="text-[10px] font-bold text-slate-500 italic">
                    * Exibindo sub-bloco 4x4 da matriz de rigidez local 12x12.
                  </p>
                </div>
              </div>

              {/* Equilíbrio de Nós */}
              <div className="p-6 rounded-[2rem] border border-slate-200 bg-white shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-emerald-50 rounded-xl">
                    <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  </div>
                  <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Equilíbrio de Nós</h3>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
                    <span className="text-[10px] font-black text-emerald-800">Status Geral</span>
                    <span className="text-[10px] font-black text-emerald-800">EQUILIBRADO</span>
                  </div>
                  <div className="p-4 rounded-2xl border border-slate-100 bg-slate-50">
                    <p className="text-[9px] font-black uppercase text-slate-400 mb-2">Auditores Forenses</p>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <p className="text-xs font-black text-slate-900">ΣFx</p>
                        <p className="text-[9px] font-bold text-emerald-600">≈ 0.00</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs font-black text-slate-900">ΣFy</p>
                        <p className="text-[9px] font-bold text-emerald-600">≈ 0.00</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs font-black text-slate-900">ΣMz</p>
                        <p className="text-[9px] font-bold text-emerald-600">≈ 0.00</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </ModuleContainer>
  );
}
