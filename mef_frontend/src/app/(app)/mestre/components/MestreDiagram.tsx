import React from 'react';
import { ArrowDown, Activity } from 'lucide-react';

interface Point {
  x: number;
  y: number;
  label?: string;
}

interface Reaction {
  x: number;
  value: number;
  label?: string;
  type?: 'pinned' | 'fixed' | 'roller' | 'spring';
}

interface MestreDiagramProps {
  points: Point[];
  title: string;
  unit: string;
  color: string;
  fillColor: string;
  totalLength: number;
  height?: number;
  reactions?: Reaction[];
}

export function MestreDiagram({
  points,
  title,
  unit,
  color,
  fillColor,
  totalLength,
  height = 180,
  reactions = [],
}: MestreDiagramProps) {
  if (!points || points.length === 0) return null;

  const width = 720;
  const padX = 40;
  const padY = 30;
  
  const safeTotalLength = totalLength > 0 ? totalLength : 1;
  
  const yValues = points.map(p => p.y);
  const maxValue = Math.max(...yValues);
  const minValue = Math.min(...yValues);
  const absMax = Math.max(Math.abs(maxValue), Math.abs(minValue), 0.001);
  
  // Scale so that absMax fits in (height/2 - padY)
  const scaleY = (height / 2 - padY) / absMax;
  const zeroY = height / 2;

  const xFor = (x: number) => padX + (x / safeTotalLength) * (width - padX * 2);
  
  // Engineering Convention: Positive Moment is drawn DOWNWARDS
  const isMomentDiagram = title.toUpperCase().includes('MOMENTO');
  const yFor = (y: number) => {
    const val = isMomentDiagram ? -y : y;
    return zeroY - val * scaleY;
  };

  const polyline = points
    .map(p => `${xFor(p.x).toFixed(1)},${yFor(p.y).toFixed(1)}`)
    .join(' ');
  
  const areaPoints = `${padX},${zeroY.toFixed(1)} ${polyline} ${xFor(points[points.length-1].x).toFixed(1)},${zeroY.toFixed(1)}`;

  const fmt = (v: number) => v.toLocaleString('pt-BR', { maximumFractionDigits: 2 });

  return (
    <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ArrowDown className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{title}</span>
        </div>
        <div className="flex gap-3 text-[9px] font-black uppercase tracking-widest text-muted-foreground">
          <span className="text-primary">MÁX {fmt(maxValue)} {unit}</span>
          <span className="text-destructive">MÍN {fmt(minValue)} {unit}</span>
        </div>
      </div>

      <div className="relative group">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto drop-shadow-sm">
          {/* Base Line */}
          <line 
            x1={padX} y1={zeroY} x2={width - padX} y2={zeroY} 
            stroke="currentColor" className="text-border" strokeWidth="1" 
          />
          
          {/* Zero labels */}
          <text x={padX - 8} y={zeroY + 4} textAnchor="end" fontSize="10" fill="currentColor" className="text-muted-foreground/50">0</text>
          
          {/* Max/Min labels */}
          <text 
            x={padX - 8} 
            y={(isMomentDiagram ? height - padY : padY) + 4} 
            textAnchor="end" fontSize="10" fill="currentColor" className="text-primary font-bold"
          >
            {fmt(maxValue)}
          </text>
          <text 
            x={padX - 8} 
            y={(isMomentDiagram ? padY : height - padY) + 4} 
            textAnchor="end" fontSize="10" fill="currentColor" className="text-destructive font-bold"
          >
            {fmt(minValue)}
          </text>

          {/* Area Fill */}
          <polygon points={areaPoints} fill={fillColor} className="transition-all duration-500" />
          
          {/* Main Line */}
          <polyline 
            points={polyline} fill="none" stroke={color} 
            strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" 
            className="transition-all duration-500"
          />

          {/* Critical Points dots */}
          {points.filter((_, i) => i % Math.max(1, Math.floor(points.length / 10)) === 0 || i === points.length - 1).map((p, i) => (
            <circle 
              key={i} cx={xFor(p.x)} cy={yFor(p.y)} r="2" 
              fill={color} className="opacity-0 group-hover:opacity-100 transition-opacity" 
            />
          ))}

          {/* Reactions Arrows and Labels */}
          {reactions.map((r, i) => {
            const rx = xFor(r.x);
            const isUp = r.value >= 0;
            const arrowY1 = zeroY;
            const arrowY2 = isUp ? zeroY - 30 : zeroY + 30;
            
            return (
              <g key={`reaction-${i}`} className="animate-in fade-in zoom-in duration-700 delay-300">
                <line 
                  x1={rx} y1={arrowY1} x2={rx} y2={arrowY2} 
                  stroke="currentColor" className="text-primary" strokeWidth="2" 
                  markerEnd="url(#arrowhead-beam)"
                />
                <text 
                  x={rx} y={isUp ? arrowY2 - 8 : arrowY2 + 15} 
                  textAnchor="middle" fontSize="10" fontWeight="bold" 
                  fill="currentColor" className="text-primary bg-background/80"
                >
                  {fmt(Math.abs(r.value))}
                </text>
                <text 
                  x={rx} y={isUp ? arrowY2 - 20 : arrowY2 + 27} 
                  textAnchor="middle" fontSize="8" fontWeight="black" 
                  fill="currentColor" className="text-muted-foreground uppercase tracking-tighter"
                >
                  {r.label || `R${i+1}`}
                </text>

                {/* Support Graphic Symbol */}
                <g transform={`translate(${rx}, ${zeroY})`} className="text-muted-foreground/40">
                  {r.type === 'fixed' && (
                    <g>
                      <line x1="-8" y1="-10" x2="-8" y2="10" stroke="currentColor" strokeWidth="2" />
                      <line x1="-12" y1="-8" x2="-8" y2="-4" stroke="currentColor" strokeWidth="1" />
                      <line x1="-12" y1="-4" x2="-8" y2="0" stroke="currentColor" strokeWidth="1" />
                      <line x1="-12" y1="0" x2="-8" y2="4" stroke="currentColor" strokeWidth="1" />
                      <line x1="-12" y1="4" x2="-8" y2="8" stroke="currentColor" strokeWidth="1" />
                    </g>
                  )}
                  {r.type === 'pinned' && (
                    <path d="M-8,12 L8,12 L0,0 Z" fill="none" stroke="currentColor" strokeWidth="1.5" />
                  )}
                  {r.type === 'roller' && (
                    <g>
                      <path d="M-8,8 L8,8 L0,0 Z" fill="none" stroke="currentColor" strokeWidth="1.5" />
                      <line x1="-8" y1="12" x2="8" y2="12" stroke="currentColor" strokeWidth="1.5" />
                    </g>
                  )}
                </g>
              </g>
            );
          })}

          <defs>
            <marker id="arrowhead-beam" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="currentColor" className="text-primary" />
            </marker>
          </defs>
        </svg>
      </div>
    </div>
  );
}

