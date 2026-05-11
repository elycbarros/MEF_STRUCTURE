import React from 'react';

interface BeamSectionDetailProps {
  data: {
    type: 'beam_section' | 'column_section';
    b: number;
    h: number;
    bf?: number;
    hf?: number;
    cover: number;
    layers: {
      position: 'bottom' | 'top' | 'skin';
      bars: {
        count: number;
        diameter: number;
      }[];
    }[];
    stirrups?: {
      diameter: number;
      spacing: number;
      legs: number;
    };
  };
}

export function BeamSectionDetail({ data }: BeamSectionDetailProps) {
  const { b, h, bf, hf, cover, layers, stirrups } = data;
  
  const scale = 300 / Math.max(b, h, bf || 0);
  const width = (bf || b) * scale + 100;
  const height = h * scale + 100;
  
  const offsetX = 50 + ((bf || b) - b) / 2 * scale;
  const offsetY = 50;

  return (
    <div className="w-full flex flex-col items-center bg-white dark:bg-zinc-950 rounded-2xl border border-border/50 p-8 shadow-sm overflow-hidden animate-in fade-in zoom-in-95 duration-500">
      <div className="w-full flex justify-between items-center mb-6">
        <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Corte Transversal Detalhado (Escala 1:10)</span>
        <div className="flex gap-2">
          <span className="bg-primary/5 text-primary text-[10px] font-bold px-3 py-1 rounded-full border border-primary/10">
            {Math.round(b*100)}x{Math.round(h*100)} cm
          </span>
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="max-w-[400px] w-full h-auto drop-shadow-2xl">
        {/* Geometria de Concreto */}
        <g className="fill-muted/20 stroke-muted-foreground/40" strokeWidth="2">
          {bf && hf ? (
             <path d={`
                M ${50} ${offsetY} 
                H ${50 + bf * scale} 
                V ${offsetY + hf * scale} 
                H ${50 + (bf + b) / 2 * scale} 
                V ${offsetY + h * scale} 
                H ${50 + (bf - b) / 2 * scale} 
                V ${offsetY + hf * scale} 
                H ${50} 
                Z`} 
             />
          ) : (
            <rect x={offsetX} y={offsetY} width={b * scale} height={h * scale} />
          )}
        </g>

        {/* Estribos */}
        {stirrups && (
          <rect 
            x={offsetX + cover * scale} 
            y={offsetY + cover * scale} 
            width={(b - 2 * cover) * scale} 
            height={(h - 2 * cover) * scale} 
            fill="none" 
            stroke="#94a3b8" 
            strokeWidth="3"
            rx="5"
          />
        )}

        {/* Armaduras Longitudinais */}
        {layers.map((layer, lIdx) => (
          <g key={lIdx}>
            {layer.bars.map((barSet) => {
              const radius = (barSet.diameter / 1000) * scale * 5; // Exagerado para visualização
              const y = layer.position === 'bottom' 
                ? offsetY + (h - cover) * scale - radius
                : layer.position === 'top' 
                ? offsetY + cover * scale + radius
                : offsetY + (h / 2) * scale;
              
              return Array.from({ length: barSet.count }).map((_, i) => {
                const x = barSet.count === 1 
                  ? offsetX + (b / 2) * scale
                  : offsetX + cover * scale + radius + (i * ((b - 2 * cover) * scale - 2 * radius) / (barSet.count - 1));
                
                return (
                  <circle 
                    key={i} 
                    cx={x} cy={y} r={radius} 
                    className="fill-zinc-800 dark:fill-zinc-200" 
                  />
                );
              });
            })}
          </g>
        ))}

        {/* Cotas */}
        <line x1={offsetX} y1={offsetY + h * scale + 20} x2={offsetX + b * scale} y2={offsetY + h * scale + 20} stroke="#64748b" strokeWidth="1" />
        <text x={offsetX + (b/2) * scale} y={offsetY + h * scale + 35} textAnchor="middle" className="text-[12px] fill-muted-foreground font-bold">{Math.round(b*100)}</text>
        
        <line x1={offsetX - 20} y1={offsetY} x2={offsetX - 20} y2={offsetY + h * scale} stroke="#64748b" strokeWidth="1" />
        <text x={offsetX - 35} y={offsetY + (h/2) * scale} textAnchor="middle" transform={`rotate(-90, ${offsetX - 35}, ${offsetY + (h/2) * scale})`} className="text-[12px] fill-muted-foreground font-bold">{Math.round(h*100)}</text>
      </svg>

      <div className="mt-8 w-full grid grid-cols-2 gap-4">
        {layers.filter(l => l.bars[0].count > 0).map((l, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 border border-border/50">
            <div className={`w-3 h-3 rounded-full ${l.position === 'top' ? 'bg-orange-500' : 'bg-blue-500'}`} />
            <div className="flex flex-col">
              <span className="text-[9px] font-black uppercase text-muted-foreground tracking-tighter">
                {l.position === 'top' ? 'Superior' : 'Inferior'}
              </span>
              <span className="text-sm font-bold">{l.bars[0].count}ø{l.bars[0].diameter}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
