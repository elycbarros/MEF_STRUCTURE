'use client';

import { useCallback, useState } from 'react';
import { Zap, Calculator, Activity, Ruler, ShieldCheck, Info } from 'lucide-react';

import { calculateSpecialElement } from '@/lib/api-mestre';
import { extractMestreSteps } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function TensionProPlayground() {
  const { 
    params, 
    updateParams, 
    setIsLoading, 
    setPedagogicalSteps, 
    setError, 
    setCalculationTrace, 
    setFullResults,
    fullResults,
    isLoading,
    error 
  } = useMestreStore();

  const [tensionParams, setTensionParams] = useState({
    span: params.L || 10.0,
    q_service: params.q || 20.0,
    p0: params.p0 || 1200.0, // kN
    eccentricity: params.ecc || 0.15, // m
    cable_type: 'bonded'
  });

  const updateParam = (key: string, value: string) => {
    const val = Number(value);
    if (!isNaN(val)) {
      setTensionParams(prev => ({ ...prev, [key]: val }));
      updateParams({ [key]: val });
    }
  };

  const handleCalculate = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await calculateSpecialElement('tension_pro', tensionParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError("Falha na análise de protensão.");
      }
    } catch (err: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
      setError(err.message || "Erro no motor Tension Pro.");
    } finally {
      setIsLoading(false);
    }
  }, [tensionParams, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, setFullResults]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary" />
          Tension Pro (Protensão)
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Info className="w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Ruler className="w-3 h-3" />
            Geometria e Cabo
          </h4>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Vão Livre (m)</Label>
            <Input type="number" value={tensionParams.span} onChange={(e) => updateParam('span', e.target.value)} className="h-9 bg-background/50" />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Excentricidade no Vão (m)</Label>
            <Input type="number" step="0.01" value={tensionParams.eccentricity} onChange={(e) => updateParam('eccentricity', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>

        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Activity className="w-3 h-3" />
            Força e Carga
          </h4>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Força Inicial P0 (kN)</Label>
            <Input type="number" value={tensionParams.p0} onChange={(e) => updateParam('p0', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Carga em Serviço (kN/m)</Label>
            <Input type="number" value={tensionParams.q_service} onChange={(e) => updateParam('q_service', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>
      </div>

      <Button onClick={handleCalculate} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Calculando Protensão...' : 'Dimensionar Protensão'}
      </Button>

      {fullResults?.summary && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <ShieldCheck className="w-3 h-3" />
            Verificações de Protensão
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <MetricCard label="Carga Eq. (kN/m)" value={fullResults.summary.q_eq?.toFixed(2)} />
            <MetricCard label="Perdas Imed. (%)" value={fullResults.summary.losses_percent?.toFixed(1)} />
            <MetricCard label="Balanço (%)" value={fullResults.summary.balance_ratio?.toFixed(0)} />
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <ShieldCheck className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: any }) { // eslint-disable-line @typescript-eslint/no-explicit-any
  return (
    <div className="p-3 rounded-xl bg-background/50 border border-border/50">
      <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">{label}</p>
      <p className="mt-1 text-sm font-black text-foreground">{value}</p>
    </div>
  );
}
