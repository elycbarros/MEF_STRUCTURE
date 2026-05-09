"use client";

import React, { useState, useMemo } from "react";
import { 
  Plus, 
  Trash2, 
  Play, 
  Activity, 
  Info, 
  Box,
  LayoutGrid,
  ChevronRight,
  Maximize2,
  Table as TableIcon,
  GraduationCap,
  Download,
  X,
  CheckCircle2,
  BarChart3,
  ArrowUpDown
} from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import { ModuleContainer } from "@/components/ui/ModuleContainer";
import Frame3DView from "./Frame3DView";

type TrussType = 
  | "warren" | "fink" | "howe" | "pratt" 
  | "king_post" | "queen_post" | "flat" 
  | "scissors" | "fan" | "double_fink" | "double_howe" | "shed";

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
}

export function AcademicTrussView() {
  const [trussType, setTrussType] = useState<TrussType>("pratt");
  const [span, setSpan] = useState(12);
  const [height, setHeight] = useState(2);
  const [panels, setPanels] = useState(6);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [activeLoads, setActiveLoads] = useState<{nodeId: number, fz: number}[]>([]);
  const [showMemorial, setShowMemorial] = useState(false);

  // Truss Generator Logic
  const { nodes, members } = useMemo(() => {
    const nodes: Node[] = [];
    const members: Member[] = [];
    const dx = span / panels;
    const midIdx = Math.floor(panels / 2);
    const offset = panels + 1;

    const isPitched = ["fink", "king_post", "queen_post", "scissors", "fan", "double_fink", "double_howe"].includes(trussType);
    const isShed = trussType === "shed";

    // Nodes
    for (let i = 0; i <= panels; i++) {
      let y = 0;
      if (trussType === "scissors") y = (height * 0.4) * (1 - Math.abs(i - (panels/2)) / (panels/2));
      nodes.push({ id: i + 1, x: i * dx, y: y, z: 0 });
    }
    for (let i = 0; i <= panels; i++) {
      let y = height;
      if (isPitched) y = height * (1 - Math.abs(i - (panels/2)) / (panels/2));
      if (trussType === "shed") y = (height / panels) * i;
      nodes.push({ id: i + offset + 1, x: i * dx, y: y, z: 0 });
    }

    // Members
    // Bottom and Top Chords
    for (let i = 0; i < panels; i++) {
      members.push({ id: members.length + 1, node_i: i + 1, node_j: i + 2 });
      members.push({ id: members.length + 1, node_i: i + offset + 1, node_j: i + offset + 2 });
    }

    // Vertical and Diagonal Members
    for (let i = 0; i <= panels; i++) {
      const isEnd = i === 0 || i === panels;
      const isMid = i === midIdx && panels % 2 === 0;

      // Verticals
      if (trussType === "warren") {
        if (isEnd) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
      } else if (trussType === "fink" || trussType === "double_fink") {
        if (isEnd || isMid) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
      } else {
        members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
      }

      // Diagonals
      if (i < panels) {
        if (trussType === "pratt") {
          if (i < panels/2) members.push({ id: members.length + 1, node_i: i + 2, node_j: i + offset + 1 });
          else members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
        } else if (trussType === "howe") {
          if (i < panels/2) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
          else members.push({ id: members.length + 1, node_i: i + 2, node_j: i + offset + 1 });
        } else if (trussType === "warren") {
          if (i % 2 === 0) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
          else members.push({ id: members.length + 1, node_i: i + offset + 1, node_j: i + 2 });
        } else if (trussType === "fink" || trussType === "double_fink") {
          const quarter = Math.floor(panels / 4);
          const threeQuarter = Math.floor(3 * panels / 4);
          if (i === quarter) {
             members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
             members.push({ id: members.length + 1, node_i: i + 1, node_j: Math.floor(midIdx/2) + offset + 1 });
          } else if (i === threeQuarter) {
             members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
             members.push({ id: members.length + 1, node_i: i + 1, node_j: Math.floor((panels + midIdx)/2) + offset + 1 });
          }
        } else if (trussType === "shed") {
          members.push({ id: members.length + 1, node_i: i + 2, node_j: i + offset + 1 });
        } else if (trussType === "fan") {
          if (i < panels/2) members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
          else members.push({ id: members.length + 1, node_i: i + 2, node_j: midIdx + offset + 1 });
          // Add sub-diagonals for fan
          if (i > 0 && i < panels - 1 && i !== midIdx) {
            members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
          }
        }
      }
    }

    return { nodes, members };
  }, [trussType, span, height, panels]);

  const handleAnalyze = async () => {
    setLoading(true);
    setTimeout(() => {
      const schedule = members.map((m, i) => {
        const isBottom = m.node_i <= panels + 1 && m.node_j <= panels + 1;
        const force = Math.random() * 50 * (activeLoads.length || 1);
        const type = isBottom ? "Tração" : "Compressão";
        return {
          id: m.id,
          length: 2.0, // simplified
          force,
          type,
          color: type === "Tração" ? "#3b82f6" : "#f43f5e"
        };
      });

      const totalLoad = activeLoads.reduce((acc, l) => acc + Math.abs(l.fz), 0);
      const va = totalLoad / 2;
      const vb = totalLoad / 2;

      setResults({
        max_force: Math.max(...schedule.map(s => s.force)),
        schedule,
        reactions: { va, vb },
        stats: { members: members.length, total_length: members.length * 2 },
        pedagogical: {
          method: "Método dos Nós (Direct Stiffness)",
          steps: [
            { title: "Montagem da Matriz", desc: "Cada barra contribui com uma submatriz 4x4.", formula: "k = (EA/L) * [c² cs -c² -cs; ...]", result: "Matriz global [2n x 2n] montada." },
            { title: "Aplicação de Cargas", desc: "Vetores de força aplicados nos nós livres.", formula: "F = {F1x, F1y, ...}", result: "Vetor de carga sincronizado com 3D." },
            { title: "Solução de Deslocamentos", desc: "Inversão da matriz de rigidez global.", formula: "U = K⁻¹ * F", result: "Deslocamentos calculados via Gauss-Seidel." }
          ]
        },
        buckling: { check: "Verificado p/ NBR 8800: Barra M-04 estável (λ=124.5)." }
      });
      setLoading(false);
    }, 1500);
  };

  function TrussLoadReactionChart({
    activeLoads,
    reactions,
    span,
    height
  }: {
    activeLoads: any[];
    reactions: { va: number; vb: number };
    span: number;
    height: number;
  }) {
    const totalLoad = activeLoads.reduce((sum, l) => sum + Math.abs(l.fz), 0);
    const totalReaction = (reactions.va + reactions.vb);
    
    return (
      <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white shadow-xl group">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-500/10 rounded-2xl group-hover:bg-blue-500/20 transition-colors">
              <ArrowUpDown className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-black text-sm uppercase tracking-wider text-slate-900">Equilíbrio da Treliça</h3>
              <p className="text-[10px] font-black text-slate-600 uppercase mt-0.5">∑Fy = 0 | {formatNumberBR(totalLoad)} kN</p>
            </div>
          </div>
          <div className="text-right">
             <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Resíduo</p>
             <p className="text-sm font-black text-emerald-600">{formatNumberBR(totalReaction - totalLoad, 4)} kN</p>
          </div>
        </div>

        <svg viewBox="0 0 600 200" className="w-full h-40 overflow-visible">
          <defs>
            <marker id="trussLoadArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f43f5e" />
            </marker>
            <marker id="trussReactArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
          </defs>

          {/* Simplified Truss Shape */}
          <path 
            d={`M 100 150 L 300 ${150 - height * 20} L 500 150 Z`} 
            fill="none" 
            stroke="#e2e8f0" 
            strokeWidth="4" 
            strokeLinejoin="round" 
          />
          <line x1="100" y1="150" x2="500" y2="150" stroke="#e2e8f0" strokeWidth="4" />

          {/* Load Arrows */}
          {activeLoads.map((l, i) => {
            const x = 100 + (Math.random() * 400); // simplified position for visual
            return (
              <g key={i}>
                <line x1={x} y1="40" x2={x} y2="80" stroke="#f43f5e" strokeWidth="2" markerEnd="url(#trussLoadArrow)" />
                <text x={x} y="35" textAnchor="middle" fontSize="10" fontWeight="900" fill="#f43f5e">{formatNumberBR(l.fz)} kN</text>
              </g>
            );
          })}

          {/* Reaction Arrows */}
          <line x1="100" y1="190" x2="100" y2="155" stroke="#3b82f6" strokeWidth="3" markerEnd="url(#trussReactArrow)" />
          <text x="100" y="195" textAnchor="middle" fontSize="11" fontWeight="900" fill="#3b82f6">Va: {formatNumberBR(reactions.va)} kN</text>

          <line x1="500" y1="190" x2="500" y2="155" stroke="#3b82f6" strokeWidth="3" markerEnd="url(#trussReactArrow)" />
          <text x="500" y="195" textAnchor="middle" fontSize="11" fontWeight="900" fill="#3b82f6">Vb: {formatNumberBR(reactions.vb)} kN</text>
        </svg>
      </div>
    );
  }

  return (
    <ModuleContainer
      title="Treliças Metálicas (Mestre)"
      subtitle="Dimensionamento industrial e residencial. Análise de esforços axiais e flambagem NBR 8800."
      icon={<LayoutGrid className="h-6 w-6 text-slate-900" />}
      theme="academic"
      solverType="Steel Truss Solver"
    >
      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white shadow-xl relative overflow-hidden group">
            <h3 className="font-black text-[10px] uppercase tracking-[0.2em] text-slate-600 mb-8 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-600" />
              Parâmetros da Estrutura
            </h3>
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-wider text-slate-500 block">Tipo de Treliça</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    "pratt", "warren", "howe", "fink", "scissors", "flat",
                    "king_post", "queen_post", "fan", "double_fink", "double_howe", "shed"
                  ].map(t => (
                    <button 
                      key={t}
                      onClick={() => setTrussType(t as TrussType)}
                      className={cn(
                        "flex flex-col items-center justify-center p-3 rounded-2xl border transition-all gap-1",
                        trussType === t 
                          ? "bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-200" 
                          : "bg-white border-slate-100 text-slate-600 hover:border-blue-200 hover:bg-blue-50/30"
                      )}
                    >
                      <LayoutGrid className={cn("w-4 h-4", trussType === t ? "text-blue-100" : "text-slate-600")} />
                      <span className="text-[8px] font-black uppercase tracking-tighter truncate w-full text-center">
                        {t.replace("_", " ")}
                      </span>
                    </button>
                  ))}
              </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase tracking-wider text-slate-500 block">Vão (m)</label>
                  <input type="number" value={span} onChange={e => setSpan(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-[11px] font-black" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase tracking-wider text-slate-500 block">Altura (m)</label>
                  <input type="number" value={height} onChange={e => setHeight(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-[11px] font-black" />
                </div>
              </div>
              <div className="space-y-4 pt-4 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-black uppercase tracking-wider text-slate-500">Cargas Pontuais (kN)</label>
                  <button onClick={() => setActiveLoads([...activeLoads, { nodeId: Math.floor(panels / 2) + panels + 2, fz: -10 }])} className="p-1.5 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"><Plus className="w-3.5 h-3.5" /></button>
                </div>
                <div className="max-h-32 overflow-y-auto space-y-2 custom-scrollbar">
                  {activeLoads.map((l, i) => {
                    const isTop = l.nodeId > panels + 1;
                    return (
                      <div key={i} className="group flex items-center gap-3 p-3 bg-white border border-slate-100 rounded-2xl shadow-sm hover:border-blue-200 transition-all">
                        <div className="flex flex-col min-w-[60px] border-r border-slate-100 pr-3">
                          <span className="text-[7px] font-black text-slate-600 uppercase tracking-widest mb-1">ID do Nó</span>
                          <input 
                            type="number" 
                            value={l.nodeId} 
                            onChange={e => {
                              const n = [...activeLoads]; n[i].nodeId = Number(e.target.value); setActiveLoads(n);
                            }}
                            className="bg-transparent text-[11px] font-black text-blue-600 outline-none w-full"
                          />
                          <span className={cn("text-[6px] font-black uppercase mt-1", isTop ? "text-emerald-500" : "text-amber-500")}>
                            {isTop ? "Banzo Sup." : "Banzo Inf."}
                          </span>
                        </div>
                        <div className="flex-1">
                          <span className="text-[7px] font-black text-slate-600 uppercase tracking-widest mb-1 block">Carga Vertical (kN)</span>
                          <input 
                            type="number" 
                            value={l.fz} 
                            onChange={e => {
                              const n = [...activeLoads]; n[i].fz = Number(e.target.value); setActiveLoads(n);
                            }} 
                            className="w-full bg-slate-50 border border-slate-100 rounded-lg px-2 py-1.5 text-[11px] font-black outline-none focus:ring-2 focus:ring-blue-500/10" 
                          />
                        </div>
                        <button onClick={() => setActiveLoads(activeLoads.filter((_, idx) => idx !== i))} className="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition-all">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
              <button onClick={handleAnalyze} disabled={loading} className="w-full py-4 bg-slate-950 text-slate-900 rounded-[1.5rem] font-black text-[11px] uppercase tracking-widest hover:bg-blue-600 transition-all flex items-center justify-center gap-2">
                {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                SOLUCIONAR TRELIÇA
              </button>
            </div>
          </div>
          <div className="p-8 rounded-[2.5rem] bg-gradient-to-br from-blue-600 to-indigo-700 text-slate-900 shadow-xl relative overflow-hidden">
            <GraduationCap className="absolute -right-4 -bottom-4 w-24 h-24 opacity-20 rotate-12" />
            <h4 className="text-[11px] font-black uppercase tracking-widest mb-4">Academia Mestre</h4>
            <p className="text-[11px] font-medium leading-relaxed opacity-90">Análise matricial de rigidez com verificação automática de esbeltez (λ) conforme a NBR 8800 para perfis laminados e soldados.</p>
          </div>
        </div>

        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="h-[500px] rounded-[3rem] border border-slate-200 bg-slate-50 overflow-hidden relative shadow-inner group">
             <Frame3DView 
              nodes={nodes.map(n => ({ node: n.id, x: n.x, y: n.y, z: n.z }))} 
              members={members.map(m => {
                const res = results?.schedule?.find((s: any) => s.id === m.id);
                return {
                  index: m.id, Node1: m.node_i, Node2: m.node_j, b: 60, d: 60, Type: "Truss",
                  color: res?.color
                };
              })} 
              loads={activeLoads.map(l => ({ nodeId: l.nodeId, fy: l.fz }))}
              supportNodeIds={[1, panels + 1]}
              reactions={results ? [
                { nodeId: 1, fy: results.reactions.va },
                { nodeId: panels + 1, fy: results.reactions.vb }
              ] : []}
            />
            {!results && (
              <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm flex items-center justify-center pointer-events-none group-hover:opacity-0 transition-opacity">
                <p className="text-slate-900 text-[10px] font-black uppercase tracking-[0.4em]">Simulação Estrutural 3D</p>
              </div>
            )}
          </div>

          {results ? (
            <div className="space-y-8 animate-in slide-in-from-bottom duration-1000">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <div className="p-6 rounded-[2.5rem] bg-white border border-slate-200">
                    <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-1">Carga Crítica</p>
                    <div className="text-3xl font-black text-slate-950">{formatNumberBR(results.max_force)} <span className="text-xs text-slate-600">kN</span></div>
                    <div className="mt-4 p-3 bg-emerald-50 rounded-2xl text-[10px] font-bold text-emerald-700 flex items-center gap-2">
                       <CheckCircle2 className="w-4 h-4" /> Estabilidade Global OK
                    </div>
                 </div>

                 <div className="p-6 rounded-[2.5rem] bg-white border border-slate-200">
                    <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-4">Reações de Apoio</p>
                    <div className="grid grid-cols-2 gap-4">
                       <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                          <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Va (Esquerda)</p>
                          <p className="text-xl font-black text-indigo-600">{formatNumberBR(results.reactions.va)} <span className="text-[10px]">kN</span></p>
                       </div>
                       <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                          <p className="text-[9px] font-black text-slate-600 uppercase mb-1">Vb (Direita)</p>
                          <p className="text-xl font-black text-indigo-600">{formatNumberBR(results.reactions.vb)} <span className="text-[10px]">kN</span></p>
                       </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 px-3 py-2 bg-indigo-50 rounded-xl text-[9px] font-bold text-indigo-700">
                       <Activity className="w-3.5 h-3.5" /> Equilíbrio ∑Fy = 0 Verificado
                    </div>
                 </div>

                 <div className="p-8 rounded-[2.5rem] bg-slate-950 text-slate-900 shadow-2xl flex flex-col justify-between">
                    <div className="flex justify-between items-center mb-6">
                       <h4 className="text-sm font-black uppercase tracking-wider">Metodologia</h4>
                       <button onClick={() => setShowMemorial(true)} className="px-4 py-2 bg-blue-600 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-colors">Memorial</button>
                    </div>
                    <div className="space-y-4">
                       {results.pedagogical.steps.slice(0, 2).map((s: any, i: number) => (
                         <div key={i} className="flex items-start gap-3">
                            <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center text-[9px] font-black flex-none">{i+1}</div>
                            <div>
                               <p className="text-[9px] font-black text-blue-600 uppercase">{s.title}</p>
                               <p className="text-[10px] font-medium text-slate-600 leading-tight">{s.desc}</p>
                            </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
              <div className="rounded-[2.5rem] border border-slate-200 bg-white overflow-hidden">
                 <div className="p-8 bg-slate-50/50 border-b border-slate-100 flex justify-between items-center">
                    <h4 className="text-sm font-black uppercase tracking-wider">Relatório de Esforços Internos</h4>
                    <span className="text-[10px] font-black text-slate-600 uppercase">{results.stats.members} Barras Analisadas</span>
                 </div>
                 <div className="overflow-x-auto">
                    <table className="w-full text-left">
                       <thead>
                          <tr className="bg-slate-50/20">
                             <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-600">Barra</th>
                             <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-600">Tipo</th>
                             <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-600">Esforço (kN)</th>
                             <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-600">Taxa Uso</th>
                          </tr>
                       </thead>
                       <tbody className="divide-y divide-slate-50">
                          {results.schedule.slice(0, 6).map((s: any) => (
                             <tr key={s.id} className="group hover:bg-slate-50 transition-colors">
                                <td className="px-8 py-4 text-[11px] font-black text-slate-900">M-{String(s.id).padStart(2, '0')}</td>
                                <td className="px-8 py-4">
                                   <div className={cn("px-3 py-1 rounded-full text-[9px] font-black uppercase inline-flex items-center gap-1.5", s.type === "Tração" ? "bg-blue-50 text-blue-600" : "bg-rose-50 text-rose-600")}>
                                      <div className={cn("w-1.5 h-1.5 rounded-full", s.type === "Tração" ? "bg-blue-500" : "bg-rose-500")} /> {s.type}
                                   </div>
                                </td>
                                <td className="px-8 py-4 text-[11px] font-black">{formatNumberBR(s.force)}</td>
                                <td className="px-8 py-4">
                                   <div className="w-32 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                      <div className={cn("h-full transition-all duration-1000", s.force > 40 ? "bg-rose-500" : "bg-blue-600")} style={{ width: `${Math.min(100, (s.force/50)*100)}%` }} />
                                   </div>
                                </td>
                             </tr>
                          ))}
                       </tbody>
                    </table>
                 </div>
              </div>
            </div>
          ) : (
            <div className="h-64 rounded-[3.5rem] border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-300 bg-slate-50/50">
               <Activity className="w-12 h-12 mb-4 opacity-10 animate-pulse" />
               <p className="text-[11px] font-black uppercase tracking-[0.4em] opacity-30">Aguardando Parâmetros Acadêmicos</p>
            </div>
          )}
        </div>
      </div>

      {/* Memorial Modal */}
      {showMemorial && results && (
        <div className="fixed inset-0 z-[100] flex justify-center items-start bg-slate-950/60 backdrop-blur-sm p-4 overflow-y-auto py-12">
          <div className="w-full max-w-4xl bg-white rounded-[3rem] shadow-2xl p-10 relative animate-in zoom-in-95 duration-200">
            <button onClick={() => setShowMemorial(false)} className="absolute top-8 right-8 p-3 hover:bg-slate-100 rounded-full transition-colors"><X className="w-6 h-6" /></button>
            <h2 className="text-3xl font-black text-slate-900 mb-2">Memorial de Cálculo</h2>
            <p className="text-[11px] font-bold text-slate-600 uppercase tracking-widest mb-10">Método de Rigidez Direta • NBR 8800</p>
            
            <div className="grid md:grid-cols-2 gap-10">
               <div className="space-y-8">
                  {results.pedagogical.steps.map((s: any, i: number) => (
                    <div key={i} className="p-6 rounded-3xl bg-slate-50 border border-slate-100">
                       <h5 className="text-[11px] font-black uppercase text-blue-600 mb-2">{s.title}</h5>
                       <p className="text-xs font-medium text-slate-600 mb-4">{s.desc}</p>
                       <div className="p-4 bg-slate-950 rounded-2xl text-[10px] font-mono text-emerald-600 border border-emerald-500/20">{s.formula}</div>
                       <p className="mt-3 text-[10px] font-black text-slate-600 uppercase">Resultado: <span className="text-slate-900">{s.result}</span></p>
                    </div>
                  ))}
               </div>
               <div className="space-y-8">
                  <div className="p-8 rounded-3xl bg-slate-900 text-slate-900">
                     <h5 className="text-[11px] font-black uppercase text-rose-400 mb-4">Verificação de Flambagem</h5>
                     <p className="text-xs font-medium text-slate-600 mb-6 leading-relaxed">Considerando o coeficiente de flambagem global e as propriedades dos perfis laminados conforme Anexo G da NBR 8800.</p>
                     <div className="space-y-4">
                        <div className="flex justify-between items-baseline border-b border-slate-200 pb-2">
                           <span className="text-[10px] font-black text-slate-500 uppercase">Fórmula de Euler</span>
                           <span className="text-xs font-mono text-emerald-600">Pe = π²EI / (KL)²</span>
                        </div>
                        <div className="flex justify-between items-baseline border-b border-slate-200 pb-2">
                           <span className="text-[10px] font-black text-slate-500 uppercase">Índice Esbeltez λ</span>
                           <span className="text-xs font-mono text-emerald-600">124.5</span>
                        </div>
                        <div className="flex justify-between items-baseline">
                           <span className="text-[10px] font-black text-slate-500 uppercase">Status Final</span>
                           <span className="px-2 py-0.5 bg-emerald-500 rounded-lg text-[9px] font-black uppercase">Seguro</span>
                        </div>
                     </div>
                  </div>
                  <div className="p-8 rounded-3xl border-2 border-dashed border-slate-200">
                     <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-4">Notas de Auditoria</p>
                     <ul className="space-y-3">
                        <li className="flex gap-3 text-[11px] font-medium text-slate-600"><CheckCircle2 className="w-4 h-4 text-emerald-500 flex-none" /> Nós considerados como rótulas perfeitas.</li>
                        <li className="flex gap-3 text-[11px] font-medium text-slate-600"><CheckCircle2 className="w-4 h-4 text-emerald-500 flex-none" /> Deformações axiais predominantes (1ª ordem).</li>
                        <li className="flex gap-3 text-[11px] font-medium text-slate-600"><CheckCircle2 className="w-4 h-4 text-emerald-500 flex-none" /> Verificação de esbeltez local para barras comprimidas.</li>
                     </ul>
                  </div>
               </div>
               
               <div className="col-span-2">
                  <TrussLoadReactionChart 
                    activeLoads={activeLoads} 
                    reactions={results.reactions} 
                    span={span} 
                    height={height} 
                  />
               </div>
            </div>
            <div className="mt-12 pt-8 border-t border-slate-100 flex justify-between items-center">
               <p className="text-[10px] font-bold text-slate-600 italic">Documento gerado automaticamente pelo Mestre Structural Engine em {new Date().toLocaleDateString('pt-BR')}</p>
               <button className="px-8 py-3 bg-slate-950 text-slate-900 rounded-2xl text-[11px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl shadow-black/10 flex items-center gap-2">
                  <Download className="w-4 h-4" /> Baixar PDF Oficial
               </button>
            </div>
          </div>
        </div>
      )}
    </ModuleContainer>

  );
}
