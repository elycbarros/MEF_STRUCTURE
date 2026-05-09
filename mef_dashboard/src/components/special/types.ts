import { LucideIcon } from 'lucide-react';

export interface BeamParams {
  L: number;
  L_left: number;
  L_right: number;
  b: number;
  h: number;
  d: number;
  fck: number;
  fyk: number;
  q: number;
  includeSelfWeight: boolean;
  leftSupport: "pinned" | "fixed" | "free" | "spring";
  rightSupport: "pinned" | "fixed" | "free" | "spring";
  pointLoads: { x: number; P: number; id: string }[];
  distributedLoads: { id: string; x_start: number; x_end: number; q_start: number; q_end: number; selfWeight?: boolean }[];
}

export interface Result {
  success?: boolean;
  summary?: any;
  diagrams?: any;
  classical_diagrams?: any;
  classical_reactions?: any;
  reactions?: any;
  pedagogical_steps?: any;
  design?: any;
  max_moment_kNm?: number;
  as_bottom_cm2?: number;
  as_top_cm2?: number;
}

export interface TabConfig {
  id: string;
  label: string;
  icon: LucideIcon;
  color: string;
}
