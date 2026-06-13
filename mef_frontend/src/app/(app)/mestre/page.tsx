'use client';

import { MestreSidebar } from './components/MestreSidebar';
import { getMestreModule } from '@/lib/mestre-modules';
import { MemorialAccordion } from './components/MemorialAccordion';
import { MemorialHeader } from './components/MemorialHeader';
import { StructuralDuel } from './components/StructuralDuel';
import { StructuralDiagram } from './components/StructuralDiagram';
import { FiberMeshView } from './components/FiberMeshView';
import { EconomyInsight } from './components/EconomyInsight';
import { Beam3DView } from './components/Beam3DView';
import { Beam2DView } from './components/Beam2DView';
import { SteelTableView } from './components/SteelTableView';
import { ExecutiveSketch } from './components/ExecutiveSketch';
import { MestreInteractionDiagram, MestreFiberMap } from './components/MestreDiagram';
import { SectionSketch } from './components/SectionSketch';
import { SpecialPlayground } from './components/SpecialPlayground';
import { EngineStatusPanel } from './components/EngineStatusPanel';
import { useMestreStore } from '@/lib/store-mestre';
import { Separator } from '@/components/ui/separator';
import {
  Share2,
  Download,
  HelpCircle,
  LayoutDashboard,
  Flame,
  AlertTriangle,
  CheckCircle2,
  Award
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function MestrePage() {
  const { selectedElementType, fullResults, params } = useMestreStore();
  const activeModule = getMestreModule(selectedElementType);
  const PlaygroundComponent = activeModule?.component || SpecialPlayground;

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar macOS Style */}
      <MestreSidebar />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header / Breadcrumb */}
        <header className="h-14 border-b border-border flex items-center justify-between px-6 bg-background/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <LayoutDashboard className="w-4 h-4" />
              <span>Mestre</span>
              <span className="text-border">/</span>
              <span className="text-foreground font-bold capitalize">{selectedElementType.replace('_', ' ')}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
              <Share2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
              <Download className="w-4 h-4" />
            </Button>
            <Separator orientation="vertical" className="h-4 mx-1" />
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary">
              <HelpCircle className="w-4 h-4" />
            </Button>
          </div>
        </header>

        {/* Dynamic Content Grid */}
        <div className="flex-1 overflow-hidden p-6 gap-6 grid grid-cols-12">

          {/* Esquerda: Visualizador + Formulário (Col 1-5) */}
          <div className="col-span-12 lg:col-span-5 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar">

            {/* HUD Visualizador */}
            <div className="h-[350px] shrink-0">
              {(selectedElementType === 'beam' ||
                selectedElementType === 'beam_cross' ||
                (selectedElementType === 'exam_auditor' && params.truss_type !== 'q31')) ? (
                <Beam2DView />
              ) : (
                <Beam3DView />
              )}
            </div>

            {/* Painel de Controle */}
            <div className="bg-card/30 rounded-2xl border border-border/50 p-6 shadow-sm">
              <PlaygroundComponent />
            </div>

            <EngineStatusPanel />
          </div>

          {/* Direita: Blackboard / Memorial (Col 6-12) */}
          <div className="col-span-12 lg:col-span-7 flex flex-col overflow-hidden bg-card/40 rounded-2xl border border-border/50 shadow-inner print:border-none print:shadow-none print:bg-white print:overflow-visible print:col-span-12">
            <div className="p-6 h-full overflow-y-auto custom-scrollbar print:overflow-visible print:p-0">
              <MemorialHeader />

              {/* ── Diagramas V/M/f — apenas para vigas (renderizados no Blackboard) ── */}
              {(selectedElementType === 'beam' || selectedElementType === 'beam_cross') && (
                <BeamDiagramsSection />
              )}

              {selectedElementType === 'column' && (
                <ColumnResultsSection />
              )}

              {selectedElementType === 'advanced_slab' && (
                <AdvancedSlabResultsSection />
              )}
              {(selectedElementType === 'beam' || selectedElementType === 'column') && <div className="mt-8"><EconomyInsight /></div>}
              <StructuralDuel />

              {/* Executive Detailing View */}
              {fullResults?.executive_detailing && (
                <div className="mt-8">
                  <ExecutiveSketch
                    geometry={fullResults.geometry}
                    rebar={fullResults.executive_detailing.rebar}
                  />
                </div>
              )}

              {/* Steel Table View */}
              {fullResults?.steel_table && (
                <div className="mt-8">
                  <SteelTableView
                    data={fullResults.steel_table.rows}
                    totals={fullResults.steel_table.totals}
                  />
                </div>
              )}

              <div className="mt-8">
                <MemorialAccordion />
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

