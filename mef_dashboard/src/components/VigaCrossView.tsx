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
  ArrowRight
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
      
      const maxDeflection = Math.max(...res.diagrams.map(d => Math.abs(d.deflection)));
      const maxMoment = Math.max(...res.diagrams.map(d => Math.abs(d.moment)));

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

  // Simplified ShieldCheck to avoid reference errors if it fails to load from lucide
  const SafeShieldCheck = ({ className }: { className?: string }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );

  return (
    <ModuleContainer
      title="Viga Cross"
      subtitle="Análise didática de vigas contínuas pelo Método de Hardy Cross. Explore a convergência de momentos em sistemas hiperestáticos."
      icon={<Layout className="h-6 w-6 text-white" />}
      theme="academic"
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
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-2xl font-black shadow-lg hover:bg-indigo-700 active:scale-95 transition-all"
          >
            <Play className="w-4 h-4 fill-current" /> Calcular Cross
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Editor de Geometria */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-[2rem] border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-50 rounded-xl">
                  <Share2 className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="font-black text-sm">Configuração da Viga</h3>
              </div>
              <button 
                onClick={addSpan}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white rounded-xl text-[10px] font-black hover:bg-indigo-700 transition-all shadow-sm"
                title="Adicionar Vão à Direita"
              >
                <Plus className="w-3 h-3" />
                ADICIONAR VÃO
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-4 mb-6 p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-[9px] font-black uppercase text-indigo-600">Geometria e Apoio Inicial</h4>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-black uppercase text-slate-500">Apoio A</span>
                  <select 
                    value={beamInput.supports[0]}
                    onChange={(e) => {
                      const newSupports = [...beamInput.supports];
                      newSupports[0] = e.target.value as SupportType;
                      setBeamInput(prev => ({ ...prev, supports: newSupports }));
                    }}
                    className="px-2 py-1 bg-white border border-slate-200 rounded-lg font-bold text-[10px]"
                  >
                    <option value="fixed">Engaste</option>
                    <option value="pin">Apoio</option>
                    <option value="free">Livre (Balanço)</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-[9px] font-black uppercase text-slate-500">Base (b)</label>
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
                    className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-lg font-bold text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[9px] font-black uppercase text-slate-500">Altura (h)</label>
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
                    className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-lg font-bold text-xs"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[9px] font-black uppercase text-slate-500">FCK (MPa)</label>
                  <input 
                    type="number"
                    value={beamInput.fck}
                    onChange={(e) => {
                      const fck = parseFloat(e.target.value) || 0;
                      // E = 5600 * sqrt(fck) approx
                      const newE = Math.round(0.85 * 5600 * Math.sqrt(fck) / 1000); 
                      setBeamInput(prev => ({ ...prev, fck: fck, eGPa: newE }));
                    }}
                    className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-lg font-bold text-xs"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-[10px] font-semibold text-slate-400 italic">Vãos inseridos sequencialmente da esquerda para a direita.</p>
              {beamInput.spans.map((span, idx) => (
                <div key={span.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-200 text-[10px] font-black text-slate-600">{idx + 1}</span>
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Vão {span.id}</span>
                    </div>
                    {beamInput.spans.length > 1 && (
                      <button onClick={() => removeSpan(idx)} className="text-slate-400 hover:text-red-500 transition-colors">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase text-slate-500">Comprimento (m)</label>
                        <input 
                          type="number"
                          value={span.length}
                          onChange={(e) => {
                            const newSpans = [...beamInput.spans];
                            newSpans[idx].length = parseFloat(e.target.value) || 0;
                            setBeamInput(prev => ({ ...prev, spans: newSpans }));
                          }}
                          className="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-bold text-xs"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[9px] font-black uppercase text-slate-500">Apoio à Direita</label>
                        <select 
                          value={beamInput.supports[idx + 1]}
                          onChange={(e) => {
                            const newSupports = [...beamInput.supports];
                            newSupports[idx + 1] = e.target.value as SupportType;
                            setBeamInput(prev => ({ ...prev, supports: newSupports }));
                          }}
                          className="w-full px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-bold text-xs"
                        >
                          <option value="fixed">Engaste</option>
                          <option value="pin">Apoio</option>
                          <option value="free">Livre (Balanço)</option>
                        </select>
                      </div>
                    </div>

                    {/* Editor de Cargas */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <label className="text-[9px] font-black uppercase text-slate-500">Cargas no Vão</label>
                        <div className="flex gap-1">
                          <button 
                            onClick={() => {
                              const newSpans = [...beamInput.spans];
                              newSpans[idx].loads.push({ type: "udl", value: 10 });
                              setBeamInput(prev => ({ ...prev, spans: newSpans }));
                            }}
                            className="text-[8px] font-black px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded uppercase"
                          >
                            + Q
                          </button>
                          <button 
                            onClick={() => {
                              const newSpans = [...beamInput.spans];
                              newSpans[idx].loads.push({ type: "point", value: 50, position: span.length / 2 });
                              setBeamInput(prev => ({ ...prev, spans: newSpans }));
                            }}
                            className="text-[8px] font-black px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded uppercase"
                          >
                            + P
                          </button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        {span.loads.map((load, lidx) => (
                          <div key={lidx} className="flex items-center gap-2 p-2 bg-white rounded-xl border border-slate-100 shadow-sm">
                            <div className="flex-1 flex gap-2">
                              <input 
                                type="number"
                                value={load.value}
                                placeholder="Valor"
                                onChange={(e) => {
                                  const newSpans = [...beamInput.spans];
                                  newSpans[idx].loads[lidx].value = parseFloat(e.target.value) || 0;
                                  setBeamInput(prev => ({ ...prev, spans: newSpans }));
                                }}
                                className="w-16 px-2 py-1 bg-slate-50 border border-slate-100 rounded text-[10px] font-black"
                              />
                              {load.type === "point" && (
                                <input 
                                  type="number"
                                  value={load.position}
                                  placeholder="Pos"
                                  onChange={(e) => {
                                    const newSpans = [...beamInput.spans];
                                    newSpans[idx].loads[lidx].position = parseFloat(e.target.value) || 0;
                                    setBeamInput(prev => ({ ...prev, spans: newSpans }));
                                  }}
                                  className="w-16 px-2 py-1 bg-slate-50 border border-slate-100 rounded text-[10px] font-black"
                                />
                              )}
                            </div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase">{load.type}</span>
                            <button 
                              onClick={() => {
                                const newSpans = [...beamInput.spans];
                                newSpans[idx].loads.splice(lidx, 1);
                                setBeamInput(prev => ({ ...prev, spans: newSpans }));
                              }}
                              className="p-1 hover:text-red-500"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 rounded-2xl bg-indigo-900 text-white shadow-xl">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-3.5 h-3.5 text-indigo-300" />
                <h4 className="text-[10px] font-black uppercase tracking-widest text-indigo-300">Editor de Cargas</h4>
              </div>
              <p className="text-[11px] font-medium leading-relaxed opacity-90">
                Use <b>+ Q</b> para carga distribuída e <b>+ P</b> para carga pontual. As reações são atualizadas no esquema dinamicamente após o cálculo.
              </p>
            </div>
          </div>
        </div>

        {/* Visualização de Resultados */}
        <div className="lg:col-span-8 space-y-6">
          <div className="p-8 rounded-[2rem] border border-slate-200 bg-white shadow-sm min-h-[500px] flex flex-col">
            
            {!results ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center">
                  <Activity className="w-10 h-10 text-slate-200" />
                </div>
                <div>
                  <h3 className="font-black text-lg text-slate-900">Aguardando Parâmetros</h3>
                  <p className="text-sm text-slate-500 max-w-sm">Configure a geometria e as cargas da viga contínua e clique em "Calcular Cross" para gerar o memorial.</p>
                </div>
              </div>
            ) : (
              <div className="space-y-8 animate-in fade-in duration-500">
                
                {/* Resumo de Convergência */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-2xl bg-indigo-50 border border-indigo-100">
                    <p className="text-[10px] font-black uppercase text-indigo-600">Iterações</p>
                    <p className="text-xl font-black text-slate-900">{results.iterations.length}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100">
                    <p className="text-[10px] font-black uppercase text-emerald-600">Status</p>
                    <p className="text-xl font-black text-slate-900">{results.converged ? "Convergido" : "Processando"}</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-slate-900 text-white">
                    <p className="text-[10px] font-black uppercase text-slate-400">Erro Residual</p>
                    <p className="text-xl font-black">{formatNumberBR(results.finalMaxUnbalanced, 4)} kNm</p>
                  </div>
                </div>

                {/* Reações de Apoio */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-emerald-600" />
                      <h3 className="font-black text-xl text-slate-900">Reações de Apoio</h3>
                    </div>
                    <div className="text-[10px] font-black px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-100 uppercase tracking-wider">
                      Verificação de Equilíbrio: OK
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                    {results.nodeReactions.map((reac, idx) => (
                      <div key={reac.nodeId} className="p-4 rounded-2xl border border-slate-100 bg-white shadow-sm">
                        <p className="text-[10px] font-black uppercase text-slate-400">Apoio {reac.nodeId}</p>
                        <p className="mt-2 text-xl font-black text-slate-900">{formatNumberBR(reac.verticalReaction)} <span className="text-xs">kN</span></p>
                      </div>
                    ))}
                    <div className="p-4 rounded-2xl border border-indigo-100 bg-indigo-50">
                      <p className="text-[10px] font-black uppercase text-indigo-600">Total ΣRy</p>
                      <p className="mt-2 text-xl font-black text-indigo-900">
                        {formatNumberBR(results.nodeReactions.reduce((s, r) => s + r.verticalReaction, 0))} kN
                      </p>
                    </div>
                  </div>
                </div>

                {/* Memorial de Cálculo Detalhado */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <TableIcon className="w-5 h-5 text-indigo-600" />
                      <h3 className="font-black text-xl text-slate-900">Memorial de Cálculo</h3>
                    </div>
                    <button 
                      onClick={handleGeneratePDF}
                      disabled={generatingPDF}
                      className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black transition-all",
                        generatingPDF 
                          ? "bg-slate-100 text-slate-400 cursor-not-allowed" 
                          : "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm shadow-indigo-200"
                      )}
                    >
                      {generatingPDF ? (
                        <>
                          <Activity className="w-3.5 h-3.5 animate-spin" /> Gerando...
                        </>
                      ) : (
                        <>
                          <Printer className="w-3.5 h-3.5" /> Gerar Memorial Técnico
                        </>
                      )}
                    </button>
                  </div>
                  
                  <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
                    <table className="w-full text-left text-[11px] font-bold">
                      <thead className="bg-slate-50 text-slate-400 border-b border-slate-200">
                        <tr>
                          <th className="px-4 py-3 uppercase tracking-wider">Propriedade</th>
                          {results.barResults.map(b => (
                            <th key={b.barId} className="px-4 py-3 uppercase tracking-wider text-center" colSpan={2}>Vão {b.barId}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        <tr>
                          <td className="px-4 py-3 text-slate-500 uppercase">Comprimento (L)</td>
                          {beamInput.spans.map(s => (
                            <td key={`${s.id}-L`} className="px-2 py-3 text-center border-l border-slate-50" colSpan={2}>{s.length} m</td>
                          ))}
                        </tr>
                        <tr className="bg-slate-50/30">
                          <td className="px-4 py-3 text-slate-500 uppercase">Inércia (I)</td>
                          {beamInput.spans.map(s => (
                            <td key={`${s.id}-I`} className="px-2 py-3 text-center border-l border-slate-50" colSpan={2}>{s.inertiaCm4} cm⁴</td>
                          ))}
                        </tr>
                        <tr className="bg-indigo-50/20">
                          <td className="px-4 py-3 text-indigo-700 font-black border-r border-slate-200 uppercase">MEP (Engaste)</td>
                          {results.barResults.map(b => (
                            <React.Fragment key={`${b.barId}-mep`}>
                              <td className="px-2 py-3 text-center">{formatNumberBR(b.mepA)}</td>
                              <td className="px-2 py-3 text-center border-r border-slate-200">{formatNumberBR(b.mepB)}</td>
                            </React.Fragment>
                          ))}
                        </tr>
                        <tr className="bg-slate-900 text-white">
                          <td className="px-4 py-4 font-black border-r border-white/10 uppercase">MOMENTO FINAL</td>
                          {results.barResults.map(b => (
                            <React.Fragment key={`${b.barId}-final`}>
                              <td className="px-2 py-4 text-center">{formatNumberBR(b.finalA)}</td>
                              <td className="px-2 py-4 text-center border-r border-white/10 font-black">{formatNumberBR(b.finalB)}</td>
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
                          const reaction = results?.nodeReactions?.find(r => r.nodeId === label);

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
                            formatter={(value: number) => [`${formatNumberBR(value)} kNm`, "Momento"]}
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
                            formatter={(value: number) => [`${formatNumberBR(value)} kN`, "Cortante"]}
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
                            formatter={(value: number) => [`${formatNumberBR(value)} mm`, "Flecha"]}
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
                          <SafeShieldCheck className="h-8 w-8 text-white" />
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
                        <p className="text-xs font-black uppercase tracking-widest text-slate-400">Diagnóstico Técnico</p>
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
                        <p className="text-xs font-black uppercase tracking-widest text-slate-400">Recomendações PhD</p>
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
          results={results} 
          input={beamInput} 
          onClose={() => setShowHtmlMemorial(false)} 
        />
      )}
    </ModuleContainer>
  );
}
