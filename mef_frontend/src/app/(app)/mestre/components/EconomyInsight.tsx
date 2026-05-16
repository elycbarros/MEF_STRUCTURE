'use client';

import React from 'react';
import { useMestreStore } from '@/lib/store-mestre';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PiggyBank, ArrowDownCircle, Info, Construction } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export function EconomyInsight() {
  const { fullResults } = useMestreStore();
  const cost = fullResults?.cost_analysis;

  if (!cost) return null;

  const { total_cost, breakdown, ratios } = cost;
  const total = breakdown.concrete + breakdown.steel + breakdown.formwork;
  
  const concretePct = (breakdown.concrete / total) * 100;
  const steelPct = (breakdown.steel / total) * 100;
  const formworkPct = (breakdown.formwork / total) * 100;

  return (
    <Card className="overflow-hidden border-emerald-500/20 bg-emerald-500/5 backdrop-blur-sm">
      <CardHeader className="p-4 pb-0">
        <CardTitle className="text-xs font-black uppercase tracking-widest flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
          <PiggyBank className="w-4 h-4" />
          Inteligência de Custo
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 space-y-4">
        {/* Total Cost Display */}
        <div className="flex justify-between items-end">
          <div>
            <p className="text-[10px] uppercase font-bold text-muted-foreground">Custo Estimado Elemento</p>
            <h2 className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
              R$ {total_cost.toLocaleString('pt-BR')}
            </h2>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase font-bold text-muted-foreground">R$ / m</p>
            <p className="text-sm font-bold">R$ {ratios.cost_per_m}</p>
          </div>
        </div>

        {/* Breakdown Progress Bars */}
        <div className="space-y-2">
          <div className="flex justify-between text-[10px] font-bold uppercase">
            <span>Composição de Preço</span>
          </div>
          
          <div className="space-y-1">
            <div className="flex justify-between text-[10px] mb-1">
              <span className="flex items-center gap-1"><Construction className="w-3 h-3"/> Concreto</span>
              <span>{concretePct.toFixed(0)}%</span>
            </div>
            <Progress value={concretePct} className="h-1 bg-emerald-200 dark:bg-emerald-900" indicatorClassName="bg-emerald-500" />
            
            <div className="flex justify-between text-[10px] mb-1 pt-1">
              <span className="flex items-center gap-1"><Info className="w-3 h-3"/> Aço</span>
              <span>{steelPct.toFixed(0)}%</span>
            </div>
            <Progress value={steelPct} className="h-1 bg-blue-200 dark:bg-blue-900" indicatorClassName="bg-blue-500" />

            <div className="flex justify-between text-[10px] mb-1 pt-1">
              <span className="flex items-center gap-1"><Info className="w-3 h-3"/> Fôrmas</span>
              <span>{formworkPct.toFixed(0)}%</span>
            </div>
            <Progress value={formworkPct} className="h-1 bg-orange-200 dark:bg-orange-900" indicatorClassName="bg-orange-500" />
          </div>
        </div>

        {/* Optimization Insight */}
        <div className="bg-emerald-500/10 rounded-lg p-3 border border-emerald-500/20 flex gap-3">
          <ArrowDownCircle className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <h4 className="text-[10px] font-black uppercase text-emerald-700 dark:text-emerald-300">Potencial de Otimização</h4>
            <p className="text-[11px] leading-snug text-emerald-600/80 dark:text-emerald-400/80">
              Taxa de aço: {ratios.steel_per_m3} kg/m³. 
              {ratios.steel_per_m3 > 100 
                ? " Consumo de aço elevado. Tente aumentar a altura (h) da seção para reduzir a armadura e o custo total."
                : " Seção bem otimizada. O equilíbrio entre concreto e aço está dentro da zona de economia máxima."}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
