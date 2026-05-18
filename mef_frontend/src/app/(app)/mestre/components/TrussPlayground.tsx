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

type TrussTypology = 'warren' | 'howe' | 'pratt' | 'shed' | 'double_shed' | 'fink' | 'fan' | 'q31';

interface TrussConfig {
  typology: TrussTypology;
  span: number;
  height: number;
  panels: number;
  section_area: number;
  q: number;
}

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

  const [trussConfig, setTrussConfig] = useState<TrussConfig>({
    typology: typeof params.truss_type === 'string' ? params.truss_type as TrussTypology : 'warren',
    span: Number(params.L) || 12.0,
    height: Number(params.h) || 1.5,
    panels: Number(params.n_panels) || 6,
    section_area: Number(params.area_cm2) || 15.0,
    q: Number(params.q) || 5.0 // kN at each top node
  });

  const updateConfig = (key: keyof TrussConfig, value: string) => {
    const parsedValue = key === 'typology' ? value as TrussTypology : Number(value);
    if (key !== 'typology' && isNaN(parsedValue as number)) return;

    setTrussConfig(prev => ({ ...prev, [key]: parsedValue }));
    const paramKey = key === 'span' ? 'L' : key === 'height' ? 'h' : key === 'panels' ? 'n_panels' : key;
    updateParams({ [paramKey]: parsedValue });
  };

  const handleCalculate = useCallback(async () => {
    const { typology, span, height, panels, q } = trussConfig;
    
    // Validação de Entrada (ignorar se for a Questão 31 pré-definida)
    if (typology !== 'q31') {
      if (!span || span <= 0 || isNaN(Number(span))) {
        setError("O vão total deve ser maior que zero.");
        return;
      }
      if (!height || height <= 0 || isNaN(Number(height))) {
        setError("A altura da treliça deve ser maior que zero.");
        return;
      }
      if (!panels || panels < 2 || isNaN(Number(panels))) {
        setError("O número de painéis deve ser pelo menos 2.");
        return;
      }
    }

    setIsLoading(true);
    setError(null);
    try {
      const nodes = [];
      const members = [];
      const loads = [];
      const supports: Record<string, number[]> = {};

      const E = 210e9; // Steel
      const section = { b: 0.1, h: 0.1, E }; // Abstract section for truss

      if (typology === 'q31') {
        // Questão 31 Predefined Model (3m wide, 6m tall)
        nodes.push(
          { id: 0, x: 0, y: 0, z: 0 },
          { id: 1, x: 3.0, y: 0, z: 0 },
          { id: 2, x: 0, y: 0, z: 3.0 },
          { id: 3, x: 3.0, y: 0, z: 3.0 },
          { id: 4, x: 0, y: 0, z: 6.0 },
          { id: 5, x: 3.0, y: 0, z: 6.0 }
        );

        members.push(
          { id: 0, node_i: 0, node_j: 1, section },
          { id: 1, node_i: 2, node_j: 3, section },
          { id: 2, node_i: 4, node_j: 5, section },
          { id: 3, node_i: 0, node_j: 2, section },
          { id: 4, node_i: 2, node_j: 4, section },
          { id: 5, node_i: 1, node_j: 3, section },
          { id: 6, node_i: 3, node_j: 5, section },
          { id: 7, node_i: 0, node_j: 3, section },
          { id: 8, node_i: 2, node_j: 5, section }
        );

        supports[0] = [0, 1, 2, 3, 4, 5]; // Node A: Fixed in all directions
        supports[1] = [1, 2, 3, 4, 5];    // Node B: Roller (free in X direction)

        loads.push(
          { node_id: 4, fx: 20000.0 },  // 20 kN horizontal to the right
          { node_id: 5, fz: -20000.0 } // 20 kN vertical downward
        );
      } else {
        const panelWidth = span / panels;

        // 1. Generate Nodes (Bottom and Top chords)
        for (let i = 0; i <= panels; i++) {
          const x = i * panelWidth;
          const bId = i;
          nodes.push({ id: bId, x, y: 0, z: 0 });
          
          const tId = i + panels + 1;
          let zTop = height;
          
          // Custom geometry per typology
          if (typology === 'fink' || typology === 'fan') {
            // Triangular shape
            zTop = (x <= span / 2) ? (2 * height * x / span) : (2 * height * (span - x) / span);
          } else if (typology === 'shed') {
            // Sawtooth shape (sloped)
            zTop = (height * x / span) + (height * 0.5);
          } else if (typology === 'double_shed') {
            // M-shape or double slope
            const mid = span / 2;
            const xRel = x <= mid ? x : x - mid;
            zTop = (height * xRel / (mid / 2)) + (height * 0.5);
            if (xRel > mid / 2) zTop = (height * (mid - xRel) / (mid / 2)) + (height * 0.5);
          }

          nodes.push({ id: tId, x, y: 0, z: zTop });

          // Loads on top chord (Gravity loads)
          const loadFactor = (i === 0 || i === panels) ? 0.5 : 1.0;
          loads.push({ node_id: tId, fz: -q * loadFactor * 1000.0 }); // API expects Newtons
        }

        // 2. Generate Supports
        supports[0] = [0, 1, 2, 3, 4, 5];
        supports[panels] = [1, 2, 4, 5];

        // 3. Generate Members
        let mId = 0;
        for (let i = 0; i < panels; i++) {
          const b1 = i;
          const b2 = i + 1;
          const t1 = i + panels + 1;
          const t2 = i + panels + 2;

          // Banzos
          members.push({ id: mId++, node_i: b1, node_j: b2, section });
          members.push({ id: mId++, node_i: t1, node_j: t2, section });
          
          // Verticais
          members.push({ id: mId++, node_i: b1, node_j: t1, section });
          if (i === panels - 1) {
            members.push({ id: mId++, node_i: b2, node_j: t2, section });
          }

          // Diagonais - Lógica por Typologia
          if (typology === 'warren') {
            if (i % 2 === 0) members.push({ id: mId++, node_i: b1, node_j: t2, section });
            else members.push({ id: mId++, node_i: t1, node_j: b2, section });
          } else if (typology === 'howe') {
            if (i < panels / 2) members.push({ id: mId++, node_i: b1, node_j: t2, section });
            else members.push({ id: mId++, node_i: t1, node_j: b2, section });
          } else if (typology === 'pratt') {
            if (i < panels / 2) members.push({ id: mId++, node_i: t1, node_j: b2, section });
            else members.push({ id: mId++, node_i: b1, node_j: t2, section });
          } else if (typology === 'shed' || typology === 'double_shed') {
            members.push({ id: mId++, node_i: b1, node_j: t2, section });
          } else if (typology === 'fink') {
            if (i < panels / 2) {
               if (i % 2 === 0) members.push({ id: mId++, node_i: b1, node_j: t2, section });
               else members.push({ id: mId++, node_i: b2, node_j: t1, section });
            } else {
               if (i % 2 === 0) members.push({ id: mId++, node_i: b2, node_j: t1, section });
               else members.push({ id: mId++, node_i: b1, node_j: t2, section });
            }
          } else if (typology === 'fan') {
            const midPanel = Math.floor(panels / 2);
            if (i < midPanel) members.push({ id: mId++, node_i: 0, node_j: t2, section });
            else members.push({ id: mId++, node_i: panels, node_j: t1, section });
          }
        }
      }

      const data = await analyzeMestreFrame(nodes, members, loads, supports, true);
      
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
        
        // Map results to nodes for visualization (Crucial for deformed diagram)
        const resultNodes = nodes.map(n => {
          // Displacements are keyed by stringified node ID in the API response
          const disp = data.displacements[String(n.id)] || [0, 0, 0, 0, 0, 0];
          return {
            ...n,
            dx: disp[0],
            dy: disp[1],
            dz: disp[2]
          };
        });
        
        setFullResults({
          ...data,
          nodes: resultNodes,
          members: members
        });
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
                <SelectItem value="double_shed">Double Shed</SelectItem>
                <SelectItem value="fink">Fink (Industrial)</SelectItem>
                <SelectItem value="fan">Fan Truss</SelectItem>
                <SelectItem value="q31" className="font-semibold text-primary">Questão 31 (Provão)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Vão Total (m)</Label>
              <Input type="number" value={trussConfig.span} onChange={(e) => updateConfig('span', e.target.value)} disabled={trussConfig.typology === 'q31'} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
              <Input type="number" step="0.1" value={trussConfig.height} onChange={(e) => updateConfig('height', e.target.value)} disabled={trussConfig.typology === 'q31'} className="h-9 bg-background/50" />
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
              <Input type="number" value={trussConfig.panels} onChange={(e) => updateConfig('panels', e.target.value)} disabled={trussConfig.typology === 'q31'} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Carga por Nó (kN)</Label>
              <Input type="number" value={trussConfig.q} onChange={(e) => updateConfig('q', e.target.value)} disabled={trussConfig.typology === 'q31'} className="h-9 bg-background/50 font-mono font-bold text-primary" />
            </div>
          </div>
        </div>
      </div>

      {trussConfig.typology === 'q31' && (
        <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 text-xs text-muted-foreground font-medium flex gap-3 items-start animate-in fade-in slide-in-from-top-2 duration-300">
          <Info className="w-5 h-5 text-primary shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="text-primary block text-sm">Questão 31 - Concurso Engenharia Estrutural</strong>
            <p className="leading-relaxed">
              Modelagem exata de treliça vertical de 3.0 m de largura e 6.0 m de altura.
              O nó 0 (Apoio A) é <strong>fixo</strong> e o nó 1 (Apoio B) é <strong>móvel</strong>.
              Força horizontal de <strong>20.0 kN (→)</strong> aplicada no nó E (4) e força vertical de <strong>20.0 kN (↓)</strong> aplicada no nó F (5).
            </p>
          </div>
        </div>
      )}

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
          reactions={fullResults.equilibrium_audit?.reactions || {}}
          efforts={fullResults.efforts || {}}
        />
      )}

      {fullResults?.efforts && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-4">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Layers className="w-3 h-3 text-primary" />
            Esforços Axiais nas Barras (kN)
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-60 overflow-y-auto pr-1">
            {fullResults.members.map((m: any) => {
              const eff = fullResults.efforts[m.id] || { i: { N: 0 } };
              const nForce = eff.i.N;
              
              let typeLabel = "Nulo";
              let badgeColor = "bg-muted text-muted-foreground border-muted-foreground/20";
              
              if (nForce > 0.01) {
                typeLabel = "Tração";
                badgeColor = "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
              } else if (nForce < -0.01) {
                typeLabel = "Compressão";
                badgeColor = "bg-rose-500/10 text-rose-500 border-rose-500/20";
              }
              
              return (
                <div key={m.id} className="flex items-center justify-between p-2 rounded-lg bg-background/50 border border-border/40 text-[11px] font-medium">
                  <div className="flex flex-col gap-0.5">
                    <span className="text-[10px] font-bold text-muted-foreground">Barra {m.id}</span>
                    <span className="text-muted-foreground font-mono">Nó {m.node_i} → Nó {m.node_j}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs">{nForce.toFixed(2)} kN</span>
                    <span className={`px-1.5 py-0.5 rounded-md text-[9px] font-black uppercase tracking-tighter border ${badgeColor}`}>
                      {typeLabel}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
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
