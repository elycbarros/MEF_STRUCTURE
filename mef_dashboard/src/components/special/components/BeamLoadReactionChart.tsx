import React from "react";
import { ArrowUpDown } from "lucide-react";
import { formatNumberBR } from "../utils";
import { BeamParams, Result } from "../types";

export function BeamLoadReactionChart({
  beamParams,
  result,
  useClassical,
}: {
  beamParams: BeamParams;
  result: Result;
  useClassical: boolean;
}) {
  const totalLength = (Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0) + (Number(beamParams.L_right) || 0);
  
  const distributedLoads = (beamParams.distributedLoads || []).length > 0
    ? beamParams.distributedLoads
    : (Number(beamParams.q) > 0 ? [{ id: "Q", x_start: 0, x_end: totalLength, q_start: Number(beamParams.q), q_end: Number(beamParams.q) }] : []);
  
  const selfWeight = beamParams.includeSelfWeight ? (Number(beamParams.b) * Number(beamParams.h) * 25) : 0;
  
  const shownDistributedLoads = [
    ...distributedLoads,
    ...(selfWeight > 0 ? [{ id: "PP", x_start: 0, x_end: totalLength, q_start: selfWeight, q_end: selfWeight, selfWeight: true }] : []),
  ];

  const reactions = useClassical
    ? (result?.classical_reactions || []).map((r: any) => ({ x: Number(r.x) || 0, R: Number(r.R) || 0 }))
    : Object.entries(result?.reactions || result?.design?.reactions || {}).map(([x, val]: [string, any]) => ({ 
        x: Number(x) || 0, 
        R: typeof val === 'number' ? val : (Number(val?.R) || Number(val?.V_kN) || 0) 
      }));

  const totalLoad = result?.summary?.total_load_kN || shownDistributedLoads.reduce((sum, dl: any) => (
    sum + (((Number(dl.q_start) || 0) + (Number(dl.q_end ?? dl.q_start) || 0)) / 2) * Math.max(0, (Number(dl.x_end) || 0) - (Number(dl.x_start) || 0))
  ), 0) + (beamParams.pointLoads || []).reduce((sum: number, p: any) => sum + (Number(p.P) || 0), 0);
  
  const totalReaction = reactions.reduce((sum: number, r: any) => sum + r.R, 0);
  const residual = result?.summary?.residual_kN ?? (totalReaction - totalLoad);

  const loadColors = {
    distributed: { stroke: "#2563eb", fill: "#dbeafe", label: "#1d4ed8", border: "#bfdbfe" },
    variable: { stroke: "#dc2626", fill: "#fee2e2", label: "#dc2626", border: "#fecaca" },
    selfWeight: { stroke: "#9333ea", fill: "#f3e8ff", label: "#7e22ce", border: "#e9d5ff" },
    point: { stroke: "#f97316", fill: "#ffedd5", label: "#ea580c", border: "#fed7aa" },
  };

  const maxValue = Math.max(
    1,
    ...shownDistributedLoads.map((dl: any) => Math.max(Math.abs(Number(dl.q_start) || 0), Math.abs(Number(dl.q_end ?? dl.q_start) || 0))),
    ...(beamParams.pointLoads || []).map((p: any) => Math.abs(Number(p.P) || 0)),
    ...reactions.map((r: any) => Math.abs(r.R)),
  );

  const scaleX = 820 / Math.max(totalLength, 0.001);
  const beamY = 230;

  const hasPointLoads = (beamParams.pointLoads || []).length > 0;
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
        <line x1={90 + (Number(beamParams.L_left) || 0) * scaleX} y1={beamY - 14} x2={90 + (Number(beamParams.L_left) || 0) * scaleX} y2={beamY + 14} stroke="#94a3b8" strokeWidth="2" />
        <line x1={90 + ((Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0)) * scaleX} y1={beamY - 14} x2={90 + ((Number(beamParams.L_left) || 0) + (Number(beamParams.L) || 0)) * scaleX} y2={beamY + 14} stroke="#94a3b8" strokeWidth="2" />

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

        {(beamParams.pointLoads || []).map((p: any, idx: number) => {
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
        <text x="90" y="397" fontSize="12" fontWeight="900" fill="#059669">Reações para cima | resíduo: {formatNumberBR(residual, 3)} kN</text>
      </svg>
    </div>
  );
}
