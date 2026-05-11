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
  const sectionWidth = bf || b;
  const displayWidth = 420;
  const displayHeight = 520;
  const margin = { top: 54, right: 76, bottom: 72, left: 92 };
  const drawableW = displayWidth - margin.left - margin.right;
  const drawableH = displayHeight - margin.top - margin.bottom;
  const scale = Math.min(drawableW / sectionWidth, drawableH / h);
  const concreteW = sectionWidth * scale;
  const concreteH = h * scale;
  const concreteX = margin.left + (drawableW - concreteW) / 2;
  const concreteY = margin.top + (drawableH - concreteH) / 2;
  const webX = concreteX + ((sectionWidth - b) / 2) * scale;
  const coverPx = Math.max(cover * scale, 10);
  const stirrupInset = coverPx;
  const stirrupX = webX + stirrupInset;
  const stirrupY = concreteY + stirrupInset;
  const stirrupW = Math.max(b * scale - 2 * stirrupInset, 8);
  const stirrupH = Math.max(concreteH - 2 * stirrupInset, 8);

  const barRadius = (diameter: number) => {
    const trueRadius = (diameter / 1000) * scale / 2;
    return Math.max(4.5, Math.min(8.5, trueRadius * 2.2));
  };

  const layerY = (position: 'bottom' | 'top' | 'skin', radius: number) => {
    if (position === 'bottom') return stirrupY + stirrupH - radius - 7;
    if (position === 'top') return stirrupY + radius + 7;
    return stirrupY + stirrupH / 2;
  };

  const barColor = (position: 'bottom' | 'top' | 'skin') => {
    if (position === 'top') return '#f97316';
    if (position === 'skin') return '#64748b';
    return '#2563eb';
  };

  const dimensionColor = '#64748b';
  
  return (
    <div className="w-full flex flex-col items-center bg-white dark:bg-zinc-950 rounded-2xl border border-border/50 p-5 shadow-sm overflow-hidden animate-in fade-in zoom-in-95 duration-500">
      <div className="w-full flex justify-between items-start gap-3 mb-4">
        <div>
          <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/70">Corte transversal da armadura</span>
          <p className="mt-1 text-xs text-muted-foreground">Concreto, estribo, cobrimento e barras longitudinais.</p>
        </div>
        <div className="flex gap-2">
          <span className="bg-primary/5 text-primary text-[10px] font-bold px-3 py-1 rounded-full border border-primary/10">
            {Math.round(b*100)}x{Math.round(h*100)} cm
          </span>
        </div>
      </div>

      <svg viewBox={`0 0 ${displayWidth} ${displayHeight}`} className="max-w-[420px] w-full h-auto">
        <defs>
          <marker id="section-arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto">
            <path d="M 0 0 L 7 3.5 L 0 7 z" fill={dimensionColor} />
          </marker>
        </defs>

        {/* Geometria de Concreto */}
        <g fill="rgba(148, 163, 184, 0.10)" stroke="rgba(100, 116, 139, 0.55)" strokeWidth="2.5">
          {bf && hf ? (
             <path d={`
                M ${concreteX} ${concreteY} 
                H ${concreteX + bf * scale} 
                V ${concreteY + hf * scale} 
                H ${concreteX + (bf + b) / 2 * scale} 
                V ${concreteY + concreteH} 
                H ${concreteX + (bf - b) / 2 * scale} 
                V ${concreteY + hf * scale} 
                H ${concreteX} 
                Z`} 
             />
          ) : (
            <rect x={webX} y={concreteY} width={b * scale} height={concreteH} rx="3" />
          )}
        </g>

        {/* Cobrimento e estribo */}
        <rect
          x={stirrupX}
          y={stirrupY}
          width={stirrupW}
          height={stirrupH}
          fill="none"
          stroke="#0f172a"
          strokeWidth="2.2"
          rx="8"
        />
        <line x1={webX} y1={stirrupY} x2={stirrupX} y2={stirrupY} stroke={dimensionColor} strokeWidth="1.5" markerEnd="url(#section-arrow)" />
        <text x={webX - 6} y={stirrupY - 8} textAnchor="start" className="text-[10px] fill-slate-500 font-bold">
          cobr. {Math.round(cover * 1000)} mm
        </text>
        <text x={stirrupX + stirrupW / 2} y={stirrupY + stirrupH / 2} textAnchor="middle" className="text-[10px] fill-slate-400 font-black uppercase tracking-widest">
          seção
        </text>

        {/* Armaduras Longitudinais */}
        {layers.map((layer, lIdx) => (
          <g key={lIdx}>
            {layer.bars.map((barSet) => {
              const radius = barRadius(barSet.diameter);
              const y = layerY(layer.position, radius);
              
              return Array.from({ length: barSet.count }).map((_, i) => {
                const x = barSet.count === 1 
                  ? stirrupX + stirrupW / 2
                  : stirrupX + radius + 10 + (i * (stirrupW - 2 * radius - 20) / (barSet.count - 1));
                
                return (
                  <g key={i}>
                    <circle cx={x} cy={y} r={radius + 2} fill="white" stroke="rgba(15, 23, 42, 0.18)" strokeWidth="1" />
                    <circle cx={x} cy={y} r={radius} fill={barColor(layer.position)} stroke="#111827" strokeWidth="1.2" />
                  </g>
                );
              });
            })}
          </g>
        ))}

        {layers.map((layer, idx) => {
          const first = layer.bars[0];
          if (!first || first.count <= 0) return null;
          const radius = barRadius(first.diameter);
          const y = layerY(layer.position, radius);
          const label = layer.position === 'top' ? 'armadura superior' : layer.position === 'bottom' ? 'armadura inferior' : 'armadura de pele';
          const labelY = layer.position === 'bottom' ? y + 31 : y - 20;
          return (
            <g key={`label-${idx}`}>
              <line x1={stirrupX + stirrupW + 8} y1={y} x2={stirrupX + stirrupW + 42} y2={labelY} stroke={barColor(layer.position)} strokeWidth="1.6" />
              <text x={stirrupX + stirrupW + 46} y={labelY - 4} className="text-[10px] fill-slate-500 font-black uppercase tracking-wider">
                {label}
              </text>
              <text x={stirrupX + stirrupW + 46} y={labelY + 11} className="text-[11px] fill-slate-900 dark:fill-slate-100 font-bold">
                {first.count}ø{first.diameter}
              </text>
            </g>
          );
        })}

        {/* Cotas */}
        <line x1={webX} y1={concreteY + concreteH + 28} x2={webX + b * scale} y2={concreteY + concreteH + 28} stroke={dimensionColor} strokeWidth="1.5" />
        <line x1={webX} y1={concreteY + concreteH + 20} x2={webX} y2={concreteY + concreteH + 36} stroke={dimensionColor} strokeWidth="1.5" />
        <line x1={webX + b * scale} y1={concreteY + concreteH + 20} x2={webX + b * scale} y2={concreteY + concreteH + 36} stroke={dimensionColor} strokeWidth="1.5" />
        <text x={webX + (b/2) * scale} y={concreteY + concreteH + 52} textAnchor="middle" className="text-[13px] fill-slate-600 font-black">{Math.round(b*100)} cm</text>
        
        <line x1={webX - 28} y1={concreteY} x2={webX - 28} y2={concreteY + concreteH} stroke={dimensionColor} strokeWidth="1.5" />
        <line x1={webX - 36} y1={concreteY} x2={webX - 20} y2={concreteY} stroke={dimensionColor} strokeWidth="1.5" />
        <line x1={webX - 36} y1={concreteY + concreteH} x2={webX - 20} y2={concreteY + concreteH} stroke={dimensionColor} strokeWidth="1.5" />
        <text x={webX - 50} y={concreteY + (h/2) * scale} textAnchor="middle" transform={`rotate(-90, ${webX - 50}, ${concreteY + (h/2) * scale})`} className="text-[13px] fill-slate-600 font-black">{Math.round(h*100)} cm</text>

        {stirrups && (
          <text x={webX} y={concreteY - 18} className="text-[10px] fill-slate-500 font-bold">
            Estribo ø{stirrups.diameter} c/{stirrups.spacing} cm
          </text>
        )}
      </svg>

      <div className="mt-4 w-full grid grid-cols-1 sm:grid-cols-3 gap-3">
        <LegendItem color="#0f172a" label="Estribo" value={stirrups ? `ø${stirrups.diameter} c/${stirrups.spacing}` : 'não informado'} />
        {layers.filter(l => l.bars[0].count > 0).map((l, i) => (
          <LegendItem
            key={i}
            color={barColor(l.position)}
            label={l.position === 'top' ? 'Superior' : l.position === 'bottom' ? 'Inferior' : 'Pele'}
            value={`${l.bars[0].count}ø${l.bars[0].diameter}`}
          />
        ))}
      </div>
    </div>
  );
}

function LegendItem({ color, label, value }: { color: string; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 border border-border/50 min-w-0">
      <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color }} />
      <div className="flex flex-col min-w-0">
        <span className="text-[9px] font-black uppercase text-muted-foreground tracking-wider truncate">
          {label}
        </span>
        <span className="text-sm font-bold truncate">{value}</span>
      </div>
    </div>
  );
}
