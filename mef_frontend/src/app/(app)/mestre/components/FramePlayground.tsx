'use client';

import { useCallback, useState } from 'react';
import { GitBranch, Calculator, Ruler, Layers, ShieldCheck, Info } from 'lucide-react';

import { analyzeMestreFrame } from '@/lib/api-mestre';
import { extractMestreSteps } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MestreSystemDiagram } from './MestreDiagram';

export function FramePlayground() {
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

  // Local state for frame configuration
  const [frameConfig, setFrameConfig] = useState({
    n_bays: params.n_bays ?? 1,
    n_levels: params.n_levels ?? 1,
    bay_width: params.bay_width ?? 5.0,
    level_height: params.level_height ?? 3.0,
    b: params.b ?? 0.20,
    h: params.h ?? 0.50,
    q: params.q ?? 15.0 // kN/m
  });

  const updateConfig = (key: string, value: string) => {
    const val = Number(value);
    if (!isNaN(val)) {
      setFrameConfig(prev => ({ ...prev, [key]: val }));
      updateParams({ [key]: val });
    }
  };

  const handleCalculate = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Generate Nodes, Members, Loads, and Supports
      const nodes = [];
      const members = [];
      const loads = [];
      const supports: Record<string, number[]> = {};

      const { n_bays, n_levels, bay_width, level_height, b, h, q } = frameConfig;

      // Create Nodes
      for (let j = 0; j <= n_levels; j++) {
        for (let i = 0; i <= n_bays; i++) {
          const id = j * (n_bays + 1) + i;
          nodes.push({
            id,
            x: i * bay_width,
            y: 0,
            z: j * level_height
          });

          // Foundation supports
          if (j === 0) {
            supports[id] = [0, 1, 2, 3, 4, 5]; // Fully fixed
          }
        }
      }

      // Create Members
      let memberId = 0;
      for (let j = 0; j <= n_levels; j++) {
        for (let i = 0; i <= n_bays; i++) {
          const curr = j * (n_bays + 1) + i;
          
          // Horizontal beams
          if (i < n_bays && j > 0) {
            const next = curr + 1;
            members.push({
              id: memberId++,
              node_i: curr,
              node_j: next,
              section: { b, h }
            });
            // Simplified: Add load as node forces at the ends
            // In a real MEF we would use distributed loads, but for pedagogical Mestre we'll simplify to node forces for now or add member loads if supported.
            const forceZ = -(q * bay_width) / 2;
            loads.push({ node_id: curr, fz: forceZ });
            loads.push({ node_id: next, fz: forceZ });
          }

          // Vertical columns
          if (j < n_levels) {
            const up = curr + (n_bays + 1);
            members.push({
              id: memberId++,
              node_i: curr,
              node_j: up,
              section: { b, h: b } // Column usually square
            });
          }
        }
      }

      const data = await analyzeMestreFrame(nodes, members, loads, supports);
      
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError("Falha na análise do pórtico.");
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao conectar com o motor de pórticos.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [frameConfig, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, setFullResults]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-primary" />
          Pórtico Espacial (Sistema)
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Info className="w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Geometria do Sistema */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Ruler className="w-3 h-3" />
            Configuração do Sistema
          </h4>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Pavimentos</Label>
              <Input type="number" value={frameConfig.n_levels} onChange={(e) => updateConfig('n_levels', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Vãos (Bays)</Label>
              <Input type="number" value={frameConfig.n_bays} onChange={(e) => updateConfig('n_bays', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Altura do Piso (m)</Label>
              <Input type="number" step="0.1" value={frameConfig.level_height} onChange={(e) => updateConfig('level_height', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Largura do Vão (m)</Label>
              <Input type="number" step="0.1" value={frameConfig.bay_width} onChange={(e) => updateConfig('bay_width', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>
        </div>

        {/* Seção e Cargas */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Layers className="w-3 h-3" />
            Seção e Carregamento
          </h4>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Base b (m)</Label>
              <Input type="number" step="0.05" value={frameConfig.b} onChange={(e) => updateConfig('b', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Altura h (m)</Label>
              <Input type="number" step="0.05" value={frameConfig.h} onChange={(e) => updateConfig('h', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Carga Distribuída q (kN/m)</Label>
            <Input type="number" value={frameConfig.q} onChange={(e) => updateConfig('q', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
          </div>
        </div>
      </div>

      <Button onClick={handleCalculate} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Analisando Estrutura...' : 'Analisar Pórtico'}
      </Button>

      {fullResults?.nodes && (
        <MestreSystemDiagram 
          nodes={fullResults.nodes} 
          members={fullResults.members} 
          title="Configuração do Pórtico e Deformada"
          deformedScale={200}
        />
      )}

      {fullResults?.equilibrium_audit && (
        <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-emerald-600 flex items-center gap-2">
            <ShieldCheck className="w-3 h-3" />
            Verificação de Equilíbrio MEF
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-[8px] uppercase font-bold text-muted-foreground">Erro de Força (kN)</p>
              <p className="text-xs font-mono font-bold text-emerald-600">
                {Math.max(...fullResults.equilibrium_audit.equilibrium_error_kN_m.slice(0,3)).toFixed(6)}
              </p>
            </div>
            <div>
              <p className="text-[8px] uppercase font-bold text-muted-foreground">Erro de Momento (kNm)</p>
              <p className="text-xs font-mono font-bold text-emerald-600">
                {Math.max(...fullResults.equilibrium_audit.equilibrium_error_kN_m.slice(3,6)).toFixed(6)}
              </p>
            </div>
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
