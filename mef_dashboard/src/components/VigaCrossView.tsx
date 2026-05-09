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
  ChevronRight,
  ChevronDown,
  ArrowRightLeft,
  Layout,
  Target,
  Printer,
  Maximize2,
  ShieldCheck,
  ArrowRight,
  ArrowUpDown
} from "lucide-react";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart
} from "recharts";
import { cn, formatNumberBR } from "@/lib/utils";
import { solveCross } from "@/modules/vigacross/engine";
import { BeamInput, CrossSolveResult, SupportType, SpanLoad } from "@/modules/vigacross/types";
import { StructuralAuditAgent } from "@/agents/StructuralAuditAgent";
import { ModuleContainer } from "@/components/ui/ModuleContainer";
import { BimExporter } from "@/lib/bimExporter";
import { OptimizationEngine } from "@/lib/optimizationEngine";
import { MemorialHtmlView } from "./MemorialHtmlView";

export function VigaCrossView() {
  const [beamInput, setBeamInput] = useState<BeamInput>({
    spans: [
      { id: "V1", length: 4, inertiaCm4: 200000, loads: [{ type: "udl", value: 20 }] },
      { id: "V2", length: 5, inertiaCm4: 200000, loads: [{ type: "point", value: 50, position: 2.5 }] }
    ],
    supports: ["fixed", "pin", "fixed"],
    eGPa: 25,
    defaultInertiaCm4: 208333,
    sectionB: 20,
    sectionH: 50,
    fck: 25,
    tolerance: 0.01,
    maxIterations: 50
  });

  const [results, setResults] = useState<CrossSolveResult | null>(null);
  const [auditResult, setAuditResult] = useState<any>(null);
  const [optimizationSuggestion, setOptimizationSuggestion] = useState<any>(null);
  const [expandedIteration, setExpandedIteration] = useState<number | null>(null);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [showHtmlMemorial, setShowHtmlMemorial] = useState(false);

  const handleRunAnalysis = async () => {
    try {
      const res = solveCross(beamInput);
      setResults(res);
      
      const maxDeflection = Math.max(...res.diagrams.map(d => Math.abs(d.deflection ?? 0)));
      const maxMoment = Math.max(...res.diagrams.map(d => Math.abs(d.moment ?? 0)));

      // Chamar Agente de Auditoria (Fase 4)
      const audit = await StructuralAuditAgent.auditBeam({
        max_displacement_mm: maxDeflection,
        span_length_m: Math.max(...beamInput.spans.map(s => s.length)),
        max_moment_kNm: maxMoment,
        h: (beamInput.sectionH || 50) / 100 // Convertendo para metros
      });
      setAuditResult(audit);

      // M5-PhD Optimization Engine (Design Generativo - Fase 5)
      const optimization = OptimizationEngine.suggestSection({
        currentB: beamInput.sectionB || 20,
        currentH: beamInput.sectionH || 50,
        currentFck: beamInput.fck || 25,
        utilization: maxDeflection / 20, // Simulação de aproveitamento baseada na flecha
        type: 'beam'
      });
      setOptimizationSuggestion(optimization);

    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleBimExport = () => {
    const totalLength = beamInput.spans.reduce((s, b) => s + b.length, 0);
    BimExporter.downloadIFC([{
      id: "VIGA-CONTINUA-01",
      type: 'BEAM',
      name: 'Viga Continua Cross',
      dimensions: { b: 0.2, h: 0.5, l: totalLength },
      position: { x: 0, y: 0, z: 0 }
    }]);
  };

  const handleGeneratePDF = async () => {
    if (!results) return;
    setShowHtmlMemorial(true);
  };

  const beamLoadSummary = useMemo(() => {
    const totalLoad = beamInput.spans.reduce((sum, span) => (
      sum + span.loads.reduce((spanSum, load) => spanSum + (load.type === "udl" ? load.value * span.length : load.value), 0)
    ), 0);
    const totalReaction = results?.nodeReactions.reduce((sum, reaction) => sum + reaction.verticalReaction, 0) ?? 0;
    return { totalLoad, totalReaction, residual: totalReaction - totalLoad };
  }, [beamInput.spans, results]);

  const buildHtmlMemorial = () => ({
    title: "Memorial Tecnico - Viga Cross",
    steps: [
      {
        id: "cross-geom",
        title: "Propriedades da Seção e Materiais",
        formula_latex: "E_{cs} = 0.85 \\cdot 5600 \\cdot \\sqrt{f_{ck}}",
        substitution_latex: `f_{ck} = ${beamInput.fck} MPa \\Rightarrow E = ${beamInput.eGPa} GPa`,
        result_latex: `b/h = ${beamInput.sectionB}/${beamInput.sectionH} cm`,
        explanation: "Definição das propriedades geométricas e mecânicas da viga para cálculo da rigidez flexional.",
        norm_ref: "NBR 6118:2014",
        status: "OK",
      },
      {
        id: "cross-mep",
        title: "Momentos de Engastamento Perfeito (MEP)",
        formula_latex: "M_{ext} = \\mp \\frac{qL^2}{12} \\text{ ou } \\mp \\frac{Pab^2}{L^2}",
        substitution_latex: results?.barResults.map(b => `Vão ${b.barId}: [${formatNumberBR(b.mepA)}, ${formatNumberBR(b.mepB)}]`).join(' \\\\ '),
        result_latex: "M_{FIX} \\text{ calculados por trecho}",
        explanation: "Momentos teóricos de engaste total em cada nó antes da redistribuição de Hardy Cross.",
        norm_ref: "Teoria das Estruturas",
        status: "OK",
      },
      {
        id: "cross-k",
        title: "Fatores de Rigidez (K) e Distribuição (D)",
        formula_latex: "K = \\frac{EI}{L}, \\quad D_i = \\frac{K_i}{\\sum K}",
        substitution_latex: "Cálculo da rigidez relativa de cada barra convergindo nos nós.",
        result_latex: `n_{nos} = ${results?.nodes.length}`,
        explanation: "Os fatores de distribuição determinam quanto do momento desbalanceado é absorvido por cada barra engastada no nó.",
        norm_ref: "Método de Cross",
        status: "OK",
      },
      {
        id: "cross-convergence",
        title: "Convergência dos Momentos",
        formula_latex: "M_{desb,max} \\to 0",
        substitution_latex: `Iterações = ${results?.iterations.length ?? 0}`,
        result_latex: `M_{desb,max} = ${formatNumberBR(results?.finalMaxUnbalanced ?? 0)} kNm`,
        explanation: "A convergência é atingida quando o momento desbalanceado nos nós fica abaixo da tolerância de 0.01 kNm.",
        norm_ref: "Método de Hardy Cross",
        status: results?.converged ? "OK" : "ALERTA",
      },
      {
        id: "cross-equilibrium",
        title: "Equilíbrio de Reações Verticais",
        formula_latex: "\\sum V = 0 \\Rightarrow \\sum R_y - \\sum Q = 0",
        substitution_latex: `${formatNumberBR(beamLoadSummary.totalReaction)} - ${formatNumberBR(beamLoadSummary.totalLoad)}`,
        result_latex: `\\Delta = ${formatNumberBR(beamLoadSummary.residual)} kN`,
        explanation: "Verificação forense da integridade do solver através do somatório de forças verticais.",
        norm_ref: "Estática das Estruturas",
        status: Math.abs(beamLoadSummary.residual) < 0.1 ? "OK" : "ALERTA",
      },
      {
        id: "cross-design",
        title: "Dimensionamento Estimado (As)",
        formula_latex: "A_s \\approx \\frac{M_d}{0.8 \\cdot h \\cdot f_{yd}}",
        substitution_latex: `M_{max} = ${formatNumberBR(Math.max(...(results?.diagrams ?? []).map(d => Math.abs(d.moment ?? 0))))} kNm`,
        result_latex: `A_{s,est} \\approx ${((Math.max(...(results?.diagrams ?? []).map(d => Math.abs(d.moment ?? 0))) * 1.4) / (0.8 * (beamInput.sectionH/100) * 43.5)).toFixed(2)} cm^2`,
        explanation: "Estimativa pedagógica da área de aço necessária para o momento fletor máximo.",
        norm_ref: "NBR 6118",
        status: "INFO",
      }
    ],
  });

  const addSpan = () => {
    if (beamInput.spans.length >= 5) return;
    const nextId = `V${beamInput.spans.length + 1}`;
    setBeamInput(prev => ({
      ...prev,
      spans: [...prev.spans, { id: nextId, length: 4, inertiaCm4: prev.defaultInertiaCm4, loads: [] }],
      supports: [...prev.supports, "pin"]
    }));
  };

  const removeSpan = (index: number) => {
    if (beamInput.spans.length <= 1) return;
    const newSpans = [...beamInput.spans];
    newSpans.splice(index, 1);
    const newSupports = [...beamInput.supports];
    newSupports.splice(index + 1, 1);
    setBeamInput(prev => ({ ...prev, spans: newSpans, supports: newSupports }));
  };

  return (
    <ModuleContainer
      title="Viga Cross"
      subtitle="Análise didática de vigas contínuas pelo Método de Hardy Cross. Explore a convergência de momentos em sistemas hiperestáticos."
      icon={<Layout className="h-6 w-6 text-slate-900" />}
      theme="premium"
      solverType="Analytic (JS)"
      onExport={handleGeneratePDF}
      onBimExport={handleBimExport}
      auditResult={auditResult}
      optimizationSuggestion={optimizationSuggestion}
    >
      <div className="space-y-6">
        <div className="flex items-center justify-end mb-4">
          <button 
            onClick={handleRunAnalysis}
            className="flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-500 active:scale-95 transition-all uppercase tracking-widest text-[10px]"
          >
            <Play className="w-4 h-4 fill-current" /> Calcular Cross
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div className="lg:col-span-4 space-y-6">
          <div className="p-8 rounded-[2.5rem] border border-slate-200 bg-white shadow-2xl">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-600/10 rounded-2xl border border-blue-600/20">
                  <Share2 className="w-6 h-6 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-black text-[10px] uppercase tracking-[0.2em] text-slate-500">Parâmetros</h3>
                  <h4 className="text-sm font-black text-slate-900">Configuração da Viga</h4>
                </div>
              </div>
              <button 
                onClick={addSpan}
                className="flex items-center gap-2 px-4 py-2 bg-slate-50 border border-slate-200 text-slate-900 rounded-xl text-[9px] font-black hover:bg-slate-100 transition-all uppercase tracking-widest"
                title="Adicionar Vão à Direita"
              >
                <Plus className="w-3 h-3" />
                VÃO
                <ArrowRight className="w-3 h-3 text-blue-500" />
              </button>
            </div>

            <div className="space-y-6 mb-8 p-6 rounded-3xl bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-[9px] font-black uppercase text-blue-600 tracking-widest">Apoio Inicial e Seção</h4>
                <div className="flex items-center gap-3">
                  <span className="text-[9px] font-black uppercase text-slate-500 tracking-widest">Apoio A</span>
                  <select 
                    value={beamInput.supports[0]}
                    onChange={(e) => {
                      const newSupports = [...beamInput.supports];
                      newSupports[0] = e.target.value as SupportType;
                      setBeamInput(prev => ({ ...prev, supports: newSupports }));
                    }}
                    className="px-3 py-1.5 bg-white border border-slate-200 rounded-xl font-black text-[10px] text-slate-900 outline-none focus:border-blue-500/50 transition-all appearance-none cursor-pointer"
                  >
                    <option value="fixed">Engaste</option>
                    <option value="pin">Apoio</option>
                    <option value="free">Livre</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest ml-1">Base (b)</label>
                  <input 
                    type="number"
                    value={beamInput.sectionB}
                    onChange={(e) => {
                      const b = parseFloat(e.target.value) || 0;
                      const h = beamInput.sectionH || 50;
                      const newInertia = (b * Math.pow(h, 3)) / 12;
                      setBeamInput(prev => ({ 
                        ...prev, 
                        sectionB: b,
                        defaultInertiaCm4: newInertia,
                        spans: prev.spans.map(s => ({ ...s, inertiaCm4: newInertia }))
                      }));
                    }}
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-2xl font-mono text-slate-900 text-xs outline-none focus:border-blue-500/30 transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest ml-1">Altura (h)</label>
                  <input 
                    type="number"
                    value={beamInput.sectionH}
                    onChange={(e) => {
                      const h = parseFloat(e.target.value) || 0;
                      const b = beamInput.sectionB || 20;
                      const newInertia = (b * Math.pow(h, 3)) / 12;
                      setBeamInput(prev => ({ 
                        ...prev, 
                        sectionH: h,
                        defaultInertiaCm4: newInertia,
                        spans: prev.spans.map(s => ({ ...s, inertiaCm4: newInertia }))
                      }));
                    }}
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-2xl font-mono text-slate-900 text-xs outline-none focus:border-blue-500/30 transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest ml-1">FCK (MPa)</label>
                  <input 
                    type="number"
                    value={beamInput.fck}
                    onChange={(e) => {
                      const fck = parseFloat(e.target.value) || 0;
                      const newE = Math.round(0.85 * 5600 * Math.sqrt(fck) / 1000); 
                      setBeamInput(prev => ({ ...prev, fck: fck, eGPa: newE }));
                    }}
                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-2xl font-mono text-slate-900 text-xs outline-none focus:border-blue-500/30 transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <p className="text-[10px] font-black text-slate-400 italic tracking-widest uppercase text-center border-b border-slate-200 pb-4">
                Topologia de Vãos (Hardy Cross)
              </p>
              {beamInput.spans.map((span, idx) => (
                <div key={span.id} className="p-6 rounded-3xl bg-white border border-slate-200 space-y-4 group/span transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-600/20 text-[10px] font-black text-blue-600 border border-blue-600/30">{idx + 1}</span>
                      <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-700">Vão {span.id}</span>
                    </div>
                    {beamInput.spans.length > 1 && (
                      <button 
                        onClick={() => removeSpan(idx)} 
                        className="p-2 text-slate-300 hover:text-red-500 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest ml-1">L (m)</label>
                        <input 
                          type="number"
                          value={span.length}
                          onChange={(e) => {
                            const newSpans = [...beamInput.spans];
                            newSpans[idx].length = parseFloat(e.target.value) || 0;
                            setBeamInput(prev => ({ ...prev, spans: newSpans }));
                          }}
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl font-mono text-slate-900 text-xs outline-none focus:border-blue-500/30 transition-all"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest ml-1">Apoio Direita</label>
                        <select 
                          value={beamInput.supports[idx + 1]}
                          onChange={(e) => {
                            const newSupports = [...beamInput.supports];
                            newSupports[idx + 1] = e.target.value as SupportType;
                            setBeamInput(prev => ({ ...prev, supports: newSupports }));
                          }}
                          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl font-black text-slate-900 text-[10px] outline-none focus:border-blue-500/30 transition-all appearance-none cursor-pointer"
                        >
                          <option value="fixed">Engaste</option>
                          <option value="pin">Apoio</option>
                          <option value="free">Livre</option>
                        </select>
                      </div>
                    </div>

                    <div className="space-y-3 pt-4 border-t border-slate-200">
                      <div className="flex items-center justify-between">
                        <label className="text-[9px] font-black uppercase text-slate-500 tracking-widest">Cargas Estáticas</label>
                        <div className="flex gap-2">
                          <button 
                            onClick={() => {
                              const newSpans = [...beamInput.spans];
                              newSpans[idx].loads.push({ type: "udl", value: 10 });
                              setBeamInput(prev => ({ ...prev, spans: newSpans }));
                            }}
                            className="text-[8px] font-black px-3 py-1.5 bg-blue-600/10 text-blue-600 rounded-lg uppercase tracking-widest border border-blue-600/20 hover:bg-blue-600/20 transition-all"
                          >
                            + Q (UDL)
                          </button>
                          <button 
                            onClick={() => {
                              const newSpans = [...beamInput.spans];
                              newSpans[idx].loads.push({ type: "point", value: 50, position: span.length / 2 });
                              setBeamInput(prev => ({ ...prev, spans: newSpans }));
                            }}
                            className="text-[8px] font-black px-3 py-1.5 bg-blue-600/10 text-blue-600 rounded-lg uppercase tracking-widest border border-blue-600/20 hover:bg-blue-600/20 transition-all"
                          >
                            + P (POINT)
                          </button>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        {span.loads.map((load, lidx) => (
                          <div key={lidx} className="flex items-center gap-3 p-3 bg-slate-50 rounded-2xl border border-slate-200 shadow-inner">
                            <div className="flex-1 flex gap-3">
                              <div className="space-y-1">
                                <span className="text-[7px] font-black text-slate-400 uppercase tracking-widest block ml-1">Valor</span>
                                <input 
                                  type="number"
                                  value={load.value}
                                  placeholder="kN"
                                  onChange={(e) => {
                                    const newSpans = [...beamInput.spans];
                                    newSpans[idx].loads[lidx].value = parseFloat(e.target.value) || 0;
                                    setBeamInput(prev => ({ ...prev, spans: newSpans }));
                                  }}
                                  className="w-20 px-3 py-2 bg-white border border-slate-200 rounded-xl text-[10px] font-mono text-slate-900 outline-none focus:border-blue-500/30"
                                />
                              </div>
                              {load.type === "point" && (
                                <div className="space-y-1">
                                  <span className="text-[7px] font-black text-slate-400 uppercase tracking-widest block ml-1">Posição</span>
                                  <input 
                                    type="number"
                                    value={load.position}
                                    placeholder="m"
                                    onChange={(e) => {
                                      const newSpans = [...beamInput.spans];
                                      const targetLoad = newSpans[idx].loads[lidx];
                                      if (targetLoad.type === "point") {
                                        targetLoad.position = parseFloat(e.target.value) || 0;
                                      }
                                      setBeamInput(prev => ({ ...prev, spans: newSpans }));
                                    }}
                                    className="w-20 px-3 py-2 bg-white border border-slate-200 rounded-xl text-[10px] font-mono text-slate-900 outline-none focus:border-blue-500/30"
                                  />
                                </div>
                              )}
                            </div>
                            <div className="px-3 py-1 rounded-lg bg-blue-600/5 border border-blue-600/10">
                              <span className="text-[8px] font-black text-blue-500 uppercase tracking-widest">{load.type}</span>
                            </div>
                            <button 
                              onClick={() => {
                                const newSpans = [...beamInput.spans];
                                newSpans[idx].loads.splice(lidx, 1);
                                setBeamInput(prev => ({ ...prev, spans: newSpans }));
                              }}
                              className="p-2 text-slate-300 hover:text-red-500 transition-all"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 p-6 rounded-[2rem] bg-slate-900 text-white relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Info className="w-12 h-12" />
              </div>
              <div className="flex items-center gap-3 mb-3 relative z-10">
                <Info className="w-4 h-4 text-blue-400" />
                <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">Guia Técnico</h4>
              </div>
              <p className="text-[11px] font-medium leading-relaxed text-slate-300 relative z-10">
                O Solver utiliza o algoritmo de <b className="text-white">Hardy Cross</b> para convergência de momentos em apoios intermediários.
              </p>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 space-y-6">
          <div className="p-10 rounded-[2.5rem] border border-slate-200 bg-white/80 shadow-2xl min-h-[500px] flex flex-col relative">
            
            {!results ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                <div className="w-24 h-24 bg-slate-100 rounded-[2rem] border border-slate-200 flex items-center justify-center">
                  <Activity className="w-12 h-12 text-slate-300" />
                </div>
                <div>
                  <h3 className="font-black text-xl text-slate-900 tracking-tight">Telemetria em Standby</h3>
                  <p className="text-sm text-slate-500 max-w-sm mt-2 font-medium">Configure o modelo estrutural à esquerda e inicie o processamento.</p>
                </div>
              </div>
            ) : (
              <div className="space-y-10">
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-6 rounded-[2rem] bg-slate-50 border border-slate-200">
                    <div className="flex items-center gap-2 mb-2">
                      <RotateCcw className="w-3.5 h-3.5 text-blue-500" />
                      <p className="text-[10px] font-black uppercase text-slate-500 tracking-[0.2em]">Iterações</p>
                    </div>
                    <p className="text-3xl font-black text-slate-900 font-mono">{results.iterations.length}</p>
                  </div>
                  <div className="p-6 rounded-[2rem] bg-emerald-50 border border-emerald-100">
                    <div className="flex items-center gap-2 mb-2">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                      <p className="text-[10px] font-black uppercase text-emerald-600 tracking-[0.2em]">Status</p>
                    </div>
                    <p className="text-2xl font-black text-slate-900">{results.converged ? "CONVERGIDO" : "EM CURSO"}</p>
                  </div>
                  <div className="p-6 rounded-[2rem] bg-slate-900 border border-slate-800">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-3.5 h-3.5 text-blue-400" />
                      <p className="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Resíduo Máx.</p>
                    </div>
                    <p className="text-2xl font-black text-white font-mono">{formatNumberBR(results.finalMaxUnbalanced, 4)} <span className="text-[10px] text-slate-500">kNm</span></p>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-6 gap-4">
                    <div className="flex items-center gap-4">
                      <div className="p-2.5 bg-blue-600/10 rounded-xl border border-blue-600/20">
                        <ArrowUpDown className="w-5 h-5 text-blue-500" />
                      </div>
                      <h3 className="font-black text-lg text-slate-900 uppercase tracking-tight">Telemetria de Cargas</h3>
                    </div>
                  </div>

                  <div className="w-full overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white p-8">
                    <svg viewBox="0 0 1000 330" className="h-auto w-full overflow-visible">
                      <defs>
                        <marker id="loadArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
                        </marker>
                        <marker id="reactionArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                          <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
                        </marker>
                      </defs>

                      <line x1="90" y1="170" x2="910" y2="170" stroke="#94a3b8" strokeWidth="1" />

                      {(() => {
                        const totalLength = beamInput.spans.reduce((sum, span) => sum + span.length, 0);
                        const scaleX = 820 / totalLength;
                        
                        const allLoadValues = beamInput.spans.flatMap((span) => span.loads.map((load) => load.value));
                        const reactionValues = results.nodeReactions.map((reaction) => Math.abs(reaction.verticalReaction));
                        const maxValue = Math.max(1, ...allLoadValues, ...reactionValues);
                        
                        let xOffset = 90;

                        return (
                          <>
                            {beamInput.spans.map((span, spanIdx) => {
                              const spanX = xOffset;
                              const spanW = span.length * scaleX;
                              xOffset += spanW;

                              return (
                                <g key={`load-chart-span-${span.id}`}>
                                  {span.loads.filter((load) => load.type === "udl").map((load, loadIdx) => {
                                    const arrowHeight = 34 + (load.value / maxValue) * 48;
                                    const arrowCount = Math.max(3, Math.ceil(span.length * 2));
                                    return (
                                      <g key={`udl-${span.id}-${loadIdx}`}>
                                        <path
                                          d={`M ${spanX} ${170 - arrowHeight} L ${spanX + spanW} ${170 - arrowHeight}`}
                                          stroke="#ef4444"
                                          strokeWidth="1.5"
                                          strokeOpacity="0.8"
                                        />
                                        {Array.from({ length: arrowCount }).map((_, idx) => {
                                          const x = spanX + (idx * spanW) / Math.max(1, arrowCount - 1);
                                          return (
                                            <line
                                              key={`udl-arrow-${idx}`}
                                              x1={x}
                                              y1={170 - arrowHeight}
                                              x2={x}
                                              y2="155"
                                              stroke="#ef4444"
                                              strokeWidth="1.5"
                                              markerEnd="url(#loadArrow)"
                                            />
                                          );
                                        })}
                                        <text x={spanX + spanW / 2} y={155 - arrowHeight} textAnchor="middle" fontSize="10" fontWeight="900" fill="#ef4444" className="font-mono">
                                          q = {formatNumberBR(load.value)} kN/m
                                        </text>
                                      </g>
                                    );
                                  })}

                                  {span.loads.filter((load) => load.type === "point").map((load, loadIdx) => {
                                    const arrowHeight = 42 + (load.value / maxValue) * 58;
                                    const x = spanX + load.position * scaleX;
                                    return (
                                      <g key={`point-${span.id}-${loadIdx}`}>
                                        <line
                                          x1={x}
                                          y1={170 - arrowHeight}
                                          x2={x}
                                          y2="155"
                                          stroke="#ef4444"
                                          strokeWidth="2.5"
                                          markerEnd="url(#loadArrow)"
                                        />
                                        <text x={x} y={155 - arrowHeight} textAnchor="middle" fontSize="10" fontWeight="900" fill="#ef4444" className="font-mono">
                                          P = {formatNumberBR(load.value)} kN
                                        </text>
                                      </g>
                                    );
                                  })}

                                   <line x1={spanX} y1="232" x2={spanX + spanW} y2="232" stroke="#cbd5e1" strokeDasharray="4 4" />
                                  <text x={spanX + spanW / 2} y="252" textAnchor="middle" fontSize="10" fontWeight="900" fill="#94a3b8" className="uppercase tracking-widest">
                                    {span.id}
                                  </text>
                                </g>
                              );
                            })}

                            {results.nodeReactions.map((reaction, idx) => {
                              const x = 90 + beamInput.spans.slice(0, idx).reduce((sum, span) => sum + span.length, 0) * scaleX;
                              const arrowHeight = 38 + (Math.abs(reaction.verticalReaction) / maxValue) * 64;
                              const isDownward = reaction.verticalReaction < 0;
                              return (
                                <g key={`reaction-chart-${reaction.nodeId}`}>
                                  <line
                                    x1={x}
                                    y1={isDownward ? 186 : 250}
                                    x2={x}
                                    y2={isDownward ? 186 + arrowHeight : 250 - arrowHeight}
                                    stroke="#10b981"
                                    strokeWidth="2.5"
                                    markerEnd="url(#reactionArrow)"
                                  />
                                  <text x={x} y="294" textAnchor="middle" fontSize="10" fontWeight="900" fill="#10b981" className="font-mono">
                                    {reaction.nodeId}: {formatNumberBR(reaction.verticalReaction)} kN
                                  </text>
                                </g>
                              );
                            })}
                          </>
                        );
                      })()}
                    </svg>
                  </div>
                </div>

                {/* Reações de Apoio HUD */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
                        <Target className="w-5 h-5 text-emerald-500" />
                      </div>
                      <h3 className="font-black text-lg text-slate-900 uppercase tracking-tight">Reações de Equilíbrio</h3>
                    </div>
                    <div className="text-[9px] font-black px-4 py-1.5 bg-emerald-500/10 text-emerald-600 rounded-full border border-emerald-500/20 uppercase tracking-[0.2em]">
                      Status: Estável
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {results.nodeReactions.map((reac, idx) => (
                      <div key={reac.nodeId} className="p-5 rounded-[1.5rem] border border-slate-200 bg-white/5 backdrop-blur-sm shadow-inner transition-all hover:bg-white/10">
                        <p className="text-[8px] font-black uppercase text-slate-900/20 tracking-widest">Apoio {reac.nodeId}</p>
                        <p className="mt-2 text-xl font-black text-slate-900 font-mono">{formatNumberBR(reac.verticalReaction)} <span className="text-[10px] text-slate-900/20">kN</span></p>
                      </div>
                    ))}
                    <div className="p-5 rounded-[1.5rem] border border-blue-500/20 bg-blue-500/5 shadow-lg shadow-blue-500/5">
                      <p className="text-[8px] font-black uppercase text-blue-600 tracking-widest">ΣRy Total</p>
                      <p className="mt-2 text-xl font-black text-slate-900 font-mono">
                        {formatNumberBR(results.nodeReactions.reduce((s, r) => s + r.verticalReaction, 0))} <span className="text-[10px] text-blue-600">kN</span>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Memorial de Cálculo HUD */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="p-2.5 bg-blue-600/10 rounded-xl border border-blue-600/20">
                        <TableIcon className="w-5 h-5 text-blue-500" />
                      </div>
                      <h3 className="font-black text-lg text-slate-900 uppercase tracking-tight">Memorial Hardy Cross</h3>
                    </div>
                    <button 
                      onClick={handleGeneratePDF}
                      disabled={generatingPDF}
                      className={cn(
                        "flex items-center gap-2 px-6 py-2.5 rounded-2xl text-[10px] font-black transition-all uppercase tracking-widest",
                        generatingPDF 
                          ? "bg-white/5 text-slate-900/20 cursor-not-allowed" 
                          : "bg-white text-black hover:bg-blue-50 shadow-xl"
                      )}
                    >
                      {generatingPDF ? (
                        <>
                          <Activity className="w-3.5 h-3.5 animate-spin" /> Gerando...
                        </>
                      ) : (
                        <>
                          <Printer className="w-3.5 h-3.5" /> Abrir Memorial HTML
                        </>
                      )}
                    </button>
                  </div>
                  
                  <div className="overflow-hidden rounded-[2.5rem] border border-slate-200 bg-white/80 shadow-inner">
                    <table className="w-full text-left text-[10px] font-bold">
                      <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                        <tr>
                          <th className="px-6 py-4 uppercase tracking-[0.2em]">Propriedade</th>
                          {results.barResults.map(b => (
                            <th key={b.barId} className="px-6 py-4 uppercase tracking-[0.2em] text-center" colSpan={2}>Vão {b.barId}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        <tr>
                          <td className="px-6 py-4 text-slate-500 uppercase tracking-widest">L (m)</td>
                          {beamInput.spans.map(s => (
                            <td key={`${s.id}-L`} className="px-2 py-4 text-center border-l border-slate-200 text-slate-900 font-mono" colSpan={2}>{s.length}</td>
                          ))}
                        </tr>
                        <tr className="bg-white/[0.02]">
                          <td className="px-6 py-4 text-slate-500 uppercase tracking-widest">Inércia (cm⁴)</td>
                          {beamInput.spans.map(s => (
                            <td key={`${s.id}-I`} className="px-2 py-4 text-center border-l border-slate-200 text-slate-900 font-mono" colSpan={2}>{s.inertiaCm4}</td>
                          ))}
                        </tr>
                        <tr className="bg-blue-500/5">
                          <td className="px-6 py-4 text-blue-600 font-black border-r border-slate-200 uppercase tracking-widest">MEP (Engaste)</td>
                          {results.barResults.map(b => (
                            <React.Fragment key={`${b.barId}-mep`}>
                              <td className="px-2 py-4 text-center text-blue-600 font-mono">{formatNumberBR(b.mepA)}</td>
                              <td className="px-2 py-4 text-center border-r border-slate-200 text-blue-600 font-mono">{formatNumberBR(b.mepB)}</td>
                            </React.Fragment>
                          ))}
                        </tr>
                        <tr className="bg-white text-black">
                          <td className="px-6 py-5 font-black border-r border-black/10 uppercase tracking-[0.2em]">MOMENTO FINAL</td>
                          {results.barResults.map(b => (
                            <React.Fragment key={`${b.barId}-final`}>
                              <td className="px-2 py-5 text-center font-mono">{formatNumberBR(b.finalA)}</td>
                              <td className="px-2 py-5 text-center border-r border-black/10 font-black font-mono">{formatNumberBR(b.finalB)}</td>
                            </React.Fragment>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Esquema Estático Premium (SVG) */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Layout className="w-5 h-5 text-indigo-600" />
                    <h3 className="font-black text-xl text-slate-900 uppercase tracking-tight">Esquema Estático</h3>
                  </div>
                  <div className="w-full bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm">
                    <svg viewBox="0 0 1000 250" className="w-full h-auto overflow-visible">
                      <defs>
                        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
                        </marker>
                      </defs>

                      {/* Viga Original */}
                      <line x1="100" y1="120" x2="900" y2="120" stroke="#1e293b" strokeWidth="3" strokeLinecap="round" />

                      {/* Linha Elástica (Deformada) */}
                      {results && results.diagrams && (
                        <path
                          d={`M 100 120 ${results.diagrams.map(p => {
                            const totalLength = beamInput.spans.reduce((s, b) => s + b.length, 0);
                            const scaleX = 800 / totalLength;
                            const x = 100 + p.xGlobal * scaleX;
                            const y = 120 + (p.deflection || 0) * 2; // Fator de escala para visibilidade
                            return `L ${x} ${y}`;
                          }).join(' ')}`}
                          fill="none"
                          stroke="#3b82f6"
                          strokeWidth="2"
                          strokeDasharray="4 2"
                          opacity="0.6"
                        />
                      )}

                      {/* Conteúdo por Vão */}
                      {(() => {
                        const totalLength = beamInput.spans.reduce((s, b) => s + b.length, 0);
                        let currentX = 100;
                        const scale = 800 / totalLength;

                        return beamInput.spans.map((span, idx) => {
                          const spanWidth = span.length * scale;
                          const startX = currentX;
                          currentX += spanWidth;

                          return (
                            <g key={`svg-span-${idx}`}>
                              {/* Carga Distribuída */}
                              {span.loads.some(l => l.type === "udl") && (
                                <g>
                                  <path 
                                    d={`M ${startX} 80 L ${startX} 50 L ${startX + spanWidth} 50 L ${startX + spanWidth} 80`} 
                                    fill="none" 
                                    stroke="#ef4444" 
                                    strokeWidth="1" 
                                  />
                                  {Array.from({ length: Math.ceil(span.length * 2) + 1 }).map((_, i) => {
                                    const arrowX = startX + (i * spanWidth) / (Math.ceil(span.length * 2));
                                    return (
                                      <line 
                                        key={i} 
                                        x1={arrowX} y1="50" x2={arrowX} y2="75" 
                                        stroke="#ef4444" strokeWidth="1" markerEnd="url(#arrow)" 
                                      />
                                    );
                                  })}
                                  <text 
                                    x={startX + spanWidth/2} y="40" 
                                    textAnchor="middle" fontSize="12" fontWeight="900" fill="#ef4444"
                                  >
                                    {span.loads.find(l => l.type === "udl")?.value} kN/m
                                  </text>
                                </g>
                              )}

                              {/* Cargas Pontuais */}
                              {span.loads.filter(l => l.type === "point").map((load, lidx) => (
                                <g key={lidx}>
                                  <line 
                                    x1={startX + load.position * scale} y1="20" 
                                    x2={startX + load.position * scale} y2="110" 
                                    stroke="#ef4444" strokeWidth="2" markerEnd="url(#arrow)" 
                                  />
                                  <text 
                                    x={startX + load.position * scale} y="15" 
                                    textAnchor="middle" fontSize="12" fontWeight="900" fill="#ef4444"
                                  >
                                    {load.value} kN
                                  </text>
                                </g>
                              ))}

                              {/* Linha de Cota Inferior */}
                              <g>
                                <line x1={startX} y1="200" x2={startX + spanWidth} y2="200" stroke="#cbd5e1" strokeDasharray="4 4" />
                                <line x1={startX} y1="195" x2={startX} y2="205" stroke="#cbd5e1" />
                                <line x1={startX + spanWidth} y1="195" x2={startX + spanWidth} y2="205" stroke="#cbd5e1" />
                                <text x={startX + spanWidth/2} y="220" textAnchor="middle" fontSize="12" fontWeight="900" fill="#64748b">{span.length} m</text>
                              </g>
                            </g>
                          );
                        });
                      })()}

                      {/* Apoios */}
                      {(() => {
                        const totalLength = beamInput.spans.reduce((s, b) => s + b.length, 0);
                        let currentXOffset = 100;
                        const scaleOffset = 800 / totalLength;

                        return beamInput.supports.map((sup, idx) => {
                          const x = currentXOffset;
                          if (idx < beamInput.spans.length) currentXOffset += beamInput.spans[idx].length * scaleOffset;
                          
                          const label = String.fromCharCode(65 + idx);
                          const reaction = results?.nodeReactions?.find(r => r.nodeId === `N${idx + 1}`);

                          return (
                            <g key={`svg-sup-${idx}`}>
                              {sup === "pin" ? (
                                <g transform={`translate(${x-15}, 125)`}>
                                  <path d="M 15 0 L 0 25 L 30 25 Z" fill="none" stroke="#475569" strokeWidth="2" />
                                  <circle cx="15" cy="12" r="3" fill="white" stroke="#475569" strokeWidth="1.5" />
                                </g>
                              ) : sup === "fixed" ? (
                                <rect x={x-10} y="122" width="20" height="5" fill="#1e293b" />
                              ) : null}
                              <text x={x} y="170" textAnchor="middle" fontSize="14" fontWeight="900" fill="#94a3b8">{label}</text>
                              {reaction && (
                                <text x={x} y="185" textAnchor="middle" fontSize="12" fontWeight="900" fill="#10b981">
                                  {formatNumberBR(reaction.verticalReaction)} kN
                                </text>
                              )}
                            </g>
                          );
                        });
                      })()}
                    </svg>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-8">
                  {/* Diagrama de Momentos */}
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Activity className="w-5 h-5 text-orange-600" />
                      <h3 className="font-black text-lg text-slate-900 uppercase">DMF (kNm)</h3>
                    </div>
                    <div className="h-[350px] w-full rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={results.diagrams}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="xGlobal" hide />
                          <YAxis reversed fontSize={9} fontWeight={700} axisLine={false} tickLine={false} />
                          <Tooltip 
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                            formatter={(value) => [`${formatNumberBR(Number(value ?? 0))} kNm`, "Momento"]}
                          />
                          <Area type="monotone" dataKey="moment" stroke="#c2410c" fill="#ffedd5" strokeWidth={2} />
                          <ReferenceLine y={0} stroke="#cbd5e1" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Diagrama de Cortantes */}
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <ArrowRightLeft className="w-5 h-5 text-emerald-600" />
                      <h3 className="font-black text-lg text-slate-900 uppercase">DEC (kN)</h3>
                    </div>
                    <div className="h-[350px] w-full rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={results.diagrams}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="xGlobal" hide />
                          <YAxis fontSize={9} fontWeight={700} axisLine={false} tickLine={false} />
                          <Tooltip 
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                            formatter={(value) => [`${formatNumberBR(Number(value ?? 0))} kN`, "Cortante"]}
                          />
                          <Area type="stepAfter" dataKey="shear" stroke="#059669" fill="#ecfdf5" strokeWidth={2} />
                          <ReferenceLine y={0} stroke="#cbd5e1" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Diagrama de Deflexão */}
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Maximize2 className="w-5 h-5 text-blue-600" />
                      <h3 className="font-black text-lg text-slate-900 uppercase">Flecha (mm)</h3>
                    </div>
                    <div className="h-[350px] w-full rounded-2xl bg-white border border-slate-100 p-4 shadow-sm">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={results.diagrams}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="xGlobal" hide />
                          <YAxis reversed fontSize={9} fontWeight={700} axisLine={false} tickLine={false} />
                          <Tooltip 
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                            formatter={(value) => [`${formatNumberBR(Number(value ?? 0))} mm`, "Flecha"]}
                          />
                          <Area type="monotone" dataKey="deflection" stroke="#2563eb" fill="#dbeafe" strokeWidth={2} />
                          <ReferenceLine y={0} stroke="#cbd5e1" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* Ph.D. Structural Auditor (Fase 4) */}
                {auditResult && (
                  <div className="mt-8 overflow-hidden rounded-[32px] border border-blue-100 bg-blue-50/30 p-8 backdrop-blur-xl transition-all hover:shadow-2xl hover:shadow-blue-500/10">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600 shadow-lg shadow-blue-600/40">
                          <ShieldCheck className="h-8 w-8 text-white" />
                        </div>
                        <div>
                          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">M5-PhD Intelligence</p>
                          <h3 className="text-2xl font-black text-slate-900">Auditoria Estrutural Ph.D.</h3>
                        </div>
                      </div>
                      <div className={cn(
                        "rounded-full px-6 py-2 text-sm font-black uppercase tracking-tighter shadow-sm",
                        auditResult.verdict === "APROVADO COM RESSALVAS" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                      )}>
                        {auditResult.verdict}
                      </div>
                    </div>

                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="space-y-4">
                        <p className="text-xs font-black uppercase tracking-widest text-slate-600">Diagnóstico Técnico</p>
                        <div className="space-y-3">
                          {auditResult.findings.map((f: string, i: number) => (
                            <div key={i} className="flex gap-3 text-sm font-bold text-slate-700 leading-relaxed bg-white/50 p-3 rounded-xl border border-white/60">
                              <span className="shrink-0">•</span>
                              <p>{f}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-4">
                        <p className="text-xs font-black uppercase tracking-widest text-slate-600">Recomendações PhD</p>
                        <div className="space-y-3">
                          {auditResult.recommendations.map((r: string, i: number) => (
                            <div key={i} className="flex gap-3 text-sm font-bold text-blue-800 leading-relaxed bg-blue-100/50 p-3 rounded-xl border border-blue-200/40">
                              <ChevronRight className="h-4 w-4 shrink-0 mt-0.5" />
                              <p>{r}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Memorial de Flechas */}
                <div className="mt-8">
                  <div className="flex items-center gap-2 mb-4">
                    <Maximize2 className="w-5 h-5 text-blue-600" />
                    <h3 className="font-black text-xl text-slate-900 uppercase tracking-tight">Verificação de Flechas (NBR 6118)</h3>
                  </div>
                  <div className="w-full bg-white rounded-[2rem] border border-slate-200 p-8 shadow-sm overflow-x-auto">
                    <table className="w-full text-sm text-left border-collapse">
                      <thead>
                        <tr className="bg-slate-50">
                          <th className="px-4 py-3 border-b font-black text-slate-500 uppercase">Vão</th>
                          <th className="px-4 py-3 border-b font-black text-slate-500 uppercase">Comprimento</th>
                          <th className="px-4 py-3 border-b font-black text-slate-500 uppercase">Flecha Máx (mm)</th>
                          <th className="px-4 py-3 border-b font-black text-slate-500 uppercase">Limite (L/250)</th>
                          <th className="px-4 py-3 border-b font-black text-slate-500 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {beamInput.spans.map((span) => {
                          const spanPoints = results.diagrams.filter(p => p.spanId === span.id);
                          const maxDeflection = Math.max(...spanPoints.map(p => Math.abs(p.deflection || 0)));
                          const limit = (span.length * 1000) / 250;
                          const ok = maxDeflection <= limit;

                          return (
                            <tr key={span.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50 transition-colors">
                              <td className="px-4 py-4 font-black text-slate-900">{span.id}</td>
                              <td className="px-4 py-4">{formatNumberBR(span.length)} m</td>
                              <td className="px-4 py-4 font-bold text-blue-600">{formatNumberBR(maxDeflection)} mm</td>
                              <td className="px-4 py-4 text-slate-500">{formatNumberBR(limit)} mm</td>
                              <td className="px-4 py-4">
                                <span className={`px-3 py-1 rounded-full text-xs font-black uppercase ${ok ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                                  {ok ? 'DENTRO DO LIMITE' : 'EXCESSIVA'}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </div>

      {showHtmlMemorial && results && (
        <MemorialHtmlView 
          blackboard={buildHtmlMemorial()}
          onClose={() => setShowHtmlMemorial(false)} 
          onDownloadPdf={() => window.print()}
        />
      )}
    </ModuleContainer>
  );
}
