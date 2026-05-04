export type SupportType = 'fixed' | 'pin' | 'free';

export interface PointLoad {
  type: 'point';
  value: number; // kN
  position: number; // m from span start
}

export interface UdlLoad {
  type: 'udl';
  value: number; // kN/m
}

export type SpanLoad = PointLoad | UdlLoad;

export interface SpanInput {
  id: string;
  length: number; // m
  inertiaCm4: number;
  loads: SpanLoad[];
}

export interface BeamInput {
  spans: SpanInput[];
  supports: SupportType[]; // size = spans + 1
  eGPa: number;
  defaultInertiaCm4: number;
  tolerance?: number;
  maxIterations?: number;
}

export interface EndMoments {
  left: number;
  right: number;
}

export interface BarEndResult {
  barId: string;
  nodeA: string;
  nodeB: string;
  mepA: number;
  mepB: number;
  finalA: number;
  finalB: number;
}

export interface CrossIteration {
  iteration: number;
  nodeResults: {
    nodeId: string;
    unbalancedMoment: number;
    distributedMoments: { barId: string; value: number }[];
    transmittedMoments: { barId: string; value: number }[];
  }[];
  maxUnbalanced: number;
}

export interface NodeReaction {
  nodeId: string;
  verticalReaction: number;
}

export interface DiagramPoint {
  xGlobal: number;
  spanId: string;
  xLocal: number;
  shear: number;
  moment: number;
}

export interface CrossSolveResult {
  input: BeamInput;
  nodes: string[];
  barResults: BarEndResult[];
  iterations: CrossIteration[];
  converged: boolean;
  finalMaxUnbalanced: number;
  nodeReactions: NodeReaction[];
  diagrams: DiagramPoint[];
}
