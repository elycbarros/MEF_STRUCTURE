import type { MestreApiResponse, MestreElementType, MestreParams } from './mestre-types';

/**
 * API Client para o Modo Mestre do Atlas Structural Engine.
 */

export const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type MestreHealth = {
  status?: string;
  engine?: string;
  version?: string;
};

export async function getMestreHealth(signal?: AbortSignal): Promise<MestreHealth> {
  const response = await fetch(`${BASE_URL}/api/health`, { signal });

  if (!response.ok) {
    throw new Error(`Engine indisponível: ${response.statusText || response.status}`);
  }

  return response.json();
}

export async function calculateSpecialElement(
  type: MestreElementType,
  params: Partial<MestreParams>,
  signal?: AbortSignal
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/calculate/special-elements`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, params }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro no motor estrutural';
    throw new Error(`Erro na análise do Mestre: ${message}`);
  }

  return response.json();
}

export async function predictPhD(params: Partial<MestreParams>): Promise<unknown> {
  const response = await fetch(`${BASE_URL}/api/mestre/phd/predict_fast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro na predição PhD';
    throw new Error(`Erro na predição PhD: ${message}`);
  }

  return response.json();
}

type FrameNode = Record<string, unknown>;
type FrameMember = Record<string, unknown>;
type FrameLoad = Record<string, unknown>;

export async function analyzeMestreFrame(
  nodes: FrameNode[],
  members: FrameMember[],
  loads: FrameLoad[],
  supports: Record<string, number[]>,
  is_truss: boolean = false
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/frame/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes, members, loads, supports, is_truss }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    // Note: Frames can return the specialized error object from api.py
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro desconhecido no servidor';
    throw new Error(`Erro na análise de pórtico: ${message}`);
  }

  return response.json();
}

export async function calculateSpt(
  spt_data: unknown[],
  signal?: AbortSignal
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/calculate/spt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spt_data }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro na análise de SPT';
    throw new Error(`Erro na análise de SPT: ${message}`);
  }

  return response.json();
}

export async function calculateStability(
  params: Partial<MestreParams>,
  signal?: AbortSignal
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/calculate/stability-mestre`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro na análise de estabilidade';
    throw new Error(`Erro na análise de estabilidade: ${message}`);
  }

  return response.json();
}

export async function calculateWind(
  params: Partial<MestreParams>,
  signal?: AbortSignal
): Promise<MestreApiResponse> {
  // O endpoint de vento está no prefixo /api/ufo no backend elite
  const response = await fetch(`${BASE_URL}/api/ufo/calculate/wind`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      v0: params.v0,
      altura_total: params.height,
      largura: params.width_x,
      profundidade: params.width_y,
      step: params.step || 1.0,
      cf: params.cf,
      area_por_nivel_m2: params.area_por_nivel_m2,
      s1: params.s1 || 1.0,
      s3: params.s3 || 1.0,
      categoria: params.categoria || 2,
      classe: params.classe || 'B',
      is_dynamic: params.is_dynamic || false,
      f1: params.f1 || 0.5,
      zeta: params.zeta || 0.01,
      beta: params.beta || 1.0
    }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.error?.message || response.statusText || 'Erro na análise de vento';
    throw new Error(`Erro na análise de vento: ${message}`);
  }

  return response.json();
}

export async function generateProfessionalMemorial(
  results: any,
  project_meta: any,
  signal?: AbortSignal
): Promise<{ pdf_url: string; filename: string }> {
  const response = await fetch(`${BASE_URL}/api/mestre/generate/professional-memorial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ results, project_meta }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Erro ao gerar memorial profissional');
  }

  return response.json();
}

export async function generateExamAuditorMemorial(
  question_id: string,
  signal?: AbortSignal
): Promise<{ success: boolean; pdf_url: string; filename: string; question_id: string }> {
  const response = await fetch(`${BASE_URL}/api/mestre/generate/exam-auditor-memorial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id }),
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Erro ao gerar PDF da auditoria');
  }

  return response.json();
}
