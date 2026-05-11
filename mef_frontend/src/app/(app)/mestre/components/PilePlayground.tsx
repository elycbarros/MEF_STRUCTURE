import { useMestreStore } from '@/lib/store-mestre';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from '@/components/ui/button';
import { Plus, Trash2, Microscope, Anchor, Layers, Calculator, Brain } from 'lucide-react';
import { useCallback } from 'react';
import { calculateSpecialElement } from '@/lib/api-mestre';
import { extractMestreSteps, type MestreParams, type SoilLayer } from '@/lib/mestre-types';

export function PilePlayground() {
  const { params, updateParams, setIsLoading, setPedagogicalSteps, setError, setCalculationTrace, isLoading } = useMestreStore();

  const handleLayerChange = (index: number, field: keyof SoilLayer, value: SoilLayer[keyof SoilLayer]) => {
    const newLayers = [...params.layers];
    newLayers[index] = { ...newLayers[index], [field]: value };
    updateParams({ layers: newLayers });
  };

  const addLayer = () => {
    const lastLayer = params.layers[params.layers.length - 1];
    const newLayer = {
      depth_m: (lastLayer?.depth_m || 0) + 2.0,
      thickness_m: 2.0,
      nspt: 10,
      soil_type: 'misto'
    };
    updateParams({ layers: [...params.layers, newLayer] });
  };

  const removeLayer = (index: number) => {
    const newLayers = params.layers.filter((_, i: number) => i !== index);
    updateParams({ layers: newLayers });
  };

  const handleCalculate = useCallback(async (currentParams: MestreParams) => {
    setIsLoading(true);
    try {
      const data = await calculateSpecialElement('pile', currentParams);
      if (data.success) {
        setPedagogicalSteps(extractMestreSteps(data));
        setCalculationTrace(data.calculation_trace ?? null);
      } else {
        setError("Falha na análise da estaca.");
      }
    } catch {
      setError("Erro de conexão com o motor.");
    } finally {
      setIsLoading(false);
    }
  }, [setCalculationTrace, setIsLoading, setPedagogicalSteps, setError]);

  const updateParam = (key: keyof MestreParams, value: string | number) => {
    const val = typeof value === 'string' ? parseFloat(value) : value;
    if (typeof val === 'number' && isNaN(val)) return;
    updateParams({ [key]: val });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Anchor className="w-5 h-5 text-primary" />
          Análise de Estaca
        </h3>
      </div>

      <div className="space-y-4">
        {/* Seção 1: Geometria */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Microscope className="w-3 h-3" />
            Parâmetros Técnicos
          </h4>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Diâmetro (m)</Label>
              <Input 
                type="number" 
                step="0.05"
                value={params.diameter} 
                onChange={(e) => updateParam('diameter', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Comp. (m)</Label>
              <Input 
                type="number" 
                value={params.length} 
                onChange={(e) => updateParam('length', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">Carga Nd (kN)</Label>
              <Input 
                type="number" 
                value={params.Nd} 
                onChange={(e) => updateParam('Nd', e.target.value)}
                className="h-9 bg-background/50 font-mono font-bold text-primary"
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[10px] text-muted-foreground uppercase">fck (MPa)</Label>
              <Input 
                type="number" 
                value={params.fck} 
                onChange={(e) => updateParam('fck', e.target.value)}
                className="h-9 bg-background/50"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Tipo de Estaca</Label>
            <Select value={params.pile_type} onValueChange={(v) => updateParam('pile_type', v)}>
              <SelectTrigger className="h-9 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bored">Escavada (Bored)</SelectItem>
                <SelectItem value="cfa">Hélice contínua</SelectItem>
                <SelectItem value="pre-cast">Pré-moldada</SelectItem>
                <SelectItem value="strauss">Strauss</SelectItem>
                <SelectItem value="franki">Franki</SelectItem>
                <SelectItem value="steel">Metálica</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Seção 2: Perfil de Solo */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Layers className="w-3 h-3" />
              Perfil de Solo (Sondagem)
            </h4>
            <Button size="icon" variant="ghost" onClick={addLayer} className="h-6 w-6 hover:bg-primary/10 hover:text-primary">
              <Plus className="h-3 w-3" />
            </Button>
          </div>

          <div className="space-y-2 max-h-[250px] overflow-y-auto pr-1 custom-scrollbar">
            {params.layers.map((layer: SoilLayer, index: number) => (
              <div key={index} className="flex gap-2 items-center bg-background/40 p-2 rounded-lg border border-border/30 group">
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <Input 
                    type="number" 
                    placeholder="H (m)"
                    value={layer.thickness_m} 
                    onChange={(e) => handleLayerChange(index, 'thickness_m', parseFloat(e.target.value))}
                    className="h-7 text-[10px] px-1.5"
                  />
                  <Input 
                    type="number" 
                    placeholder="NSPT"
                    value={layer.nspt} 
                    onChange={(e) => handleLayerChange(index, 'nspt', parseFloat(e.target.value))}
                    className="h-7 text-[10px] px-1.5"
                  />
                  <Select value={layer.soil_type} onValueChange={(v) => handleLayerChange(index, 'soil_type', v)}>
                    <SelectTrigger className="h-7 text-[9px] px-1.5">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="areia">Areia</SelectItem>
                      <SelectItem value="silte">Silte</SelectItem>
                      <SelectItem value="argila">Argila</SelectItem>
                      <SelectItem value="misto">Misto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => removeLayer(index)}
                  className="h-7 w-7 opacity-0 group-hover:opacity-100 text-destructive transition-opacity"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        <Button 
          onClick={() => handleCalculate(params)} 
          className="flex-1 macos-button h-11 gap-2"
          disabled={isLoading}
        >
          <Calculator className="w-4 h-4" />
          {isLoading ? 'Analisando...' : 'Calcular Capacidade'}
        </Button>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
