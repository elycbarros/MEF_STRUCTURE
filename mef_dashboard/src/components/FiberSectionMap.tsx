"use client";

import React, { useMemo } from "react";
import { formatNumberBR } from "@/lib/utils";

interface Fiber {
  x: number;
  y: number;
  eps: number;
  sig_MPa: number;
}

interface FiberSectionMapProps {
  fibers: Fiber[];
  b: number; // m
  h: number; // m
}

export function FiberSectionMap({ fibers, b, h }: FiberSectionMapProps) {
  const maxStress = useMemo(() => Math.max(0.1, ...fibers.map(f => Math.abs(f.sig_MPa))), [fibers]);
  
  // Agrupar fibras por linhas/colunas para facilitar o desenho
  // Como nx, ny são 20x20 no backend
  const nx = 20;
  const ny = 20;

  const getFillColor = (sig: number) => {
    if (sig === 0) return "#f8fafc";
    // Gradiente de compressão (vermelho/laranja)
    const ratio = Math.abs(sig) / maxStress;
    const lightness = 95 - (ratio * 40); // 95% to 55%
    return `hsl(0, 80%, ${lightness}%)`;
  };

  return (
    <div className="flex flex-col gap-4 p-6 rounded-3xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between">
        <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-600">Mapa de Tensões na Seção (Fibras)</h4>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-red-600" />
            <span className="text-[10px] font-bold text-slate-600">Compressão Máx</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm bg-slate-100 border border-slate-200" />
            <span className="text-[10px] font-bold text-slate-600">Tração/Nula</span>
          </div>
        </div>
      </div>

      <div className="relative aspect-square w-full max-w-[300px] mx-auto">
        <svg viewBox={`0 0 ${nx} ${ny}`} className="w-full h-full rounded-lg border border-slate-100 shadow-inner overflow-hidden">
          {fibers.map((fiber, idx) => {
            // Converter coordenadas x,y (centro zero) para índices de grid 0 a 19
            // x de -b/2 a b/2 -> col de 0 a 19
            const col = Math.round(((fiber.x + b/2) / b) * (nx - 1));
            // y de -h/2 a h/2 -> row de 0 a 19 (invertido para SVG y=0 no topo)
            const row = Math.round(((h/2 - fiber.y) / h) * (ny - 1));
            
            return (
              <rect
                key={idx}
                x={col}
                y={row}
                width="1"
                height="1"
                fill={getFillColor(fiber.sig_MPa)}
                className="hover:stroke-black hover:stroke-[0.1] transition-all cursor-crosshair"
              >
                <title>{`Stress: ${formatNumberBR(fiber.sig_MPa, 2)} MPa\nStrain: ${(fiber.eps * 1000).toFixed(3)} ‰`}</title>
              </rect>
            );
          })}
        </svg>
        
        {/* Eixos */}
        <div className="absolute -left-6 top-1/2 -translate-y-1/2 h-full flex flex-col justify-between text-[8px] font-black text-slate-600 py-1">
          <span>+Y</span>
          <span>0</span>
          <span>-Y</span>
        </div>
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-full flex justify-between text-[8px] font-black text-slate-600 px-1">
          <span>-X</span>
          <span>0</span>
          <span>+X</span>
        </div>
      </div>

      <div className="mt-2 p-4 rounded-2xl bg-slate-50 border border-slate-100">
        <p className="text-[9px] font-black text-slate-600 uppercase mb-2">Parecer da Seção Rigorosa</p>
        <p className="text-xs font-semibold leading-relaxed text-slate-600">
          Visualização de 400 fibras integradas via Newton-Raphson. A zona comprimida segue o diagrama parábola-retângulo da NBR 6118.
        </p>
      </div>
    </div>
  );
}
