'use client';

import React from 'react';
import { useMestreStore } from '@/lib/store-mestre';

const safeNum = (v: unknown, fallback = 0): number => {
  const n = parseFloat(String(v));
  return Number.isFinite(n) ? n : fallback;
};

// ── Helper: normalise a series of {x,y} or DiagramPoint into {x,y} ──────────
function normaliseSeries(raw: unknown[]): { x: number; y: number }[] {
  if (!raw?.length) return [];
  const first = raw[0] as any;
  if ('xGlobal' in first) return raw.map((p: any) => ({ x: p.xGlobal, y: p.shear ?? 0 }));
  return raw.map((p: any) => ({ x: safeNum(p.x), y: safeNum(p.y) }));
}
function normaliseMoment(raw: unknown[]): { x: number; y: number }[] {
  if (!raw?.length) return [];
  const first = raw[0] as any;
  if ('xGlobal' in first) return raw.map((p: any) => ({ x: p.xGlobal, y: p.moment ?? 0 }));
  return raw.map((p: any) => ({ x: safeNum(p.x), y: safeNum(p.y) }));
}

// ── SVG polygon from series ──────────────────────────────────────────────────
function makePolygon(
  pts: { x: number; y: number }[],
  totalLen: number,
  maxAbsVal: number,
  stripH: number,   // height of the diagram strip in SVG units
  baseY: number,    // y-coordinate of the baseline
  flip = false,     // moment convention: positive down
  xScale = 1,
): string {
  if (!pts.length || maxAbsVal < 1e-6) return '';
  const yScale = (stripH * 0.85) / maxAbsVal;
  const toSvgY = (v: number) => baseY + (flip ? -v : v) * yScale;
  const scaled = pts.map(p => ({ x: p.x * xScale, y: toSvgY(p.y) }));
  const first = scaled[0];
  const last = scaled[scaled.length - 1];
  return [
    `${first.x},${baseY}`,
    ...scaled.map(p => `${p.x},${p.y}`),
    `${last.x},${baseY}`,
  ].join(' ');
}

