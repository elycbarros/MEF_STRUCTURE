"use client";

import React, { useCallback, useMemo, useState } from "react";
import { AlertTriangle, BookOpen, BookText, Building2, CheckCircle2, Copy, Database, Download, FileText, Gauge, Layers3, Plus, PlugZap, Printer, RefreshCw, RotateCcw, ShieldCheck, StretchHorizontal, Trash2, XCircle } from "lucide-react";
import { fieldRisks, foundationTypes, knowledgeReferences, purposePresets, soilPresets } from "@/lib/radierKnowledge";
import { ExecutiveDecisionCard } from "@/components/dashboard/ExecutiveDecisionCard";
import { ReportView } from "@/components/ReportView";
import { MetricPill, RiskBadge, RiskDot } from "@/components/ui/StatusUI";
import { formatNumberBR, cn } from "@/lib/utils";
import { PillarEditor } from "@/components/PillarEditor";
import { HoleEditor, Hole } from "@/components/HoleEditor";
import Frame3DView from "@/components/Frame3DView";
import Structural3DView from "@/components/Structural3DView";
import ProfessionalDashboard from "@/components/ProfessionalDashboard";
import TerminalLogs from "@/components/TerminalLogs";
import MemberSectionView from "@/components/MemberSectionView";
import EffortDiagrams from "@/components/EffortDiagrams";
import { SpecialElementsView } from "@/components/SpecialElementsView";
import { WindStabilityView } from "@/components/WindStabilityView";
import { useProjectState } from "@/hooks/useProjectState";
import { useRadierAnalysis, type Pillar } from "@/hooks/useRadierAnalysis";
import { useFrameAnalysis } from "@/hooks/useFrameAnalysis";
import { buildFramePremiumPayload } from "@/lib/framePayloadBuilder";
import WelcomeScreen from "@/components/WelcomeScreen";
import { PhDEngineView } from "@/components/PhDEngineView";
import { VigaCrossView } from "@/components/VigaCrossView";
import { GuidedGeometryView } from "@/components/GuidedGeometryView";
import { TensionProView } from "@/components/TensionProView";
import { UfoStabilityView } from "@/components/UfoStabilityView";
import { MainHeader } from "@/components/MainHeader";
import { MainSidebar } from "@/components/MainSidebar";
import { SupportLocationSection } from "@/components/SupportLocationSection";
import { AcademicDashboard } from "@/components/AcademicDashboard";
import { AcademicBacklogView } from "@/components/AcademicBacklogView";
import { 
  asRecord, 
  asRecordArray, 
  asStringArray, 
  collectFileArtifacts, 
  formatBoolean, 
  formatMaybeNumber, 
  formatMaybePercent, 
  normalizeFrameDiagram, 
  parseLocaleNumberInput, 
  uniqueStrings 
} from "@/lib/formatters";
import { 
  buildFieldRiskSummary, 
  formatChecklistStatus, 
  formatDiagnosticConservatism, 
  formatFoundationClassification, 
  formatFoundationTriggerLevel 
} from "@/lib/foundationFormatters";

import {
  Activity,
  Settings,
  FileText as FileTextIcon,
  RefreshCw as RefreshCwIcon,
  Download as DownloadIcon,
  Zap,
  Maximize2,
  Info,
  ChevronRight,
  Layers,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layout,
  PlusCircle,
  X,
  Wind,
  Box,
  Link2,
  ChevronDown,
  ChevronUp
} from "lucide-react";

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function RebarCard({ title, required, adopted, suggestion, detail }: { title: string; required: number | null; adopted: number | null; suggestion?: string; detail?: string }) {
  const note = suggestion ?? detail;
  const ratio = required && adopted ? adopted / required : null;
  const ok = ratio !== null ? ratio >= 1.0 : null;
  return (
    <div className="rounded-2xl border border-[#e0e7ef] bg-white p-4">
      <p className="text-xs font-black uppercase tracking-wider text-[#6a7485]">{title}</p>
      <p className="mt-2 text-2xl font-black">{adopted !== null ? `${adopted.toFixed(2)}` : "--"} <span className="text-sm font-bold text-[#6a7485]">cm²/m</span></p>
      <p className="text-xs text-[#8a9ab0] mt-1">Calculado: {required !== null ? required.toFixed(2) : "--"} cm²/m</p>
      {ratio !== null && (
        <p className={`text-xs font-black mt-1 ${ok ? "text-[#1f8f56]" : "text-[#c52626]"}`}>
          η = {ratio.toFixed(2)} — {ok ? "ATENDE" : "NÃO ATENDE"}
        </p>
      )}
      {note && <p className="text-[11px] text-[#667085] mt-1 italic">{note}</p>}
    </div>
  );
}

function numberOr(v: unknown, fallback: number): number | null {
  const n = Number(v);
  return isFinite(n) ? n : (isFinite(fallback) ? fallback : null);
}

interface DeterministicResults {
  qsoil_max_kPa: number;
  mx_abs_max_kNm_m: number;
  w_max_mm: number;
}

interface MaturityScore {
  score_0_5: number;
}

interface MemorialSummary {
  [key: string]: unknown;
  checklist_profissional?: {
    status?: string;
    items?: Array<{ id?: string; description?: string; pass?: boolean }>;
  };
}

interface CalculateResponse {
  success: boolean;
  deterministic?: DeterministicResults;
  memorial?: MemorialSummary;
  maturity_score?: MaturityScore;
  master?: Record<string, unknown>;
  guided_context?: GuidedContext;
  field_risk_summary?: FieldRiskSummary;
  reinforcement_summary?: ReinforcementSummary;
  foundation_recommendation?: FoundationRecommendation;
  executive_decision?: Record<string, unknown>;
  didactic_guide_markdown?: string | null;
  detail?: string;
  frame_data?: any; // Novo campo para StrucPy
}

interface LineSupport {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  support_type: "pinned" | "fixed" | "spring";
  k_spring?: number;
}

type TabId = "dashboard" | "geometria" | "pilares" | "armadura" | "resultado" | "integracao" | "especiais" | "vento" | "vigas" | "vigacross" | "pilares_isolados" | "backlog";

type AnalysisMode = "guided" | "manual";
type RiskSeverity = "green" | "yellow" | "red";
type DiagnosticConservatism = "permissive" | "balanced" | "conservative";
type KvSource = "plate_load_test" | "settlement_backcalc" | "spt_correlation" | "table_reference" | "engineering_estimate";
type NumericParamKey = "Lx" | "Ly" | "h" | "kv" | "sigma_adm_kPa" | "q" | "fck" | "fyk";

interface GuidedContext {
  mode: AnalysisMode;
  foundation_type: string;
  purpose_preset: string;
  soil_preset: string;
  references: string[];
}

interface FieldRiskSummary {
  status: "green" | "yellow" | "red";
  selected: Array<{ id: string; label: string; severity: RiskSeverity; action: string }>;
  recommendations: string[];
}

