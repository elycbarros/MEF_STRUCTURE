"use client";

import React from 'react';

interface Coord {
  x: number;
  y: number;
}

interface SectionSketchProps {
  b_m: number;
  h_m: number;
  rebars: Coord[];
  phi_mm: number;
  label: string;
}

export function SectionSketch({ b_m, h_m, rebars, phi_mm, label }: SectionSketchProps) {
  const width = 300;
  const height = 300;
  const margin = 50;
  
  // Encontrar fator de escala para caber no box 300x300
  const scale = (Math.min(width, height) - 2 * margin) / Math.max(b_m, h_m);
  
  const mapX = (x: number) => margin + x * scale;
  const mapY = (y: number) => height - margin - y * scale;

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-2xl relative flex flex-col items-center">
      <div className="absolute top-4 left-6 flex items-center gap-2">
        <div className="w-2 h-2 bg-blue-500 rounded-full" />
        <span className="text-[9px] font-mono text-slate-400 tracking-widest uppercase">Seção Transversal - {label}</span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto max-w-[200px] mt-6">
        {/* Seção de Concreto */}
        <rect 
          x={mapX(0)} 
          y={mapY(h_m)} 
          width={b_m * scale} 
          height={h_m * scale} 
          fill="rgba(255,255,255,0.03)" 
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="1.5"
        />

        {/* Barras Longitudinais */}
        {rebars.map((r, i) => (
          <circle 
            key={i}
            cx={mapX(r.x)}
            cy={mapY(r.y)}
            r={(phi_mm / 1000) * scale * 2.5} // Multiplicador para visibilidade
            fill="#3b82f6"
            className="drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]"
          />
        ))}

        {/* Estribo (Simbolizado pelo contorno interno) */}
        <rect 
          x={mapX(0.03)} 
          y={mapY(h_m - 0.03)} 
          width={(b_m - 0.06) * scale} 
          height={(h_m - 0.06) * scale} 
          fill="none" 
          stroke="#f97316"
          strokeWidth="1"
          strokeOpacity="0.5"
        />

        {/* Cotas */}
        <text x={mapX(b_m/2)} y={mapY(h_m) - 10} fill="#94a3b8" fontSize="12" textAnchor="middle">{Math.round(b_m*100)} cm</text>
        <text x={mapX(b_m) + 15} y={mapY(h_m/2)} fill="#94a3b8" fontSize="12" textAnchor="start" transform={`rotate(90, ${mapX(b_m)+15}, ${mapY(h_m/2)})`}>{Math.round(h_m*100)} cm</text>
      </svg>

      <div className="mt-4 text-[10px] font-mono text-slate-500 text-center">
        {rebars.length} Φ {phi_mm.toFixed(1)} mm <br/>
        (CA-50)
      </div>
    </div>
  );
}
