"use client";

import React, { useState } from "react";
import { 
  ChevronRight, Ruler, Layers, Zap, Box, Wind, Search, 
  RotateCcw, Layers3, StretchHorizontal, Scissors, Layout, Cpu 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

// Modules
import { StairModule } from "./special/modules/StairModule";
import { ReservoirModule } from "./special/modules/ReservoirModule";
import { FoundationModule } from "./special/modules/FoundationModule";
import { GeotechnicalModule } from "./special/modules/GeotechnicalModule";
import { SpecificElementsModule } from "./special/modules/SpecificElementsModule";

// Shared Components
import { PedagogicalStepsView } from "./PedagogicalStepsView";
import { MemorialHtmlView } from "./MemorialHtmlView";

interface SpecialElementsViewProps {
  apiBaseUrl: string;
  isProfessionalMode?: boolean;
  onGoBack?: () => void;
  type?: "viga" | "pilar" | "escada" | "parede" | "footing" | "spt" | "stability" | "reservatorio";
}

type SpecialTab = "stair" | "concrete_wall" | "footing" | "spt" | "stability" | "retaining_wall" | "reservoir" | "corbel" | "gerber_tooth" | "deep_beam" | "helical_stairs";

export function SpecialElementsView({ apiBaseUrl, type }: SpecialElementsViewProps) {
  const resolveInitialTab = (selectedType?: SpecialElementsViewProps["type"]): SpecialTab =>
    selectedType === "parede" ? "concrete_wall" :
    selectedType === "spt" ? "spt" :
    selectedType === "stability" ? "stability" :
    selectedType === "reservatorio" ? "reservoir" :
    "stair";

  const [activeTab, setActiveTab] = useState<SpecialTab>(resolveInitialTab(type));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [useClassical, setUseClassical] = useState(true);
  const [showFullMemorial, setShowFullMemorial] = useState(false);

  // Params State
  const [stairParams, setStairParams] = useState({ L: 4.0, H: 2.8, width: 1.2, q: 5.0, t: 15, fck: 30 });
  const [wallParams, setWallParams] = useState({ Nd: 500, h: 2.8, t: 0.12, fck: 30 });

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
    let url = `${apiBaseUrl}/calculate/special-elements`;
    let body: any = {};

    try {
      if (activeTab === "spt") {
        url = `${apiBaseUrl}/calculate/spt`;
        body = { spt_data: sptData };
      } else if (activeTab === "stability") {
        url = `${apiBaseUrl}/calculate/stability-mestre`;
        body = windParams;
      } else {
        const paramsMap: Record<string, any> = { stair: stairParams, concrete_wall: wallParams, footing: footingParams, retaining_wall: retainingWallParams, reservoir: reservoirParams, corbel: corbelParams, gerber_tooth: gerberParams, deep_beam: deepBeamParams, helical_stairs: helicalStairParams };
        body = { type: activeTab, params: paramsMap[activeTab] };
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setResult(await response.json());
    } catch (error) {
      console.error("Erro ao calcular:", error);
    } finally {
      setLoading(false);
    }
  };

  const menuItems = [
    { id: "stair", label: "Escadas de Lance", icon: Ruler },

    { id: "helical_stairs", label: "Escada Helicoidal", icon: RotateCcw },
    { id: "reservoir", label: "Tanques / Piscinas", icon: Box },
    { id: "corbel", label: "Consolos Curtos", icon: StretchHorizontal },
    { id: "gerber_tooth", label: "Dentes Gerber", icon: Scissors },
    { id: "deep_beam", label: "Vigas Parede", icon: Layout },
    { id: "concrete_wall", label: "Parede de Concreto", icon: Layers },
    { id: "footing", label: "Sapatas Isoladas", icon: Box },
    { id: "spt", label: "Sondagem SPT", icon: Search },
    { id: "stability", label: "Estabilidade \u03B3z", icon: Wind },
  ];

  return (
    <div className="flex flex-col gap-8 py-4 max-w-7xl mx-auto px-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Especiais <span className="text-blue-600 italic">Lab</span></h2>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Mestre Structural Intelligence v5.0 • Forensic Audit Mode</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
        <aside className="space-y-2 bg-white p-2 rounded-3xl border border-slate-200 h-fit">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id as SpecialTab); setResult(null); }}
              className={cn(
                "w-full flex items-center gap-3 px-5 py-3.5 rounded-2xl text-sm font-black transition-all",
                activeTab === item.id ? "bg-blue-600 text-white shadow-lg shadow-blue-200" : "text-slate-500 hover:bg-slate-50"
              )}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </aside>

        <main>
          {activeTab === "stair" && <StairModule stairParams={stairParams} setStairParams={setStairParams} result={result} loading={loading} calculate={calculate} setShowFullMemorial={setShowFullMemorial} />}

          {activeTab === "reservoir" && <ReservoirModule resParams={reservoirParams} setResParams={setReservoirParams} result={result} loading={loading} calculate={calculate} setShowFullMemorial={setShowFullMemorial} />}
          {(activeTab === "footing" || activeTab === "spt") && <FoundationModule activeTab={activeTab} footingParams={footingParams} setFootingParams={setFootingParams} sptData={sptData} setSptData={setSptData} result={result} loading={loading} calculate={calculate} />}
          {(activeTab === "stability" || activeTab === "retaining_wall") && <GeotechnicalModule activeTab={activeTab} windParams={windParams} setWindParams={setWindParams} retainingWallParams={retainingWallParams} setRetainingWallParams={setRetainingWallParams} result={result} loading={loading} calculate={calculate} />}
          {["corbel", "gerber_tooth", "deep_beam"].includes(activeTab) && <SpecificElementsModule activeTab={activeTab} corbelParams={corbelParams} setCorbelParams={setCorbelParams} gerberParams={gerberParams} setGerberParams={setGerberParams} deepBeamParams={deepBeamParams} setDeepBeamParams={setDeepBeamParams} result={result} loading={loading} calculate={calculate} setShowFullMemorial={setShowFullMemorial} />}
          
          <AnimatePresence>
            {result?.pedagogical_steps && !showFullMemorial && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-8">
                <PedagogicalStepsView steps={result.pedagogical_steps} />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      {showFullMemorial && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/90 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50 rounded-t-3xl">
              <h3 className="font-black text-xl text-slate-900">Memorial de Cálculo • NBR 6118</h3>
              <button onClick={() => setShowFullMemorial(false)} className="px-4 py-2 bg-slate-900 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-slate-800 transition-colors">Fechar</button>
            </div>
            <div className="flex-1 overflow-y-auto p-8 bg-[#fdfdfd]">
               <MemorialHtmlView htmlContent={result?.pedagogical_steps_html || result?.memorial_html || "<p>Memorial em processamento...</p>"} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