interface Fiber {
  x: number;
  y: number;
  sig_MPa: number;
  eps: number;
}

interface MestreFiberMapProps {
  fibers: Fiber[];
  b: number;
  h: number;
  title: string;
}

export function MestreFiberMap({ fibers, b, h, title }: MestreFiberMapProps) {
  if (!fibers || fibers.length === 0) return null;

  const size = 300;
  const pad = 20;
  const innerSize = size - pad * 2;
  
  // Encontrar limites de tensão para o color map
  const stresses = fibers.map(f => f.sig_MPa);
  const maxSig = Math.max(...stresses, 0.1);

  // Mapear coordenadas (centro geométrico em 0,0) para coordenadas SVG
  const xFor = (x: number) => pad + (x / b + 0.5) * innerSize;
  const yFor = (y: number) => pad + (0.5 - y / h) * innerSize;

  // Tamanho de cada fibra no SVG
  const dx = (innerSize / Math.sqrt(fibers.length)) * 1.1;

  const getColor = (sig: number) => {
    if (sig === 0) return 'rgba(var(--muted-foreground), 0.1)';
    // Compressão: Tons de Vermelho/Laranja (sig > 0 no solver mestre)
    // Se sig > 0.85*fcd (aprox 20-40 MPa), vermelho intenso
    const intensity = Math.min(sig / maxSig, 1);
    return `rgba(239, 68, 68, ${0.1 + intensity * 0.9})`;
  };

  return (
    <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{title}</span>
        <div className="flex gap-2 text-[9px] font-black uppercase text-muted-foreground">
          <span>MAX σ: {maxSig.toFixed(1)} MPa</span>
        </div>
      </div>

      <div className="flex justify-center">
        <svg viewBox={`0 0 ${size} ${size}`} className="w-64 h-64 drop-shadow-sm">
          {/* Section Outline */}
          <rect 
            x={pad} y={pad} width={innerSize} height={innerSize} 
            fill="none" stroke="currentColor" className="text-border" strokeWidth="1" 
          />

          {/* Fibers */}
          {fibers.map((f, i) => (
            <rect
              key={i}
              x={xFor(f.x) - dx/2}
              y={yFor(f.y) - dx/2}
              width={dx}
              height={dx}
              fill={getColor(f.sig_MPa)}
              className="hover:stroke-white hover:stroke-[1px] transition-colors"
            >
              <title>{`σ = ${f.sig_MPa.toFixed(2)} MPa\nε = ${f.eps.toFixed(5)}`}</title>
            </rect>
          ))}
        </svg>
      </div>
    </div>
  );
}

