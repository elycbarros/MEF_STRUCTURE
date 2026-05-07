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
  Table as TableIcon
} from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import { ModuleContainer } from "@/components/ui/ModuleContainer";
import Frame3DView from "./Frame3DView";

type TrussType = 
  | "warren" | "fink" | "howe" | "pratt" 
  | "king_post" | "queen_post" | "flat" 
  | "scissors" | "fan" | "double_fink" | "double_howe";

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

  // Truss Generator Logic
  const { nodes, members } = useMemo(() => {
    const nodes: Node[] = [];
    const members: Member[] = [];
    const dx = span / panels;
    const midIdx = panels / 2;

    const isPitched = ["fink", "king_post", "queen_post", "scissors", "fan", "double_fink", "double_howe"].includes(trussType);
    const isFlat = !isPitched;

    // Bottom Chord Nodes
    for (let i = 0; i <= panels; i++) {
      let y = 0;
      if (trussType === "scissors") {
        // Scissors truss bottom chord also rises
        const distFromMid = Math.abs(i - midIdx);
        y = (height * 0.4) * (1 - distFromMid / midIdx);
      }
      nodes.push({ id: i + 1, x: i * dx, y: y, z: 0 });
    }

    // Top Chord Nodes
    const offset = panels + 1;
    for (let i = 0; i <= panels; i++) {
      let y = height;
      if (isPitched) {
        const distFromMid = Math.abs(i - midIdx);
        y = height * (1 - distFromMid / midIdx);
      }
      nodes.push({ id: i + offset + 1, x: i * dx, y: y, z: 0 });
    }

    // Bottom Chord Members
    for (let i = 0; i < panels; i++) {
      members.push({ id: members.length + 1, node_i: i + 1, node_j: i + 2 });
    }

    // Top Chord Members
    for (let i = 0; i < panels; i++) {
      members.push({ id: members.length + 1, node_i: i + offset + 1, node_j: i + offset + 2 });
    }

    // Verticals and Diagonals
    if (isFlat) {
      for (let i = 0; i <= panels; i++) {
        // Verticals
        if (trussType !== "warren" || i === 0 || i === panels) {
           members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
        }
      }

      // Diagonals for flat trusses
      for (let i = 0; i < panels; i++) {
        if (trussType === "pratt") {
          if (i < midIdx) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
          else members.push({ id: members.length + 1, node_i: i + 2, node_j: i + offset + 1 });
        } else if (trussType === "howe") {
          if (i < midIdx) members.push({ id: members.length + 1, node_i: i + 2, node_j: i + offset + 1 });
          else members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
        } else if (trussType === "warren") {
          if (i % 2 === 0) members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
          else members.push({ id: members.length + 1, node_i: i + offset + 1, node_j: i + 2 });
        } else if (trussType === "flat") {
          // Cross diagonals or simple alternate
          members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 2 });
        }
      }
    } else {
      // Pitched trusses
      if (trussType === "king_post") {
        members.push({ id: members.length + 1, node_i: midIdx + 1, node_j: midIdx + offset + 1 });
      } else if (trussType === "queen_post") {
        const q1 = Math.floor(panels * 0.3);
        const q2 = Math.ceil(panels * 0.7);
        members.push({ id: members.length + 1, node_i: q1 + 1, node_j: q1 + offset + 1 });
        members.push({ id: members.length + 1, node_i: q2 + 1, node_j: q2 + offset + 1 });
        members.push({ id: members.length + 1, node_i: q1 + offset + 1, node_j: q2 + offset + 1 });
      } else if (trussType === "fink" || trussType === "double_fink") {
        // Simplified Fink: Web members connecting to midpoints of chords
        for (let i = 0; i <= panels; i++) {
          if (i !== 0 && i !== panels && i === midIdx) {
             members.push({ id: members.length + 1, node_i: i + 1, node_j: i + offset + 1 });
          }
          if (i < midIdx) members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
          else if (i > midIdx) members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
        }
      } else {
        // Fallback for other pitched: Vertical at mid and simple diagonals
        members.push({ id: members.length + 1, node_i: midIdx + 1, node_j: midIdx + offset + 1 });
        for (let i = 0; i < panels; i++) {
           members.push({ id: members.length + 1, node_i: i + 1, node_j: midIdx + offset + 1 });
        }
      }
    }

    return { nodes, members };
  }, [trussType, span, height, panels]);

  const handleAnalyze = async () => {
    setLoading(true);
    // Simulating call to backend /api/mestre/truss/analyze
    setTimeout(() => {
      setResults({
        max_force: 45.2,
        critical_member: 4,
        buckling_factor: 1.85,
        pedagogical: {
          method: "Método dos Nós / Ritter",
          steps: ["Isolamento do nó A", "Equilíbrio ΣFy = 0", "Equilíbrio ΣFx = 0"]
        }
      });
      setLoading(false);
    }, 1000);
  };

  return (
    <ModuleContainer
      title="Treliças Metálicas (Mestre)"
      subtitle="Geração e análise de treliças típicas (Pratt, Howe, Warren). Estudo de esforços axiais e flambagem em perfis metálicos."
      icon={<LayoutGrid className="h-6 w-6 text-white" />}
      theme="academic"
      solverType="Steel Truss Solver"
    >
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="p-6 rounded-[2rem] border border-slate-200 bg-white shadow-sm">
            <h3 className="font-black text-sm uppercase tracking-wider text-slate-400 mb-6">Configuração da Treliça</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-[10px] font-black uppercase text-slate-500 mb-1 block">Tipo de Treliça</label>
                <select 
                  value={trussType}
                  onChange={(e) => setTrussType(e.target.value as TrussType)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold"
                >
                  <option value="warren">Treliça Warren (Equilibrada)</option>
                  <option value="fink">Treliça Fink (Padrão)</option>
                  <option value="howe">Treliça Howe (Diagonais Comprimidas)</option>
                  <option value="pratt">Treliça Pratt (Diagonais Tracionadas)</option>
                  <option value="king_post">Treliça King Post (Poste Central)</option>
                  <option value="queen_post">Treliça Queen Post</option>
                  <option value="flat">Treliça Plana (Paralela)</option>
                  <option value="scissors">Treliça Tesoura (Scissors)</option>
                  <option value="fan">Treliça Leque (Fan)</option>
                  <option value="double_fink">Treliça Double Fink</option>
                  <option value="double_howe">Treliça Howe Dupla</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black uppercase text-slate-500 mb-1 block">Vão (m)</label>
                  <input type="number" value={span} onChange={e => setSpan(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold" />
                </div>
                <div>
                  <label className="text-[10px] font-black uppercase text-slate-500 mb-1 block">Altura (m)</label>
                  <input type="number" value={height} onChange={e => setHeight(Number(e.target.value))} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold" />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-black uppercase text-slate-500 mb-1 block">Número de Painéis</label>
                <input type="range" min="2" max="12" step="2" value={panels} onChange={e => setPanels(Number(e.target.value))} className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600" />
                <div className="flex justify-between text-[10px] font-bold text-slate-400 mt-1">
                  <span>2</span>
                  <span>{panels} painéis</span>
                  <span>12</span>
                </div>
              </div>

              <button 
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3 bg-blue-600 text-white rounded-2xl font-black text-xs hover:bg-blue-700 transition-all shadow-md active:scale-95 mt-4"
              >
                {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                GERAR E ANALISAR
              </button>
            </div>
          </div>

          <div className="p-6 rounded-[2rem] border border-slate-200 bg-blue-50/50">
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-4 h-4 text-blue-600" />
              <h4 className="text-[10px] font-black uppercase text-blue-600">Conceito Mestre</h4>
            </div>
            <p className="text-[11px] font-medium text-blue-900/80 leading-relaxed">
              Treliças são sistemas onde as barras trabalham predominantemente à **tração ou compressão**. O Modo Mestre foca no equilíbrio dos nós e na verificação de flambagem local (NBR 8800).
            </p>
          </div>
        </div>

        <div className="col-span-12 lg:col-span-8 space-y-6">
          <div className="h-[450px] rounded-[2.5rem] border border-slate-200 bg-slate-50 overflow-hidden relative shadow-inner">
             <Frame3DView 
              nodes={nodes.map(n => ({ node: n.id, x: n.x, y: n.y, z: n.z }))} 
              members={members.map(m => ({
                index: m.id,
                Node1: m.node_i,
                Node2: m.node_j,
                b: 100, d: 100, // Perfil genérico para visualização
                Type: "Truss"
              }))} 
            />
          </div>

          {results && (
            <div className="grid grid-cols-3 gap-6 animate-in slide-in-from-bottom duration-500">
              <div className="p-6 rounded-[2rem] border border-slate-200 bg-white">
                <p className="text-[10px] font-black uppercase text-slate-400 mb-1">Esforço Máx.</p>
                <p className="text-2xl font-black text-slate-900">{formatNumberBR(results.max_force)} kN</p>
                <div className="mt-2 text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full inline-block">Compressão</div>
              </div>

              <div className="p-6 rounded-[2rem] border border-slate-200 bg-white">
                <p className="text-[10px] font-black uppercase text-slate-400 mb-1">Flambagem (λ)</p>
                <p className="text-2xl font-black text-slate-900">{formatNumberBR(results.buckling_factor)}</p>
                <div className="mt-2 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full inline-block">Seguro</div>
              </div>

              <div className="p-6 rounded-[2rem] border border-slate-200 bg-white">
                <p className="text-[10px] font-black uppercase text-slate-400 mb-1">Método de Solução</p>
                <p className="text-xs font-black text-slate-900 mt-2">{results.pedagogical.method}</p>
                <ul className="mt-2 space-y-1">
                  {results.pedagogical.steps.map((s: string, i: number) => (
                    <li key={i} className="text-[9px] font-bold text-slate-500 flex items-center gap-1">
                      <ChevronRight className="w-2 h-2" /> {s}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </ModuleContainer>
  );
}
