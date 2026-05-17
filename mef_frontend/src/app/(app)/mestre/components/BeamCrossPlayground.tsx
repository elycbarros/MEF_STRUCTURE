import { useMemo, useState, useEffect } from 'react';
import { Activity, Calculator, Plus, Share2, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useMestreStore } from '@/lib/store-mestre';
import { solveCross } from '@/lib/vigacross/engine';
import type { BeamInput, CrossSolveResult, SpanLoad, SupportType } from '@/lib/vigacross/types';
import type { MestreStep } from '@/lib/mestre-types';
import { MestreDiagram } from './MestreDiagram';
import { StructuralDiagram } from './StructuralDiagram';

const SUPPORT_LABELS: Record<string, string> = {
  fixed: 'Engaste',
  pin: 'Apoio Fixo',
  roller: 'Apoio Móvel',
  free: 'Livre',
};

const defaultBeamInput: BeamInput = {
  spans: [
    { id: 'V1', length: 4, inertiaCm4: 208333, loads: [{ type: 'udl', value: 20 }] },
    { id: 'V2', length: 5, inertiaCm4: 208333, loads: [{ type: 'point', value: 50, position: 2.5 }] },
  ],
  supports: ['fixed', 'pin', 'fixed'],
  eGPa: 25,
  defaultInertiaCm4: 208333,
  sectionB: 20,
  sectionH: 50,
  fck: 25,
  tolerance: 0.01,
  maxIterations: 50,
};

function asFiniteNumber(value: unknown, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function fmt(value: unknown, precision = 2) {
  return asFiniteNumber(value).toLocaleString('pt-BR', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });
}

function inertiaCm4(bCm: number, hCm: number) {
  const inertia = (asFiniteNumber(bCm) * Math.pow(asFiniteNumber(hCm), 3)) / 12;
  return Number.isFinite(inertia) ? inertia : 0;
}

