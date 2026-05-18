import { create } from 'zustand';
import { extractMestreResult, extractMestreSteps, type MestreApiResponse, type MestreCalculationTrace, type MestreElementType, type MestreParams, type MestreStep } from './mestre-types';

type MestreModuleSnapshot = {
  params: MestreParams;
  pedagogicalSteps: MestreStep[];
  calculationTrace: MestreCalculationTrace | null;
  prediction: unknown | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fullResults: any | null;
};

interface MestreState {
  selectedElementType: MestreElementType;
  params: MestreParams;
  moduleSnapshots: Partial<Record<MestreElementType, MestreModuleSnapshot>>;
  pedagogicalSteps: MestreStep[];
  isLoading: boolean;
  error: string | null;
  calculationTrace: MestreCalculationTrace | null;
  prediction: unknown | null;
  sidebarCollapsed: boolean;
  viewMode: 'interactive' | 'memorial';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fullResults: any | null;

  // Global Engineering Settings
  unitConfig: {
    length: 'm' | 'cm' | 'mm';
    force: 'kN' | 'tf';
    stress: 'MPa' | 'kPa';
  };
  loadCases: Array<{ id: string; name: string; type: 'pp' | 'perm' | 'acid' | 'wind'; factor: number }>;
  combinations: Array<{ name: string; cases: Array<{ id: string; gamma: number }> }>;
  projectMeta: {
    title: string;
    client: string;
    engineer: string;
    crea: string;
    location: string;
  };

  // Actions
  setSelectedElementType: (type: MestreElementType) => void;
  updateParams: (newParams: Partial<MestreParams>) => void;
  setPedagogicalSteps: (steps: MestreStep[]) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCalculationTrace: (trace: MestreCalculationTrace | null) => void;
  setPrediction: (prediction: unknown) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setViewMode: (mode: 'interactive' | 'memorial') => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setFullResults: (results: any) => void;
  applyMestreResponse: (response: MestreApiResponse) => void;

  // Engineering Actions
  updateUnitConfig: (config: Partial<MestreState['unitConfig']>) => void;
  setLoadCases: (cases: MestreState['loadCases']) => void;
  setCombinations: (combinations: MestreState['combinations']) => void;
  setProjectMeta: (meta: Partial<MestreState['projectMeta']>) => void;
}

const DEFAULT_MESTRE_PARAMS: MestreParams = {
  L: 6.0,
  b: 0.20,
  h: 0.50,
  q: 20.0,
  fck: 30.0,
  diameter: 0.40,
  length: 12.0,
  Nd: 500.0,
  pile_type: 'bored',
  layers: [
    { depth_m: 2.0, thickness_m: 2.0, nspt: 5, soil_type: 'areia' },
    { depth_m: 8.0, thickness_m: 6.0, nspt: 15, soil_type: 'silte' },
    { depth_m: 15.0, thickness_m: 7.0, nspt: 30, soil_type: 'areia' },
  ],
  sigma_adm: 300.0,
  ap: 0.20,
  bp: 0.20,
  dist_piles: 1.6,
  diam_pile: 0.4,
  d_height: 0.65,
  fyk: 500.0,
  L_free: 3.0,
  Mxd: 25.0,
  Myd: 10.0,
  caa: 2,
  Lx: 5.0,
  Ly: 4.0,
  slab_type: 'solid',
  v0: 30.0,
  height: 30.0,
  width_x: 12.0,
};

const MODULE_PARAM_PRESETS: Partial<Record<MestreElementType, Partial<MestreParams>>> = {
  beam: {
    L: 6.0,
    b: 0.20,
    h: 0.50,
    q: 20.0,
    supports: [{ x: 0, type: 'pinned' }, { x: 6.0, type: 'pinned' }],
    distributed_loads: [{ x_start: 0, x_end: 6.0, q_start: 20.0, q_end: 20.0 }],
    point_loads: [],
  },
  column: { b: 0.40, h: 0.40, Nd: 1000.0, L_free: 3.0, Mxd: 25.0, Myd: 10.0 },
  slab: { Lx: 5.0, Ly: 4.0, h: 0.16, q: 5.0, slab_type: 'solid' },
  footing: { Nd: 500.0, sigma_adm: 300.0, ap: 0.20, bp: 0.20, fck: 25.0 },
  pile: { diameter: 0.40, length: 12.0, Nd: 500.0, pile_type: 'bored' },
  pile_cap: { dist_piles: 1.6, d_height: 0.65, diam_pile: 0.4, Nd: 500.0 },
  frames: { n_bays: 1, n_levels: 1, bay_width: 5.0, level_height: 3.0, b: 0.20, h: 0.50, q: 15.0, use_special_portico: false },
  trusses: { L: 12.0, h: 1.5, n_panels: 6, area_cm2: 15.0, q: 5.0, truss_type: 'warren' },
  stability: { height: 30.0, v0: 30.0, f1_hz: 0.5 },
  wind: { v0: 30.0, height: 15.0, width_x: 10.0, s1: 1.0, s3: 1.0, is_dynamic: false },
  spt: { layers: DEFAULT_MESTRE_PARAMS.layers },
  advanced_slab: { Lx: 10.0, Ly: 10.0, h: 0.40, kv: 30.0, fck: 30.0, q: 5.0 },
  tension_pro: { L: 10.0, q: 20.0, p0: 1200.0, ecc: 0.15 },
  exam_auditor: { L: 8.0, b: 0.20, h: 0.50, q: 0.0, truss_type: undefined, supports: [{ x: 0.0, type: 'pinned' }, { x: 6.0, type: 'roller' }], distributed_loads: [], point_loads: [{ x: 8.0, P: 30.0 }] },
};

