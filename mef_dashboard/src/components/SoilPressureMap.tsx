"use client";

import React from "react";

interface SoilPressureMapProps {
  Lx: number;
  Ly: number;
  qmax: number;
  qmed: number;
  sigma_adm: number;
  pillars?: Array<{ x: number; y: number; id: string; p_kN: number }>;
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function pressureToColor(q: number, qmin: number, qmax: number): string {
  if (qmax <= qmin) return "rgb(52,199,89)";
  const t = Math.max(0, Math.min(1, (q - qmin) / (qmax - qmin)));
  // verde → amarelo → vermelho
  if (t < 0.5) {
    const r = Math.round(lerp(52, 255, t * 2));
    const g = Math.round(lerp(199, 204, t * 2));
    const b = Math.round(lerp(89, 10, t * 2));
    return `rgb(${r},${g},${b})`;
  } else {
    const r = Math.round(lerp(255, 255, (t - 0.5) * 2));
    const g = Math.round(lerp(204, 45, (t - 0.5) * 2));
    const b = Math.round(lerp(10, 58, (t - 0.5) * 2));
    return `rgb(${r},${g},${b})`;
  }
}

export function SoilPressureMap({
  Lx,
  Ly,
  qmax,
  qmed,
  sigma_adm,
  pillars = [],
}: SoilPressureMapProps) {
  const W = 400;
  const H = Math.round((Ly / Lx) * W);
  const PAD = 32;
  const svgW = W + PAD * 2;
  const svgH = H + PAD * 2 + 50;

  // Grade 8×8 de pressões estimadas (distribuição simplificada Winkler)
  const NX = 10;
  const NY = 10;
  const cellW = W / NX;
  const cellH = H / NY;
  const qmin = qmed * 0.3;

  // Calcular pressão estimada em cada célula: pressão base + influência dos pilares
  const cells: { cx: number; cy: number; q: number }[] = [];
  for (let iy = 0; iy < NY; iy++) {
    for (let ix = 0; ix < NX; ix++) {
      const px = (ix + 0.5) / NX; // normalizado 0..1
      const py = (iy + 0.5) / NY;
      const worldX = px * Lx;
      const worldY = py * Ly;

      let q = qmed;
      if (pillars.length > 0) {
        // Influência gaussiana de cada pilar
        let maxInfluence = 0;
        for (const p of pillars) {
          const dx = (worldX - p.x) / Lx;
          const dy = (worldY - p.y) / Ly;
          const dist2 = dx * dx + dy * dy;
          const sigma = 0.12;
          const influence = Math.exp(-dist2 / (2 * sigma * sigma));
          maxInfluence = Math.max(maxInfluence, influence);
        }
        // Pressão varia entre qmed e qmax em função da proximidade de pilares
        q = qmed + (qmax - qmed) * maxInfluence;
      }
      cells.push({ cx: PAD + (ix + 0.5) * cellW, cy: PAD + (iy + 0.5) * cellH, q });
    }
  }

  const pressureRatio = qmax / Math.max(sigma_adm, 1);
  const ratioColor = pressureRatio >= 1 ? "#ff2d55" : pressureRatio >= 0.85 ? "#ff9f0a" : "#34c759";

  return (
    <div className="flex flex-col items-center gap-4">
      <svg
        width={svgW}
        height={svgH}
        viewBox={`0 0 ${svgW} ${svgH}`}
        className="rounded-xl border border-black/5 bg-white shadow-sm w-full max-w-[500px]"
      >
        {/* Grade de pressões */}
        {cells.map((cell, i) => (
          <rect
            key={i}
            x={cell.cx - cellW / 2}
            y={cell.cy - cellH / 2}
            width={cellW}
            height={cellH}
            fill={pressureToColor(cell.q, qmin, qmax)}
            opacity={0.82}
          />
        ))}

        {/* Borda do radier */}
        <rect
          x={PAD}
          y={PAD}
          width={W}
          height={H}
          fill="none"
          stroke="#1d171f"
          strokeWidth={2}
          rx={2}
        />

        {/* Pilares */}
        {pillars.map((p) => {
          const svgX = PAD + (p.x / Lx) * W;
          const svgY = PAD + (p.y / Ly) * H;
          return (
            <g key={p.id}>
              <circle cx={svgX} cy={svgY} r={6} fill="#1d171f" opacity={0.9} />
              <text
                x={svgX + 8}
                y={svgY - 6}
                fontSize={7}
                fill="#1d171f"
                fontFamily="monospace"
              >
                {p.id}
              </text>
            </g>
          );
        })}

        {/* Labels dimensão */}
        <text x={PAD + W / 2} y={PAD + H + 16} textAnchor="middle" fontSize={9} fill="#666" fontFamily="Arial">
          {Lx.toFixed(1)} m
        </text>
        <text
          x={PAD - 14}
          y={PAD + H / 2}
          textAnchor="middle"
          fontSize={9}
          fill="#666"
          fontFamily="Arial"
          transform={`rotate(-90, ${PAD - 14}, ${PAD + H / 2})`}
        >
          {Ly.toFixed(1)} m
        </text>

        {/* Legenda de escala */}
        {[0, 0.25, 0.5, 0.75, 1].map((t, i) => {
          const q = qmin + (qmax - qmin) * t;
          const lx = PAD + (W / 4) * i;
          return (
            <g key={i}>
              <rect x={lx} y={PAD + H + 24} width={W / 4} height={10} fill={pressureToColor(q, qmin, qmax)} />
              <text x={lx + 2} y={PAD + H + 44} fontSize={7} fill="#444" fontFamily="Arial">
                {q.toFixed(0)} kPa
              </text>
            </g>
          );
        })}
        <text x={PAD} y={PAD + H + 22} fontSize={7} fill="#888" fontFamily="Arial">
          Pressão de contato estimada:
        </text>
      </svg>

      {/* Métricas inline */}
      <div className="flex gap-4 text-xs font-medium">
        <span className="px-2 py-1 rounded bg-apple-bg/40 border border-black/5">
          σmáx = <strong>{qmax?.toFixed(1)} kPa</strong>
        </span>
        <span className="px-2 py-1 rounded bg-apple-bg/40 border border-black/5">
          σmédio = <strong>{qmed?.toFixed(1)} kPa</strong>
        </span>
        <span
          className="px-2 py-1 rounded border font-bold"
          style={{ color: ratioColor, borderColor: ratioColor + "40" }}
        >
          η = {pressureRatio.toFixed(3)}
        </span>
      </div>
    </div>
  );
}