function buildCrossSteps(input: BeamInput, results: CrossSolveResult): MestreStep[] {
  const totalLoad = input.spans.reduce(
    (sum, span) => sum + span.loads.reduce((spanSum, load) => spanSum + (load.type === 'udl' ? load.value * span.length : load.value), 0),
    0,
  );
  const totalReaction = results.nodeReactions.reduce((sum, reaction) => sum + reaction.verticalReaction, 0);
  const maxShear = Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.shear))));
  const maxMoment = Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.moment))));
  const maxDeflection = Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.deflection))));

  return [
    {
      id: 'cross-geom',
      title: 'Propriedades da Seção e Materiais',
      formula: String.raw`I = \frac{b h^3}{12}, \quad K = \frac{EI}{L}`,
      substitution: String.raw`b = ${input.sectionB}\,cm, \quad h = ${input.sectionH}\,cm, \quad E = ${input.eGPa}\,GPa`,
      result: String.raw`I = ${fmt(input.defaultInertiaCm4, 0)}\,cm^4`,
      explanation: 'Define a rigidez relativa de cada vão para distribuição dos momentos pelo método de Hardy Cross.',
      norm: 'Teoria das Estruturas',
    },
    {
      id: 'cross-fixed-end',
      title: 'Momentos de Engastamento Perfeito',
      formula: String.raw`M_{EP} = \mp\frac{qL^2}{12} \quad \text{ou} \quad M_{EP} = \mp\frac{Pab^2}{L^2}`,
      substitution: results.barResults.map((bar) => `${bar.barId}: ${fmt(bar.mepA)} / ${fmt(bar.mepB)} kNm`).join(' ; '),
      result: String.raw`M_{EP}\ \text{calculado para cada extremidade}`,
      explanation: 'Parte-se dos momentos de engastamento perfeito antes das liberações e redistribuições nos nós.',
      norm: 'Método de Hardy Cross',
    },
    {
      id: 'cross-convergence',
      title: 'Convergência por Distribuição de Momentos',
      formula: String.raw`M_{desb,max} \to 0`,
      substitution: String.raw`n = ${results.iterations.length}, \quad tolerancia = ${input.tolerance}`,
      result: String.raw`M_{desb,max} = ${fmt(results.finalMaxUnbalanced, 4)}\,kNm`,
      explanation: 'Os momentos desbalanceados são distribuídos conforme a rigidez relativa de cada barra conectada ao nó.',
      norm: 'Método de Hardy Cross',
    },
    {
      id: 'cross-equilibrium',
      title: 'Equilíbrio de Reações Verticais',
      formula: String.raw`\sum R_y - \sum Q = 0`,
      substitution: String.raw`\sum R_y = ${fmt(totalReaction)}\,kN, \quad \sum Q = ${fmt(totalLoad)}\,kN`,
      result: String.raw`\Delta = ${fmt(totalReaction - totalLoad, 4)}\,kN`,
      explanation: 'Verifica a consistência estática global após a redistribuição dos momentos finais.',
      norm: 'Estática das Estruturas',
    },
    {
      id: 'cross-analytical-formulas',
      title: 'Equações Analíticas por Trecho (Mestre)',
      formula: String.raw`V(x) = V_{iso} + \frac{M_B + M_A}{L}, \quad M(x) = M_A + (V_0)x - \frac{qx^2}{2}`,
      substitution: 'Superposição de efeitos isostáticos e momentos de apoio',
      result: String.raw`\left\{ \begin{array}{l} ${results.barResults.map(bar => {
        const q = input.spans.find(s => s.id === bar.barId)?.loads.find(l => l.type === 'udl')?.value || 0;
        const L = input.spans.find(s => s.id === bar.barId)?.length ?? 0;
        const ma = bar.finalA;
        const mb = bar.finalB;
        const v0 = (q * L / 2) + (mb + ma) / L;
        return String.raw`\text{Trecho } ${bar.barId}: \quad V(x) = ${fmt(v0)} - ${fmt(q)}x, \quad M(x) = ${fmt(-ma)} + ${fmt(v0)}x - ${fmt(q/2)}x^2`;
      }).join(String.raw` \\ `)} \end{array} \right.`,
      explanation: 'Para fins didáticos, as equações analíticas permitem determinar os valores exatos de cortante e momento em qualquer ponto do vão.',
      norm: 'Resistência dos Materiais',
    },
    {
      id: 'cross-influence-lines',
      title: 'Análise de Trens-Tipo (Linhas de Influência)',
      formula: String.raw`\text{Envoltória} = \max/\min [ \text{Momento} (x) \text{ para toda carga móvel} ]`,
      substitution: String.raw`\text{Alternância de sobrecargas nos vãos adjacentes}`,
      result: String.raw`\text{Pior Caso (Apoios vs Vãos)}`,
      explanation: 'Em vigas contínuas, os esforços máximos não ocorrem com toda a viga carregada simultaneamente. As Linhas de Influência determinam a posição exata da sobrecarga para maximizar momentos nos apoios (cargas adjacentes) ou nos vãos (cargas alternadas).',
      norm: 'Teoria das Estruturas',
    },
    {
      id: 'biblio-hibbeler',
      title: 'Referência Bibliográfica (Teoria das Estruturas)',
      formula: String.raw`\text{HIBBELER, R.C. Análise Estrutural. 8.ed.}`,
      substitution: String.raw`\text{Capítulo 11: Análise de Vigas e Pórticos Estaticamente Indeterminados}`,
      result: String.raw`\text{Base teórica para o Método de Hardy Cross}`,
      explanation: 'A metodologia de distribuição de momentos e cálculo de rigidez segue os padrões da literatura clássica de engenharia estrutural.',
      norm: 'Bibliografia Base'
    }
  ];
}

