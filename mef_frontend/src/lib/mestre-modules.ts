import { 
  Box, 
  Columns, 
  Grid3X3, 
  ArrowUpRight, 
  Square, 
  Layers, 
  Waves,
  Activity,
  Anchor,
  Triangle,
  Layout,
  Maximize2,
  Share2,
  Search,
  Wind,
  BookOpen,
  Zap,
  GitBranch,
  Network,
  LucideIcon
} from 'lucide-react';
import { MestreElementType } from './mestre-types';
import React from 'react';

// Import components (using dynamic imports or direct imports)
// Since they are currently used in page.tsx, we can import them here.
// Note: These paths are relative to src/lib/
import { BeamPlayground } from '@/app/(app)/mestre/components/BeamPlayground';
import { BeamCrossPlayground } from '@/app/(app)/mestre/components/BeamCrossPlayground';
import { ColumnPlayground } from '@/app/(app)/mestre/components/ColumnPlayground';
import { SlabPlayground } from '@/app/(app)/mestre/components/SlabPlayground';
import { PilePlayground } from '@/app/(app)/mestre/components/PilePlayground';
import { PileCapPlayground } from '@/app/(app)/mestre/components/PileCapPlayground';
import { FootingPlayground } from '@/app/(app)/mestre/components/FootingPlayground';
import { SpecialPlayground } from '@/app/(app)/mestre/components/SpecialPlayground';
import { SptPlayground } from '@/app/(app)/mestre/components/SptPlayground';
import { StabilityPlayground } from '@/app/(app)/mestre/components/StabilityPlayground';
import { WindPlayground } from '@/app/(app)/mestre/components/WindPlayground';
import { FramePlayground } from '@/app/(app)/mestre/components/FramePlayground';
import { TrussPlayground } from '@/app/(app)/mestre/components/TrussPlayground';
import { TensionProPlayground } from '@/app/(app)/mestre/components/TensionProPlayground';
import { AdvancedSlabPlayground } from '@/app/(app)/mestre/components/AdvancedSlabPlayground';

export type MestreCategory = 
  | "Elementos NBR 6118"
  | "Fundações"
  | "Sistemas"
  | "Módulos Especiais";

export interface MestreModuleDefinition {
  id: MestreElementType | string;
  label: string;
  icon: LucideIcon;
  category: MestreCategory;
  component?: React.ComponentType;
  disabled?: boolean;
}

export const MESTRE_CATEGORIES: MestreCategory[] = [
  "Elementos NBR 6118",
  "Fundações",
  "Sistemas",
  "Módulos Especiais"
];

export const MESTRE_MODULES: MestreModuleDefinition[] = [
  // Elementos NBR 6118
  { id: 'beam', label: 'Viga Isolada', icon: Box, category: 'Elementos NBR 6118', component: BeamPlayground },
  { id: 'column', label: 'Pilar (Flexo)', icon: Columns, category: 'Elementos NBR 6118', component: ColumnPlayground },
  { id: 'slab', label: 'Laje', icon: Grid3X3, category: 'Elementos NBR 6118', component: SlabPlayground },
  { id: 'stair', label: 'Escada', icon: ArrowUpRight, category: 'Elementos NBR 6118', component: SpecialPlayground },
  { id: 'helical_stairs', label: 'Escada Helicoidal', icon: ArrowUpRight, category: 'Elementos NBR 6118', component: SpecialPlayground },
  { id: 'concrete_wall', label: 'Parede de Concreto', icon: Columns, category: 'Elementos NBR 6118', component: SpecialPlayground },
  { id: 'corbel', label: 'Consolo Curto', icon: Layout, category: 'Elementos NBR 6118', component: SpecialPlayground },
  { id: 'gerber_tooth', label: 'Dente Gerber', icon: Activity, category: 'Elementos NBR 6118', component: SpecialPlayground },
  { id: 'deep_beam', label: 'Viga Parede', icon: Maximize2, category: 'Elementos NBR 6118', component: SpecialPlayground },

  // Fundações
  { id: 'footing', label: 'Sapata Isolada', icon: Square, category: 'Fundações', component: FootingPlayground },
  { id: 'pile', label: 'Estaca', icon: Anchor, category: 'Fundações', component: PilePlayground },
  { id: 'pile_cap', label: 'Bloco sobre Estacas', icon: Triangle, category: 'Fundações', component: PileCapPlayground },
  { id: 'retaining_wall', label: 'Muro Arrimo', icon: Layers, category: 'Fundações', component: SpecialPlayground },
  { id: 'spt', label: 'Sondagem SPT', icon: Search, category: 'Fundações', component: SptPlayground },
  { id: 'advanced_slab', label: 'Radier Avançado', icon: Grid3X3, category: 'Fundações', component: AdvancedSlabPlayground },

  // Sistemas
  { id: 'frames', label: 'Pórticos', icon: GitBranch, category: 'Sistemas', component: FramePlayground },
  { id: 'trusses', label: 'Treliças', icon: Network, category: 'Sistemas', component: TrussPlayground },
  { id: 'stability', label: 'Estabilidade γz', icon: Activity, category: 'Sistemas', component: StabilityPlayground },
  { id: 'wind', label: 'Vento / NBR 6123', icon: Wind, category: 'Sistemas', component: WindPlayground },

  // Módulos Especiais
  { id: 'beam_cross', label: 'Viga Cross', icon: Share2, category: 'Módulos Especiais', component: BeamCrossPlayground },
  { id: 'tension_pro', label: 'Tension Pro', icon: Zap, category: 'Módulos Especiais', component: TensionProPlayground },
  { id: 'reservoir', label: 'Reservatório', icon: Waves, category: 'Módulos Especiais', component: SpecialPlayground },
  { id: 'tech_library', label: 'Biblioteca Técnica', icon: BookOpen, category: 'Módulos Especiais', disabled: true },
];

export function getMestreModule(id: string): MestreModuleDefinition | undefined {
  return MESTRE_MODULES.find(m => m.id === id);
}

export function getModulesByCategory(category: MestreCategory): MestreModuleDefinition[] {
  return MESTRE_MODULES.filter(m => m.category === category);
}
