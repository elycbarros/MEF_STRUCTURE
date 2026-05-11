import { useMestreStore } from '@/lib/store-mestre';
import { calculateSpecialElement } from '@/lib/api-mestre';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Loader2, Calculator, Brain, Settings2, Info, Ruler, Waves, Layers, Maximize2, TriangleAlert } from 'lucide-react';
import type { ComponentType, ReactNode, SVGProps } from 'react';
import { useState, useCallback } from 'react';
import { extractMestreSteps, type MestreParams } from '@/lib/mestre-types';

export function SpecialPlayground() {
  const { selectedElementType, setPedagogicalSteps, setIsLoading, setError, setCalculationTrace, error, isLoading } = useMestreStore();
  const [paramsByElement, setParamsByElement] = useState<Record<string, Partial<MestreParams>>>({});
  const params = paramsByElement[selectedElementType] ?? {};

  const handleCalculate = useCallback(async (currentParams: Partial<MestreParams>) => {
    setIsLoading(true);
    try {
      setError(null);
      const result = await calculateSpecialElement(selectedElementType, currentParams);
      if (result.success && result.pedagogical_steps) {
        setPedagogicalSteps(extractMestreSteps(result));
        setCalculationTrace(result.calculation_trace ?? null);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Erro de conexão com o motor.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedElementType, setCalculationTrace, setError, setPedagogicalSteps, setIsLoading]);

  const updateParam = (key: keyof MestreParams, value: MestreParams[keyof MestreParams]) => {
    const newParams = { ...params, [key]: value };
    setParamsByElement((current) => ({ ...current, [selectedElementType]: newParams }));
  };

  const renderSection = (
    title: string,
    Icon: ComponentType<SVGProps<SVGSVGElement>>,
    children: ReactNode
  ) => (
    <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
      <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
        <Icon className="w-3 h-3" />
        {title}
      </h4>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );

  const renderFields = () => {
    switch (selectedElementType) {
      case 'corbel':
        return renderSection("Geometria e Carga", Settings2, (
          <>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Carga Vertical Nd (kN)</Label>
              <Input type="number" value={params.fd_kN || 250} onChange={(e) => updateParam('fd_kN', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Dist. &apos;a&apos; (m)</Label>
                <Input type="number" step="0.01" value={params.a_dist || 0.25} onChange={(e) => updateParam('a_dist', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Alt. &apos;d&apos; (m)</Label>
                <Input type="number" step="0.01" value={params.d_eff || 0.45} onChange={(e) => updateParam('d_eff', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'stair':
        return renderSection("Parâmetros da Escada", Settings2, (
          <>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Vão Horizontal (m)</Label>
              <Input type="number" value={params.L || 4.0} onChange={(e) => updateParam('L', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
                <Input type="number" value={params.H || 3.0} onChange={(e) => updateParam('H', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Largura (m)</Label>
                <Input type="number" value={params.width || 1.2} onChange={(e) => updateParam('width', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Carga Variável (kN/m²)</Label>
              <Input type="number" value={params.q || 5.0} onChange={(e) => updateParam('q', Number(e.target.value))} className="h-9 bg-background/50 font-bold text-primary" />
            </div>
          </>
        ));
      case 'helical_stairs':
        return renderSection("Escada Helicoidal", Settings2, (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Raio (m)</Label>
                <Input type="number" step="0.1" value={params.radius || 2.5} onChange={(e) => updateParam('radius', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Ângulo total (graus)</Label>
                <Input type="number" value={params.angle_total_deg || 180} onChange={(e) => updateParam('angle_total_deg', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Espelho (m)</Label>
                <Input type="number" step="0.01" value={params.h_step || 0.18} onChange={(e) => updateParam('h_step', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Espessura (m)</Label>
                <Input type="number" step="0.01" value={params.t || 0.15} onChange={(e) => updateParam('t', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Carga (kN/m²)</Label>
                <Input type="number" step="0.1" value={params.q_acid || 3.0} onChange={(e) => updateParam('q_acid', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'retaining_wall':
        return renderSection("Muro de Arrimo", Layers, (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
                <Input type="number" value={params.h_wall || 4.0} onChange={(e) => updateParam('h_wall', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Base (m)</Label>
                <Input type="number" value={params.b_base || 2.5} onChange={(e) => updateParam('b_base', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">γ solo (kN/m³)</Label>
                <Input type="number" value={params.gamma_soil || 18} onChange={(e) => updateParam('gamma_soil', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">φ solo (graus)</Label>
                <Input type="number" value={params.phi_soil || 30} onChange={(e) => updateParam('phi_soil', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'concrete_wall':
        return renderSection("Parede de Concreto", Layers, (
          <>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Carga Normal Nd (kN/m)</Label>
              <Input type="number" value={params.Nd || 500} onChange={(e) => updateParam('Nd', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
                <Input type="number" step="0.1" value={params.h || 2.8} onChange={(e) => updateParam('h', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Espessura (m)</Label>
                <Input type="number" step="0.01" value={params.t || 0.12} onChange={(e) => updateParam('t', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
                <Input type="number" value={params.fck || 30} onChange={(e) => updateParam('fck', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'reservoir':
        return renderSection("Reservatório", Waves, (
          <>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Compr. (m)</Label>
                <Input type="number" value={params.length || 5} onChange={(e) => updateParam('length', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Larg. (m)</Label>
                <Input type="number" value={params.width || 3} onChange={(e) => updateParam('width', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura água (m)</Label>
                <Input type="number" value={params.depth || 3} onChange={(e) => updateParam('depth', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'gerber_tooth':
        return renderSection("Dente Gerber", Ruler, (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Vd (kN)</Label>
                <Input type="number" value={params.vd_kN || 150} onChange={(e) => updateParam('vd_kN', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Hd (kN)</Label>
                <Input type="number" value={params.hd_kN || 30} onChange={(e) => updateParam('hd_kN', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">a (m)</Label>
                <Input type="number" step="0.01" value={params.a_dist || 0.15} onChange={(e) => updateParam('a_dist', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">d (m)</Label>
                <Input type="number" step="0.01" value={params.d_eff || 0.4} onChange={(e) => updateParam('d_eff', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">b (m)</Label>
                <Input type="number" step="0.01" value={params.b || 0.2} onChange={(e) => updateParam('b', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
          </>
        ));
      case 'deep_beam':
        return renderSection("Viga Parede", Maximize2, (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Vão (m)</Label>
                <Input type="number" value={params.L || 4} onChange={(e) => updateParam('L', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
              <div className="space-y-1.5">
                <Label className="text-[10px] text-muted-foreground uppercase">Altura (m)</Label>
                <Input type="number" value={params.h || 3} onChange={(e) => updateParam('h', Number(e.target.value))} className="h-9 bg-background/50" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Carga distribuída fd (kN/m)</Label>
              <Input type="number" value={params.fd_kN_m || 100} onChange={(e) => updateParam('fd_kN_m', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
          </>
        ));
      default:
        return (
          <div className="p-8 bg-muted/20 rounded-xl border border-dashed border-muted-foreground/30 text-center space-y-3">
            <Info className="w-8 h-8 text-muted-foreground/40 mx-auto" />
            <p className="text-xs text-muted-foreground italic leading-relaxed">
              Configurações avançadas para <span className="font-bold text-foreground capitalize">{selectedElementType.replace('_', ' ')}</span> em processamento pelo Atlas Core.
            </p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Calculator className="w-5 h-5 text-primary" />
          Configuração do Elemento
        </h3>
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-primary" />}
      </div>

      <div className="space-y-4">
        {renderFields()}
      </div>

      <div className="pt-2">
        <Button 
          className="w-full macos-button h-12 gap-2 shadow-lg shadow-primary/10"
          onClick={() => handleCalculate(params)}
          disabled={isLoading}
        >
          <Brain className="w-4 h-4" />
          {isLoading ? 'Analisando...' : 'Processar Análise Mestre'}
        </Button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <TriangleAlert className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}

      <p className="text-[10px] text-muted-foreground/50 text-center leading-relaxed italic">
        A análise pedagógica segmentada utiliza modelos analíticos simplificados para fins de aprendizado estrutural.
      </p>
    </div>
  );
}
