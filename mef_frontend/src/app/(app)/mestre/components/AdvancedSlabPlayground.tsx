'use client';

import { useCallback, useState } from 'react';
import { Grid3X3, Calculator, Ruler, Layers, ShieldCheck, Info, Trash2, Plus } from 'lucide-react';

import { calculateSpecialElement } from '@/lib/api-mestre';
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
import { Switch } from '@/components/ui/switch';

interface ColumnLoad {
  id: number;
  x: number;
  y: number;
  fz: number;
}

interface AdvancedSlabConfig {
  Lx: number;
  Ly: number;
  h: number;
  kv: number;
  fck: number;
  q_dist: number;
  is_raft: boolean;
  is_nonlinear_isi: boolean;
}

export function AdvancedSlabPlayground() {
  const { 
    params, 
    updateParams, 
    setIsLoading, 
    setError, 
    applyMestreResponse,
    fullResults,
    isLoading,
    error 
  } = useMestreStore();

  const [slabConfig, setSlabConfig] = useState<AdvancedSlabConfig>({
    Lx: Number(params.Lx) || 10.0,
    Ly: Number(params.Ly) || 10.0,
    h: Number(params.h) || 0.40,
    kv: Number(params.kv) || 30.0, // MN/m³ (Winkler)
    fck: Number(params.fck) || 30.0,
    q_dist: Number(params.q) || 5.0,
    is_raft: true,
    is_nonlinear_isi: false
  });

  const [columns, setColumns] = useState<ColumnLoad[]>([]);

  const updateConfig = <Key extends keyof AdvancedSlabConfig>(key: Key, value: AdvancedSlabConfig[Key]) => {
    setSlabConfig(prev => ({ ...prev, [key]: value }));
    updateParams({ [key]: value });
  };

  const addColumn = () => {
    const newId = columns.length > 0 ? Math.max(...columns.map(c => c.id)) + 1 : 1;
    setColumns([...columns, { id: newId, x: slabConfig.Lx / 2, y: slabConfig.Ly / 2, fz: 500 }]);
  };

  const removeColumn = (id: number) => {
    setColumns(columns.filter(c => c.id !== id));
  };

  const updateColumn = (id: number, key: keyof ColumnLoad, value: string) => {
    const val = Number(value);
    if (!isNaN(val)) {
      setColumns(columns.map(c => c.id === id ? { ...c, [key]: val } : c));
    }
  };

  const handleCalculate = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const payload = {
        ...slabConfig,
        columns,
        type: 'advanced_slab'
      };
      
      const data = await calculateSpecialElement('advanced_slab', payload);
      
      if (data.success) {
        applyMestreResponse(data);
      } else {
        setError("Falha na análise avançada.");
      }
    } catch (err: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
      setError(err.message || "Erro no motor Radier Avançado.");
    } finally {
      setIsLoading(false);
    }
  }, [applyMestreResponse, slabConfig, columns, setIsLoading, setError]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Grid3X3 className="w-5 h-5 text-primary" />
          Radier Avançado e Lajes em Solo
        </h3>
        <Button variant="outline" className="h-11 px-4 border-primary/20 hover:bg-primary/5 text-primary">
          <Info className="w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Geometria e Solo */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Ruler className="w-3 h-3" />
            Painel e Solo
          </h4>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="adv-lx-input" className="text-[10px] text-muted-foreground uppercase">Lx (m)</Label>
              <Input id="adv-lx-input" type="number" value={slabConfig.Lx} onChange={(e) => updateConfig('Lx', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="adv-ly-input" className="text-[10px] text-muted-foreground uppercase">Ly (m)</Label>
              <Input id="adv-ly-input" type="number" value={slabConfig.Ly} onChange={(e) => updateConfig('Ly', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="adv-h-input" className="text-[10px] text-muted-foreground uppercase">Espessura h (m)</Label>
              <Input id="adv-h-input" type="number" step="0.05" value={slabConfig.h} onChange={(e) => updateConfig('h', Number(e.target.value))} className="h-9 bg-background/50" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="adv-kv-input" className="text-[10px] text-muted-foreground uppercase">Mod. Reação kv (MN/m³)</Label>
              <Input id="adv-kv-input" type="number" value={slabConfig.kv} onChange={(e) => updateConfig('kv', Number(e.target.value))} className="h-9 bg-background/50 font-mono text-primary font-bold" />
            </div>
          </div>
        </div>

        {/* Cargas Distribuídas */}
        <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Layers className="w-3 h-3" />
            Carregamento Global
          </h4>

          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Carga Distribuída q (kN/m²)</Label>
            <Input type="number" value={slabConfig.q_dist} onChange={(e) => updateConfig('q_dist', Number(e.target.value))} className="h-9 bg-background/50" />
          </div>

          <div className="space-y-1.5">
            <Label className="text-[10px] text-muted-foreground uppercase">Modelo</Label>
            <Select value={slabConfig.is_raft ? 'raft' : 'slab'} onValueChange={(val) => updateConfig('is_raft', val === 'raft')}>
              <SelectTrigger className="h-9 bg-background/50">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="raft">Radier (Winkler)</SelectItem>
                <SelectItem value="slab">Laje (Apoios Rígidos)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5 pt-2 border-t border-primary/5">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-[10px] font-bold text-orange-600 uppercase">Análise Solo Não-Linear (ISE)</Label>
                <p className="text-[9px] text-muted-foreground leading-tight">Plastificação do solo via Winkler Não-Linear</p>
              </div>
              <Switch 
                checked={slabConfig.is_nonlinear_isi} 
                onCheckedChange={(val) => updateConfig('is_nonlinear_isi', val)} 
              />
            </div>
          </div>
        </div>
      </div>

      {/* Cargas de Pilares (Pontuais) */}
      <div className="space-y-4 p-4 rounded-xl bg-muted/30 border border-border/50">
        <div className="flex items-center justify-between">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <Plus className="w-3 h-3" />
            Cargas de Pilares (Nodais)
          </h4>
          <Button onClick={addColumn} variant="ghost" size="sm" className="h-7 text-[10px] font-black uppercase tracking-widest">
            Adicionar Pilar
          </Button>
        </div>

        {columns.length === 0 ? (
          <div className="py-4 text-center text-[10px] text-muted-foreground uppercase font-medium">Nenhum pilar adicionado</div>
        ) : (
          <div className="space-y-2 max-h-[200px] overflow-y-auto pr-2">
            {columns.map((col) => (
              <div key={col.id} className="grid grid-cols-4 gap-2 items-end p-2 rounded-lg bg-background/40 border border-border/50">
                <div className="space-y-1">
                  <Label htmlFor={`col-x-${col.id}`} className="text-[8px] uppercase">X (m)</Label>
                  <Input id={`col-x-${col.id}`} type="number" value={col.x} onChange={(e) => updateColumn(col.id, 'x', e.target.value)} className="h-8 text-xs bg-background/50" />
                </div>
                <div className="space-y-1">
                  <Label htmlFor={`col-y-${col.id}`} className="text-[8px] uppercase">Y (m)</Label>
                  <Input id={`col-y-${col.id}`} type="number" value={col.y} onChange={(e) => updateColumn(col.id, 'y', e.target.value)} className="h-8 text-xs bg-background/50" />
                </div>
                <div className="space-y-1">
                  <Label htmlFor={`col-fz-${col.id}`} className="text-[8px] uppercase">Fz (kN)</Label>
                  <Input id={`col-fz-${col.id}`} type="number" value={col.fz} onChange={(e) => updateColumn(col.id, 'fz', e.target.value)} className="h-8 text-xs bg-background/50 text-primary font-bold" />
                </div>
                <Button onClick={() => removeColumn(col.id)} variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:bg-destructive/10">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <Button onClick={handleCalculate} className="w-full macos-button h-12 gap-2" disabled={isLoading}>
        <Calculator className="w-4 h-4" />
        {isLoading ? 'Analisando Radier...' : 'Analisar Sistema'}
      </Button>

      {fullResults?.summary && (
        <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3" id="advanced-slab-results">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
            <ShieldCheck className="w-3 h-3" />
            Resultados MEF (Placas)
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <MetricCard label="Recalque Máx (mm)" value={fullResults.summary.max_settlement_mm?.toFixed(2)} />
            <MetricCard label="Momento Mx+ (kNm/m)" value={fullResults.summary.mx_pos?.toFixed(1)} />
            <MetricCard label="Momento My+ (kNm/m)" value={fullResults.summary.my_pos?.toFixed(1)} />
            <MetricCard label="Pressão Solo (kPa)" value={fullResults.summary.soil_pressure_kPa?.toFixed(1)} />
            <MetricCard label="Status Geotécnico" value={fullResults.summary.status_geotech} color={fullResults.summary.status_geotech === 'OK' || fullResults.summary.status_geotech === 'ELÁSTICO' ? 'text-emerald-500' : 'text-orange-500'} />
            {fullResults.summary.is_nonlinear_isi && (
              <MetricCard 
                label="Plastificação" 
                value={`${((fullResults.summary.plastification_ratio || 0) * 100).toFixed(1)}%`} 
                color={fullResults.summary.plastification_ratio > 0 ? 'text-orange-500' : 'text-emerald-500'}
              />
            )}
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

function MetricCard({ label, value, color }: { label: string; value: any; color?: string }) { // eslint-disable-line @typescript-eslint/no-explicit-any
  return (
    <div className="p-3 rounded-xl bg-background/50 border border-border/50">
      <p className="text-[8px] uppercase font-black text-muted-foreground tracking-tighter">{label}</p>
      <p className={`mt-1 text-sm font-black ${color || 'text-foreground'}`}>{value}</p>
    </div>
  );
}
