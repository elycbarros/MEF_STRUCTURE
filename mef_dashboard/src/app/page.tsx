"use client";

import React, { useState, useEffect } from "react";
import { ChevronDown, ChevronUp, Cpu } from "lucide-react";
import Structural3DView from "@/components/Structural3DView";
import ProfessionalDashboard from "@/components/ProfessionalDashboard";
import TerminalLogs from "@/components/TerminalLogs";
import { SpecialElementsView } from "@/components/SpecialElementsView";
import { BeamLabView } from "@/components/BeamLabView";
import { ColumnLabView } from "@/components/ColumnLabView";
import { WindStabilityView } from "@/components/WindStabilityView";
import WelcomeScreen from "@/components/WelcomeScreen";
import { PhDEngineView } from "@/components/PhDEngineView";
import { VigaCrossView } from "@/components/VigaCrossView";
import { GuidedGeometryView } from "@/components/GuidedGeometryView";
import { TensionProView } from "@/components/TensionProView";
import { MainHeader } from "@/components/MainHeader";
import { MainSidebar } from "@/components/MainSidebar";
import { SupportLocationSection } from "@/components/SupportLocationSection";
import { AcademicDashboard } from "@/components/AcademicDashboard";
import { AcademicBacklogView } from "@/components/AcademicBacklogView";
import { AcademicPorticoView } from "@/components/AcademicPorticoView";
import { AcademicTrussView } from "@/components/AcademicTrussView";
import LibraryView from "@/components/LibraryView";
import { ReinforcementView } from "@/components/ReinforcementView";
import { FrameAnalysisResultsView } from "@/components/FrameAnalysisResultsView";
import { cn } from "@/lib/utils";
import { useStructuralApp } from "@/hooks/useStructuralApp";

