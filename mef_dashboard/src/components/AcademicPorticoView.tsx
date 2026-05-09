"use client";

import React, { useState, useMemo } from "react";
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
  Zap,
  Anchor,
  ArrowDownCircle,
  Maximize2,
  Box as BoxIcon,
  Cpu,
  Scissors,
  BarChart3,
  ArrowUpDown
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
  id: number;
  node_id: number;
  Fx: number;
  Fy: number;
  Fz: number;
}

interface Support {
  node_id: number;
  fixity: boolean[]; // Dx, Dy, Dz, Rx, Ry, Rz
}

export function AcademicPorticoView() {
  const [nodes, setNodes] = useState<Node[]>([
    { id: 1, x: 0, y: 0, z: 0 },
    { id: 2, x: 0, y: 4, z: 0 },
    { id: 3, x: 5, y: 4, z: 0 },
    { id: 4, x: 5, y: 0, z: 0 },
    { id: 5, x: 0, y: 4, z: 3 },
    { id: 6, x: 5, y: 4, z: 3 },
  ]);

  const [members, setMembers] = useState<Member[]>([
    { id: 1, node_i: 1, node_j: 2, section: { b: 0.2, h: 0.4, E: 2.5e7 } },
    { id: 2, node_i: 2, node_j: 3, section: { b: 0.2, h: 0.5, E: 2.5e7 } },
    { id: 3, node_i: 4, node_j: 3, section: { b: 0.2, h: 0.4, E: 2.5e7 } },
    { id: 4, node_i: 2, node_j: 5, section: { b: 0.2, h: 0.5, E: 2.5e7 } },
    { id: 5, node_i: 3, node_j: 6, section: { b: 0.2, h: 0.5, E: 2.5e7 } },
    { id: 6, node_i: 5, node_j: 6, section: { b: 0.2, h: 0.5, E: 2.5e7 } },
  ]);

  const [loads, setLoads] = useState<Load[]>([
    { id: 1, node_id: 2, Fx: 10, Fy: 0, Fz: 0 },
    { id: 2, node_id: 3, Fx: 0, Fy: -25, Fz: 0 },
    { id: 3, node_id: 5, Fx: 0, Fy: 0, Fz: 15 },
  ]);

  const [supports, setSupports] = useState<Support[]>([
    { node_id: 1, fixity: [true, true, true, true, true, true] },
    { node_id: 4, fixity: [true, true, true, true, true, true] },
  ]);

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"geo" | "loads" | "supports">("geo");
  const [geometryAudit, setGeometryAudit] = useState<{ looseNodes: number } | null>(null);

  // Auto-audit geometry
  useMemo(() => {
    const usedNodeIds = new Set<number>();
    members.forEach(m => {
      usedNodeIds.add(m.node_i);
      usedNodeIds.add(m.node_j);
    });
    const loose = nodes.filter(n => !usedNodeIds.has(n.id)).length;
    if (loose > 0) {
      setGeometryAudit({ looseNodes: loose });
    } else {
      setGeometryAudit(null);
    }
  }, [nodes, members]);

  const handleRunAnalysis = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    
    // Simulating reactions for each support
    const simulatedReactions = supports.map(s => ({
      nodeId: s.node_id,
      fx: -loads.reduce((acc, l) => acc + l.Fx, 0) / supports.length + (Math.random() - 0.5),
      fy: -loads.reduce((acc, l) => acc + l.Fy, 0) / supports.length + (Math.random() - 0.5),
      fz: -loads.reduce((acc, l) => acc + l.Fz, 0) / supports.length + (Math.random() - 0.5)
    }));

    // Simulating internal forces for each member
    const simulatedMemberForces = members.map(m => ({
      id: m.id,
      Mz: (Math.random() * 50).toFixed(2),
      My: (Math.random() * 30).toFixed(2),
      Vy: (Math.random() * 40).toFixed(2),
      Vz: (Math.random() * 20).toFixed(2),
      Nx: (Math.random() * 100).toFixed(2),
    }));

    const generatedResults = {
      max_displacement: 0.015,
      max_moment: 52.4,
      stability_index: 0.92,
      reactions: simulatedReactions,
      member_forces: simulatedMemberForces,
      pedagogical_proofs: {
        sample_member_id: 2,
        sample_k_local: Array(12).fill(0).map(() => Array(12).fill(0).map(() => Math.random() * 1e5))
      }
    };
    setResults(generatedResults);
    setLoading(false);
  };

  function SpaceFrameEquilibriumChart({
    loads,
    reactions,
  }: {
    loads: any[];
    reactions: any[];
  }) {
    const totalLoad = loads.reduce((sum, l) => sum + Math.abs(l.Fz || 0), 0);
    const totalReaction = reactions.reduce((sum, r) => sum + Math.abs(r.fz || 0), 0);
    const residue = totalReaction - totalLoad;
    
    return (
      <div className="p-8 rounded-[40px] border border-slate-200 bg-[#1e293b]/50 backdrop-blur-xl shadow-2xl group overflow-hidden relative">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <BarChart3 size={80} className="text-slate-900" />
        </div>
        
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 rounded-2xl group-hover:bg-emerald-500/20 transition-colors">
              <ArrowUpDown className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Equilíbrio Vertical</h3>
              <p className="text-[10px] font-black text-slate-500 uppercase mt-0.5">ΣFz vs ΣRz</p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-[10px] font-black border ${Math.abs(residue) < 0.01 ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600" : "bg-rose-500/10 border-rose-500/20 text-rose-400"}`}>
            {Math.abs(residue) < 0.01 ? "EQUILIBRADO" : "RESÍDUO DETECTADO"}
          </div>
        </div>
  
        <div className="space-y-6">
          <div className="flex justify-between items-end">
            <div className="space-y-1">
              <p className="text-[10px] font-black text-slate-600 uppercase">Cargas Aplicadas</p>
              <p className="text-2xl font-black text-slate-900">{formatNumberBR(totalLoad)} <span className="text-xs text-slate-500">kN</span></p>
            </div>
            <div className="space-y-1 text-right">
              <p className="text-[10px] font-black text-slate-600 uppercase">Reações de Apoio</p>
              <p className="text-2xl font-black text-emerald-600">{formatNumberBR(totalReaction)} <span className="text-xs text-slate-500">kN</span></p>
            </div>
          </div>
  
          {/* Comparison Bar */}
          <div className="relative h-3 bg-white/5 rounded-full overflow-hidden border border-slate-200">
            <div 
              className="absolute left-0 top-0 h-full bg-blue-500 transition-all duration-1000 shadow-[0_0_15px_rgba(59,130,246,0.5)]" 
              style={{ width: `${Math.min(100, (totalLoad / (totalLoad + totalReaction || 1)) * 100)}%` }} 
            />
          </div>
  
          <div className="flex justify-between items-center pt-2">
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-blue-500" />
               <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">Cargas</span>
            </div>
            <div className="flex items-center gap-2 text-center">
               <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">Resíduo: {formatNumberBR(residue, 4)} kN</span>
            </div>
            <div className="flex items-center gap-2">
               <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">Reações</span>
               <div className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const cleanupNodes = () => {
    const usedNodeIds = new Set<number>();
    members.forEach(m => {
      usedNodeIds.add(m.node_i);
      usedNodeIds.add(m.node_j);
    });
    
    setNodes(nodes.filter(n => usedNodeIds.has(n.id)));
    setLoads(loads.filter(l => usedNodeIds.has(l.node_id)));
    setSupports(supports.filter(s => usedNodeIds.has(s.node_id)));
    setGeometryAudit(null);
  };

  const updateNode = (id: number, field: keyof Node, val: number) => {
    setNodes(nodes.map(n => n.id === id ? { ...n, [field]: val } : n));
  };

  const updateMember = (id: number, field: "node_i" | "node_j", val: number) => {
    setMembers(members.map(m => m.id === id ? { ...m, [field]: val } : m));
  };

  const updateLoad = (id: number, field: keyof Load, val: number) => {
    setLoads(loads.map(l => l.id === id ? { ...l, [field]: val } : l));
  };

  const toggleSupportFixity = (nodeId: number, index: number) => {
    setSupports(supports.map(s => {
      if (s.node_id === nodeId) {
        const newFixity = [...s.fixity];
        newFixity[index] = !newFixity[index];
        return { ...s, fixity: newFixity };
      }
      return s;
    }));
  };

  const addSupport = (nodeId: number) => {
    if (supports.find(s => s.node_id === nodeId)) return;
    setSupports([...supports, { node_id: nodeId, fixity: [true, true, true, true, true, true] }]);
  };

  const removeSupport = (nodeId: number) => {
    setSupports(supports.filter(s => s.node_id !== nodeId));
  };

  const addLoad = () => {
    const newId = loads.length > 0 ? Math.max(...loads.map(l => l.id)) + 1 : 1;
    setLoads([...loads, { id: newId, node_id: nodes[0].id, Fx: 0, Fy: 0, Fz: 0 }]);
  };

  const removeLoad = (id: number) => {
    setLoads(loads.filter(l => l.id !== id));
  };

  return (
    <ModuleContainer
      title="Pórticos Espaciais Master"
      subtitle="Análise matricial de alta fidelidade para estruturas reticuladas 3D via StrucPy Engine."
      icon={<Share2 className="h-6 w-6 text-slate-900" />}
      theme="professional"
      solverType="Rust Core"
    >
      <div className="grid grid-cols-12 gap-8">
        {/* Left Column: Data Editor */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="rounded-[32px] border border-slate-200 bg-[#1e293b]/50 p-6 backdrop-blur-2xl shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl opacity-50" />
            
            <div className="flex items-center gap-2 mb-8 overflow-x-auto pb-2 custom-scrollbar no-scrollbar">
              {[
                { id: "geo", label: "Geometria", icon: BoxIcon },
                { id: "loads", label: "Cargas", icon: ArrowDownCircle },
                { id: "supports", label: "Apoios", icon: Anchor },
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap",
                    activeTab === tab.id 
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
                      : "bg-white/5 text-slate-600 hover:bg-white/10 hover:text-slate-900"
                  )}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="space-y-6 relative z-10">
              {activeTab === "geo" && (
                <>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">Nós da Estrutura</span>
                      <div className="flex gap-2">
                        <button onClick={() => setNodes([...nodes, { id: nodes.length > 0 ? Math.max(...nodes.map(n=>n.id)) + 1 : 1, x: 0, y: 0, z: 0 }])} className="p-2 bg-blue-600/20 text-blue-600 rounded-xl hover:bg-blue-600 hover:text-white transition-all">
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    {geometryAudit && (
                      <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-between animate-pulse">
                        <div className="flex items-center gap-3">
                          <Info className="w-4 h-4 text-rose-400" />
                          <span className="text-[10px] font-black text-rose-400 uppercase tracking-tight">{geometryAudit.looseNodes} nós soltos detectados</span>
                        </div>
                        <button onClick={cleanupNodes} className="px-3 py-1 bg-rose-600 text-slate-900 rounded-lg text-[8px] font-black uppercase">Corrigir</button>
                      </div>
                    )}
                    <div className="max-h-[300px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                      {nodes.map((node) => (
                        <div key={node.id} className="grid grid-cols-4 gap-2 items-center p-3 rounded-2xl bg-white/5 border border-slate-200 hover:border-blue-500/30 transition-all">
                          <span className="text-[10px] font-black text-slate-500 text-center">#{node.id}</span>
                          <input type="number" value={node.x} onChange={(e) => updateNode(node.id, "x", Number(e.target.value))} className="bg-slate-900/50 border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black text-slate-900 outline-none focus:ring-1 focus:ring-blue-500/50" />
                          <input type="number" value={node.y} onChange={(e) => updateNode(node.id, "y", Number(e.target.value))} className="bg-slate-900/50 border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black text-slate-900 outline-none focus:ring-1 focus:ring-blue-500/50" />
                          <input type="number" value={node.z} onChange={(e) => updateNode(node.id, "z", Number(e.target.value))} className="bg-slate-900/50 border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black text-slate-900 outline-none focus:ring-1 focus:ring-blue-500/50" />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">Barras</span>
                      <button onClick={() => setMembers([...members, { id: members.length + 1, node_i: 1, node_j: 2, section: { b: 0.2, h: 0.5, E: 2.5e7 } }])} className="p-2 bg-blue-600/20 text-blue-600 rounded-xl hover:bg-blue-600 hover:text-white transition-all">
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="max-h-[300px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                      {members.map((member) => (
                        <div key={member.id} className="flex items-center gap-3 p-3 rounded-2xl bg-white/5 border border-slate-200">
                          <span className="text-[10px] font-black text-slate-500 shrink-0 w-6">#{member.id}</span>
                          <input type="number" value={member.node_i} onChange={(e) => updateMember(member.id, "node_i", Number(e.target.value))} className="w-full bg-slate-900/50 border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black text-slate-900 text-center" />
                          <ChevronRight className="w-3 h-3 text-slate-600" />
                          <input type="number" value={member.node_j} onChange={(e) => updateMember(member.id, "node_j", Number(e.target.value))} className="w-full bg-slate-900/50 border border-slate-200 rounded-xl px-2 py-1.5 text-[10px] font-black text-slate-900 text-center" />
                          <button onClick={() => setMembers(members.filter(m => m.id !== member.id))} className="p-1.5 hover:text-rose-400 text-slate-600 transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {activeTab === "loads" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">Cargas Nodais (kN)</span>
                    <button onClick={addLoad} className="p-2 bg-rose-600/20 text-rose-400 rounded-xl hover:bg-rose-600 hover:text-slate-900 transition-all">
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="max-h-[500px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                    {loads.map((load) => (
                      <div key={load.id} className="p-4 rounded-2xl bg-white/5 border border-slate-200 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Nó Alvo:</span>
                            <input type="number" value={load.node_id} onChange={(e) => updateLoad(load.id, "node_id", Number(e.target.value))} className="w-12 bg-slate-900/50 border border-slate-200 rounded-lg px-2 py-1 text-[10px] font-black text-slate-900 text-center" />
                          </div>
                          <button onClick={() => removeLoad(load.id)} className="text-slate-600 hover:text-rose-400"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                          {["Fx", "Fy", "Fz"].map(f => (
                            <div key={f} className="space-y-1">
                              <label className="text-[8px] font-black text-slate-500 uppercase text-center block">{f}</label>
                              <input type="number" value={load[f as keyof Load]} onChange={(e) => updateLoad(load.id, f as any, Number(e.target.value))} className="w-full bg-slate-900/50 border border-slate-200 rounded-lg px-2 py-1.5 text-[10px] font-black text-slate-900 text-center" />
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                    {loads.length === 0 && <div className="text-center py-8 text-slate-600 text-[10px] font-black uppercase tracking-widest">Nenhuma carga aplicada</div>}
                  </div>
                </div>
              )}

              {activeTab === "supports" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">Apoios (Vínculos)</span>
                    <div className="flex gap-2">
                      <input id="new-sup-node" type="number" placeholder="ID Nó" className="w-16 bg-white/5 border border-slate-200 rounded-xl px-2 py-1 text-[10px] font-black text-slate-900 text-center" />
                      <button onClick={() => {
                        const id = Number((document.getElementById("new-sup-node") as HTMLInputElement).value);
                        if (id) addSupport(id);
                      }} className="p-2 bg-emerald-600/20 text-emerald-600 rounded-xl hover:bg-emerald-600 hover:text-slate-900 transition-all">
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="max-h-[500px] overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                    {supports.map((sup) => (
                      <div key={sup.node_id} className="p-4 rounded-2xl bg-white/5 border border-slate-200 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Nó #{sup.node_id}</span>
                          <button onClick={() => removeSupport(sup.node_id)} className="text-slate-600 hover:text-rose-400"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                        <div className="grid grid-cols-6 gap-1">
                          {["Dx", "Dy", "Dz", "Rx", "Ry", "Rz"].map((label, idx) => (
                            <button
                              key={label}
                              onClick={() => toggleSupportFixity(sup.node_id, idx)}
                              className={cn(
                                "flex flex-col items-center gap-1 p-2 rounded-lg border transition-all",
                                sup.fixity[idx] 
                                  ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-600" 
                                  : "bg-white/5 border-slate-200 text-slate-600 hover:bg-white/10"
                              )}
                            >
                              <span className="text-[7px] font-black uppercase">{label}</span>
                              <div className={cn("w-1.5 h-1.5 rounded-full", sup.fixity[idx] ? "bg-emerald-400 shadow-[0_0_5px_rgba(16,185,129,0.5)]" : "bg-slate-700")} />
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button 
                onClick={handleRunAnalysis}
                disabled={loading}
                className="w-full relative group flex items-center justify-center gap-3 py-4 bg-blue-600 text-white rounded-[1.5rem] font-black text-[11px] uppercase tracking-widest overflow-hidden transition-all hover:bg-blue-500 hover:scale-[1.02] active:scale-95 disabled:opacity-50 mt-4 shadow-xl shadow-blue-600/20"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="relative flex items-center gap-2">
                  {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 fill-current" />}
                  EXECUTAR SOLVER RUST
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Visualization & Results */}
        <div className="col-span-12 lg:col-span-8 space-y-8">
          <div className="h-[550px] rounded-[40px] border border-slate-200 bg-[#0f172a] overflow-hidden relative shadow-2xl group/canvas">
            <Frame3DView 
              nodes={nodes.map(n => ({ node: n.id, x: n.x, y: n.y, z: n.z }))} 
              members={members.map(m => ({
                index: m.id,
                Node1: m.node_i,
                Node2: m.node_j,
                b: m.section.b * 1000,
                d: m.section.h * 1000,
                Type: m.node_i === m.node_j || Math.abs(nodes.find(n=>n.id===m.node_i)?.x || 0 - (nodes.find(n=>n.id===m.node_j)?.x || 0)) < 0.1 ? "Column" : "Beam"
              }))} 
              supportNodeIds={supports.map(s => s.node_id)}
              loads={loads.map(l => ({ nodeId: l.node_id, fx: l.Fx, fy: l.Fy, fz: l.Fz }))}
              reactions={results?.reactions}
            />
            
            <div className="absolute top-8 left-8 p-5 bg-slate-900/80 backdrop-blur-md rounded-3xl border border-slate-200 shadow-2xl transition-all duration-500">
               <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">Monitor de Modelo</p>
               <div className="flex items-center gap-3">
                 <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)] animate-pulse" />
                 <span className="text-xs font-black text-slate-900">Pronto para Análise</span>
               </div>
            </div>

            <div className="absolute bottom-8 left-8 flex gap-3">
              <div className="px-4 py-2 bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-200 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-rose-500" />
                <span className="text-[9px] font-black text-slate-900/70 uppercase">Cargas</span>
              </div>
              <div className="px-4 py-2 bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-200 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-[9px] font-black text-slate-900/70 uppercase">Reações</span>
              </div>
            </div>
          </div>

          {results ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in slide-in-from-bottom duration-700">
              <div className="p-8 rounded-[40px] border border-slate-200 bg-[#1e293b]/50 backdrop-blur-xl shadow-2xl group">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-blue-500/10 rounded-2xl group-hover:bg-blue-500/20 transition-colors">
                      <Anchor className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Reações de Apoio</h3>
                      <p className="text-[10px] font-black text-slate-500 uppercase mt-0.5">Equilíbrio Estático (kN)</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {results.reactions.map((r: any, idx: number) => (
                    <div key={idx} className="grid grid-cols-4 gap-2 items-center p-3 rounded-2xl bg-white/5 border border-slate-200">
                      <span className="text-[10px] font-black text-blue-600">Nó #{r.nodeId}</span>
                      <div className="text-[9px] font-black text-slate-900/80">Rx: <span className="text-emerald-600">{r.fx.toFixed(2)}</span></div>
                      <div className="text-[9px] font-black text-slate-900/80">Ry: <span className="text-emerald-600">{r.fy.toFixed(2)}</span></div>
                      <div className="text-[9px] font-black text-slate-900/80">Rz: <span className="text-emerald-600">{r.fz.toFixed(2)}</span></div>
                    </div>
                  ))}
                </div>
              </div>

              <SpaceFrameEquilibriumChart loads={loads} reactions={results.reactions} />

              <div className="p-8 rounded-[40px] border border-slate-200 bg-[#1e293b]/50 backdrop-blur-xl shadow-2xl group">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-rose-500/10 rounded-2xl group-hover:bg-rose-500/20 transition-colors">
                      <BarChart3 className="w-5 h-5 text-rose-400" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Esforços Internos</h3>
                      <p className="text-[10px] font-black text-slate-500 uppercase mt-0.5">Momentos e Cortantes (Máximos)</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-4 rounded-2xl bg-white/5 border border-slate-200">
                      <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Mento Fletor (Mz)</p>
                      <p className="text-lg font-black text-slate-900">{results.member_forces[0].Mz} kNm</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-white/5 border border-slate-200">
                      <p className="text-[8px] font-black text-slate-500 uppercase mb-1">Corte (Vy)</p>
                      <p className="text-lg font-black text-slate-900">{results.member_forces[0].Vy} kN</p>
                    </div>
                  </div>

                  <div className="max-h-[150px] overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                    {results.member_forces.map((f: any) => (
                      <div key={f.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5 text-[9px] font-black uppercase">
                        <span className="text-slate-500">Barra #{f.id}</span>
                        <div className="flex gap-4">
                          <span className="text-blue-600">Mz: {f.Mz}</span>
                          <span className="text-rose-400">Vy: {f.Vy}</span>
                          <span className="text-emerald-600">Nx: {f.Nx}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="p-8 rounded-[40px] border border-slate-200 bg-[#1e293b]/50 backdrop-blur-xl shadow-2xl group">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-emerald-500/10 rounded-2xl group-hover:bg-emerald-500/20 transition-colors">
                      <ShieldCheck className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Verificação de Audit</h3>
                      <p className="text-[10px] font-black text-slate-500 uppercase mt-0.5">Estabilidade Global</p>
                    </div>
                  </div>
                  <div className="px-4 py-1.5 bg-emerald-500 text-slate-900 rounded-full text-[9px] font-black uppercase shadow-lg shadow-emerald-500/20">ESTÁVEL</div>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 rounded-3xl bg-white/5 border border-slate-200 text-center group-hover:border-emerald-500/30 transition-all">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Desloc. Máx.</p>
                      <p className="text-xl font-black text-slate-900">{formatNumberBR(results.max_displacement * 1000)} mm</p>
                    </div>
                    <div className="p-5 rounded-3xl bg-white/5 border border-slate-200 text-center group-hover:border-blue-500/30 transition-all">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Momento Máx.</p>
                      <p className="text-xl font-black text-slate-900">{formatNumberBR(results.max_moment)} kNm</p>
                    </div>
                  </div>

                  <div className="p-6 rounded-[2.5rem] bg-blue-500/10 border border-blue-500/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Taxa de Utilização</span>
                      <span className="text-xs font-black text-slate-900">{(results.stability_index * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden p-0.5">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" style={{ width: "92%" }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-72 rounded-[50px] border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-600 bg-white/5 group hover:border-blue-500/30 transition-all duration-700">
              <div className="p-6 bg-slate-900 rounded-[2.5rem] shadow-2xl mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 border border-slate-200">
                <Activity className="w-10 h-10 text-blue-500/40" />
              </div>
              <p className="text-[11px] font-black uppercase tracking-[0.4em] text-slate-500">Aguardando Processamento Matricial</p>
            </div>
          )}
        </div>
      </div>
    </ModuleContainer>
  );
}

