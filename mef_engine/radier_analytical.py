from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class AnalyticalConfig:
    Lx: float
    Ly: float
    loads_kN: np.ndarray # Array of [x, y, p]
    q_uniform_Pa: float = 0.0

def calculate_rigid_soil_pressure(cfg: AnalyticalConfig) -> dict:
    """Calcula a pressão de solo assumindo radier perfeitamente rígido."""
    area = cfg.Lx * cfg.Ly
    Ix = (cfg.Ly * cfg.Lx**3) / 12.0
    Iy = (cfg.Lx * cfg.Ly**3) / 12.0
    
    # Centro do radier (geométrico)
    x_g, y_g = cfg.Lx / 2.0, cfg.Ly / 2.0
    
    # Cargas de pilares (o solver trabalha em N, mas o analitico prefere kN para pressoes em kPa)
    loads_kN_val = cfg.loads_kN[:, 2] / 1000.0
    p_total = np.sum(loads_kN_val)
    mx_total = np.sum(loads_kN_val * (cfg.loads_kN[:, 1] - y_g))
    my_total = np.sum(loads_kN_val * (cfg.loads_kN[:, 0] - x_g))
    
    # Carga uniforme
    p_uniform = (cfg.q_uniform_Pa / 1000.0) * area
    p_sum = p_total + p_uniform
    
    # Pressões nos 4 cantos
    corners = [
        (0.0, 0.0),
        (cfg.Lx, 0.0),
        (cfg.Lx, cfg.Ly),
        (0.0, cfg.Ly)
    ]
    
    pressures = []
    for x, y in corners:
        dx = x - x_g
        dy = y - y_g
        # q = P/A + My*x/Iy + Mx*y/Ix
        q = (p_sum / area) + (my_total * dx / Iy) + (mx_total * dy / Ix)
        pressures.append(q)
    
    return {
        'q_med_rigid_kPa': float(p_sum / area),
        'q_max_rigid_kPa': float(max(pressures)),
        'q_min_rigid_kPa': float(min(pressures)),
        'p_total_kN': float(p_sum),
        'eccentricity_x_m': float(my_total / p_sum) if p_sum > 0 else 0.0,
        'eccentricity_y_m': float(mx_total / p_sum) if p_sum > 0 else 0.0,
    }
    

def calculate_analytical_moments(cfg: AnalyticalConfig, rigid: dict) -> dict:
    """Estima momentos fletores analíticos simplificados."""
    q_med = rigid['q_med_rigid_kPa']
    # Referência normativa simplificada: M = q * L^2 / 10 (estimativa de faixa contínua)
    # Usamos o maior vão médio entre pilares ou 20% do comprimento total como 'vão de referência'
    l_ref = max(cfg.Lx, cfg.Ly) * 0.25 
    m_ref = (q_med * l_ref**2) / 10.0
    
    return {
        'm_ref_analitico_kNm_m': float(m_ref),
        'vao_referencia_m': float(l_ref)
    }


def calculate_analytical_comparison(
    mef_summary: dict, 
    cfg: AnalyticalConfig,
    punching_mef_df: pd.DataFrame | None = None
) -> dict:
    """Consolida o comparativo entre MEF e Analítico."""
    rigid = calculate_rigid_soil_pressure(cfg)
    
    q_mef_med = mef_summary.get('loads_total_kN', 0) / max(cfg.Lx * cfg.Ly, 1e-9)
    q_mef_max = mef_summary.get('qsoil_max_kPa', 0)
    
    q_an_med = rigid['q_med_rigid_kPa']
    q_an_max = rigid['q_max_rigid_kPa']
    
    moments_an = calculate_analytical_moments(cfg, rigid)
    m_mef_max = max(abs(mef_summary.get('mx_abs_max_kNm_m', 0)), abs(mef_summary.get('my_abs_max_kNm_m', 0)))

    comp = {
        'pressao_media_mef_kPa': q_mef_med,
        'pressao_max_mef_kPa': q_mef_max,
        'pressao_media_analitica_kPa': q_an_med,
        'pressao_max_analitica_kPa': q_an_max,
        'ratio_pressao_media': q_mef_med / q_an_med if q_an_med > 0 else 1.0,
        'ratio_pressao_max': q_mef_max / q_an_max if q_an_max > 0 else 1.0,
        'momento_max_mef_kNm_m': m_mef_max,
        'momento_ref_analitico_kNm_m': moments_an['m_ref_analitico_kNm_m'],
        'ratio_momento': m_mef_max / moments_an['m_ref_analitico_kNm_m'] if moments_an['m_ref_analitico_kNm_m'] > 0 else 1.0,
        'punching_comparison': []
    }
    
    if punching_mef_df is not None:
        for _, row in punching_mef_df.iterrows():
            mef_ratio = float(row['ratio'])
            # O "analitico" aqui estamos simplificando como o ratio bruto (sem alivio de solo ou com alivio simplificado do pilar)
            # Em alguns cenarios legados o CSV nao possui ratio_gross; usa-se ratio como fallback.
            an_ratio = float(row.get('ratio_gross', row['ratio']))
            
            diff = ((mef_ratio / an_ratio) - 1.0) * 100.0 if an_ratio > 0 else 0.0
            
            comp['punching_comparison'].append({
                'id': row['id'],
                'local': row['local'],
                'mef_ratio': mef_ratio,
                'analytical_ratio': an_ratio,
                'diff_percent': diff
            })

    return comp
