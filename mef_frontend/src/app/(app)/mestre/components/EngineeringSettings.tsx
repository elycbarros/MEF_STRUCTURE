'use client';

import { Settings, Ruler, Zap, Filter, Plus, Trash2, Shield } from 'lucide-react';
import { useMestreStore } from '@/lib/store-mestre';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

type LoadCaseType = 'pp' | 'perm' | 'acid' | 'wind';
type LoadCaseUpdate = Partial<{ name: string; type: LoadCaseType; factor: number }>;
type LengthUnit = 'm' | 'cm' | 'mm';
type ForceUnit = 'kN' | 'tf';
type StressUnit = 'MPa' | 'kPa';

export function EngineeringSettings() {
  const { 
    unitConfig, 
    updateUnitConfig, 
    loadCases, 
    setLoadCases,
    combinations
  } = useMestreStore();

  const addLoadCase = () => {
    const id = `case_${Date.now()}`;
    setLoadCases([...loadCases, { id, name: 'Nova Carga', type: 'acid', factor: 1.0 }]);
  };

  const removeLoadCase = (id: string) => {
    setLoadCases(loadCases.filter(c => c.id !== id));
  };

  const updateLoadCase = (id: string, updates: LoadCaseUpdate) => {
    setLoadCases(loadCases.map(c => c.id === id ? { ...c, ...updates } : c));
  };

  return (
    <Sheet>
      <SheetTrigger 
        render={
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2 h-9 px-3 text-muted-foreground hover:text-primary hover:bg-primary/5">
            <Settings className="w-4 h-4" />
            <span className="text-xs font-medium">Configurações Globais</span>
          </Button>
        }
      />
      <SheetContent side="right" className="w-[400px] sm:w-[540px] overflow-y-auto">
        <SheetHeader className="pb-6">
          <SheetTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" />
            Infraestrutura de Engenharia
          </SheetTitle>
          <SheetDescription>
            Configure as unidades globais, casos de carga e combinações normativas para todo o projeto Atlas.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-8 py-4">
          {/* Unidades Globais */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-muted-foreground">
              <Ruler className="w-3.5 h-3.5" />
              Sistema de Unidades
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase">Comprimento</Label>
                <Select value={unitConfig.length} onValueChange={(v) => updateUnitConfig({ length: v as LengthUnit })}>
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="m">Metros (m)</SelectItem>
                    <SelectItem value="cm">Centímetros (cm)</SelectItem>
                    <SelectItem value="mm">Milímetros (mm)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] uppercase">Força</Label>
                <Select value={unitConfig.force} onValueChange={(v) => updateUnitConfig({ force: v as ForceUnit })}>
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="kN">Quilonewton (kN)</SelectItem>
                    <SelectItem value="tf">Tonelada-força (tf)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] uppercase">Tensão</Label>
                <Select value={unitConfig.stress} onValueChange={(v) => updateUnitConfig({ stress: v as StressUnit })}>
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MPa">Megapascal (MPa)</SelectItem>
                    <SelectItem value="kPa">Quilopascal (kPa)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </section>

          <Separator />

          {/* Casos de Carga */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-muted-foreground">
                <Zap className="w-3.5 h-3.5" />
                Casos de Carga
              </div>
              <Button onClick={addLoadCase} variant="outline" size="sm" className="h-7 text-[10px] font-black uppercase tracking-widest gap-1">
                <Plus className="w-3 h-3" /> Adicionar
              </Button>
            </div>
            
            <div className="space-y-2">
              {loadCases.map((lc) => (
                <div key={lc.id} className="flex items-center gap-2 p-2 rounded-lg bg-muted/30 border border-border/50">
                  <Input 
                    value={lc.name} 
                    onChange={(e) => updateLoadCase(lc.id, { name: e.target.value })}
                    className="h-8 text-xs bg-background/50 flex-1"
                  />
                  <Select value={lc.type} onValueChange={(v) => updateLoadCase(lc.id, { type: v as LoadCaseType })}>
                    <SelectTrigger className="h-8 w-24 text-[10px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pp">Peso Próprio</SelectItem>
                      <SelectItem value="perm">Permanente</SelectItem>
                      <SelectItem value="acid">Acidental</SelectItem>
                      <SelectItem value="wind">Vento</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input 
                    type="number"
                    value={lc.factor} 
                    onChange={(e) => updateLoadCase(lc.id, { factor: Number(e.target.value) })}
                    className="h-8 w-16 text-xs bg-background/50 text-center"
                  />
                  <Button onClick={() => removeLoadCase(lc.id)} variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              ))}
            </div>
          </section>

          <Separator />

          {/* Combinações */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-muted-foreground">
              <Filter className="w-3.5 h-3.5" />
              Combinações (ELU / ELS)
            </div>
            
            <div className="space-y-4">
              {combinations.map((comb, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-primary/5 border border-primary/10 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-primary">{comb.name}</span>
                    <Badge variant="outline" className="text-[8px] font-black uppercase tracking-tighter">NBR 6118</Badge>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {comb.cases.map((c) => {
                      const lCase = loadCases.find(lc => lc.id === c.id);
                      return (
                        <Badge key={c.id} variant="secondary" className="text-[9px] gap-1 px-2 py-0.5 bg-background">
                          <span className="text-muted-foreground font-medium">{lCase?.name || c.id}</span>
                          <span className="text-primary font-bold">x{c.gamma}</span>
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
            
            <p className="text-[10px] text-muted-foreground italic leading-relaxed">
              * As combinações configuradas aqui serão aplicadas automaticamente em todos os solvers de sistemas (Pórticos, Treliças e Lajes Avançadas).
            </p>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  );
}
