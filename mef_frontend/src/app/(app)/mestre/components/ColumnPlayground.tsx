import { useCallback } from 'react';
import { Calculator, Columns, Crosshair, RotateCw, ShieldCheck } from 'lucide-react';

import { calculateSpecialElement } from '@/lib/api-mestre';
import { type MestreParams } from '@/lib/mestre-types';
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

export function ColumnPlayground() {
  const {
    params,
    updateParams,
    setIsLoading,
    setError,
    applyMestreResponse,
    isLoading,
    error
  } = useMestreStore();

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      setError(null);
      const data = await calculateSpecialElement('column', currentParams);
      if (data.success) {
        const result = data.result && typeof data.result === 'object'
          ? data.result as { summary?: unknown }
          : null;
        applyMestreResponse({
          ...data,
          full_results: result?.summary ?? data.result ?? data,
        });
      } else {
        setError('Falha na análise do pilar.');
      }
    } catch (columnError) {
      setError(columnError instanceof Error ? columnError.message : 'Erro de conexão com o motor.');
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
          <Columns className="w-5 h-5 text-primary" />
          Laboratório de Pilares
        </h3>
      </div>

      <div className="space-y-4">
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Crosshair className="w-3 h-3" />
            Seção e Esbeltez
          </h4>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="col-b-input" className="text-[10px] text-muted-foreground uppercase">Largura b (m)</Label>
              <Input id="col-b-input" type="number" step="0.05" value={params.b} onChange={(e) => updateNumber('b', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="col-h-input" className="text-[10px] text-muted-foreground uppercase">Altura h (m)</Label>
              <Input id="col-h-input" type="number" step="0.05" value={params.h} onChange={(e) => updateNumber('h', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Comprimento livre (m)</Label>
              <Input type="number" step="0.1" value={params.L_free ?? 3} onChange={(e) => updateNumber('L_free', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
              <Input type="number" value={params.fck} onChange={(e) => updateNumber('fck', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>
        </div>

        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <RotateCw className="w-3 h-3" />
            Solicitações de Cálculo
          </h4>

          <div className="space-y-1.5">
            <Label htmlFor="col-nd-input" className="text-xs text-muted-foreground">Carga axial Nd (kN)</Label>
            <Input id="col-nd-input" type="number" value={params.Nd} onChange={(e) => updateNumber('Nd', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="col-mxd-input" className="text-[10px] text-muted-foreground uppercase">Mxd (kNm)</Label>
              <Input id="col-mxd-input" type="number" value={params.Mxd ?? 0} onChange={(e) => updateNumber('Mxd', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="col-myd-input" className="text-[10px] text-muted-foreground uppercase">Myd (kNm)</Label>
              <Input id="col-myd-input" type="number" value={params.Myd ?? 0} onChange={(e) => updateNumber('Myd', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Classe de agressividade</Label>
            <Select value={(params.caa ?? 2).toString()} onValueChange={(value) => updateNumber('caa', value)}>
              <SelectTrigger className="h-9 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">CAA I</SelectItem>
                <SelectItem value="2">CAA II</SelectItem>
                <SelectItem value="3">CAA III</SelectItem>
                <SelectItem value="4">CAA IV</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Button onClick={() => handleCalculate(params)} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Verificando...' : 'Dimensionar Pilar'}
      </Button>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive animate-in fade-in duration-300">
          <ShieldCheck className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}
