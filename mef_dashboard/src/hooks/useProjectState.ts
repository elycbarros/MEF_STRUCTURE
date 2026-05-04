import { useState, useCallback, useMemo } from "react";
import { Gauge, ShieldCheck, Building2, StretchHorizontal, FileText, Wind, Box, Database, Search, Cpu, ClipboardCheck } from "lucide-react";

export type AcademicTabId = "dashboard" | "geometria" | "pilares_isolados" | "vigas" | "especiais" | "forensic" | "backlog";
export type TabId = AcademicTabId | "pilares" | "armadura" | "resultado" | "integracao" | "vento";
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
  const [systemType, setSystemType] = useState<"radier" | "laje">(mode === "academic" ? "laje" : "radier");

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

  const tabs = useMemo(() => {
    if (mode === "academic") {
      return [
        { id: "dashboard", label: "Painel", icon: Gauge },
        { id: "backlog", label: "Backlog", icon: ClipboardCheck },
        { id: "geometria", label: "Lajes e Radier", icon: ShieldCheck },
        { id: "pilares_isolados", label: "Dimensionar Pilar", icon: Cpu },
        { id: "vigas", label: "Dimensionar Viga", icon: Box },
        { id: "especiais", label: "Escadas e Reservatórios", icon: Database }
      ];
    }

    const allTabs = [
      { id: "dashboard", label: "Painel", icon: Gauge },
      { id: "geometria", label: systemType === "radier" ? "Modo Guiado" : "Parâmetros", icon: ShieldCheck },
      { id: "pilares", label: "Pilares", icon: Building2 },
      { id: "armadura", label: "Armadura", icon: StretchHorizontal },
      { id: "resultado", label: "Relatório", icon: FileText },
      { id: "vento", label: "Vento", icon: Wind },
      { id: "especiais", label: "Especiais", icon: Box },
      { id: "forensic", label: "Laboratório Forense", icon: Search },
      { id: "integracao", label: "PhD Console", icon: Cpu },
    ];

    return allTabs;
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
    docMeta,
    setDocMeta,
    tabs
  };
}