// ── Seção de Diagramas no Blackboard ─────────────────────────────────────────
// Lê resultados do store e exibe V, M, f para beam e beam_cross no painel direito.
function BeamDiagramsSection() {
  const { fullResults, selectedElementType } = useMestreStore();
  const isCross = selectedElementType === 'beam_cross';

  if (!fullResults) return null;

  // ── Viga Isolada ──
  if (!isCross) {
    if (!fullResults.diagrams) return null;

    const reactions = fullResults.reactions
      ? (Object.values(fullResults.reactions) as any[])
          .sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
          .map((r: any, idx: number) => ({
            x: r.x ?? 0,
            value: r.R ?? 0,
            label: `V${String.fromCharCode(97 + idx)}`
          }))
      : [];

    const mkData = (type: 'shear' | 'moment' | 'deflection') => {
      const mefPoints = fullResults.diagrams[type] || [];
      const series: any[] = [{
        name: 'MEF Numérico',
        points: mefPoints,
        color: type === 'shear' ? 'hsl(217 91% 55%)' : type === 'moment' ? 'hsl(262 83% 58%)' : 'hsl(20 90% 48%)'
      }];
      if (fullResults.classical_diagrams) {
        let pts: any[] = [];
        if (type === 'shear' && fullResults.classical_diagrams.V_kN)
          pts = fullResults.classical_diagrams.x_m.map((x: number, i: number) => ({ x, y: fullResults.classical_diagrams.V_kN[i] }));
        else if (type === 'moment' && fullResults.classical_diagrams.M_kNm)
          pts = fullResults.classical_diagrams.x_m.map((x: number, i: number) => ({ x, y: fullResults.classical_diagrams.M_kNm[i] }));
        else if (type === 'deflection')
          pts = mefPoints;
        if (pts.length > 0)
          series.push({ name: 'Clássico Analítico', points: pts, color: '#059669', dashed: true });
      }
      return {
        type, series,
        unit: type === 'shear' ? 'kN' : type === 'moment' ? 'kNm' : 'mm',
        label: type === 'shear' ? 'ESFORÇO CORTANTE' : type === 'moment' ? 'MOMENTO FLETOR' : 'LINHA ELÁSTICA',
        reactions: type === 'shear' ? reactions : []
      };
    };

    return (
      <div className="mt-6 space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
        <SectionTitle label="Diagramas de Esforços" />
        <StructuralDiagram data={mkData('shear')} />
        <StructuralDiagram data={mkData('moment')} />
        <StructuralDiagram data={mkData('deflection')} />
      </div>
    );
  }

  // ── Viga Cross ──
  if (!fullResults.diagrams || !Array.isArray(fullResults.diagrams)) return null;

  const diags = fullResults.diagrams as any[];
  const totalLen = diags.length > 0 ? diags[diags.length - 1].xGlobal : 0;

  const mkCrossData = (type: 'shear' | 'moment' | 'deflection') => ({
    type,
    unit: type === 'shear' ? 'kN' : type === 'moment' ? 'kNm' : 'mm',
    label: type === 'shear' ? 'ESFORÇO CORTANTE' : type === 'moment' ? 'MOMENTO FLETOR' : 'LINHA ELÁSTICA',
    series: [{
      name: 'Hardy Cross',
      points: diags.map((p: any) => ({ x: p.xGlobal, y: p[type] ?? 0 })),
      color: type === 'shear' ? 'hsl(217 91% 55%)' : type === 'moment' ? 'hsl(262 83% 58%)' : 'hsl(20 90% 48%)'
    }],
    reactions: type === 'shear'
      ? (fullResults.nodeReactions || []).map((r: any, i: number) => ({
          x: diags.find((d: any) => d.spanId === `V${i + 1}`)?.xGlobal ?? (i === 0 ? 0 : totalLen),
          value: r.verticalReaction,
          label: r.nodeId
        }))
      : []
  });

  return (
    <div className="mt-6 space-y-4 animate-in fade-in slide-in-from-top-4 duration-500">
      <SectionTitle label="Diagramas — Hardy Cross" />
      <StructuralDiagram data={mkCrossData('shear')} />
      <StructuralDiagram data={mkCrossData('moment')} />
      <StructuralDiagram data={mkCrossData('deflection')} />
    </div>
  );
}

