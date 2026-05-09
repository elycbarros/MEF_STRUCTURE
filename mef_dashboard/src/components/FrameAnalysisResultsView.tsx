"use client";

import React from "react";
import { Info, X } from "lucide-react";
import Frame3DView from "./Frame3DView";
import EffortDiagrams from "./EffortDiagrams";
import MemberSectionView from "./MemberSectionView";
import { ReportView } from "./ReportView";
import { normalizeFrameDiagram } from "@/lib/formatters";

interface FrameAnalysisResultsViewProps {
  results: any;
  frameResults: any;
  stabilityResults: any;
  windResults: any;
  docMeta: any;
  apiBaseUrl: string;
  onBack: () => void;
  params: any;
  selectedMember: number | null;
  setSelectedMember: (id: number | null) => void;
}

export function FrameAnalysisResultsView({
  results,
  frameResults,
  stabilityResults,
  windResults,
  docMeta,
  apiBaseUrl,
  onBack,
  params,
  selectedMember,
  setSelectedMember
}: FrameAnalysisResultsViewProps) {
  if (!frameResults) return null;

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          {[
            { label: "Motor", value: String(frameResults.analysis_type ?? "V4.0"), sub: "Frame3DEngine" },
            { label: "γz", value: Number(frameResults.gamma_z ?? 1).toFixed(3), sub: String(frameResults.stability_class ?? "N/D") },
            { label: "Topo 1ª ordem", value: `${Number(frameResults.top_displacement_1st_order_mm ?? 0).toFixed(2)} mm`, sub: "deslocamento X" },
            { label: "Topo 2ª ordem", value: `${Number(frameResults.top_displacement_2nd_order_mm ?? 0).toFixed(2)} mm`, sub: "P-Delta" },
            { label: "Vento", value: String(frameResults.wind_loads_applied ?? 0), sub: "cargas nodais" },
          ].map((item) => (
            <div key={item.label} className="rounded-3xl border border-slate-200 bg-white/80 p-6 backdrop-blur-xl transition-all hover:border-blue-500/30">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400">{item.label}</p>
              <p className="mt-3 text-2xl font-black text-slate-900 font-mono">{item.value}</p>
              <p className="mt-1 text-[10px] font-black uppercase tracking-widest text-slate-900/20">{item.sub}</p>
            </div>
          ))}
        </div>

        {frameResults.stability_message && (
          <div className="rounded-[2rem] border border-blue-500/20 bg-blue-500/5 p-6 text-sm font-black text-blue-400 backdrop-blur-xl flex items-center gap-4">
            <Info className="h-5 w-5 shrink-0" />
            <span className="uppercase tracking-widest leading-relaxed">{frameResults.stability_message}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[500px] rounded-[2.5rem] bg-white/60 overflow-hidden border border-slate-200 relative shadow-2xl backdrop-blur-xl">
            <div className="absolute top-6 left-6 z-10 bg-white/80 backdrop-blur-md px-4 py-2 rounded-2xl border border-slate-200 shadow-xl">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-900">Modelo Analítico 3D</p>
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">Geometria do Pórtico Espacial Premium</p>
            </div>
            <Frame3DView
              nodes={frameResults.model_3d?.nodes ?? []}
              members={frameResults.model_3d?.members ?? []}
              onSelectMember={setSelectedMember}
            />
          </div>
          <div className="h-[500px] rounded-[2.5rem] bg-white/60 border border-slate-200 shadow-2xl p-8 flex flex-col backdrop-blur-xl">
            <div className="mb-6">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-900">Envelopes de Esforços</p>
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-400">Diagramas de Momentos e Cortantes</p>
            </div>
            {(() => {
              const diagramData = normalizeFrameDiagram(frameResults, selectedMember ?? 0);
              if (diagramData.length === 0) {
                return (
                  <div className="flex flex-1 items-center justify-center rounded-[2rem] border border-dashed border-slate-200 bg-white/5 text-center p-8">
                    <p className="text-[11px] font-black uppercase tracking-widest text-slate-400 leading-relaxed">
                      Diagramas de esforços serão ligados na próxima etapa do pórtico premium.
                    </p>
                  </div>
                );
              }
              return (
                <div className="grid flex-1 content-center gap-6 overflow-y-auto pr-2 custom-scrollbar">
                  <EffortDiagrams memberId={selectedMember ?? 0} data={diagramData} type="moment" unit="kNm" variant="dark" />
                  <EffortDiagrams memberId={selectedMember ?? 0} data={diagramData} type="shear" unit="kN" variant="dark" />
                </div>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Modal de Detalhamento de Seção */}
      {selectedMember !== null && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white/60 backdrop-blur-md p-4">
          <div className="w-full max-w-lg rounded-[2.5rem] border border-slate-200 bg-white/80 p-8 shadow-2xl animate-in zoom-in-95 duration-300 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-8">
              <div>
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-400">Inspeção de Elemento</p>
                <h3 className="text-2xl font-black text-slate-900 tracking-tighter">Detalhamento Técnico</h3>
              </div>
              <button
                onClick={() => setSelectedMember(null)}
                className="p-3 rounded-2xl bg-white/5 border border-slate-200 hover:bg-white/10 transition-colors"
              >
                <X className="h-5 w-5 text-slate-900" />
              </button>
            </div>

            {(() => {
              const member = frameResults.model_3d.members.find((m: any) => m.index === selectedMember);
              const isBeam = member?.Type !== "Column";
              const design = isBeam
                 ? frameResults.design.beams.find((b: any) => b.Beam === member?.index || b.id === member?.index)
                 : frameResults.design.pillars.find((p: any) => p.Column === member?.index || p.id === member?.index);

              return (
                <div className="space-y-8">
                  <MemberSectionView
                    b={member?.b / 10 || 20}
                    h={member?.d / 10 || 50}
                    as_top={design?.As_top || design?.As2 || 2.5}
                    as_bottom={design?.As_bottom || design?.As1 || design?.As || 3.8}
                    type={isBeam ? 'beam' : 'pillar'}
                    title={`${isBeam ? 'Viga' : 'Pilar'} ${selectedMember}`}
                  />

                  <div className="rounded-2xl border border-slate-200 bg-white/5 p-6 space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Material</span>
                      <span className="text-sm font-black text-slate-900 font-mono">C{params.fck} <span className="text-[10px] text-slate-400 mx-1">/</span> CA-50</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Esforço Crítico</span>
                      <span className="text-sm font-black text-slate-900 font-mono">{isBeam ? `Mk = ${(design?.M_max || 0).toFixed(2)} kNm` : `Nd = ${(design?.Nd || 0).toFixed(2)} kN`}</span>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      <ReportView
        results={results}
        frameResults={frameResults}
        stabilityResults={stabilityResults}
        windResults={windResults}
        projectMeta={docMeta}
        apiBaseUrl={apiBaseUrl}
        onBack={onBack}
      />
    </div>
  );
}