function buildModuleParams(type: MestreElementType, snapshot?: MestreModuleSnapshot): MestreParams {
  return {
    ...DEFAULT_MESTRE_PARAMS,
    ...(MODULE_PARAM_PRESETS[type] ?? {}),
    ...(snapshot?.params ?? {}),
  };
}

export const useMestreStore = create<MestreState>((set) => ({
  selectedElementType: 'beam',
  sidebarCollapsed: false,
  viewMode: 'interactive',
  params: buildModuleParams('beam'),
  moduleSnapshots: {},
  pedagogicalSteps: [],
  isLoading: false,
  error: null,
  calculationTrace: null,
  prediction: null,
  fullResults: null,
  unitConfig: { length: 'm', force: 'kN', stress: 'MPa' },
  loadCases: [
    { id: 'pp', name: 'Peso Próprio', type: 'pp', factor: 1.0 },
    { id: 'perm', name: 'Permanente', type: 'perm', factor: 1.0 },
    { id: 'acid', name: 'Acidental', type: 'acid', factor: 1.0 },
  ],
  combinations: [
    { name: 'ELU Fundamental', cases: [{ id: 'pp', gamma: 1.4 }, { id: 'perm', gamma: 1.4 }, { id: 'acid', gamma: 1.4 }] },
  ],
  projectMeta: {
    title: 'Edifício Residencial Atlas',
    client: 'Engenharia & Co',
    engineer: 'Eng. Estrutural: Ely Barros',
    crea: '123456789-0',
    location: 'Palhoça - SC',
  },

  setSelectedElementType: (type) => set((state) => {
    if (state.selectedElementType === type) return {};

    const snapshots = {
      ...state.moduleSnapshots,
      [state.selectedElementType]: {
        params: state.params,
        pedagogicalSteps: state.pedagogicalSteps,
        calculationTrace: state.calculationTrace,
        prediction: state.prediction,
        fullResults: state.fullResults,
      },
    };
    const nextSnapshot = snapshots[type];

    return {
      selectedElementType: type,
      params: buildModuleParams(type, nextSnapshot),
      pedagogicalSteps: nextSnapshot?.pedagogicalSteps ?? [],
      prediction: nextSnapshot?.prediction ?? null,
      error: null,
      calculationTrace: nextSnapshot?.calculationTrace ?? null,
      fullResults: nextSnapshot?.fullResults ?? null,
      isLoading: false,
      moduleSnapshots: snapshots,
    };
  }),
  updateParams: (newParams) => set((state) => ({ params: { ...state.params, ...newParams } })),
  setPedagogicalSteps: (steps) => set({ pedagogicalSteps: steps }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error: error }),
  setCalculationTrace: (trace) => set({ calculationTrace: trace }),
  setPrediction: (prediction) => set({ prediction: prediction }),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setFullResults: (results) => set({ fullResults: results }),
  applyMestreResponse: (response) => set({
    pedagogicalSteps: extractMestreSteps(response),
    calculationTrace: response.calculation_trace ?? null,
    fullResults: extractMestreResult(response),
  }),
  updateUnitConfig: (config) => set((state) => ({ unitConfig: { ...state.unitConfig, ...config } })),
  setLoadCases: (cases) => set({ loadCases: cases }),
  setCombinations: (combinations) => set({ combinations: combinations }),
  setProjectMeta: (meta) => set((state) => ({ projectMeta: { ...state.projectMeta, ...meta } })),
}));
