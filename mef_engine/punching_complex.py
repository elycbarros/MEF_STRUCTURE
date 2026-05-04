"""
punching_complex.py — Punção em Geometrias Complexas (Shafts, Recortes, Furos)

Motor de cálculo de perímetros críticos de punção para casos não-retangulares,
incluindo detecção automática de aberturas (shafts de elevador, furos de passagem)
e recortes em "L" ou "T" próximos aos pilares.

Referências:
- ABNT NBR 6118:2023, Seção 19.5 — Punção.
- EN 1992-1-1:2004 (Eurocode 2), Seção 6.4 — Punching.
- ACI 318-25, Seção 22.6 — Two-way shear.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import List, Optional, Tuple


@dataclass
class Opening:
    """Representa uma abertura (shaft, furo) no radier."""
    id: str = 'SHAFT_01'
    x_min: float = 0.0    # Canto inferior esquerdo X
    y_min: float = 0.0
    x_max: float = 1.0    # Canto superior direito X
    y_max: float = 1.0
    opening_type: str = 'shaft'  # 'shaft', 'hole', 'recess'


@dataclass
class ComplexPunchingResult:
    """Resultado da verificação de punção com geometria complexa."""
    column_id: str
    u1_original_m: float     # Perímetro C' original (sem deduções)
    u1_reduced_m: float      # Perímetro C' após dedução por aberturas
    deduction_m: float       # Comprimento total deduzido
    deduction_pct: float     # % de redução
    openings_affecting: list  # IDs das aberturas que afetam
    tau_sd_original_MPa: float
    tau_sd_corrected_MPa: float
    impact_ratio: float      # tau_corrected / tau_original
    is_critical: bool        # Se a correção muda o veredito
    geometry_notes: list      # Observações de engenharia


def _point_in_rect(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> bool:
    """Verifica se ponto (px,py) está dentro de retângulo [x1,y1] -> [x2,y2]."""
    return x1 <= px <= x2 and y1 <= py <= y2


def _rect_overlap(
    ax1: float, ay1: float, ax2: float, ay2: float,
    bx1: float, by1: float, bx2: float, by2: float
) -> Tuple[float, float, float, float]:
    """
    Calcula a interseção de dois retângulos.
    Retorna (ox1, oy1, ox2, oy2) ou None se não há sobreposição.
    """
    ox1 = max(ax1, bx1)
    oy1 = max(ay1, by1)
    ox2 = min(ax2, bx2)
    oy2 = min(ay2, by2)
    
    if ox1 < ox2 and oy1 < oy2:
        return (ox1, oy1, ox2, oy2)
    return None


def _perimeter_deduction_for_opening(
    col_x: float, col_y: float,
    bx: float, by: float,
    d: float, offset_factor: float,
    opening: Opening
) -> Tuple[float, list]:
    """
    Calcula a dedução no perímetro C' (u1) causada por uma abertura.
    
    Regra NBR 6118 / Eurocode 2:
    1. Traçar linhas radiais do centro do pilar tangentes à abertura.
    2. O arco do perímetro C' interceptado entre essas tangentes é deduzido.
    
    Implementação simplificada (retangular):
    - Verificar se a abertura está dentro da zona de influência (2d do pilar).
    - Calcular o ângulo subtendido pelas tangentes.
    - Deduzir o arco correspondente do perímetro C'.
    """
    notes = []
    
    # Zona de influência = retângulo do pilar expandido por offset_factor * d
    offset = offset_factor * d
    zone_x1 = col_x - bx / 2.0 - offset
    zone_x2 = col_x + bx / 2.0 + offset
    zone_y1 = col_y - by / 2.0 - offset
    zone_y2 = col_y + by / 2.0 + offset
    
    # Verificar sobreposição da abertura com a zona de influência
    overlap = _rect_overlap(
        zone_x1, zone_y1, zone_x2, zone_y2,
        opening.x_min, opening.y_min, opening.x_max, opening.y_max
    )
    
    if overlap is None:
        return 0.0, [f'Abertura {opening.id} fora da zona de influência ({offset_factor}d)']
    
    # Calcular dedução baseada no ângulo subtendido
    ox1, oy1, ox2, oy2 = overlap
    
    # Centro do pilar
    cx, cy = col_x, col_y
    
    # Cantos da abertura mais próximos ao perímetro C'
    # Calcular ângulos das tangentes a partir do centro do pilar
    corners = [
        (opening.x_min, opening.y_min),
        (opening.x_max, opening.y_min),
        (opening.x_max, opening.y_max),
        (opening.x_min, opening.y_max),
    ]
    
    angles = []
    for (px, py) in corners:
        dx = px - cx
        dy = py - cy
        if abs(dx) > 1e-9 or abs(dy) > 1e-9:
            angles.append(np.arctan2(dy, dx))
    
    if len(angles) < 2:
        return 0.0, [f'Abertura {opening.id}: ângulos insuficientes para dedução']
    
    # Arco subtendido = diferença entre ângulos extremos
    angles = sorted(angles)
    arc_angle = angles[-1] - angles[0]
    
    # Garantir que o arco é o menor dos dois possíveis
    if arc_angle > np.pi:
        arc_angle = 2 * np.pi - arc_angle
    
    # Raio médio do perímetro C'
    r_avg = (bx + by) / 4.0 + offset  # Aproximação para pilar retangular
    
    # Comprimento do arco deduzido
    deduction = arc_angle * r_avg
    
    notes.append(
        f'Abertura {opening.id} ({opening.opening_type}): '
        f'arco={np.degrees(arc_angle):.1f}°, dedução={deduction:.3f}m'
    )
    
    return float(deduction), notes


def check_complex_punching(
    columns_df,         # DataFrame com id, x, y, bx, by, p
    openings: list,     # Lista de Opening
    cfg,                # DesignConfig
    u1_original: np.ndarray,  # Perímetros C' originais calculados pelo motor padrão
    tau_sd_original: np.ndarray,  # tau_sd do motor padrão (MPa)
    tau_rd1: np.ndarray,          # tau_rd1 (MPa)
) -> list:
    """
    Verificação de punção complexa com aberturas.
    
    Para cada pilar, verifica se alguma abertura está dentro da zona 2d
    e recalcula o perímetro C' e o tau_sd corrigido.
    """
    d = max(cfg.h - cfg.cover - 0.010, 0.05)
    results = []
    
    for i, row in enumerate(columns_df.itertuples()):
        col_x = row.x
        col_y = row.y
        bx = row.bx
        by = row.by
        
        total_deduction = 0.0
        affecting_openings = []
        all_notes = []
        
        for opening in openings:
            deduction, notes = _perimeter_deduction_for_opening(
                col_x, col_y, bx, by, d, cfg.punching_offset_factor, opening
            )
            total_deduction += deduction
            all_notes.extend(notes)
            if deduction > 0:
                affecting_openings.append(opening.id)
        
        # Perímetro corrigido (mínimo 20% do original para evitar divisão por zero)
        u1_reduced = max(u1_original[i] - total_deduction, 0.20 * u1_original[i])
        
        # Recalcular tau_sd com perímetro reduzido
        # tau_sd_corrected = tau_sd_original * (u1_original / u1_reduced)
        if u1_original[i] > 1e-9:
            tau_sd_corrected = tau_sd_original[i] * (u1_original[i] / u1_reduced)
        else:
            tau_sd_corrected = tau_sd_original[i]
        
        deduction_pct = (total_deduction / max(u1_original[i], 1e-9)) * 100.0
        impact_ratio = tau_sd_corrected / max(tau_sd_original[i], 1e-9)
        
        # Verificar se a correção muda o veredito
        was_ok = tau_sd_original[i] <= tau_rd1[i]
        is_ok = tau_sd_corrected <= tau_rd1[i]
        is_critical = was_ok and not is_ok  # Mudou de OK para NOK
        
        if is_critical:
            all_notes.append(
                f'ATENÇÃO: Pilar {row.id} muda de ATENDE para NÃO_ATENDE '
                f'com abertura. tau_sd sobe de {tau_sd_original[i]:.3f} para {tau_sd_corrected:.3f} MPa.'
            )
        
        results.append(ComplexPunchingResult(
            column_id=str(row.id),
            u1_original_m=float(u1_original[i]),
            u1_reduced_m=float(u1_reduced),
            deduction_m=float(total_deduction),
            deduction_pct=round(float(deduction_pct), 1),
            openings_affecting=affecting_openings,
            tau_sd_original_MPa=float(tau_sd_original[i]),
            tau_sd_corrected_MPa=float(tau_sd_corrected),
            impact_ratio=round(float(impact_ratio), 3),
            is_critical=bool(is_critical),
            geometry_notes=all_notes,
        ))
    
    return results


def format_complex_punching_report(results: list) -> dict:
    """
    Consolida os resultados da punção complexa em formato de memorial.
    """
    affected_columns = [r for r in results if r.deduction_m > 0]
    critical_columns = [r for r in results if r.is_critical]
    
    summary = {
        'total_columns_checked': len(results),
        'columns_affected_by_openings': len(affected_columns),
        'columns_with_changed_verdict': len(critical_columns),
        'max_deduction_pct': max((r.deduction_pct for r in results), default=0.0),
        'max_impact_ratio': max((r.impact_ratio for r in results), default=1.0),
        'critical_columns': [r.column_id for r in critical_columns],
        'details': [
            {
                'column_id': r.column_id,
                'u1_original_m': r.u1_original_m,
                'u1_reduced_m': r.u1_reduced_m,
                'deduction_pct': r.deduction_pct,
                'tau_sd_original_MPa': r.tau_sd_original_MPa,
                'tau_sd_corrected_MPa': r.tau_sd_corrected_MPa,
                'impact_ratio': r.impact_ratio,
                'is_critical': r.is_critical,
                'openings': r.openings_affecting,
                'notes': r.geometry_notes,
            }
            for r in affected_columns
        ],
        'classification': (
            'CRITICO_REQUER_REFORCO' if critical_columns else
            'AFETADO_SEM_MUDANCA_VEREDITO' if affected_columns else
            'SEM_ABERTURAS_NA_ZONA'
        ),
    }
    
    return summary
