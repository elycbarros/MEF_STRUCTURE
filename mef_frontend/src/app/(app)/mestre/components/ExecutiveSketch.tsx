"use client";

import React from 'react';

interface Coord {
  x: number;
  y: number;
}

interface RebarGeo {
  label: string;
  phi: number;
  count: number;
  coords: Coord[];
  total_length_m: number;
}

interface ExecutiveSketchProps {
  geometry: {
    b_cm: number;
    h_cm: number;
    L_m: number;
  };
  rebar: {
    n1: RebarGeo;
    n2: RebarGeo;
  };
}

export function ExecutiveSketch({ geometry, rebar }: ExecutiveSketchProps) {
  const { L_m, h_cm } = geometry;
  const h_m = h_cm / 100;
  
  // Escalonamento para o SVG
  const width = 800;
  const height = 200;
  const margin = 40;
  
  const scaleX = (width - 2 * margin) / L_m;
  const scaleY = (height - 2 * margin) / h_m;
  
  const mapX = (x: number) => margin + x * scaleX;
  const mapY = (y: number) => height - margin - y * scaleY;

  const renderPath = (coords: Coord[]) => {
    return coords.map((c, i) => `${i === 0 ? 'M' : 'L'} ${mapX(c.x)} ${mapY(c.y)}`).join(' ');
  };

  return (
    <div className="w-full bg-slate-900 p-6 rounded-xl border border-slate-800 overflow-hidden shadow-2xl relative">
      <div className="absolute top-4 left-6 flex items-center gap-2">
        <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
        <span className="text-[10px] font-mono text-slate-400 tracking-widest uppercase">Elevação Executiva - Viga</span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto mt-4">
        {/* Concreto */}
        <rect 
          x={mapX(0)} 
          y={mapY(h_m)} 
          width={L_m * scaleX} 
          height={h_m * scaleY} 
          fill="rgba(255,255,255,0.05)" 
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="1"
          strokeDasharray="4 2"
        />

        {/* Linhas de Cota */}
        <line x1={mapX(0)} y1={height - 15} x2={mapX(L_m)} y2={height - 15} stroke="#475569" strokeWidth="1" />
        <text x={mapX(L_m/2)} y={height - 5} fill="#94a3b8" fontSize="10" textAnchor="middle">L = {L_m.toFixed(2)} m</text>

        {/* Armadura Inferior N1 */}
        <path 
          d={renderPath(rebar.n1.coords)} 
          fill="none" 
          stroke="#f97316" 
          strokeWidth="2.5" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
        />
        <text x={mapX(L_m/2)} y={mapY(0) + 15} fill="#f97316" fontSize="10" fontWeight="bold" textAnchor="middle">
          {rebar.n1.label}: {rebar.n1.count} Φ {rebar.n1.phi.toFixed(1)} - L={rebar.n1.total_length_m.toFixed(2)}m
        </text>

        {/* Armadura Superior N2 */}
        <path 
          d={renderPath(rebar.n2.coords)} 
          fill="none" 
          stroke="#3b82f6" 
          strokeWidth="2.5" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
        />
        <text x={mapX(L_m/2)} y={mapY(h_m) - 10} fill="#3b82f6" fontSize="10" fontWeight="bold" textAnchor="middle">
          {rebar.n2.label}: {rebar.n2.count} Φ {rebar.n2.phi.toFixed(1)} - L={rebar.n2.total_length_m.toFixed(2)}m
        </text>
      </svg>
      
      <div className="mt-4 grid grid-cols-2 gap-4">
         <div className="text-[10px] font-mono text-slate-500 border-l-2 border-orange-500 pl-2">
            DETALHAMENTO N1: Bitola calculada para ELU. Ancoragem com ganchos de 15cm.
         </div>
         <div className="text-[10px] font-mono text-slate-500 border-l-2 border-blue-500 pl-2">
            DETALHAMENTO N2: Porta-estribos calculada para montagem.
         </div>
      </div>
    </div>
  );
}
