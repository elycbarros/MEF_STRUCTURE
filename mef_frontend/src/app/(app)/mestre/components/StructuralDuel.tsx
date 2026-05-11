'use client';

import { ShieldAlert, Sword, CheckCircle2, AlertCircle, Info, BrainCircuit } from 'lucide-react';
import { useMestreStore } from '@/lib/store-mestre';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export function StructuralDuel() {
  const { calculationTrace } = useMestreStore();
  
  if (!calculationTrace?.duel || calculationTrace.duel.length === 0) return null;

  return (
    <div className="mt-8 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-3">
        <div className="bg-primary/10 p-2 rounded-lg">
          <Sword className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
            O Duelo Estrutural
            <span className="text-[10px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded">AUDITORIA</span>
          </h3>
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-tight">Análise Comparativa: Formulação Clássica vs. Elementos Finitos</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {calculationTrace.duel.map((entry, idx) => {
          const isHighDivergence = Math.abs(entry.difference_percent) > 15;
          const isLowDivergence = Math.abs(entry.difference_percent) < 5;

          return (
            <div key={idx} className="group relative overflow-hidden rounded-2xl border border-border/50 bg-card hover:border-primary/30 transition-all duration-300">
              <div className="absolute top-0 left-0 w-1 h-full bg-primary/20 group-hover:bg-primary transition-colors" />
              
              <div className="p-4 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                {/* Parâmetro */}
                <div className="space-y-1">
                  <span className="text-[9px] font-black uppercase tracking-tighter text-muted-foreground/60">Parâmetro</span>
                  <p className="text-xs font-bold truncate">{entry.parameter}</p>
                </div>

                {/* Valores */}
                <div className="col-span-2 grid grid-cols-2 gap-4">
                  <div className="p-2 rounded-xl bg-muted/30 border border-border/30 text-center">
                    <span className="text-[8px] font-black uppercase tracking-tighter text-muted-foreground block mb-1">Clássico (Analytical)</span>
                    <span className="text-xs font-mono font-bold">{entry.classical_value}</span>
                  </div>
                  <div className="p-2 rounded-xl bg-primary/5 border border-primary/10 text-center">
                    <span className="text-[8px] font-black uppercase tracking-tighter text-primary/70 block mb-1">MEF (Numerical)</span>
                    <span className="text-xs font-mono font-bold text-primary">{entry.mef_value}</span>
                  </div>
                </div>

                {/* Divergência e Insight */}
                <div className="flex items-center justify-between md:justify-end gap-4">
                  <div className={cn(
                    "flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-black tracking-tighter uppercase",
                    isHighDivergence ? "bg-destructive/10 text-destructive" : 
                    isLowDivergence ? "bg-emerald-500/10 text-emerald-500" :
                    "bg-amber-500/10 text-amber-500"
                  )}>
                    {isHighDivergence ? <ShieldAlert className="w-3 h-3" /> : 
                     isLowDivergence ? <CheckCircle2 className="w-3 h-3" /> : 
                     <AlertCircle className="w-3 h-3" />}
                    {entry.difference_percent > 0 ? '+' : ''}{entry.difference_percent.toFixed(1)}%
                  </div>

                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full text-muted-foreground hover:text-primary">
                          <Info className="w-4 h-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent side="left" className="max-w-[280px] p-3 text-[11px] leading-relaxed">
                        <p className="font-bold mb-1 uppercase tracking-widest text-[9px]">Insight Pedagógico</p>
                        {entry.insight}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10 flex gap-4 items-start">
        <div className="mt-1">
          <BrainCircuit className="w-5 h-5 text-primary" />
        </div>
        <div className="space-y-1">
          <p className="text-[11px] font-bold text-primary uppercase tracking-widest">Nota da Auditoria</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Divergências entre métodos clássicos e numéricos são comuns e esperadas devido a simplificações geométricas, consideração de deformação por cisalhamento (Mindlin) e refinamento de malha. O Atlas utiliza estas diferenças para aprofundar seu entendimento fenomenológico.
          </p>
        </div>
      </div>
    </div>
  );
}
