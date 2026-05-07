"use client";

import React, { useState } from "react";
import { ArrowUpDown, ChevronRight, Plus, Ruler, Trash2, Layers, Zap, Box, Wind, Search, BookOpen, RotateCcw, Layers3, StretchHorizontal, Scissors, Layout, Cpu } from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import { PedagogicalStepsView } from "./PedagogicalStepsView";
import { MemorialHtmlView } from "./MemorialHtmlView";
import EffortDiagrams from "./EffortDiagrams";
import { ElegantTooltip } from "./ui/ElegantTooltip";
import { FiberSectionMap } from "./FiberSectionMap";

interface SpecialElementsViewProps {
  apiBaseUrl: string;
  isProfessionalMode?: boolean;
  onGoBack?: () => void;
  type?: "viga" | "pilar" | "escada" | "parede" | "footing" | "spt" | "stability" | "reservatorio";
}

function normalizeBeamDiagram(diagrams: any): Array<{ x: number; moment: number; shear: number }> {
  const xs = Array.isArray(diagrams?.x_m) ? diagrams.x_m : [];
  const moments = Array.isArray(diagrams?.M_kNm) ? diagrams.M_kNm : [];
  const shears = Array.isArray(diagrams?.V_kN) ? diagrams.V_kN : [];
  const n = Math.min(xs.length, moments.length, shears.length);

  return Array.from({ length: n }, (_, index) => ({
    x: Number(xs[index]) || 0,
    moment: Number(moments[index]) || 0,
    shear: Number(shears[index]) || 0,
  }));
}

function BeamLoadReactionChart({
  beamParams,
  result,
  useClassical,
}: {
  beamParams: any;
  result: any;
  useClassical: boolean;
}) {
  const totalLength = beamParams.L_left + beamParams.L + beamParams.L_right;
  const distributedLoads = beamParams.distributedLoads.length > 0
    ? beamParams.distributedLoads
    : (beamParams.q > 0 ? [{ id: "Q", x_start: 0, x_end: totalLength, q_start: beamParams.q, q_end: beamParams.q }] : []);
  const selfWeight = beamParams.includeSelfWeight ? beamParams.b * beamParams.h * 25 : 0;
  const shownDistributedLoads = [
    ...distributedLoads,
    ...(selfWeight > 0 ? [{ id: "PP", x_start: 0, x_end: totalLength, q_start: selfWeight, q_end: selfWeight, selfWeight: true }] : []),
  ];
  const reactions = useClassical
    ? (result.classical_reactions || []).map((r: any) => ({ x: Number(r.x) || 0, R: Number(r.R) || 0 }))
    : Object.entries(result.reactions || {}).map(([x, val]: [string, any]) => ({ x: Number(x) || 0, R: Number(val?.V_kN) || 0 }));
  const totalLoad = shownDistributedLoads.reduce((sum, dl: any) => (
    sum + (((Number(dl.q_start) || 0) + (Number(dl.q_end ?? dl.q_start) || 0)) / 2) * Math.max(0, (Number(dl.x_end) || 0) - (Number(dl.x_start) || 0))
  ), 0) + beamParams.pointLoads.reduce((sum: number, p: any) => sum + (Number(p.P) || 0), 0);
  const totalReaction = reactions.reduce((sum: number, r: any) => sum + r.R, 0);
  const loadColors = {
    distributed: { stroke: "#2563eb", fill: "#dbeafe", label: "#1d4ed8", border: "#bfdbfe" },
    variable: { stroke: "#dc2626", fill: "#fee2e2", label: "#dc2626", border: "#fecaca" },
    selfWeight: { stroke: "#9333ea", fill: "#f3e8ff", label: "#7e22ce", border: "#e9d5ff" },
    point: { stroke: "#f97316", fill: "#ffedd5", label: "#ea580c", border: "#fed7aa" },
  };
  const maxValue = Math.max(
    1,
    ...shownDistributedLoads.map((dl: any) => Math.max(Math.abs(Number(dl.q_start) || 0), Math.abs(Number(dl.q_end ?? dl.q_start) || 0))),
    ...beamParams.pointLoads.map((p: any) => Math.abs(Number(p.P) || 0)),
    ...reactions.map((r: any) => Math.abs(r.R)),
  );
  const scaleX = 820 / Math.max(totalLength, 0.001);
  const beamY = 230;
  const hasPointLoads = beamParams.pointLoads.length > 0;
  const hasVariableLoads = shownDistributedLoads.some((dl: any) => {
    const qStart = Number(dl.q_start) || 0;
    const qEnd = Number(dl.q_end ?? dl.q_start) || 0;
    return !dl.selfWeight && Math.abs(qStart - qEnd) > 0.001;
  });
  const hasUniformLoads = shownDistributedLoads.some((dl: any) => {
    const qStart = Number(dl.q_start) || 0;
    const qEnd = Number(dl.q_end ?? dl.q_start) || 0;
    return !dl.selfWeight && Math.abs(qStart - qEnd) <= 0.001;
  });
  const hasSelfWeightLoad = shownDistributedLoads.some((dl: any) => dl.selfWeight);
  const activeLaneKeys = [
    hasSelfWeightLoad ? "selfWeight" : null,
    hasUniformLoads ? "distributed" : null,
    hasVariableLoads ? "variable" : null,
    hasPointLoads ? "point" : null,
  ].filter(Boolean) as Array<"selfWeight" | "distributed" | "variable" | "point">;
  const compactLaneEndYs = [202, 176, 150, 124];
  const laneEndByType = activeLaneKeys.reduce<Record<string, number>>((acc, key, index) => {
    acc[key] = compactLaneEndYs[index] ?? 112;
    return acc;
  }, {});

  return (
    <div className="rounded-2xl border border-[#e0e7ef] bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-5 w-5 text-[#0071e3]" />
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-800">Cargas Aplicadas e Reações</p>
        </div>
        <div className="text-right">
          <p className="text-[10px] font-black uppercase text-slate-400">ΣCargas / ΣReações</p>
          <p className="text-sm font-black text-slate-900">{formatNumberBR(totalLoad)} / {formatNumberBR(totalReaction)} kN</p>
        </div>
      </div>

      <svg viewBox="0 0 1000 410" className="h-auto w-full overflow-visible" role="img" aria-label="Cargas e reações da viga">
        <defs>
          <marker id="beamLoadArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626" />
          </marker>
          <marker id="beamDistributedArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={loadColors.distributed.stroke} />
          </marker>
          <marker id="beamVariableArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={loadColors.variable.stroke} />
          </marker>
          <marker id="beamSelfWeightArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={loadColors.selfWeight.stroke} />
          </marker>
          <marker id="beamPointArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={loadColors.point.stroke} />
          </marker>
          <marker id="beamReactionArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
          </marker>
        </defs>

        <line x1="90" y1={beamY} x2="910" y2={beamY} stroke="#0f172a" strokeWidth="5" strokeLinecap="round" />
        <line x1={90 + beamParams.L_left * scaleX} y1={beamY - 14} x2={90 + beamParams.L_left * scaleX} y2={beamY + 14} stroke="#94a3b8" strokeWidth="2" />
        <line x1={90 + (beamParams.L_left + beamParams.L) * scaleX} y1={beamY - 14} x2={90 + (beamParams.L_left + beamParams.L) * scaleX} y2={beamY + 14} stroke="#94a3b8" strokeWidth="2" />

        {shownDistributedLoads.map((dl: any, idx: number) => {
          const x1 = 90 + (Number(dl.x_start) || 0) * scaleX;
          const x2 = 90 + (Number(dl.x_end) || 0) * scaleX;
          const qStart = Number(dl.q_start) || 0;
          const qEnd = Number(dl.q_end ?? dl.q_start) || 0;
          const q = Math.max(Math.abs(qStart), Math.abs(qEnd));
          const isVariable = Math.abs(qStart - qEnd) > 0.001;
          const arrowCount = Math.max(3, Math.ceil(((Number(dl.x_end) || 0) - (Number(dl.x_start) || 0)) * 2));
          const labelText = isVariable
            ? `${dl.selfWeight ? "PP" : "q"} ${formatNumberBR(qStart)} -> ${formatNumberBR(qEnd)} kN/m`
            : `${dl.selfWeight ? "PP" : "q"} = ${formatNumberBR(q)} kN/m`;
          const labelX = Math.min(Math.max((x1 + x2) / 2, 170), 830);
          const labelWidth = Math.max(112, labelText.length * 7.4);
          const laneKey = dl.selfWeight ? "selfWeight" : isVariable ? "variable" : "distributed";
          const sameLaneOffset = shownDistributedLoads
            .slice(0, idx)
            .filter((prev: any) => {
              const prevVariable = Math.abs((Number(prev.q_start) || 0) - (Number(prev.q_end ?? prev.q_start) || 0)) > 0.001;
              const prevLane = prev.selfWeight ? "selfWeight" : prevVariable ? "variable" : "distributed";
              return prevLane === laneKey;
            }).length * 14;
          const arrowEndY = (laneEndByType[laneKey] ?? 176) + sameLaneOffset;
          const laneHeight = laneKey === "selfWeight" ? 18 : 30;
          const qScale = laneHeight / Math.max(q, 0.001);
          const yStart = arrowEndY - Math.abs(qStart) * qScale;
          const yEnd = arrowEndY - Math.abs(qEnd) * qScale;
          const color = dl.selfWeight ? loadColors.selfWeight : isVariable ? loadColors.variable : loadColors.distributed;
          const markerId = dl.selfWeight ? "beamSelfWeightArrow" : isVariable ? "beamVariableArrow" : "beamDistributedArrow";
          return (
            <g key={`beam-dl-${dl.id ?? idx}`}>
              <path
                d={`M ${x1} ${arrowEndY} L ${x1} ${yStart} L ${x2} ${yEnd} L ${x2} ${arrowEndY}`}
                fill={isVariable || dl.selfWeight ? color.fill : "none"}
                fillOpacity={isVariable || dl.selfWeight ? 0.55 : 0}
                stroke={color.stroke}
                strokeWidth={dl.selfWeight ? "1.5" : "2"}
              />
              {Array.from({ length: arrowCount }).map((_, arrowIdx) => {
                const x = x1 + (arrowIdx * (x2 - x1)) / Math.max(1, arrowCount - 1);
                const ratio = arrowIdx / Math.max(1, arrowCount - 1);
                const qAtX = Math.abs(qStart + (qEnd - qStart) * ratio);
                const arrowTopY = arrowEndY - qAtX * qScale;
                return <line key={arrowIdx} x1={x} y1={arrowTopY} x2={x} y2={arrowEndY} stroke={color.stroke} strokeWidth={dl.selfWeight ? "1.5" : "2"} markerEnd={`url(#${markerId})`} />;
              })}
              <rect
                x={labelX - labelWidth / 2}
                y={Math.min(yStart, yEnd) - 25}
                width={labelWidth}
                height="20"
                rx="6"
                fill="white"
                stroke={color.border}
              />
              <text x={labelX} y={Math.min(yStart, yEnd) - 11} textAnchor="middle" fontSize="13" fontWeight="900" fill={color.label}>
                {labelText}
              </text>
            </g>
          );
        })}

        {beamParams.pointLoads.map((p: any, idx: number) => {
          const x = 90 + (Number(p.x) || 0) * scaleX;
          const pointX = Number(p.x) || 0;
          const occupiedEndYs = shownDistributedLoads
            .filter((dl: any) => pointX >= (Number(dl.x_start) || 0) - 0.05 && pointX <= (Number(dl.x_end) || 0) + 0.05)
            .map((dl: any) => {
              const qStart = Number(dl.q_start) || 0;
              const qEnd = Number(dl.q_end ?? dl.q_start) || 0;
              const isVariable = Math.abs(qStart - qEnd) > 0.001;
              const laneKey = dl.selfWeight ? "selfWeight" : isVariable ? "variable" : "distributed";
              return laneEndByType[laneKey] ?? 176;
            });
          const freePointLane = compactLaneEndYs.find((laneY) => (
            !occupiedEndYs.some((occupiedY) => Math.abs(occupiedY - laneY) < 22)
          ));
          const pointEndY = (freePointLane ?? laneEndByType.point ?? 124) + idx * 8;
          const pointTopY = Math.max(58, pointEndY - 68);
          const labelY = pointTopY - 10;
          return (
            <g key={`beam-pl-${p.id ?? idx}`}>
              <line x1={x} y1={pointTopY} x2={x} y2={pointEndY} stroke={loadColors.point.stroke} strokeWidth="3" markerEnd="url(#beamPointArrow)" />
              <rect x={x - 58} y={labelY - 14} width="116" height="20" rx="6" fill="white" stroke={loadColors.point.border} />
              <text x={x} y={labelY} textAnchor="middle" fontSize="13" fontWeight="900" fill={loadColors.point.label}>
                P = {formatNumberBR(p.P)} kN
              </text>
            </g>
          );
        })}

        {reactions.map((r: any, idx: number) => {
          const x = 90 + r.x * scaleX;
          const arrowHeight = 38 + (Math.abs(r.R) / maxValue) * 64;
          const isDownward = r.R < 0;
          return (
            <g key={`beam-reaction-${idx}`}>
              <line x1={x} y1={isDownward ? beamY + 18 : 332} x2={x} y2={isDownward ? beamY + 18 + arrowHeight : 332 - arrowHeight} stroke="#059669" strokeWidth="3" markerEnd="url(#beamReactionArrow)" />
              <text x={x} y="370" textAnchor="middle" fontSize="13" fontWeight="900" fill="#059669">
                R{idx + 1}: {formatNumberBR(r.R)} kN
              </text>
            </g>
          );
        })}

        <line x1="90" y1="286" x2="910" y2="286" stroke="#cbd5e1" strokeDasharray="4 4" />
        <text x="90" y="306" textAnchor="start" fontSize="12" fontWeight="900" fill="#64748b">0.00 m</text>
        <text x="910" y="306" textAnchor="end" fontSize="12" fontWeight="900" fill="#64748b">{formatNumberBR(totalLength)} m</text>
        <g fontSize="12" fontWeight="900">
          <circle cx="94" cy="34" r="5" fill={loadColors.distributed.stroke} />
          <text x="106" y="38" fill={loadColors.distributed.label}>Distribuída</text>
          <circle cx="198" cy="34" r="5" fill={loadColors.variable.stroke} />
          <text x="210" y="38" fill={loadColors.variable.label}>Triangular/trapezoidal</text>
          <circle cx="362" cy="34" r="5" fill={loadColors.selfWeight.stroke} />
          <text x="374" y="38" fill={loadColors.selfWeight.label}>Peso próprio</text>
          <circle cx="474" cy="34" r="5" fill={loadColors.point.stroke} />
          <text x="486" y="38" fill={loadColors.point.label}>Pontual</text>
        </g>
        <text x="90" y="397" fontSize="12" fontWeight="900" fill="#059669">Reações para cima | resíduo: {formatNumberBR(totalReaction - totalLoad, 3)} kN</text>
      </svg>
    </div>
  );
}