export function Beam2DView() {
  const { params, selectedElementType, fullResults } = useMestreStore();

  const isCross = selectedElementType === 'beam_cross';

  // ── Spans ─────────────────────────────────────────────────────────────────
  const spans: any[] = isCross && params.spans
    ? params.spans
    : [{
        id: 'V1',
        length: params.L || 6.0,
        loads: [
          ...(params.distributed_loads?.length
            ? params.distributed_loads.map((dl: any) => ({
                type: 'udl',
                value: dl.q_start,
                q_end: dl.q_end,
                x_start: dl.x_start,
                x_end: dl.x_end,
              }))
            : params.q > 0
              ? [{ type: 'udl', value: params.q, x_start: 0, x_end: params.L || 6.0 }]
              : []),
          ...(params.point_loads || []).map((pl: any) => ({ type: 'point', value: pl.P, moment: pl.M || 0, position: pl.x })),
        ],
      }];

  const totalLength = Math.max(spans.reduce((s, sp) => s + safeNum(sp.length), 0), 0.1);
  const h = safeNum(params.h, 0.5);

  // ── Diagram data ──────────────────────────────────────────────────────────
  let shearPts: { x: number; y: number }[] = [];
  let momentPts: { x: number; y: number }[] = [];
  const hasDiagrams = !!fullResults;

  if (fullResults) {
    if (!isCross) {
      // Beam isolada: diagrams.shear / diagrams.moment (array {x,y})
      if (fullResults.diagrams?.shear)  shearPts  = normaliseSeries(fullResults.diagrams.shear);
      if (fullResults.diagrams?.moment) momentPts = normaliseMoment(fullResults.diagrams.moment);
    } else {
      // Viga Cross: diagrams is DiagramPoint[]
      if (Array.isArray(fullResults.diagrams)) {
        shearPts  = fullResults.diagrams.map((p: any) => ({ x: p.xGlobal, y: p.shear ?? 0 }));
        momentPts = fullResults.diagrams.map((p: any) => ({ x: p.xGlobal, y: p.moment ?? 0 }));
      }
    }
  }

  const maxShear  = shearPts.length  ? Math.max(...shearPts.map(p  => Math.abs(p.y)),  0.01) : 1;
  const maxMoment = momentPts.length ? Math.max(...momentPts.map(p => Math.abs(p.y)), 0.01) : 1;

  // ── Reactions ─────────────────────────────────────────────────────────────
  const calcReactions: { x: number; value: number; label: string }[] = (() => {
    if (!fullResults) return [];
    if (!isCross && fullResults.reactions && typeof fullResults.reactions === 'object') {
      return (Object.values(fullResults.reactions) as any[])
        .sort((a, b) => (a.x ?? 0) - (b.x ?? 0))
        .map((r: any, i) => ({ x: safeNum(r.x), value: safeNum(r.R ?? r.value ?? 0), label: `V${String.fromCharCode(97 + i)}` }));
    }
    if (isCross && fullResults.nodeReactions) {
      const lengths = (params.spans || []).map((s: any) => safeNum(s.length));
      return (fullResults.nodeReactions as any[]).map((r: any, i) => ({
        x: lengths.slice(0, i).reduce((a: number, b: number) => a + b, 0),
        value: safeNum(r.verticalReaction),
        label: r.nodeId || `N${i + 1}`,
      }));
    }
    return [];
  })();

  const maxReaction = calcReactions.length ? Math.max(...calcReactions.map(r => Math.abs(r.value)), 0.01) : 1;

  const beamSupports: { x: number; type: string }[] = (() => {
    const rawSupports = Array.isArray(params.supports) ? params.supports : [];
    const explicit = rawSupports
      .map((s: any) => {
        if (typeof s === 'string') return null;
        if (!s || typeof s !== 'object') return null;
        return { x: safeNum(s.x, Number.NaN), type: String(s.type || 'pinned') };
      })
      .filter((s): s is { x: number; type: string } => !!s && Number.isFinite(s.x));

    if (!isCross && explicit.length > 0) return explicit;

    if (!isCross && calcReactions.length > 0) {
      return calcReactions.map((r, i) => ({
        x: r.x,
        type: i === 0 ? 'pinned' : 'roller',
      }));
    }

    return [
      { x: 0, type: 'pinned' },
      { x: totalLength, type: 'roller' },
    ];
  })();

  // ── Layout constants ──────────────────────────────────────────────────────
  const loadZone    = 0.9;          // above beam
  const reactZone   = (calcReactions.length > 0 || beamSupports.length > 0) ? 0.7 : 0;
  const stripH      = hasDiagrams ? 0.8 : 0;   // height of each diagram strip (V and M)
  const stripGap    = hasDiagrams ? 0.15 : 0;  // gap between strips
  const labelZone   = hasDiagrams ? 0.25 : 0;  // label row under each strip

  const totalSvgH = loadZone + h + reactZone + (stripH + stripGap + labelZone) * (hasDiagrams ? 2 : 0) + 0.4;

  // Y positions (top of each section, relative to beam centreline at y=0)
  const beamTop    = -h / 2;
  const beamBot    =  h / 2;
  const reactBase  = beamBot + 0.06;
  const shearBase  = beamBot + reactZone + 0.12;
  const momentBase = shearBase + stripH + stripGap + labelZone + 0.05;

  const viewBox = `${-0.6} ${-(loadZone + h / 2)} ${totalLength + 1.2} ${totalSvgH}`;

  // ── Markers ───────────────────────────────────────────────────────────────
  const markerDefs = (
    <defs>
      <marker id="arr-load" markerWidth="6" markerHeight="5" refX="0" refY="2.5" orient="auto">
        <polygon points="0 0,5 2.5,0 5" fill="currentColor" />
      </marker>
      <marker id="arr-react" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">
        <polygon points="0 0,8 3,0 6" fill="#ef4444" />
      </marker>
    </defs>
  );

  // ── Support symbol renderer ───────────────────────────────────────────────
  const renderSupport = (x: number, type: string, key: number) => {
    const sz = 0.22;
    const base = beamBot;
    if (type === 'fixed') {
      return (
        <g key={key}>
          <rect x={x - 0.06} y={beamTop - 0.1} width={0.12} height={h + 0.2} fill="#2563eb" opacity={0.8} />
          {[...Array(5)].map((_, j) => (
            <line key={j} x1={x - 0.06} y1={beamTop - 0.1 + j * 0.2} x2={x - 0.18} y2={beamTop + j * 0.2} stroke="#2563eb" strokeWidth="0.012" />
          ))}
        </g>
      );
    }
    const tri = `${x},${base} ${x - sz / 2},${base + sz} ${x + sz / 2},${base + sz}`;
    return (
      <g key={key}>
        <polygon points={tri} fill="rgba(37, 99, 235, 0.10)" stroke="#2563eb" strokeWidth="0.025" />
        {type === 'pin' || type === 'pinned'
          ? <line x1={x - sz / 2} y1={base + sz + 0.04} x2={x + sz / 2} y2={base + sz + 0.04} stroke="#2563eb" strokeWidth="0.018" />
          : <>
              <line x1={x - sz} y1={base + sz} x2={x + sz} y2={base + sz} stroke="#2563eb" strokeWidth="0.018" />
              <circle cx={x - sz * 0.5} cy={base + sz + 0.07} r="0.04" fill="#2563eb" />
              <circle cx={x}           cy={base + sz + 0.07} r="0.04" fill="#2563eb" />
              <circle cx={x + sz * 0.5} cy={base + sz + 0.07} r="0.04" fill="#2563eb" />
            </>}
      </g>
    );
  };

  const renderSupports = () => {
    if (isCross) {
      const types: string[] = ((params.supports as any[]) || []).map((s: any) =>
        typeof s === 'string' ? s : (s?.type ?? 'pin'));
      let cx = 0;
      return spans.map((sp, i) => {
        const el = types[i] && types[i] !== 'free' ? renderSupport(cx, types[i], i) : null;
        cx += safeNum(sp.length);
        if (i === spans.length - 1 && types[i + 1] && types[i + 1] !== 'free') {
          return [el, renderSupport(cx, types[i + 1], i + 100)];
        }
        return el;
      });
    }
    return beamSupports.map((support, i) => renderSupport(support.x, support.type, i));
  };

  // ── Load rendering ────────────────────────────────────────────────────────
  const renderLoads = () => {
    let cx = 0;
    return spans.flatMap((span, si) => {
      const spanLen = safeNum(span.length);
      const x0 = cx;
      cx += spanLen;
      return (span.loads || []).map((load: any, li: number) => {
        if (load.type === 'udl') {
          const sx = x0 + safeNum(load.x_start, 0);
          const ex = x0 + safeNum(load.x_end, spanLen);
          const q1 = safeNum(load.value, 0);
          const q2 = safeNum(load.q_end, q1);
          const w = ex - sx;
          const nArrows = Math.max(Math.floor(w * 5), 3);
          const hMax = 0.55;
          return (
            <g key={`l-${si}-${li}`} className="text-destructive/60">
              {[...Array(nArrows)].map((_, ai) => {
                const t  = nArrows > 1 ? ai / (nArrows - 1) : 0;
                const ax = sx + w * t;
                const ah = Math.max(hMax * ((q1 + (q2 - q1) * t) / 20), 0.08);
                return <line key={ai} x1={ax} y1={beamTop - ah} x2={ax} y2={beamTop - 0.04} stroke="currentColor" strokeWidth="0.012" markerEnd="url(#arr-load)" />;
              })}
              <line x1={sx} y1={beamTop - Math.max(hMax * q1 / 20, 0.08)} x2={ex} y2={beamTop - Math.max(hMax * q2 / 20, 0.08)} stroke="currentColor" strokeWidth="0.012" />
              <text x={(sx + ex) / 2} y={beamTop - Math.max(hMax * Math.max(q1, q2) / 20, 0.08) - 0.14} textAnchor="middle" fontSize="0.11" fontWeight="700" fill="currentColor">
                {q1 === q2 ? `${q1} kN/m` : `${q1}→${q2} kN/m`}
              </text>
            </g>
          );
        }
        if (load.type === 'point') {
          const px  = x0 + safeNum(load.position);
          const pv  = safeNum(load.value);
          const mv  = safeNum(load.moment);
          return (
            <g key={`l-${si}-${li}`}>
              {pv > 0 && (
                <g className="text-destructive">
                  <line x1={px} y1={beamTop - 0.75} x2={px} y2={beamTop - 0.04} stroke="currentColor" strokeWidth="0.022" markerEnd="url(#arr-load)" />
                  <text x={px} y={beamTop - 0.84} textAnchor="middle" fontSize="0.13" fontWeight="900" fill="currentColor">{pv} kN</text>
                </g>
              )}
              {mv !== 0 && (
                <g className="text-orange-500">
                  <path
                    d={mv > 0
                      ? `M ${px + 0.15} ${beamTop - 0.4} A 0.15 0.15 0 1 0 ${px} ${beamTop - 0.25}`
                      : `M ${px - 0.15} ${beamTop - 0.4} A 0.15 0.15 0 1 1 ${px} ${beamTop - 0.25}`
                    }
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="0.025"
                    markerEnd="url(#arr-load)"
                  />
                  <text x={px} y={beamTop - 0.62} textAnchor="middle" fontSize="0.12" fontWeight="900" fill="currentColor">{Math.abs(mv)} kNm</text>
                </g>
              )}
            </g>
          );
        }
        return null;
      });
    });
  };

  // ── Diagram strip builder ─────────────────────────────────────────────────
  const renderStrip = (
    pts: { x: number; y: number }[],
    maxVal: number,
    baseY: number,
    color: string,
    fillOpacity: number,
    label: string,
    unit: string,
    flip = false,
  ) => {
    if (!pts.length) return null;
    const poly = makePolygon(pts, totalLength, maxVal, stripH, baseY, flip);
    const maxPt = pts.reduce((best, p) => Math.abs(p.y) > Math.abs(best.y) ? p : best, pts[0]);
    const minPt = pts.reduce((best, p) => p.y < best.y ? p : best, pts[0]);
    const yScale = (stripH * 0.85) / maxVal;
    const toSvgY = (v: number) => baseY + (flip ? -v : v) * yScale;

    return (
      <g>
        {/* Baseline */}
        <line x1={0} y1={baseY} x2={totalLength} y2={baseY} stroke={color} strokeWidth="0.012" opacity={0.4} />
        {/* Vão dividers */}
        {(() => { let cx2 = 0; return spans.slice(0, -1).map((sp, i) => { cx2 += safeNum(sp.length); return <line key={i} x1={cx2} y1={baseY} x2={cx2} y2={baseY + (flip ? -stripH : stripH)} stroke={color} strokeWidth="0.008" strokeDasharray="0.04 0.04" opacity={0.3} />; }); })()}
        {/* Filled polygon */}
        <polygon points={poly} fill={color} fillOpacity={fillOpacity} stroke={color} strokeWidth="0.018" strokeLinejoin="round" />
        {/* Zero crossings */}
        {pts.map((p, i) => {
          if (i === 0 || !pts[i - 1]) return null;
          const prev = pts[i - 1];
          if ((prev.y < 0 && p.y >= 0) || (prev.y >= 0 && p.y < 0)) {
            const t = -prev.y / (p.y - prev.y);
            const zx = prev.x + t * (p.x - prev.x);
            return <circle key={i} cx={zx} cy={baseY} r="0.025" fill={color} />;
          }
          return null;
        })}
        {/* Max value annotation */}
        <circle cx={maxPt.x} cy={toSvgY(maxPt.y)} r="0.035" fill={color} />
        <text x={maxPt.x} y={toSvgY(maxPt.y) - 0.09} textAnchor="middle" fontSize="0.1" fontWeight="700" fill={color}>
          {maxPt.y.toFixed(1)}
        </text>
        {/* Min value annotation (if different) */}
        {Math.abs(minPt.y - maxPt.y) > 0.5 && (
          <>
            <circle cx={minPt.x} cy={toSvgY(minPt.y)} r="0.035" fill={color} />
            <text x={minPt.x} y={toSvgY(minPt.y) + 0.18} textAnchor="middle" fontSize="0.1" fontWeight="700" fill={color}>
              {minPt.y.toFixed(1)}
            </text>
          </>
        )}
        {/* Strip label */}
        <text x={-0.08} y={baseY + (flip ? -stripH * 0.5 : stripH * 0.5)} textAnchor="end" fontSize="0.095" fontWeight="900" fill={color} opacity={0.8}>
          {label}
        </text>
        <text x={-0.08} y={baseY + (flip ? -stripH * 0.5 : stripH * 0.5) + 0.14} textAnchor="end" fontSize="0.08" fill={color} opacity={0.5}>
          {unit}
        </text>
      </g>
    );
  };

  return (
    <div className="w-full h-full bg-white dark:bg-slate-950 rounded-2xl border border-border/50 shadow-inner flex items-center justify-center relative overflow-hidden group">
      {/* Grid background */}
      <div className="absolute inset-0 opacity-[0.025] pointer-events-none"
        style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '18px 18px' }} />

      <svg
        viewBox={viewBox}
        className="w-[92%] h-[92%] transition-all duration-700"
        preserveAspectRatio="xMidYMid meet"
      >
        {markerDefs}

        {/* ── Beam spans ── */}
        {(() => {
          let cx = 0;
          return spans.map((span, i) => {
            const sl = safeNum(span.length);
            const x = cx; cx += sl;
            return (
              <g key={i}>
                <rect x={x} y={beamTop} width={sl} height={h}
                  fill="currentColor" fillOpacity="0.07" stroke="currentColor" strokeWidth="0.02"
                  className="text-slate-400 dark:text-slate-600" />
                {/* span label */}
                <text x={x + sl / 2} y={0.04} textAnchor="middle" fontSize="0.09" fill="currentColor" className="text-slate-400" opacity={0.5}>
                  L{i + 1}={sl.toFixed(2)}m
                </text>
              </g>
            );
          });
        })()}

        {/* Neutral axis */}
        <line x1={0} y1={0} x2={totalLength} y2={0} stroke="currentColor" strokeWidth="0.005" strokeDasharray="0.08 0.05" className="text-primary/15" />

        {/* ── Loads ── */}
        {renderLoads()}

        {/* ── Supports ── */}
        {renderSupports()}

        {/* ── Reaction arrows (post-calc) ── */}
        {calcReactions.map((r, i) => {
          const ah = 0.55 * (Math.abs(r.value) / maxReaction);
          const tip = beamBot + 0.04;
          const tail = tip + Math.max(ah, 0.18);
          return (
            <g key={i} className="animate-in fade-in duration-500">
              <line x1={r.x} y1={tail} x2={r.x} y2={tip} stroke="#ef4444" strokeWidth="0.035" markerEnd="url(#arr-react)" />
              <text x={r.x} y={tail + 0.18} textAnchor="middle" fontSize="0.11" fontWeight="700" fill="#ef4444">
                {r.label}={Math.abs(r.value).toFixed(1)} kN
              </text>
            </g>
          );
        })}

        {/* ── Diagram strips ── */}
        {hasDiagrams && shearPts.length > 0 && (
          <g className="animate-in fade-in duration-700">
            {/* Shear separator line */}
            <line x1={-0.5} y1={shearBase - 0.06} x2={totalLength + 0.2} y2={shearBase - 0.06} stroke="currentColor" strokeWidth="0.008" strokeDasharray="0.06 0.04" className="text-slate-300 dark:text-slate-700" />
            {renderStrip(shearPts, maxShear, shearBase, 'hsl(217 91% 55%)', 0.18, 'V', 'kN', false)}
          </g>
        )}

        {hasDiagrams && momentPts.length > 0 && (
          <g className="animate-in fade-in duration-1000">
            <line x1={-0.5} y1={momentBase - 0.06} x2={totalLength + 0.2} y2={momentBase - 0.06} stroke="currentColor" strokeWidth="0.008" strokeDasharray="0.06 0.04" className="text-slate-300 dark:text-slate-700" />
            {/* Moment positive downward convention (flip=true) */}
            {renderStrip(momentPts, maxMoment, momentBase, 'hsl(262 83% 58%)', 0.2, 'M', 'kNm', true)}
          </g>
        )}

        {/* ── Dimension line ── */}
        <g className="text-slate-400">
          <line x1={0} y1={beamBot + reactZone + 0.25} x2={totalLength} y2={beamBot + reactZone + 0.25} stroke="currentColor" strokeWidth="0.01" />
          <text x={totalLength / 2} y={beamBot + reactZone + 0.45} textAnchor="middle" fontSize="0.16" fontWeight="900" fill="currentColor" className="text-foreground">
            {totalLength.toFixed(2)} m
          </text>
        </g>
      </svg>

      {/* Badge */}
      <div className="absolute bottom-3 left-3 flex flex-col gap-1 pointer-events-none">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">
            {isCross ? 'Hardy Cross' : 'MEF 2ª Ordem'}
          </span>
        </div>
        <div className="bg-background/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-border/50 shadow-sm">
          <p className="text-xs font-bold text-foreground">
            {totalLength.toFixed(2)}m × {(h * 100).toFixed(0)}cm
            {hasDiagrams && shearPts.length > 0 && (
              <span className="ml-1.5 text-[10px] text-blue-500">· V+M inline</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
