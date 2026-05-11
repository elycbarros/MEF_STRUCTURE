'use client';

import { useCallback } from 'react';
import { Wind, Calculator, Gauge, Shield, Box, Brain, Activity } from 'lucide-react';

import { calculateWind } from '@/lib/api-mestre';
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


import { MestreDiagram } from './MestreDiagram';

export function WindPlayground() {
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
      const data = await calculateWind(currentParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError("Falha no cálculo de vento.");
      }
    } catch {
      setError("Erro de conexão com o motor NBR 6123.");
    } finally {
      setIsLoading(false);
    }
  }, [setCalculationTrace, setIsLoading, setPedagogicalSteps, setError, setFullResults]);

  const updateNumber = (key: keyof MestreParams, value: string) => {
    const parsed = Number(value);
    if (!Number.isNaN(parsed)) updateParams({ [key]: parsed });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Wind className="w-5 h-5 text-primary" />
          Vento (NBR 6123)
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      <div className="space-y-4">
        {/* Velocidade e Topografia */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Gauge className="w-3 h-3" />
            Velocidade e Fatores
          </h4>

          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Velocidade Básica V0 (m/s)</Label>
              <Input 
                type="number" 
                value={params.v0 ?? 30} 
                onChange={(e) => updateNumber('v0', e.target.value)} 
                className="h-9 bg-background/50 font-mono font-bold text-primary" 
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Fator S1 (Topográfico)</Label>
                <Input type="number" step="0.1" value={params.s1 ?? 1.0} onChange={(e) => updateNumber('s1', e.target.value)} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Fator S3 (Estatístico)</Label>
                <Input type="number" step="0.1" value={params.s3 ?? 1.0} onChange={(e) => updateNumber('s3', e.target.value)} className="h-9 bg-background/50" />
              </div>
            </div>
          </div>
        </div>

        {/* Geometria e Rugosidade */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Box className="w-3 h-3" />
            Rugosidade e Geometria
          </h4>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura Total (m)</Label>
                <Input type="number" value={params.height ?? 15} onChange={(e) => updateNumber('height', e.target.value)} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Largura Exposta (m)</Label>
                <Input type="number" value={params.width_x ?? 10} onChange={(e) => updateNumber('width_x', e.target.value)} className="h-9 bg-background/50" />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Categoria de Rugosidade</Label>
              <Select value={(params.categoria ?? 2).toString()} onValueChange={(value) => updateNumber('categoria', value)}>
                <SelectTrigger className="h-9 bg-background/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Cat I (Mar, campos planos)</SelectItem>
                  <SelectItem value="2">Cat II (Campos com obstáculos)</SelectItem>
                  <SelectItem value="3">Cat III (Vilotas, subúrbios)</SelectItem>
                  <SelectItem value="4">Cat IV (Cidades densas)</SelectItem>
                  <SelectItem value="5">Cat V (Centros metropolitanos)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Efeitos Dinâmicos */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Activity className="w-3 h-3" />
              Análise Dinâmica
            </h4>
            <input 
              type="checkbox"
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
              checked={params.is_dynamic ?? false} 
              onChange={(e) => updateParams({ is_dynamic: e.target.checked })} 
            />
          </div>

          {params.is_dynamic && (
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Freq. f1 (Hz)</Label>
                <Input type="number" step="0.1" value={params.f1 ?? 0.5} onChange={(e) => updateNumber('f1', e.target.value)} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Zeta (Amort.)</Label>
                <Input type="number" step="0.01" value={params.zeta ?? 0.01} onChange={(e) => updateNumber('zeta', e.target.value)} className="h-9 bg-background/50" />
              </div>
            </div>
          )}
        </div>
      </div>

      <Button onClick={() => handleCalculate(params)} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Analisando Ventos...' : 'Calcular Forças'}
      </Button>

      {fullResults?.profile && (
        <MestreDiagram
          title="Perfil de Pressão Dinâmica (q)"
          unit="Pa"
          color="#3b82f6"
          fillColor="rgba(59, 130, 246, 0.1)"
          totalLength={params.height || 30}
          points={fullResults.profile.map((p: any) => ({ x: p.z, y: p.q_Pa }))} // eslint-disable-line @typescript-eslint/no-explicit-any
        />
      )}

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <Shield className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}
