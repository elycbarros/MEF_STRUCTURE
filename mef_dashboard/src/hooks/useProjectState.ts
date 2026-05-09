import { useState, useCallback, useMemo } from "react";
import { Gauge, ShieldCheck, Building2, StretchHorizontal, FileText, Wind, Box, Database, Search, Cpu, ClipboardCheck, Share2, Activity, Zap, BookOpen, Book, Layers } from "lucide-react";

export type AcademicTabId = "dashboard" | "geometria" | "porticos" | "trelicas" | "pilares_isolados" | "vigas" | "especiais" | "vigacross" | "backlog" | "biblioteca";
export type TabId = AcademicTabId | "pilares" | "armadura" | "resultado" | "vento" | "tensionpro";
type LogEntry = {
  message: string;
  type: "info" | "success" | "error" | "warning";
  timestamp: string;
};

export function useProjectState(mode: "academic" | "professional" | null = "professional") {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Pronto.");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [systemType, setSystemType] = useState<"radier" | "laje">("radier");
  const [slabType, setSlabType] = useState<"solid" | "ribbed" | "hollow_core" | "prestressed" | "trussed">("solid");
  const [fillerType, setFillerType] = useState<"ceramic" | "eps">("ceramic");
  const [b_nerv, setBNerv] = useState(0.10);
  const [dist_nerv, setDistNerv] = useState(0.50);
  const [h_mesa, setHMesa] = useState(0.05);
  const [area_voids, setAreaVoids] = useState(0.04);
  const [p_force, setPForce] = useState(200.0);
  const [ecc, setEcc] = useState(0.05);

  const [docMeta, setDocMeta] = useState({
    obra: mode === "academic" ? "Exercicio Acadêmico 01" : "Edifício Torre Central",
    cliente: mode === "academic" ? "Prof. Dr. Engenheiro" : "Cliente não informado",
    local: "Brasil",
    responsavel: "Eng. Responsável",
    registro: "CREA a informar",
    revisao: "R00",
    emissao: new Date().toLocaleDateString("pt-BR"),
  });

  const addLog = useCallback((message: string, type: "info" | "success" | "error" | "warning" = "info") => {
    setLogs(prev => [...prev, {
      message,
      type,
      timestamp: new Date().toLocaleTimeString("pt-BR", { hour12: false })
    }]);
  }, []);

  const { primaryTabs, secondaryTabs } = useMemo(() => {
    const p = [
      { id: "dashboard", label: "Painel", icon: Gauge },
      { id: "lajes", label: "LAJES", icon: Layers },
      { id: "geometria", label: "RADIER", icon: ShieldCheck },
      { id: "porticos", label: "PÓRTICOS", icon: Share2 },
      { id: "trelicas", label: "TRELIÇAS", icon: Activity },
      { id: "pilares_isolados", label: "DIMENSIONAR PILAR", icon: Cpu },
      { id: "vigas", label: "DIMENSIONAR VIGA", icon: Box },
      { id: "especiais", label: "PAREDES E ESPECIAIS", icon: Database },
    ];

    const s = [
      { id: "vigacross", label: "VIGA CROSS", icon: Share2 },
      { id: "tensionpro", label: "TENSION PRO", icon: Zap },
      { id: "backlog", label: "Backlog", icon: ClipboardCheck },
      { id: "biblioteca", label: "Biblioteca", icon: BookOpen }
    ];

    return { primaryTabs: p, secondaryTabs: s };
  }, [systemType, mode]);

  return {
    activeTab,
    setActiveTab,
    loading,
    setLoading,
    statusMessage,
    setStatusMessage,
    logs,
    addLog,
    systemType,
    setSystemType,
    slabType,
    setSlabType,
    docMeta,
    setDocMeta,
    primaryTabs,
    secondaryTabs,
    b_nerv, setBNerv,
    dist_nerv, setDistNerv,
    h_mesa, setHMesa,
    area_voids, setAreaVoids,
    p_force, setPForce,
    ecc, setEcc,
    fillerType, setFillerType
  };
}
