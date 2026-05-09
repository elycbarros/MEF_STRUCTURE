"use client";

import React from "react";
import { Plus, Trash2, Maximize } from "lucide-react";

interface SupportLocationSectionProps {
  pillars: any[];
  addPillar: () => void;
  removePillar: (index: number) => void;
  updatePillar: (index: number, key: string, value: any) => void;
  restoreSamplePillars: () => void;
  lineSupports: any[];
  addLineSupport: () => void;
  removeLineSupport: (index: number) => void;
  updateLineSupport: (index: number, key: string, value: any) => void;
  setLineSupports?: (ls: any[]) => void;
  holes?: any[];
  areaLoads?: any[];
  updateAreaLoad?: (index: number, key: string, value: any) => void;
  systemType: "radier" | "laje";
  params: any;
  slabType?: string;
}

function SupportPreview({ 
  pillars, 
  lineSupports, 
  Lx, 
  Ly,
  holes = [],
  areaLoads = [],
  updatePillar,
  updateLineSupport,
  updateAreaLoad
}: { 
  pillars: any[], 
  lineSupports: any[], 
  Lx: number, 
  Ly: number,
  holes?: any[],
  areaLoads?: any[],
  updatePillar: (index: number, key: string, value: any) => void,
  updateLineSupport?: (index: number, key: string, value: any) => void,
  updateAreaLoad?: (index: number, key: string, value: any) => void
}) {
  const [draggingPillarIndex, setDraggingPillarIndex] = React.useState<number | null>(null);
  const [draggingLineIndex, setDraggingLineIndex] = React.useState<{index: number, point: 'start' | 'end'} | null>(null);
  const [draggingAreaIndex, setDraggingAreaIndex] = React.useState<number | null>(null);
  const [dragOffset, setDragOffset] = React.useState({ x: 0, y: 0 });
  const svgRef = React.useRef<SVGSVGElement>(null);

  const width = 600;
  const height = 400;
  const padding = 40;

  const scale = Math.min((width - 2 * padding) / Lx, (height - 2 * padding) / Ly);
  const offsetX = (width - Lx * scale) / 2;
  const offsetY = (height - Ly * scale) / 2;

  const toX = (x: number) => offsetX + x * scale;
  const toY = (y: number) => height - (offsetY + y * scale);
  
  const fromX = (svgX: number) => (svgX - offsetX) / scale;
  const fromY = (svgY: number) => (height - svgY - offsetY) / scale;

  const handleMouseMove = (e: React.MouseEvent) => {
    if ((draggingPillarIndex === null && draggingLineIndex === null && draggingAreaIndex === null) || !svgRef.current) return;

    const svg = svgRef.current;
    const CTM = svg.getScreenCTM();
    if (!CTM) return;

    const mouseX = (e.clientX - CTM.e) / CTM.a;
    const mouseY = (e.clientY - CTM.f) / CTM.d;

    const SNAP_DIST = 0.5; // 50cm magnetic snap zone
    
    let rawX = fromX(mouseX);
    let rawY = fromY(mouseY);
    
    let newX = Math.max(0, Math.min(Lx, rawX));
    let newY = Math.max(0, Math.min(Ly, rawY));
    
    if (draggingPillarIndex !== null) {
      const p = pillars[draggingPillarIndex];
      const bx = Number(p.bx || 0.4);
      const by = Number(p.by || 0.4);

      // Smart Boundary Snap (considering pillar faces)
      if (Math.abs(rawX - 0) < SNAP_DIST || Math.abs(rawX - bx/2) < SNAP_DIST/2) newX = bx / 2;
      if (Math.abs(rawX - Lx) < SNAP_DIST || Math.abs(rawX - (Lx - bx/2)) < SNAP_DIST/2) newX = Lx - bx / 2;
      if (Math.abs(rawY - 0) < SNAP_DIST || Math.abs(rawY - by/2) < SNAP_DIST/2) newY = by / 2;
      if (Math.abs(rawY - Ly) < SNAP_DIST || Math.abs(rawY - (Ly - by/2)) < SNAP_DIST/2) newY = Ly - by / 2;

      updatePillar(draggingPillarIndex, "x", newX.toFixed(2));
      updatePillar(draggingPillarIndex, "y", newY.toFixed(2));
    } else if (draggingLineIndex !== null && updateLineSupport) {
      // Magnetic Snap Logic for Lines (center snap is fine)
      if (Math.abs(newX - 0) < SNAP_DIST) newX = 0;
      if (Math.abs(newX - Lx) < SNAP_DIST) newX = Lx;
      if (Math.abs(newY - 0) < SNAP_DIST) newY = 0;
      if (Math.abs(newY - Ly) < SNAP_DIST) newY = Ly;

      const { index, point } = draggingLineIndex;
      if (point === 'start') {
        updateLineSupport(index, "x1", newX.toFixed(2));
        updateLineSupport(index, "y1", newY.toFixed(2));
      } else {
        updateLineSupport(index, "x2", newX.toFixed(2));
        updateLineSupport(index, "y2", newY.toFixed(2));
      }
    } else if (draggingAreaIndex !== null && updateAreaLoad) {
      const load = areaLoads[draggingAreaIndex];
      const w = Number(load.x_max) - Number(load.x_min);
      const h = Number(load.y_max) - Number(load.y_min);
      
      let nx1 = rawX - dragOffset.x;
      let ny1 = rawY - dragOffset.y;
      
      // Keep within boundaries
      nx1 = Math.max(0, Math.min(Lx - w, nx1));
      ny1 = Math.max(0, Math.min(Ly - h, ny1));
      
      updateAreaLoad(draggingAreaIndex, "x_min", nx1.toFixed(2));
      updateAreaLoad(draggingAreaIndex, "x_max", (nx1 + w).toFixed(2));
      updateAreaLoad(draggingAreaIndex, "y_min", ny1.toFixed(2));
      updateAreaLoad(draggingAreaIndex, "y_max", (ny1 + h).toFixed(2));
    }
  };

  const handleMouseUp = () => {
    setDraggingPillarIndex(null);
    setDraggingLineIndex(null);
    setDraggingAreaIndex(null);
  };

  const handleAreaStartDrag = (e: React.MouseEvent, index: number) => {
    if (!svgRef.current) return;
    const svg = svgRef.current;
    const CTM = svg.getScreenCTM();
    if (!CTM) return;
    const mouseX = (e.clientX - CTM.e) / CTM.a;
    const mouseY = (e.clientY - CTM.f) / CTM.d;
    const x = fromX(mouseX);
    const y = fromY(mouseY);
    
    const load = areaLoads[index];
    setDragOffset({
      x: x - Number(load.x_min),
      y: y - Number(load.y_min)
    });
    setDraggingAreaIndex(index);
  };

  return (
    <div className="rounded-2xl border border-[#e3e8f2] bg-white p-4 overflow-hidden select-none">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs font-black uppercase tracking-widest text-[#667085]">Preview Interativo (Vista em Planta)</p>
          <p className="text-[10px] text-slate-600 font-bold mt-0.5 italic">Dica: Arraste os pilares e as extremidades das vigas para ajustar a posição.</p>
        </div>
        <div className="flex gap-4 text-[10px] font-bold text-[#8a9ab0]">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-sm bg-[#2563eb]"></div>
            <span>Pilar</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-0.5 w-3 bg-red-500"></div>
            <span>Viga</span>
          </div>
        </div>
      </div>
      <div 
        className="relative aspect-[3/2] w-full bg-[#f8fafc] rounded-xl border border-dashed border-[#d1d9e6] flex items-center justify-center cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg 
          ref={svgRef}
          viewBox={`0 0 ${width} ${height}`} 
          className="w-full h-full"
        >
          {/* Reference Grid (1x1m) */}
          <g>
            {Array.from({ length: Math.floor(Lx) + 1 }).map((_, i) => (
              <line
                key={`grid-x-${i}`}
                x1={toX(i)}
                y1={offsetY}
                x2={toX(i)}
                y2={offsetY + Ly * scale}
                stroke="#e2e8f0"
                strokeWidth="0.5"
                strokeDasharray="2 2"
              />
            ))}
            {Array.from({ length: Math.floor(Ly) + 1 }).map((_, i) => (
              <line
                key={`grid-y-${i}`}
                x1={offsetX}
                y1={toY(i)}
                x2={offsetX + Lx * scale}
                y2={toY(i)}
                stroke="#e2e8f0"
                strokeWidth="0.5"
                strokeDasharray="2 2"
              />
            ))}
          </g>

          {/* Slab Boundary */}
          <rect
            x={offsetX}
            y={offsetY}
            width={Lx * scale}
            height={Ly * scale}
            fill="none"
            stroke="#94a3b8"
            strokeWidth="1.5"
          />

          {/* Furos e Aberturas */}
          {holes.map((hole, i) => {
            const xmin = Number(hole.x_min || 0);
            const xmax = Number(hole.x_max || 0);
            const ymin = Number(hole.y_min || 0);
            const ymax = Number(hole.y_max || 0);
            const hw = (xmax - xmin) * scale;
            const hh = (ymax - ymin) * scale;
            if (hw <= 0 || hh <= 0) return null;
            return (
              <g key={`hole-${i}`}>
                <rect
                  x={toX(xmin)}
                  y={toY(ymax)}
                  width={hw}
                  height={hh}
                  fill="white"
                  stroke="#cbd5e1"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                />
                <text
                  x={toX(xmin) + hw / 2}
                  y={toY(ymax) + hh / 2}
                  textAnchor="middle"
                  alignmentBaseline="middle"
                  className="text-[10px] font-bold fill-[#94a3b8] select-none"
                >
                  Furo {i + 1}
                </text>
              </g>
            );
          })}
          
          {/* Line Supports (Beams) */}
          {lineSupports.map((ls, i) => {
            const x1 = Number(ls.x1);
            const y1 = Number(ls.y1);
            const x2 = Number(ls.x2);
            const y2 = Number(ls.y2);
            return (
              <g key={`ls-${i}`}>
                <line
                  x1={toX(x1)}
                  y1={toY(y1)}
                  x2={toX(x2)}
                  y2={toY(y2)}
                  stroke="#ef4444"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
                <circle 
                  cx={toX(x1)} 
                  cy={toY(y1)} 
                  r={8} 
                  fill="#ef4444" 
                  className="cursor-grab active:cursor-grabbing opacity-30 hover:opacity-100"
                  onMouseDown={() => setDraggingLineIndex({index: i, point: 'start'})}
                />
                <circle 
                  cx={toX(x2)} 
                  cy={toY(y2)} 
                  r={8} 
                  fill="#ef4444" 
                  className="cursor-grab active:cursor-grabbing opacity-30 hover:opacity-100"
                  onMouseDown={() => setDraggingLineIndex({index: i, point: 'end'})}
                />
                <text
                  x={(toX(x1) + toX(x2)) / 2}
                  y={(toY(y1) + toY(y2)) / 2 - 5}
                  textAnchor="middle"
                  className="text-[10px] font-black fill-red-600 select-none"
                >
                  {ls.id}
                </text>
              </g>
            );
          })}

          {/* Cargas de Área */}
          {areaLoads.map((load, i) => {
            const xmin = Number(load.x_min || 0);
            const xmax = Number(load.x_max || 0);
            const ymin = Number(load.y_min || 0);
            const ymax = Number(load.y_max || 0);
            const lw = (xmax - xmin) * scale;
            const lh = (ymax - ymin) * scale;
            if (lw <= 0 || lh <= 0) return null;
            return (
              <g key={`load-${i}`}>
                <rect
                  x={toX(xmin)}
                  y={toY(ymax)}
                  width={lw}
                  height={lh}
                  fill="rgba(99, 102, 241, 0.15)"
                  stroke="#6366f1"
                  strokeWidth="1.5"
                  strokeDasharray="2 2"
                  className="cursor-grab active:cursor-grabbing hover:fill-[rgba(99,102,241,0.25)] transition-colors"
                  onMouseDown={(e) => handleAreaStartDrag(e, i)}
                />
                <text
                  x={toX(xmin) + lw / 2}
                  y={toY(ymax) + lh / 2}
                  textAnchor="middle"
                  alignmentBaseline="middle"
                  className="text-[9px] font-black fill-[#4f46e5] select-none"
                >
                  q = {load.q_kN} kN/m²
                </text>
              </g>
            );
          })}

          {/* Pillars */}
          {pillars.map((p, i) => {
            const px = Number(p.x);
            const py = Number(p.y);
            const bx = Number(p.bx || 0.4) * scale;
            const by = Number(p.by || 0.4) * scale;
            
            const isOutside = px < 0 || px > Lx || py < 0 || py > Ly;
            const isDragging = draggingPillarIndex === i;
            
            return (
              <g 
                key={`p-${i}`}
                onMouseDown={() => setDraggingPillarIndex(i)}
                className="cursor-grab active:cursor-grabbing"
              >
                <rect
                  x={toX(px) - bx / 2}
                  y={toY(py) - by / 2}
                  width={bx}
                  height={by}
                  fill={isOutside ? "#ef4444" : "#2563eb"}
                  className={`opacity-90 ${isDragging ? "stroke-2 stroke-yellow-400" : ""}`}
                />
                <text
                  x={toX(px)}
                  y={toY(py) - by / 2 - 5}
                  textAnchor="middle"
                  className={`text-[10px] font-black ${isOutside ? "fill-red-600" : "fill-[#1f2937]"} select-none`}
                >
                  {p.id} {isOutside ? "(FORA)" : ""}
                </text>
              </g>
            );
          })}

          {/* Dimensions */}
          <text x={offsetX + (Lx * scale) / 2} y={offsetY - 10} textAnchor="middle" className="text-[10px] fill-[#64748b] font-bold select-none">
            Lx = {Lx.toFixed(2)}m
          </text>
          <text x={offsetX - 10} y={offsetY + (Ly * scale) / 2} textAnchor="middle" transform={`rotate(-90, ${offsetX - 10}, ${offsetY + (Ly * scale) / 2})`} className="text-[10px] fill-[#64748b] font-bold select-none">
            Ly = {Ly.toFixed(2)}m
          </text>
        </svg>
      </div>
    </div>
  );
}

export function SupportLocationSection({
  pillars,
  addPillar,
  removePillar,
  updatePillar,
  restoreSamplePillars,
  lineSupports,
  addLineSupport,
  removeLineSupport,
  updateLineSupport,
  setLineSupports,
  holes = [],
  systemType,
  params,
  areaLoads = [],
  updateAreaLoad,
  slabType = "solid"
}: SupportLocationSectionProps) {
  const Lx = Number(params.Lx || 10);
  const Ly = Number(params.Ly || 10);

  const getSupportWarning = () => {
    if (slabType === "hollow_core") {
      return {
        title: "RESTRIÇÃO DE APOIO: Laje Alveolar",
        text: "NBR 14861: Apoios pontuais (pilares) sem viga de borda são proibidos. A carga deve ser transferida através de capa de concreto armado ou viga de coroamento para evitar fissuração por esforço cortante localizado.",
        color: "text-red-700 bg-red-50 border-red-200"
      };
    }
    if (slabType === "prestressed") {
      return {
        title: "AVISO ESTRUTURAL: Protensão",
        text: "Verificar zona de ancoragem (Ancoragem Ativa/Passiva). Apoios em extremidade exigem armadura de fretagem e verificação de punção (NBR 6118, 19.5.3) devido às altas tensões concentradas.",
        color: "text-orange-700 bg-orange-50 border-orange-200"
      };
    }
    if (slabType === "ribbed") {
      return {
        title: "DETALHAMENTO: Laje Nervurada",
        text: "Apoios pontuais exigem capitéis sólidos (região maciça) de dimensões mínimas 2.5h para garantir a transmissão de esforços de compressão e evitar falha por punção nas nervuras.",
        color: "text-blue-700 bg-blue-50 border-blue-200"
      };
    }
    if (slabType === "trussed") {
      return {
        title: "REQUISITO EXECUTIVO: Laje Treliçada",
        text: "As vigotas devem ter apoio mínimo de 5cm sobre alvenaria ou 3cm sobre vigas de concreto. Apoios indiretos exigem armadura de suspensão transversal adequada.",
        color: "text-emerald-700 bg-emerald-50 border-emerald-200"
      };
    }
    return null;
  };

  const warning = getSupportWarning();

  const margearPillar = (index: number) => {
    const p = pillars[index];
    const bx = Number(p.bx || 0.4);
    const by = Number(p.by || 0.4);
    let nx = Number(p.x);
    let ny = Number(p.y);

    // Se estiver a menos de 1/3 da dimensão da laje de uma borda, cola na face
    if (nx < Lx / 3) nx = bx / 2;
    else if (nx > 2 * Lx / 3) nx = Lx - bx / 2;
    
    if (ny < Ly / 3) ny = by / 2;
    else if (ny > 2 * Ly / 3) ny = Ly - by / 2;

    updatePillar(index, "x", nx.toFixed(2));
    updatePillar(index, "y", ny.toFixed(2));
  };

  return (
    <div className="space-y-8 mt-10 border-t pt-10">
      {warning && (
        <div className={`p-4 rounded-2xl border text-xs font-bold ${warning.color} flex flex-col gap-1 shadow-sm`}>
          <span className="uppercase tracking-widest opacity-80">{warning.title}</span>
          <span className="opacity-90 leading-relaxed">{warning.text}</span>
        </div>
      )}

      <SupportPreview 
        pillars={pillars} 
        lineSupports={lineSupports} 
        Lx={Lx} 
        Ly={Ly} 
        holes={holes}
        areaLoads={areaLoads}
        updatePillar={updatePillar}
        updateLineSupport={updateLineSupport}
        updateAreaLoad={updateAreaLoad}
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-black">Locação de Pilares e Apoios</h2>
          <p className="text-sm font-semibold text-[#667085] mt-1">Defina as coordenadas e dimensões dos apoios discretos.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={restoreSamplePillars}
            className="rounded-xl border border-[#d6deea] bg-white px-3 py-2 text-sm font-bold text-[#4d5360] hover:bg-[#f7f9fc]"
          >
            Restaurar exemplo
          </button>
          <button
            type="button"
            onClick={addPillar}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-3 py-2 text-sm font-bold text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Adicionar pilar
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-[#e3e8f2]">
        <table className="min-w-full text-sm">
          <thead className="bg-[#f7f9fc]">
            <tr className="text-left text-xs font-bold uppercase tracking-wider text-[#667085]">
              <th className="px-3 py-3">ID</th>
              <th className="px-3 py-3">X (m)</th>
              <th className="px-3 py-3">Y (m)</th>
              <th className="px-3 py-3">Fz (kN)</th>
              <th className="px-3 py-3">bx (m)</th>
              <th className="px-3 py-3">by (m)</th>
              <th className="px-3 py-3">Tipo</th>
              <th className="px-3 py-3">Ação</th>
            </tr>
          </thead>
          <tbody>
                {pillars.map((pillar, index) => {
                  const getPillarStatus = () => {
                    const bx = Number(pillar.bx || 0.4);
                    const by = Number(pillar.by || 0.4);
                    if (slabType === "hollow_core") {
                      if (bx < 0.30) return { msg: "Apoio Estreito (mín 30cm p/ alveolar)", color: "text-red-500" };
                    }
                    if (slabType === "prestressed") {
                      if (bx < 0.20 || by < 0.20) return { msg: "Risco de Punção Elevado", color: "text-orange-500" };
                    }
                    return null;
                  };
                  const status = getPillarStatus();

                  return (
                    <tr key={`${pillar.id}-${index}`} className="border-t border-[#edf1f7] group hover:bg-[#f8fafc] transition-colors">
                      <td className="px-3 py-2">
                        <div className="flex flex-col gap-0.5">
                          <input
                            value={pillar.id}
                            onChange={(e) => updatePillar(index, "id", e.target.value)}
                            className="w-16 rounded-lg border border-[#d9dfe9] px-2 py-1 font-bold text-slate-700"
                          />
                          {status && <span className={`text-[9px] font-black uppercase ${status.color}`}>{status.msg}</span>}
                        </div>
                      </td>
                      <td className="px-3 py-2">
                        <input
                          type="text"
                          inputMode="decimal"
                          value={pillar.x}
                          onChange={(e) => updatePillar(index, "x", e.target.value)}
                          className="w-16 rounded-lg border border-[#d9dfe9] px-2 py-1"
                        />
                      </td>
                      <td className="px-3 py-2">
                        <input
                          type="text"
                          inputMode="decimal"
                          value={pillar.y}
                          onChange={(e) => updatePillar(index, "y", e.target.value)}
                          className="w-16 rounded-lg border border-[#d9dfe9] px-2 py-1"
                        />
                      </td>
                <td className="px-3 py-2">
                  <input
                    type="text"
                    inputMode="decimal"
                    value={pillar.fz ?? 0}
                    onChange={(e) => updatePillar(index, "fz", e.target.value)}
                    className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1 font-bold text-[#2563eb]"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    type="text"
                    inputMode="decimal"
                    value={pillar.bx ?? 0.5}
                    onChange={(e) => updatePillar(index, "bx", e.target.value)}
                    className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    type="text"
                    inputMode="decimal"
                    value={pillar.by ?? 0.5}
                    onChange={(e) => updatePillar(index, "by", e.target.value)}
                    className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                  />
                </td>
                <td className="px-3 py-2">
                  <select
                    value={pillar.support_type}
                    onChange={(e) => updatePillar(index, "support_type", e.target.value)}
                    className="w-24 rounded-lg border border-[#d9dfe9] bg-white px-2 py-1 text-xs font-semibold"
                  >
                    <option value="pinned">Rotulado</option>
                    <option value="fixed">Engastado</option>
                    <option value="spring">Elástico</option>
                  </select>
                </td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => margearPillar(index)}
                      title="Margear (Ajustar ao limite)"
                      className="inline-flex items-center gap-1 rounded-lg bg-[#f0f4f8] px-2 py-1 text-xs font-bold text-[#2563eb] hover:bg-[#e1e9f2]"
                    >
                      <Maximize className="h-3 w-3" />
                      Margear
                    </button>
                    <button
                      type="button"
                      onClick={() => removePillar(index)}
                      className="inline-flex items-center gap-1 rounded-lg bg-[#ffecec] px-2 py-1 text-xs font-bold text-[#b42318] hover:bg-[#ffd8d8]"
                    >
                      <Trash2 className="h-3 w-3" />
                      Remover
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        </table>
      </div>

      {systemType === "laje" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-xl font-black">Apoios em Linha (Vigas)</h3>
            <button
              type="button"
              onClick={addLineSupport}
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-3 py-2 text-sm font-bold text-white hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Viga extra (Livre)
            </button>
          </div>
          
          <div className="rounded-xl border border-[#d6deea] bg-[#f8fafc] p-4">
            <p className="text-xs font-bold uppercase tracking-widest text-[#667085] mb-3">Toggles Rápidos de Contorno</p>
            <div className="flex flex-wrap gap-2">
              {[
                { id: "VE", label: "VE (Esquerda)" },
                { id: "VD", label: "VD (Direita)" },
                { id: "HA", label: "HA (Abaixo)" },
                { id: "HC", label: "HC (Acima)" }
              ].map(boundary => {
                const exists = lineSupports.some(ls => ls.id === boundary.id);
                return (
                  <button
                    key={boundary.id}
                    type="button"
                    onClick={() => {
                      if (!setLineSupports) return;
                      if (exists) {
                        setLineSupports(lineSupports.filter(ls => ls.id !== boundary.id));
                      } else {
                        let newLine = null;
                        if (boundary.id === "VE") newLine = { id: "VE", x1: 0, y1: 0, x2: 0, y2: Ly, support_type: "pinned" };
                        if (boundary.id === "VD") newLine = { id: "VD", x1: Lx, y1: 0, x2: Lx, y2: Ly, support_type: "pinned" };
                        if (boundary.id === "HA") newLine = { id: "HA", x1: 0, y1: 0, x2: Lx, y2: 0, support_type: "pinned" };
                        if (boundary.id === "HC") newLine = { id: "HC", x1: 0, y1: Ly, x2: Lx, y2: Ly, support_type: "pinned" };
                        if (newLine) setLineSupports([...lineSupports, newLine]);
                      }
                    }}
                    className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-colors ${
                      exists 
                        ? "bg-blue-600 text-white border border-blue-600 shadow-sm" 
                        : "bg-white text-[#4b5563] border border-[#d1d9e6] hover:bg-[#edf1f7]"
                    }`}
                  >
                    {boundary.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-[#e3e8f2]">
            <table className="min-w-full text-sm">
              <thead className="bg-[#f7f9fc]">
                <tr className="text-left text-xs font-bold uppercase tracking-wider text-[#667085]">
                  <th className="px-3 py-3">ID</th>
                  <th className="px-3 py-3">X1</th>
                  <th className="px-3 py-3">Y1</th>
                  <th className="px-3 py-3">X2</th>
                  <th className="px-3 py-3">Y2</th>
                  <th className="px-3 py-3">Apoio</th>
                  <th className="px-3 py-3">Ação</th>
                </tr>
              </thead>
              <tbody>
                {lineSupports.map((line, index) => (
                  <tr key={`${line.id}-${index}`} className="border-t border-[#edf1f7]">
                    <td className="px-3 py-2">
                      <input
                        value={line.id}
                        onChange={(e) => updateLineSupport(index, "id", e.target.value)}
                        className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        inputMode="decimal"
                        value={line.x1}
                        onChange={(e) => updateLineSupport(index, "x1", e.target.value)}
                        className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        inputMode="decimal"
                        value={line.y1}
                        onChange={(e) => updateLineSupport(index, "y1", e.target.value)}
                        className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        inputMode="decimal"
                        value={line.x2}
                        onChange={(e) => updateLineSupport(index, "x2", e.target.value)}
                        className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="text"
                        inputMode="decimal"
                        value={line.y2}
                        onChange={(e) => updateLineSupport(index, "y2", e.target.value)}
                        className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        value={line.support_type}
                        onChange={(e) => updateLineSupport(index, "support_type", e.target.value)}
                        className="w-24 rounded-lg border border-[#d9dfe9] bg-white px-2 py-1 text-xs font-semibold"
                      >
                        <option value="pinned">Rotulado</option>
                        <option value="fixed">Engastado</option>
                        <option value="spring">Elástico</option>
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        onClick={() => removeLineSupport(index)}
                        className="inline-flex items-center gap-1 rounded-lg bg-[#ffecec] px-2 py-1 text-xs font-bold text-[#b42318] hover:bg-[#ffd8d8]"
                      >
                        <Trash2 className="h-3 w-3" />
                        Remover
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
