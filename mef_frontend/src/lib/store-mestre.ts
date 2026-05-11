import { create } from 'zustand';
import type { MestreCalculationTrace, MestreElementType, MestreParams, MestreStep } from './mestre-types';

interface MestreState {
  selectedElementType: MestreElementType;
  params: MestreParams;
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
  
  // Engineering Actions
  updateUnitConfig: (config: Partial<MestreState['unitConfig']>) => void;
  setLoadCases: (cases: MestreState['loadCases']) => void;
  setCombinations: (combinations: MestreState['combinations']) => void;
}

export const useMestreStore = create<MestreState>((set) => ({
  selectedElementType: 'beam',
  sidebarCollapsed: false,
  viewMode: 'interactive',
  params: {
    L: 6.0,
    b: 0.20,
    h: 0.50,
    q: 20.0,
    fck: 30.0,
    // Pile defaults
    diameter: 0.40,
    length: 12.0,
    Nd: 500.0,
    pile_type: 'bored',
    layers: [
      { depth_m: 2.0, thickness_m: 2.0, nspt: 5, soil_type: 'areia' },
      { depth_m: 8.0, thickness_m: 6.0, nspt: 15, soil_type: 'silte' },
      { depth_m: 15.0, thickness_m: 7.0, nspt: 30, soil_type: 'areia' },
    ],
    // Footing defaults
    sigma_adm: 300.0,
    ap: 0.20,
    bp: 0.20,
    dist_piles: 1.6,
    diam_pile: 0.4,
    d_height: 0.65,
    fyk: 500.0,
    // Column defaults
    L_free: 3.0,
    Mxd: 25.0,
    Myd: 10.0,
    caa: 2,
    // Slab defaults
    Lx: 5.0,
    Ly: 4.0,
    slab_type: 'solid',
    // Stability defaults
    v0: 30.0,
    height: 30.0,
    width_x: 12.0,
  },
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

  setSelectedElementType: (type) => set({ selectedElementType: type, pedagogicalSteps: [], prediction: null, error: null, calculationTrace: null }),
  updateParams: (newParams) => set((state) => ({ params: { ...state.params, ...newParams } })),
  setPedagogicalSteps: (steps) => set({ pedagogicalSteps: steps }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error: error }),
  setCalculationTrace: (trace) => set({ calculationTrace: trace }),
  setPrediction: (prediction) => set({ prediction: prediction }),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setFullResults: (results) => set({ fullResults: results }),
  updateUnitConfig: (config) => set((state) => ({ unitConfig: { ...state.unitConfig, ...config } })),
  setLoadCases: (cases) => set({ loadCases: cases }),
  setCombinations: (combinations) => set({ combinations: combinations }),
}));