export function BeamCrossPlayground() {
  const { setPedagogicalSteps, setCalculationTrace, setError, setIsLoading, isLoading, error, updateParams, setFullResults } = useMestreStore();
  const [beamInput, setBeamInput] = useState<BeamInput>(defaultBeamInput);
  const [results, setResults] = useState<CrossSolveResult | null>(null);

  // Sincronizar com o estado global para o visualizador 2D (com debounce para evitar loops)
  useEffect(() => {
    const timer = setTimeout(() => {
      updateParams({
        spans: beamInput.spans as any,
        supports: beamInput.supports as any,
        h: (beamInput.sectionH || 50) / 100,
        b: (beamInput.sectionB || 20) / 100,
        fck: beamInput.fck || 25,
        L: beamInput.spans.reduce((sum, s) => sum + (s.length || 0), 0)
      });
    }, 300);
    return () => clearTimeout(timer);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [beamInput.spans, beamInput.supports, beamInput.sectionH, beamInput.sectionB, beamInput.fck]);

  const totalLength = useMemo(() => Math.max(beamInput.spans.reduce((sum, span) => sum + asFiniteNumber(span.length), 0), 0), [beamInput.spans]);
  const maxAbsShear = results ? Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.shear)))) : 0;
  const maxAbsMoment = results ? Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.moment)))) : 0;
  const maxAbsDeflection = results ? Math.max(0, ...results.diagrams.map((point) => Math.abs(asFiniteNumber(point.deflection)))) : 0;

  const getStructuralDiagramData = (type: 'shear' | 'moment' | 'deflection') => {
    if (!results?.diagrams) return null;
    
    return {
      type,
      unit: type === 'shear' ? 'kN' : type === 'moment' ? 'kNm' : 'mm',
      label: type === 'shear' ? 'ESFORÇO CORTANTE' : type === 'moment' ? 'MOMENTO FLETOR' : 'LINHA ELÁSTICA',
      series: [{
        name: 'Hardy Cross',
        points: results.diagrams.map(p => ({ x: p.xGlobal, y: p[type] ?? 0 })),
        color: type === 'shear' ? 'hsl(217 91% 55%)' : type === 'moment' ? 'hsl(262 83% 58%)' : 'hsl(20 90% 48%)'
      }],
      reactions: results.nodeReactions.map((r, i) => ({
        x: results.diagrams.find(d => d.spanId === `V${i+1}`)?.xGlobal ?? (i === results.nodeReactions.length - 1 ? totalLength : 0),
        value: r.verticalReaction,
        label: r.nodeId
      }))
    };
  };

  const updateSection = (field: 'sectionB' | 'sectionH' | 'fck', value: number) => {
    setBeamInput((current) => {
      const sectionB = field === 'sectionB' ? asFiniteNumber(value) : asFiniteNumber(current.sectionB, 20);
      const sectionH = field === 'sectionH' ? asFiniteNumber(value) : asFiniteNumber(current.sectionH, 50);
      const fck = field === 'fck' ? asFiniteNumber(value) : asFiniteNumber(current.fck, 25);
      const nextInertia = inertiaCm4(sectionB, sectionH);
      const calculateE = (f: number) => {
        const alphaE = 1.0;
        let eCi;
        if (f <= 50) {
          eCi = alphaE * 5600 * Math.sqrt(Math.max(f, 1));
        } else {
          eCi = 21500 * alphaE * Math.pow((f + 8) / 10, 1/3);
        }
        const alphaI = Math.min(0.8 + 0.2 * (f / 80), 1.0);
        return Math.round(eCi * alphaI / 1000); // GPa
      };
      const eGPa = field === 'fck' ? calculateE(fck) : current.eGPa;

      return {
        ...current,
        sectionB,
        sectionH,
        fck,
        eGPa,
        defaultInertiaCm4: nextInertia,
        spans: current.spans.map((span) => ({ ...span, inertiaCm4: nextInertia })),
      };
    });
  };

  const addSpan = () => {
    setBeamInput((current) => {
      if (current.spans.length >= 5) return current;
      const nextIndex = current.spans.length + 1;
      return {
        ...current,
        spans: [...current.spans, { id: `V${nextIndex}`, length: 4, inertiaCm4: current.defaultInertiaCm4, loads: [{ type: 'udl', value: 10 }] }],
        supports: [...current.supports, 'pin'],
      };
    });
  };

  const removeSpan = (index: number) => {
    setBeamInput((current) => {
      if (current.spans.length <= 1) return current;
      return {
        ...current,
        spans: current.spans.filter((_, idx) => idx !== index).map((span, idx) => ({ ...span, id: `V${idx + 1}` })),
        supports: current.supports.filter((_, idx) => idx !== index + 1),
      };
    });
  };

  const updateSupport = (index: number, value: SupportType) => {
    setBeamInput((current) => ({
      ...current,
      supports: current.supports.map((support, idx) => (idx === index ? value : support)),
    }));
  };

  const updateSpan = (index: number, key: 'length' | 'inertiaCm4', value: number) => {
    setBeamInput((current) => ({
      ...current,
      spans: current.spans.map((span, idx) => (idx === index ? { ...span, [key]: value } : span)),
    }));
  };

  const addLoad = (spanIndex: number, load: SpanLoad) => {
    setBeamInput((current) => ({
      ...current,
      spans: current.spans.map((span, idx) => (idx === spanIndex ? { ...span, loads: [...span.loads, load] } : span)),
    }));
  };

  const updateLoad = (spanIndex: number, loadIndex: number, patch: Partial<SpanLoad>) => {
    setBeamInput((current) => ({
      ...current,
      spans: current.spans.map((span, idx) => {
        if (idx !== spanIndex) return span;
        return {
          ...span,
          loads: span.loads.map((load, lidx) => (lidx === loadIndex ? ({ ...load, ...patch } as SpanLoad) : load)),
        };
      }),
    }));
  };

  const removeLoad = (spanIndex: number, loadIndex: number) => {
    setBeamInput((current) => ({
      ...current,
      spans: current.spans.map((span, idx) => (idx === spanIndex ? { ...span, loads: span.loads.filter((_, lidx) => lidx !== loadIndex) } : span)),
    }));
  };

  const handleCalculate = () => {
    setIsLoading(true);
    try {
      setError(null);
      if (totalLength <= 0 || beamInput.spans.some((span) => asFiniteNumber(span.length) <= 0)) {
        throw new Error('Todos os vãos precisam ter comprimento maior que zero.');
      }
      const solved = solveCross(beamInput);
      setResults(solved);
      setPedagogicalSteps(buildCrossSteps(beamInput, solved));
      // Persiste resultados no store global → BeamDiagramsSection e Beam2DView lêem daqui
      setFullResults({
        diagrams: solved.diagrams,
        nodeReactions: solved.nodeReactions,
        barResults: solved.barResults,
        converged: solved.converged,
        iterations: solved.iterations.length,
      });
      setCalculationTrace({
        requested_type: 'beam_cross',
        solver_module: 'vigacross.solveCross',
        blackboard_builder: 'BeamCrossPlayground.buildCrossSteps',
        classical_check: true,
        mef_check: false,
      });
    } catch (crossError) {
      setError(crossError instanceof Error ? crossError.message : 'Erro no cálculo Hardy Cross.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Share2 className="w-5 h-5 text-primary" />
          Viga Cross
        </h3>
        <Button onClick={addSpan} variant="outline" size="sm" className="h-8 text-[10px] gap-1">
          <Plus className="w-3 h-3" />
          Vão
        </Button>
      </div>

      <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-4">
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Base b (cm)</Label>
            <Input type="number" value={beamInput.sectionB ?? 20} onChange={(event) => updateSection('sectionB', Number(event.target.value))} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Altura h (cm)</Label>
            <Input type="number" value={beamInput.sectionH ?? 50} onChange={(event) => updateSection('sectionH', Number(event.target.value))} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
            <Input type="number" value={beamInput.fck ?? 25} onChange={(event) => updateSection('fck', Number(event.target.value))} className="h-9 bg-background/50" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">E (GPa)</Label>
            <Input type="number" value={beamInput.eGPa ?? 25} onChange={(event) => setBeamInput((current) => ({ ...current, eGPa: Number(event.target.value) }))} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Tolerância</Label>
            <Input type="number" step="0.001" value={beamInput.tolerance ?? 0.01} onChange={(event) => setBeamInput((current) => ({ ...current, tolerance: Number(event.target.value) }))} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Iterações</Label>
            <Input type="number" value={beamInput.maxIterations ?? 50} onChange={(event) => setBeamInput((current) => ({ ...current, maxIterations: Number(event.target.value) }))} className="h-9 bg-background/50" />
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Apoio inicial</span>
            <SupportSelect value={beamInput.supports[0]} onChange={(value) => updateSupport(0, value)} />
          </div>
        </div>

        {beamInput.spans.map((span, spanIndex) => (
          <div key={span.id} className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-4">
            <div className="flex items-center justify-between gap-3">
              <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Vão {span.id}</span>
              <div className="flex items-center gap-2">
                <SupportSelect value={beamInput.supports[spanIndex + 1]} onChange={(value) => updateSupport(spanIndex + 1, value)} />
                <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive/60" onClick={() => removeSpan(spanIndex)} disabled={beamInput.spans.length <= 1}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Comprimento (m)</Label>
                <Input type="number" step="0.1" value={span.length ?? 4} onChange={(event) => updateSpan(spanIndex, 'length', Number(event.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label className="text-[10px] text-muted-foreground uppercase">Inércia (cm⁴)</Label>
                  <span className="text-[9px] text-muted-foreground/60 uppercase">Auto</span>
                </div>
                <Input type="number" value={Math.round(span.inertiaCm4 ?? 208333)} disabled className="h-9 bg-muted/50 cursor-not-allowed opacity-70" />
              </div>
            </div>

            <div className="space-y-3 pt-3 border-t border-border/50">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Cargas</span>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => addLoad(spanIndex, { type: 'udl', value: 10 })}>
                    + q
                  </Button>
                  <Button type="button" variant="outline" size="sm" className="h-7 text-[10px]" onClick={() => addLoad(spanIndex, { type: 'point', value: 50, position: span.length / 2 })}>
                    + P
                  </Button>
                </div>
              </div>

              {span.loads.map((load, loadIndex) => (
                <div key={`${span.id}-${loadIndex}`} className="bg-background/40 p-3 rounded-lg border border-border/40 space-y-2">
                  <div className="grid grid-cols-[1fr_1fr_auto] gap-2 items-end">
                    <div className="space-y-1.5">
                      <Label className="text-[9px] text-muted-foreground uppercase">{load.type === 'udl' ? 'q1 (kN/m)' : 'P (kN)'}</Label>
                      <Input type="number" value={load.value ?? 0} onChange={(event) => updateLoad(spanIndex, loadIndex, { value: Number(event.target.value) })} className="h-8 text-xs bg-transparent" />
                    </div>
                    <div className="space-y-1.5">
                      <Label className="text-[9px] text-muted-foreground uppercase">{load.type === 'udl' ? 'q2 (kN/m)' : 'Posição (m)'}</Label>
                      {load.type === 'udl' ? (
                        <Input
                          type="number"
                          value={(load as any).q_end ?? load.value}
                          onChange={(event) => updateLoad(spanIndex, loadIndex, { q_end: Number(event.target.value) } as any)}
                          className="h-8 text-xs bg-primary/5 font-bold"
                          title="Intensidade no final do vão (carga trapezoidal)"
                        />
                      ) : (
                        <Input
                          type="number"
                          value={(load as any).position ?? 0}
                          onChange={(event) => updateLoad(spanIndex, loadIndex, { position: Number(event.target.value) } as Partial<SpanLoad>)}
                          className="h-8 text-xs bg-transparent"
                        />
                      )}
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive/60" onClick={() => removeLoad(spanIndex, loadIndex)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  {/* Badge trapezoidal */}
                  {load.type === 'udl' && (load as any).q_end !== undefined && Math.abs((load as any).q_end - load.value) > 0.01 && (
                    <div className="text-[9px] text-primary font-bold uppercase tracking-wide">
                      ▲ Carga trapezoidal: {load.value} → {(load as any).q_end} kN/m
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <Button onClick={handleCalculate} className="w-full macos-button h-12 gap-2 shadow-lg shadow-primary/10" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Calculando...' : 'Calcular Hardy Cross'}
      </Button>

      {error && (
        <div className="p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium">
          {error}
        </div>
      )}

      {results && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <MetricCard label="Vãos" value={String(beamInput.spans.length)} />
            <MetricCard label="Iterações" value={String(results.iterations.length)} />
            <MetricCard label="V máx." value={`${fmt(maxAbsShear)} kN`} />
            <MetricCard label="M máx." value={`${fmt(maxAbsMoment)} kNm`} />
            <MetricCard label="f máx." value={`${fmt(maxAbsDeflection)} mm`} />
          </div>

          <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-primary" />
              <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Reações</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {results.nodeReactions.map((reaction, i) => (
                <div key={reaction.nodeId} className="flex justify-between rounded-lg bg-background/50 px-3 py-2 text-xs">
                  <span className="font-bold">{reaction.nodeId}</span>
                  <span className="font-mono">{fmt(reaction.verticalReaction)} kN</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-muted/30 border border-border/50 overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="text-[10px] uppercase text-muted-foreground">
                <tr>
                  <th className="text-left py-2">Vão</th>
                  <th className="text-right py-2">MEP A</th>
                  <th className="text-right py-2">MEP B</th>
                  <th className="text-right py-2">Final A</th>
                  <th className="text-right py-2">Final B</th>
                </tr>
              </thead>
              <tbody>
                {results.barResults.map((bar) => (
                  <tr key={bar.barId} className="border-t border-border/50">
                    <td className="py-2 font-bold">{bar.barId}</td>
                    <td className="py-2 text-right font-mono">{fmt(bar.mepA)}</td>
                    <td className="py-2 text-right font-mono">{fmt(bar.mepB)}</td>
                    <td className="py-2 text-right font-mono">{fmt(bar.finalA)}</td>
                    <td className="py-2 text-right font-mono">{fmt(bar.finalB)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="space-y-6">
            {(() => {
              const shearData = getStructuralDiagramData('shear');
              const momentData = getStructuralDiagramData('moment');
              const deflectionData = getStructuralDiagramData('deflection');
              
              return (
                <>
                  {shearData && <StructuralDiagram data={shearData as any} />}
                  {momentData && <StructuralDiagram data={momentData as any} />}
                  {deflectionData && <StructuralDiagram data={deflectionData as any} />}
                </>
              );
            })()}
          </div>
        </div>
      )}

      <p className="text-[10px] text-muted-foreground/60 text-center leading-relaxed italic">
        Método didático de Hardy Cross para vigas contínuas hiperestáticas. Para dimensionamento executivo, compare com o módulo MEF de vigas.
      </p>
    </div>
  );
}

function SupportSelect({ value, onChange }: { value: SupportType; onChange: (value: SupportType) => void }) {
  return (
    <Select value={value} onValueChange={(nextValue) => onChange(nextValue as SupportType)}>
      <SelectTrigger className="h-8 w-[120px] bg-background/50 text-xs">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(SUPPORT_LABELS).map(([support, label]) => (
          <SelectItem key={support} value={support}>
            {label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-3 rounded-xl bg-muted/30 border border-border/50">
      <p className="text-[9px] uppercase font-black text-muted-foreground tracking-widest">{label}</p>
      <p className="mt-1 text-sm font-black text-foreground">{value}</p>
    </div>
  );
}