export function MestreInteractionDiagram({ 
  envelope, 
  solicitant, 
  title, 
  unitM = "kNm", 
  unitN = "kN" 
}: {
  envelope: { n: number; m: number }[];
  solicitant: { n: number; m: number };
  title: string;
  unitM?: string;
  unitN?: string;
}) {
  if (!envelope || envelope.length === 0) return null;

  const size = 300;
  const pad = 40;
  const innerSize = size - pad * 2;

  const nValues = envelope.map(p => p.n);
  const mValues = envelope.map(p => p.m);
  
  const minN = Math.min(...nValues, solicitant.n);
  const maxN = Math.max(...nValues, solicitant.n);
  const maxM = Math.max(...mValues.map(Math.abs), Math.abs(solicitant.m), 0.1);

  // Scale N to fit height, M to fit width (centered)
  const scaleN = innerSize / (maxN - minN || 1);
  const scaleM = (innerSize / 2) / maxM;

  const xFor = (m: number) => pad + innerSize / 2 + m * scaleM;
  const yFor = (n: number) => pad + innerSize - (n - minN) * scaleN;

  const polyline = envelope
    .map(p => `${xFor(p.m).toFixed(1)},${yFor(p.n).toFixed(1)}`)
    .join(' ');

  const solX = xFor(solicitant.m);
  const solY = yFor(solicitant.n);

  return (
    <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{title}</span>
        <div className="flex gap-3 text-[9px] font-black uppercase text-muted-foreground">
          <span className="text-primary">Nd: {solicitant.n.toFixed(0)} {unitN}</span>
          <span className="text-primary">Md: {solicitant.m.toFixed(1)} {unitM}</span>
        </div>
      </div>

      <div className="flex justify-center">
        <svg viewBox={`0 0 ${size} ${size}`} className="w-64 h-64 drop-shadow-sm overflow-visible">
          {/* Axis */}
          <line x1={pad + innerSize/2} y1={pad} x2={pad + innerSize/2} y2={pad + innerSize} stroke="currentColor" className="text-border" strokeWidth="1" strokeDasharray="4 4" />
          <line x1={pad} y1={yFor(0)} x2={pad + innerSize} y2={yFor(0)} stroke="currentColor" className="text-border" strokeWidth="1" />

          {/* Envelope */}
          <polyline 
            points={polyline} fill="rgba(37, 99, 235, 0.1)" stroke="rgb(37, 99, 235)" 
            strokeWidth="2" strokeLinejoin="round" className="transition-all duration-500"
          />

          {/* Solicitant Point */}
          <circle cx={solX} cy={solY} r="4" fill="rgb(239, 68, 68)" className="animate-pulse" />
          <line x1={pad + innerSize/2} y1={solY} x2={solX} y2={solY} stroke="rgb(239, 68, 68)" strokeWidth="1" strokeDasharray="2 2" />
          <line x1={solX} y1={yFor(minN)} x2={solX} y2={solY} stroke="rgb(239, 68, 68)" strokeWidth="1" strokeDasharray="2 2" />

          {/* Labels */}
          <text x={pad + innerSize/2} y={pad - 10} textAnchor="middle" fontSize="10" fill="currentColor" className="text-muted-foreground font-bold">N</text>
          <text x={pad + innerSize + 10} y={yFor(0)} textAnchor="start" fontSize="10" fill="currentColor" className="text-muted-foreground font-bold">M</text>
        </svg>
      </div>
    </div>
  );
}

interface SystemNode {
  id: number;
  x: number;
  z: number;
  dx?: number;
  dz?: number;
}

interface SystemMember {
  node_i: number;
  node_j: number;
}

interface MestreSystemDiagramProps {
  nodes: SystemNode[];
  members: SystemMember[];
  title: string;
  deformedScale?: number;
  reactions?: Record<string, number[]>;
}