function ColumnResultsSection() {
  const { fullResults, params } = useMestreStore();

  if (!fullResults) return null;

  return (
    <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-top-4 duration-500">
      <SectionTitle label="Dimensionamento e Esbeltez do Pilar" />

      {/* 2nd Order Analysis Summary */}
      {fullResults.slenderness && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            Análise de 2ª Ordem e Esbeltez (P-Delta Local)
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-background/50 border border-border/50">
              <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">λx (Esbeltez)</p>
              <p className="mt-1 text-sm font-black text-foreground">{fullResults.slenderness.lambda_x}</p>
            </div>
            <div className="p-3 rounded-xl bg-background/50 border border-border/50">
              <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">λy (Esbeltez)</p>
              <p className="mt-1 text-sm font-black text-foreground">{fullResults.slenderness.lambda_y}</p>
            </div>
            <div className="p-3 rounded-xl bg-background/50 border border-border/50">
              <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">Mx Total</p>
              <p className="mt-1 text-sm font-black text-foreground">{fullResults.Md_x_total_kNm} kNm</p>
            </div>
            <div className="p-3 rounded-xl bg-background/50 border border-border/50">
              <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">My Total</p>
              <p className="mt-1 text-sm font-black text-foreground">{fullResults.Md_y_total_kNm} kNm</p>
            </div>
          </div>
          <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-2 px-1">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            Método: {fullResults.moments_2nd_order?.method || 'Pilar Padrão (NBR 6118)'}
          </div>
        </div>
      )}

      {/* Detailing Section (Sketch + Steel Table) */}
      {fullResults.detailing && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SectionSketch
            b_m={params.b ?? 0.4}
            h_m={params.h ?? 0.4}
            rebars={fullResults.detailing.executive?.rebar_coords || []}
            phi_mm={fullResults.detailing.longitudinal?.phi_mm || 10.0}
            label="Seção Pilar"
          />
          <SteelTableView
            data={[{
              pos: "N1",
              phi_mm: fullResults.detailing.longitudinal?.phi_mm || 10.0,
              count: fullResults.detailing.longitudinal?.count || 4,
              length_m: params.L_free ?? 3.0,
              total_length_m: (fullResults.detailing.longitudinal?.count || 4) * (params.L_free ?? 3.0),
              weight_kg: fullResults.detailing.steel_ca50_kg || 0,
              type: "CA-50"
            }]}
            totals={{
              total_ca50_kg: fullResults.detailing.steel_ca50_kg || 0,
              total_ca60_kg: 0,
              grand_total_kg: fullResults.detailing.steel_ca50_kg || 0
            }}
          />
        </div>
      )}

      {/* N-M Interaction Diagrams */}
      {fullResults.fiber_results?.interaction_diagram_x && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MestreInteractionDiagram
            envelope={fullResults.fiber_results.interaction_diagram_x}
            solicitant={{ n: fullResults.Nd_kN, m: fullResults.Md_x_total_kNm }}
            title="Interação N x Mx (Biaxial X)"
          />
          <MestreInteractionDiagram
            envelope={fullResults.fiber_results.interaction_diagram_y}
            solicitant={{ n: fullResults.Nd_kN, m: fullResults.Md_y_total_kNm }}
            title="Interação N x My (Biaxial Y)"
          />
        </div>
      )}

      {/* Fiber Stress Map & FiberMeshView side-by-side or stacked */}
      {fullResults.fiber_results?.fibers && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MestreFiberMap
            fibers={fullResults.fiber_results.fibers}
            b={params.b ?? 0.4}
            h={params.h ?? 0.4}
            title="Mapa de Tensões na Seção"
          />
          <FiberMeshView />
        </div>
      )}
    </div>
  );
}

interface ReinforcementZone {
  Asx_cm2_m: number;
  Asy_cm2_m: number;
  sugestao_x: string;
  sugestao_y: string;
}

interface ThermalItem {
  id: string;
  description: string;
  priority: string;
}

interface SolutionItem {
  id: string;
  nome: string;
  maturidade: string;
  viabilidade: string;
  quando_estudar: string;
  disponivel: boolean;
}

