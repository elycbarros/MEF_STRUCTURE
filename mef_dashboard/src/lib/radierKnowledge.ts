export type FoundationTypeStatus = "implemented" | "roadmap";
export type RiskSeverity = "green" | "yellow" | "red";

export interface FoundationType {
  id: string;
  name: string;
  status: FoundationTypeStatus;
  modelNote: string;
  roadmapNote: string;
}

export interface PurposePreset {
  id: string;
  name: string;
  q_kN_m2: number;
  h_m: number;
  serviceLimitMm: number;
  technicalNote: string;
}

export interface SoilPreset {
  id: string;
  name: string;
  kv_kN_m3: number;
  sigma_adm_kPa: number;
  risk: RiskSeverity;
  technicalNote: string;
}

export interface FieldRisk {
  id: string;
  label: string;
  severity: RiskSeverity;
  action: string;
}

export const foundationTypes: FoundationType[] = [
  {
    id: "smooth",
    name: "Radier liso",
    status: "implemented",
    modelNote: "Placa de espessura constante sobre solo de Winkler.",
    roadmapNote: "Modelo atual do solver: laje de fundacao macica/lisa.",
  },
  {
    id: "drop_panel",
    name: "Pedestais ou cogumelos",
    status: "roadmap",
    modelNote: "Engrossamento local sob pilares para flexao, cortante e puncao.",
    roadmapNote: "Proxima etapa natural: espessura local e contornos de puncao refinados.",
  },
  {
    id: "ribbed",
    name: "Radier nervurado",
    status: "roadmap",
    modelNote: "Sistema com nervuras/vigas principais e secundarias sob os apoios.",
    roadmapNote: "Pode evoluir por grelha equivalente ou laje + vigas de fundacao.",
  },
  {
    id: "box",
    name: "Radier em caixao",
    status: "roadmap",
    modelNote: "Alta rigidez global, com comportamento de celulas/caixoes.",
    roadmapNote: "Exige modelo de rigidez tridimensional ou grelha/lâmina mais detalhada.",
  },
];

export const purposePresets: PurposePreset[] = [
  {
    id: "residential_low",
    name: "Residencial baixo porte",
    q_kN_m2: 2,
    h_m: 0.35,
    serviceLimitMm: 25,
    technicalNote: "Preset conservador para casas/sobrados com foco em recalque diferencial.",
  },
  {
    id: "commercial_light",
    name: "Comercial leve",
    q_kN_m2: 4,
    h_m: 0.45,
    serviceLimitMm: 35,
    technicalNote: "Uso comercial sem trafego pesado interno; ajustar para publico intenso.",
  },
  {
    id: "warehouse_light",
    name: "Galpao leve",
    q_kN_m2: 10,
    h_m: 0.55,
    serviceLimitMm: 50,
    technicalNote: "Armazenagem leve e operacao com equipamentos pequenos.",
  },
  {
    id: "industrial_storage",
    name: "Deposito industrial",
    q_kN_m2: 20,
    h_m: 0.7,
    serviceLimitMm: 50,
    technicalNote: "Preset para cargas distribuidas relevantes e controle de fissuracao.",
  },
  {
    id: "logistics_heavy",
    name: "Logistico / porta-palete",
    q_kN_m2: 40,
    h_m: 0.9,
    serviceLimitMm: 50,
    technicalNote: "Exige checagem de cargas concentradas e operacao de equipamentos.",
  },
  {
    id: "parking_light",
    name: "Patio veiculos leves",
    q_kN_m2: 3,
    h_m: 0.35,
    serviceLimitMm: 35,
    technicalNote: "Base para estacionamento/manobra de veiculos leves; validar carga por roda.",
  },
  {
    id: "parking_heavy",
    name: "Patio veiculos pesados",
    q_kN_m2: 10,
    h_m: 0.75,
    serviceLimitMm: 50,
    technicalNote: "Exige verificacao de carga concentrada, fadiga operacional e base/sub-base.",
  },
];

export const soilPresets: SoilPreset[] = [
  {
    id: "soft_organic",
    name: "Solo muito fraco / organico",
    kv_kN_m3: 7500,
    sigma_adm_kPa: 50,
    risk: "red",
    technicalNote: "Turfa, lodo ou camada muito compressivel. Radier direto requer mitigacao geotecnica.",
  },
  {
    id: "wet_clay",
    name: "Argila umida / mole",
    kv_kN_m3: 25000,
    sigma_adm_kPa: 100,
    risk: "yellow",
    technicalNote: "Alta sensibilidade a recalques e heterogeneidade; estudo de solo deve comandar o preset.",
  },
  {
    id: "medium_clay",
    name: "Argila media",
    kv_kN_m3: 45000,
    sigma_adm_kPa: 150,
    risk: "yellow",
    technicalNote: "Valor intermediario para analise preliminar com controle de recalque diferencial.",
  },
  {
    id: "dry_stiff_clay",
    name: "Argila seca dura",
    kv_kN_m3: 80000,
    sigma_adm_kPa: 220,
    risk: "green",
    technicalNote: "Suporte melhor, ainda dependente de sondagem e verificacao de expansividade.",
  },
  {
    id: "sandy_gravel",
    name: "Areia/cascalho compacto",
    kv_kN_m3: 120000,
    sigma_adm_kPa: 300,
    risk: "green",
    technicalNote: "Faixa alta de suporte para estudo preliminar; confirmar nivel d'agua e compacidade.",
  },
  {
    id: "very_stiff_gravel",
    name: "Cascalho muito compacto",
    kv_kN_m3: 200000,
    sigma_adm_kPa: 450,
    risk: "green",
    technicalNote: "Solo de alta rigidez; conferir variabilidade e camada de apoio real.",
  },
];

export const fieldRisks: FieldRisk[] = [
  {
    id: "heterogeneous_soil",
    label: "Solo heterogeneo na cota de apoio",
    severity: "yellow",
    action: "Exigir revisao geotecnica, campanha complementar ou kv_map por sondagem.",
  },
  {
    id: "water_in_excavation",
    label: "Agua/percolacao na cava",
    severity: "red",
    action: "Bloquear ok executivo ate definir drenagem, rebaixamento ou procedimento de concretagem adequado.",
  },
  {
    id: "boulders",
    label: "Matacoes ou blocos de rocha",
    severity: "red",
    action: "Nao considerar apoio direto local sem remocao, tratamento ou solucao alternativa.",
  },
  {
    id: "altered_rock",
    label: "Rocha alterada/decomposta",
    severity: "yellow",
    action: "Usar tensao admissivel especifica da rocha real, sem herdar valor de rocha sa.",
  },
  {
    id: "expansive_or_collapsible",
    label: "Solo expansivo ou colapsivel",
    severity: "red",
    action: "Radier/fundacao rasa nao deve ser liberado sem substituicao, melhoria do solo ou fundacao profunda.",
  },
];

export const knowledgeReferences = [
  "Joao Carlos de Campos, Elementos de Fundacoes em Concreto, cap. 5 e cap. 14.",
  "ABNT NBR 6122: projeto e execucao de fundacoes.",
  "ABNT NBR 6118: lajes lisas/cogumelo, espessuras minimas, puncao e detalhamento.",
  "CYPECAD Memoria de Calculo, secao 2.18: lajes e vigas de fundacao sobre Winkler.",
];
