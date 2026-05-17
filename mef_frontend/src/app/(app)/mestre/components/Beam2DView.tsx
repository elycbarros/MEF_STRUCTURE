'use client';

import React from 'react';
import { useMestreStore } from '@/lib/store-mestre';

export function Beam2DView() {
  const { params, selectedElementType, fullResults } = useMestreStore();

  // Se for beam_cross, usamos a lista de vãos. Se for beam isolada, simulamos um vão único.
  const isCross = selectedElementType === 'beam_cross';
  const spans = isCross && params.spans ? params.spans : [
    {
      id: 'V1',
      length: params.L || 6.0,
      loads: [
        ...(params.distributed_loads && params.distributed_loads.length > 0
          ? params.distributed_loads.map((dl: any) => ({
              type: 'udl' as const,
              value: dl.q_start,
              q_end: dl.q_end,
              x_start: dl.x_start,
              x_end: dl.x_end
            }))
          : params.q > 0 ? [{ type: 'udl' as const, value: params.q, x_start: 0, x_end: params.L || 6.0 }] : []),
        ...(params.point_loads || []).map((pl: any) => ({ type: 'point' as const, value: pl.P, position: pl.x }))
      ]
    }
  ];

  const safeNum = (v: any, fallback = 0) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : fallback;
  };

  const totalLength = safeNum(spans.reduce((sum, s) => sum + safeNum(s.length), 0));
  const h = safeNum(params.h, 0.50);

  // --- Reações calculadas (pós-cálculo) ---
  // Viga Isolada: fullResults.reactions = { N1: { x, R, type }, N2: {...} }
  // Viga Cross:   fullResults vem do store via nodeReactions[] do vigacross
  const calcReactions: { x: number; value: number; label: string }[] = (() => {
    if (!fullResults) return [];

    // Viga Isolada (beam) — backend retorna reactions como objeto
    if (!isCross && fullResults.reactions && typeof fullResults.reactions === 'object') {
      const raw = Object.values(fullResults.reactions) as any[];
      return raw
        .sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
        .map((r, idx) => ({
          x: safeNum(r.x, 0),
          value: safeNum(r.R ?? r.value ?? r.vertical ?? 0),
          label: `V${String.fromCharCode(97 + idx)}`
        }));
    }

    // Viga Cross — nodeReactions já estão no resultado do solveCross (via store fullResults)
    if (isCross && fullResults.nodeReactions) {
      let xAcc = 0;
      const spanLengths = (params.spans || []).map((s: any) => safeNum(s.length));
      return (fullResults.nodeReactions as any[]).map((r: any, idx: number) => {
        const x = spanLengths.slice(0, idx).reduce((a: number, b: number) => a + b, 0);
        xAcc += idx < spanLengths.length ? spanLengths[idx] ?? 0 : 0;
        return {
          x,
          value: safeNum(r.verticalReaction),
          label: r.nodeId || `N${idx + 1}`
        };
      });
    }

    return [];
  })();

  // Viewbox dinâmico
  const padding = 1.0;
  const loadZoneH = 0.9; // espaço acima da viga para cargas
  const reactionZoneH = calcReactions.length > 0 ? 0.85 : 0; // espaço abaixo para reações
  const totalSvgH = h + loadZoneH + reactionZoneH + padding * 2;

  const viewBox = `${-padding} ${-(loadZoneH + h / 2)} ${totalLength + padding * 2} ${totalSvgH}`;

  const renderSupportSymbol = (rawX: number, type: string, i: number) => {
    const x = safeNum(rawX);
    const color = "text-primary";
    if (type === 'fixed') {
      return (
        <g key={`sup-${i}`}>
          <rect x={x - 0.05} y={-h / 2 - 0.2} width={0.1} height={h + 0.4} fill="currentColor" className="text-slate-400" />
          {[...Array(5)].map((_, j) => (
            <line
              key={j}
              x1={x - 0.05} y1={-h / 2 - 0.2 + j * 0.2}
              x2={x - 0.15} y2={-h / 2 - 0.2 + j * 0.2 + 0.1}
              stroke="currentColor" strokeWidth="0.01" className="text-slate-400"
            />
          ))}
        </g>
      );
    }

    // Apoio Móvel (1º Gênero)
    if (type === 'roller') {
      const size = 0.25;
      return (
        <g key={`sup-${i}`}>
          <polygon points={`${x},${h / 2} ${x - size / 2},${h / 2 + size} ${x + size / 2},${h / 2 + size}`} fill="none" stroke="currentColor" strokeWidth="0.03" className={color} />
          <line x1={x - size / 2} y1={h / 2 + size + 0.05} x2={x + size / 2} y2={h / 2 + size + 0.05} stroke="currentColor" strokeWidth="0.02" className={color} />
        </g>
      );
    }

    // Apoio Fixo (2º Gênero)
    const size = 0.25;
    return (
      <g key={`sup-${i}`}>
        <polygon points={`${x},${h / 2} ${x - size / 2},${h / 2 + size} ${x + size / 2},${h / 2 + size}`} fill="none" stroke="currentColor" strokeWidth="0.03" className={color} />
        <line x1={x - size} y1={h / 2 + size} x2={x + size} y2={h / 2 + size} stroke="currentColor" strokeWidth="0.02" className="text-primary/30" />
      </g>
    );
  };

  const renderSupports = () => {
    if (isCross) {
      let currentX = 0;
      const symbols = [];
      const supportTypes: string[] = ((params.supports as any[]) || []).map((s: any) =>
        typeof s === 'string' ? s : (s?.type ?? 'pin')
      );

      for (let i = 0; i <= spans.length; i++) {
        const type = supportTypes[i] || 'pin';
        if (type !== 'free') {
          symbols.push(renderSupportSymbol(currentX, type === 'pin' ? 'pinned' : type, i));
        }
        if (i < spans.length) currentX += spans[i].length;
      }
      return symbols;
    }

    const currentSupports: any[] = params.supports || [];
    if (currentSupports.length > 0) {
      return currentSupports.map((s: any, i: number) => renderSupportSymbol(typeof s === 'object' ? s.x : 0, typeof s === 'object' ? s.type : s, i));
    }

    return [
      renderSupportSymbol(0, 'pinned', 0),
      renderSupportSymbol(totalLength, 'pinned', 1)
    ];
  };

  // Altura da seta de reação (proporcional ao maior valor)
  const maxReaction = calcReactions.length > 0 ? Math.max(...calcReactions.map(r => Math.abs(r.value))) : 1;
  const reactionArrowMaxH = 0.7;
  const reactionArrowH = (val: number) =>
    maxReaction > 0 ? reactionArrowMaxH * (Math.abs(val) / maxReaction) : reactionArrowMaxH;

  return (
    <div className="w-full h-full bg-white dark:bg-slate-950 rounded-2xl border border-border/50 shadow-inner flex items-center justify-center relative overflow-hidden group">
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '20px 20px' }} />

      <svg viewBox={viewBox} className="w-[90%] h-[90%] drop-shadow-2xl transition-all duration-500" preserveAspectRatio="xMidYMid meet">
        <defs>
          <marker id="arrowhead-2d" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
            <polygon points="0 0, 5 3.5, 0 7" fill="currentColor" />
          </marker>
          <marker id="arrowhead-reaction" markerWidth="10" markerHeight="7" refX="5" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
          </marker>
        </defs>

        {/* Vãos da Viga */}
        {(() => {
          let currentX = 0;
          return spans.map((span, i) => {
            const x = safeNum(currentX);
            const spanLen = safeNum(span.length);
            currentX += spanLen;
            return (
              <g key={`span-${i}`}>
                {/* Corpo do Vão */}
                <rect
                  x={x} y={-h / 2} width={spanLen} height={h}
                  fill="currentColor" fillOpacity="0.08" stroke="currentColor" strokeWidth="0.02"
                  className="text-slate-400 dark:text-slate-600"
                />

                {/* Cargas do Vão */}
                {span.loads?.map((load: any, li: number) => {
                  if (load.type === 'udl') {
                    const startX = x + safeNum(load.x_start, 0);
                    const endX = x + safeNum(load.x_end, spanLen);
                    const qStart = safeNum(load.value, 0);
                    const qEnd = safeNum(load.q_end, qStart);

                    const currentUDLLen = endX - startX;
                    const numArrows = Math.max(Math.floor(currentUDLLen * 4), 2);

                    const hStart = 0.4 * (qStart / 20);
                    const hEnd = 0.4 * (qEnd / 20);

                    return (
                      <g key={`load-${i}-${li}`} className="text-destructive/30">
                        {[...Array(numArrows)].map((_, arrowIdx) => {
                          const t = numArrows > 1 ? arrowIdx / (numArrows - 1) : 0;
                          const arrowX = startX + currentUDLLen * t;
                          const arrowH = hStart + (hEnd - hStart) * t;
                          return (
                            <line
                              key={arrowIdx}
                              x1={arrowX} y1={-h / 2 - Math.max(arrowH, 0.1)}
                              x2={arrowX} y2={-h / 2 - 0.05}
                              stroke="currentColor" strokeWidth="0.015" markerEnd="url(#arrowhead-2d)"
                            />
                          );
                        })}
                        <line x1={startX} y1={-h / 2 - Math.max(hStart, 0.1)} x2={endX} y2={-h / 2 - Math.max(hEnd, 0.1)} stroke="currentColor" strokeWidth="0.015" />

                        {/* Labels */}
                        <text x={startX} y={-h / 2 - Math.max(hStart, 0.1) - 0.1} textAnchor="start" fontSize="0.12" fontWeight="bold" fill="currentColor">
                          {qStart.toFixed(0)}
                        </text>
                        {qStart !== qEnd && (
                          <text x={endX} y={-h / 2 - Math.max(hEnd, 0.1) - 0.1} textAnchor="end" fontSize="0.12" fontWeight="bold" fill="currentColor">
                            {qEnd.toFixed(0)}
                          </text>
                        )}
                        <text x={(startX + endX) / 2} y={-h / 2 - Math.max(hStart, hEnd, 0.1) - 0.25} textAnchor="middle" fontSize="0.1" fill="currentColor" className="opacity-60">
                          kN/m
                        </text>
                      </g>
                    );
                  }
                  if (load.type === 'point') {
                    const px = x + safeNum(load.position);
                    const pVal = safeNum(load.value);
                    return (
                      <g key={`load-${i}-${li}`} className="text-destructive">
                        <line
                          x1={px} y1={-h / 2 - 0.8} x2={px} y2={-h / 2 - 0.05}
                          stroke="currentColor" strokeWidth="0.025" markerEnd="url(#arrowhead-2d)"
                        />
                        <text x={px} y={-h / 2 - 0.9} textAnchor="middle" fontSize="0.15" fontWeight="black" fill="currentColor">
                          {pVal} kN
                        </text>
                      </g>
                    );
                  }
                  return null;
                })}
              </g>
            );
          })
        })()}

        {/* Eixo Central */}
        <line x1={0} y1={0} x2={totalLength} y2={0} stroke="currentColor" strokeWidth="0.005" strokeDasharray="0.1 0.05" className="text-primary/20" />

        {/* Apoios */}
        {renderSupports()}

        {/* ── Reações Calculadas (pós-cálculo) ── */}
        {calcReactions.map((r, idx) => {
          const rx = safeNum(r.x);
          const ah = reactionArrowH(r.value);
          const isUp = r.value >= 0;
          // Seta: nasce abaixo da base da viga, aponta para cima (se reação positiva)
          const yTip = h / 2 + 0.05;      // ponta da seta (toca a base da viga)
          const yTail = yTip + ah;         // cauda da seta

          return (
            <g key={`react-${idx}`} className="animate-in fade-in duration-500">
              {/* Linha da seta */}
              <line
                x1={rx} y1={isUp ? yTail : yTip}
                x2={rx} y2={isUp ? yTip : yTail}
                stroke="#ef4444" strokeWidth="0.04"
                markerEnd="url(#arrowhead-reaction)"
              />
              {/* Label valor */}
              <text
                x={rx} y={yTail + 0.18}
                textAnchor="middle" fontSize="0.13" fontWeight="bold"
                fill="#ef4444"
              >
                {r.label} = {Math.abs(r.value).toFixed(1)} kN
              </text>
            </g>
          );
        })}

        {/* Cotas */}
        <g className="text-slate-400">
          <line x1={0} y1={h / 2 + 0.6} x2={totalLength} y2={h / 2 + 0.6} stroke="currentColor" strokeWidth="0.01" />
          <text x={totalLength / 2} y={h / 2 + 0.85} textAnchor="middle" fontSize="0.18" fontWeight="black" fill="currentColor" className="text-foreground">
            {totalLength.toFixed(2)}m
          </text>
        </g>
      </svg>

      {/* Badge inferior */}
      <div className="absolute bottom-4 left-4 flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
            {isCross ? 'Viga Contínua (Hardy Cross)' : 'Viga Isolada (MEF)'}
          </span>
        </div>
        <div className="bg-background/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border/50 shadow-sm">
          <p className="text-xs font-bold text-foreground">
            {totalLength.toFixed(2)}m <span className="text-muted-foreground mx-1">×</span> {(h * 100).toFixed(0)}cm
            {calcReactions.length > 0 && (
              <span className="ml-2 text-red-500 text-[10px]">
                · {calcReactions.length} reações
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
