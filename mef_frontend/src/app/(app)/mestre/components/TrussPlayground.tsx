'use client';

import { useCallback, useState } from 'react';
import { Network, Calculator, Activity, Layers, ShieldCheck, Info } from 'lucide-react';

import { analyzeMestreFrame } from '@/lib/api-mestre';
import { extractMestreSteps } from '@/lib/mestre-types';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MestreSystemDiagram } from './MestreDiagram';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type TrussTypology = 'warren' | 'howe' | 'pratt' | 'shed';

export function TrussPlayground() {
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

  const [trussConfig, setTrussConfig] = useState({
    typology: (params.truss_type as TrussTypology) || 'warren',
    span: params.L || 12.0,
    height: params.h || 1.5,
    panels: params.n_panels || 6,
    section_area: params.area_cm2 || 15.0,
    q: params.q || 5.0 // kN at each top node
  });

  const updateConfig = (key: string, value: string | number) => {
    setTrussConfig(prev => ({ ...prev, [key]: value }));
    updateParams({ [key]: value });
  };

  const handleCalculate = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { typology, span, height, panels, q } = trussConfig;
      const nodes = [];
      const members = [];
      const loads = [];
      const supports: Record<string, number[]> = {};

      const panelWidth = span / panels;
      const E = 210e9; // Steel
      const section = { b: 0.1, h: 0.1, E }; // Abstract section for truss

      // 1. Generate Nodes (Bottom and Top chords)
      for (let i = 0; i <= panels; i++) {
        // Bottom chord
        const bId = i;
        nodes.push({ id: bId, x: i * panelWidth, y: 0, z: 0 });
        
        // Top chord
        const tId = i + panels + 1;
        nodes.push({ id: tId, x: i * panelWidth, y: 0, z: height });

        // Loads on top chord
        if (i > 0 && i < panels) {
           loads.push({ node_id: tId, fz: -q });
        } else {
           loads.push({ node_id: tId, fz: -q/2 });
        }
      }

      // 2. Generate Supports
      supports[0] = [0, 1, 2]; // Pinned
      supports[panels] = [1, 2]; // Roller (Z fixed, Y fixed, X free)

      // 3. Generate Members
      let mId = 0;
      for (let i = 0; i < panels; i++) {
        const b1 = i;
        const b2 = i + 1;
        const t1 = i + panels + 1;
        const t2 = i + panels + 2;

        // Bottom chord
        members.push({ id: mId++, node_i: b1, node_j: b2, section });
        // Top chord
        members.push({ id: mId++, node_i: t1, node_j: t2, section });
        // Verticals
        members.push({ id: mId++, node_i: b1, node_j: t1, section });
        if (i === panels - 1) {
          members.push({ id: mId++, node_i: b2, node_j: t2, section });
        }

        // Diagonals
        if (typology === 'warren') {
          if (i % 2 === 0) {
            members.push({ id: mId++, node_i: b1, node_j: t2, section });
          } else {
            members.push({ id: mId++, node_i: t1, node_j: b2, section });
          }
        } else if (typology === 'howe') {
          if (i < panels / 2) {
            members.push({ id: mId++, node_i: b1, node_j: t2, section });
          } else {
            members.push({ id: mId++, node_i: t1, node_j: b2, section });
          }
        } else if (typology === 'pratt') {
          if (i < panels / 2) {
            members.push({ id: mId++, node_i: t1, node_j: b2, section });
          } else {
            members.push({ id: mId++, node_i: b1, node_j: t2, section });
          }
        }
      }

      const data = await analyzeMestreFrame(nodes, members, loads, supports);
      
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        setFullResults(data);
      } else {
        setError("Falha na análise da treliça.");
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Erro no motor de treliças.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [trussConfig, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, setFullResults]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Network className="w-5 h-5 text-primary" />
          Treliça Paramétrica (Sistema)
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Info className="w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Layers className="w-3 h-3" />
            Tipologia e Geometria
          </h4>

          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Tipo de Treliça</Label>
            <Select value={trussConfig.typology} onValueChange={(val) => updateConfig('typology', val)}>
              <SelectTrigger className="h-9 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="warren">Warren</SelectItem>
                <SelectItem value="howe">Howe</SelectItem>
                <SelectItem value="pratt">Pratt</SelectItem>
                <SelectItem value="shed">Shed (Sawtooth)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Vão Total (m)</Label>
              <Input type="number" value={trussConfig.span} onChange={(e) => updateConfig('span', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
              <Input type="number" step="0.1" value={trussConfig.height} onChange={(e) => updateConfig('height', e.target.value)} className="h-9 bg-background/50" />
            </div>
          </div>
        </div>

        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Activity className="w-3 h-3" />
            Discretização e Carga
          </h4>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Nº de Painéis</Label>
              <Input type="number" value={trussConfig.panels} onChange={(e) => updateConfig('panels', e.target.value)} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Carga por Nó (kN)</Label>
              <Input type="number" value={trussConfig.q} onChange={(e) => updateConfig('q', e.target.value)} className="h-9 bg-background/50 font-mono font-bold text-primary" />
            </div>
          </div>
        </div>
      </div>

      <Button onClick={handleCalculate} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Calculando Treliça...' : 'Dimensionar Treliça'}
      </Button>

      {fullResults?.nodes && (
        <MestreSystemDiagram 
          nodes={fullResults.nodes} 
          members={fullResults.members} 
          title="Esquema da Treliça e Deformada"
          deformedScale={500}
        />
      )}

      {fullResults?.equilibrium_audit && (
        <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-emerald-600 flex items-center gap-2">
            <ShieldCheck className="w-3 h-3" />
            Auditoria de Esforços
          </h4>
          <div className="text-[10px] text-muted-foreground font-medium leading-relaxed">
            Equilíbrio Nodal verificado com resíduo de {Math.max(...fullResults.equilibrium_audit.equilibrium_error_kN_m).toFixed(8)} kN.
            Análise via MEF de Barras (Deslocamentos).
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
