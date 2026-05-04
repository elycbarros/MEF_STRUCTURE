"""
pile_group_interaction.py — Efeito de Grupo de Estacas (Poulos & Davis / Randolph & Wroth)

Implementa fatores de interação estaca-estaca para radiers estaqueados,
reduzindo a rigidez efetiva de estacas em grupos densos pela sobreposição
de bulbos de tensão no solo.

Referências:
- Poulos, H.G. & Davis, E.H. (1980). Pile Foundation Analysis and Design.
- Randolph, M.F. & Wroth, C.P. (1979). An analysis of the deformation of vertically loaded piles.
- NBR 6122:2019 — Projeto e execução de fundações.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import List, Optional


@dataclass
class PileGroupConfig:
    """Parâmetros para análise de grupo de estacas."""
    Es_kPa: float = 30_000.0       # Módulo de elasticidade do solo (kPa)
    nu_soil: float = 0.30           # Coeficiente de Poisson do solo
    pile_type: str = 'friction'     # 'friction' ou 'end_bearing'
    Ep_kPa: float = 30_000_000.0   # Módulo do concreto da estaca (kPa)
    min_efficiency: float = 0.30    # Eficiência mínima do grupo (safety floor)


def _interaction_factor_poulos(
    s: float, d: float, L: float, Es: float, Ep: float, nu: float,
    pile_type: str = 'friction'
) -> float:
    """
    Calcula o fator de interação alpha entre duas estacas (Poulos, 1968/1980).
    
    s: espaçamento entre eixos (m)
    d: diâmetro da estaca (m)
    L: comprimento da estaca (m)
    Es: módulo do solo (kPa)
    Ep: módulo da estaca (kPa)
    nu: Poisson do solo
    
    Retorna alpha ∈ [0, 1]: 0 = sem interação, 1 = interação total.
    
    Modelo simplificado baseado na solução de Randolph & Wroth (1979):
    alpha ≈ ln(r_m / s) / ln(r_m / r_0)
    onde r_m = 2.5 * L * (1 - nu) e r_0 = d/2
    """
    if s <= 0 or d <= 0 or L <= 0:
        return 0.0
    
    r_0 = d / 2.0
    # Raio de influência máximo (Randolph & Wroth)
    r_m = 2.5 * L * (1.0 - nu)
    
    if s >= r_m:
        return 0.0  # Sem interação a grandes distâncias
    
    if s <= r_0:
        return 1.0  # Estacas se tocam
    
    # Fator de interação logarítmico
    alpha = np.log(r_m / s) / np.log(r_m / r_0)
    
    # Ajuste para estacas de ponta vs. atrito
    if pile_type == 'end_bearing':
        alpha *= 0.5  # Estacas de ponta têm menor interação lateral
    
    return float(np.clip(alpha, 0.0, 1.0))


def compute_interaction_matrix(
    piles: list,
    config: PileGroupConfig
) -> np.ndarray:
    """
    Constrói a matriz de interação [n x n] para o grupo de estacas.
    
    alpha_ij = fator de interação entre estaca i e j
    Diagonal = 1.0 (auto-interação)
    
    O recalque do grupo é: w_group = [alpha] * w_isolated
    """
    n = len(piles)
    alpha = np.eye(n, dtype=float)
    
    for i in range(n):
        for j in range(i + 1, n):
            dx = piles[i].x - piles[j].x
            dy = piles[i].y - piles[j].y
            s = np.sqrt(dx**2 + dy**2)
            
            # Usar a média dos diâmetros e comprimentos
            d_avg = (piles[i].diameter_m + piles[j].diameter_m) / 2.0
            L_avg = (piles[i].length_m + piles[j].length_m) / 2.0
            
            a = _interaction_factor_poulos(
                s, d_avg, L_avg,
                config.Es_kPa, config.Ep_kPa, config.nu_soil,
                config.pile_type
            )
            alpha[i, j] = a
            alpha[j, i] = a
    
    return alpha


def compute_group_efficiency(
    piles: list,
    config: PileGroupConfig
) -> dict:
    """
    Calcula a eficiência do grupo de estacas.
    
    Eficiência η = 1 / (soma da coluna da matriz de interação / n)
    
    Retorna:
    - efficiency_per_pile: η individual por estaca
    - group_efficiency: η global do grupo
    - stiffness_reduction: fator de redução da rigidez (k_group = k_isolated * reduction)
    - interaction_matrix: matriz alpha completa
    """
    if not piles or len(piles) < 2:
        return {
            'efficiency_per_pile': [1.0] * len(piles) if piles else [],
            'group_efficiency': 1.0,
            'stiffness_reduction': np.ones(len(piles)) if piles else np.array([]),
            'interaction_matrix': np.eye(len(piles)) if piles else np.array([[]]),
            'settlement_amplification': 1.0,
            'summary': 'Estaca isolada ou sem estacas — sem efeito de grupo.'
        }
    
    alpha = compute_interaction_matrix(piles, config)
    n = len(piles)
    
    # Fator de amplificação de recalque por estaca = soma da coluna alpha
    settlement_factors = alpha.sum(axis=1)  # Cada estaca "sente" a influência de todas as outras
    
    # Eficiência por estaca: quanto da rigidez isolada permanece
    # k_eff = k_isolated / settlement_factor
    efficiency_per_pile = 1.0 / settlement_factors
    
    # Aplicar piso de eficiência
    efficiency_per_pile = np.maximum(efficiency_per_pile, config.min_efficiency)
    
    # Eficiência global do grupo
    group_efficiency = float(np.mean(efficiency_per_pile))
    
    # Fator de redução da rigidez para injetar no solver
    stiffness_reduction = efficiency_per_pile.copy()
    
    # Amplificação global de recalque
    settlement_amplification = float(np.mean(settlement_factors))
    
    # Classificação
    if group_efficiency >= 0.85:
        classification = 'GRUPO_EFICIENTE'
        note = 'Espaçamento adequado — interação mínima entre estacas.'
    elif group_efficiency >= 0.60:
        classification = 'GRUPO_MODERADO'
        note = 'Interação moderada — considerar redistribuição de cargas.'
    else:
        classification = 'GRUPO_INEFICIENTE'
        note = 'Alta sobreposição de bulbos — reavaliar espaçamento ou diâmetros.'
    
    return {
        'efficiency_per_pile': efficiency_per_pile.tolist(),
        'group_efficiency': round(group_efficiency, 4),
        'stiffness_reduction': stiffness_reduction,
        'interaction_matrix': alpha,
        'settlement_amplification': round(settlement_amplification, 4),
        'classification': classification,
        'summary': note
    }


def apply_group_effect_to_piles(piles: list, config: PileGroupConfig) -> list:
    """
    Aplica o efeito de grupo, reduzindo a rigidez efetiva de cada estaca.
    Retorna a lista de estacas com stiffness_kN_m ajustada.
    """
    if not piles or len(piles) < 2:
        return piles
    
    result = compute_group_efficiency(piles, config)
    reduction = result['stiffness_reduction']
    
    for i, pile in enumerate(piles):
        original_k = getattr(pile, 'stiffness_kN_m', 0.0) or 0.0
        pile.stiffness_kN_m = original_k * float(reduction[i])
    
    return piles
"""
consolidation_engine.py — Módulo de Adensamento e Fluência do Solo

Implementa a Teoria de Adensamento de Terzaghi para previsão de recalques
ao longo do tempo em solos argilosos compressíveis.

Referências:
- Terzaghi, K. (1943). Theoretical Soil Mechanics.
- ABNT NBR 6122:2019 — Projeto e execução de fundações.
- Bowles, J.E. (1997). Foundation Analysis and Design.
"""
