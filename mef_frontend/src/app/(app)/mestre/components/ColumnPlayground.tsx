import { useCallback } from 'react';
import { Calculator, Columns, Crosshair, RotateCw, ShieldCheck, Activity } from 'lucide-react';

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

import { MestreFiberMap, MestreInteractionDiagram } from './MestreDiagram';

export function ColumnPlayground() {
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
      setError(null);
      const data = await calculateSpecialElement('column', currentParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError('Falha na análise do pilar.');
      }
    } catch {
      setError('Erro de conexão com o motor.');
    } finally {
      setIsLoading(false);
    }
  }, [setCalculationTrace, setError, setIsLoading, setPedagogicalSteps, setFullResults]);

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
              <Label className="text-[10px] text-muted-foreground uppercase">Largura b (m)</Label>
              <Input type="number" step="0.05" value={params.b} onChange={(e) => updateNumber('b', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Altura h (m)</Label>
              <Input type="number" step="0.05" value={params.h} onChange={(e) => updateNumber('h', e.target.value)} className="h-9 bg-background/50" />
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
            <Label className="text-xs text-muted-foreground">Carga axial Nd (kN)</Label>
            <Input type="number" value={params.Nd} onChange={(e) => updateNumber('Nd', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Mxd (kNm)</Label>
              <Input type="number" value={params.Mxd ?? 0} onChange={(e) => updateNumber('Mxd', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Myd (kNm)</Label>
              <Input type="number" value={params.Myd ?? 0} onChange={(e) => updateNumber('Myd', e.target.value)} className="h-9 bg-background/50" />
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

      {fullResults?.fiber_results?.interaction_diagram_x && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-4 duration-500">
          <MestreInteractionDiagram 
            envelope={fullResults.fiber_results.interaction_diagram_x}
            solicitant={{ n: fullResults.Nd_kN, m: fullResults.Md_x_total_kNm }}
            title="Interação N x Mx (Biaxial X)"
          />
          <MestreInteractionDiagram 
            envelope={fullResults.fiber_results.interaction_diagram_y}
            solicitant={{ n: fullResults.Nd_kN, m: fullResults.Md_y_total_kNm }}
            title="Interação N x My (Biaxial Y)"
          />
        </div>
      )}

      {fullResults?.slenderness && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Activity className="w-3 h-3" />
            Análise de 2ª Ordem e Esbeltez
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard label="λx (Esbeltez)" value={fullResults.slenderness.lambda_x} />
            <MetricCard label="λy (Esbeltez)" value={fullResults.slenderness.lambda_y} />
            <MetricCard label="Mx Total" value={`${fullResults.Md_x_total_kNm} kNm`} />
            <MetricCard label="My Total" value={`${fullResults.Md_y_total_kNm} kNm`} />
          </div>
          <div className="text-[10px] text-muted-foreground font-medium flex items-center gap-2 px-1">
            <span className="w-1.5 h-1.5 rounded-full bg-primary" />
            Método: {fullResults.moments_2nd_order?.method || 'Pilar Padrão (NBR 6118)'}
          </div>
        </div>
      )}

      {fullResults?.fiber_results?.fibers && (
        <MestreFiberMap 
          fibers={fullResults.fiber_results.fibers}
          b={params.b}
          h={params.h}
          title="Mapa de Tensões na Seção"
        />
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
