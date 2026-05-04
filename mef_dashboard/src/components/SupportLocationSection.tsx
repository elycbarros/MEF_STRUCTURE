"use client";

import React from "react";
import { Plus, Trash2 } from "lucide-react";

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
  systemType: "radier" | "laje";
  params: any;
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
  systemType,
  params
}: SupportLocationSectionProps) {
  return (
    <div className="space-y-8 mt-10 border-t pt-10">
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
            className="inline-flex items-center gap-2 rounded-xl bg-[#0071e3] px-3 py-2 text-sm font-bold text-white hover:bg-[#0062c7]"
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
            {pillars.map((pillar, index) => (
              <tr key={`${pillar.id}-${index}`} className="border-t border-[#edf1f7]">
                <td className="px-3 py-2">
                  <input
                    value={pillar.id}
                    onChange={(e) => updatePillar(index, "id", e.target.value)}
                    className="w-16 rounded-lg border border-[#d9dfe9] px-2 py-1"
                  />
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
                    className="w-20 rounded-lg border border-[#d9dfe9] px-2 py-1 font-bold text-[#0071e3]"
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
                  <button
                    type="button"
                    onClick={() => removePillar(index)}
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

      {systemType === "laje" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-xl font-black">Apoios em Linha (Vigas)</h3>
            <button
              type="button"
              onClick={addLineSupport}
              className="inline-flex items-center gap-2 rounded-xl bg-[#0071e3] px-3 py-2 text-sm font-bold text-white hover:bg-[#0062c7]"
            >
              <Plus className="h-4 w-4" />
              Adicionar viga
            </button>
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