export function MestreSystemDiagram({
  nodes,
  members,
  title,
  deformedScale = 50,
  reactions = {},
}: MestreSystemDiagramProps) {
  if (!nodes || nodes.length === 0) return null;

  const width = 720;
  const height = 400;
  const pad = 60;

  // Calculate bounds including deformed state to avoid clipping
  const deformedNodes = nodes.map(n => ({
    x: n.x + (n.dx || 0) * deformedScale,
    z: n.z + (n.dz || 0) * deformedScale
  }));

  const minX = Math.min(...nodes.map(n => n.x), ...deformedNodes.map(n => n.x));
  const maxX = Math.max(...nodes.map(n => n.x), ...deformedNodes.map(n => n.x));
  const minZ = Math.min(...nodes.map(n => n.z), ...deformedNodes.map(n => n.z));
  const maxZ = Math.max(...nodes.map(n => n.z), ...deformedNodes.map(n => n.z));

  const rangeX = Math.max(maxX - minX, 0.1);
  const rangeZ = Math.max(maxZ - minZ, 0.1);

  const scale = Math.min((width - pad * 2) / rangeX, (height - pad * 2) / rangeZ);

  const xFor = (x: number) => pad + (x - minX) * scale;
  const zFor = (z: number) => height - pad - (z - minZ) * scale;

  return (
    <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
      <div className="flex items-center gap-2">
        <Activity className="w-3.5 h-3.5 text-primary" />
        <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{title}</span>
      </div>

      <div className="relative">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          {/* Undeformed Structure */}
          {members.map((m, i) => {
            const ni = nodes.find(n => n.id === m.node_i);
            const nj = nodes.find(n => n.id === m.node_j);
            if (!ni || !nj) return null;
            return (
              <line
                key={`und-${i}`}
                x1={xFor(ni.x)} y1={zFor(ni.z)}
                x2={xFor(nj.x)} y2={zFor(nj.z)}
                stroke="currentColor"
                strokeWidth="2"
                strokeDasharray="4 4"
                className="text-muted-foreground/30"
              />
            );
          })}

          {/* Deformed Structure */}
          {members.map((m, i) => {
            const ni = nodes.find(n => n.id === m.node_i);
            const nj = nodes.find(n => n.id === m.node_j);
            if (!ni || !nj) return null;
            
            const xi = ni.x + (ni.dx || 0) * deformedScale;
            const zi = ni.z + (ni.dz || 0) * deformedScale;
            const xj = nj.x + (nj.dx || 0) * deformedScale;
            const zj = nj.z + (nj.dz || 0) * deformedScale;

            return (
              <line
                key={`def-${i}`}
                x1={xFor(xi)} y1={zFor(zi)}
                x2={xFor(xj)} y2={zFor(zj)}
                stroke="#007AFF"
                strokeWidth="3"
                strokeLinecap="round"
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((n) => (
            <circle
              key={n.id}
              cx={xFor(n.x + (n.dx || 0) * deformedScale)}
              cy={zFor(n.z + (n.dz || 0) * deformedScale)}
              r="4"
              fill="white"
              stroke="#007AFF"
              strokeWidth="2"
            />
          ))}

          {/* Reaction Arrows */}
          {Object.entries(reactions).map(([nid, rVec]) => {
            const n = nodes.find(node => String(node.id) === nid);
            if (!n) return null;
            
            const nx = xFor(n.x);
            const nz = zFor(n.z);
            
            // Fz is vertical in our mapping (zFor)
            // Rx is horizontal (xFor)
            const rx_val = rVec[0];
            const rz_val = rVec[2]; // Fz is usually index 2 in 3D frame [Rx, Ry, Rz, Mx, My, Mz]
            
            return (
              <g key={`sys-reaction-${nid}`} className="text-primary animate-in fade-in zoom-in duration-700">
                {/* Vertical Reaction */}
                {Math.abs(rz_val) > 0.01 && (
                  <g>
                    <line 
                      x1={nx} y1={nz} x2={nx} y2={nz - (rz_val > 0 ? 40 : -40)} 
                      stroke="currentColor" strokeWidth="2" markerEnd="url(#arrowhead-system)"
                    />
                    <text x={nx + 5} y={nz - (rz_val > 0 ? 25 : -25)} fontSize="9" fontWeight="bold" fill="currentColor">
                      {fmt(Math.abs(rz_val))} kN
                    </text>
                  </g>
                )}
                {/* Horizontal Reaction */}
                {Math.abs(rx_val) > 0.01 && (
                  <g>
                    <line 
                      x1={nx} y1={nz} x2={nx + (rx_val > 0 ? 40 : -40)} y2={nz} 
                      stroke="currentColor" strokeWidth="2" markerEnd="url(#arrowhead-system)"
                    />
                    <text x={nx + (rx_val > 0 ? 20 : -20)} y={nz - 5} textAnchor="middle" fontSize="9" fontWeight="bold" fill="currentColor">
                      {fmt(Math.abs(rx_val))} kN
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          <defs>
            <marker id="arrowhead-system" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M0,0 L6,3 L0,6 Z" fill="currentColor" />
            </marker>
          </defs>
        </svg>
      </div>
    </div>
  );
}
