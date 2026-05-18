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
import { Plus, Trash2, Search, Layers, Calculator, Brain, Shield } from 'lucide-react';
import { useCallback } from 'react';
import { calculateSpt } from '@/lib/api-mestre';
import { type SoilLayer } from '@/lib/mestre-types';

export function SptPlayground() {
  const { params, updateParams, setIsLoading, setError, applyMestreResponse, isLoading, error } = useMestreStore();

  const handleLayerChange = (index: number, field: keyof SoilLayer, value: SoilLayer[keyof SoilLayer]) => {
    const newLayers = [...params.layers];
    newLayers[index] = { ...newLayers[index], [field]: value };
    updateParams({ layers: newLayers });
  };

  const addLayer = () => {
    const lastLayer = params.layers[params.layers.length - 1];
    const newLayer = {
      depth_m: (lastLayer?.depth_m || 0) + 1.0,
      thickness_m: 1.0,
      nspt: 10,
      soil_type: 'areia'
    };
    updateParams({ layers: [...params.layers, newLayer] });
  };

  const removeLayer = (index: number) => {
    const newLayers = params.layers.filter((_, i: number) => i !== index);
    updateParams({ layers: newLayers });
  };

  const handleCalculate = useCallback(async (currentLayers: SoilLayer[]) => {
    setIsLoading(true);
    setError(null);
    try {
      // Ajustar dados para o formato esperado pelo backend (spt_data)
      const sptData = currentLayers.map(l => ({
        depth_m: l.depth_m,
        nspt: l.nspt,
        soil_type: l.soil_type
      }));

      const data = await calculateSpt(sptData);
      if (data.success) {
        applyMestreResponse({
          ...data,
          calculation_trace: data.calculation_trace ?? {
            requested_type: 'spt',
            solver_module: 'GeotechnicalEngine.analyze_spt',
            blackboard_builder: 'build_spt_blackboard',
            classical_check: true,
            mef_check: false
          },
          full_results: data.result ?? data,
        });
      } else {
        setError("Falha na análise de SPT.");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro de conexão com o motor geotécnico.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [applyMestreResponse, setIsLoading, setError]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Search className="w-5 h-5 text-primary" />
          Sondagem SPT
        </h3>
      </div>

      <div className="space-y-4">
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
              <Layers className="w-3 h-3" />
              Camadas de Solo
            </h4>
            <Button size="icon" variant="ghost" onClick={addLayer} className="h-6 w-6 hover:bg-primary/10 hover:text-primary">
              <Plus className="h-3 w-3" />
            </Button>
          </div>

          <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1 custom-scrollbar">
            {params.layers.map((layer: SoilLayer, index: number) => (
              <div key={index} className="flex gap-2 items-center bg-background/40 p-2 rounded-lg border border-border/30 group">
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <div className="space-y-1">
                    <Label className="text-[8px] text-muted-foreground uppercase px-1">Cota (m)</Label>
                    <Input 
                      type="number" 
                      value={layer.depth_m} 
                      onChange={(e) => handleLayerChange(index, 'depth_m', parseFloat(e.target.value))}
                      className="h-7 text-[10px] px-1.5"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[8px] text-muted-foreground uppercase px-1">NSPT</Label>
                    <Input 
                      type="number" 
                      value={layer.nspt} 
                      onChange={(e) => handleLayerChange(index, 'nspt', parseFloat(e.target.value))}
                      className="h-7 text-[10px] px-1.5"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[8px] text-muted-foreground uppercase px-1">Tipo</Label>
                    <Select value={layer.soil_type} onValueChange={(v) => handleLayerChange(index, 'soil_type', v)}>
                      <SelectTrigger className="h-7 text-[9px] px-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="areia">Areia</SelectItem>
                        <SelectItem value="silte">Silte</SelectItem>
                        <SelectItem value="argila">Argila</SelectItem>
                        <SelectItem value="misto">Misto</SelectItem>
                        <SelectItem value="aterro">Aterro</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => removeLayer(index)}
                  className="h-7 w-7 opacity-0 group-hover:opacity-100 text-destructive transition-opacity self-end mb-1"
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
          onClick={() => handleCalculate(params.layers)} 
          className="flex-1 macos-button h-11 gap-2"
          disabled={isLoading}
        >
          <Calculator className="w-4 h-4" />
          {isLoading ? 'Processando...' : 'Analisar Sondagem'}
        </Button>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Brain className="w-4 h-4" />
        </Button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
          <Shield className="w-4 h-4 mt-0.5 shrink-0" />
          <p className="text-xs font-medium leading-relaxed">{error}</p>
        </div>
      )}
    </div>
  );
}
