from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class AnalyticalConfig:
    Lx: float
    Ly: float
    loads_N: np.ndarray | None = None # Array of [x, y, p] in Newtons
    q_uniform_Pa: float = 0.0
    area_loads: list = None # List of dicts or AreaLoad objects in kN/m² or Pa
    pillars: list = None # List of Pillar objects

def calculate_rigid_soil_pressure(cfg: AnalyticalConfig) -> dict:
    """Calcula a pressão de solo assumindo radier perfeitamente rígido."""
    area = cfg.Lx * cfg.Ly
    Ix = (cfg.Ly * cfg.Lx**3) / 12.0
    Iy = (cfg.Lx * cfg.Ly**3) / 12.0
    
    # Centro do radier (geométrico)
    x_g, y_g = cfg.Lx / 2.0, cfg.Ly / 2.0
    
    # Cargas de pilares
    p_total = 0.0
    mx_total = 0.0
    my_total = 0.0
    
    # Prioridade 1: Array loads_N (SI)
    if cfg.loads_N is not None and len(cfg.loads_N) > 0:
        p_vals_kN = cfg.loads_N[:, 2] / 1000.0
        p_total += np.sum(p_vals_kN)
        mx_total += np.sum(p_vals_kN * (cfg.loads_N[:, 1] - y_g))
        my_total += np.sum(p_vals_kN * (cfg.loads_N[:, 0] - x_g))
    # Prioridade 2: Lista pillars (objetos ou dicts)
    elif cfg.pillars:
        for p in cfg.pillars:
            # Tenta pegar p_kN (preferido) ou p (em N)
            pkN = getattr(p, 'p_kN', None)
            if pkN is None and isinstance(p, dict):
                pkN = p.get('p_kN', p.get('p', 0.0) / 1000.0)
            elif pkN is None:
                pkN = getattr(p, 'p', 0.0) / 1000.0
            
            x = getattr(p, 'x', p.get('x', 0.0) if isinstance(p, dict) else 0.0)
            y = getattr(p, 'y', p.get('y', 0.0) if isinstance(p, dict) else 0.0)
            
            p_total += pkN
            mx_total += pkN * (y - y_g)
            my_total += pkN * (x - x_g)
    
    # Carga uniforme (convertendo Pa para kN/m²)
    p_uniform = (cfg.q_uniform_Pa / 1000.0) * area
    
    # Cargas de área regionais
    p_area_loads = 0.0
    mx_area_loads = 0.0
    my_area_loads = 0.0
    if cfg.area_loads:
        for al in cfg.area_loads:
            if isinstance(al, dict):
                xmin, xmax = al['x_min'], al['x_max']
                ymin, ymax = al['y_min'], al['y_max']
                q_val = al.get('q_kN', al.get('q_Pa', 0.0))
            else:
                xmin, xmax = al.x_min, al.x_max
                ymin, ymax = al.y_min, al.y_max
                q_val = getattr(al, 'q_kN', getattr(al, 'q_Pa', 0.0))
            
            # Se q_val for alto (>1000), assumimos que está em Pa, senão kPa
            if q_val > 1000:
                q_val /= 1000.0
                
            al_area = (xmax - xmin) * (ymax - ymin)
            p_al = q_val * al_area
            x_c = (xmin + xmax) / 2.0
            y_c = (ymin + ymax) / 2.0
            
            p_area_loads += p_al
            mx_area_loads += p_al * (y_c - y_g)
            my_area_loads += p_al * (x_c - x_g)

    p_sum = p_total + p_uniform + p_area_loads
    mx_total = mx_total + mx_area_loads
    my_total = my_total + my_area_loads
    
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
    
    # Fallback: Se o rígido deu zero mas o MEF tem carga, algo falhou no mapeamento de pilares
    p_sum = rigid['p_total_kN']
    area = max(cfg.Lx * cfg.Ly, 1e-9)
    
    if p_sum < 1e-3:
        p_sum = mef_summary.get('loads_total_kN', 0)
        rigid['p_total_kN'] = p_sum
        rigid['q_med_rigid_kPa'] = p_sum / area
        # Como não temos as posições aqui, assumimos q_max = q_med (uniforme)
        rigid['q_max_rigid_kPa'] = p_sum / area
        rigid['q_min_rigid_kPa'] = p_sum / area
    
    q_mef_med = mef_summary.get('loads_total_kN', 0) / area
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
        
        # Estrutura esperada pelo ReportView.tsx
        'analytical': {
            'q_med_kPa': q_an_med,
            'q_max_kPa': q_an_max,
            'm_ref_kNm_m': moments_an['m_ref_analitico_kNm_m']
        },
        'mef': {
            'q_med_kPa': q_mef_med,
            'q_max_kPa': q_mef_max,
            'm_max_kNm_m': m_mef_max
        },
        'divergence_metrics': {
            'q_med_diff_pct': (q_mef_med / q_an_med - 1.0) if q_an_med > 0 else 0.0,
            'q_max_diff_pct': (q_mef_max / q_an_max - 1.0) if q_an_max > 0 else 0.0,
            'm_diff_pct': (m_mef_max / moments_an['m_ref_analitico_kNm_m'] - 1.0) if moments_an['m_ref_analitico_kNm_m'] > 0 else 0.0,
        },
        
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
