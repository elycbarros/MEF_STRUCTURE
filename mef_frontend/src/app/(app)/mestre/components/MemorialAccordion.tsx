'use client';

import { useMestreStore } from '@/lib/store-mestre';
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from '@/components/ui/accordion';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Card, CardContent } from '@/components/ui/card';
import { BookOpen, TriangleAlert, Info, LayoutList, FileText } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StructuralDiagram } from './StructuralDiagram';
import { BeamSectionDetail } from './BeamSectionDetail';
import { TechnicalDiagram } from './TechnicalDiagram';
import type { MestreStep } from '@/lib/mestre-types';

export function MemorialAccordion() {
  const { pedagogicalSteps, isLoading, viewMode, setViewMode } = useMestreStore();

  if (isLoading && pedagogicalSteps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-muted-foreground animate-pulse">
        <BookOpen className="w-12 h-12 mb-4 opacity-20" />
        <p>Orquestrando memorial pedagógico...</p>
      </div>
    );
  }

  if (pedagogicalSteps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
        <Info className="w-12 h-12 mb-4 opacity-20" />
        <p>Ajuste os parâmetros e clique em calcular para gerar o memorial.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" id="pedagogical-memorial-root">
      <div className="flex items-center justify-between mb-4 print:hidden">
        <div className="flex flex-col gap-1">
          <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            Blackboard: Roteiro de Cálculo
          </h3>
          <div className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 w-fit">
            <TriangleAlert className="w-3 h-3" />
            AUDITORIA NBR 6118
          </div>
        </div>

        <Tabs 
          value={viewMode} 
          onValueChange={(v) => setViewMode(v as 'interactive' | 'memorial')}
          className="bg-muted/50 p-1 rounded-lg"
        >
          <TabsList className="h-8 bg-transparent gap-1">
            <TabsTrigger value="interactive" className="h-6 text-[10px] font-bold uppercase tracking-wider gap-2">
              <LayoutList className="w-3 h-3" />
              Interativo
            </TabsTrigger>
            <TabsTrigger value="memorial" className="h-6 text-[10px] font-bold uppercase tracking-wider gap-2">
              <FileText className="w-3 h-3" />
              Memorial
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {viewMode === 'interactive' ? (
        <Accordion type="single" collapsible className="w-full space-y-3">
          {pedagogicalSteps.map((step, index) => (
            <AccordionItem 
              key={step.id || index} 
              value={`item-${index}`}
              className="border border-border rounded-xl px-4 bg-card/50 hover:bg-card transition-colors shadow-sm"
            >
              <AccordionTrigger className="hover:no-underline py-4">
                <div className="flex flex-col items-start text-left gap-1">
                  <span className="text-[10px] font-bold text-primary uppercase">Passo {index + 1}</span>
                  <span className="font-semibold text-sm tracking-tight">{step.title}</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="pb-6 pt-2 space-y-4 border-t border-border/50">
                {/* Render Step Content */}
                <StepContent step={step} />
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      ) : (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {pedagogicalSteps.map((step, index) => (
            <div key={step.id || index} className="relative">
              {index < pedagogicalSteps.length - 1 && (
                <div className="absolute left-6 top-12 bottom-0 w-px bg-gradient-to-b from-primary/20 via-primary/5 to-transparent -z-10" />
              )}
              <Card className="border-none shadow-lg bg-card overflow-hidden ring-1 ring-border/50">
                <div className="bg-primary/5 px-6 py-4 border-b border-primary/10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-black text-xs">
                      {index + 1}
                    </div>
                    <h3 className="font-bold text-base tracking-tight">{step.title}</h3>
                  </div>
                  {step.norm && (
                    <span className="text-[10px] font-black uppercase text-primary/60 tracking-widest">{step.norm}</span>
                  )}
                </div>
                <CardContent className="p-8">
                  <StepContent step={step} isMemorial />
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StepContent({ step, isMemorial = false }: { step: MestreStep, isMemorial?: boolean }) {
  return (
    <div className="space-y-6">
      {/* Fórmula Principal */}
      <div className={`${isMemorial ? 'bg-muted/20' : 'bg-muted/30'} rounded-2xl p-6 border border-border/50 flex justify-center overflow-x-auto shadow-inner transition-colors hover:bg-muted/40`}>
        <div className="text-lg md:text-xl text-foreground font-medium py-2">
          <ReactMarkdown 
            remarkPlugins={[remarkMath]} 
            rehypePlugins={[rehypeKatex]}
          >
            {`$$ ${step.formula} $$`}
          </ReactMarkdown>
        </div>
      </div>

      {/* Substituição e Resultado */}
      <div className={`grid ${isMemorial ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'} gap-4`}>
        <div className="space-y-3 p-4 rounded-xl bg-primary/5 border border-primary/10 shadow-sm transition-all hover:bg-primary/[0.07]">
          <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 shadow-sm" />
            Substituição
          </div>
          <div className="text-sm md:text-base overflow-x-auto py-1">
            <ReactMarkdown 
              remarkPlugins={[remarkMath]} 
              rehypePlugins={[rehypeKatex]}
            >
              {`$ ${step.substitution} $`}
            </ReactMarkdown>
          </div>
        </div>

        <div className="space-y-3 p-4 rounded-xl bg-primary/10 border border-primary/20 shadow-sm transition-all hover:bg-primary/[0.12]">
          <div className="text-[10px] font-bold text-primary uppercase tracking-widest flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-sm" />
            Resultado
          </div>
          <div className="text-sm md:text-base font-bold text-primary overflow-x-auto py-1">
            <ReactMarkdown 
              remarkPlugins={[remarkMath]} 
              rehypePlugins={[rehypeKatex]}
            >
              {`$ ${step.result} $`}
            </ReactMarkdown>
          </div>
        </div>
      </div>
      
      {/* Visualização de Dados (Gráfico, Diagrama ou Detalhamento) */}
      {step.diagramData ? (
        <TechnicalDiagram data={step.diagramData} />
      ) : step.detailingData ? (
        <BeamSectionDetail data={step.detailingData} />
      ) : step.chartData ? (
        <StructuralDiagram data={step.chartData} />
      ) : null}

      {/* Explicação */}
      <div className="pt-4 border-t border-border/50">
        <p className="text-sm text-muted-foreground leading-relaxed italic">
          {step.explanation}
        </p>
      </div>
    </div>
  );
}
