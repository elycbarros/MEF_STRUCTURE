import { useMestreStore } from '@/lib/store-mestre';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Square, Microscope, Info, Calculator, Brain } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { StructuralDuel } from './StructuralDuel';
import { useCallback } from 'react';
import { calculateSpecialElement } from '@/lib/api-mestre';
import { extractMestreSteps, type MestreParams } from '@/lib/mestre-types';

import { MestreDiagram } from './MestreDiagram';
import { SoilProfileVisualizer } from './SoilProfileVisualizer';

export function FootingPlayground() {
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

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      const data = await calculateSpecialElement('footing', currentParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError("Falha na análise da sapata.");
      }
    } catch {
      setError("Erro de conexão com o motor.");
    } finally {
      setIsLoading(false);
    }
  }, [setCalculationTrace, setIsLoading, setPedagogicalSteps, setError, setFullResults]);

  const updateParam = (key: keyof MestreParams, value: string) => {
    const val = parseFloat(value);
    if (!isNaN(val)) {
      updateParams({ [key]: val });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Square className="w-5 h-5 text-primary" />
          Dimensionamento de Sapata
        </h3>
        <div className="flex gap-2">
           <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
             <Info className="w-4 h-4" />
           </Button>
        </div>
      </div>

      <div className="space-y-4">
        {/* Seção 1: Geotecnia */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Microscope className="w-3 h-3" />
              Solo e Carregamento
            </h4>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="Nd" className="text-xs text-muted-foreground">Carga Axial Nd (kN)</Label>
              <Input 
                id="Nd" 
                type="number" 
                value={params.Nd} 
                onChange={(e) => updateParam('Nd', e.target.value)}
                className="h-9 bg-background/50 font-mono text-primary font-bold"
              />
            </div>
            
            <div className="space-y-1.5">
              <Label htmlFor="sigma_adm" className="text-xs text-muted-foreground">Tensão Adm. (kPa)</Label>
              <Input 
                id="sigma_adm" 
                type="number" 
                value={params.sigma_adm} 
                onChange={(e) => updateParam('sigma_adm', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
          </div>

          <SoilProfileVisualizer />

          <div className="space-y-1.5 pt-2 border-t border-primary/5">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-[10px] font-bold text-orange-600 uppercase">Análise Não-Linear (ISE)</Label>
                <p className="text-[8px] text-muted-foreground leading-tight">Plastificação do solo via Winkler Não-Linear</p>
              </div>
              <Switch 
                checked={params.is_nonlinear_isi || false} 
                onCheckedChange={(val) => updateParams({ is_nonlinear_isi: val })} 
              />
            </div>
          </div>
        </div>

        {/* Seção 2: Estrutura */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Calculator className="w-3 h-3" />
            Geometria do Pilar e Concreto
          </h4>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="ap" className="text-[10px] text-muted-foreground uppercase">Pilar Lado A (m)</Label>
              <Input 
                id="ap" 
                type="number" 
                step="0.05"
                value={params.ap} 
                onChange={(e) => updateParam('ap', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="bp" className="text-[10px] text-muted-foreground uppercase">Pilar Lado B (m)</Label>
              <Input 
                id="bp" 
                type="number" 
                step="0.05"
                value={params.bp} 
                onChange={(e) => updateParam('bp', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="fck" className="text-xs text-muted-foreground">Concreto fck (MPa)</Label>
            <Input 
              id="fck" 
              type="number" 
              value={params.fck} 
              onChange={(e) => updateParam('fck', e.target.value)}
              className="h-9 bg-background/50"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        <Button 
          onClick={() => handleCalculate(params)} 
          className="flex-1 macos-button h-11 gap-2"
          disabled={isLoading}
        >
          <Calculator className="w-4 h-4" />
          {isLoading ? 'Calculando...' : 'Recalcular'}
        </Button>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      {fullResults?.sigma_max_kPa && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Microscope className="w-3 h-3" />
            Resumo Geotécnico
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="Pressão Máx (kPa)" value={fullResults.sigma_max_kPa.toFixed(1)} />
            <MetricCard label="Status Solo" value={fullResults.status_geotech || fullResults.status} color={fullResults.status_geotech === 'ELÁSTICO' || fullResults.status === 'OK' ? 'text-emerald-500' : 'text-orange-500'} />
            {fullResults.is_nonlinear_isi && (
              <MetricCard 
                label="Plastificação" 
                value={`${((fullResults.isi_details?.plastification_ratio || 0) * 100).toFixed(1)}%`} 
                color={fullResults.isi_details?.plastification_ratio > 0 ? 'text-orange-500' : 'text-emerald-500'}
              />
            )}
          </div>
        </div>
      )}

      {fullResults?.sigma_max_kPa && (
        <MestreDiagram
          title="Distribuição de Pressões no Solo"
          unit="kPa"
          color="#10b981"
          fillColor="rgba(16, 185, 129, 0.1)"
          totalLength={fullResults.A_m || 2}
          points={[
            { x: 0, y: fullResults.sigma_max_kPa },
            { x: fullResults.A_m / 2, y: fullResults.sigma_max_kPa },
            { x: fullResults.A_m, y: fullResults.sigma_max_kPa },
          ]}
        />
      )}
      
      <StructuralDuel />

      <p className="text-[10px] text-muted-foreground/60 text-center leading-relaxed px-4">
        Cálculo normativo baseado na NBR 6118:2023 e NBR 6122.
        Resultados em tempo real via Atlas Core.
      </p>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: any; color?: string }) { // eslint-disable-line @typescript-eslint/no-explicit-any
  return (
    <div className="p-3 rounded-xl bg-background/50 border border-border/50">
      <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">{label}</p>
      <p className={`mt-1 text-sm font-black ${color || 'text-foreground'}`}>{value}</p>
    </div>
  );
}
