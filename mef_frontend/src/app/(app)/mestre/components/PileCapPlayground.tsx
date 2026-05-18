import { useCallback } from 'react';
import { Calculator, Cuboid, Diameter, Ruler, TriangleAlert } from 'lucide-react';

import { calculateSpecialElement } from '@/lib/api-mestre';
import { type MestreParams } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export function PileCapPlayground() {
  const { params, updateParams, setIsLoading, setError, applyMestreResponse, isLoading, error } = useMestreStore();

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      setError(null);
      const data = await calculateSpecialElement('pile_cap', currentParams);
      if (data.success) {
        applyMestreResponse(data);
      } else {
        setError('Falha na análise do bloco sobre estacas.');
      }
    } catch {
      setError('Erro de conexão com o motor.');
    } finally {
      setIsLoading(false);
    }
  }, [applyMestreResponse, setError, setIsLoading]);

  const updateNumber = (key: keyof MestreParams, value: string) => {
    const parsed = Number(value);
    if (!Number.isNaN(parsed)) updateParams({ [key]: parsed });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Cuboid className="w-5 h-5 text-primary" />
          Bloco sobre Estacas
        </h3>
      </div>

      <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
          <Ruler className="w-3 h-3" />
          Geometria do bloco
        </h4>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Distância entre estacas (m)</Label>
            <Input type="number" step="0.05" value={params.dist_piles ?? 1.6} onChange={(e) => updateNumber('dist_piles', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Altura útil d (m)</Label>
            <Input type="number" step="0.05" value={params.d_height ?? 0.65} onChange={(e) => updateNumber('d_height', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Pilar ap (m)</Label>
            <Input type="number" step="0.05" value={params.ap} onChange={(e) => updateNumber('ap', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Pilar bp (m)</Label>
            <Input type="number" step="0.05" value={params.bp} onChange={(e) => updateNumber('bp', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>
      </div>

      <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
          <Diameter className="w-3 h-3" />
          Estacas e materiais
        </h4>

        <div className="space-y-1.5">
          <Label className="text-xs text-muted-foreground">Carga axial Nd (kN)</Label>
          <Input type="number" value={params.Nd} onChange={(e) => updateNumber('Nd', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Ø estaca (m)</Label>
            <Input type="number" step="0.05" value={params.diam_pile ?? 0.4} onChange={(e) => updateNumber('diam_pile', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
            <Input type="number" value={params.fck} onChange={(e) => updateNumber('fck', e.target.value)} className="h-9 bg-background/50" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">fyk (MPa)</Label>
            <Input type="number" value={params.fyk ?? 500} onChange={(e) => updateNumber('fyk', e.target.value)} className="h-9 bg-background/50" />
          </div>
        </div>
      </div>

      <Button onClick={() => handleCalculate(params)} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Calculando...' : 'Dimensionar Bloco'}
      </Button>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <TriangleAlert className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}
