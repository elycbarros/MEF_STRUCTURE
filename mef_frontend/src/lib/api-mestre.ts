import type { MestreApiResponse, MestreElementType, MestreParams, PointLoad } from './mestre-types';

/**
 * API Client para o Modo Mestre do Atlas Structural Engine.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    throw new Error(`Erro na análise do Mestre: ${response.statusText}`);
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
    throw new Error(`Erro na predição PhD: ${response.statusText}`);
  }

  return response.json();
}

type FrameNode = Record<string, unknown>;
type FrameMember = Record<string, unknown>;

export async function analyzeMestreFrame(
  nodes: FrameNode[],
  members: FrameMember[],
  loads: PointLoad[],
  supports: Record<string, number[]>
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/frame/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nodes, members, loads, supports }),
  });

  if (!response.ok) {
    throw new Error(`Erro na análise de pórtico: ${response.statusText}`);
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
    throw new Error(`Erro na análise de SPT: ${response.statusText}`);
  }

  return response.json();
}

export async function calculateStability(
  params: { v0: number; height: number; width_x: number },
  signal?: AbortSignal
): Promise<MestreApiResponse> {
  const response = await fetch(`${BASE_URL}/api/mestre/calculate/stability-mestre`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Erro na análise de estabilidade: ${response.statusText}`);
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
    throw new Error(`Erro na análise de vento: ${response.statusText}`);
  }

  return response.json();
}
