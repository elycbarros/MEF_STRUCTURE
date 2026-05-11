import { useCallback } from 'react';
import { Calculator, Grid3X3, Layers, Ruler, TriangleAlert } from 'lucide-react';

import { calculateSpecialElement } from '@/lib/api-mestre';
import { extractMestreSteps, type MestreParams } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export function SlabPlayground() {
  const { params, updateParams, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, isLoading, error } = useMestreStore();

  const equivalentSpan = params.Lx ?? params.L;
  const equivalentWidth = params.Ly ?? 4;

  const buildPayload = useCallback((currentParams: MestreParams): MestreParams => ({
    ...currentParams,
    L: currentParams.Lx ?? currentParams.L,
    b: currentParams.Ly ?? currentParams.b,
    h: currentParams.h,
    q: currentParams.q,
  }), []);

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      setError(null);
      const data = await calculateSpecialElement('slab', buildPayload(currentParams));
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
      } else {
        setError('Falha na análise da laje.');
      }
    } catch {
      setError('Erro de conexão com o motor.');
    } finally {
      setIsLoading(false);
    }
  }, [buildPayload, setCalculationTrace, setError, setIsLoading, setPedagogicalSteps]);

  const updateNumber = (key: keyof MestreParams, value: string) => {
    const parsed = Number(value);
    if (!Number.isNaN(parsed)) updateParams({ [key]: parsed });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Grid3X3 className="w-5 h-5 text-primary" />
          Laboratório de Lajes
        </h3>
      </div>

      <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
          <Ruler className="w-3 h-3" />
          Geometria do Painel
        </h4>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Vão Lx (m)</Label>
            <Input type="number" step="0.1" value={equivalentSpan} onChange={(e) => updateNumber('Lx', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Vão Ly (m)</Label>
            <Input type="number" step="0.1" value={equivalentWidth} onChange={(e) => updateNumber('Ly', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Espessura h (m)</Label>
            <Input type="number" step="0.01" value={params.h} onChange={(e) => updateNumber('h', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Tipo</Label>
            <Select value={params.slab_type ?? 'solid'} onValueChange={(value) => updateParams({ slab_type: value as MestreParams['slab_type'] })}>
              <SelectTrigger className="h-9 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="solid">Maciça</SelectItem>
                <SelectItem value="ribbed">Nervurada</SelectItem>
                <SelectItem value="prestressed">Protendida</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
          <Layers className="w-3 h-3" />
          Materiais e Cargas
        </h4>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Carga q (kN/m²)</Label>
            <Input type="number" step="0.5" value={params.q} onChange={(e) => updateNumber('q', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
            <Input type="number" value={params.fck} onChange={(e) => updateNumber('fck', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-3 flex gap-3 text-amber-700 dark:text-amber-300">
        <TriangleAlert className="w-4 h-4 shrink-0 mt-0.5" />
        <p className="text-xs leading-relaxed">
          Modo atual: laje equivalente para memorial didático. O modelo global de placas/radier fica para o Atlas Pro.
        </p>
      </div>

      <Button onClick={() => handleCalculate(params)} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Processando...' : 'Analisar Laje'}
      </Button>

      {error && <p className="text-xs text-destructive font-medium">{error}</p>}
    </div>
  );
}
