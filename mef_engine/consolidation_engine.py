"""
consolidation_engine.py — Módulo de Adensamento e Fluência do Solo

Implementa a Teoria de Adensamento de Terzaghi para previsão de recalques
ao longo do tempo em solos argilosos compressíveis.

Referências:
- Terzaghi, K. (1943). Theoretical Soil Mechanics.
- ABNT NBR 6122:2019 — Projeto e execução de fundações.
- Bowles, J.E. (1997). Foundation Analysis and Design.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from typing import List, Optional


@dataclass
class ConsolidationLayer:
    """Uma camada de solo compressível para análise de adensamento."""
    name: str = 'argila_mole'
    H_m: float = 5.0              # Espessura da camada compressível (m)
    Cc: float = 0.30              # Índice de compressão (adim)
    Cs: float = 0.05              # Índice de recompressão (swelling)
    e0: float = 1.20              # Índice de vazios inicial
    sigma_v0_kPa: float = 50.0   # Tensão vertical efetiva inicial (kPa)
    sigma_p_kPa: float = 80.0    # Tensão de pré-adensamento (kPa) — OCR-based
    Cv_m2_year: float = 1.5       # Coeficiente de adensamento vertical (m²/ano)
    C_alpha: float = 0.015        # Índice de compressão secundária (creep)
    drainage: str = 'double'      # 'single' ou 'double' (drenagem uni/bilateral)


@dataclass
class ConsolidationConfig:
    """Configuração global da análise de adensamento."""
    layers: list = field(default_factory=lambda: [ConsolidationLayer()])
    time_points_years: list = field(default_factory=lambda: [0.5, 1, 2, 5, 10, 25, 50])
    delta_sigma_kPa: float = 100.0  # Acréscimo de tensão pela fundação
    n_terms_fourier: int = 20        # Termos da série de Fourier para U(Tv)


def _degree_of_consolidation_1d(Tv: float, n_terms: int = 20) -> float:
    """
    Grau de adensamento U(Tv) pela solução exata de Terzaghi (série de Fourier).
    
    U(Tv) = 1 - Σ (2/M²) * exp(-M² * Tv)
    onde M = π/2 * (2m + 1)
    """
    if Tv <= 0:
        return 0.0
    if Tv > 3.0:
        return 1.0  # Praticamente 100% consolidado
    
    U = 0.0
    for m in range(n_terms):
        M = np.pi / 2.0 * (2 * m + 1)
        U += (2.0 / M**2) * np.exp(-M**2 * Tv)
    
    return float(np.clip(1.0 - U, 0.0, 1.0))


def _primary_settlement(
    layer: ConsolidationLayer,
    delta_sigma: float
) -> float:
    """
    Calcula o recalque primário total (Sp) usando a Teoria de Adensamento.
    
    Se sigma_v0 + delta_sigma <= sigma_p (solo OC, overconsolidated):
        Sp = (Cs / (1 + e0)) * H * log10((sigma_v0 + delta_sigma) / sigma_v0)
    
    Se sigma_v0 < sigma_p < sigma_v0 + delta_sigma (solo parcialmente OC):
        Sp = (Cs / (1+e0)) * H * log10(sigma_p / sigma_v0) +
             (Cc / (1+e0)) * H * log10((sigma_v0 + delta_sigma) / sigma_p)
    
    Se sigma_v0 >= sigma_p (solo NC, normally consolidated):
        Sp = (Cc / (1 + e0)) * H * log10((sigma_v0 + delta_sigma) / sigma_v0)
    """
    H = layer.H_m
    Cc = layer.Cc
    Cs = layer.Cs
    e0 = layer.e0
    sv0 = max(layer.sigma_v0_kPa, 1e-6)
    sp = max(layer.sigma_p_kPa, sv0)
    ds = max(delta_sigma, 0.0)
    
    svf = sv0 + ds
    
    if svf <= sp:
        # Solo overconsolidado (OC)
        settlement_m = (Cs / (1.0 + e0)) * H * np.log10(svf / sv0)
    elif sv0 < sp:
        # Parcialmente OC → NC
        settlement_m = (
            (Cs / (1.0 + e0)) * H * np.log10(sp / sv0) +
            (Cc / (1.0 + e0)) * H * np.log10(svf / sp)
        )
    else:
        # Solo NC (normalmente consolidado)
        settlement_m = (Cc / (1.0 + e0)) * H * np.log10(svf / sv0)
    
    return float(max(settlement_m, 0.0))


def _secondary_settlement(
    layer: ConsolidationLayer,
    t_years: float,
    t_primary_years: float
) -> float:
    """
    Calcula o recalque secundário (creep) após o fim do adensamento primário.
    
    Ss = C_alpha * H * log10(t / t_p)
    
    Só ocorre para t > t_primary (fim do adensamento primário ~90%).
    """
    if t_years <= t_primary_years or layer.C_alpha <= 0:
        return 0.0
    
    return float(layer.C_alpha * layer.H_m * np.log10(t_years / t_primary_years))


def _time_for_consolidation(layer: ConsolidationLayer, U_target: float = 0.90) -> float:
    """
    Calcula o tempo (em anos) para atingir U_target de adensamento primário.
    
    Para U > 60%: Tv ≈ -0.933 * ln(1 - U) - 0.085
    Para U ≤ 60%: Tv ≈ (π/4) * U²
    """
    if layer.drainage == 'double':
        Hdr = layer.H_m / 2.0
    else:
        Hdr = layer.H_m
    
    if U_target <= 0.60:
        Tv = (np.pi / 4.0) * U_target**2
    else:
        Tv = -0.933 * np.log(1.0 - U_target) - 0.085
    
    t_years = Tv * Hdr**2 / max(layer.Cv_m2_year, 1e-9)
    return float(t_years)


def run_consolidation_analysis(
    config: ConsolidationConfig,
) -> dict:
    """
    Executa a análise completa de adensamento para todas as camadas.
    
    Retorna:
    - settlement_vs_time: [{t_years, U_pct, settlement_primary_mm, settlement_secondary_mm, total_mm}]
    - total_primary_mm: recalque primário total final
    - total_secondary_mm: recalque secundário acumulado em t_final
    - t90_years: tempo para 90% de consolidação
    - layer_details: detalhamento por camada
    - classification: classificação do risco temporal
    """
    layers = config.layers
    delta_sigma = config.delta_sigma_kPa
    time_points = sorted(config.time_points_years)
    n_terms = config.n_terms_fourier
    
    # Recalque primário total por camada
    sp_total_mm = 0.0
    layer_details = []
    t90_max = 0.0
    
    for layer in layers:
        sp = _primary_settlement(layer, delta_sigma) * 1000.0  # mm
        t90 = _time_for_consolidation(layer, 0.90)
        t90_max = max(t90_max, t90)
        
        layer_details.append({
            'name': layer.name,
            'H_m': layer.H_m,
            'Cc': layer.Cc,
            'e0': layer.e0,
            'OCR': round(layer.sigma_p_kPa / max(layer.sigma_v0_kPa, 1e-6), 2),
            'settlement_primary_mm': round(sp, 2),
            't90_years': round(t90, 2),
            'C_alpha': layer.C_alpha,
        })
        sp_total_mm += sp
    
    # Curva recalque vs. tempo
    settlement_curve = []
    for t in time_points:
        w_primary = 0.0
        w_secondary = 0.0
        U_avg = 0.0
        
        for i, layer in enumerate(layers):
            sp_layer = layer_details[i]['settlement_primary_mm']
            t90_layer = layer_details[i]['t90_years']
            
            # Hdr = caminho de drenagem
            Hdr = layer.H_m / 2.0 if layer.drainage == 'double' else layer.H_m
            
            # Tv = Cv * t / Hdr²
            Tv = layer.Cv_m2_year * t / max(Hdr**2, 1e-9)
            U = _degree_of_consolidation_1d(Tv, n_terms)
            U_avg += U / len(layers)
            
            w_primary += U * sp_layer
            w_secondary += _secondary_settlement(layer, t, t90_layer)
        
        settlement_curve.append({
            't_years': t,
            'U_pct': round(U_avg * 100.0, 1),
            'settlement_primary_mm': round(w_primary, 2),
            'settlement_secondary_mm': round(w_secondary * 1000.0, 2),
            'total_mm': round(w_primary + w_secondary * 1000.0, 2),
        })
    
    # Classificação de risco temporal
    final_total = settlement_curve[-1]['total_mm'] if settlement_curve else 0.0
    ratio_secondary = (settlement_curve[-1]['settlement_secondary_mm'] / max(final_total, 1e-9)) if settlement_curve else 0.0
    
    if final_total > 100.0:
        classification = 'RISCO_CRITICO'
        note = 'Recalque total previsto > 100mm. Fundação profunda ou tratamento de solo obrigatório.'
    elif final_total > 50.0:
        classification = 'RISCO_ALTO'
        note = 'Recalque significativo ao longo do tempo. Monitorar com instrumentação.'
    elif ratio_secondary > 0.30:
        classification = 'ATENCAO_CREEP'
        note = 'Componente de fluência relevante. Avaliar solos orgânicos ou compressíveis.'
    elif t90_max > 10.0:
        classification = 'ATENCAO_TEMPORAL'
        note = 'Adensamento primário lento (> 10 anos). Considerar pré-carregamento.'
    else:
        classification = 'ADEQUADO'
        note = 'Recalque ao longo do tempo dentro dos limites usuais.'
    
    return {
        'settlement_vs_time': settlement_curve,
        'total_primary_mm': round(sp_total_mm, 2),
        'total_secondary_mm': round(settlement_curve[-1]['settlement_secondary_mm'], 2) if settlement_curve else 0.0,
        'final_total_mm': round(final_total, 2),
        't90_years': round(t90_max, 2),
        'layer_details': layer_details,
        'classification': classification,
        'summary': note,
        'delta_sigma_kPa': delta_sigma,
    }