interface ReinforcementSummary {
  status?: string;
  flexure?: Record<string, unknown>;
  punching?: Record<string, unknown>;
  serviceability?: Record<string, unknown>;
  detailing_guidance?: Record<string, unknown>;
  critical_zones?: Array<Record<string, unknown>>;
  notes?: string[];
}

interface FoundationRecommendation {
  classification?: string;
  executive_label?: string;
  decision_rank?: number;
  main_recommendation?: string;
  priority_actions?: string[];
  trigger_counts?: Record<string, unknown>;
  technical_level_counts?: Record<string, unknown>;
  diagnostic_conservatism?: Record<string, unknown>;
  input_policy?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
  triggers?: Array<Record<string, unknown>>;
  alternatives?: Array<Record<string, unknown>>;
  scope_note?: string;
}

const DIAGNOSTIC_CONSERVATISM_OPTIONS: Array<{
  id: DiagnosticConservatism;
  label: string;
  description: string;
}> = [
    {
      id: "balanced",
      label: "Equilibrado",
      description: "Faixa padrão para leitura preliminar sem afrouxar nem travar cedo demais.",
    },
    {
      id: "conservative",
      label: "Conservador",
      description: "Antecipa restrições e puxa os alertas para mais cedo.",
    },
    {
      id: "permissive",
      label: "Permissivo",
      description: "Tolera proximidade maior dos limites antes de escalar o diagnóstico.",
    },
  ];

const KV_SOURCE_OPTIONS: Array<{
  id: KvSource;
  label: string;
  confidence: number;
  description: string;
}> = [
    {
      id: "plate_load_test",
      label: "Prova de carga",
      confidence: 0.9,
      description: "Valor medido em campo, ainda dependente de escala e representatividade.",
    },
    {
      id: "settlement_backcalc",
      label: "Retroanálise de recalque",
      confidence: 0.8,
      description: "Estimado por recalque observado/calculado para fundação real.",
    },
    {
      id: "spt_correlation",
      label: "Correlação SPT",
      confidence: 0.65,
      description: "Útil para anteprojeto, exige faixa de sensibilidade.",
    },
    {
      id: "table_reference",
      label: "Tabela/literatura",
      confidence: 0.5,
      description: "Referência preliminar; documentar fonte e intervalo.",
    },
    {
      id: "engineering_estimate",
      label: "Estimativa inicial",
      confidence: 0.35,
      description: "Premissa fraca para decisão executiva sem validação.",
    },
  ];

