import { useState, useCallback } from 'react';
import { useMestreStore } from '@/lib/store-mestre';
import { calculateSpecialElement } from '@/lib/api-mestre';
import { extractMestreSteps, type BeamSupport, type DistributedLoad, type MestreParams, type PointLoad, type SupportType, type MestreApiResponse } from '@/lib/mestre-types';
import { MestreDiagram } from './MestreDiagram';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { 
  Box, 
  Calculator, 
  Brain, 
  Ruler, 
  TriangleAlert, 
  Plus, 
  Trash2, 
  Settings2,
  Anchor,
  ArrowDown
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';

export function BeamPlayground() {
  const { 
    params, 
    updateParams, 
    setPedagogicalSteps, 
    setIsLoading, 
    setError,
    setCalculationTrace,
    error,
    isLoading, 
    selectedElementType,
    fullResults,
    setFullResults
  } = useMestreStore();

  const results = fullResults;
  const totalLength = params.L || 6.0;

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12_000); // 12s for complex FEA
    try {
      setError(null);
      // Prepare payload for backend (mapping internal state to expected backend keys)
      const payload = {
        ...currentParams,
        // Ensure supports and loads are arrays
        supports: currentParams.supports || [{ x: 0, type: 'pinned' }, { x: currentParams.L, type: 'pinned' }],
        distributed_loads: currentParams.distributed_loads || [{ x_start: 0, x_end: currentParams.L, q_start: currentParams.q, q_end: currentParams.q }],
        point_loads: currentParams.point_loads || []
      };

      const response = await calculateSpecialElement(selectedElementType, payload, controller.signal);
      const steps = extractMestreSteps(response);
      setPedagogicalSteps(steps);
      setCalculationTrace(response.calculation_trace ?? null);
      
      // The actual solver output is nested in response.result
      const analysisResults = response.result || response;
      
      // Debug: ensure we have diagrams
      if (!analysisResults.diagrams && response.diagrams) {
        analysisResults.diagrams = response.diagrams;
      }
      
      setFullResults({ ...analysisResults });
      
      if (steps.length === 0) {
        setError('O motor de cálculo não gerou passos. Verifique se os apoios e cargas estão dentro do vão.');
      }
    } catch (error: unknown) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        setError('O motor MEF excedeu o tempo de resposta (12s). Tente reduzir a complexidade.');
      } else if (error instanceof Error) {
        // Security: Mask tracebacks to avoid information exposure
        const cleanMessage = error.message.includes('Traceback') || error.message.includes('stack trace')
          ? 'Ocorreu um erro interno no servidor. Detalhes técnicos ocultados por segurança.'
          : error.message;
        setError(`Erro técnico: ${cleanMessage}`);
      } else {
        setError('Erro técnico inesperado no motor de cálculo.');
      }
    } finally {
      clearTimeout(timeout);
      setIsLoading(false);
    }
  }, [selectedElementType, setPedagogicalSteps, setIsLoading, setError, setCalculationTrace]);

  const updateNumber = (key: keyof MestreParams, value: string) => {
    const parsed = parseFloat(value);
    if (!Number.isNaN(parsed)) {
      updateParams({ [key]: parsed });
    }
  };

  const updateNestedParam = (key: keyof MestreParams, value: MestreParams[keyof MestreParams]) => {
    updateParams({ [key]: value });
  };

  const addSupport = () => {
    const current: BeamSupport[] = params.supports || [{ x: 0, type: 'pinned' }, { x: params.L, type: 'pinned' }];
    updateNestedParam('supports', [...current, { x: params.L / 2, type: 'pinned' }]);
  };

  const removeSupport = (index: number) => {
    const current = [...(params.supports || [])];
    current.splice(index, 1);
    updateNestedParam('supports', current);
  };

  const addPointLoad = () => {
    const current: PointLoad[] = params.point_loads || [];
    updateNestedParam('point_loads', [...current, { x: params.L / 2, P: 50.0 }]);
  };

  const removePointLoad = (index: number) => {
    const current = [...(params.point_loads || [])];
    current.splice(index, 1);
    updateNestedParam('point_loads', current);
  };

  const applyBeamPreset = (preset: 'biapoiada' | 'balanco-esquerdo' | 'balanco-direito' | 'balanco-duplo' | 'engastada-livre') => {
    const L = params.L || 6;
    const q = params.q || 20;
    const leftOverhang = Math.min(Math.max(L * 0.2, 0.8), L * 0.35);
    const rightSupport = Math.max(L - leftOverhang, L * 0.55);
    const leftSupport = Math.min(leftOverhang, L * 0.45);
    const doubleLeft = Math.min(Math.max(L * 0.15, 0.6), L * 0.3);
    const doubleRight = Math.max(L - doubleLeft, L * 0.7);

    const presets: Record<typeof preset, BeamSupport[]> = {
      'biapoiada': [{ x: 0, type: 'pinned' }, { x: L, type: 'pinned' }],
      'balanco-esquerdo': [{ x: leftSupport, type: 'pinned' }, { x: L, type: 'pinned' }],
      'balanco-direito': [{ x: 0, type: 'pinned' }, { x: rightSupport, type: 'pinned' }],
      'balanco-duplo': [{ x: doubleLeft, type: 'pinned' }, { x: doubleRight, type: 'pinned' }],
      'engastada-livre': [{ x: 0, type: 'fixed' }],
    };

    updateParams({
      supports: presets[preset],
      distributed_loads: [{ x_start: 0, x_end: L, q_start: q, q_end: q }],
    });
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Box className="w-5 h-5 text-primary" />
          Laboratório de Vigas (MEF 3D)
        </h3>
      </div>

      <Tabs defaultValue="geometry" className="w-full">
        <TabsList className="grid grid-cols-4 h-10 bg-muted/50 p-1 mb-6">
          <TabsTrigger value="geometry" className="text-[10px] uppercase font-bold tracking-tight gap-2">
            <Ruler className="w-3.5 h-3.5" />
            Geometria
          </TabsTrigger>
          <TabsTrigger value="supports" className="text-[10px] uppercase font-bold tracking-tight gap-2">
            <Anchor className="w-3.5 h-3.5" />
            Vínculos
          </TabsTrigger>
          <TabsTrigger value="loads" className="text-[10px] uppercase font-bold tracking-tight gap-2">
            <ArrowDown className="w-3.5 h-3.5" />
            Cargas
          </TabsTrigger>
          <TabsTrigger value="materials" className="text-[10px] uppercase font-bold tracking-tight gap-2">
            <Settings2 className="w-3.5 h-3.5" />
            Ajustes
          </TabsTrigger>
        </TabsList>

        <TabsContent value="geometry" className="space-y-4 animate-in fade-in duration-300">
          <div className="p-5 rounded-2xl bg-muted/20 border border-border/50 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="beam-l-input" className="text-[10px] font-bold text-muted-foreground uppercase">Vão Total (L) [m]</Label>
                <Input 
                  id="beam-l-input"
                  type="number" step="0.1" 
                  value={params.L} 
                  onChange={(e) => updateNumber('L', e.target.value)}
                  className="bg-background/50 border-primary/10"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-muted-foreground uppercase">Tipo de Seção</Label>
                <Select 
                  value={params.section_type || 'rectangular'} 
                  onValueChange={(v) => updateParams({ section_type: v as MestreParams['section_type'] })}
                >
                  <SelectTrigger className="h-10 bg-background/50 border-primary/10">
                    <SelectValue placeholder="Seção" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rectangular">Retangular</SelectItem>
                    <SelectItem value="t-beam">Viga T (Laje)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="beam-b-input" className="text-[10px] font-bold text-muted-foreground uppercase">Largura (b) [m]</Label>
                <Input 
                  id="beam-b-input"
                  type="number" step="0.01" 
                  value={params.b} 
                  onChange={(e) => updateNumber('b', e.target.value)}
                  className="bg-background/50 border-primary/10"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="beam-h-input" className="text-[10px] font-bold text-muted-foreground uppercase">Altura (h) [m]</Label>
                <Input 
                  id="beam-h-input"
                  type="number" step="0.01" 
                  value={params.h} 
                  onChange={(e) => updateNumber('h', e.target.value)}
                  className="bg-background/50 border-primary/10"
                />
              </div>
            </div>

            {params.section_type === 't-beam' && (
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-primary/5 animate-in slide-in-from-top-2">
                <div className="space-y-2">
                  <Label className="text-[10px] font-bold text-primary uppercase">Mesa (bf) [m]</Label>
                  <Input 
                    type="number" step="0.05" 
                    value={params.bf || 0.60} 
                    onChange={(e) => updateParams({ bf: parseFloat(e.target.value) })}
                    className="bg-primary/5 border-primary/20"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] font-bold text-primary uppercase">Flange (hf) [m]</Label>
                  <Input 
                    type="number" step="0.01" 
                    value={params.hf || 0.10} 
                    onChange={(e) => updateParams({ hf: parseFloat(e.target.value) })}
                    className="bg-primary/5 border-primary/20"
                  />
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="supports" className="space-y-4 animate-in fade-in duration-300">
          <div className="p-5 rounded-2xl bg-muted/20 border border-border/50 space-y-4">
            <div className="space-y-3">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Modelos rápidos</span>
              <div className="grid grid-cols-2 gap-2">
                <Button type="button" variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => applyBeamPreset('biapoiada')}>
                  Biapoiada
                </Button>
                <Button type="button" variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => applyBeamPreset('engastada-livre')}>
                  Engastada livre
                </Button>
                <Button type="button" variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => applyBeamPreset('balanco-esquerdo')}>
                  Balanço esquerdo
                </Button>
                <Button type="button" variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => applyBeamPreset('balanco-direito')}>
                  Balanço direito
                </Button>
                <Button type="button" variant="outline" size="sm" className="col-span-2 h-8 text-[10px]" onClick={() => applyBeamPreset('balanco-duplo')}>
                  Balanço duplo
                </Button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Apoios e Vínculos</span>
              <Button onClick={addSupport} variant="outline" size="sm" className="h-7 text-[10px] gap-1 border-primary/20 text-primary">
                <Plus className="w-3 h-3" /> Adicionar
              </Button>
            </div>
            
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
              {(params.supports || [{ x: 0, type: 'pinned' }, { x: params.L, type: 'pinned' }]).map((sup: BeamSupport, idx: number) => (
                <div key={idx} className="flex gap-2 items-end bg-background/40 p-3 rounded-xl border border-primary/5 shadow-sm">
                  <div className="flex-1 space-y-1.5">
                    <Label className="text-[9px] uppercase font-bold text-muted-foreground">Posição (x) [m]</Label>
                    <Input 
                      type="number" step="0.1" value={sup.x} 
                      onChange={(e) => {
                        const s = [...(params.supports || [])];
                        s[idx] = { ...s[idx], x: parseFloat(e.target.value) };
                        updateNestedParam('supports', s);
                      }}
                      className="h-8 text-xs bg-transparent"
                    />
                  </div>
                  <div className="flex-1 space-y-1.5">
                    <Label className="text-[9px] uppercase font-bold text-muted-foreground">Tipo</Label>
                    <Select 
                      value={sup.type} 
                      onValueChange={(v) => {
                        const s = [...(params.supports || [])];
                        s[idx] = { ...s[idx], type: v as SupportType };
                        updateNestedParam('supports', s);
                      }}
                    >
                      <SelectTrigger className="h-8 text-xs bg-transparent">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pinned">Simples</SelectItem>
                        <SelectItem value="fixed">Engaste</SelectItem>
                        <SelectItem value="spring">Elástico</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button 
                    variant="ghost" size="icon" className="h-8 w-8 text-destructive/50 hover:text-destructive"
                    onClick={() => removeSupport(idx)}
                    disabled={idx < 2 && (params.supports?.length || 0) <= 2}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="loads" className="space-y-4 animate-in fade-in duration-300">
          <div className="p-5 rounded-2xl bg-muted/20 border border-border/50 space-y-6">
            {/* Cargas Distribuídas Avançadas */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Cargas Distribuídas (q)</span>
                <Button 
                  onClick={() => {
                    const current: DistributedLoad[] = params.distributed_loads || [{ x_start: 0, x_end: params.L, q_start: params.q, q_end: params.q }];
                    updateNestedParam('distributed_loads', [...current, { x_start: 0, x_end: params.L, q_start: 10, q_end: 10 }]);
                  }} 
                  variant="outline" size="sm" className="h-7 text-[10px] gap-1 border-primary/20 text-primary"
                >
                  <Plus className="w-3 h-3" /> Adicionar
                </Button>
              </div>

              <div className="space-y-3 max-h-[250px] overflow-y-auto pr-2">
                {(params.distributed_loads || [{ x_start: 0, x_end: params.L, q_start: params.q, q_end: params.q }]).map((dl: DistributedLoad, idx: number) => (
                  <div key={idx} className="bg-background/40 p-4 rounded-xl border border-primary/5 shadow-sm space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-muted-foreground">Início (x1) [m]</Label>
                        <Input 
                          type="number" step="0.1" value={dl.x_start} 
                          onChange={(e) => {
                            const d = [...(params.distributed_loads || [])];
                            d[idx] = { ...d[idx], x_start: parseFloat(e.target.value) };
                            updateNestedParam('distributed_loads', d);
                          }}
                          className="h-8 text-xs bg-transparent"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-muted-foreground">Fim (x2) [m]</Label>
                        <Input 
                          type="number" step="0.1" value={dl.x_end} 
                          onChange={(e) => {
                            const d = [...(params.distributed_loads || [])];
                            d[idx] = { ...d[idx], x_end: parseFloat(e.target.value) };
                            updateNestedParam('distributed_loads', d);
                          }}
                          className="h-8 text-xs bg-transparent"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-primary">q1 [kN/m]</Label>
                        <Input 
                          type="number" step="1" value={dl.q_start} 
                          onChange={(e) => {
                            const d = [...(params.distributed_loads || [])];
                            d[idx] = { ...d[idx], q_start: parseFloat(e.target.value) };
                            updateNestedParam('distributed_loads', d);
                          }}
                          className="h-8 text-xs bg-primary/5 font-bold"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-primary">q2 [kN/m]</Label>
                        <Input 
                          type="number" step="1" value={dl.q_end} 
                          onChange={(e) => {
                            const d = [...(params.distributed_loads || [])];
                            d[idx] = { ...d[idx], q_end: parseFloat(e.target.value) };
                            updateNestedParam('distributed_loads', d);
                          }}
                          className="h-8 text-xs bg-primary/5 font-bold"
                        />
                      </div>
                    </div>
                    {idx > 0 && (
                      <Button 
                        variant="ghost" size="sm" className="w-full h-6 text-[9px] text-destructive/50 hover:text-destructive gap-1"
                        onClick={() => {
                          const d = [...(params.distributed_loads || [])];
                          d.splice(idx, 1);
                          updateNestedParam('distributed_loads', d);
                        }}
                      >
                        <Trash2 className="w-3 h-3" /> Remover Trecho
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-primary/5 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Cargas Concentradas (P) & Momentos (M)</span>
                <Button onClick={addPointLoad} variant="outline" size="sm" className="h-7 text-[10px] gap-1 border-primary/20 text-primary">
                  <Plus className="w-3 h-3" /> Adicionar
                </Button>
              </div>

              <div className="space-y-2 max-h-[250px] overflow-y-auto pr-2">
                {(params.point_loads || []).map((pl: PointLoad, idx: number) => (
                  <div key={idx} className="bg-background/40 p-3 rounded-xl border border-primary/5 shadow-sm space-y-3">
                    <div className="grid grid-cols-3 gap-2">
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-muted-foreground">Pos (x) [m]</Label>
                        <Input 
                          type="number" step="0.1" value={pl.x} 
                          onChange={(e) => {
                            const p = [...(params.point_loads || [])];
                            p[idx] = { ...p[idx], x: parseFloat(e.target.value) };
                            updateNestedParam('point_loads', p);
                          }}
                          className="h-8 text-xs bg-transparent"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-primary">Força (P) [kN]</Label>
                        <Input 
                          type="number" step="5" value={pl.P} 
                          onChange={(e) => {
                            const p = [...(params.point_loads || [])];
                            p[idx] = { ...p[idx], P: parseFloat(e.target.value) };
                            updateNestedParam('point_loads', p);
                          }}
                          className="h-8 text-xs bg-primary/5 font-bold"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[9px] uppercase font-bold text-orange-500">Mom. (M) [kNm]</Label>
                        <Input 
                          type="number" step="5" value={pl.M || 0} 
                          onChange={(e) => {
                            const p = [...(params.point_loads || [])];
                            p[idx] = { ...p[idx], M: parseFloat(e.target.value) };
                            updateNestedParam('point_loads', p);
                          }}
                          className="h-8 text-xs bg-orange-500/5 font-bold"
                        />
                      </div>
                    </div>
                    <Button 
                      variant="ghost" size="sm" className="w-full h-6 text-[9px] text-destructive/50 hover:text-destructive gap-1"
                      onClick={() => removePointLoad(idx)}
                    >
                      <Trash2 className="w-3 h-3" /> Remover Carga
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="materials" className="space-y-4 animate-in fade-in duration-300">
          <div className="p-5 rounded-2xl bg-muted/20 border border-border/50 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="beam-fck-input" className="text-[10px] font-bold text-muted-foreground uppercase">Concreto (fck) [MPa]</Label>
                <Input 
                  id="beam-fck-input"
                  type="number" value={params.fck} 
                  onChange={(e) => updateNumber('fck', e.target.value)}
                  className="bg-background/50 border-primary/10"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-muted-foreground uppercase">CAA (Norma)</Label>
                <Select 
                  value={params.caa?.toString() || '2'} 
                  onValueChange={(v) => updateParams({ caa: parseInt(v) })}
                >
                  <SelectTrigger className="h-10 bg-background/50 border-primary/10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">I (Rural)</SelectItem>
                    <SelectItem value="2">II (Urbana)</SelectItem>
                    <SelectItem value="3">III (Marinha)</SelectItem>
                    <SelectItem value="4">IV (Industrial)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-muted-foreground uppercase">Cobrimento (c) [mm]</Label>
                <Input 
                  type="number" value={params.cover_mm || 30} 
                  onChange={(e) => updateParams({ cover_mm: parseFloat(e.target.value) })}
                  className="bg-background/50 border-primary/10"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] font-bold text-muted-foreground uppercase">Aço (fyk) [MPa]</Label>
                <Input 
                  type="number" value={params.fy || 500} 
                  onChange={(e) => updateParams({ fy: parseFloat(e.target.value) })}
                  className="bg-background/50 border-primary/10"
                />
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      <div className="flex gap-2 pt-2">
        <Button 
          onClick={() => handleCalculate(params)} 
          className="flex-1 macos-button h-12 gap-2 text-sm font-bold shadow-lg shadow-primary/20"
          disabled={isLoading}
        >
          <Calculator className="w-5 h-5" />
          {isLoading ? 'Executando Motor MEF...' : 'Analisar Estrutura'}
        </Button>
        <Button 
          variant="outline" 
          className="h-12 px-4 border-primary/20 hover:bg-primary/5 text-primary"
          title="Otimização Automática (AI)"
        >
          <Brain className="w-5 h-5" />
        </Button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive animate-in shake duration-500">
          <TriangleAlert className="w-5 h-5 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}

      {results?.diagrams && (
        <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-500" id="mestre-diagrams">
          <MestreDiagram 
            points={results.diagrams.shear || []} 
            title="Esforço Cortante" 
            unit="kN" 
            color="hsl(217 91% 55%)" 
            fillColor="hsl(217 91% 55% / 0.1)" 
            totalLength={totalLength}
          />
          <MestreDiagram 
            points={results.diagrams.moment || []} 
            title="Momento Fletor" 
            unit="kNm" 
            color="hsl(262 83% 58%)" 
            fillColor="hsl(262 83% 58% / 0.1)" 
            totalLength={totalLength}
          />
          <MestreDiagram 
            points={results.diagrams.deflection || []} 
            title="Linha Elástica" 
            unit="mm" 
            color="hsl(20 90% 48%)" 
            fillColor="hsl(20 90% 48% / 0.1)" 
            totalLength={totalLength}
          />
        </div>
      )}

      <div className="flex flex-col items-center gap-2 pt-4 border-t border-border/50">
        <p className="text-[10px] text-muted-foreground/60 text-center leading-relaxed italic px-8">
          Solver ATLAS Pro: Elementos Finitos de 2ª Ordem com validação cruzada NBR 6118.
        </p>
      </div>
    </div>
  );
}
