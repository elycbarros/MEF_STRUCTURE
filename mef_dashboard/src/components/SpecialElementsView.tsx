"use client";

import React, { useState } from "react";
import { ChevronRight, Download, Plus, Ruler, Trash2, Waves, Zap } from "lucide-react";
import { cn, formatNumberBR } from "@/lib/utils";
import { PedagogicalStepsView } from "./PedagogicalStepsView";
import EffortDiagrams from "./EffortDiagrams";
import { ElegantTooltip } from "./ui/ElegantTooltip";

interface SpecialElementsViewProps {
  apiBaseUrl: string;
  type?: "viga" | "pilar" | "escada" | "reservatorio" | "footing" | "spt" | "stability";
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

export function SpecialElementsView({ apiBaseUrl, type }: SpecialElementsViewProps) {
  const initialTab = type === "viga" ? "beam" : type === "pilar" ? "column" : type === "reservatorio" ? "reservoir" : type === "footing" ? "footing" : type === "spt" ? "spt" : type === "stability" ? "stability" : "stair";
  const [activeTab, setActiveTab] = useState<"stair" | "reservoir" | "beam" | "column" | "footing" | "spt" | "stability">(initialTab);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [useClassical, setUseClassical] = useState(true);
  const [showComparison, setShowComparison] = useState(false);

  // Sync with prop if it changes
  React.useEffect(() => {
    if (type) {
      setActiveTab(type === "viga" ? "beam" : type === "pilar" ? "column" : type === "reservatorio" ? "reservoir" : type === "footing" ? "footing" : "stair");
    }
  }, [type]);

  // Estados dos inputs
  const [stairParams, setStairParams] = useState({ L: 4.0, H: 2.8, width: 1.2, q: 5.0, t: 15, fck: 30 });
  const [resParams, setResParams] = useState({
    name: "RES_01",
    type: "buried",
    Lx: 5.0,
    Ly: 4.0,
    H: 3.0,
    freeboard: 0.2,
    wall_thickness: 0.2,
    slab_thickness: 0.2,
    top_slab_thickness: 0.12,
    n_chambers: 1,
    fck: 30,
    fyk: 500,
    cover_internal: 0.04,
    cover_external: 0.03,
    soil_depth: 2.0,
    soil_gamma: 18,
    soil_ka: 0.33,
    surcharge_kPa: 5,
    live_load_top_kPa: 2,
    liquid_gamma: 10,
    wk_limit_wet: 0.1,
    gamma_f: 1.4,
  });
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
    leftSupport: "pinned",
    rightSupport: "pinned",
    leftK: 10000,
    rightK: 10000,
  });
  const [colParams, setColParams] = useState({ b: 0.40, h: 0.40, Nd: 1200, Mxd: 40, Myd: 15, L_free: 3.0, fck: 25, caa: 2 });
  const [footingParams, setFootingParams] = useState({ Nd: 800.0, sigma_adm: 250.0, ap: 0.20, bp: 0.40, fck: 25 });
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
    else if (activeTab === "reservoir") params = resParams;
    else if (activeTab === "beam") params = beamParams;
    else if (activeTab === "column") params = colParams;
    else if (activeTab === "footing") params = footingParams;

    try {
      const isColumn = activeTab === "column";
      const isBeam = activeTab === "beam";
      const isReservoir = activeTab === "reservoir";
      const url = isColumn
        ? `${apiBaseUrl}/calculate/column`
        : isBeam
          ? `${apiBaseUrl}/calculate/beam`
          : isReservoir
            ? `${apiBaseUrl}/calculate/reservoir`
            : `${apiBaseUrl}/calculate/special-elements`;
      const body = isColumn
        ? {
            b: colParams.b,
            h: colParams.h,
            fck: colParams.fck,
            caa: colParams.caa,
            L_free: colParams.L_free,
            Nd_kN: colParams.Nd,
            Mxd_kNm: colParams.Mxd,
            Myd_kNm: colParams.Myd,
          }
        : isBeam
          ? {
              L: beamParams.L,
              b: beamParams.b,
              h: beamParams.h,
              fck: beamParams.fck,
              caa: beamParams.caa,
              cover: beamParams.coverCm / 100,
              gamma_f: beamParams.gammaF,
              redistribution_delta: beamParams.redistributionDelta,
              n_elements: beamParams.nElements,
              include_self_weight: beamParams.includeSelfWeight,
              supports: [
                { x: 0.0, type: beamParams.leftSupport, k_vertical: beamParams.leftK * 1000 },
                { x: beamParams.L, type: beamParams.rightSupport, k_vertical: beamParams.rightK * 1000 },
              ],
              distributed_loads: [
                { x_start: 0.0, x_end: beamParams.L, q_start: beamParams.q * 1000 },
              ],
              point_loads: beamParams.pointLoads.map(p => ({ x: p.x, P: p.P * 1000 })),
            }
        : isReservoir
          ? resParams
          : activeTab === "spt"
            ? { spt_data: sptData }
            : activeTab === "stability"
              ? windParams
              : { type: activeTab, params };

      const url = activeTab === "spt" ? `${apiBaseUrl}/calculate/spt` : activeTab === "stability" ? `${apiBaseUrl}/calculate/stability` : `${apiBaseUrl}/calculate/special-elements`;
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

  const downloadAcademicPdf = async () => {
    const isColumn = activeTab === "column";
    const isBeam = activeTab === "beam";
    const isSpt = activeTab === "spt";
    const isStability = activeTab === "stability";
    if (!isColumn && !isBeam && !isSpt && !isStability) return;

    let url = "";
    let body: any = {};

    if (isColumn) {
      url = `${apiBaseUrl}/export/academic/column`;
      body = { b: colParams.b, h: colParams.h, fck: colParams.fck, caa: colParams.caa, L_free: colParams.L_free, Nd_kN: colParams.Nd, Mxd_kNm: colParams.Mxd, Myd_kNm: colParams.Myd };
    } else if (isBeam) {
      url = `${apiBaseUrl}/export/academic/beam`;
      body = { L: beamParams.L, b: beamParams.b, h: beamParams.h, fck: beamParams.fck, caa: beamParams.caa, cover: beamParams.coverCm / 100, gamma_f: beamParams.gammaF, redistribution_delta: beamParams.redistributionDelta, n_elements: beamParams.nElements, include_self_weight: beamParams.includeSelfWeight, supports: [{ x: 0.0, type: beamParams.leftSupport }, { x: beamParams.L, type: beamParams.rightSupport }], distributed_loads: [{ x_start: 0.0, x_end: beamParams.L, q_start: beamParams.q * 1000 }], point_loads: beamParams.pointLoads.map(p => ({ x: p.x, P: p.P * 1000 })) };
    } else if (isSpt) {
      url = `${apiBaseUrl}/export/academic/spt`;
      body = { spt_data: sptData };
    } else if (isStability) {
      url = `${apiBaseUrl}/export/academic/stability`;
      body = windParams;
    }

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(`Falha ao exportar PDF (${response.status})`);
    const blob = await response.blob();
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    const filenames: any = { beam: "engine_mestre_viga.pdf", column: "engine_mestre_pilar.pdf", spt: "mestre_sondagem.pdf", stability: "mestre_vento_estabilidade.pdf" };
    link.download = filenames[activeTab] || "memorial_pedagogico.pdf";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(href);
  };

  return (
    <div className="flex flex-col gap-6">
      {!type && (
        <div className="flex flex-wrap gap-2">
          {[
            { id: "stair", label: "Escadas", icon: Ruler },
            { id: "reservoir", label: "Reservatórios", icon: Waves },
            { id: "footing", label: "Sapatas", icon: Box },
            { id: "spt", label: "Geotecnia", icon: Search },
            { id: "stability", label: "Estabilidade", icon: Wind },
            { id: "beam", label: "Vigas", icon: Zap },
            { id: "column", label: "Pilares", icon: Zap },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-black transition ${
                activeTab === tab.id ? "bg-[#0071e3] text-white shadow-lg shadow-[#0071e3]/20" : "bg-white text-[#4d5360] hover:bg-gray-50 border border-black/5"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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

          {activeTab === "reservoir" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-cyan-100 bg-cyan-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-cyan-700">Reservatório / piscina</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Analisa volume, paredes, laje de fundo, fissuração, empuxo externo e subpressão.
                </p>
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Tipologia e geometria</p>
                <div>
                  <label className="text-xs font-bold text-[#667085]">Tipo</label>
                  <select value={resParams.type} onChange={(e) => setResParams({ ...resParams, type: e.target.value })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold">
                    <option value="elevated">Elevado</option>
                    <option value="ground">Apoiado no solo</option>
                    <option value="buried">Enterrado</option>
                    <option value="pool">Piscina</option>
                  </select>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Lx [m]</label>
                    <input type="number" value={resParams.Lx} onChange={(e) => setResParams({ ...resParams, Lx: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Ly [m]</label>
                    <input type="number" value={resParams.Ly} onChange={(e) => setResParams({ ...resParams, Ly: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Água H [m]</label>
                    <input type="number" value={resParams.H} onChange={(e) => setResParams({ ...resParams, H: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Folga [m]</label>
                    <input type="number" value={resParams.freeboard} onChange={(e) => setResParams({ ...resParams, freeboard: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Parede [m]</label>
                    <input type="number" value={resParams.wall_thickness} onChange={(e) => setResParams({ ...resParams, wall_thickness: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Fundo [m]</label>
                    <input type="number" value={resParams.slab_thickness} onChange={(e) => setResParams({ ...resParams, slab_thickness: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Material, fissuração e solo</p>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <ElegantTooltip content="Resistência característica do concreto à compressão (aos 28 dias).">
                    <label className="text-xs font-bold text-[#667085]">fck [MPa]</label>
                  </ElegantTooltip>
                    <input type="number" value={resParams.fck} onChange={(e) => setResParams({ ...resParams, fck: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">c molhada [m]</label>
                    <input type="number" value={resParams.cover_internal} onChange={(e) => setResParams({ ...resParams, cover_internal: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">wk lim [mm]</label>
                    <input type="number" value={resParams.wk_limit_wet} onChange={(e) => setResParams({ ...resParams, wk_limit_wet: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Solo h [m]</label>
                    <input type="number" value={resParams.soil_depth} onChange={(e) => setResParams({ ...resParams, soil_depth: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">γsolo</label>
                    <input type="number" value={resParams.soil_gamma} onChange={(e) => setResParams({ ...resParams, soil_gamma: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Ka</label>
                    <input type="number" value={resParams.soil_ka} onChange={(e) => setResParams({ ...resParams, soil_ka: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "beam" && (
            <div className="space-y-5">
              <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-blue-700">Modelo acadêmico</p>
                <p className="mt-1 text-xs font-semibold leading-relaxed text-slate-600">
                  Defina geometria, ações, durabilidade, apoios e parâmetros numéricos para gerar o memorial pedagógico completo.
                </p>
              </div>

              <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Geometria</p>
              <div>
                <ElegantTooltip content="Distância teórica entre os centros dos apoios da viga ou faces internas.">
                  <label className="text-xs font-bold text-[#667085]">Vão Livre (L) [m]</label>
                </ElegantTooltip>
                  <input type="number" step="0.1" value={beamParams.L} onChange={(e) => setBeamParams({ ...beamParams, L: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
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
                <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Ações e combinações</p>
              <div>
                <ElegantTooltip content="Carga por metro linear, somando peso próprio, alvenaria e revestimentos.">
                  <label className="text-xs font-bold text-[#667085]">Carga distribuída característica (qk) [kN/m]</label>
                </ElegantTooltip>
                <input type="number" step="0.1" value={beamParams.q} onChange={(e) => setBeamParams({ ...beamParams, q: Number(e.target.value) })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold" />
              </div>
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
                <div className="flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[#98a2b3]">Cargas Pontuais</p>
                  <button
                    type="button"
                    onClick={() => {
                      const id = `PL${beamParams.pointLoads.length + 1}`;
                      setBeamParams({
                        ...beamParams,
                        pointLoads: [...beamParams.pointLoads, { id, x: beamParams.L / 2, P: 50 }]
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
                      <option value="pinned">Apoio Fixo (2 restrições)</option>
                      <option value="fixed">Engaste (3 restrições)</option>
                      <option value="roller">Apoio Móvel (1 restrição)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-bold text-[#667085]">Apoio direito</label>
                    <select value={beamParams.rightSupport} onChange={(e) => setBeamParams({ ...beamParams, rightSupport: e.target.value })} className="w-full mt-1 rounded-xl border border-[#e0e7ef] bg-[#f9fafb] p-3 text-sm font-bold">
                      <option value="pinned">Apoio Fixo (2 restrições)</option>
                      <option value="fixed">Engaste (3 restrições)</option>
                      <option value="roller">Apoio Móvel (1 restrição)</option>
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
          {(activeTab === "beam" || activeTab === "column" || activeTab === "spt" || activeTab === "stability") && (
            <button
              type="button"
              onClick={downloadAcademicPdf}
              className="w-full flex items-center justify-center gap-2 rounded-2xl border border-amber-200 bg-amber-50 py-3 text-sm font-black text-amber-700 hover:bg-amber-100 active:scale-95 transition-all"
            >
              <Download size={16} />
              Memorial Pedagógico PDF
            </button>
          )}
        </div>

        {/* Coluna de Resultados */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <div className="rounded-3xl border border-[#e0e7ef] bg-white p-8 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-black text-xl text-[#101828]">Memória de Cálculo</h3>
                <span className="px-3 py-1 bg-[#f2f4f7] rounded-full text-[10px] font-black uppercase text-[#667085]">NBR 6118</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {activeTab === "beam" && (
                  <>
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs font-bold text-[#667085] uppercase">Momento Fletor (Mk)</p>
                        <p className="text-3xl font-black">{formatNumberBR(result.design?.M_max_pos_kNm ?? result.Mk)} <span className="text-sm font-bold text-[#8a9ab0]">kNm</span></p>
                      </div>
                      <div>
                        <p className="text-xs font-bold text-[#667085] uppercase">Armadura Tracionada (As)</p>
                        <p className="text-3xl font-black text-[#1f8f56]">{formatNumberBR(result.design?.flexure_bottom?.As_cm2 ?? result.As_cm2)} <span className="text-sm font-bold text-[#8a9ab0]">cm²</span></p>
                      </div>
                    </div>
                    <div className="rounded-2xl bg-[#f9fafb] p-6 space-y-3 border border-[#f2f4f7]">
                      <p className="text-sm font-bold">Verificação de Rigidez</p>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-black ${(result.design?.overall_status ?? result.status) === "ATENDE" || result.status === "OK" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700 border border-rose-200 animate-pulse"}`}>
                        {result.design?.overall_status ?? result.status}
                      </span>
                      <p className="text-xs text-[#667085]">A viga agora usa o solver premium e exibe o roteiro MESTRE passo a passo.</p>
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
                  </>
                )}

                {(activeTab === "stair" || activeTab === "reservoir" || activeTab === "footing" || activeTab === "spt" || activeTab === "stability") && (
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

                {activeTab === "reservoir" && (
                  <div className="col-span-2 space-y-4">
                    <div className="grid gap-4 md:grid-cols-4">
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Volume</p>
                        <p className="mt-2 text-2xl font-black">{formatNumberBR(result.summary?.volume_m3)} <span className="text-sm text-[#8a9ab0]">m³</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">As parede</p>
                        <p className="mt-2 text-2xl font-black text-emerald-600">{formatNumberBR(result.summary?.As_parede_cm2_m)} <span className="text-sm text-[#8a9ab0]">cm²/m</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">wk máx.</p>
                        <p className="mt-2 text-2xl font-black">{formatNumberBR(result.summary?.wk_max_mm, 3)} <span className="text-sm text-[#8a9ab0]">mm</span></p>
                      </div>
                      <div className="rounded-2xl bg-[#f9fafb] p-5 border border-[#f2f4f7]">
                        <p className="text-xs font-bold text-[#667085] uppercase">Status</p>
                        <p className="mt-2 text-sm font-black">{result.summary?.status ?? result.overall_status ?? "--"}</p>
                      </div>
                    </div>
                    <div className="rounded-2xl border border-cyan-100 bg-cyan-50/60 p-5">
                      <p className="text-sm font-black text-cyan-900">Parecer hidráulico-estrutural</p>
                      <p className="mt-2 text-xs font-semibold leading-relaxed text-cyan-900">
                        Caso governante: {result.wall_envelope?.governing ?? "--"}. 
                        Pressão no fundo: {formatNumberBR(result.hydraulic?.pressao_fundo_kPa)} kPa. 
                        {result.subpressao?.status ? `Subpressão: ${result.subpressao.status} (FS=${result.subpressao.fator_flutuacao}).` : "Sem verificação crítica de subpressão para esta tipologia."}
                      </p>
                    </div>
                  </div>
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
                <div className="flex gap-1">
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

              <div className="grid gap-4 lg:grid-cols-2">
                <EffortDiagrams
                  memberId={1}
                  data={normalizeBeamDiagram(useClassical ? result.classical_diagrams : result.diagrams)}
                  comparisonData={showComparison ? normalizeBeamDiagram(useClassical ? result.diagrams : result.classical_diagrams) : undefined}
                  comparisonLabel={showComparison ? (useClassical ? "MEF Premium" : "Método Clássico") : undefined}
                  type="moment"
                  unit="kNm"
                  title={useClassical ? "Momento Clássico (qL²/8)" : "Momento Premium (MEF)"}
                  variant="light"
                />
                <EffortDiagrams
                  memberId={1}
                  data={normalizeBeamDiagram(useClassical ? result.classical_diagrams : result.diagrams)}
                  comparisonData={showComparison ? normalizeBeamDiagram(useClassical ? result.diagrams : result.classical_diagrams) : undefined}
                  comparisonLabel={showComparison ? (useClassical ? "MEF Premium" : "Método Clássico") : undefined}
                  type="shear"
                  unit="kN"
                  title={useClassical ? "Esforço Cortante (qL/2)" : "Cortante Premium (MEF)"}
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
    </div>
  );
}