const samplePillars: Pillar[] = [
  { id: "P01", x: 4.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P02", x: 16.0, y: 4.0, p_kN: 3500.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P03", x: 28.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P04", x: 4.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P05", x: 16.0, y: 12.0, p_kN: 5200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  { id: "P06", x: 28.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
];

const sampleBeams: LineSupport[] = [
  { id: "V01", x1: 0, y1: 0, x2: 32.5, y2: 0, support_type: "pinned" },
  { id: "V02", x1: 0, y1: 24.8, x2: 32.5, y2: 24.8, support_type: "pinned" },
];


export default function Home() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_RADIER_API_URL ?? "http://127.0.0.1:8000";

  const [selectedMode, setSelectedMode] = useState<"academic" | "professional" | null>(null);

  const {
    activeTab, setActiveTab,
    loading, setLoading,
    statusMessage, setStatusMessage,
    logs, addLog,
    systemType, setSystemType,
    docMeta, setDocMeta,
    tabs
  } = useProjectState(selectedMode);

  const {
    params, setParams,
    pillars, setPillars,
    lineSupports, setLineSupports,
    holes, setHoles,
    results, setResults,
    foundationTypeId, setFoundationTypeId,
    purposePresetId, setPurposePresetId,
    soilPresetId, setSoilPresetId,
    diagnosticConservatism, setDiagnosticConservatism,
    kvSource, setKvSource,
    kvConfidence, setKvConfidence,
    ignorePillars, setIgnorePillars,
    selectedFieldRiskIds, setSelectedFieldRiskIds
  } = useRadierAnalysis();

  const {
    windParams, setWindParams,
    frameResults, setFrameResults,
    stabilityResults, setStabilityResults,
    windResults, setWindResults
  } = useFrameAnalysis();

  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [apiChecking, setApiChecking] = useState(false);
  const [isProfessionalMode, setIsProfessionalMode] = useState(true);
  const [memorialGeneratedAt, setMemorialGeneratedAt] = useState<Date | null>(null);
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>("guided");

  const [selectedMember, setSelectedMember] = useState<number | null>(null);
  const [optLogs, setOptLogs] = useState<any[]>([]);

  const runWindStabilityAnalysis = async () => {
    setLoading(true);
    setStatusMessage("Calculando Vento e Estabilidade Global...");
    try {
      const response = await fetch(`${apiBaseUrl}/calculate/wind-stability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(windParams),
      });
      const data = await response.json();
      if (data.success) {
        setWindResults(data.wind);
        setStabilityResults(data.stability);
        setStatusMessage("Sucesso! Vento e Estabilidade calculados.");
      } else {
        setStatusMessage("Erro no cálculo de vento.");
      }
    } catch (err) {
      console.error(err);
      setStatusMessage("Erro na conexão com API.");
    } finally {
      setLoading(false);
    }
  };

  const runUnifiedAnalysis = async () => {
    setLoading(true);
    addLog("Iniciando Análise Global Unificada (Pórtico + Radier)...", "info");
    addLog("Sincronizando rigidez do solo com a superestrutura...", "info");
    try {
      const response = await fetch(`${apiBaseUrl}/calculate_v2_unified`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Lx: params.Lx,
          Ly: params.Ly,
          h: params.h,
          kv: params.kv,
          fck: params.fck,
          pillars: pillars.map(p => ({ id: p.id, x: p.x, y: p.y, bx: p.bx, by: p.by })),
          pillar_height: (params as any).pillar_height || 3.0,
          q: params.q,
          num_floors: Math.ceil(windParams.altura_total / 3) || 10,
          wind_v0: windParams.v0,
          wind_categoria: windParams.categoria,
          wind_f1_hz: windParams.f1,
          wind_zeta: windParams.zeta,
          wind_is_dynamic: windParams.is_dynamic
        })
      });
      const data = await response.json();
      if (data.success) {
        setResults(data.radier);
        setFrameResults(data.frame);
        setStabilityResults(data.stability);
        addLog("Convergência global atingida. Resultados sincronizados.", "success");
        setStatusMessage("Sucesso! Análise Unificada Concluída.");
        setActiveTab("dashboard");
      } else {
        addLog(`Kernel rejeitou a análise unificada: ${data.detail}`, "error");
      }
    } catch (err) {
      console.error(err);
      addLog("Erro na conexão com API de análise global.", "error");
      setStatusMessage("Erro na conexão com API.");
    } finally {
      setLoading(false);
    }
  };

  const memorial = (results?.memorial ?? {}) as Record<string, unknown>;
  const checklistProf = asRecord(memorial.checklist_profissional);
  const checklistItems = asRecordArray(checklistProf.items);
  const benchmark = asRecord(memorial.benchmark_evidences);
  const benchmarkChecks = asRecordArray(benchmark.checks);
  const structuralChecks = asRecord(memorial.verificacoes_estruturais);
  const serviceChecks = asRecord(memorial.verificacoes_de_servico);
  const reinforcementSummary = asRecord(results?.reinforcement_summary);
  const reinforcementFlexure = asRecord(reinforcementSummary.flexure ?? structuralChecks.flexao);
  const reinforcementPunching = asRecord(reinforcementSummary.punching ?? structuralChecks.puncao);
  const reinforcementService = asRecord(reinforcementSummary.serviceability);
  const reinforcementNotes = asStringArray(reinforcementSummary.notes);
  const reinforcementCriticalZones = asRecordArray(reinforcementSummary.critical_zones);
  const detailingGuidance = asRecord(reinforcementSummary.detailing_guidance ?? memorial.detalhamento_final);
  const foundationRecommendation = asRecord(results?.foundation_recommendation);
  const executiveDecision = asRecord(results?.executive_decision);
  const foundationTriggers = asRecordArray(foundationRecommendation.triggers);
  const foundationAlternatives = asRecordArray(foundationRecommendation.alternatives);
  const foundationPriorityActions = asStringArray(foundationRecommendation.priority_actions);
  const foundationMetrics = asRecord(foundationRecommendation.metrics);
  const foundationTechnicalCounts = asRecord(foundationRecommendation.technical_level_counts);
  const foundationDiagnosticProfile = asRecord(foundationRecommendation.diagnostic_conservatism);
  const foundationInputPolicy = asRecord(foundationRecommendation.input_policy);
  const modeRead = asRecord(memorial.leitura_orientada_por_modo);
  const modeAssessment = asRecord(memorial.avaliacao_tecnica_por_modo);
  const researchNotes = asRecord(memorial.pesquisa_e_melhoria);
  const artifactFiles = collectFileArtifacts(results?.master);
  const selectedFoundationType = foundationTypes.find((item) => item.id === foundationTypeId) ?? foundationTypes[0];
  const selectedPurposePreset = purposePresets.find((item) => item.id === purposePresetId) ?? purposePresets[0];
  const selectedSoilPreset = soilPresets.find((item) => item.id === soilPresetId) ?? soilPresets[0];
  const selectedKvSource = KV_SOURCE_OPTIONS.find((item) => item.id === kvSource) ?? KV_SOURCE_OPTIONS[0];
  const selectedFieldRisks = useMemo(
    () => fieldRisks.filter((risk) => selectedFieldRiskIds.includes(risk.id)),
    [selectedFieldRiskIds],
  );
  const localRiskSummary = useMemo(
    () => buildFieldRiskSummary(selectedFieldRisks, selectedSoilPreset.risk),
    [selectedFieldRisks, selectedSoilPreset.risk],
  );
  const apiRiskSummary = results?.field_risk_summary ?? null;
  const displayedRiskSummary = useMemo(() => apiRiskSummary ?? localRiskSummary, [apiRiskSummary, localRiskSummary]);

  const maturityScore = results?.maturity_score?.score_0_5 ?? null;
  const checklistStatus = String(checklistProf.status ?? "Sem resultado");
  const checklistStatusLabel = formatChecklistStatus(checklistStatus);
  const recommendedActions = uniqueStrings([
    ...asStringArray(modeRead.recommended_actions),
    ...asStringArray(modeAssessment.executive_recommendations),
    ...asStringArray(researchNotes.oportunidades_de_melhoria),
  ]);

  const totals = useMemo(() => {
    const pillarCount = pillars.length;
    const totalLoad = pillars.reduce((acc, p) => acc + (Number.isFinite(p.p_kN) ? p.p_kN : 0), 0);
    return { pillarCount, totalLoad };
  }, [pillars]);

  const updateParam = (key: NumericParamKey, value: number) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const applyGuidedPreset = () => {
    setParams((prev) => ({
      ...prev,
      h: selectedPurposePreset.h_m,
      q: selectedPurposePreset.q_kN_m2,
      kv: selectedSoilPreset.kv_kN_m3,
      sigma_adm_kPa: selectedSoilPreset.sigma_adm_kPa,
    }));
    setKvSource("table_reference");
    setKvConfidence(0.5);
    setStatusMessage("Preset guiado aplicado aos parâmetros.");
  };

  const updateKvSource = (source: KvSource) => {
    const selected = KV_SOURCE_OPTIONS.find((item) => item.id === source) ?? KV_SOURCE_OPTIONS[0];
    setKvSource(source);
    setKvConfidence(selected.confidence);
  };

  const toggleFieldRisk = (id: string) => {
    setSelectedFieldRiskIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const updateDocMeta = (key: keyof typeof docMeta, value: string) => {
    setDocMeta((prev) => ({ ...prev, [key]: value }));
  };

  const updatePillar = (index: number, key: string, value: string) => {
    setPillars((prev) =>
      prev.map((item, i) => {
        if (i !== index) return item;
        if (key === "id") return { ...item, id: value };
        if (key === "support_type") return { ...item, support_type: value };
        const parsed = parseLocaleNumberInput(value);
        if (parsed === null) return item;
        return { ...item, [key]: parsed };
      }),
    );
  };

  const addPillar = () => {
    const id = `P${String(pillars.length + 1).padStart(2, "0")}`;
    setPillars((prev) => [...prev, { id, x: 5, y: 5, p_kN: 1500, bx: 0.5, by: 0.5, support_type: "pinned" }]);
    setStatusMessage("Pilar adicionado.");
  };

  const removePillar = (index: number) => {
    setPillars((prev) => prev.filter((_, i) => i !== index));
    setStatusMessage("Pilar removido.");
  };

  const updateLineSupport = (index: number, key: string, value: string) => {
    setLineSupports((prev) =>
      prev.map((item, i) => {
        if (i !== index) return item;
        if (key === "id") return { ...item, id: value };
        if (key === "support_type") return { ...item, support_type: value as any };
        const parsed = parseLocaleNumberInput(value);
        if (parsed === null) return item;
        return { ...item, [key]: parsed };
      }),
    );
  };

  const addLineSupport = () => {
    const id = `V${String(lineSupports.length + 1).padStart(2, "0")}`;
    setLineSupports((prev) => [...prev, { id, x1: 0, y1: 0, x2: params.Lx, y2: 0, support_type: "pinned" }]);
    setStatusMessage("Viga (apoio em linha) adicionada.");
  };

  const removeLineSupport = (index: number) => {
    setLineSupports((prev) => prev.filter((_, i) => i !== index));
    setStatusMessage("Viga removida.");
  };

  const restoreSamplePillars = () => {
    setPillars(samplePillars);
    if (systemType === "laje") {
      setLineSupports(sampleBeams);
    }
    setStatusMessage("Geometria de exemplo restaurada.");
  };

  const checkApiConnection = async () => {
    setApiChecking(true);
    try {
      const response = await fetch(`${apiBaseUrl}/`, { method: "GET" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setApiOnline(true);
      setStatusMessage("API conectada com sucesso.");
    } catch (error) {
      setApiOnline(false);
      const message = error instanceof Error ? error.message : "Falha na conexão";
      setStatusMessage(`API indisponível: ${message}`);
    } finally {
      setApiChecking(false);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    addLog("Solicitando análise MEF de radier ao kernel estrutural...", "info");
    try {
      const response = await fetch(`${apiBaseUrl}/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...params,
          kv: params.kv * 1000,
          q: params.q * 1000,
          system_type: systemType,
          pillars,
          line_supports: lineSupports,
          holes,
          analysis_mode: analysisMode,
          foundation_type: foundationTypeId,
          purpose_preset_id: purposePresetId,
          soil_preset_id: soilPresetId,
          field_risk_ids: selectedFieldRiskIds,
          diagnostic_conservatism: diagnosticConservatism,
          ignore_pillars: ignorePillars,
          soil_parameter_context: {
            kv_source: kvSource,
            kv_source_label: selectedKvSource.label,
            kv_confidence: kvConfidence,
          },
          guided_context: {
            mode: analysisMode,
            foundation_type: selectedFoundationType.name,
            purpose_preset: selectedPurposePreset.name,
            soil_preset: selectedSoilPreset.name,
            references: knowledgeReferences,
          },
        }),
      });

      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
          const payload = (await response.json()) as { detail?: string };
          if (payload.detail) detail = `${detail}: ${payload.detail}`;
        } catch {
          // fallback com status já definido
        }
        addLog(`Erro crítico na análise: ${detail}`, "error");
        throw new Error(detail);
      }

      const payload = (await response.json()) as CalculateResponse;
      if (!payload.success) {
        addLog(`Kernel estrutural rejeitou os dados: ${payload.detail}`, "error");
        throw new Error(payload.detail ?? "Falha no cálculo");
      }
      setResults(payload);
      setActiveTab("resultado");
      addLog("Análise MEF concluída. Malha de elementos finitos gerada.", "success");
      setStatusMessage("Análise concluída com sucesso.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Falha ao executar análise";
      addLog(`Erro na análise: ${message}`, "error");
      setStatusMessage(`Erro: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const runFrameAnalysis = async () => {
    setLoading(true);
    setStatusMessage("Executando pórtico 3D Premium V4.0...");
    try {
      const framePayload = buildFramePremiumPayload(pillars, params, windParams);
      const response = await fetch(`${apiBaseUrl}/calculate/frame`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(framePayload),
      });

      if (!response.ok) throw new Error("Falha na análise de pórtico");
      const payload = await response.json();
      if (!payload.success) throw new Error(payload.detail || payload.error || "Falha no motor premium");
      setFrameResults(payload);
      setActiveTab("resultado");
      addLog(`Pórtico V4.0 concluído: γz = ${payload.gamma_z ?? "n/d"} (${payload.stability_class ?? "sem classe"})`, "success");
      setStatusMessage("Análise de pórtico 3D Premium concluída.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Falha";
      addLog(`Erro no pórtico V4.0: ${message}`, "error");
      setStatusMessage(`Erro: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    setLoading(true);
    setOptLogs([]);
    setStatusMessage("Executando auto-dimensionamento iterativo...");
    try {
      const response = await fetch(`${apiBaseUrl}/optimize_design`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...params,
          kv: params.kv * 1000,
          q: params.q * 1000,
          pillars,
          analysis_mode: analysisMode,
          system_type: systemType,
          line_supports: lineSupports,
          foundation_type: foundationTypeId,
          purpose_preset_id: purposePresetId,
          soil_preset_id: soilPresetId,
          field_risk_ids: selectedFieldRiskIds,
          diagnostic_conservatism: diagnosticConservatism,
          ignore_pillars: ignorePillars,
          soil_parameter_context: {
            kv_source: kvSource,
            kv_source_label: selectedKvSource.label,
            kv_confidence: kvConfidence,
          },
        }),
      });

      if (!response.ok) throw new Error("Falha no Otimizador");

      const payload = await response.json();
      if (!payload.success) throw new Error(payload.message || "Falha no calculo");

      if (payload.optimized) {
        setParams(prev => ({ ...prev, h: payload.recommended_h }));
        setStatusMessage(`Auto-dimensionado com sucesso: h = ${payload.recommended_h}m (${payload.foundation_type})`);
      } else {
        setStatusMessage(`Auto-design não resolveu: ${payload.message}`);
      }

      if (payload.optimization_history) {
        setOptLogs(payload.optimization_history);
      }

      if (payload.result) {
        setResults(payload.result);
        setActiveTab("resultado");
      }

    } catch (error) {
      setStatusMessage(`Erro: ${error instanceof Error ? error.message : "Desconhecido"}`);
    } finally {
      setLoading(false);
    }
  };

  const [numPavimentos, setNumPavimentos] = useState(1);
  const estimateLoads = async () => {
    setStatusMessage("Estimando cargas (NBR 6120)...");
    try {
      let tipoUso = selectedPurposePreset.name.toLowerCase();
      if (tipoUso.includes("resid")) tipoUso = "residencial";
      else if (tipoUso.includes("comerc") || tipoUso.includes("loj")) tipoUso = "comercial";
      else if (tipoUso.includes("escrit")) tipoUso = "escritorio";
      else if (tipoUso.includes("gara") || tipoUso.includes("estacion")) tipoUso = "garagem";
      else tipoUso = "comercial"; // default if not matched

      const response = await fetch(`${apiBaseUrl}/estimate_loads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tipo_uso: tipoUso,
          num_pavimentos: numPavimentos
        })
      });
      const payload = await response.json();
      if (payload.success) {
        setParams(prev => ({ ...prev, q: payload.estimated_q_kPa }));
        setStatusMessage(`Carga estimada para ${numPavimentos} pav(s) de uso ${tipoUso}: ${payload.estimated_q_kPa} kN/m²`);
      }
    } catch (e) {
      setStatusMessage("Erro ao estimar cargas.");
    }
  };

  const copySummary = async () => {
    const summary = {
      parametros: params,
      contexto_guiado: {
        mode: analysisMode,
        foundation_type: selectedFoundationType.name,
        purpose_preset: selectedPurposePreset.name,
        soil_preset: selectedSoilPreset.name,
        diagnostic_conservatism: diagnosticConservatism,
        ignore_pillars: ignorePillars,
        soil_parameter_context: {
          kv_source: kvSource,
          kv_source_label: selectedKvSource.label,
          kv_confidence: kvConfidence,
        },
      },
      riscos_de_campo: displayedRiskSummary,
      total_pilares: totals.pillarCount,
      carga_total_kN: totals.totalLoad,
      deterministic: results?.deterministic ?? null,
      maturity_score: results?.maturity_score ?? null,
      checklist_status: checklistStatus,
      diagnostico_fundacao: results?.foundation_recommendation ?? null,
      decisao_executiva: results?.executive_decision ?? null,
      recomendacoes: recommendedActions,
      checklist_itens: checklistItems,
      benchmark: benchmarkChecks,
    };
    await navigator.clipboard.writeText(JSON.stringify(summary, null, 2));
    setStatusMessage("Resumo copiado para área de transferência.");
  };

  const downloadDidacticGuide = () => {
    const content = results?.didactic_guide_markdown;
    if (!content) {
      setStatusMessage("Execute a análise para gerar o guia didático.");
      return;
    }
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "guia_didatico_radier.md";
    anchor.click();
    URL.revokeObjectURL(url);
    setStatusMessage("Guia didático exportado em Markdown.");
  };

  const downloadResults = () => {
    if (!results) {
      setStatusMessage("Execute a análise antes de exportar.");
      return;
    }
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "radier_resultado.json";
    anchor.click();
    URL.revokeObjectURL(url);
    setStatusMessage("Resultado exportado em JSON.");
  };

  const buildCurrentMemorial = useCallback(
    (generatedAt: Date) => {
      if (!results) return "";
      // buildCurrentMemorial retorna o HTML do memorial com dados do projeto atual
      const exec = (results.executive_decision ?? {}) as Record<string, unknown>;
      const memorial = (results.memorial ?? {}) as Record<string, unknown>;
      const geoVerif = asRecord(memorial.verificacoes_geotecnicas);
      const structVerif = asRecord(memorial.verificacoes_estruturais);
      const serviceVerif = asRecord(memorial.verificacoes_de_servico);
      const flexure = asRecord(structVerif.flexao);
      const punching = asRecord(structVerif.puncao);

      const fmt = (v: unknown, d = 2) =>
        typeof v === "number" && isFinite(v) ? v.toFixed(d) : "N/D";

      return `
        <h1 style="font-size:20px;margin:0 0 4px">${escapeHtml(docMeta.obra)}</h1>
        <p class="meta">${escapeHtml(docMeta.local)} | Emissão: ${escapeHtml(docMeta.emissao)} | Rev: ${escapeHtml(docMeta.revisao)}</p>
        <p class="meta">Responsável: ${escapeHtml(docMeta.responsavel)} — ${escapeHtml(docMeta.registro)}</p>
        <p class="meta">Gerado em: ${generatedAt.toLocaleString("pt-BR")}</p>
        <h2>1. Decisão Executiva</h2>
        <p><strong>${String(exec.executive_label ?? "N/D")}</strong> | Go/No-Go: ${String(exec.go_no_go ?? "N/D")}</p>
        <p>${escapeHtml(String(exec.main_recommendation ?? "N/D"))}</p>
        <h2>2. Dados de Entrada</h2>
        <ul>
          <li>Geometria: ${fmt(params.Lx)} m × ${fmt(params.Ly)} m | h = ${fmt(params.h, 3)} m</li>
          <li>fck = ${fmt(params.fck, 0)} MPa | fyk = ${fmt(params.fyk, 0)} MPa</li>
          <li>kv = ${fmt(params.kv, 0)} kN/m³ | σadm = ${fmt(params.sigma_adm_kPa, 0)} kPa</li>
        </ul>
        <h2>3. Verificações Geotécnicas</h2>
        <ul>
          <li>Pressão média: ${fmt(geoVerif.pressao_media_kPa)} kPa</li>
          <li>Pressão máxima: ${fmt(geoVerif.pressao_max_modelo_kPa)} kPa ≤ ${fmt(geoVerif.tensao_admissivel_kPa)} kPa → ${geoVerif.atende_pressao_max_modelo ? "ATENDE" : "NÃO ATENDE"}</li>
        </ul>
        <h2>4. Armadura</h2>
        <ul>
          <li>Asx sup: ${fmt(flexure.Asx_top_adot_max_cm2_m)} cm²/m | Asy sup: ${fmt(flexure.Asy_top_adot_max_cm2_m)} cm²/m</li>
          <li>Asx inf: ${fmt(flexure.Asx_bottom_adot_max_cm2_m)} cm²/m | Asy inf: ${fmt(flexure.Asy_bottom_adot_max_cm2_m)} cm²/m</li>
        </ul>
        <h2>5. Punção (NBR 6118)</h2>
        <ul>
          <li>τsd = ${fmt(punching.tau_sd, 3)} MPa | τrd1 = ${fmt(punching.tau_rd1, 3)} MPa | η = ${fmt(punching.ratio_max, 3)} → ${punching.atende ? "ATENDE" : "NÃO ATENDE"}</li>
        </ul>
        <h2>6. Recalques</h2>
        <ul>
          <li>w_máx = ${fmt(serviceVerif.w_max_mm)} mm | w_dif = ${fmt(serviceVerif.w_diff_mm)} mm</li>
        </ul>
      `;
    },
    [
      analysisMode,
      apiBaseUrl,
      diagnosticConservatism,
      ignorePillars,
      displayedRiskSummary,
      docMeta,
      params,
      pillars,
      results,
      kvSource,
      kvConfidence,
      selectedKvSource.label,
      selectedFoundationType.name,
      selectedPurposePreset.name,
      selectedSoilPreset.name,
    ],
  );

  const memorialMathHtml = useMemo(() => {
    if (!results || !memorialGeneratedAt) return "";
    return buildCurrentMemorial(memorialGeneratedAt);
  }, [buildCurrentMemorial, memorialGeneratedAt, results]);

  const generateMemorial = () => {
    if (!results) {
      setStatusMessage("Execute a análise antes de gerar o memorial.");
      return;
    }
    const generatedAt = new Date();
    setMemorialGeneratedAt(generatedAt);
    setStatusMessage("Memorial gerado com sucesso.");
  };

  const downloadMemorial = () => {
    if (!memorialMathHtml) {
      setStatusMessage("Gere o memorial antes de baixar.");
      return;
    }
    const blob = new Blob([memorialMathHtml], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "memorial_calculo_radier.html";
    anchor.click();
    URL.revokeObjectURL(url);
    setStatusMessage("Memorial baixado em .html.");
  };

  const printMemorial = () => {
    if (!memorialMathHtml) {
      setStatusMessage("Gere o memorial antes de imprimir.");
      return;
    }
    const printWindow = window.open("", "_blank", "width=1100,height=800");
    if (!printWindow) {
      setStatusMessage("Não foi possível abrir a janela de impressão.");
      return;
    }
    const html = `<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <title>Memorial de Cálculo - Radier</title>
    <style>
      body { font-family: "Times New Roman", serif; margin: 20px; color: #0f172a; line-height: 1.35; }
      h1 { font-size: 24px; margin: 0 0 6px 0; }
      h2 { margin: 18px 0 8px 0; font-size: 18px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; }
      .meta { font-family: Arial, sans-serif; font-size: 12px; color: #334155; margin-bottom: 12px; }
      .eq { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; margin: 8px 0; }
      .eq-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
      .eq-index { font-family: Arial, sans-serif; font-size: 12px; font-weight: 700; color: #0f172a; }
      .eq-norm { font-family: Arial, sans-serif; font-size: 11px; color: #475569; text-transform: uppercase; letter-spacing: .03em; }
      .eq-title { font-family: Arial, sans-serif; font-size: 12px; text-transform: uppercase; color: #475569; margin-bottom: 4px; font-weight: 700; }
      .eq-formula { font-size: 18px; margin: 2px 0; }
      .eq-sub { font-size: 15px; color: #1e293b; }
      .eq-res { font-size: 16px; font-weight: 700; margin-top: 3px; }
      ul { margin: 6px 0 10px 20px; }
      li { margin: 3px 0; }
      .print-footer { margin-top: 24px; border-top: 1px solid #cbd5e1; padding-top: 10px; font-family: Arial, sans-serif; font-size: 11px; color: #334155; }
      .sign-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 10px; }
      .sign-box { border-top: 1px solid #64748b; padding-top: 6px; min-height: 42px; }
      @media print {
        body { margin: 12mm; }
        .print-footer { position: fixed; left: 12mm; right: 12mm; bottom: 8mm; background: #fff; }
      }
    </style>
  </head>
  <body>
    ${memorialMathHtml}
    <div class="print-footer">
      <div>Revisão: ${escapeHtml(docMeta.revisao)} | Emissão: ${escapeHtml(docMeta.emissao)} | Local: ${escapeHtml(docMeta.local)}</div>
      <div class="sign-row">
        <div class="sign-box">
          ${escapeHtml(docMeta.responsavel)}<br />
          ${escapeHtml(docMeta.registro)}
        </div>
        <div class="sign-box">
          Aprovador / Coordenador Técnico
        </div>
      </div>
    </div>
    <script>
      window.onload = function () { window.print(); };
    </script>
  </body>
</html>`;
    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
    setStatusMessage("Janela de impressão aberta. Você pode salvar em PDF.");
  };

  if (!selectedMode) {
    return (
      <WelcomeScreen
        onSelectMode={(mode) => {
          setSelectedMode(mode);
          setIsProfessionalMode(mode === "professional");
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
        />

        <div className="mt-8 grid grid-cols-12 gap-8">
          {selectedMode !== "academic" && (
            <MainSidebar
              tabs={tabs}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              theme={isProfessionalMode ? "professional" : "academic"}
            />
          )}

          <section className={cn(
            "col-span-12 rounded-[40px] border p-8 transition-all duration-700 shadow-2xl",
            isProfessionalMode 
              ? "bg-[#16191f] border-white/5 shadow-blue-900/10" 
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
                        onClick={() => setIsProfessionalMode(false)}
                        className={cn(
                          "px-3 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all",
                          !isProfessionalMode ? "bg-white text-[#1a1c1e] shadow-sm" : "text-[#6a7485]"
                        )}
                      >
                        Lab Mode
                      </button>
                      <button
                        onClick={() => setIsProfessionalMode(true)}
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

                {isProfessionalMode && results ? (
                  <ProfessionalDashboard memorial={results.memorial} config={params} mode={selectedMode ?? "professional"} />
                ) : (
                  <>
                    {selectedMode === "academic" ? (
                      <AcademicDashboard
                        setActiveTab={setActiveTab}
                        setSystemType={setSystemType}
                      />
                    ) : (
                      <div className="space-y-6">
                        <div className="grid gap-4 md:grid-cols-4">
                          <div className="rounded-2xl border-2 border-[#f4f8ff] bg-[#f4f8ff]/50 p-4 shadow-sm">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[#6a7485]">Lajes Isoladas</p>
                            <p className="mt-2 text-2xl font-black text-[#1a1c1e]">{systemType === "laje" ? "Ativo" : "--"}</p>
                            <p className="text-[10px] font-bold text-[#8a9ab0] mt-1">Análise de Flechas</p>
                          </div>
                          <div className="rounded-2xl border-2 border-[#eefbf3] bg-[#eefbf3]/50 p-4 shadow-sm">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[#5a7d68]">Radier Isolado</p>
                            <p className="mt-2 text-2xl font-black text-[#1a1c1e]">{systemType === "radier" ? "Ativo" : "--"}</p>
                            <p className="text-[10px] font-bold text-[#8a9ab0] mt-1">Análise de Solo</p>
                          </div>
                          <div className="rounded-2xl border-2 border-[#fff6ea] bg-[#fff6ea]/50 p-4 shadow-sm">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[#8c6f45]">Vigas Isoladas</p>
                            <p className="mt-2 text-2xl font-black text-[#1a1c1e]">OK</p>
                            <p className="text-[10px] font-bold text-[#8a9ab0] mt-1">NBR 6118 (Flexão)</p>
                          </div>
                          <div className="rounded-2xl border-2 border-[#f3f4f6] bg-[#f3f4f6]/50 p-4 shadow-sm">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[#4b5563]">Pilares Isolados</p>
                            <p className="mt-2 text-2xl font-black text-[#1a1c1e]">Auditado</p>
                            <p className="text-[10px] font-bold text-[#8a9ab0] mt-1">NBR 6118 (Esbeltez)</p>
                          </div>
                        </div>
                        <div className="rounded-2xl border border-[#eceef3] bg-white p-4">
                          <p className="text-sm font-semibold text-[#5f6470]">Checklist Profissional</p>
                          <p className="mt-2 text-lg font-bold">{checklistStatusLabel}</p>
                        </div>
                        <div className="grid gap-4 lg:grid-cols-2">
                          <div className="rounded-2xl border border-[#eceef3] bg-white p-4">
                            <div className="flex items-center justify-between gap-3">
                              <p className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Contexto guiado</p>
                              <RiskBadge severity={displayedRiskSummary.status} />
                            </div>
                            <div className="mt-3 grid gap-2 text-sm font-semibold text-[#374151]">
                              <p>Tipo: <strong>{selectedFoundationType.name}</strong></p>
                              <p>Finalidade: <strong>{selectedPurposePreset.name}</strong></p>
                              {systemType === "radier" && (
                                <p>Solo: <strong>{selectedSoilPreset.name}</strong></p>
                              )}
                            </div>
                          </div>
                          <div className="rounded-2xl border border-[#eceef3] bg-white p-4">
                            <p className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Base de conhecimento</p>
                            <ul className="mt-3 space-y-2 text-sm font-semibold text-[#4b5563]">
                              {knowledgeReferences.map((item) => (
                                <li key={item} className="flex gap-2">
                                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-none text-[#0f766e]" />
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
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

            {activeTab === "geometria" && (
              <GuidedGeometryView
                mode={selectedMode}
                systemType={systemType}
                setSystemType={setSystemType}
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
                holes={holes}
                setHoles={setHoles}
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

            {activeTab === "pilares" && (
              <SupportLocationSection
                pillars={pillars}
                addPillar={addPillar}
                removePillar={removePillar}
                updatePillar={updatePillar}
                restoreSamplePillars={restoreSamplePillars}
                lineSupports={lineSupports}
                addLineSupport={addLineSupport}
                removeLineSupport={removeLineSupport}
                updateLineSupport={updateLineSupport}
                systemType={systemType}
                params={params}
              />
            )}

            {activeTab === "armadura" && (
              <div className="space-y-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black">Módulo de Armadura do Radier</h2>
                    <p className="mt-1 text-sm font-semibold text-[#667085]">
                      Resumo de flexão, mínimos, sugestões comerciais, punção e fissuração.
                    </p>
                  </div>
                  <span className="rounded-full bg-[#eefbf3] px-3 py-1 text-xs font-black uppercase text-[#166534]">
                    NBR 6118 + Wood-Armer simplificado
                  </span>
                </div>

                {!results && (
                  <div className="rounded-2xl border border-dashed border-[#d6deea] bg-[#fafbfd] p-6 text-sm font-semibold text-[#6b7280]">
                    Execute a análise para preencher o módulo de armadura.
                  </div>
                )}

                {results && (
                  <div className="space-y-5">
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                      <RebarCard
                        title="X inferior"
                        required={numberOr(reinforcementFlexure.Asx_bottom_req_max_cm2_m, NaN)}
                        adopted={numberOr(reinforcementFlexure.Asx_bottom_adot_max_cm2_m, NaN)}
                        detail={String(reinforcementFlexure.sugestao_x_inf ?? "--")}
                      />
                      <RebarCard
                        title="X superior"
                        required={numberOr(reinforcementFlexure.Asx_top_req_max_cm2_m, NaN)}
                        adopted={numberOr(reinforcementFlexure.Asx_top_adot_max_cm2_m, NaN)}
                        detail={String(reinforcementFlexure.sugestao_x_sup ?? "--")}
                      />
                      <RebarCard
                        title="Y inferior"
                        required={numberOr(reinforcementFlexure.Asy_bottom_req_max_cm2_m, NaN)}
                        adopted={numberOr(reinforcementFlexure.Asy_bottom_adot_max_cm2_m, NaN)}
                        detail={String(reinforcementFlexure.sugestao_y_inf ?? "--")}
                      />
                      <RebarCard
                        title="Y superior"
                        required={numberOr(reinforcementFlexure.Asy_top_req_max_cm2_m, NaN)}
                        adopted={numberOr(reinforcementFlexure.Asy_top_adot_max_cm2_m, NaN)}
                        detail={String(reinforcementFlexure.sugestao_y_sup ?? "--")}
                      />
                    </div>

                    <div className="grid gap-4 lg:grid-cols-3">
                      <div className="rounded-2xl border border-[#e5ebf4] bg-white p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Armadura mínima</h3>
                        <p className="mt-3 text-3xl font-black text-[#111827]">
                          {formatMaybeNumber(reinforcementFlexure.As_min_face_cm2_m)}
                          <span className="ml-1 text-sm font-bold text-[#667085]">cm²/m por face</span>
                        </p>
                        <p className="mt-2 text-sm font-semibold text-[#667085]">
                          Total mínimo: {formatMaybeNumber(reinforcementFlexure.As_min_total_cm2_m)} cm²/m.
                        </p>
                      </div>

                      <div className="rounded-2xl border border-[#e5ebf4] bg-white p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Punção</h3>
                        <p className="mt-3 text-3xl font-black text-[#111827]">
                          η = {formatMaybeNumber(reinforcementPunching.ratio_max)}
                        </p>
                        <p className="mt-2 text-sm font-semibold text-[#667085]">
                          Local crítico: {String(reinforcementPunching.critical_local ?? "--")} | Status: {formatBoolean(reinforcementPunching.atende)}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-[#e5ebf4] bg-white p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Fissuração</h3>
                        <p className="mt-3 text-sm font-semibold text-[#374151]">
                          X: {formatMaybeNumber(reinforcementService.wk_x_max_mm ?? serviceChecks.wk_x_max_mm)} mm
                        </p>
                        <p className="mt-1 text-sm font-semibold text-[#374151]">
                          Y: {formatMaybeNumber(reinforcementService.wk_y_max_mm ?? serviceChecks.wk_y_max_mm)} mm
                        </p>
                        <p className="mt-2 text-sm font-semibold text-[#667085]">
                          Limite: {formatMaybeNumber(reinforcementService.wk_limit_mm ?? serviceChecks.wk_limit_mm)} mm
                        </p>
                      </div>
                    </div>

                    <div className="grid gap-4 lg:grid-cols-2">
                      <div className="rounded-2xl border border-[#e5ebf4] bg-white p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Diretrizes de detalhamento</h3>
                        <ul className="mt-3 space-y-2 text-sm font-semibold text-[#4b5563]">
                          <li>Inferior: {String(detailingGuidance.armadura_inferior ?? "distribuir nas duas direções conforme momentos positivos")}</li>
                          <li>Superior: {String(detailingGuidance.armadura_superior ?? "reforçar sobre pilares, bordas e momentos negativos")}</li>
                          <li>Locais: {String(detailingGuidance.reforcos_locais ?? "avaliar punção, bordas e aberturas")}</li>
                        </ul>
                      </div>

                      <div className="rounded-2xl border border-[#e5ebf4] bg-[#f8fbff] p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Observações do módulo</h3>
                        <ul className="mt-3 space-y-2 text-sm font-semibold text-[#4b5563]">
                          {(reinforcementNotes.length ? reinforcementNotes : [
                            "Definir faixas, ancoragens, emendas e reforços no detalhamento executivo.",
                            "Sugestões comerciais são preliminares e devem ser revisadas pelo responsável técnico.",
                          ]).map((note) => (
                            <li key={note} className="flex gap-2">
                              <CheckCircle2 className="mt-0.5 h-4 w-4 flex-none text-[#0f766e]" />
                              <span>{note}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {reinforcementCriticalZones.length > 0 && (
                      <div className="rounded-2xl border border-[#e5ebf4] bg-white p-4">
                        <h3 className="text-sm font-black uppercase tracking-wider text-[#4d5360]">Faixas críticas para detalhamento</h3>
                        <div className="mt-3 grid gap-3 lg:grid-cols-3">
                          {reinforcementCriticalZones.map((zone, idx) => (
                            <div key={`critical-zone-${idx}`} className="rounded-xl bg-[#f7f9fd] p-3">
                              <div className="flex items-center justify-between gap-2">
                                <p className="text-sm font-black text-[#111827]">{String(zone.zone ?? "Região")}</p>
                                <span className={`rounded-full px-2 py-0.5 text-[11px] font-black uppercase ${String(zone.priority) === "alta" ? "bg-[#ffecec] text-[#b42318]" : "bg-[#fff7ed] text-[#9a3412]"}`}>
                                  {String(zone.priority ?? "média")}
                                </span>
                              </div>
                              <p className="mt-2 text-xs font-semibold text-[#667085]">{String(zone.guidance ?? "")}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {activeTab === "resultado" && (
              <div className="space-y-10">
                {frameResults && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
                      {[
                        { label: "Motor", value: String(frameResults.analysis_type ?? "V4.0"), sub: "Frame3DEngine" },
                        { label: "γz", value: Number(frameResults.gamma_z ?? 1).toFixed(3), sub: String(frameResults.stability_class ?? "N/D") },
                        { label: "Topo 1ª ordem", value: `${Number(frameResults.top_displacement_1st_order_mm ?? 0).toFixed(2)} mm`, sub: "deslocamento X" },
                        { label: "Topo 2ª ordem", value: `${Number(frameResults.top_displacement_2nd_order_mm ?? 0).toFixed(2)} mm`, sub: "P-Delta" },
                        { label: "Vento", value: String(frameResults.wind_loads_applied ?? 0), sub: "cargas nodais" },
                      ].map((item) => (
                        <div key={item.label} className="rounded-2xl border border-[#e5ebf4] bg-white p-4 shadow-sm">
                          <p className="text-[10px] font-black uppercase tracking-wider text-[#667085]">{item.label}</p>
                          <p className="mt-2 text-xl font-black text-[#111827]">{item.value}</p>
                          <p className="mt-1 text-[11px] font-bold text-[#8a9ab0]">{item.sub}</p>
                        </div>
                      ))}
                    </div>

                    {frameResults.stability_message && (
                      <div className="rounded-2xl border border-[#dbeafe] bg-[#eff6ff] p-4 text-sm font-bold text-[#1e3a8a]">
                        {frameResults.stability_message}
                      </div>
                    )}

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div className="h-[500px] rounded-apple bg-black/5 overflow-hidden border border-black/5 relative shadow-inner">
                        <div className="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-black/10 shadow-sm">
                          <p className="text-[10px] font-black uppercase tracking-wider text-apple-text">Modelo Analítico 3D</p>
                          <p className="text-[9px] font-bold text-apple-muted">Geometria do Pórtico Espacial Premium</p>
                        </div>
                        <Frame3DView
                          nodes={frameResults.model_3d?.nodes ?? []}
                          members={frameResults.model_3d?.members ?? []}
                          onSelectMember={setSelectedMember}
                        />
                      </div>
                      <div className="h-[500px] rounded-apple bg-white border border-black/5 shadow-sm p-6 flex flex-col">
                        <div className="mb-4">
                          <p className="text-[10px] font-black uppercase tracking-wider text-apple-text">Envelopes de Esforços</p>
                          <p className="text-[9px] font-bold text-apple-muted">Diagramas de Momentos e Cortantes</p>
                        </div>
                        {(() => {
                          const diagramData = normalizeFrameDiagram(frameResults, selectedMember ?? 0);
                          if (diagramData.length === 0) {
                            return (
                              <div className="flex flex-1 items-center justify-center rounded-2xl border border-dashed border-[#d9dfe9] bg-[#f8fafc] text-center text-xs font-bold text-[#667085]">
                                Diagramas de esforços serão ligados na próxima etapa do pórtico premium.
                              </div>
                            );
                          }
                          return (
                            <div className="grid flex-1 content-center gap-4">
                              <EffortDiagrams memberId={selectedMember ?? 0} data={diagramData} type="moment" unit="kNm" />
                              <EffortDiagrams memberId={selectedMember ?? 0} data={diagramData} type="shear" unit="kN" />
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  </div>
                )}

                {/* Modal de Detalhamento de Seção */}
                {selectedMember !== null && frameResults && (
                  <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
                    <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl animate-in zoom-in-95 duration-200">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-black text-apple-text">Detalhamento Técnico</h3>
                        <button
                          onClick={() => setSelectedMember(null)}
                          className="p-2 rounded-full hover:bg-black/5"
                        >
                          <X className="h-5 w-5" />
                        </button>
                      </div>

                      {(() => {
                        const member = frameResults.model_3d.members.find((m: any) => m.index === selectedMember);
                        const isBeam = member?.Type !== "Column";
                        const design = isBeam
                          ? frameResults.design.beams.find((b: any) => b.Beam === member?.index || b.id === member?.index)
                          : frameResults.design.pillars.find((p: any) => p.Column === member?.index || p.id === member?.index);

                        return (
                          <div className="space-y-6">
                            <MemberSectionView
                              b={member?.b / 10 || 20}
                              h={member?.d / 10 || 50}
                              as_top={design?.As_top || design?.As2 || 2.5}
                              as_bottom={design?.As_bottom || design?.As1 || design?.As || 3.8}
                              type={isBeam ? 'beam' : 'pillar'}
                              title={`${isBeam ? 'Viga' : 'Pilar'} ${selectedMember}`}
                            />

                            <div className="rounded-2xl bg-apple-bg p-4 space-y-2">
                              <div className="flex justify-between text-xs">
                                <span className="text-apple-muted">Material</span>
                                <span className="font-bold">C{params.fck} / CA-50</span>
                              </div>
                              <div className="flex justify-between text-xs">
                                <span className="text-apple-muted">Esforço Crítico</span>
                                <span className="font-bold">{isBeam ? `Mk = ${(design?.M_max || 0).toFixed(2)} kNm` : `Nd = ${(design?.Nd || 0).toFixed(2)} kN`}</span>
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
                />
              </div>
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
                  <div className="flex items-center gap-2 px-3 py-1 bg-black/5 rounded-full border border-black/5">
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

            {(activeTab === "especiais" || activeTab === "vigas" || activeTab === "pilares_isolados") && (
              <div className="space-y-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-[#1d1d1f]">
                      {activeTab === "vigas" ? "Dimensionamento de Vigas" : activeTab === "pilares_isolados" ? "Dimensionamento de Pilares" : "Elementos Especiais"}
                    </h2>
                    <p className="mt-1 text-sm font-semibold text-[#666a73]">
                      Cálculo analítico {activeTab === "especiais" ? "de escadas e reservatórios" : ""} conforme NBR 6118.
                    </p>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-black/5 rounded-full border border-black/5">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span className="text-[10px] font-black uppercase tracking-wider text-[#1d1d1f]">Solvers Ativos</span>
                  </div>
                </div>
                <SpecialElementsView
                  apiBaseUrl={apiBaseUrl}
                  type={activeTab === "vigas" ? "viga" : activeTab === "pilares_isolados" ? "pilar" : "reservatorio"}
                />
              </div>
            )}

            {activeTab === "vigacross" && (
              <VigaCrossView />
            )}

            {activeTab === "tensionpro" && (
              <TensionProView />
            )}

            {activeTab === "ufo" && (
              <UfoStabilityView />
            )}

            {activeTab === "integracao" && (
              <PhDEngineView
                apiBaseUrl={apiBaseUrl}
                config={params}
              />
            )}
          </section>
        </div>
      </div>
      <TerminalLogs logs={logs} isVisible={loading || logs.length > 0} />

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
