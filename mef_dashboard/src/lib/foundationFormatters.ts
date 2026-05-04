import { RiskSeverity, FieldRiskSummary, DiagnosticConservatism } from "@/hooks/useRadierAnalysis";
import { uniqueStrings } from "./formatters";

export function buildFieldRiskSummary(
  selected: Array<{ id: string; label: string; severity: RiskSeverity; action: string }>,
  soilSeverity: RiskSeverity,
): FieldRiskSummary {
  const severityOrder: Record<RiskSeverity, number> = { green: 0, yellow: 1, red: 2 };
  const worst = selected.reduce<RiskSeverity>(
    (acc, item) => (severityOrder[item.severity] > severityOrder[acc] ? item.severity : acc),
    soilSeverity,
  );
  const recommendations = selected.map((item) => item.action);
  if (soilSeverity === "red") {
    recommendations.unshift("Solo do preset exige mitigação geotécnica antes de liberar fundação rasa.");
  }
  if (soilSeverity === "yellow") {
    recommendations.unshift("Confirmar parâmetros do solo com sondagem, prova de carga ou correlação validada.");
  }
  if (recommendations.length === 0) {
    recommendations.push("Manter registro das premissas geotécnicas e controle executivo de compactação, lastro, lona e cura.");
  }
  return {
    status: worst,
    selected,
    recommendations: uniqueStrings(recommendations),
  };
}

export function formatChecklistStatus(value: string): string {
  const labels: Record<string, string> = {
    apto_para_estudo_preliminar_profissional: "Apto para estudo preliminar profissional",
    apto_com_restricoes: "Apto com restrições técnicas",
    nao_apto_requer_revisao_tecnica: "Não apto: requer revisão técnica",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}

export function formatFoundationClassification(value: string): string {
  const labels: Record<string, string> = {
    radier_liso_viavel_preliminarmente: "Radier liso viável preliminarmente",
    radier_liso_viavel_com_alertas: "Radier liso viável com alertas",
    radier_liso_viavel_com_restricoes: "Radier liso viável com restrições",
    radier_liso_nao_recomendado_sem_revisao: "Radier liso não recomendado sem revisão",
    estudar_solucao_alternativa: "Estudar solução alternativa",
    sem_diagnostico: "Sem diagnóstico",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}

export function formatFoundationTriggerLevel(value: string): string {
  const labels: Record<string, string> = {
    alerta: "Alerta",
    restricao: "Restrição",
    bloqueio: "Bloqueio",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}

export function formatDiagnosticConservatism(value: DiagnosticConservatism, options: any[]): string {
  return options.find((item) => item.id === value)?.label ?? "Equilibrado";
}
