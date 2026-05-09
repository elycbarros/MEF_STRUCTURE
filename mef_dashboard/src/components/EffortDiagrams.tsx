"use client";

import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { cn, formatNumberBR } from "@/lib/utils";

interface ForcePoint {
  x: number;
  moment: number;
  shear: number;
}

interface EffortDiagramsProps {
  memberId: number;
  data: ForcePoint[];
  type: "moment" | "shear";
  unit: string;
  title?: string;
  variant?: "dark" | "light";
  comparisonData?: ForcePoint[];
  comparisonLabel?: string;
}

const width = 400;
const height = 150;
const padding = 22;
const axisY = height / 2;

function valueOf(point: ForcePoint, type: "moment" | "shear") {
  return type === "moment" ? point.moment : point.shear;
}

export default function EffortDiagrams({ memberId, data, type, unit, title, variant = "dark", comparisonData, comparisonLabel }: EffortDiagramsProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const diagram = useMemo(() => {
    if (!data || data.length === 0) {
      return { areaPath: "", linePath: "", compLinePath: "", points: [], maxIndex: -1, maxVal: 1, xMax: 1 };
    }

    const combinedData = comparisonData ? [...data, ...comparisonData] : data;
    const xMax = Math.max(...combinedData.map((point) => point.x), 1e-9);
    const maxVal = Math.max(...combinedData.map((point) => Math.abs(valueOf(point, type))), 1e-9);
    
    const xScale = (width - 2 * padding) / xMax;
    const yScale = (height / 2 - padding) / maxVal;

    const screenPoints = data.map((point) => {
      const val = valueOf(point, type);
      return {
        x: padding + point.x * xScale,
        y: axisY - val * yScale,
        val,
        source: point,
      };
    });

    const pathPoints = screenPoints.map((point) => `${point.x},${point.y}`);
    const maxIndex = data.reduce((best, point, index) => (
      Math.abs(valueOf(point, type)) > Math.abs(valueOf(data[best], type)) ? index : best
    ), 0);

    const firstX = screenPoints[0].x;
    const lastX = screenPoints[screenPoints.length - 1].x;

    let compLinePath = "";
    if (comparisonData && comparisonData.length > 0) {
      const compPoints = comparisonData.map((point) => {
        const val = valueOf(point, type);
        return `${padding + point.x * xScale},${axisY - val * yScale}`;
      });
      compLinePath = `M ${compPoints.join(" L ")}`;
    }

    return {
      areaPath: `M ${firstX},${axisY} L ${pathPoints.join(" L ")} L ${lastX},${axisY} Z`,
      linePath: `M ${pathPoints.join(" L ")}`,
      compLinePath,
      points: screenPoints,
      maxIndex,
      maxVal,
      xMax,
    };
  }, [data, comparisonData, type]);

  const selected = diagram.points[selectedIndex ?? diagram.maxIndex];
  const maxPoint = diagram.points[diagram.maxIndex];
  const isLight = variant === "light";
  const color = type === "moment" ? "#2563eb" : "#059669";
  const fill = type === "moment" ? "rgba(37,99,235,0.16)" : "rgba(5,150,105,0.16)";
  const resolvedTitle = title ?? (type === "moment" ? "Diagrama de Momentos Fletores" : "Diagrama de Esforços Cortantes");

  const updateSelection = (clientX: number, rect: DOMRect) => {
    if (!data?.length) return;
    const relative = Math.min(Math.max((clientX - rect.left) / rect.width, 0), 1);
    const xSvg = relative * width;
    const nearest = diagram.points.reduce((best, point, index) => (
      Math.abs(point.x - xSvg) < Math.abs(diagram.points[best].x - xSvg) ? index : best
    ), 0);
    setSelectedIndex(nearest);
  };

  const handlePointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    updateSelection(event.clientX, event.currentTarget.getBoundingClientRect());
  };

  const handlePointerLeave = () => setSelectedIndex(null);

  return (
    <div className={cn(
      "rounded-[2.5rem] border p-8 shadow-2xl transition-all duration-500",
      isLight 
        ? "border-slate-200 bg-white" 
        : "border-slate-200 bg-slate-50/80 backdrop-blur-2xl shadow-blue-900/5 hover:border-blue-500/30",
    )}>
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className={cn("text-sm font-bold uppercase tracking-widest", isLight ? "text-slate-950" : "text-slate-900")}>{resolvedTitle}</h3>
          <p className={cn("mt-1 text-[10px] font-semibold", isLight ? "text-slate-500" : "text-slate-500")}>Arraste o cursor para ler uma seção.</p>
        </div>
        <span className={cn("text-[10px] font-mono", isLight ? "text-slate-500" : "text-slate-500")}>Membro #{memberId} ({unit})</span>
      </div>

      {selected && (
        <div className={cn(
          "mb-4 grid grid-cols-2 gap-4 rounded-2xl border px-5 py-3 text-xs",
          isLight ? "border-slate-200 bg-slate-50 text-slate-700" : "border-slate-200 bg-white/80 text-slate-900",
        )}>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest opacity-40">Seção x</p>
            <p className="font-black font-mono text-sm">{formatNumberBR(selected.source.x)} m</p>
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest opacity-40">{type === "moment" ? "M(x)" : "V(x)"}</p>
            <p className="font-black font-mono text-sm" style={{ color }}>{formatNumberBR(selected.val)} {unit}</p>
          </div>
        </div>
      )}

      <div className="relative h-[150px] w-full flex items-center justify-center">
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 400 150"
          preserveAspectRatio="none"
          onPointerMove={handlePointerMove}
          onPointerLeave={handlePointerLeave}
          className="touch-none cursor-crosshair"
        >
          <line x1={padding} y1={axisY} x2={width - padding} y2={axisY} stroke={isLight ? "rgba(15,23,42,0.16)" : "rgba(255,255,255,0.12)"} strokeWidth="1" />

          <motion.path
            initial={{ opacity: 0, pathLength: 0 }}
            animate={{ opacity: 1, pathLength: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            d={diagram.areaPath}
            stroke={color}
            fill={fill}
            strokeWidth="2"
            fillOpacity="0.2"
          />

          <path d={diagram.linePath} fill="none" stroke={color} strokeWidth="2.5" vectorEffect="non-scaling-stroke" />

          {diagram.compLinePath && (
            <path 
              d={diagram.compLinePath} 
              fill="none" 
              stroke={isLight ? "rgba(100,116,139,0.5)" : "rgba(255,255,255,0.4)"} 
              strokeWidth="1.5" 
              strokeDasharray="4 4" 
              vectorEffect="non-scaling-stroke" 
            />
          )}

          {maxPoint && (
            <>
              <circle cx={maxPoint.x} cy={maxPoint.y} r="4" fill={color} />
              <line x1={maxPoint.x} y1="18" x2={maxPoint.x} y2="132" stroke={color} strokeDasharray="3 3" strokeOpacity="0.55" vectorEffect="non-scaling-stroke" />
            </>
          )}

          {selected && (
            <>
              <line x1={selected.x} y1="12" x2={selected.x} y2="138" stroke={isLight ? "rgba(15,23,42,0.45)" : "rgba(255,255,255,0.55)"} strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
              <circle cx={selected.x} cy={selected.y} r="5" fill={isLight ? "#fff" : "#0f172a"} stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
            </>
          )}

          {data.length > 0 && (
            <>
              <text x={padding} y={axisY + (type === "moment" ? -10 : 20)} fill={isLight ? "rgba(15,23,42,0.55)" : "rgba(255,255,255,0.45)"} fontSize="10" textAnchor="start">
                {formatNumberBR(valueOf(data[0], type), 1)}
              </text>
              <text x={width - padding} y={axisY + (type === "moment" ? -10 : 20)} fill={isLight ? "rgba(15,23,42,0.55)" : "rgba(255,255,255,0.45)"} fontSize="10" textAnchor="end">
                {formatNumberBR(valueOf(data[data.length - 1], type), 1)}
              </text>
            </>
          )}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap gap-4">
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }}></div>
           <span className={cn("text-[10px]", isLight ? "text-slate-600" : "text-slate-700")}>Esforço solicitante</span>
        </div>
        <div className="flex items-center gap-2">
           <div className={cn("w-2 h-0.5", isLight ? "bg-slate-300" : "bg-white/20")}></div>
           <span className={cn("text-[10px]", isLight ? "text-slate-600" : "text-slate-700")}>Linha de eixo</span>
        </div>
        {comparisonLabel && diagram.compLinePath && (
          <div className="flex items-center gap-2">
            <div className={cn("w-3 h-0.5 border-t border-dashed", isLight ? "border-slate-400" : "border-white/40")}></div>
            <span className={cn("text-[10px]", isLight ? "text-slate-600" : "text-slate-700")}>{comparisonLabel}</span>
          </div>
        )}
        {maxPoint && (
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full border-2" style={{ borderColor: color }} />
            <span className={cn("text-[10px]", isLight ? "text-slate-600" : "text-slate-700")}>
              Máx: {formatNumberBR(maxPoint.val)} {unit} em x={formatNumberBR(maxPoint.source.x)} m
            </span>
          </div>
        )}
        <div className={cn("ml-auto text-[10px] font-mono", isLight ? "text-slate-600" : "text-slate-900/35")}>
          {data.length} seções
        </div>
      </div>
    </div>
  );
}
