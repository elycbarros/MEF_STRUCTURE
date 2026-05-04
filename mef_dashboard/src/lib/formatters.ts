import { formatNumberBR } from "./utils";

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

export function asRecordArray(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === "object" && !Array.isArray(item)) as Array<Record<string, unknown>> : [];
}

export function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item) => typeof item === "string") as string[] : [];
}

export function numberFromRecord(record: Record<string, unknown>, keys: string[], fallback = 0): number {
  for (const key of keys) {
    const value = Number(record[key]);
    if (Number.isFinite(value)) return value;
  }
  return fallback;
}

export function normalizeFrameDiagram(frameResults: unknown, memberId: number): Array<{ x: number; moment: number; shear: number }> {
  const frame = asRecord(frameResults);
  const diagrams = asRecordArray(frame.diagrams);
  if (diagrams.length === 0) return [];

  const selected = diagrams.find((item) => Number(item.memberId) === memberId || Number(item.member_index) === memberId);
  if (!selected) return [];

  const rows = asRecordArray(selected?.data);

  return rows.map((row, index) => ({
    x: numberFromRecord(row, ["x", "X", "x_m", "station", "pos"], index),
    moment: numberFromRecord(row, ["moment", "M", "M_kNm", "m_kNm", "Mz", "Mz_kNm"]),
    shear: numberFromRecord(row, ["shear", "V", "V_kN", "v_kN", "Vy", "Vy_kN"]),
  }));
}

export function uniqueStrings(values: string[]): string[] {
  return [...new Set(values.map((v) => v.trim()).filter(Boolean))];
}

export function formatBoolean(value: unknown): string {
  if (value === true) return "SIM";
  if (value === false) return "NÃO";
  return "--";
}

export function formatMaybeNumber(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value) ? formatNumberBR(value, 4) : "--";
}

export function formatMaybePercent(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value) ? `${formatNumberBR(value * 100, 0)}%` : "--";
}

export function parseLocaleNumberInput(raw: string): number | null {
  const cleaned = raw.trim();
  if (!cleaned) return null;
  const normalized = cleaned.includes(",")
    ? cleaned.replace(/\./g, "").replace(",", ".")
    : cleaned;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

export function collectFileArtifacts(value: unknown, prefix = ""): Array<{ label: string; path: string }> {
  if (!value || typeof value !== "object") return [];
  const obj = value as Record<string, unknown>;
  const out: Array<{ label: string; path: string }> = [];
  for (const [key, v] of Object.entries(obj)) {
    const label = prefix ? `${prefix}.${key}` : key;
    if (typeof v === "string" && (v.includes("/") || v.endsWith(".json") || v.endsWith(".csv") || v.endsWith(".md"))) {
      out.push({ label, path: v });
      continue;
    }
    if (v && typeof v === "object" && !Array.isArray(v)) {
      out.push(...collectFileArtifacts(v, label));
    }
  }
  return out;
}