export default function Home() {
  const [selectedMode, setSelectedMode] = useState<"academic" | "professional" | null>(null);
  const isProfessionalMode = selectedMode === "professional";

  const {
    activeTab, setActiveTab,
    loading, setLoading,
    statusMessage, setStatusMessage,
    logs, addLog,
    systemType, setSystemType,
    slabType, setSlabType,
    docMeta, setDocMeta,
    tabs,
    runAnalysis,
    runOptimization,
    runFrameAnalysis,
    checkApiConnection,
    handleBackToDashboard,
    apiBaseUrl,
    apiOnline,
    apiChecking,
    showTerminal,
    setShowTerminal,
    optLogs,
    params,
    setParams,
    results,
    frameResults,
    stabilityResults,
    windResults,
    reinforcementFlexure,
    reinforcementPunching,
    reinforcementService,
    reinforcementNotes,
    reinforcementCriticalZones,
    detailingGuidance,
    serviceChecks,
    selectedFoundationType,
    selectedPurposePreset,
    selectedSoilPreset,
    displayedRiskSummary,
    checklistStatusLabel,
    selectedMember,
    setSelectedMember,
    pillars,
    setPillars,
    lineSupports,
    setLineSupports,
    holes,
    setHoles,
    areaLoads,
    setAreaLoads,
    windParams,
    setWindParams,
    numPavimentos,
    setNumPavimentos,
    showLoadToast,
    estimateLoads,
    b_nerv, setBNerv,
    dist_nerv, setDistNerv,
    h_mesa, setHMesa,
    area_voids, setAreaVoids,
    p_force, setPForce,
    ecc, setEcc,
    fillerType, setFillerType,
    ignorePillars, setIgnorePillars,
    analysisMode,
    addPillar,
    removePillar,
    updatePillar,
    restoreSamplePillars,
    addLineSupport,
    removeLineSupport,
    updateLineSupport,
    updateAreaLoad,
    applyGuidedPreset,
    updateKvSource,
    updateParam,
    runWindStabilityAnalysis,
    primaryTabs,
    secondaryTabs,
    KV_SOURCE_OPTIONS,
    kvSource,
    kvConfidence,
    setKvConfidence
  } = useStructuralApp(selectedMode);
  
  // Sync systemType with activeTab for Lajes/Radier
  useEffect(() => {
    if (activeTab === "geometria") setSystemType("radier");
    if (activeTab === "lajes") setSystemType("laje");
  }, [activeTab, setSystemType]);

  if (!selectedMode) {
    return (
      <WelcomeScreen
        onSelectMode={(mode) => {
          setSelectedMode(mode);
        }}
      />
    );
  }

  return (
    <div className={cn(
      "min-h-screen transition-colors duration-700 p-4 md:p-8",
      isProfessionalMode ? "bg-[#0f1115]" : "bg-[#f8f9fa]"
    )}>
      <div className="mx-auto max-w-[1600px]">
        <MainHeader
          selectedMode={selectedMode}
          setSelectedMode={setSelectedMode}
          systemType={systemType}
          setSystemType={setSystemType}
          checkApiConnection={checkApiConnection}
          apiChecking={apiChecking}
          runOptimization={runOptimization}
          runAnalysis={runAnalysis}
          runFrameAnalysis={runFrameAnalysis}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          loading={loading}
          apiBaseUrl={apiBaseUrl}
          apiOnline={apiOnline}
          statusMessage={statusMessage}
          optLogs={optLogs}
          secondaryTabs={secondaryTabs}
        />

        <div className="mt-8 grid grid-cols-12 gap-8">
          <MainSidebar
            tabs={primaryTabs}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            theme={isProfessionalMode ? "professional" : "academic"}
          />

          <section className={cn(
            "col-span-12 rounded-[40px] border p-8 transition-all duration-700 shadow-2xl",
            isProfessionalMode 
              ? "bg-[#16191f] border-slate-200 shadow-blue-900/10" 
              : "bg-white/80 border-slate-200 shadow-slate-200/50",
            selectedMode !== "academic" ? "col-span-12" : "col-span-12"
          )}>
            {activeTab === "dashboard" && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-black">Painel de Controle</h2>
                  {selectedMode !== "academic" && (
                    <div className="flex items-center gap-2 p-1 bg-[#f0f2f6] rounded-xl">
                      <button
                        onClick={() => setSelectedMode("academic")}
                        className={cn(
                          "px-3 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all",
                          !isProfessionalMode ? "bg-white text-[#1a1c1e] shadow-sm" : "text-[#6a7485]"
                        )}
                      >
                        Lab Mode
                      </button>
                      <button
                        onClick={() => setSelectedMode("professional")}
                        className={cn(
                          "px-3 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all",
                          isProfessionalMode ? "bg-[#1a1c1e] text-white shadow-md" : "text-[#6a7485]"
                        )}
                      >
                        Pro Mode
                      </button>
                    </div>
                  )}
                </div>

                {selectedMode === "academic" ? (
                  <AcademicDashboard
                    setActiveTab={setActiveTab}
                    setSystemType={setSystemType}
                  />
                ) : (
                  <ProfessionalDashboard 
                    memorial={results?.memorial} 
                    config={params} 
                    mode="professional" 
                  />
                )}

                {/* 3D Preview in Dashboard */}
                {results && results.master && (
                  <div className="mt-8">
                    <h3 className="text-sm font-black text-[#1a1c1e] uppercase tracking-widest mb-4">Gêmeo Digital (Digital Twin)</h3>
                    <Structural3DView
                      Lx={params.Lx}
                      Ly={params.Ly}
                      h={params.h}
                      nodes={(results.master as any).nodes || []}
                      elements={(results.master as any).elements || []}
                      pillars={pillars.map(p => ({
                        id: p.id,
                        x: p.x,
                        y: p.y,
                        bx: p.bx ?? 0.5,
                        by: p.by ?? 0.5,
                        reaction_kN: (results.master as any).pillar_reactions?.[p.id] || p.p_kN
                      }))}
                      viewMode="displacements"
                    />
                  </div>
                )}
              </div>
            )}

            {(activeTab === "geometria" || activeTab === "lajes") && (
              <GuidedGeometryView
                mode={selectedMode}
                systemType={systemType}
                setSystemType={setSystemType}
                slabType={slabType}
                setSlabType={setSlabType}
                b_nerv={b_nerv}
                setBNerv={setBNerv}
                dist_nerv={dist_nerv}
                setDistNerv={setDistNerv}
                h_mesa={h_mesa}
                setHMesa={setHMesa}
                area_voids={area_voids}
                setAreaVoids={setAreaVoids}
                p_force={p_force}
                setPForce={setPForce}
                ecc={ecc}
                setEcc={setEcc}
                fillerType={fillerType}
                setFillerType={setFillerType}
                ignorePillars={ignorePillars}
                setIgnorePillars={setIgnorePillars}
                pillars={pillars}
                addPillar={addPillar}
                removePillar={removePillar}
                updatePillar={updatePillar}
                restoreSamplePillars={restoreSamplePillars}
                lineSupports={lineSupports}
                addLineSupport={addLineSupport}
                removeLineSupport={removeLineSupport}
                updateLineSupport={updateLineSupport}
                setLineSupports={setLineSupports}
                holes={holes}
                setHoles={setHoles}
                areaLoads={areaLoads}
                setAreaLoads={setAreaLoads}
                updateAreaLoad={updateAreaLoad}
                applyGuidedPreset={applyGuidedPreset}
                analysisMode={analysisMode}
                kvConfidence={kvConfidence}
                setKvConfidence={setKvConfidence}
                kvSource={kvSource}
                updateKvSource={updateKvSource}
                params={params}
                updateParam={updateParam}
                numPavimentos={numPavimentos}
                setNumPavimentos={setNumPavimentos}
                estimateLoads={estimateLoads}
                showLoadToast={showLoadToast}
                KV_SOURCE_OPTIONS={KV_SOURCE_OPTIONS}
                runAnalysis={runAnalysis}
                loading={loading}
              />
            )}

            {activeTab === "backlog" && selectedMode === "academic" && (
              <AcademicBacklogView
                setActiveTab={setActiveTab}
                setSystemType={setSystemType}
              />
            )}

            {activeTab === "porticos" && selectedMode === "academic" && (
              <AcademicPorticoView />
            )}

            {activeTab === "trelicas" && selectedMode === "academic" && (
              <AcademicTrussView />
            )}

            {activeTab === "pilares" && (
              <SupportLocationSection
                pillars={pillars}
                addPillar={addPillar}
                removePillar={removePillar}
                updatePillar={updatePillar}
                restoreSamplePillars={restoreSamplePillars}
                lineSupports={lineSupports}
                setLineSupports={setLineSupports}
                addLineSupport={addLineSupport}
                removeLineSupport={removeLineSupport}
                updateLineSupport={updateLineSupport}
                systemType={systemType}
                params={params}
                holes={holes}
                areaLoads={areaLoads}
                updateAreaLoad={updateAreaLoad}
              />
            )}

            {activeTab === "armadura" && (
              <ReinforcementView
                flexure={reinforcementFlexure}
                punching={reinforcementPunching}
                service={reinforcementService}
                guidance={detailingGuidance}
                notes={reinforcementNotes}
                criticalZones={reinforcementCriticalZones}
                serviceChecks={serviceChecks}
              />
            )}

            {activeTab === "resultado" && (
              <FrameAnalysisResultsView
                results={results}
                frameResults={frameResults}
                stabilityResults={stabilityResults}
                windResults={windResults}
                docMeta={docMeta}
                apiBaseUrl={apiBaseUrl}
                onBack={handleBackToDashboard}
                params={params}
                selectedMember={selectedMember}
                setSelectedMember={setSelectedMember}
              />
            )}

            {activeTab === "vento" && (
              <div className="space-y-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-apple-text">Vento e Estabilidade</h2>
                    <p className="mt-1 text-sm font-semibold text-apple-muted">
                      Análise de pressões dinâmicas (NBR 6123) e efeitos de 2ª ordem (Gamma-Z / P-Delta).
                    </p>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-black/5">
                    <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                    <span className="text-[10px] font-black uppercase tracking-wider text-apple-text">Wind Engine v3.5</span>
                  </div>
                </div>
                <WindStabilityView
                  params={windParams}
                  onParamChange={(key, value) => setWindParams(prev => ({ ...prev, [key]: value }))}
                  onRunAnalysis={runWindStabilityAnalysis}
                  results={windResults}
                  stabilityResults={stabilityResults}
                  loading={loading}
                />
              </div>
            )}

            {activeTab === "vigas" && (
              <BeamLabView apiBaseUrl={apiBaseUrl} />
            )}

            {activeTab === "pilares_isolados" && (
              <ColumnLabView apiBaseUrl={apiBaseUrl} />
            )}

            {activeTab === "especiais" && (
              <div className="space-y-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-[#1d1d1f]">Elementos Especiais</h2>
                    <p className="mt-1 text-sm font-semibold text-[#666a73]">
                      Cálculo analítico de paredes e elementos especiais conforme NBR 6118.
                    </p>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-black/5">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span className="text-[10px] font-black uppercase tracking-wider text-[#1d1d1f]">Solvers Ativos</span>
                  </div>
                </div>
                <SpecialElementsView
                  apiBaseUrl={apiBaseUrl}
                  isProfessionalMode={isProfessionalMode}
                  onGoBack={() => setActiveTab("dashboard")}
                />
              </div>
            )}

            {activeTab === "vigacross" && (
              <VigaCrossView />
            )}

            {activeTab === "biblioteca" && (
              <LibraryView />
            )}

            {activeTab === "tensionpro" && (
              <TensionProView />
            )}

          </section>
        </div>
      </div>
      <TerminalLogs logs={logs} isVisible={showTerminal} />

      {/* Floating Scroll to Bottom Button */}
      <button
        onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
        className="fixed bottom-24 right-8 z-[100] flex h-11 w-11 items-center justify-center rounded-full bg-white/80 backdrop-blur-md text-[#1d1d1f] shadow-lg border border-black/5 transition-all hover:scale-110 active:scale-95 group"
        title="Ir para o fim da página"
      >
        <ChevronDown className="h-5 w-5 transition-transform group-hover:translate-y-0.5" />
      </button>

      <button
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        className="fixed bottom-36 right-8 z-[100] flex h-11 w-11 items-center justify-center rounded-full bg-white/80 backdrop-blur-md text-[#1d1d1f] shadow-lg border border-black/5 transition-all hover:scale-110 active:scale-95 group"
        title="Ir para o topo"
      >
        <ChevronUp className="h-5 w-5 transition-transform group-hover:-translate-y-0.5" />
      </button>
    </div>
  );
}

// Helpers movidos para @/lib/formatters.ts e @/lib/foundationFormatters.ts
