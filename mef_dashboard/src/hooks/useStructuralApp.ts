"use client";

import React, { useState, useCallback, useEffect, useMemo } from "react";
import { useProjectState } from "./useProjectState";
import { useRadierAnalysis } from "./useRadierAnalysis";
import { useFrameAnalysis } from "./useFrameAnalysis";
import { buildFramePremiumPayload } from "@/lib/framePayloadBuilder";
import { 
  asRecord, 
  asRecordArray, 
  asStringArray, 
  collectFileArtifacts, 
  parseLocaleNumberInput, 
  uniqueStrings 
} from "@/lib/formatters";
import { buildFieldRiskSummary, formatChecklistStatus } from "@/lib/foundationFormatters";
import { fieldRisks, foundationTypes, purposePresets, soilPresets } from "@/lib/radierKnowledge";

const samplePillars = [
  { id: "P01", x: 4.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P02", x: 16.0, y: 4.0, p_kN: 3500.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P03", x: 28.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P04", x: 4.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P05", x: 16.0, y: 12.0, p_kN: 5200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P06", x: 28.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
];

const KV_SOURCE_OPTIONS = [
  { id: "plate_load_test", label: "Prova de carga", confidence: 0.9 },
  { id: "settlement_backcalc", label: "Retroanálise de recalque", confidence: 0.8 },
  { id: "spt_correlation", label: "Correlação SPT", confidence: 0.65 },
  { id: "table_reference", label: "Tabela/literatura", confidence: 0.5 },
  { id: "engineering_estimate", label: "Estimativa inicial", confidence: 0.35 },
];

export function useStructuralApp(selectedMode: "academic" | "professional" | null) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_RADIER_API_URL ?? "http://127.0.0.1:8000";

  const projectState = useProjectState(selectedMode);
  const radierAnalysis = useRadierAnalysis();
  const frameAnalysis = useFrameAnalysis();

  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [apiChecking, setApiChecking] = useState(false);
  const [memorialGeneratedAt, setMemorialGeneratedAt] = useState<Date | null>(null);
  const [analysisMode, setAnalysisMode] = useState<"guided" | "manual">("guided");
  const [optLogs, setOptLogs] = useState<any[]>([]);
  const [showTerminal, setShowTerminal] = useState(false);
  const [selectedMember, setSelectedMember] = useState<number | null>(null);
  const [numPavimentos, setNumPavimentos] = useState(1);
  const [showLoadToast, setShowLoadToast] = useState(false);


  // Derived Data (extracted from page.tsx)
  const memorial = useMemo(() => (radierAnalysis.results?.memorial ?? {}) as Record<string, unknown>, [radierAnalysis.results]);
  const checklistProf = useMemo(() => asRecord(memorial.checklist_profissional), [memorial]);
  const reinforcementSummary = useMemo(() => asRecord(radierAnalysis.results?.reinforcement_summary), [radierAnalysis.results]);
  const structuralChecks = useMemo(() => asRecord(memorial.verificacoes_estruturais), [memorial]);
  
  const reinforcementFlexure = useMemo(() => asRecord(reinforcementSummary.flexure ?? structuralChecks.flexao), [reinforcementSummary, structuralChecks]);
  const reinforcementPunching = useMemo(() => asRecord(reinforcementSummary.punching ?? structuralChecks.puncao), [reinforcementSummary, structuralChecks]);
  const reinforcementService = useMemo(() => asRecord(reinforcementSummary.serviceability), [reinforcementSummary]);
  const reinforcementNotes = useMemo(() => asStringArray(reinforcementSummary.notes), [reinforcementSummary]);
  const reinforcementCriticalZones = useMemo(() => asRecordArray(reinforcementSummary.critical_zones), [reinforcementSummary]);
  const detailingGuidance = useMemo(() => asRecord(reinforcementSummary.detailing_guidance ?? memorial.detalhamento_final), [reinforcementSummary, memorial]);
  const serviceChecks = useMemo(() => asRecord(memorial.verificacoes_de_servico), [memorial]);
  
  const selectedFoundationType = useMemo(() => foundationTypes.find((item) => item.id === radierAnalysis.foundationTypeId) ?? foundationTypes[0], [radierAnalysis.foundationTypeId]);
  const selectedPurposePreset = useMemo(() => purposePresets.find((item) => item.id === radierAnalysis.purposePresetId) ?? purposePresets[0], [radierAnalysis.purposePresetId]);
  const selectedSoilPreset = useMemo(() => soilPresets.find((item) => item.id === radierAnalysis.soilPresetId) ?? soilPresets[0], [radierAnalysis.soilPresetId]);
  
  const selectedFieldRisks = useMemo(
    () => fieldRisks.filter((risk) => radierAnalysis.selectedFieldRiskIds.includes(risk.id)),
    [radierAnalysis.selectedFieldRiskIds],
  );
  const localRiskSummary = useMemo(
    () => buildFieldRiskSummary(selectedFieldRisks, selectedSoilPreset.risk),
    [selectedFieldRisks, selectedSoilPreset.risk],
  );
  const displayedRiskSummary = radierAnalysis.results?.field_risk_summary ?? localRiskSummary;
  const checklistStatusLabel = formatChecklistStatus(String(checklistProf.status ?? "Sem resultado"));

  const checkApiConnection = useCallback(async () => {
    setApiChecking(true);
    try {
      const res = await fetch(`${apiBaseUrl}/health`);
      const data = await res.json();
      setApiOnline(data.status === "healthy" || data.status === "ok");
    } catch {
      setApiOnline(false);
    } finally {
      setApiChecking(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    checkApiConnection();
  }, [checkApiConnection]);

  // Terminal Auto-hide
  useEffect(() => {
    if (projectState.loading) {
      setShowTerminal(true);
    } else {
      const hasError = projectState.logs.some(l => l.type === 'error');
      if (!hasError && projectState.logs.length > 0) {
        const timer = setTimeout(() => setShowTerminal(false), 3000);
        return () => clearTimeout(timer);
      }
    }
  }, [projectState.loading, projectState.logs]);

  const runAnalysis = async () => {
    projectState.setLoading(true);
    projectState.addLog("Iniciando processamento no motor HPC...", "info");
    try {
      const res = await fetch(`${apiBaseUrl}/calculate_v2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...radierAnalysis.params,
          pillars: radierAnalysis.ignorePillars ? [] : radierAnalysis.pillars,
          line_supports: radierAnalysis.lineSupports,
          holes: radierAnalysis.holes,
          area_loads: radierAnalysis.areaLoads,
          foundation_type_id: radierAnalysis.foundationTypeId,
          purpose_preset_id: radierAnalysis.purposePresetId,
          soil_preset_id: radierAnalysis.soilPresetId,
          diagnostic_conservatism: radierAnalysis.diagnosticConservatism,
          kv_source: radierAnalysis.kvSource,
          kv_confidence: radierAnalysis.kvConfidence,
          selected_field_risks: radierAnalysis.selectedFieldRiskIds
        }),
      });
      const data = await res.json();
      if (data.success) {
        radierAnalysis.setResults(data);
        projectState.addLog("Análise concluída com sucesso.", "success");
        projectState.setActiveTab("armadura");
      }
    } catch {
      projectState.addLog("Erro de rede.", "error");
    } finally {
      projectState.setLoading(false);
    }
  };

  const runOptimization = async () => {
    projectState.setLoading(true);
    projectState.addLog("Iniciando Otimização Multi-Mestre...", "info");
    try {
      const res = await fetch(`${apiBaseUrl}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...radierAnalysis.params, pillars: radierAnalysis.pillars }),
      });
      const data = await res.json();
      if (data.success) {
        setOptLogs(data.logs || []);
        projectState.addLog("Otimização concluída.", "success");
      }
    } finally {
      projectState.setLoading(false);
    }
  };

  const runFrameAnalysis = async () => {
    projectState.setLoading(true);
    projectState.addLog("Iniciando Frame3DEngine...", "info");
    try {
      const payload = buildFramePremiumPayload(radierAnalysis.params, radierAnalysis.pillars, frameAnalysis.windParams);
      const res = await fetch(`${apiBaseUrl}/calculate/frame-premium`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        frameAnalysis.setFrameResults(data.frame);
        projectState.addLog("Análise de pórtico concluída.", "success");
        projectState.setActiveTab("resultado");
      }
    } finally {
      projectState.setLoading(false);
    }
  };

  const handleBackToDashboard = () => projectState.setActiveTab("dashboard");

  // Missing Helper Functions
  const addPillar = useCallback(() => {
    const newId = `P${(radierAnalysis.pillars.length + 1).toString().padStart(2, '0')}`;
    radierAnalysis.setPillars(prev => [...prev, { id: newId, x: 0, y: 0, p_kN: 100, bx: 0.5, by: 0.5, support_type: "pinned" }]);
  }, [radierAnalysis]);

  const removePillar = useCallback((id: string) => {
    radierAnalysis.setPillars(prev => prev.filter(p => p.id !== id));
  }, [radierAnalysis]);

  const updatePillar = useCallback((id: string, updates: Partial<Pillar>) => {
    radierAnalysis.setPillars(prev => prev.map(p => p.id === id ? { ...p, ...updates } : p));
  }, [radierAnalysis]);

  const restoreSamplePillars = useCallback(() => {
    radierAnalysis.setPillars(samplePillars);
  }, [radierAnalysis]);

  const addLineSupport = useCallback(() => {
    const newId = `V${(radierAnalysis.lineSupports.length + 1).toString().padStart(2, '0')}`;
    radierAnalysis.setLineSupports(prev => [...prev, { id: newId, x1: 0, y1: 0, x2: 1, y2: 1, support_type: "pinned" }]);
  }, [radierAnalysis]);

  const removeLineSupport = useCallback((id: string) => {
    radierAnalysis.setLineSupports(prev => prev.filter(s => s.id !== id));
  }, [radierAnalysis]);

  const updateLineSupport = useCallback((id: string, updates: any) => {
    radierAnalysis.setLineSupports(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
  }, [radierAnalysis]);

  const updateAreaLoad = useCallback((id: string, updates: any) => {
    radierAnalysis.setAreaLoads(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
  }, [radierAnalysis]);

  const applyGuidedPreset = useCallback((preset: any) => {
    radierAnalysis.setParams(prev => ({ ...prev, h: preset.h, kv: preset.kv }));
    projectState.addLog(`Preset aplicado: ${preset.name}`, "info");
  }, [radierAnalysis, projectState]);

  const updateKvSource = useCallback((id: string) => {
    const opt = KV_SOURCE_OPTIONS.find(o => o.id === id);
    if (opt) {
      radierAnalysis.setKvSource(id as any);
      radierAnalysis.setKvConfidence(opt.confidence);
    }
  }, [radierAnalysis]);

  const updateParam = useCallback((key: string, value: any) => {
    radierAnalysis.setParams(prev => ({ ...prev, [key]: value }));
  }, [radierAnalysis]);

  const estimateLoads = useCallback(() => {
    const preset = purposePresets.find(p => p.id === radierAnalysis.purposePresetId) || purposePresets[0];
    const estimatedQ = preset.q_kN_m2 * numPavimentos;
    updateParam("q", estimatedQ);
    setShowLoadToast(true);
    setTimeout(() => setShowLoadToast(false), 3000);
    projectState.addLog(`Carga estimada para ${numPavimentos} pavimentos: ${estimatedQ} kN/m²`, "info");
  }, [radierAnalysis.purposePresetId, numPavimentos, updateParam, projectState]);

  const runWindStabilityAnalysis = async () => {
    projectState.setLoading(true);
    projectState.addLog("Iniciando análise de estabilidade e vento...", "info");
    try {
      const res = await fetch(`${apiBaseUrl}/calculate/stability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...radierAnalysis.params, wind: frameAnalysis.windParams }),
      });
      const data = await res.json();
      if (data.success) {
        frameAnalysis.setStabilityResults(data.stability);
        frameAnalysis.setWindResults(data.wind);
        projectState.addLog("Análise de estabilidade concluída.", "success");
      }
    } finally {
      projectState.setLoading(false);
    }
  };

  return {
    ...projectState,
    ...radierAnalysis,
    ...frameAnalysis,
    apiOnline,
    apiChecking,
    memorialGeneratedAt,
    analysisMode,
    setAnalysisMode,
    optLogs,
    apiBaseUrl,
    showTerminal,
    setShowTerminal,
    selectedMember,
    setSelectedMember,
    numPavimentos,
    setNumPavimentos,
    showLoadToast,
    estimateLoads,
    
    // Derived state
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
    
    // Actions
    checkApiConnection,
    runAnalysis,
    runOptimization,
    runFrameAnalysis,
    handleBackToDashboard,
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
    KV_SOURCE_OPTIONS
  };
}
