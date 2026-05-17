export type MestreElementType =
  | "beam"
  | "beam_cross"
  | "column"
  | "slab"
  | "footing"
  | "pile"
  | "pile_cap"
  | "stair"
  | "helical_stairs"
  | "retaining_wall"
  | "concrete_wall"
  | "reservoir"
  | "corbel"
  | "gerber_tooth"
  | "deep_beam"
  | "spt"
  | "stability"
  | "wind"
  | "vento"
  | "frames"
  | "trusses"
  | "advanced_slab"
  | "tension_pro"
  | "tech_library";

export type SupportType = "pinned" | "fixed" | "roller" | "spring";

export interface BeamSupport {
  x: number;
  type: SupportType;
}

export interface DistributedLoad {
  x_start: number;
  x_end: number;
  q_start: number;
  q_end: number;
}

export interface PointLoad {
  x: number;
  P: number;
  M?: number;
}

export interface SoilLayer {
  depth_m: number;
  thickness_m: number;
  nspt: number;
  soil_type: string;
}

export type MestreParams = {
  L: number;
  b: number;
  h: number;
  q: number;
  fck: number;
  diameter: number;
  length: number;
  Nd: number;
  pile_type: string;
  layers: SoilLayer[];
  sigma_adm: number;
  ap: number;
  bp: number;
  A_m?: number;
  B_m?: number;
  h_m?: number;
  section_type?: "rectangular" | "t-beam";
  bf?: number;
  hf?: number;
  supports?: BeamSupport[];
  distributed_loads?: DistributedLoad[];
  point_loads?: PointLoad[];
  caa?: number;
  cover_mm?: number;
  fy?: number;
  nd?: number;
  a_dist?: number;
  d_eff?: number;
  L_horizontal?: number;
  q_live?: number;
  L_free?: number;
  Mxd?: number;
  Myd?: number;
  Lx?: number;
  Ly?: number;
  slab_type?: "solid" | "ribbed" | "prestressed";
  width?: number;
  t?: number;
  H?: number;
  dist_piles?: number;
  diam_pile?: number;
  d_height?: number;
  fyk?: number;
  h_wall?: number;
  b_base?: number;
  gamma_soil?: number;
  phi_soil?: number;
  depth?: number;
  vd_kN?: number;
  hd_kN?: number;
  fd_kN?: number;
  fd_kN_m?: number;
  radius?: number;
  angle_total_deg?: number;
  h_step?: number;
  q_acid?: number;
  weight_wall?: number;
  v0?: number;
  height?: number;
  width_x?: number;
  width_y?: number;
  s1?: number;
  s3?: number;
  categoria?: number;
  classe?: string;
  is_dynamic?: boolean;
  f1?: number;
  zeta?: number;
  beta?: number;
  cf?: number;
  area_por_nivel_m2?: number;
  step?: number;
  total_p_kN?: number;
  m1_kNm?: number;
  spans?: import('@/lib/vigacross/types').SpanInput[];
} & Record<string, unknown>;

export interface MestreStep {
  id: string;
  title: string;
  formula: string;
  substitution: string;
  result: string;
  explanation: string;
  norm?: string;
  diagram?: string;
  diagramData?: TechnicalDiagramData;
  chartData?: {
    type: "shear" | "moment" | "deflection";
    unit: string;
    label: string;
    series: {
      name: string;
      points: { x: number; y: number }[];
      color?: string;
      dashed?: boolean;
    }[];
    reactions?: {
      x: number;
      value: number;
      label: string;
    }[];
  };
  detailingData?: {
    type: "beam_section" | "column_section";
    b: number;
    h: number;
    bf?: number;
    hf?: number;
    cover: number;
    layers: {
      position: "bottom" | "top" | "skin";
      bars: {
        count: number;
        diameter: number;
      }[];
    }[];
    stirrups?: {
      diameter: number;
      spacing: number;
      legs: number;
    };
  };
}

export interface TechnicalDiagramData {
  kind:
    | "footing"
    | "slab"
    | "retaining_wall"
    | "stair"
    | "reservoir"
    | "corbel"
    | "gerber_tooth"
    | "deep_beam"
    | string;
  title: string;
  values?: Record<string, number | string | null>;
}

export interface MestreApiResponse {
  success?: boolean;
  pedagogical_steps?: { steps?: MestreStep[] } | MestreStep[];
  calculation_trace?: MestreCalculationTrace;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

export function extractMestreSteps(response: MestreApiResponse): MestreStep[] {
  const steps = response.pedagogical_steps;
  if (Array.isArray(steps)) return steps;
  return steps?.steps ?? [];
}

export interface StructuralDuelEntry {
  parameter: string;
  classical_value: string;
  mef_value: string;
  difference_percent: number;
  insight: string;
}

export interface MestreCalculationTrace {
  requested_type: MestreElementType;
  solver_module: string | null;
  blackboard_builder: string | null;
  classical_check: boolean;
  mef_check: boolean;
  duel?: StructuralDuelEntry[];
}
