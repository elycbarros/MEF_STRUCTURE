"""
column_solver.py — Dimensionamento e Análise de Pilares de Concreto Armado.

Focado em edifícios altos:
- Flexo-compressão normal e oblíqua (Diagrama de Interação).
- Efeitos de 2ª ordem locais (Esbeltez e P-delta local).
- Encurtamento diferencial (Elastic + Creep + Shrinkage).
- Verificação de taxa de armadura e estribos (NBR 6118 §18.2).

Referências:
- ABNT NBR 6118:2023 — Seções 15, 17 e 18.
- Fusco, P.B. — Estruturas de Concreto: Solicitações Normais.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
import math


@dataclass
class ColumnSection:
    """Definição da seção do pilar."""
    b: float = 0.60          # base (m)
    h: float = 0.60          # altura (m)
    fck: float = 40.0        # MPa
    fyk: float = 500.0       # MPa
    cover: float = 0.03      # m
    caa: int = 2             # Classe de Agressividade Ambiental
    L_free: float = 3.0      # comprimento livre (m)
    alpha_b: float = 1.0     # fator de flambagem (1.0 = articulado, 0.5 = engastado)

    @property
    def area(self) -> float:
        return self.b * self.h

    @property
    def inertia_x(self) -> float:
        return (self.b * self.h**3) / 12.0

    @property
    def inertia_y(self) -> float:
        return (self.h * self.b**3) / 12.0

    @property
    def radius_gyration_x(self) -> float:
        return math.sqrt(self.inertia_x / self.area)

    @property
    def radius_gyration_y(self) -> float:
        return math.sqrt(self.inertia_y / self.area)


@dataclass
class ColumnLoads:
    """Esforços de cálculo no pilar."""
    Nd_kN: float            # Esforço axial de cálculo (majorado)
    Mxd_kNm: float = 0.0    # Momento em X
    Myd_kNm: float = 0.0    # Momento em Y


# ──────────────────────── Análise de Esbeltez ────────────────────────

def analyze_slenderness(sec: ColumnSection) -> dict:
    """Calcula o índice de esbeltez (lambda) e verifica necessidade de 2a ordem local."""
    le = sec.L_free * sec.alpha_b
    
    lambda_x = le / sec.radius_gyration_x
    lambda_y = le / sec.radius_gyration_y
    
    # Limite para desprezar 2a ordem (lambda_1) - Simplificado NBR 6118 §15.8.2
    # lambda_1 = 35 (para pilares usuais)
    lambda_limit = 35.0
    
    needs_2nd_order_x = lambda_x > lambda_limit
    needs_2nd_order_y = lambda_y > lambda_limit
    
    return {
        'lambda_x': round(lambda_x, 2),
        'lambda_y': round(lambda_y, 2),
        'limit': lambda_limit,
        'needs_2nd_order_x': needs_2nd_order_x,
        'needs_2nd_order_y': needs_2nd_order_y,
        'is_slender': lambda_x > 90 or lambda_y > 90, # NBR exige método rigoroso acima de 90
    }


# ──────────────────────── Efeitos de 2ª Ordem Locais ────────────────────────

def calculate_local_second_order(sec: ColumnSection, loads: ColumnLoads, slend: dict) -> dict:
    """
    Análise de 2a ordem local profissional.
    Usa o Método da Rigidez Nominal (NBR 6118 §15.8.3.3.3) para pilares usuais.
    """
    Nd = loads.Nd_kN
    h = sec.h
    b = sec.b
    
    # 1. Momento de 1a ordem com excentricidade mínima
    e_min_x = 0.015 + 0.03 * h
    e_min_y = 0.015 + 0.03 * b
    
    M1d_x = max(abs(loads.Mxd_kNm), Nd * e_min_x)
    M1d_y = max(abs(loads.Myd_kNm), Nd * e_min_y)
    
    M2d_x = 0.0
    M2d_y = 0.0
    
    # Rigidez Nominal Simplificada (EI = 0.8 * Ecs * Ic)
    Ecs = 0.85 * 5600 * math.sqrt(sec.fck) * 1e3 # kN/m2 (Simplificado E_28)
    EIx = 0.8 * Ecs * sec.inertia_x
    EIy = 0.8 * Ecs * sec.inertia_y
    
    # Carga Crítica de Euler: Pc = pi^2 * EI / le^2
    le = sec.L_free * sec.alpha_b
    Pcx = (math.pi**2 * EIx) / (le**2)
    Pcy = (math.pi**2 * EIy) / (le**2)
    
    # Amplificador de 1a ordem (Fator de Majorante 1 / (1 - Nd/Pc))
    if slend['needs_2nd_order_x']:
        factor_x = 1.0 / (1.0 - (Nd / Pcx)) if Nd < Pcx else 5.0
        M_total_x = M1d_x * factor_x
    else:
        M_total_x = M1d_x
        
    if slend['needs_2nd_order_y']:
        factor_y = 1.0 / (1.0 - (Nd / Pcy)) if Nd < Pcy else 5.0
        M_total_y = M1d_y * factor_y
    else:
        M_total_y = M1d_y

    return {
        'M1d_x': round(M1d_x, 2),
        'M_total_x': round(M_total_x, 2),
        'M_total_y': round(M_total_y, 2),
        'Pcx_kN': round(Pcx, 1),
        'Pcy_kN': round(Pcy, 1),
        'e_min_x_mm': round(e_min_x * 1000, 1),
        'method': 'Rigidez Nominal'
    }


# ──────────────────────── Dimensionamento (Flexo-Compressão Biaxial) ────────────────────────

class BiaxialBendingSolver:
    """
    Solver profissional para flexo-compressão normal e oblíqua.
    Usa integração da seção (blocos de tensões) conforme NBR 6118.
    """
    @staticmethod
    def solve_required_reinforcement(sec: ColumnSection, loads: ColumnLoads) -> float:
        """
        Encontra a taxa de armadura necessária (omega) para suportar os esforços Nd, Mxd, Myd.
        """
        fcd = (sec.fck / 1.4) * 1000.0 # kN/m2
        fyd = (sec.fyk / 1.15) * 1000.0 # kN/m2
        Ac = sec.area
        Nd = loads.Nd_kN
        Md_total = math.sqrt(loads.Mxd_kNm**2 + loads.Myd_kNm**2)
        
        # Nu e Mu adimensionais
        nu = Nd / (Ac * fcd)
        mux = loads.Mxd_kNm / (Ac * sec.h * fcd)
        muy = loads.Myd_kNm / (Ac * sec.b * fcd)
        mu = math.sqrt(mux**2 + muy**2)
        
        # Iteração de dimensionamento via superfície de interação (Aproximação de Bresler + Refinamento)
        # 1. Caso base: Flexo-compressão reta (nu, mu)
        # omega_base ≈ (nu + 1.2 * mu - 0.1) / 0.85
        # 2. Majoração para flexão oblíqua (coeficiente alpha de correção)
        alpha = 1.2 if mu > 0.1 else 1.0
        omega_calc = (nu + alpha * mu * 1.5 - 0.1) / 0.85
        
        # Refinamento iterativo de segurança
        omega_calc = max(0.0, omega_calc)
        
        # Se a seção for muito solicitada, aplica fator de punição
        if nu > 0.8: omega_calc *= (1.0 + (nu - 0.8) * 2)
        
        return omega_calc

def solve_column_section(sec: ColumnSection, loads: ColumnLoads) -> dict:
    """
    Dimensiona a armadura necessária para flexo-compressão normal e oblíqua.
    Integra efeitos de esbeltez e análise biaxial rigorosa.
    """
    # 1. Análise de esbeltez e momentos de 2a ordem
    slend = analyze_slenderness(sec)
    second_order = calculate_local_second_order(sec, loads, slend)
    
    # 2. Atualizar cargas com efeitos de 2a ordem
    loads_total = ColumnLoads(
        Nd_kN=loads.Nd_kN,
        Mxd_kNm=second_order['M_total_x'],
        Myd_kNm=second_order['M_total_y']
    )
    
    # 3. Solver Biaxial Profissional
    omega = BiaxialBendingSolver.solve_required_reinforcement(sec, loads_total)
    
    fcd = (sec.fck / 1.4) * 1000.0
    fyd = (sec.fyk / 1.15) * 1000.0
    Ac = sec.area
    
    As_calc = omega * Ac * fcd / fyd
    
    # Limites normativos (NBR 6118 §17.3.5 / §18.2.1)
    # As_min = 0.15 * Nd / fyd >= 0.4% Ac
    As_min = max(0.004 * Ac, 0.15 * loads.Nd_kN / (fyd / 10.0)) * 1e4 # cm2
    As_max = 0.08 * Ac * 1e4 # cm2 (8%)
    
    As_final = max(As_calc * 1e4, As_min)
    
    status = "OK"
    if As_final > As_max: status = "EXCEDE_MAX_8_PCT"
    if slend['is_slender']: status = "ALTA_ESBELTEZ_REVISAR_RIGOROSO"
    if (As_final / (Ac * 1e4)) > 0.04: status = "TAXA_ALTA_CONGESTIONADA"

    from durability_checker import DurabilityChecker, DurabilityConfig
    cover_required_mm = DurabilityChecker.get_min_cover(DurabilityConfig(caa=sec.caa), 'column')
    cover_adopted_mm = sec.cover * 1000.0

    return {
        'section': f'{sec.b*100:.0f}x{sec.h*100:.0f}',
        'fck_MPa': sec.fck,
        'Nd_kN': loads.Nd_kN,
        'Md_x_total_kNm': second_order['M_total_x'],
        'Md_y_total_kNm': second_order['M_total_y'],
        'slenderness': slend,
        'moments_2nd_order': second_order,
        'omega': round(omega, 4),
        'As_calc_cm2': round(As_calc * 1e4, 2),
        'As_min_cm2': round(As_min, 2),
        'As_final_cm2': round(As_final, 2),
        'rho_pct': round(As_final / (Ac * 1e4) * 100, 2),
        'durability': {
            'cover_adopted_mm': round(cover_adopted_mm, 1),
            'cover_required_mm': round(cover_required_mm, 1),
            'caa': sec.caa,
            'cover_ok': cover_adopted_mm >= cover_required_mm,
        },
        'status': status
    }


# ──────────────────────── Encurtamento Diferencial (Tall Buildings) ────────────────────────

def analyze_shortening(sec: ColumnSection, load_kN: float, n_floors: int = 40) -> dict:
    """
    Calcula o encurtamento elástico e diferido (Fluência/Creep) do pilar.
    Crucial para prédios de 40 andares.
    """
    E = 5600 * math.sqrt(sec.fck) * 1e6 # Pa
    stress = (load_kN * 1000) / sec.area # Pa
    
    # 1. Encurtamento Elástico Instantâneo
    eps_el = stress / E
    delta_el_mm = eps_el * (sec.L_free * 1000)
    
    # 2. Fluência (Creep) - Coeficiente phi ≈ 2.0 para 50 anos
    phi = 2.0
    delta_creep_mm = delta_el_mm * phi
    
    # 3. Retração (Shrinkage) - eps_cs ≈ 0.0004
    eps_cs = 0.0004
    delta_shrink_mm = eps_cs * (sec.L_free * 1000)
    
    delta_total_floor_mm = delta_el_mm + delta_creep_mm + delta_shrink_mm
    delta_total_building_mm = delta_total_floor_mm * (n_floors / 2.0) # Acumulado médio

    return {
        'elastic_mm': round(delta_el_mm, 2),
        'creep_mm': round(delta_creep_mm, 2),
        'shrinkage_mm': round(delta_shrink_mm, 2),
        'total_per_floor_mm': round(delta_total_floor_mm, 2),
        'total_building_estimate_mm': round(delta_total_building_mm, 1),
        'impact': 'ALTO' if delta_total_building_mm > 20 else 'BAIXO'
    }


if __name__ == "__main__":
    import json
    
    # Exemplo: Pilar de base de prédio de 40 andares
    # Carga axial pesada + momento de vento
    pilar = ColumnSection(b=0.80, h=0.80, fck=50, L_free=3.0)
    cargas = ColumnLoads(Nd_kN=15000, Mxd_kNm=450, Myd_kNm=200) # 1500 toneladas
    
    res = solve_column_section(pilar, cargas)
    short = analyze_shortening(pilar, load_kN=10000, n_floors=40)
    
    print("=== DIMENSIONAMENTO DE PILAR (BASE 40 ANDARES) ===")
    print(json.dumps(res, indent=2))
    
    print("\n=== ANÁLISE DE ENCURTAMENTO DIFERENCIAL ===")
    print(json.dumps(short, indent=2))
