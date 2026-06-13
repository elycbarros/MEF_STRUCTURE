import React, { useMemo } from 'react';

interface Point {
  x: number;
  y: number;
}

interface Series {
  name: string;
  points: Point[];
  color?: string;
  dashed?: boolean;
}

interface StructuralDiagramProps {
  data: {
    type: 'shear' | 'moment' | 'deflection' | string;
    unit: string;
    label: string;
    title?: string;
    series: Series[];
    reactions?: {
      x: number;
      value: number;
      label: string;
    }[];
  };
}

export function StructuralDiagram({ data }: StructuralDiagramProps) {
  const { series, type, unit, label } = data;

  const { minX, maxX, minY, maxY, width, height, padding } = useMemo(() => {
    let allPoints: Point[] = [];
    series.forEach(s => { allPoints = [...allPoints, ...s.points]; });

    const xs = allPoints.map(p => p.x);
    const ys = allPoints.map(p => p.y);

    const minX = xs.length > 0 ? Math.min(...xs) : 0;
    const maxX = xs.length > 0 ? Math.max(...xs) : 1;
    const minY = ys.length > 0 ? Math.min(...ys, 0) : -1;
    const maxY = ys.length > 0 ? Math.max(...ys, 0) : 1;

    return {
      minX, maxX, minY, maxY,
      width: 800,
      height: 320,
      padding: 50
    };
  }, [series]);

  const getX = (x: number) => padding + ((x - minX) / (maxX - minX || 1)) * (width - 2 * padding);
  const getY = (y: number) => {
    const rangeY = maxY - minY || 1;
    let normalizedY = (y - minY) / rangeY;

    // Convenção de Engenharia Estrutural: Momento Positivo para BAIXO
    if (type === 'moment') {
      normalizedY = 1 - normalizedY;
    }

    return height - padding - 30 - normalizedY * (height - 2 * padding - 30);
  };

  const getPath = (points: Point[]) => {
    if (points.length === 0) return '';
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(p.x)} ${getY(p.y)}`).join(' ');
  };

  const getAreaPath = (points: Point[]) => {
    if (points.length === 0) return '';
    const d = getPath(points);
    const baselineY = getY(0);
    const firstX = getX(points[0].x);
    const lastX = getX(points[points.length - 1].x);
    return `${d} L ${lastX} ${baselineY} L ${firstX} ${baselineY} Z`;
  };

  const defaultColors = {
    shear: 'hsl(217 91% 55%)',
    moment: 'hsl(262 83% 58%)',
    deflection: 'hsl(142 76% 45%)'
  }[type] || 'hsl(217 91% 55%)';

  const fmt = (v: number) => v.toLocaleString('pt-BR', { maximumFractionDigits: 2 });

  return (
    <div className="w-full bg-white dark:bg-zinc-950 rounded-2xl border border-border/50 p-6 shadow-md overflow-hidden animate-in fade-in zoom-in-95 duration-500">
      <div className="flex justify-between items-center mb-6 px-2">
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60">{label}</span>
          <h4 className="text-sm font-bold text-foreground">{data.title || "Duelo Analítico: MEF vs Clássico"}</h4>
        </div>
        <div className="bg-primary/5 border border-primary/10 px-3 py-1.5 rounded-full">
          <span className="text-[10px] font-mono font-black text-primary">UNIDADE: {unit}</span>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto overflow-visible select-none"
      >
        {/* Support Graphic Symbols on Baseline */}
        {data.reactions?.map((r, idx) => {
          const rx = getX(r.x);
          const ry = getY(0);
          const sz = 8;
          return (
            <g key={`sup-sym-${idx}`} className="text-zinc-300 dark:text-zinc-700 animate-in fade-in duration-500">
              <polygon
                points={`${rx},${ry} ${rx - sz},${ry + sz * 1.5} ${rx + sz},${ry + sz * 1.5}`}
                fill="currentColor"
                fillOpacity="0.2"
                stroke="currentColor"
                strokeWidth="1.5"
              />
              <line
                x1={rx - sz * 1.3}
                y1={ry + sz * 1.5 + 2}
                x2={rx + sz * 1.3}
                y2={ry + sz * 1.5 + 2}
                stroke="currentColor"
                strokeWidth="1.5"
              />
            </g>
          );
        })}

        {/* Grids Horizontais (Eixos) */}
        <line
          x1={getX(minX)} y1={getY(minY)}
          x2={getX(minX)} y2={getY(maxY)}
          stroke="currentColor" strokeWidth="1" strokeOpacity="0.1"
        />
        <line
          x1={getX(minX)} y1={getY(0)}
          x2={getX(maxX)} y2={getY(0)}
          stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.4"
          className="text-muted-foreground"
        />

        {series.map((s, idx) => {
          const color = s.color || defaultColors;
          return (
            <g key={idx} className="transition-opacity hover:opacity-100 opacity-95">
              {/* Área Sombreada */}
              {idx === 0 && (
                <path d={getAreaPath(s.points)} fill={color} fillOpacity="0.06" />
              )}
              {/* Linha do Diagrama */}
              <path
                d={getPath(s.points)}
                fill="none"
                stroke={color}
                strokeWidth={idx === 0 ? "3" : "2"}
                strokeDasharray={s.dashed ? "6 4" : "0"}
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Pontos de Destaque (Máximos) */}
              {s.points.length > 0 && (
                (() => {
                  const absYs = s.points.map(p => Math.abs(p.y));
                  const maxIdx = absYs.indexOf(Math.max(...absYs));
                  const pMax = s.points[maxIdx];
                  const yPos = getY(pMax.y);
                  const isPositive = pMax.y >= 0;
                  // Se for momento, positivo é para baixo, então offset inverte
                  const offset = type === 'moment'
                    ? (isPositive ? 25 : -15)
                    : (isPositive ? -15 : 25);

                  return (
                    <g>
                      <circle cx={getX(pMax.x)} cy={yPos} r={idx === 0 ? "4" : "3"} fill={color} />
                      {idx === 0 && (
                        <text
                          x={getX(pMax.x)}
                          y={yPos + offset}
                          textAnchor="middle"
                          className="fill-foreground text-[12px] font-black font-mono"
                        >
                          {fmt(pMax.y)} {unit}
                        </text>
                      )}
                    </g>
                  );
                })()
              )}
            </g>
          );
        })}

        {/* Node Indicators on Zero Line */}
        {data.reactions?.map((r, idx) => {
          const rx = getX(r.x);
          const ry = getY(0);
          return (
            <circle
              key={`node-circle-${idx}`}
              cx={rx}
              cy={ry}
              r="4"
              fill="white"
              stroke={defaultColors}
              strokeWidth="2.5"
              className="drop-shadow-sm"
            />
          );
        })}

        {/* Eixo X - Comprimento */}
        <text x={getX(minX)} y={getY(0) - 10} textAnchor="start" className="fill-muted-foreground text-[10px] font-bold">0.0m</text>
        <text x={getX(maxX)} y={getY(0) - 10} textAnchor="end" className="fill-muted-foreground text-[10px] font-bold">{maxX.toFixed(1)}m</text>

        {/* Reações de Apoio */}
        {data.reactions?.map((r, idx) => {
          const xPos = getX(r.x);
          const yBase = getY(0);
          const isUp = r.value >= 0;
          const arrowLen = 35;

          const y1 = yBase + (isUp ? arrowLen + 15 : -arrowLen - 15);
          const y2 = yBase + (isUp ? 15 : -15);

          return (
            <g key={idx} className="animate-in fade-in zoom-in-50 duration-1000 delay-300">
              {/* Seta da Reação */}
              <line
                x1={xPos} y1={y1}
                x2={xPos} y2={y2}
                stroke="#ef4444" strokeWidth="2.5"
                markerEnd="url(#arrowhead)"
              />
              <text
                x={xPos}
                y={yBase + (isUp ? arrowLen + 28 : -arrowLen - 22)}
                textAnchor="middle"
                className="fill-red-500 text-[11px] font-black font-mono"
              >
                {r.label}: {fmt(Math.abs(r.value))} kN
              </text>
            </g>
          );
        })}

        {/* Definição da Seta */}
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
          </marker>
        </defs>
      </svg>

      {/* Legenda Profissional */}
      <div className="mt-4 flex justify-center gap-6 border-t border-border/40 pt-4">
        {series.map((s, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div
              className={`w-8 h-1 rounded-full ${s.dashed ? 'border-t-2 border-dashed' : ''}`}
              style={{ backgroundColor: s.dashed ? 'transparent' : (s.color || defaultColors), borderColor: s.color || defaultColors }}
            />
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{s.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

