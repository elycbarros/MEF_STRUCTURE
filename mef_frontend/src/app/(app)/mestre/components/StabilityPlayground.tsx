import { useMestreStore } from '@/lib/store-mestre';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Wind, Activity, Calculator, Brain, Building2, Ruler, Shield } from 'lucide-react';
import { useCallback } from 'react';
import { calculateStability } from '@/lib/api-mestre';
import { extractMestreSteps, type MestreParams } from '@/lib/mestre-types';

export function StabilityPlayground() {
  const { params, updateParams, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, setFullResults, isLoading, error } = useMestreStore();

  const updateParam = (key: string, value: string | number) => {
    const val = typeof value === 'string' ? parseFloat(value) : value;
    if (typeof val === 'number' && isNaN(val)) return;
    updateParams({ [key]: val });
  };

  const handleCalculate = useCallback(async (p: Partial<MestreParams>) => {
    setIsLoading(true);
    setError(null);
    try {
      const stabilityParams = {
        v0: Number(p.v0 || 30.0),
        height: Number(p.height || 30.0),
        width_x: Number(p.width_x || 12.0)
      };

      const data = await calculateStability(stabilityParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? {
          requested_type: 'stability',
          solver_module: 'WindEngine.estimate_gamma_z',
          blackboard_builder: 'build_stability_blackboard',
          classical_check: true,
          mef_check: false
        });
        setFullResults(data.result ?? data);
      } else {
        setError("Falha na análise de estabilidade.");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro de conexão com o motor de vento/estabilidade.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [setCalculationTrace, setFullResults, setIsLoading, setPedagogicalSteps, setError]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          Estabilidade Global (γz)
        </h3>
      </div>

      <div className="space-y-4">
        {/* Parâmetros da Edificação */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Building2 className="w-3 h-3" />
            Geometria do Edifício
          </h4>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                <Ruler className="w-3 h-3" />
                Altura Total (m)
              </Label>
              <Input 
                type="number" 
                value={params.height || 30.0} 
                onChange={(e) => updateParam('height', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                <Ruler className="w-3 h-3" />
                Largura X (m)
              </Label>
              <Input 
                type="number" 
                value={params.width_x || 12.0} 
                onChange={(e) => updateParam('width_x', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
          </div>
        </div>

        {/* Parâmetros de Vento */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Wind className="w-3 h-3" />
            Vento (NBR 6123)
          </h4>
          
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Velocidade Básica V0 (m/s)</Label>
            <Input 
              type="number" 
              value={params.v0 || 30.0} 
              onChange={(e) => updateParam('v0', e.target.value)}
              className="h-9 bg-background/50 font-mono font-bold text-primary"
            />
            <p className="text-[9px] text-muted-foreground italic">Ex: 30 a 50 m/s conforme região do Brasil</p>
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
          {isLoading ? 'Calculando...' : 'Estimar γz'}
        </Button>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <Shield className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}
