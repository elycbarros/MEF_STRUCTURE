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
import { SpecialPlayground } from './components/SpecialPlayground';
import { useMestreStore } from '@/lib/store-mestre';
import { Separator } from '@/components/ui/separator';
import { 
  Share2, 
  Download, 
  HelpCircle,
  LayoutDashboard,
  Presentation
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function MestrePage() {
  const { selectedElementType, fullResults } = useMestreStore();
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
              {(selectedElementType === 'beam' || selectedElementType === 'beam_cross') ? <Beam2DView /> : <Beam3DView />}
            </div>

            {/* Painel de Controle */}
            <div className="bg-card/30 rounded-2xl border border-border/50 p-6 shadow-sm">
              <PlaygroundComponent />
            </div>

            {/* Alerta de Verificação Rápida */}
            <div className="bg-primary/5 border border-primary/10 rounded-xl p-4 flex gap-4">
              <div className="bg-primary/20 w-10 h-10 rounded-lg flex items-center justify-center shrink-0">
                <Presentation className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-primary">Análise Dinâmica Ativa</h4>
                <p className="text-xs text-primary/70 leading-relaxed">
                  O Atlas está processando os dados em tempo real via Rust Core. 
                  O memorial à direita reflete o estado atual do elemento estrutural.
                </p>
              </div>
            </div>
          </div>

          {/* Direita: Blackboard / Memorial (Col 6-12) */}
          <div className="col-span-12 lg:col-span-7 flex flex-col overflow-hidden bg-card/40 rounded-2xl border border-border/50 shadow-inner print:border-none print:shadow-none print:bg-white print:overflow-visible print:col-span-12">
            <div className="p-6 h-full overflow-y-auto custom-scrollbar print:overflow-visible print:p-0">
              <MemorialHeader />
              
              {/* ── Diagramas V/M/f — apenas para vigas (renderizados no Blackboard) ── */}
              {(selectedElementType === 'beam' || selectedElementType === 'beam_cross') && (
                <BeamDiagramsSection />
              )}

              {selectedElementType === 'column' && <div className="mt-8"><FiberMeshView /></div>}
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

function SectionTitle({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-1.5 h-4 rounded-full bg-primary" />
      <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">{label}</h3>
    </div>
  );
}