export function SpecialElementsView({ apiBaseUrl, type }: SpecialElementsViewProps) {
  type SpecialTab = "stair" | "concrete_wall" | "beam" | "column" | "footing" | "spt" | "stability" | "retaining_wall" | "reservoir" | "corbel" | "gerber_tooth" | "deep_beam" | "helical_stairs";
  const resolveInitialTab = (selectedType?: SpecialElementsViewProps["type"]): SpecialTab =>
    selectedType === "parede" ? "concrete_wall" :
    selectedType === "viga" ? "beam" :
    selectedType === "pilar" ? "column" :
    selectedType === "footing" ? "footing" :
    selectedType === "spt" ? "spt" :
    selectedType === "stability" ? "stability" :
    selectedType === "reservatorio" ? "reservoir" :
    "stair";
  const initialTab = resolveInitialTab(type);
  const [activeTab, setActiveTab] = useState<SpecialTab>(initialTab);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [useClassical, setUseClassical] = useState(true);
  const [showComparison, setShowComparison] = useState(false);
  const [showFullMemorial, setShowFullMemorial] = useState(false);

  // Sync with prop if it changes
  React.useEffect(() => {
    if (type) {
      setActiveTab(resolveInitialTab(type));
    }
  }, [type]);

  // Estados dos inputs
  const [stairParams, setStairParams] = useState({ L: 4.0, H: 2.8, width: 1.2, q: 5.0, t: 15, fck: 30 });
  const [wallParams, setWallParams] = useState({ Nd: 500, h: 2.8, t: 0.12, fck: 30 });
  const [beamParams, setBeamParams] = useState({
    L: 6.0,
    b: 0.20,
    h: 0.50,
    q: 20.0,
    fck: 30,
    caa: 2,
    coverCm: 3.0,
    gammaF: 1.4,
    redistributionDelta: 0.90,
    nElements: 40,
    includeSelfWeight: true,
    pointLoads: [] as Array<{ id: string; x: number; P: number }>,
    distributedLoads: [] as Array<{ id: string; x_start: number; x_end: number; q_start: number; q_end: number }>,
    leftSupport: "pinned",
    rightSupport: "pinned",
    L_left: 0.0,
    L_right: 0.0,
    leftK: 10000,
    rightK: 10000,
    asymmetric_offset: 0.0,
  });
  const [colParams, setColParams] = useState({ b: 0.40, h: 0.40, Nd: 1200, Mxd: 40, Myd: 15, L_free: 3.0, fck: 25, caa: 2 });
  const [footingParams, setFootingParams] = useState({ Nd: 800.0, sigma_adm: 250.0, ap: 0.20, bp: 0.40, fck: 25 });
  const [retainingWallParams, setRetainingWallParams] = useState({ h_wall: 4.0, gamma_soil: 18.0, phi_soil: 30.0, weight_wall: 120.0, b_base: 2.5, surcharge: 10.0 });
  const [reservoirParams, setReservoirParams] = useState({ length: 5.0, width: 3.0, depth: 3.0, thick: 0.20, fck: 30 });
  const [corbelParams, setCorbelParams] = useState({ fd_kN: 200, a_dist: 0.25, d_eff: 0.45, fck: 30 });
  const [gerberParams, setGerberParams] = useState({ vd_kN: 150, hd_kN: 30, a_dist: 0.15, d_eff: 0.40, b_width: 0.20, fck: 30 });
  const [deepBeamParams, setDeepBeamParams] = useState({ L: 4.0, h: 3.0, b: 0.20, fck: 30 });
  const [helicalStairParams, setHelicalStairParams] = useState({ radius: 2.5, angle_total_deg: 180, h_step: 0.18, thick: 0.15, q_acid: 3.0 });
  const [sptData, setSptData] = useState([
    { depth_m: 1.0, nspt: 2, soil_type: "Ateu" },
    { depth_m: 2.0, nspt: 5, soil_type: "Silte Argiloso" },
    { depth_m: 3.0, nspt: 12, soil_type: "Areia Compacta" },
  ]);
  const [windParams, setWindParams] = useState({ v0: 30.0, height: 30.0, width_x: 12.0 });

  const calculate = async () => {
    setLoading(true);
    let params: any = {};
    if (activeTab === "stair") params = stairParams;
    else if (activeTab === "concrete_wall") params = wallParams;
    else if (activeTab === "beam") params = beamParams;
    else if (activeTab === "column") params = colParams;
    else if (activeTab === "footing") params = footingParams;
    else if (activeTab === "retaining_wall") params = { ...retainingWallParams, type: "retaining_wall" };
    else if (activeTab === "reservoir") params = { ...reservoirParams, type: "reservoir" };
    else if (activeTab === "corbel") params = { ...corbelParams, type: "corbel" };
    else if (activeTab === "gerber_tooth") params = { ...gerberParams, type: "gerber_tooth" };
    else if (activeTab === "deep_beam") params = { ...deepBeamParams, type: "deep_beam" };
    else if (activeTab === "helical_stairs") params = { ...helicalStairParams, type: "helical_stairs" };

    try {
      const isSpt = activeTab === "spt";
      const isStability = activeTab === "stability";

      let body: any = {};
      let url = `${apiBaseUrl}/calculate/special-elements`;

      if (isSpt) {
        url = `${apiBaseUrl}/calculate/spt`;
        body = { spt_data: sptData };
      } else if (isStability) {
        url = `${apiBaseUrl}/calculate/stability-mestre`;
        body = windParams;
      } else if (activeTab === "column") {
        url = `${apiBaseUrl}/calculate/column`;
        body = {
          ...colParams,
          Nd_kN: colParams.Nd,
          Mxd_kNm: colParams.Mxd,
          Myd_kNm: colParams.Myd,
          n_floors_for_shortening: 10
        };
      } else if (activeTab === "beam") {
        url = `${apiBaseUrl}/calculate/beam`;
        const totalL = beamParams.L_left + beamParams.L + beamParams.L_right;
        const supports = [];
        
        // Mapeamento inteligente de apoios para o solver de elementos finitos
        if (beamParams.leftSupport !== "free") {
          supports.push({ 
            x: beamParams.L_left, 
            type: beamParams.leftSupport === "spring" ? "spring" : (beamParams.leftSupport === "fixed" ? "fixed" : "pinned"),
            k_vertical: beamParams.leftK
          });
        }
        if (beamParams.rightSupport !== "free") {
          supports.push({ 
            x: beamParams.L_left + beamParams.L, 
            type: beamParams.rightSupport === "spring" ? "spring" : (beamParams.rightSupport === "fixed" ? "fixed" : "pinned"),
            k_vertical: beamParams.rightK
          });
        }

        body = {
          L: totalL,
          b: beamParams.b,
          h: beamParams.h,
          fck: beamParams.fck,
          caa: beamParams.caa,
          supports: supports,
          distributed_loads: beamParams.distributedLoads.length > 0 
            ? beamParams.distributedLoads 
            : [{ x_start: 0, x_end: totalL, q_start: beamParams.q, q_end: beamParams.q }],
          point_loads: beamParams.pointLoads,
          n_elements: beamParams.nElements,
          include_self_weight: beamParams.includeSelfWeight,
          gamma_f: beamParams.gammaF,
          redistribution_delta: beamParams.redistributionDelta,
          asymmetric_offset: beamParams.asymmetric_offset
        };
      } else {
        body = { type: activeTab, params };
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      
      // Padronização para o Mestre: alguns retornam {result, pedagogical_steps}
      if (data.pedagogical_steps || data.result) {
         setResult(data);
      } else {
         setResult(data);
      }
    } catch (error) {
      console.error("Erro ao calcular elemento isolado:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr_1fr] gap-6">
        {/* Sidebar de Elementos */}
        {!type && (
          <div className="lg:col-span-1 flex flex-col rounded-3xl border border-[#e0e7ef] bg-white overflow-hidden shadow-sm h-fit">
            <div className="bg-[#f2f4f7] p-4 border-b border-[#e0e7ef]">
              <h3 className="font-black text-sm text-[#4d5360] uppercase tracking-widest">Element</h3>
            </div>
            <div className="flex flex-col">
              {[
                { id: "retaining_wall", label: "Muros", icon: Layers3 },
                { id: "stair", label: "Escadas", icon: Ruler },
                { id: "helical_stairs", label: "Escada Helicoidal", icon: RotateCcw },
                { id: "reservoir", label: "Tanques / Reservatórios", icon: Box },
                { id: "corbel", label: "Consolos", icon: StretchHorizontal },
                { id: "gerber_tooth", label: "Dentes Gerber", icon: Scissors },
                { id: "deep_beam", label: "Vigas Parede", icon: Layout },
                { id: "concrete_wall", label: "Parede de Concreto", icon: Layers },
                { id: "footing", label: "Sapatas", icon: Box },
                { id: "spt", label: "Sondagem SPT", icon: Search },
                { id: "stability", label: "Estabilidade Gamma-Z", icon: Wind },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id as any);
                    setResult(null); // Limpar resultado ao trocar de elemento
                  }}
                  className={cn(
                    "flex items-center gap-3 px-6 py-4 text-sm font-black transition-all border-b border-[#f2f4f7] last:border-0 text-left",
                    activeTab === tab.id 
                      ? "bg-[#0071e3] text-white shadow-inner" 
                      : "text-[#4d5360] hover:bg-[#f9fafb] bg-white"
                  )}
                >
                  <tab.icon className={cn("h-4 w-4", activeTab === tab.id ? "text-white" : "text-[#8a9ab0]")} />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        )}
        {/* Coluna de Inputs */}
        <div className="lg:col-span-1 space-y-4 rounded-3xl border border-[#e0e7ef] bg-white p-6 shadow-sm">
          <h3 className="font-black text-lg text-[#101828]">Parâmetros</h3>
          
          {activeTab === "stair" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-cyan-100 bg-cyan-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-cyan-700">Escada de lance único</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Modelo por metro de largura com peso próprio, reação nos apoios e armadura principal por flexão.
                </p>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Projeção L [m]</label>
                    <input type="number" value={stairParams.L} onChange={(e) => setStairParams({ ...stairParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Desnível H [m]</label>
                    <input type="number" value={stairParams.H} onChange={(e) => setStairParams({ ...stairParams, H: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Largura [m]</label>
                    <input type="number" value={stairParams.width} onChange={(e) => setStairParams({ ...stairParams, width: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Espessura [cm]</label>
                    <input type="number" value={stairParams.t} onChange={(e) => setStairParams({ ...stairParams, t: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Ações e material</p>
                <div>
                  <label className="text-xs font-bold text-[#667085]">Carga adicional q [kN/m²]</label>
                  <input type="number" value={stairParams.q} onChange={(e) => setStairParams({ ...stairParams, q: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div>
                  <ElegantTooltip content="Resistência característica do concreto à compressão (aos 28 dias).">
                    <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                  </ElegantTooltip>
                  <input type="number" value={stairParams.fck} onChange={(e) => setStairParams({ ...stairParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
            </div>
          )}

          {activeTab === "helical_stairs" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-purple-100 bg-purple-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-purple-700">Escada Helicoidal</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Análise 3D de torção e flexão em vigas curvas.
                </p>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-bold text-[#667085]">Raio Médio [m]</label>
                  <input type="number" value={helicalStairParams.radius} onChange={(e) => setHelicalStairParams({ ...helicalStairParams, radius: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">Ângulo Total [graus]</label>
                  <input type="number" value={helicalStairParams.angle_total_deg} onChange={(e) => setHelicalStairParams({ ...helicalStairParams, angle_total_deg: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Espessura [m]</label>
                    <input type="number" step="0.01" value={helicalStairParams.thick} onChange={(e) => setHelicalStairParams({ ...helicalStairParams, thick: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Carga q [kN/m²]</label>
                    <input type="number" value={helicalStairParams.q_acid} onChange={(e) => setHelicalStairParams({ ...helicalStairParams, q_acid: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "retaining_wall" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-orange-100 bg-orange-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-orange-700">Muro de Arrimo</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Verificação de estabilidade (Tombamento e Deslizamento).
                </p>
              </div>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Altura Muro [m]</label>
                    <input type="number" value={retainingWallParams.h_wall} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, h_wall: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Base [m]</label>
                    <input type="number" value={retainingWallParams.b_base} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, b_base: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">γ solo [kN/m³]</label>
                    <input type="number" value={retainingWallParams.gamma_soil} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, gamma_soil: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">φ solo [°]</label>
                    <input type="number" value={retainingWallParams.phi_soil} onChange={(e) => setRetainingWallParams({ ...retainingWallParams, phi_soil: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "reservoir" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-700">Reservatório Retangular</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Estanqueidade e controle de fissuração (w_k).
                </p>
              </div>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Comp. [m]</label>
                    <input type="number" value={reservoirParams.length} onChange={(e) => setReservoirParams({ ...reservoirParams, length: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Larg. [m]</label>
                    <input type="number" value={reservoirParams.width} onChange={(e) => setReservoirParams({ ...reservoirParams, width: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Alt. [m]</label>
                    <input type="number" value={reservoirParams.depth} onChange={(e) => setReservoirParams({ ...reservoirParams, depth: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "corbel" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-yellow-100 bg-yellow-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-yellow-700">Consolo Curto</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Modelo de Biela e Tirante (Strut-and-Tie).
                </p>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-bold text-[#667085]">Carga Fd [kN]</label>
                  <input type="number" value={corbelParams.fd_kN} onChange={(e) => setCorbelParams({ ...corbelParams, fd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Braço a [m]</label>
                    <input type="number" step="0.01" value={corbelParams.a_dist} onChange={(e) => setCorbelParams({ ...corbelParams, a_dist: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Alt. útil d [m]</label>
                    <input type="number" step="0.01" value={corbelParams.d_eff} onChange={(e) => setCorbelParams({ ...corbelParams, d_eff: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "gerber_tooth" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-pink-100 bg-pink-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-pink-700">Dente Gerber</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Armadura de suspensão e tirantes horizontais.
                </p>
              </div>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Vd [kN]</label>
                    <input type="number" value={gerberParams.vd_kN} onChange={(e) => setGerberParams({ ...gerberParams, vd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Hd [kN]</label>
                    <input type="number" value={gerberParams.hd_kN} onChange={(e) => setGerberParams({ ...gerberParams, hd_kN: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "deep_beam" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-indigo-100 bg-indigo-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-indigo-700">Viga Parede</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Ajuste de braço de alavanca (z) para L/h ≤ 2.
                </p>
              </div>
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Vão L [m]</label>
                    <input type="number" value={deepBeamParams.L} onChange={(e) => setDeepBeamParams({ ...deepBeamParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Altura h [m]</label>
                    <input type="number" value={deepBeamParams.h} onChange={(e) => setDeepBeamParams({ ...deepBeamParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "concrete_wall" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-emerald-700">Parede de Concreto</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Dimensionamento de paredes estruturais submetidas a compressão centrada ou pequenos momentos.
                </p>
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria e Carga</p>
                <div>
                  <label className="text-xs font-bold text-[#667085]">Carga Nd [kN/m]</label>
                  <input type="number" value={wallParams.Nd} onChange={(e) => setWallParams({ ...wallParams, Nd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Altura h [m]</label>
                    <input type="number" step="0.1" value={wallParams.h} onChange={(e) => setWallParams({ ...wallParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Espessura t [m]</label>
                    <input type="number" step="0.01" value={wallParams.t} onChange={(e) => setWallParams({ ...wallParams, t: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                  <input type="number" value={wallParams.fck} onChange={(e) => setWallParams({ ...wallParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
            </div>
          )}

          {activeTab === "beam" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-700">Modelo acadêmico</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Defina geometria, ações e apoios para gerar o memorial pedagógico. Suporta vigas bi-apoiadas, engastadas ou em balanço.
                </p>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria</p>
                <div className="grid grid-cols-3 gap-2">
                  <div className="col-span-1">
                    <label className="text-[10px] font-black text-[#667085] uppercase">Balanço Esq. [m]</label>
                    <input type="number" step="0.1" value={beamParams.L_left} onChange={(e) => setBeamParams({ ...beamParams, L_left: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div className="col-span-1">
                    <label className="text-[10px] font-black text-blue-600 uppercase">Vão Central (L) [m]</label>
                    <input type="number" step="0.1" value={beamParams.L} onChange={(e) => setBeamParams({ ...beamParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-blue-200 bg-blue-50/30 p-3 text-sm font-bold shadow-inner" />
                  </div>
                  <div className="col-span-1">
                    <label className="text-[10px] font-black text-[#667085] uppercase">Balanço Dir. [m]</label>
                    <input type="number" step="0.1" value={beamParams.L_right} onChange={(e) => setBeamParams({ ...beamParams, L_right: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <ElegantTooltip content="Largura da seção transversal da viga (dimensão horizontal).">
                      <label className="text-xs font-bold text-[#667085]">Largura (b) [m]</label>
                    </ElegantTooltip>
                    <input type="number" step="0.1" value={beamParams.b} onChange={(e) => setBeamParams({ ...beamParams, b: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <ElegantTooltip content="Altura total da viga (da face superior à face inferior).">
                      <label className="text-xs font-bold text-[#667085]">Altura (h) [m]</label>
                    </ElegantTooltip>
                    <input type="number" step="0.1" value={beamParams.h} onChange={(e) => setBeamParams({ ...beamParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Ações e combinações</p>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        const id = `DL${beamParams.distributedLoads.length + 1}`;
                        setBeamParams({
                          ...beamParams,
                          distributedLoads: [
                            ...beamParams.distributedLoads, 
                            { id, x_start: 0, x_end: beamParams.L_left + beamParams.L + beamParams.L_right, q_start: 20, q_end: 20 }
                          ]
                        });
                      }}
                      className="flex items-center gap-1 text-[10px] font-black text-blue-600 hover:text-blue-700"
                    >
                      <Plus size={12} /> CARGA POR TRECHO
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const id = `DL${beamParams.distributedLoads.length + 1}`;
                        setBeamParams({
                          ...beamParams,
                          distributedLoads: [
                            ...beamParams.distributedLoads,
                            { id, x_start: 0, x_end: beamParams.L_left + beamParams.L + beamParams.L_right, q_start: 0, q_end: 20 }
                          ]
                        });
                      }}
                      className="flex items-center gap-1 text-[10px] font-black text-red-600 hover:text-red-700"
                    >
                      <Plus size={12} /> TRIANGULAR
                    </button>
                  </div>
                </div>

                {beamParams.distributedLoads.length === 0 ? (
                  <div>
                    <ElegantTooltip content="Carga por metro linear em toda a extensão da viga.">
                      <label className="text-xs font-bold text-[#667085]">Carga distribuída qk (Global) [kN/m]</label>
                    </ElegantTooltip>
                    <input 
                      type="number" 
                      step="0.1" 
                      value={beamParams.q} 
                      onChange={(e) => setBeamParams({ ...beamParams, q: Number(e.target.value) })} 
                      className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" 
                    />
                  </div>
                ) : (
                  <div className="space-y-2">
                    {beamParams.distributedLoads.map((dl, idx) => (
                      <div key={dl.id} className="grid grid-cols-12 gap-2 items-end">
                        <div className="col-span-3">
                          <label className="text-[9px] font-bold text-[#667085]">Início [m]</label>
                          <input
                            type="number"
                            step="0.1"
                            value={dl.x_start}
                            onChange={(e) => {
                              const newList = [...beamParams.distributedLoads];
                              newList[idx].x_start = Number(e.target.value);
                              setBeamParams({ ...beamParams, distributedLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-3">
                          <label className="text-[9px] font-bold text-[#667085]">Fim [m]</label>
                          <input
                            type="number"
                            step="0.1"
                            value={dl.x_end}
                            onChange={(e) => {
                              const newList = [...beamParams.distributedLoads];
                              newList[idx].x_end = Number(e.target.value);
                              setBeamParams({ ...beamParams, distributedLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="text-[9px] font-bold text-[#667085]">qi [kN/m]</label>
                          <input
                            type="number"
                            value={dl.q_start}
                            onChange={(e) => {
                              const newList = [...beamParams.distributedLoads];
                              newList[idx].q_start = Number(e.target.value);
                              setBeamParams({ ...beamParams, distributedLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="text-[9px] font-bold text-[#667085]">qf [kN/m]</label>
                          <input
                            type="number"
                            value={dl.q_end}
                            onChange={(e) => {
                              const newList = [...beamParams.distributedLoads];
                              newList[idx].q_end = Number(e.target.value);
                              setBeamParams({ ...beamParams, distributedLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-1 flex justify-center pb-1">
                          <button
                            type="button"
                            onClick={() => {
                              setBeamParams({
                                ...beamParams,
                                distributedLoads: beamParams.distributedLoads.filter((_, i) => i !== idx)
                              });
                            }}
                            className="text-red-500 hover:text-red-700 transition"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <ElegantTooltip content="Coeficiente de ponderação das ações (NBR 6118). Padrão = 1.4.">
                      <label className="text-xs font-bold text-[#667085]">γf</label>
                    </ElegantTooltip>
                    <input type="number" step="0.05" value={beamParams.gammaF} onChange={(e) => setBeamParams({ ...beamParams, gammaF: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <label className="flex items-center gap-3 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-xs font-black text-[#667085]">
                    <input type="checkbox" checked={beamParams.includeSelfWeight} onChange={(e) => setBeamParams({ ...beamParams, includeSelfWeight: e.target.checked })} className="h-4 w-4 accent-black" />
                    Peso próprio
                  </label>
                </div>
              </div>

              <div className="space-y-3">
                <div className="rounded-xl border border-blue-100 bg-blue-50/20 p-3">
                  <p className="text-[10px] font-black text-blue-700 uppercase mb-1">Extensão Total da Viga</p>
                  <p className="text-sm font-black text-slate-800">
                    {(beamParams.L_left + beamParams.L + beamParams.L_right).toFixed(2)} m
                  </p>
                  <p className="text-[9px] font-bold text-slate-500 mt-1">
                    Apoios em x = {beamParams.L_left.toFixed(2)}m e x = {(beamParams.L_left + beamParams.L).toFixed(2)}m
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Cargas Pontuais</p>
                  <button
                    type="button"
                    onClick={() => {
                      const id = `PL${beamParams.pointLoads.length + 1}`;
                      setBeamParams({
                        ...beamParams,
                        pointLoads: [...beamParams.pointLoads, { id, x: beamParams.L_left + beamParams.L / 2, P: 50 }]
                      });
                    }}
                    className="flex items-center gap-1 text-[10px] font-black text-blue-600 hover:text-blue-700"
                  >
                    <Plus size={12} /> ADICIONAR
                  </button>
                </div>

                {beamParams.pointLoads.length === 0 ? (
                  <p className="text-[10px] text-center italic text-[#98a2b3] py-2 border border-dashed rounded-xl">Nenhuma carga pontual</p>
                ) : (
                  <div className="space-y-2">
                    {beamParams.pointLoads.map((pl, idx) => (
                      <div key={pl.id} className="grid grid-cols-7 gap-2 items-end">
                        <div className="col-span-3">
                          <label className="text-[9px] font-bold text-[#667085]">x [m]</label>
                          <input
                            type="number"
                            step="0.1"
                            value={pl.x}
                            onChange={(e) => {
                              const newList = [...beamParams.pointLoads];
                              newList[idx].x = Number(e.target.value);
                              setBeamParams({ ...beamParams, pointLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-3">
                          <label className="text-[9px] font-bold text-[#667085]">P [kN]</label>
                          <input
                            type="number"
                            value={pl.P}
                            onChange={(e) => {
                              const newList = [...beamParams.pointLoads];
                              newList[idx].P = Number(e.target.value);
                              setBeamParams({ ...beamParams, pointLoads: newList });
                            }}
                            className="w-full mt-0.5 rounded-lg border border-[#e0e7ef] bg-[#f9fafb] p-2 text-xs font-bold"
                          />
                        </div>
                        <div className="col-span-1 flex justify-center pb-1">
                          <button
                            type="button"
                            onClick={() => {
                              setBeamParams({
                                ...beamParams,
                                pointLoads: beamParams.pointLoads.filter((_, i) => i !== idx)
                              });
                            }}
                            className="text-red-500 hover:text-red-700 transition"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Materiais e durabilidade</p>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <ElegantTooltip content="Resistência característica do concreto à compressão (aos 28 dias).">
                      <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                    </ElegantTooltip>
                    <input type="number" value={beamParams.fck} onChange={(e) => setBeamParams({ ...beamParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <ElegantTooltip content="Classe de Agressividade Ambiental (1 a 4) conforme NBR 6118.">
                      <label className="text-xs font-bold text-[#667085]">CAA</label>
                    </ElegantTooltip>
                    <input type="number" min={1} max={4} value={beamParams.caa} onChange={(e) => setBeamParams({ ...beamParams, caa: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <ElegantTooltip content="Cobrimento nominal das armaduras para proteção contra corrosão.">
                      <label className="text-xs font-bold text-[#667085]">c [cm]</label>
                    </ElegantTooltip>
                    <input type="number" step="0.5" value={beamParams.coverCm} onChange={(e) => setBeamParams({ ...beamParams, coverCm: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Apoios e análise</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Apoio esquerdo</label>
                    <select value={beamParams.leftSupport} onChange={(e) => setBeamParams({ ...beamParams, leftSupport: e.target.value })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold">
                      <option value="pinned">Apoio Fixo (Rotulado)</option>
                      <option value="fixed">Engaste (Rígido)</option>
                      <option value="roller">Apoio Móvel (Deslizante)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Apoio direito</label>
                    <select value={beamParams.rightSupport} onChange={(e) => setBeamParams({ ...beamParams, rightSupport: e.target.value })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold">
                      <option value="pinned">Apoio Fixo (Rotulado)</option>
                      <option value="fixed">Engaste (Rígido)</option>
                      <option value="roller">Apoio Móvel (Deslizante)</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <ElegantTooltip content="Fator de redução de momentos negativos via ductilidade (0.75 a 1.0).">
                      <label className="text-xs font-bold text-[#667085]">Redistribuição δ</label>
                    </ElegantTooltip>
                    <input type="number" min="0.75" max="1" step="0.05" value={beamParams.redistributionDelta} onChange={(e) => setBeamParams({ ...beamParams, redistributionDelta: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <ElegantTooltip content="Grau de refinamento da malha de Elementos Finitos (discretização).">
                      <label className="text-xs font-bold text-[#667085]">Elementos MEF</label>
                    </ElegantTooltip>
                    <input type="number" min="2" max="500" value={beamParams.nElements} onChange={(e) => setBeamParams({ ...beamParams, nElements: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="pt-2">
                  <ElegantTooltip content="Excentricidade geométrica adicional (e0) devido à assimetria da seção (L, C, etc.).">
                    <label className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Offset Assimétrico (e0) [m]</label>
                  </ElegantTooltip>
                  <input 
                    type="number" 
                    step="0.01" 
                    value={beamParams.asymmetric_offset} 
                    onChange={(e) => setBeamParams({ ...beamParams, asymmetric_offset: Number(e.target.value) })} 
                    className="w-full mt-1 rounded-xl border border-blue-100 bg-blue-50/20 p-3 text-sm font-black text-blue-700 shadow-inner" 
                  />
                  <p className="mt-1 text-[9px] font-bold text-slate-400">Gera momentos torsores adicionais automáticos no motor MEF.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "column" && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-bold text-[#667085]">b [m]</label>
                  <input type="number" value={colParams.b} onChange={(e) => setColParams({ ...colParams, b: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">h [m]</label>
                  <input type="number" value={colParams.h} onChange={(e) => setColParams({ ...colParams, h: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">Carga de Cálculo (Nd) [kN]</label>
                <input type="number" value={colParams.Nd} onChange={(e) => setColParams({ ...colParams, Nd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs font-bold text-[#667085]">Mxd [kNm]</label>
                  <input type="number" value={colParams.Mxd} onChange={(e) => setColParams({ ...colParams, Mxd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">Myd [kNm]</label>
                  <input type="number" value={colParams.Myd} onChange={(e) => setColParams({ ...colParams, Myd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
              <div>
                <label className="text-xs font-bold text-[#667085]">Altura Livre (Lf) [m]</label>
                <input type="number" value={colParams.L_free} onChange={(e) => setColParams({ ...colParams, L_free: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <ElegantTooltip content="Resistência característica do concreto à compressão (aos 28 dias).">
                    <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                  </ElegantTooltip>
                  <input type="number" value={colParams.fck} onChange={(e) => setColParams({ ...colParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">CAA</label>
                  <input type="number" min={1} max={4} value={colParams.caa} onChange={(e) => setColParams({ ...colParams, caa: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
            </div>
          )}

          {activeTab === "footing" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-amber-100 bg-amber-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-amber-700">Sapata isolada rígida</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Dimensionamento de base, rigidez e armadura para sapatas centradas sob carga vertical.
                </p>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Carga e Solo</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Nd [kN]</label>
                    <input type="number" value={footingParams.Nd} onChange={(e) => setFootingParams({ ...footingParams, Nd: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">σ adm [kPa]</label>
                    <input type="number" value={footingParams.sigma_adm} onChange={(e) => setFootingParams({ ...footingParams, sigma_adm: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Pilar e Concreto</p>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">ap [m]</label>
                    <input type="number" value={footingParams.ap} onChange={(e) => setFootingParams({ ...footingParams, ap: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">bp [m]</label>
                    <input type="number" value={footingParams.bp} onChange={(e) => setFootingParams({ ...footingParams, bp: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                  <input type="number" value={footingParams.fck} onChange={(e) => setFootingParams({ ...footingParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
              </div>
            </div>
          )}

          {activeTab === "spt" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-700">Interpretação de Sondagem</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Insira os valores de N_SPT para cada metro para definir a cota de assentamento e tensão admissível.
                </p>
              </div>
              <div className="space-y-2">
                {sptData.map((layer, idx) => (
                  <div key={idx} className="flex gap-2 items-center bg-white p-2 rounded-xl border border-slate-100">
                    <span className="text-[10px] font-black w-8">{layer.depth_m}m</span>
                    <input 
                      type="number" 
                      value={layer.nspt} 
                      onChange={(e) => {
                        const newSpt = [...sptData];
                        newSpt[idx].nspt = Number(e.target.value);
                        setSptData(newSpt);
                      }}
                      className="w-16 rounded-lg border border-[#e0e7ef] p-1 text-xs font-bold text-center" 
                    />
                    <input 
                      type="text" 
                      value={layer.soil_type} 
                      onChange={(e) => {
                        const newSpt = [...sptData];
                        newSpt[idx].soil_type = e.target.value;
                        setSptData(newSpt);
                      }}
                      className="flex-1 rounded-lg border border-[#e0e7ef] p-1 text-xs font-medium" 
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "stability" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-teal-100 bg-teal-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-teal-700">Vento e Estabilidade Global</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Defina os parâmetros do edifício para calcular a pressão do vento e o coeficiente de estabilidade Gamma-Z.
                </p>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-bold text-[#667085]">V0 [m/s]</label>
                  <input type="number" value={windParams.v0} onChange={(e) => setWindParams({ ...windParams, v0: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Altura Total [m]</label>
                    <input type="number" value={windParams.height} onChange={(e) => setWindParams({ ...windParams, height: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Largura X [m]</label>
                    <input type="number" value={windParams.width_x} onChange={(e) => setWindParams({ ...windParams, width_x: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          <button
            onClick={calculate}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-2xl bg-black py-4 font-black text-white hover:bg-[#1d2939] active:scale-95 transition-all disabled:opacity-50"
          >
            {loading ? "Calculando..." : <><Zap size={18} /> Dimensionar</>}
          </button>
          {(activeTab === "spt" || activeTab === "stability") && (
            <button
              type="button"
              onClick={() => setShowFullMemorial(true)}
              disabled={!result?.pedagogical_steps}
              className="w-full flex items-center justify-center gap-2 rounded-2xl border border-amber-200 bg-amber-50 py-3 text-sm font-black text-amber-700 hover:bg-amber-100 active:scale-95 transition-all"
            >
              <BookOpen size={16} />
              Memorial Pedagógico HTML
            </button>
          )}
        </div>

        {/* Coluna de Resultados */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                  <h3 className="font-black text-xl text-[#101828]">Memória de Cálculo</h3>
                  <button 
                    onClick={() => setShowFullMemorial(true)}
                    className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-[10px] font-black uppercase hover:bg-amber-100 transition-all"
                  >
                    <BookOpen size={12} /> Visualizar Memorial Completo
                  </button>
                </div>
                <span className="px-3 py-1 bg-[#f2f4f7] rounded-full text-[10px] font-black uppercase text-[#667085]">NBR 6118</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {activeTab === "beam" && (
                  <>
                    <div className="space-y-6">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="rounded-2xl bg-white p-4 border border-slate-100 shadow-sm">
                          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Mk (+) Máximo</p>
                          <p className="mt-1 text-xl font-black text-slate-900">{formatNumberBR(result.design?.M_max_pos_kNm ?? 0)} <span className="text-[10px] text-slate-400">kNm</span></p>
                          <p className="mt-2 text-[10px] font-bold text-emerald-600">As inf: {formatNumberBR(result.design?.flexure_bottom?.As_cm2 ?? 0)} cm²</p>
                        </div>
                        <div className="rounded-2xl bg-white p-4 border border-slate-100 shadow-sm">
                          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Mk (-) Máximo</p>
                          <p className="mt-1 text-xl font-black text-slate-900">{formatNumberBR(Math.abs(result.design?.M_max_neg_kNm ?? 0))} <span className="text-[10px] text-slate-400">kNm</span></p>
                          <p className="mt-2 text-[10px] font-bold text-blue-600">As sup: {formatNumberBR(result.design?.flexure_top?.As_cm2 ?? 0)} cm²</p>
                        </div>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-slate-900 mb-2">Flecha e Rigidez</p>
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-[10px] font-black uppercase text-slate-400">Flecha MEF</p>
                            <p className="text-lg font-black text-slate-900">{formatNumberBR(result.design?.deflection?.max_mm ?? result.deflection_mm, 2)} <span className="text-[10px]">mm</span></p>
                          </div>
                          <span className={`text-[10px] px-3 py-1 rounded-full font-black ${(result.design?.overall_status ?? result.status) === "ATENDE" || result.status === "OK" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700 border border-rose-200 animate-pulse"}`}>
                            {result.design?.overall_status ?? result.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {activeTab === "beam" && result?.result?.detailing && (
                  <div className="col-span-2 mt-4 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl border border-blue-100 bg-blue-50/30 p-5">
                      <p className="text-[10px] font-black uppercase tracking-widest text-blue-700">Armadura Inferior</p>
                      <p className="mt-2 text-2xl font-black text-slate-800">{result.result.detailing.inf.spec}</p>
                      <p className="mt-1 text-xs font-bold text-blue-600">L_ancoragem = {result.result.detailing.inf.lb_nec} cm</p>
                    </div>
                    <div className="rounded-2xl border border-slate-200 bg-white p-5">
                      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Armadura Superior</p>
                      <p className="mt-2 text-2xl font-black text-slate-800">{result.result.detailing.sup.spec}</p>
                      <p className="mt-1 text-xs font-bold text-slate-600">L_ancoragem = {result.result.detailing.sup.lb_nec} cm</p>
                    </div>
                    <div className="col-span-2 rounded-2xl border border-emerald-100 bg-emerald-50/30 p-4 flex justify-between items-center">
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-emerald-700">Estribos e Decalagem</p>
                        <p className="mt-1 text-sm font-bold text-slate-700">{result.result.detailing.stirrups} | a_l = {result.result.detailing.geometry.al_cm} cm</p>
                      </div>
                      <Box className="text-emerald-600" size={24} />
                    </div>
                  </div>
                )}

                {activeTab === "column" && (
                  <>
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs font-bold text-[#667085] uppercase">Armadura Final (As)</p>
                        <p className="text-3xl font-black text-emerald-600">{formatNumberBR(result.design?.As_final_cm2 ?? result.As_cm2)} <span className="text-sm font-bold text-[#8a9ab0]">cm²</span></p>
                      </div>
                      <div>
                        <p className="text-xs font-bold text-[#667085] uppercase">Índice de Esbeltez (λ)</p>
                        <p className="text-3xl font-black">{formatNumberBR(result.design?.slenderness?.lambda_x ?? result.lambda, 1)}</p>
                      </div>
                    </div>
                    <div className="rounded-2xl bg-[#f9fafb] p-6 space-y-3 border border-[#f2f4f7]">
                      <p className="text-sm font-bold">Status do Pilar</p>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-black ${(result.design?.status ?? result.status) === "OK" ? "bg-emerald-100 text-emerald-700" : "bg-red-600 text-white border border-red-700 animate-pulse shadow-sm"}`}>
                        {result.design?.status ?? result.status}
                      </span>
                      <p className="text-xs text-[#667085]">Pilar verificado com roteiro didático. Se λ {">"} 35, os efeitos locais de 2ª ordem entram na análise.</p>
                    </div>
                    {result.fiber_results?.fibers && (
                      <div className="col-span-2">
                        <FiberSectionMap 
                          fibers={result.fiber_results.fibers} 
                          b={colParams.b} 
                          h={colParams.h} 
                        />
                      </div>
                    )}
                  </>
                )}

                {(activeTab === "stair" || activeTab === "concrete_wall" || activeTab === "footing" || activeTab === "spt" || activeTab === "stability") && (
                   <p className="col-span-2 text-sm font-bold text-[#667085]">Cálculo concluído com sucesso. O resumo abaixo destaca os parâmetros governantes.</p>
                )}
                
                {activeTab === "stair" && (
                   <div className="col-span-2 grid gap-4 md:grid-cols-3">
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Momento Mk</p>
                        <p className="mt-2 text-2xl font-black">{formatNumberBR(result.Mk)} <span className="text-sm text-[#8a9ab0]">kNm/m</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Armadura principal</p>
                        <p className="mt-2 text-2xl font-black text-emerald-600">{formatNumberBR(result.As_cm2_m)} <span className="text-sm text-[#8a9ab0]">cm²/m</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Reação total</p>
                        <p className="mt-2 text-2xl font-black">{formatNumberBR(result.total_reaction_kN)} <span className="text-sm text-[#8a9ab0]">kN</span></p>
                        <span className={`mt-3 inline-flex rounded-full px-2 py-1 text-[10px] font-black ${result.status === "ATENDE" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700 border border-rose-200 animate-pulse"}`}>{result.status}</span>
                      </div>
                   </div>
                )}

                {activeTab === "concrete_wall" && (
                  <div className="col-span-2 space-y-4">
                    <div className="grid gap-4 md:grid-cols-4">
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Esbeltez (λ)</p>
                        <p className="mt-2 text-2xl font-black">{formatNumberBR(result.result?.lambda, 1)}</p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Carga Real</p>
                        <p className="mt-2 text-2xl font-black text-rose-600">{formatNumberBR(result.result?.nd_kN_m)} <span className="text-sm text-[#8a9ab0]">kN/m</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Capacidade (NRd)</p>
                        <p className="mt-2 text-2xl font-black text-emerald-600">{formatNumberBR(result.result?.n_rd_kN_m)} <span className="text-sm text-[#8a9ab0]">kN/m</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Status</p>
                        <p className="mt-2 text-sm font-black">{result.result?.status ?? "OK"}</p>
                      </div>
                    </div>
                    <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-5">
                      <p className="text-sm font-black text-emerald-900">Parecer Técnico da Parede</p>
                      <p className="mt-2 text-xs font-semibold leading-relaxed text-emerald-900">
                        A parede de {formatNumberBR(result.result?.t_wall_m * 100)}cm de espessura possui índice de esbeltez λ={formatNumberBR(result.result?.lambda, 1)}. 
                        {result.result?.lambda > 30 ? " Atenção: Efeitos de segunda ordem são significativos." : " Esbeltez dentro dos limites usuais para paredes estruturais."}
                        A carga solicitante Nd={formatNumberBR(result.result?.nd_kN_m)} kN/m é {result.result?.nd_kN_m <= result.result?.n_rd_kN_m ? "inferior" : "superior"} à capacidade resistente NRd={formatNumberBR(result.result?.n_rd_kN_m)} kN/m.
                      </p>
                    </div>
                  </div>
                )}
                {activeTab === "footing" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                      <p className="text-xs font-bold text-[#667085] uppercase">Dimensões</p>
                      <p className="mt-2 text-2xl font-black">{formatNumberBR(result.result?.a_m)} × {formatNumberBR(result.result?.b_m)} <span className="text-sm text-[#8a9ab0]">m</span></p>
                    </div>
                    <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                      <p className="text-xs font-bold text-[#667085] uppercase">Espessura (h)</p>
                      <p className="mt-2 text-2xl font-black">{formatNumberBR(result.result?.h_m)} <span className="text-sm text-[#8a9ab0]">m</span></p>
                    </div>
                    <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                      <p className="text-xs font-bold text-[#667085] uppercase">Pressão Real</p>
                      <p className="mt-2 text-2xl font-black">{formatNumberBR(result.result?.sigma_real_kPa)} <span className="text-sm text-[#8a9ab0]">kPa</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "retaining_wall" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100">
                      <p className="text-xs font-bold text-teal-700 uppercase">Segurança Tombamento</p>
                      <p className="mt-2 text-3xl font-black text-teal-900">{formatNumberBR(result.result?.fs_tomb, 2)}</p>
                      <p className="text-[10px] font-bold text-teal-600 mt-1">Mínimo: 1.50</p>
                    </div>
                    <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100">
                      <p className="text-xs font-bold text-teal-700 uppercase">Segurança Deslizamento</p>
                      <p className="mt-2 text-3xl font-black text-teal-900">{formatNumberBR(result.result?.fs_desl, 2)}</p>
                      <p className="text-[10px] font-bold text-teal-600 mt-1">Mínimo: 1.50</p>
                    </div>
                  </div>
                )}

                {activeTab === "reservoir" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100">
                      <p className="text-xs font-bold text-blue-700 uppercase">Momento Máximo</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.result?.m_max_kNm, 1)} <span className="text-sm">kNm/m</span></p>
                    </div>
                    <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100">
                      <p className="text-xs font-bold text-blue-700 uppercase">Armadura Base</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.result?.as_base_cm2, 2)} <span className="text-sm">cm²/m</span></p>
                    </div>
                    <div className="rounded-2xl bg-blue-50 p-5 border border-blue-100 text-center">
                      <p className="text-xs font-bold text-blue-700 uppercase">Volume Útil</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.result?.volume_m3, 1)} <span className="text-sm">m³</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "corbel" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-orange-50 p-5 border border-orange-100">
                      <p className="text-xs font-bold text-orange-700 uppercase">Tração no Tirante (Td)</p>
                      <p className="mt-2 text-3xl font-black text-orange-900">{formatNumberBR(result.result?.f_tirante_kN, 1)} <span className="text-sm">kN</span></p>
                    </div>
                    <div className="rounded-2xl bg-orange-50 p-5 border border-orange-100">
                      <p className="text-xs font-bold text-orange-700 uppercase">As Principal</p>
                      <p className="mt-2 text-3xl font-black text-orange-900">{formatNumberBR(result.result?.as_principal_cm2, 2)} <span className="text-sm">cm²</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "gerber_tooth" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-purple-50 p-5 border border-purple-100">
                      <p className="text-xs font-bold text-purple-700 uppercase">As Suspensão</p>
                      <p className="mt-2 text-3xl font-black text-purple-900">{formatNumberBR(result.result?.as_suspensao_cm2, 2)} <span className="text-sm">cm²</span></p>
                    </div>
                    <div className="rounded-2xl bg-purple-50 p-5 border border-purple-100">
                      <p className="text-xs font-bold text-purple-700 uppercase">As Tirante (Ash)</p>
                      <p className="mt-2 text-3xl font-black text-purple-900">{formatNumberBR(result.result?.as_tirante_cm2, 2)} <span className="text-sm">cm²</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "deep_beam" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl bg-slate-50 p-5 border border-slate-200">
                      <p className="text-xs font-bold text-slate-700 uppercase">Braço Alavanca (z)</p>
                      <p className="mt-2 text-2xl font-black text-slate-900">{formatNumberBR(result.result?.z_m, 2)} <span className="text-sm">m</span></p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-5 border border-slate-200">
                      <p className="text-xs font-bold text-slate-700 uppercase">As Tração</p>
                      <p className="mt-2 text-2xl font-black text-slate-900">{formatNumberBR(result.result?.as_tracao_cm2, 2)} <span className="text-sm">cm²</span></p>
                    </div>
                    <div className="rounded-2xl bg-slate-50 p-5 border border-slate-200">
                      <p className="text-xs font-bold text-slate-700 uppercase">Tipo</p>
                      <p className="mt-2 text-sm font-black text-slate-900">{result.result?.type === "single" ? "Bi-apoiada" : "Contínua"}</p>
                    </div>
                  </div>
                )}

                {activeTab === "helical_stairs" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-rose-50 p-5 border border-rose-100">
                      <p className="text-xs font-bold text-rose-700 uppercase">Torção Máxima (Tk)</p>
                      <p className="mt-2 text-3xl font-black text-rose-900">{formatNumberBR(result.result?.t_max_kNm, 1)} <span className="text-sm">kNm</span></p>
                    </div>
                    <div className="rounded-2xl bg-rose-50 p-5 border border-rose-100">
                      <p className="text-xs font-bold text-rose-700 uppercase">Momento Máximo (Mk)</p>
                      <p className="mt-2 text-3xl font-black text-rose-900">{formatNumberBR(result.result?.m_max_kNm, 1)} <span className="text-sm">kNm</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "spt" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl bg-[#f0f9ff] p-5 border border-blue-100">
                      <p className="text-xs font-bold text-blue-700 uppercase">Tensão Admissível</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{formatNumberBR(result.result?.sigma_adm_kPa)} <span className="text-sm">kPa</span></p>
                    </div>
                    <div className="rounded-2xl bg-[#f0f9ff] p-5 border border-blue-100">
                      <p className="text-xs font-bold text-blue-700 uppercase">N_SPT Projeto</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{result.result?.nspt_design}</p>
                    </div>
                    <div className="rounded-2xl bg-[#f0f9ff] p-5 border border-blue-100">
                      <p className="text-xs font-bold text-blue-700 uppercase">Cota Assentamento</p>
                      <p className="mt-2 text-2xl font-black text-blue-900">{result.result?.depth_m} <span className="text-sm">m</span></p>
                    </div>
                  </div>
                )}

                {activeTab === "stability" && (
                  <div className="col-span-2 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100 text-center">
                      <p className="text-xs font-bold text-teal-700 uppercase">Coeficiente γz</p>
                      <p className="mt-2 text-4xl font-black text-teal-900">{formatNumberBR(result.result?.gamma_z, 2)}</p>
                      <span className={`mt-2 inline-block px-3 py-1 rounded-full text-[10px] font-black uppercase ${result.result?.gamma_z <= 1.1 ? "bg-emerald-100 text-emerald-700" : "bg-orange-100 text-orange-700"}`}>
                        {result.result?.gamma_z <= 1.1 ? "Edifício Rígido" : "Edifício Flexível"}
                      </span>
                    </div>
                    <div className="rounded-2xl bg-[#f0fdfa] p-5 border border-teal-100">
                      <p className="text-xs font-bold text-teal-700 uppercase">Força de Arraste Total</p>
                      <p className="mt-2 text-2xl font-black text-teal-900">{formatNumberBR(result.result?.force_total_kN)} <span className="text-sm">kN</span></p>
                      <p className="mt-1 text-[10px] text-teal-600 font-bold italic">Considerando Ca = {result.result?.ca}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[300px] flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-[#e0e7ef] bg-white p-8 text-center">
              <div className="w-16 h-16 bg-[#f2f4f7] rounded-full flex items-center justify-center mb-4">
                <ChevronRight className="text-[#8a9ab0] rotate-90" />
              </div>
              <p className="font-bold text-[#667085]">Aguardando parâmetros...</p>
              <p className="text-xs text-[#8a9ab0] mt-1">Escolha o elemento e clique em dimensionar.</p>
            </div>
          )}
          {activeTab === "beam" && result && (
            <div className="space-y-6">
              {/* Toggle de Modo Visualização */}
              <div className="flex items-center justify-between bg-white border border-[#e0e7ef] p-2 rounded-2xl shadow-sm">
                <div className="flex items-center gap-1">
                  <button 
                    onClick={() => setUseClassical(true)}
                    className={cn("px-4 py-2 rounded-xl text-xs font-black transition", useClassical ? "bg-[#0071e3] text-white" : "text-[#667085] hover:bg-gray-50")}
                  >
                    MÉTODO CLÁSSICO
                  </button>
                  <button 
                    onClick={() => setUseClassical(false)}
                    className={cn("px-4 py-2 rounded-xl text-xs font-black transition", !useClassical ? "bg-[#0071e3] text-white" : "text-[#667085] hover:bg-gray-50")}
                  >
                    SOLVER MEF
                  </button>
                </div>
                <div className="flex items-center gap-3 pr-2">
                  <span className="text-[10px] font-black text-[#98a2b3] uppercase tracking-tighter">Comparar</span>
                  <button 
                    onClick={() => setShowComparison(!showComparison)}
                    className={cn(
                      "relative inline-flex h-5 w-9 items-center rounded-full transition-colors",
                      showComparison ? "bg-green-500" : "bg-[#e0e7ef]"
                    )}
                  >
                    <span className={cn("inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform", showComparison ? "translate-x-5" : "translate-x-0.5")} />
                  </button>
                </div>
              </div>

              <BeamLoadReactionChart
                beamParams={beamParams}
                result={result}
                useClassical={useClassical}
              />

              {/* Seção de Reações de Apoio */}
              <div className="rounded-2xl border border-[#e0e7ef] bg-[#f9fafb]/50 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <div className="h-4 w-1 rounded-full bg-[#0071e3]" />
                  <p className="text-[10px] font-black uppercase tracking-widest text-slate-800">Reações de Apoio (kN)</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {useClassical ? (
                    (result.classical_reactions || []).map((r: any, idx: number) => (
                      <div key={`react-${idx}`} className="flex items-center justify-between rounded-xl bg-white p-3 shadow-sm border border-blue-50">
                        <span className="text-[10px] font-bold text-slate-500">Apoio x={r.x.toFixed(2)}m</span>
                        <span className="text-sm font-black text-blue-600">{r.R.toFixed(2)} kN</span>
                      </div>
                    ))
                  ) : (
                    Object.entries(result.reactions || {}).map(([coord, val]: [string, any], idx: number) => (
                      <div key={`react-mef-${idx}`} className="flex items-center justify-between rounded-xl bg-white p-3 shadow-sm border border-emerald-50">
                        <span className="text-[10px] font-bold text-slate-500">Apoio x={Number(coord).toFixed(2)}m</span>
                        <span className="text-sm font-black text-emerald-600">{(val.V_kN || 0).toFixed(2)} kN</span>
                      </div>
                    ))
                  )}
                </div>
                {showComparison && (
                   <div className="mt-3 pt-3 border-t border-slate-200">
                     <p className="text-[9px] font-black text-[#98a2b3] uppercase mb-2">Comparação (Outro método)</p>
                     <div className="grid grid-cols-2 gap-4 opacity-60">
                        {!useClassical ? (
                          (result.classical_reactions || []).map((r: any, idx: number) => (
                            <div key={`comp-react-${idx}`} className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-slate-400">Analítico x={r.x.toFixed(2)}m</span>
                              <span className="text-xs font-bold text-slate-600">{r.R.toFixed(2)} kN</span>
                            </div>
                          ))
                        ) : (
                          Object.entries(result.reactions || {}).map(([coord, val]: [string, any], idx: number) => (
                            <div key={`comp-react-mef-${idx}`} className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-slate-400">MEF x={Number(coord).toFixed(2)}m</span>
                              <span className="text-xs font-bold text-slate-600">{(val.V_kN || 0).toFixed(2)} kN</span>
                            </div>
                          ))
                        )}
                     </div>
                   </div>
                )}
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <EffortDiagrams
                  memberId={1}
                  data={normalizeBeamDiagram(useClassical ? result.classical_diagrams : result.diagrams)}
                  comparisonData={showComparison ? normalizeBeamDiagram(useClassical ? result.diagrams : result.classical_diagrams) : undefined}
                  comparisonLabel={showComparison ? (useClassical ? "MEF Premium" : "Método Clássico") : undefined}
                  type="moment"
                  unit="kNm"
                  title={useClassical ? "Diagrama de Momentos (Analítico)" : "Diagrama de Momentos (MEF Premium)"}
                  variant="light"
                />
                <EffortDiagrams
                  memberId={1}
                  data={normalizeBeamDiagram(useClassical ? result.classical_diagrams : result.diagrams)}
                  comparisonData={showComparison ? normalizeBeamDiagram(useClassical ? result.diagrams : result.classical_diagrams) : undefined}
                  comparisonLabel={showComparison ? (useClassical ? "MEF Premium" : "Método Clássico") : undefined}
                  type="shear"
                  unit="kN"
                  title={useClassical ? "Diagrama de Cortantes (Analítico)" : "Diagrama de Cortantes (MEF Premium)"}
                  variant="light"
                />
              </div>
            </div>
          )}
          {result?.pedagogical_steps && (
            <PedagogicalStepsView blackboard={result.pedagogical_steps} />
          )}
        </div>
      </div>
      {showFullMemorial && result?.pedagogical_steps && (
        <MemorialHtmlView 
          blackboard={result.pedagogical_steps} 
          onClose={() => setShowFullMemorial(false)}
          onDownloadPdf={() => window.print()}
        />
      )}
    </div>
  );
}
