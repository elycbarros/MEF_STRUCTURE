"""
building_core.py — Modelagem de Núcleos Rígidos (Core) de Edifícios

Modela o sistema de contraventamento do edifício:
- Fosso de elevador (seção em "U", "C" ou retangular oca)
- Caixa de escada (paredes de cisalhamento)
- Paredes estruturais isoladas (shear walls)
- Combinação de núcleos para rigidez global

Calcula propriedades reais (Ix, Iy, J, centro de cisalhamento)
e alimenta: stability_engine.py, ssi_advanced.py, wind_engine.py

Referências:
- ABNT NBR 6118:2023 §15 — Instabilidade e efeitos de 2ª ordem.
- ABNT NBR 16858-1 — Elevadores (requisitos de fosso).
- ABNT NBR 9077 — Saídas de emergência (dimensões de escada).
- Timoshenko, S.P. — Theory of Elastic Stability.
- Smith, B.S. & Coull, A. (1991) — Tall Building Structures.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np
import math


# ──────────────────────── Geometrias de Seção ────────────────────────

@dataclass
class WallSegment:
    """Segmento de parede retangular posicionado no plano XY."""
    x_start: float     # início X (m)
    y_start: float     # início Y (m)
    x_end: float       # fim X (m)
    y_end: float       # fim Y (m)
    thickness: float   # espessura (m)

    @property
    def length(self) -> float:
        return math.sqrt((self.x_end - self.x_start)**2 + (self.y_end - self.y_start)**2)

    @property
    def area(self) -> float:
        return self.length * self.thickness

    @property
    def centroid(self) -> Tuple[float, float]:
        return ((self.x_start + self.x_end) / 2.0, (self.y_start + self.y_end) / 2.0)

    @property
    def angle_rad(self) -> float:
        return math.atan2(self.y_end - self.y_start, self.x_end - self.x_start)

    def local_inertias(self) -> Tuple[float, float]:
        """Inércias no sistema local da parede (forte e fraca)."""
        L = self.length
        t = self.thickness
        I_strong = t * L**3 / 12.0   # sobre eixo fraco (flexão no plano)
        I_weak = L * t**3 / 12.0     # sobre eixo forte (fora do plano)
        return I_strong, I_weak


@dataclass
class CoreSection:
    """
    Seção de núcleo rígido composta por segmentos de parede.
    Calcula propriedades geométricas no sistema global.
    """
    name: str = 'CORE_01'
    segments: List[WallSegment] = field(default_factory=list)
    fck: float = 35.0       # MPa
    E: float = 0.0          # Pa (se 0, calcula via fck)
    height: float = 3.0     # pé-direito do pavimento (m)
    n_floors: int = 1       # número de pavimentos

    def __post_init__(self):
        if self.E <= 0:
            self.E = 5600.0 * (self.fck ** 0.5) * 1e6

    @property
    def total_area(self) -> float:
        return sum(s.area for s in self.segments)

    @property
    def centroid(self) -> Tuple[float, float]:
        """Centro de gravidade da seção composta."""
        if not self.segments:
            return (0.0, 0.0)
        Ax = sum(s.area * s.centroid[0] for s in self.segments)
        Ay = sum(s.area * s.centroid[1] for s in self.segments)
        A = self.total_area
        return (Ax / max(A, 1e-9), Ay / max(A, 1e-9))

    def compute_properties(self) -> dict:
        """
        Calcula todas as propriedades geométricas e mecânicas:
        Ix, Iy, Ixy (inércias globais), J (torção), EI, GJ
        """
        cx, cy = self.centroid
        Ix = 0.0   # sobre eixo X passando pelo centróide
        Iy = 0.0   # sobre eixo Y passando pelo centróide
        Ixy = 0.0  # produto de inércia
        J = 0.0    # rigidez torcional (Saint-Venant)

        for seg in self.segments:
            A = seg.area
            sx, sy = seg.centroid
            dx = sx - cx
            dy = sy - cy
            angle = seg.angle_rad

            I_strong, I_weak = seg.local_inertias()

            # Rotação para sistema global (Steiner + rotação)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            Ix_local = I_strong * sin_a**2 + I_weak * cos_a**2
            Iy_local = I_strong * cos_a**2 + I_weak * sin_a**2
            Ixy_local = (I_strong - I_weak) * sin_a * cos_a

            # Steiner (transporte)
            Ix += Ix_local + A * dy**2
            Iy += Iy_local + A * dx**2
            Ixy += Ixy_local + A * dx * dy

            # Torção de Saint-Venant para seção retangular fina
            # J ≈ Σ (L × t³ / 3)
            J += seg.length * seg.thickness**3 / 3.0

        G = self.E / (2.0 * (1.0 + 0.20))  # G = E / 2(1+ν)

        return {
            'name': self.name,
            'area_m2': round(float(self.total_area), 4),
            'centroid_x_m': round(float(cx), 4),
            'centroid_y_m': round(float(cy), 4),
            'Ix_m4': float(Ix),
            'Iy_m4': float(Iy),
            'Ixy_m4': float(Ixy),
            'J_m4': float(J),
            'EIx_Nm2': float(self.E * Ix),
            'EIy_Nm2': float(self.E * Iy),
            'GJ_Nm2': float(G * J),
            'E_Pa': float(self.E),
            'G_Pa': float(G),
            'n_segments': len(self.segments),
        }


# ──────────────────────── Geometrias Pré-definidas ────────────────────────

def create_elevator_shaft(
    x0: float = 0.0, y0: float = 0.0,
    width: float = 2.50, depth: float = 2.50,
    wall_thickness: float = 0.20,
    open_side: str = 'south',  # porta: north, south, east, west
    fck: float = 35.0,
    n_floors: int = 40,
    name: str = 'FOSSO_ELEV'
) -> CoreSection:
    """
    Cria fosso de elevador com 3 paredes (1 lado aberto para porta).
    
    Seção em "U" invertido:
    ┌───────────┐
    │           │
    │  ELEVADOR │
    │           │
    └     ↑     ┘   ← porta (lado aberto)
    """
    w = width
    d = depth
    t = wall_thickness
    segments = []

    # Norte (topo)
    if open_side != 'north':
        segments.append(WallSegment(x0, y0 + d, x0 + w, y0 + d, t))
    # Sul (base)
    if open_side != 'south':
        segments.append(WallSegment(x0, y0, x0 + w, y0, t))
    # Oeste (esquerda)
    if open_side != 'west':
        segments.append(WallSegment(x0, y0, x0, y0 + d, t))
    # Leste (direita)
    if open_side != 'east':
        segments.append(WallSegment(x0 + w, y0, x0 + w, y0 + d, t))

    return CoreSection(name=name, segments=segments, fck=fck, n_floors=n_floors)


def create_stair_core(
    x0: float = 0.0, y0: float = 0.0,
    width: float = 3.00, depth: float = 6.00,
    wall_thickness: float = 0.20,
    has_central_wall: bool = True,  # parede central (divisória de lances)
    fck: float = 35.0,
    n_floors: int = 40,
    name: str = 'CAIXA_ESC'
) -> CoreSection:
    """
    Cria caixa de escada retangular com parede central opcional.
    
    ┌──────────────┐
    │   LANCE 1    │
    ├──────────────┤  ← parede central
    │   LANCE 2    │
    └──────────────┘
    """
    w = width
    d = depth
    t = wall_thickness
    segments = [
        WallSegment(x0, y0 + d, x0 + w, y0 + d, t),   # Norte
        WallSegment(x0, y0, x0 + w, y0, t),             # Sul
        WallSegment(x0, y0, x0, y0 + d, t),             # Oeste
        WallSegment(x0 + w, y0, x0 + w, y0 + d, t),     # Leste
    ]
    if has_central_wall:
        segments.append(WallSegment(x0, y0 + d/2, x0 + w, y0 + d/2, t))

    return CoreSection(name=name, segments=segments, fck=fck, n_floors=n_floors)


def create_shear_wall(
    x0: float = 0.0, y0: float = 0.0,
    length: float = 5.00,
    thickness: float = 0.20,
    direction: str = 'x',  # 'x' ou 'y'
    fck: float = 35.0,
    n_floors: int = 40,
    name: str = 'PAREDE_01'
) -> CoreSection:
    """Cria parede de cisalhamento isolada."""
    if direction == 'x':
        seg = WallSegment(x0, y0, x0 + length, y0, thickness)
    else:
        seg = WallSegment(x0, y0, x0, y0 + length, thickness)
    return CoreSection(name=name, segments=[seg], fck=fck, n_floors=n_floors)


# ──────────────────────── Rigidez Global do Edifício ────────────────────────

@dataclass
class BuildingBracingSystem:
    """
    Sistema completo de contraventamento do edifício.
    Combina múltiplos núcleos e paredes para calcular a rigidez global.
    """
    cores: List[CoreSection] = field(default_factory=list)
    total_height: float = 120.0     # altura total do edifício (m)
    n_floors: int = 40
    floor_weight_kN: float = 5000.0  # peso por pavimento (kN)

    def compute_global_stiffness(self) -> dict:
        """
        Calcula a rigidez equivalente do sistema de contraventamento.
        
        EI_total = Σ EI_i  (soma das contribuições de cada núcleo)
        GJ_total = Σ GJ_i  (resistência torcional)
        
        Aplica NBR 6118 §15.7.3:
        - Paredes/Núcleos: 0.8 × EI (não-linearidade física)
        """
        EIx_total = 0.0
        EIy_total = 0.0
        GJ_total = 0.0
        core_details = []

        NLF_FACTOR = 0.80  # NBR 6118: paredes e pilares-parede

        for core in self.cores:
            props = core.compute_properties()
            EIx = props['EIx_Nm2'] * NLF_FACTOR
            EIy = props['EIy_Nm2'] * NLF_FACTOR
            GJ = props['GJ_Nm2'] * NLF_FACTOR

            EIx_total += EIx
            EIy_total += EIy
            GJ_total += GJ

            core_details.append({
                'name': core.name,
                **props,
                'EIx_NLF_Nm2': EIx,
                'EIy_NLF_Nm2': EIy,
                'GJ_NLF_Nm2': GJ,
                'contribution_x_pct': 0.0,  # será calculado abaixo
                'contribution_y_pct': 0.0,
            })

        # Porcentagem de contribuição
        for d in core_details:
            d['contribution_x_pct'] = round(d['EIx_NLF_Nm2'] / max(EIx_total, 1e-9) * 100, 1)
            d['contribution_y_pct'] = round(d['EIy_NLF_Nm2'] / max(EIy_total, 1e-9) * 100, 1)

        # Deslocamento no topo sob vento unitário (1 kN)
        H = self.total_height
        delta_x_unit = H**3 / (3.0 * max(EIx_total, 1e-9))  # m/kN
        delta_y_unit = H**3 / (3.0 * max(EIy_total, 1e-9))

        # Frequência fundamental estimada (cantilever uniforme)
        # f1 = (1.875²) / (2π) × √(EI / (m × L⁴))
        mass_per_m = self.floor_weight_kN * 1000.0 / (9.81 * H)  # kg/m (peso → massa)
        EI_min = min(EIx_total, EIy_total)
        if mass_per_m > 0 and EI_min > 0:
            f1_hz = (1.875**2 / (2 * np.pi)) * np.sqrt(EI_min / (mass_per_m * H**4))
        else:
            f1_hz = 0.5

        # Classificação de rigidez
        drift_ratio = delta_x_unit * 100 / H  # drift/H por kN
        total_P = self.n_floors * self.floor_weight_kN

        return {
            'EIx_total_Nm2': float(EIx_total),
            'EIy_total_Nm2': float(EIy_total),
            'GJ_total_Nm2': float(GJ_total),
            'n_cores': len(self.cores),
            'core_details': core_details,
            'f1_estimated_Hz': round(float(f1_hz), 3),
            'delta_topo_mm_per_kN_x': round(float(delta_x_unit * 1000), 6),
            'delta_topo_mm_per_kN_y': round(float(delta_y_unit * 1000), 6),
            'total_weight_kN': float(total_P),
            'NLF_applied': True,
            'NLF_factor': NLF_FACTOR,
        }

    def get_stiffness_for_stability(self) -> dict:
        """
        Retorna EI e parâmetros formatados para stability_engine.py.
        """
        gs = self.compute_global_stiffness()
        EI_min = min(gs['EIx_total_Nm2'], gs['EIy_total_Nm2'])
        return {
            'stiffness_EI': EI_min / 1000.0,  # kN·m² (stability_engine usa kN)
            'f1_hz': gs['f1_estimated_Hz'],
            'total_weight_kN': gs['total_weight_kN'],
            'height_m': self.total_height,
        }

    def get_stiffness_for_ssi(self) -> dict:
        """
        Retorna parâmetros para ssi_advanced.py (rigidez por pilar).
        """
        gs = self.compute_global_stiffness()
        n_cores = max(len(self.cores), 1)
        EI_per_core = min(gs['EIx_total_Nm2'], gs['EIy_total_Nm2']) / n_cores
        k_rot = (4.0 * EI_per_core) / max(self.total_height / self.n_floors, 1.0)
        return {
            'k_rotational_per_core_Nm_rad': float(k_rot),
            'total_EI_Nm2': float(min(gs['EIx_total_Nm2'], gs['EIy_total_Nm2'])),
            'n_cores': n_cores,
        }


# ──────────────────────── Análise de Excentricidade (Torção) ────────────────────────

def check_torsion_eccentricity(
    building: BuildingBracingSystem,
    building_centroid: Tuple[float, float],
) -> dict:
    """
    Verifica a excentricidade entre o centro de rigidez e o centro de massa.
    
    Se e/L > 10%, o edifício tem tendência à torção sob vento.
    NBR 6118 exige consideração de excentricidade acidental de 5% de L.
    """
    gs = building.compute_global_stiffness()
    details = gs['core_details']

    # Centro de rigidez (ponderado por EI)
    EI_total_x = sum(d['EIx_NLF_Nm2'] for d in details)
    EI_total_y = sum(d['EIy_NLF_Nm2'] for d in details)

    cr_x = sum(d['centroid_x_m'] * d['EIy_NLF_Nm2'] for d in details) / max(EI_total_y, 1e-9)
    cr_y = sum(d['centroid_y_m'] * d['EIx_NLF_Nm2'] for d in details) / max(EI_total_x, 1e-9)

    cm_x, cm_y = building_centroid

    ex = abs(cr_x - cm_x)
    ey = abs(cr_y - cm_y)

    # Dimensões de referência do edifício
    all_x = [s.x_start for c in building.cores for s in c.segments] + \
            [s.x_end for c in building.cores for s in c.segments]
    all_y = [s.y_start for c in building.cores for s in c.segments] + \
            [s.y_end for c in building.cores for s in c.segments]
    Lx = max(all_x) - min(all_x) if all_x else 1.0
    Ly = max(all_y) - min(all_y) if all_y else 1.0

    ratio_x = ex / max(Lx, 1e-9)
    ratio_y = ey / max(Ly, 1e-9)

    # Classificação
    max_ratio = max(ratio_x, ratio_y)
    if max_ratio <= 0.05:
        classification = 'SIMETRICO'
        note = 'Núcleos bem posicionados. Torção mínima esperada.'
    elif max_ratio <= 0.10:
        classification = 'ACEITAVEL'
        note = 'Excentricidade dentro dos limites. Considerar excentricidade acidental (5%).'
    elif max_ratio <= 0.20:
        classification = 'ATENCAO'
        note = 'Excentricidade significativa. Verificar efeitos torsionais.'
    else:
        classification = 'CRITICO'
        note = 'Alta excentricidade. Risco de torção excessiva sob vento. Reavaliar posição dos núcleos.'

    return {
        'center_of_rigidity': {'x': round(cr_x, 3), 'y': round(cr_y, 3)},
        'center_of_mass': {'x': round(cm_x, 3), 'y': round(cm_y, 3)},
        'eccentricity_x_m': round(ex, 3),
        'eccentricity_y_m': round(ey, 3),
        'ratio_x_pct': round(ratio_x * 100, 1),
        'ratio_y_pct': round(ratio_y * 100, 1),
        'classification': classification,
        'note': note,
    }


# ──────────────────────── Pipeline ────────────────────────

def run_core_analysis(
    cores: list = None,
    building_Lx: float = 24.0,
    building_Ly: float = 24.0,
    n_floors: int = 40,
    floor_height: float = 3.0,
    floor_weight_kN: float = 5000.0,
    fck: float = 35.0,
) -> dict:
    """
    Análise completa do sistema de contraventamento.
    Se cores=None, cria um exemplo típico (fosso + escada centrais).
    """
    if cores is None:
        # Exemplo: fosso de elevador central + caixa de escada ao lado
        cx = building_Lx / 2.0
        cy = building_Ly / 2.0
        cores = [
            create_elevator_shaft(cx - 1.25, cy - 1.25, 2.50, 2.50, 0.20,
                                  fck=fck, n_floors=n_floors, name='FOSSO_ELEV_01'),
            create_stair_core(cx + 2.0, cy - 3.0, 3.00, 6.00, 0.20,
                              fck=fck, n_floors=n_floors, name='CAIXA_ESC_01'),
        ]

    total_height = n_floors * floor_height

    building = BuildingBracingSystem(
        cores=cores,
        total_height=total_height,
        n_floors=n_floors,
        floor_weight_kN=floor_weight_kN,
    )

    global_stiffness = building.compute_global_stiffness()
    stability_params = building.get_stiffness_for_stability()
    ssi_params = building.get_stiffness_for_ssi()

    torsion = check_torsion_eccentricity(
        building,
        building_centroid=(building_Lx / 2.0, building_Ly / 2.0),
    )

    return {
        'global_stiffness': global_stiffness,
        'stability_params': stability_params,
        'ssi_params': ssi_params,
        'torsion_check': torsion,
        'summary': {
            'n_cores': len(cores),
            'total_height_m': total_height,
            'EIx_MNm2': round(global_stiffness['EIx_total_Nm2'] / 1e6, 1),
            'EIy_MNm2': round(global_stiffness['EIy_total_Nm2'] / 1e6, 1),
            'f1_Hz': global_stiffness['f1_estimated_Hz'],
            'torsion_class': torsion['classification'],
        }
    }


if __name__ == '__main__':
    import json
    result = run_core_analysis(n_floors=40, fck=35)
    print(json.dumps(result['summary'], indent=2))
    print(json.dumps(result['torsion_check'], indent=2))
    print(f"\nEI para stability_engine: {result['stability_params']['stiffness_EI']:.0f} kN·m²")
    print(f"K_rot para SSI: {result['ssi_params']['k_rotational_per_core_Nm_rad']:.0f} N·m/rad")
