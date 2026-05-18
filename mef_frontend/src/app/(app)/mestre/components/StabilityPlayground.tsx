import { useMestreStore } from '@/lib/store-mestre';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Wind, Activity, Calculator, Brain, Building2, Ruler, Shield } from 'lucide-react';
import { useCallback } from 'react';
import { calculateStability } from '@/lib/api-mestre';
import { type MestreParams } from '@/lib/mestre-types';

export function StabilityPlayground() {
  const { params, updateParams, setIsLoading, setError, applyMestreResponse, isLoading, error } = useMestreStore();

  const paramNumber = (value: unknown, fallback: number) => {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
  };

  const updateParam = (key: string, value: string | number) => {
    const val = typeof value === 'string' ? parseFloat(value) : value;
    if (typeof val === 'number' && isNaN(val)) return;
    updateParams({ [key]: val });
  };

  const handleCalculate = useCallback(async (p: Partial<MestreParams>) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await calculateStability(p);
      if (data.success) {
        applyMestreResponse({
          ...data,
          calculation_trace: data.calculation_trace ?? {
            requested_type: 'stability',
            solver_module: 'WindEngine.estimate_gamma_z',
            blackboard_builder: 'build_stability_blackboard',
            classical_check: true,
            mef_check: false
          },
          full_results: data.result ?? data,
        });
      } else {
        setError("Falha na análise de estabilidade.");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro de conexão com o motor de vento/estabilidade.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [applyMestreResponse, setIsLoading, setError]);

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
            Geometria e Massa
          </h4>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">Altura Total (m)</Label>
              <Input type="number" value={paramNumber(params.height, 30.0)} onChange={(e) => updateParam('height', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">Frequência f1 (Hz)</Label>
              <Input type="number" step="0.1" value={paramNumber(params.f1_hz, 0.5)} onChange={(e) => updateParam('f1_hz', e.target.value)} className="h-9 bg-background/50 font-bold" />
            </div>
          </div>
        </div>

        {/* Parâmetros de Vento Dinâmico */}
        <div className="space-y-4 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-emerald-600 flex items-center gap-2">
            <Wind className="w-3 h-3" />
            Vento Dinâmico (NBR 6123)
          </h4>
          
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase font-bold">V0 (m/s)</Label>
              <Input type="number" value={paramNumber(params.v0, 30.0)} onChange={(e) => updateParam('v0', e.target.value)} className="h-9 bg-background/50" />
            </div>
            
            <div className="flex items-center justify-between p-2 rounded-lg bg-background/40 border border-emerald-500/10">
              <span className="text-[10px] font-bold uppercase text-emerald-700">Modo Dinâmico (Davenport)</span>
              <input 
                type="checkbox" 
                checked={Boolean(params.is_dynamic)} 
                onChange={(e) => updateParam('is_dynamic', e.target.checked ? 1 : 0)}
                className="w-4 h-4 accent-emerald-500"
              />
            </div>

            <div className="flex items-center justify-between p-2 rounded-lg bg-background/40 border border-blue-500/10">
              <span className="text-[10px] font-bold uppercase text-blue-700">Análise Sísmica (NBR 15421)</span>
              <input 
                type="checkbox" 
                checked={Boolean(params.check_seismic)} 
                onChange={(e) => updateParam('check_seismic', e.target.checked ? 1 : 0)}
                className="w-4 h-4 accent-blue-500"
              />
            </div>
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
