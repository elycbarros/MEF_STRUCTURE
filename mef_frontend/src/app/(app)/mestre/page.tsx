'use client';

import { MestreSidebar } from './components/MestreSidebar';
import { getMestreModule } from '@/lib/mestre-modules';
import { MemorialAccordion } from './components/MemorialAccordion';
import { MemorialHeader } from './components/MemorialHeader';
import { StructuralDuel } from './components/StructuralDuel';
import { Beam3DView } from './components/Beam3DView';
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
  const { selectedElementType } = useMestreStore();
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
          
          {/* Esquerda: Playground + Visualização (Col 1-5) */}
          <div className="col-span-12 lg:col-span-5 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar">
            
            {/* HUD Visualizador 3D */}
            <div className="h-[350px] shrink-0">
              <Beam3DView />
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
              <StructuralDuel />
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
