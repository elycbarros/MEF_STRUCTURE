import { useState } from "react";

export interface Pillar {
  id: string;
  x: number;
  y: number;
  p_kN: number;
  bx: number;
  by: number;
  support_type: string;
}

export interface LineSupport {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  support_type: string;
}

export interface Hole {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface AreaLoad {
  id: string;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  q_kN: number;
}

export type DiagnosticConservatism = "permissive" | "balanced" | "conservative";
export type RiskSeverity = "green" | "yellow" | "red";
export interface FieldRiskSummary {
  status: RiskSeverity;
  selected: Array<{ id: string; label: string; severity: RiskSeverity; action: string }>;
  recommendations: string[];
}
export type KvSource = "plate_load_test" | "settlement_backcalc" | "spt_correlation" | "table_reference" | "engineering_estimate";

export function useRadierAnalysis() {
  const [params, setParams] = useState({
    Lx: 32.5,
    Ly: 24.8,
    h: 1.15,
    kv: 22000,
    sigma_adm_kPa: 200,
    q: 140,
    fck: 30,
    fyk: 500,
    ssi_enabled: false,
  });

  const [pillars, setPillars] = useState<Pillar[]>([
    { id: "P01", x: 4.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
    { id: "P02", x: 16.0, y: 4.0, p_kN: 3500.0, bx: 0.5, by: 0.5, support_type: "pinned" },
    { id: "P03", x: 28.0, y: 4.0, p_kN: 2200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
    { id: "P04", x: 4.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
    { id: "P05", x: 16.0, y: 12.0, p_kN: 5200.0, bx: 0.5, by: 0.5, support_type: "pinned" },
    { id: "P06", x: 28.0, y: 12.0, p_kN: 3800.0, bx: 0.5, by: 0.5, support_type: "pinned" },
  ]);

  const [lineSupports, setLineSupports] = useState<LineSupport[]>([
    { id: "V01", x1: 0, y1: 0, x2: 32.5, y2: 0, support_type: "pinned" },
    { id: "V02", x1: 0, y1: 24.8, x2: 32.5, y2: 24.8, support_type: "pinned" },
  ]);

  const [holes, setHoles] = useState<Hole[]>([]);
  const [areaLoads, setAreaLoads] = useState<AreaLoad[]>([]);
  const [results, setResults] = useState<any>(null);

  // Guided Mode State
  const [foundationTypeId, setFoundationTypeId] = useState("smooth");
  const [purposePresetId, setPurposePresetId] = useState("industrial_storage");
  const [soilPresetId, setSoilPresetId] = useState("medium_clay");
  const [diagnosticConservatism, setDiagnosticConservatism] = useState<DiagnosticConservatism>("balanced");
  const [kvSource, setKvSource] = useState<KvSource>("table_reference");
  const [kvConfidence, setKvConfidence] = useState(0.5);
  const [ignorePillars, setIgnorePillars] = useState(false);
  const [selectedFieldRiskIds, setSelectedFieldRiskIds] = useState<string[]>([]);

  return {
    params,
    setParams,
    pillars,
    setPillars,
    lineSupports,
    setLineSupports,
    holes,
    setHoles,
    areaLoads,
    setAreaLoads,
    results,
    setResults,
    foundationTypeId, setFoundationTypeId,
    purposePresetId, setPurposePresetId,
    soilPresetId, setSoilPresetId,
    diagnosticConservatism, setDiagnosticConservatism,
    kvSource, setKvSource,
    kvConfidence, setKvConfidence,
    ignorePillars, setIgnorePillars,
    selectedFieldRiskIds, setSelectedFieldRiskIds
  };
}
