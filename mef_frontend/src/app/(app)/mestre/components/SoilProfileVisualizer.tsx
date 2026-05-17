'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useMestreStore } from '@/lib/store-mestre';
import { SoilLayer } from '@/lib/mestre-types';
import { cn } from '@/lib/utils';
import { ArrowDown, GripVertical, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

const SOIL_TYPES = [
  { id: 'areia', label: 'Areia', color: 'bg-amber-100 border-amber-300 text-amber-800' },
  { id: 'argila', label: 'Argila', color: 'bg-rose-100 border-rose-300 text-rose-800' },
  { id: 'silte', label: 'Silte', color: 'bg-slate-200 border-slate-300 text-slate-800' },
  { id: 'rocha', label: 'Rocha', color: 'bg-slate-400 border-slate-500 text-white' },
];

export function SoilProfileVisualizer() {
  const { params, updateParams } = useMestreStore();
  const [draggingLayerIndex, setDraggingLayerIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const layers = params.layers || [];
  const maxDepth = 20; // Escala visual máxima em metros
  const scale = 30; // pixels por metro

  const handleMouseDown = (index: number) => (e: React.MouseEvent) => {
    setDraggingLayerIndex(index);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (draggingLayerIndex === null || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const relativeY = e.clientY - rect.top;
      const newDepth = Math.max(0.5, Math.min(maxDepth, relativeY / scale));

      const newLayers = [...layers];
      // Ajustar a espessura da camada atual e o depth da próxima
      const prevDepth = draggingLayerIndex > 0 ? newLayers[draggingLayerIndex - 1].depth_m : 0;
      newLayers[draggingLayerIndex].depth_m = newDepth;
      newLayers[draggingLayerIndex].thickness_m = Math.max(0.2, newDepth - prevDepth);

      // Cascata: ajustar profundidades das camadas seguintes se necessário
      for (let i = draggingLayerIndex + 1; i < newLayers.length; i++) {
        newLayers[i].depth_m = newLayers[i-1].depth_m + newLayers[i].thickness_m;
      }

      updateParams({ layers: newLayers });
    };

    const handleMouseUp = () => setDraggingLayerIndex(null);

    if (draggingLayerIndex !== null) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [draggingLayerIndex, layers, updateParams]);

  const addLayer = () => {
    const lastDepth = layers.length > 0 ? layers[layers.length - 1].depth_m : 0;
    const newLayer: SoilLayer = {
      depth_m: lastDepth + 2.0,
      thickness_m: 2.0,
      nspt: 10,
      soil_type: 'areia'
    };
    updateParams({ layers: [...layers, newLayer] });
  };

  const removeLayer = (index: number) => {
    const newLayers = layers.filter((_, i) => i !== index);
    // Recalcular profundidades
    let currentDepth = 0;
    const updated = newLayers.map(l => {
      currentDepth += l.thickness_m;
      return { ...l, depth_m: currentDepth };
    });
    updateParams({ layers: updated });
  };

  const updateLayerType = (index: number, type: string) => {
    const newLayers = [...layers];
    newLayers[index].soil_type = type;
    updateParams({ layers: newLayers });
  };

  const updateNSpt = (index: number, val: string) => {
    const n = parseInt(val);
    if (!isNaN(n)) {
      const newLayers = [...layers];
      newLayers[index].nspt = n;
      updateParams({ layers: newLayers });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
          <ArrowDown className="w-3 h-3" />
          Perfil de Sondagem (SPT)
        </h4>
        <Button onClick={addLayer} variant="ghost" size="sm" className="h-6 text-[9px] gap-1 px-2 border border-primary/20 text-primary hover:bg-primary/5">
          <Plus className="w-3 h-3" /> Camada
        </Button>
      </div>

      <div className="flex gap-6 items-start">
        {/* Régua de Profundidade */}
        <div className="w-8 flex flex-col items-end text-[10px] text-muted-foreground font-mono pt-1">
          {[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20].map(d => (
            <div key={d} style={{ height: d === 20 ? 0 : 2 * scale }} className="relative">
              <span className="absolute -top-1.5 right-1">{d}m</span>
              {d < 20 && <div className="w-1.5 h-px bg-border absolute top-0 right-0" />}
            </div>
          ))}
        </div>

        {/* Visualizador de Camadas */}
        <div 
          ref={containerRef}
          className="flex-1 relative bg-muted/20 rounded-xl border border-dashed border-border/60 overflow-hidden"
          style={{ height: maxDepth * scale }}
        >
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
            <defs>
              <pattern id="pattern-areia" width="4" height="4" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.5" fill="currentColor" />
              </pattern>
              <pattern id="pattern-argila" width="10" height="10" patternUnits="userSpaceOnUse">
                <line x1="0" y1="10" x2="10" y2="0" stroke="currentColor" strokeWidth="0.5" />
              </pattern>
              <pattern id="pattern-silte" width="8" height="8" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1" fill="currentColor" />
                <circle cx="6" cy="6" r="1" fill="currentColor" />
              </pattern>
              <pattern id="pattern-rocha" width="12" height="12" patternUnits="userSpaceOnUse">
                <path d="M0 0 L12 12 M12 0 L0 12" stroke="currentColor" strokeWidth="1" />
              </pattern>
            </defs>
          </svg>

          {layers.map((layer, idx) => {
            const soil = SOIL_TYPES.find(t => t.id === layer.soil_type) || SOIL_TYPES[0];
            const top = idx === 0 ? 0 : layers[idx - 1].depth_m * scale;
            const height = layer.thickness_m * scale;

            return (
              <div 
                key={idx}
                className={cn(
                  "absolute left-0 w-full border-b flex items-center transition-shadow group/layer",
                  soil.color,
                  draggingLayerIndex === idx && "z-10 shadow-xl brightness-95"
                )}
                style={{ top, height }}
              >
                {/* Pattern Overlay */}
                <div 
                  className="absolute inset-0 opacity-10 pointer-events-none" 
                  style={{ 
                    backgroundImage: `url(#pattern-${layer.soil_type})`,
                    backgroundSize: '10px 10px' // fallback visual
                  }} 
                />

                <div className="px-3 flex items-center justify-between w-full relative z-10">
                  <div className="flex flex-col">
                    <span className="text-[9px] font-black uppercase opacity-70 leading-none">{soil.label}</span>
                    <div className="flex items-center gap-2 mt-1">
                      <input 
                        type="number" 
                        value={layer.nspt}
                        onChange={(e) => updateNSpt(idx, e.target.value)}
                        className="w-10 bg-white/60 border-none text-[11px] font-bold rounded px-1 focus:ring-1 ring-primary outline-none"
                      />
                      <span className="text-[9px] font-bold opacity-50">N_spt</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 opacity-0 group-hover/layer:opacity-100 transition-opacity">
                    <select 
                      value={layer.soil_type}
                      onChange={(e) => updateLayerType(idx, e.target.value)}
                      className="bg-white/60 border-none text-[9px] font-bold rounded px-1 py-0.5 outline-none cursor-pointer"
                    >
                      {SOIL_TYPES.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
                    </select>
                    <button 
                      onClick={() => removeLayer(idx)}
                      className="p-1 hover:text-destructive transition-colors bg-white/40 rounded shadow-sm"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                {/* Depth Indicator (Center) */}
                <div className="absolute right-2 top-1/2 -translate-y-1/2 text-[8px] font-mono text-black/20 font-bold">
                  Δz = {layer.thickness_m.toFixed(2)}m
                </div>

                {/* Handle de Arrasto (Base da Camada) */}
                <div 
                  onMouseDown={handleMouseDown(idx)}
                  className="absolute bottom-0 left-0 w-full h-3 cursor-ns-resize flex items-center justify-center group-hover/layer:bg-black/10 transition-colors"
                >
                  <div className="w-12 h-1 bg-black/20 rounded-full opacity-40 group-hover/layer:opacity-100" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="p-3 bg-primary/5 border border-primary/10 rounded-xl">
        <p className="text-[9px] text-muted-foreground leading-relaxed italic">
          Arraste a borda inferior de cada camada para ajustar a espessura. Defina o N_spt para o cálculo automático da tensão admissível.
        </p>
      </div>
    </div>
  );
}