function AdvancedSlabResultsSection() {
  const { fullResults } = useMestreStore();

  if (!fullResults) return null;

  const rec = (fullResults.foundation_recommendation || {}) as Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  const decision = (fullResults.executive_decision || {}) as Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  const reinfMap = (fullResults.reinforcement_map || {}) as { zones?: Record<string, ReinforcementZone>; nota?: string };
  const thermal = (fullResults.thermal_checklist || {}) as { applicable?: boolean; h_adopted_m?: number; nota?: string; items?: ThermalItem[] };
  const comp = (fullResults.solution_comparison || {}) as { solutions?: SolutionItem[]; nota?: string };

  return (
    <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-top-4 duration-500">

      {/* ── Quadro de Decisão Executiva ── */}
      {decision.decision_status && (
        <div className="p-5 rounded-2xl border border-border/50 bg-muted/20 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-primary" />
              <h4 className="text-xs font-black uppercase tracking-wider text-foreground">
                Decisão Executiva & Viabilidade
              </h4>
            </div>
            <span className={`text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full ${
              decision.go_no_go === 'go_preliminar'
                ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                : decision.go_no_go === 'conditional_go'
                ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                : 'bg-destructive/10 text-destructive border border-destructive/20'
            }`}>
              {decision.go_no_go?.replace('_', ' ')}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-background/50 border border-border/40">
              <span className="text-[8px] font-black uppercase tracking-wider text-muted-foreground">Diagnóstico da Solução</span>
              <p className="mt-1 text-sm font-bold text-foreground">{decision.executive_label || rec.executive_label}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-background/50 border border-border/40">
              <span className="text-[8px] font-black uppercase tracking-wider text-muted-foreground">Próximo Passo Recomendado</span>
              <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{decision.next_step}</p>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-background/50 border border-border/40">
            <span className="text-[8px] font-black uppercase tracking-wider text-muted-foreground">Recomendação Principal</span>
            <p className="mt-1 text-xs text-muted-foreground leading-relaxed font-semibold">{decision.main_recommendation}</p>
          </div>
        </div>
      )}

      {/* ── Mapa de Armaduras Regionais (Wood-Armer / NBR 6118) ── */}
      {reinfMap.zones && (
        <div className="p-5 rounded-2xl border border-border/50 bg-background/30 space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            <h4 className="text-xs font-black uppercase tracking-wider text-foreground">
              Mapa de Armaduras por Regiões (cm²/m)
            </h4>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {Object.entries(reinfMap.zones).map(([zoneKey, zoneVal]) => (
              <div key={zoneKey} className="p-3.5 rounded-xl bg-background/40 border border-border/30 space-y-2">
                <span className="text-[9px] font-black uppercase text-muted-foreground tracking-tighter block truncate">
                  {zoneKey.replace(/_/g, ' ')}
                </span>
                <div className="grid grid-cols-2 gap-2 text-center border-t border-border/20 pt-2">
                  <div>
                    <span className="text-[8px] font-bold text-muted-foreground">DIR X</span>
                    <p className="text-xs font-black text-foreground">{zoneVal.Asx_cm2_m} cm²</p>
                    <p className="text-[8px] font-medium text-primary tracking-tighter block truncate mt-0.5">{zoneVal.sugestao_x}</p>
                  </div>
                  <div>
                    <span className="text-[8px] font-bold text-muted-foreground">DIR Y</span>
                    <p className="text-xs font-black text-foreground">{zoneVal.Asy_cm2_m} cm²</p>
                    <p className="text-[8px] font-medium text-primary tracking-tighter block truncate mt-0.5">{zoneVal.sugestao_y}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-[9px] text-muted-foreground italic leading-tight">{reinfMap.nota}</p>
        </div>
      )}

      {/* ── Checklist de Concreto Massa e Risco Térmico ── */}
      {thermal.applicable && (
        <div className="p-5 rounded-2xl border border-orange-500/20 bg-orange-500/5 space-y-4">
          <div className="flex items-center gap-2 text-orange-600 dark:text-orange-500">
            <Flame className="w-5 h-5" />
            <h4 className="text-xs font-black uppercase tracking-wider">
              Atenção: Diretrizes de Concreto Massa (h = {thermal.h_adopted_m}m)
            </h4>
          </div>

          <p className="text-xs text-muted-foreground leading-relaxed">
            {thermal.nota}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {thermal.items?.map((item) => (
              <div key={item.id} className="flex items-start gap-2.5 p-3 rounded-xl bg-background/50 border border-orange-500/10">
                <CheckCircle2 className="w-4 h-4 text-orange-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs font-bold text-foreground leading-tight">{item.description}</p>
                  <span className="inline-block mt-1 text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-600">
                    Prioridade: {item.priority}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Comparativo de Soluções de Fundação ── */}
      {comp.solutions && (
        <div className="p-5 rounded-2xl border border-border/50 bg-background/30 space-y-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-muted-foreground" />
            <h4 className="text-xs font-black uppercase tracking-wider text-foreground">
              Comparativo Técnico-Econômico Qualitativo
            </h4>
          </div>

          <div className="space-y-2.5">
            {comp.solutions.map((sol) => (
              <div key={sol.id} className="p-3.5 rounded-xl bg-background/40 border border-border/30 flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${sol.disponivel ? 'bg-emerald-500' : 'bg-muted-foreground/40'}`} />
                    <span className="text-xs font-bold text-foreground">{sol.nome}</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground leading-relaxed max-w-xl">{sol.quando_estudar}</p>
                </div>
                <div className="text-left sm:text-right shrink-0">
                  <span className={`inline-block text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md ${
                    sol.disponivel
                      ? 'bg-emerald-500/10 text-emerald-500'
                      : 'bg-muted/40 text-muted-foreground'
                  }`}>
                    {sol.maturidade.replace('_', ' ')}
                  </span>
                  <p className="text-[8px] font-mono text-muted-foreground/60 mt-1 uppercase tracking-tighter">{sol.viabilidade}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="text-[9px] text-muted-foreground italic leading-tight">{comp.nota}</p>
        </div>
      )}

    </div>
  );
}

function SectionTitle({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-1.5 h-4 rounded-full bg-primary" />
      <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">{label}</h3>
    </div>
  );
}
