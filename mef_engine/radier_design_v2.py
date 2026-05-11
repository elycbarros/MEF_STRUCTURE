from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.spatial import Delaunay, QhullError
from scipy.interpolate import griddata

@dataclass
class DesignConfig:
    fck: float = 30.0
    fyk: float = 500.0
    h: float = 0.70
    Lx: float = 24.0
    Ly: float = 24.0
    module_name: str = 'radier'
    cover: float = 0.05
    gamma_s: float = 1.15
    gamma_c: float = 1.4
    rho_min: float = 0.0015
    punching_offset_factor: float = 2.0
    wk_limit_mm: float = 0.30
    bar_diameter_x_mm: float = 12.5
    bar_diameter_y_mm: float = 12.5
    eta1: float = 2.25
    system_type: str = 'radier'
    gamma_f: float = 1.4
    
    
def suggest_commercial_reinforcement(as_cm2_m: float, h_m: float = 0.50) -> str:
    """Sugere bitola e espaçamento comercial baseado na área de aço e limites normativos."""
    from radier_detailing import DetailingEngine
    # Escolha inteligente baseada na espessura
    preferred = 12.5 if h_m >= 0.40 else 10.0
    detailing = DetailingEngine.suggest_reinforcement(as_cm2_m, preferred)
    return detailing.get('text', 'N/A')


def calculate_reinforcement_metrics(df_flexure: pd.DataFrame, h_m: float, Lx: float, Ly: float) -> dict:
    """Calcula métricas globais de consumo de aço e concreto."""
    # Estimativa simplificada: soma das 4 camadas de As_adotada (médias) * área
    as_cols = ['Asx_bottom_adot_cm2_m', 'Asx_top_adot_cm2_m', 'Asy_bottom_adot_cm2_m', 'Asy_top_adot_cm2_m']
    total_as_cm2_m = df_flexure[as_cols].mean().sum()
    
    area_m2 = Lx * Ly
    volume_m3 = area_m2 * h_m
    
    # Peso = Area (cm2/m) * Lx (m) * Ly (m) * densidade (7850 kg/m3)
    # 1 cm2/m = 1e-4 m2/m
    # Peso total (aprox) = sum(As_media) * Area * 7.85 kg/m (para 1cm2 de barra por metro)
    # Na verdade: Peso = As (m2/m) * Area (m2) * 7850 kg/m3
    weight_kg = total_as_cm2_m * 1e-4 * area_m2 * 7850.0
    
    # Adicionar 10% para perdas, dobras e transpasse
    weight_kg *= 1.10
    
    return {
        'total_steel_kg': round(float(weight_kg), 2),
        'steel_density_kg_m3': round(float(weight_kg / volume_m3), 2) if volume_m3 > 0 else 0,
        'steel_density_kg_m2': round(float(weight_kg / area_m2), 2) if area_m2 > 0 else 0,
        'concrete_volume_m3': round(float(volume_m3), 2),
    }


def _bar_spacing_mm(as_cm2_m: pd.Series, phi_mm: float) -> pd.Series:
    area_bar_mm2 = np.pi * phi_mm**2 / 4.0
    as_mm2_m = np.maximum(as_cm2_m.to_numpy(dtype=float) * 100.0, 1e-9)
    return pd.Series(1000.0 * area_bar_mm2 / as_mm2_m, index=as_cm2_m.index)


def _sigma_s_service_mpa(moment_nm_per_m: pd.Series, as_cm2_m: pd.Series, z_m: float) -> pd.Series:
    as_m2_m = np.maximum(as_cm2_m.to_numpy(dtype=float) * 1e-4, 1e-12)
    sigma_pa = np.abs(moment_nm_per_m.to_numpy(dtype=float)) / np.maximum(z_m * as_m2_m, 1e-12)
    return pd.Series(sigma_pa / 1e6, index=moment_nm_per_m.index)


def _rho_ri(as_cm2_m: pd.Series, phi_mm: float, spacing_mm: pd.Series, h_m: float) -> pd.Series:
    cover_depth_mm = min(7.5 * phi_mm, 0.5 * h_m * 1000.0)
    acr_mm2 = np.maximum(np.minimum(spacing_mm.to_numpy(dtype=float), 15.0 * phi_mm) * 2.0 * cover_depth_mm, 1e-9)
    as_mm2 = np.maximum(as_cm2_m.to_numpy(dtype=float) * spacing_mm.to_numpy(dtype=float) / 10.0, 1e-9)
    return pd.Series(as_mm2 / acr_mm2, index=as_cm2_m.index)


def _wk_nbr_mm(phi_mm: float, eta1: float, sigma_s_mpa: pd.Series, rho_ri: pd.Series, fctm_mpa: float, es_mpa: float = 210000.0) -> pd.Series:
    sigma = np.maximum(sigma_s_mpa.to_numpy(dtype=float), 0.0)
    rho = np.maximum(rho_ri.to_numpy(dtype=float), 1e-9)
    wk_1 = phi_mm / (12.5 * eta1) * (sigma / es_mpa) * (3.0 * sigma / max(fctm_mpa, 1e-9))
    wk_2 = phi_mm / (12.5 * eta1) * (sigma / es_mpa) * ((4.0 / rho) + 45.0)
    return pd.Series(np.minimum(wk_1, wk_2), index=sigma_s_mpa.index)

def design_flexure_from_elements(elements_csv: str, cfg: DesignConfig, out_csv: str = 'output/radier_design_flexure_v2.csv'):
    df = pd.read_csv(elements_csv)
    d = max(cfg.h - cfg.cover - 0.010, 0.05)
    fyd = cfg.fyk / cfg.gamma_s
    z = 0.9 * d
    mxy_abs = np.abs(df['mxy_Nm_per_m'])

    # Wood-Armer simplificado para separar armadura superior/inferior por direção.
    df['Mx_bottom_Nm_per_m'] = np.maximum(df['mx_Nm_per_m'], 0.0) + mxy_abs
    df['Mx_top_Nm_per_m'] = np.maximum(-df['mx_Nm_per_m'], 0.0) + mxy_abs
    df['My_bottom_Nm_per_m'] = np.maximum(df['my_Nm_per_m'], 0.0) + mxy_abs
    df['My_top_Nm_per_m'] = np.maximum(-df['my_Nm_per_m'], 0.0) + mxy_abs

    # Dimensionamento Preciso (Bloco Retangular NBR 6118)
    fcd = cfg.fck / cfg.gamma_c
    alpha_cc = 0.85
    lambda_c = 0.8
    psi = 0.4
    if cfg.fck > 50:
        lambda_c = 0.8 - (cfg.fck - 50) / 400
        psi = 0.4 - (cfg.fck - 50) / 1000
        alpha_cc = 0.85 * (1 - (cfg.fck - 50) / 200)

    # Mrd = alpha_cc * fcd * bw * (lambda_c * x) * (d - psi * lambda_c * x)
    # k = Md / (bw * d^2 * alpha_cc * fcd)
    k_val_bottom_x = (df['Mx_bottom_Nm_per_m'] * 1.0) / (1.0 * d**2 * alpha_cc * (fcd * 1e6))
    k_val_top_x = (df['Mx_top_Nm_per_m'] * 1.0) / (1.0 * d**2 * alpha_cc * (fcd * 1e6))
    k_val_bottom_y = (df['My_bottom_Nm_per_m'] * 1.0) / (1.0 * d**2 * alpha_cc * (fcd * 1e6))
    k_val_top_y = (df['My_top_Nm_per_m'] * 1.0) / (1.0 * d**2 * alpha_cc * (fcd * 1e6))

    def solve_xi(k):
        # k = lambda * xi * (1 - psi * lambda * xi)
        # psi * lambda^2 * xi^2 - lambda * xi + k = 0
        a = psi * lambda_c**2
        b = -lambda_c
        delta = b**2 - 4 * a * k
        return np.where(delta >= 0, (-b - np.sqrt(np.maximum(delta, 0))) / (2 * a), 1.0)

    xi_bx = solve_xi(k_val_bottom_x)
    xi_tx = solve_xi(k_val_top_x)
    xi_by = solve_xi(k_val_bottom_y)
    xi_ty = solve_xi(k_val_top_y)

    df['xi_x_bottom'] = xi_bx
    df['xi_x_top'] = xi_tx
    
    # Armadura Necessária: As = Md / (fyd * d * (1 - psi * lambda * xi))
    df['Asx_bottom_req_cm2_m'] = (df['Mx_bottom_Nm_per_m'] / (fyd * 1e6 * d * (1 - psi * lambda_c * xi_bx))) * 1e4
    df['Asx_top_req_cm2_m'] = (df['Mx_top_Nm_per_m'] / (fyd * 1e6 * d * (1 - psi * lambda_c * xi_tx))) * 1e4
    df['Asy_bottom_req_cm2_m'] = (df['My_bottom_Nm_per_m'] / (fyd * 1e6 * d * (1 - psi * lambda_c * xi_by))) * 1e4
    df['Asy_top_req_cm2_m'] = (df['My_top_Nm_per_m'] / (fyd * 1e6 * d * (1 - psi * lambda_c * xi_ty))) * 1e4

    # Taxa Mínima (NBR 6118 Tabela 19.1)
    fctm = 0.3 * (cfg.fck ** (2/3)) if cfg.fck <= 50 else 2.12 * np.log(1 + 0.11 * cfg.fck)
    # rho_min para lajes (estimativa por fctm/fyk)
    rho_min = max(0.0015, 0.233 * fctm / cfg.fyk)
    as_min_total_cm2_m = rho_min * 1.0 * cfg.h * 1e4
    as_min_face_cm2_m = as_min_total_cm2_m / 2.0
    
    df['As_min_total_cm2_m'] = as_min_total_cm2_m
    df['As_min_face_cm2_m'] = as_min_face_cm2_m

    df['Asx_bottom_adot_cm2_m'] = np.maximum(df['Asx_bottom_req_cm2_m'], as_min_face_cm2_m)
    df['Asx_top_adot_cm2_m'] = np.maximum(df['Asx_top_req_cm2_m'], as_min_face_cm2_m)
    df['Asy_bottom_adot_cm2_m'] = np.maximum(df['Asy_bottom_req_cm2_m'], as_min_face_cm2_m)
    df['Asy_top_adot_cm2_m'] = np.maximum(df['Asy_top_req_cm2_m'], as_min_face_cm2_m)

    # Compatibilidade retroativa com o memorial existente.
    df['Asx_req_cm2_m'] = np.maximum(df['Asx_bottom_req_cm2_m'], df['Asx_top_req_cm2_m'])
    df['Asy_req_cm2_m'] = np.maximum(df['Asy_bottom_req_cm2_m'], df['Asy_top_req_cm2_m'])
    df['As_min_cm2_m'] = as_min_total_cm2_m
    df['Asx_adot_cm2_m'] = np.maximum(df['Asx_bottom_adot_cm2_m'], df['Asx_top_adot_cm2_m'])
    df['Asy_adot_cm2_m'] = np.maximum(df['Asy_bottom_adot_cm2_m'], df['Asy_top_adot_cm2_m'])

    # Sugestões de detalhamento comercial
    df['detalhe_x_inf'] = df['Asx_bottom_adot_cm2_m'].apply(lambda x: suggest_commercial_reinforcement(x, cfg.h))
    df['detalhe_x_sup'] = df['Asx_top_adot_cm2_m'].apply(lambda x: suggest_commercial_reinforcement(x, cfg.h))
    df['detalhe_y_inf'] = df['Asy_bottom_adot_cm2_m'].apply(lambda x: suggest_commercial_reinforcement(x, cfg.h))
    df['detalhe_y_sup'] = df['Asy_top_adot_cm2_m'].apply(lambda x: suggest_commercial_reinforcement(x, cfg.h))

    df.to_csv(out_csv, index=False)
    metrics = calculate_reinforcement_metrics(df, cfg.h, cfg.Lx, cfg.Ly)
    return out_csv, metrics


def check_serviceability_flexure(
    elements_csv: str,
    flexure_design_csv: str,
    cfg: DesignConfig,
    out_csv: str = 'output/radier_serviceability_check_v2.csv',
):
    df = pd.read_csv(elements_csv).merge(
        pd.read_csv(flexure_design_csv)[[
            'elem',
            'Asx_bottom_adot_cm2_m',
            'Asx_top_adot_cm2_m',
            'Asy_bottom_adot_cm2_m',
            'Asy_top_adot_cm2_m',
        ]],
        on='elem',
        how='left',
    )
    d = max(cfg.h - cfg.cover - 0.010, 0.05)
    fctm = 0.30 * cfg.fck ** (2.0 / 3.0)
    z = 0.9 * d
    mxy_abs = np.abs(df['mxy_Nm_per_m'])
    mser_x_bottom = pd.Series(np.maximum(df['mx_Nm_per_m'], 0.0), index=df.index) + mxy_abs
    mser_x_top = pd.Series(np.maximum(-df['mx_Nm_per_m'], 0.0), index=df.index) + mxy_abs
    mser_y_bottom = pd.Series(np.maximum(df['my_Nm_per_m'], 0.0), index=df.index) + mxy_abs
    mser_y_top = pd.Series(np.maximum(-df['my_Nm_per_m'], 0.0), index=df.index) + mxy_abs

    sx_bottom = _bar_spacing_mm(df['Asx_bottom_adot_cm2_m'], cfg.bar_diameter_x_mm)
    sx_top = _bar_spacing_mm(df['Asx_top_adot_cm2_m'], cfg.bar_diameter_x_mm)
    sy_bottom = _bar_spacing_mm(df['Asy_bottom_adot_cm2_m'], cfg.bar_diameter_y_mm)
    sy_top = _bar_spacing_mm(df['Asy_top_adot_cm2_m'], cfg.bar_diameter_y_mm)

    sigma_x_bottom = _sigma_s_service_mpa(mser_x_bottom, df['Asx_bottom_adot_cm2_m'], z)
    sigma_x_top = _sigma_s_service_mpa(mser_x_top, df['Asx_top_adot_cm2_m'], z)
    sigma_y_bottom = _sigma_s_service_mpa(mser_y_bottom, df['Asy_bottom_adot_cm2_m'], z)
    sigma_y_top = _sigma_s_service_mpa(mser_y_top, df['Asy_top_adot_cm2_m'], z)

    rho_x_bottom = _rho_ri(df['Asx_bottom_adot_cm2_m'], cfg.bar_diameter_x_mm, sx_bottom, cfg.h)
    rho_x_top = _rho_ri(df['Asx_top_adot_cm2_m'], cfg.bar_diameter_x_mm, sx_top, cfg.h)
    rho_y_bottom = _rho_ri(df['Asy_bottom_adot_cm2_m'], cfg.bar_diameter_y_mm, sy_bottom, cfg.h)
    rho_y_top = _rho_ri(df['Asy_top_adot_cm2_m'], cfg.bar_diameter_y_mm, sy_top, cfg.h)

    wk_x_bottom = _wk_nbr_mm(cfg.bar_diameter_x_mm, cfg.eta1, sigma_x_bottom, rho_x_bottom, fctm)
    wk_x_top = _wk_nbr_mm(cfg.bar_diameter_x_mm, cfg.eta1, sigma_x_top, rho_x_top, fctm)
    wk_y_bottom = _wk_nbr_mm(cfg.bar_diameter_y_mm, cfg.eta1, sigma_y_bottom, rho_y_bottom, fctm)
    wk_y_top = _wk_nbr_mm(cfg.bar_diameter_y_mm, cfg.eta1, sigma_y_top, rho_y_top, fctm)

    out = pd.DataFrame({
        'elem': df['elem'],
        'xc_m': df['xc_m'],
        'yc_m': df['yc_m'],
        'sigma_x_bottom_MPa': sigma_x_bottom,
        'sigma_x_top_MPa': sigma_x_top,
        'sigma_y_bottom_MPa': sigma_y_bottom,
        'sigma_y_top_MPa': sigma_y_top,
        'rho_x_bottom': rho_x_bottom,
        'rho_x_top': rho_x_top,
        'rho_y_bottom': rho_y_bottom,
        'rho_y_top': rho_y_top,
        'spacing_x_bottom_mm': sx_bottom,
        'spacing_x_top_mm': sx_top,
        'spacing_y_bottom_mm': sy_bottom,
        'spacing_y_top_mm': sy_top,
        'wk_est_x_bottom_mm': wk_x_bottom,
        'wk_est_x_top_mm': wk_x_top,
        'wk_est_y_bottom_mm': wk_y_bottom,
        'wk_est_y_top_mm': wk_y_top,
        'wk_est_x_mm': np.maximum(wk_x_bottom, wk_x_top),
        'wk_est_y_mm': np.maximum(wk_y_bottom, wk_y_top),
        'wk_limit_mm': cfg.wk_limit_mm,
        'wk_x_ok': np.maximum(wk_x_bottom, wk_x_top) <= cfg.wk_limit_mm,
        'wk_y_ok': np.maximum(wk_y_bottom, wk_y_top) <= cfg.wk_limit_mm,
        'w_m': df['w_mean_m'] if 'w_mean_m' in df.columns else (df['w_m'] if 'w_m' in df.columns else 0.0),
        'mx_Nm_per_m': df['mx_Nm_per_m'],
        'my_Nm_per_m': df['my_Nm_per_m'],
        'mxy_Nm_per_m': df['mxy_Nm_per_m'],
        'Asx_bottom_adot_cm2_m': df['Asx_bottom_adot_cm2_m'],
        'Asx_top_adot_cm2_m': df['Asx_top_adot_cm2_m'],
        'Asy_bottom_adot_cm2_m': df['Asy_bottom_adot_cm2_m'],
        'Asy_top_adot_cm2_m': df['Asy_top_adot_cm2_m'],
    })
    out.to_csv(out_csv, index=False)
    return out_csv

def _estimate_soil_reaction_kN(nodes_df: pd.DataFrame, x: float, y: float, area_m2: float, influence_dim_x: float, influence_dim_y: float) -> float:
    x_min = x - influence_dim_x / 2.0
    x_max = x + influence_dim_x / 2.0
    y_min = y - influence_dim_y / 2.0
    y_max = y + influence_dim_y / 2.0
    window = nodes_df[
        (nodes_df['x_m'] >= x_min) & (nodes_df['x_m'] <= x_max) &
        (nodes_df['y_m'] >= y_min) & (nodes_df['y_m'] <= y_max)
    ]
    if window.empty:
        distances = ((nodes_df['x_m'] - x) ** 2 + (nodes_df['y_m'] - y) ** 2) ** 0.5
        qsoil_mean_pa = float(nodes_df.loc[distances.nsmallest(4).index, 'qsoil_Pa'].mean())
    else:
        qsoil_mean_pa = float(window['qsoil_Pa'].mean())
    return qsoil_mean_pa * area_m2 / 1e3


def _classify_column_position(x1: float, x2: float, y1: float, y2: float, Lx: float, Ly: float, tol: float = 1e-9) -> str:
    touches = sum([
        x1 <= tol,
        x2 >= Lx - tol,
        y1 <= tol,
        y2 >= Ly - tol,
    ])
    if touches >= 2:
        return 'canto'
    if touches == 1:
        return 'borda'
    return 'interior'


def _get_k_factor(c1: float, c2: float) -> float:
    """Fator k da NBR 6118 baseado na proporção do pilar."""
    ratio = c1 / max(c2, 1e-9)
    if ratio <= 0.5: return 0.45
    if ratio <= 1.0: return 0.45 + (0.60 - 0.45) * (ratio - 0.5) / 0.5
    if ratio <= 2.0: return 0.60 + (0.70 - 0.60) * (ratio - 1.0) / 1.0
    if ratio <= 3.0: return 0.70 + (0.80 - 0.70) * (ratio - 2.0) / 1.0
    return 0.80


def _calculate_wp_and_beta(local: str, c1: float, c2: float, d: float, vsd: float, msd_x: float, msd_y: float, u1: float) -> tuple[float, float]:
    """Calcula Wp e o fator beta conforme NBR 6118."""
    # c1: dimensão paralela ao momento
    # Wp para pilar retangular interior (aproximação NBR 6118)
    # Wp = c1^2 / 2 + c1*c2 + 4*c2*d + 16*d^2 + 2*pi*d*c1
    wp = (c1**2 / 2.0) + (c1 * c2) + (4.0 * c2 * d) + (16.0 * d**2) + (2.0 * np.pi * d * c1)
    
    k_x = _get_k_factor(c1, c2)
    k_y = _get_k_factor(c2, c1)
    
    # Se msd for zero, beta mínimo
    beta_min = 1.0
    if local == 'interior': beta_min = 1.15
    elif local == 'borda': beta_min = 1.40
    elif local == 'canto': beta_min = 1.50
    
    if abs(vsd) < 1e-3:
        return wp, beta_min
        
    term_x = (k_x * abs(msd_x) / wp) if wp > 0 else 0
    term_y = (k_y * abs(msd_y) / wp) if wp > 0 else 0 # Simplificação: usando mesmo Wp ou rotacionado
    
    beta = 1.0 + (u1 / vsd) * (term_x + term_y)
    return wp, max(beta, beta_min)


def _rect_intersection_metrics(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    Lx: float,
    Ly: float,
) -> tuple[float, float, float, float, str]:
    xi1 = max(0.0, x1)
    xi2 = min(Lx, x2)
    yi1 = max(0.0, y1)
    yi2 = min(Ly, y2)
    width = max(xi2 - xi1, 0.0)
    height = max(yi2 - yi1, 0.0)
    area = width * height
    perimeter = 0.0
    if width > 0 and yi2 < Ly:
        perimeter += width
    if width > 0 and yi1 > 0:
        perimeter += width
    if height > 0 and xi1 > 0:
        perimeter += height
    if height > 0 and xi2 < Lx:
        perimeter += height
    local = _classify_column_position(xi1, xi2, yi1, yi2, Lx, Ly)
    return perimeter, area, width, height, local


def _critical_contours(
    x: float,
    y: float,
    bx: float,
    by: float,
    d: float,
    Lx: float,
    Ly: float,
    offset_factor: float,
) -> dict:
    half_bx = bx / 2.0
    half_by = by / 2.0
    x1 = x - half_bx
    x2 = x + half_bx
    y1 = y - half_by
    y2 = y + half_by
    u0, a0, w0, h0, local = _rect_intersection_metrics(x1, x2, y1, y2, Lx, Ly)
    offset = offset_factor * d
    u1, a1, w1, h1, local_u1 = _rect_intersection_metrics(x1 - offset, x2 + offset, y1 - offset, y2 + offset, Lx, Ly)
    return {
        'u0': u0,
        'a0': a0,
        'u1': u1,
        'a1': a1,
        'critical_width_m': w1,
        'critical_height_m': h1,
        'local': local_u1 if local_u1 != 'interior' or local == 'interior' else local,
    }


def _estimate_rho_punching(
    flexure_df: pd.DataFrame,
    x: float,
    y: float,
    bx: float,
    by: float,
    d: float,
    Lx: float,
    Ly: float,
) -> float:
    influence_x = min(bx + 6.0 * d, Lx)
    influence_y = min(by + 6.0 * d, Ly)
    x_min = max(0.0, x - influence_x / 2.0)
    x_max = min(Lx, x + influence_x / 2.0)
    y_min = max(0.0, y - influence_y / 2.0)
    y_max = min(Ly, y + influence_y / 2.0)
    window = flexure_df[
        (flexure_df['xc_m'] >= x_min) & (flexure_df['xc_m'] <= x_max) &
        (flexure_df['yc_m'] >= y_min) & (flexure_df['yc_m'] <= y_max)
    ]
    if window.empty:
        return 0.001
    asx = float(window[['Asx_bottom_adot_cm2_m', 'Asx_top_adot_cm2_m']].max(axis=1).mean())
    asy = float(window[['Asy_bottom_adot_cm2_m', 'Asy_top_adot_cm2_m']].max(axis=1).mean())
    d_cm = max(d * 100.0, 1e-9)
    rho_x = asx / (100.0 * d_cm)
    rho_y = asy / (100.0 * d_cm)
    return max((rho_x * rho_y) ** 0.5, 0.001)


def check_punching(
    columns_csv: str,
    cfg: DesignConfig,
    out_csv: str = 'output/radier_punching_check_v2.csv',
    nodes_csv: str | None = None,
    flexure_design_csv: str | None = None,
):
    df = pd.read_csv(columns_csv)
    d = max(cfg.h - cfg.cover - 0.010, 0.05)
    if 'local' not in df.columns:
        df['local'] = 'interior'
    contour_data = [
        _critical_contours(row.x, row.y, row.bx, row.by, d, cfg.Lx, cfg.Ly, cfg.punching_offset_factor)
        for row in df.itertuples(index=False)
    ]
    u0 = np.array([item['u0'] for item in contour_data], dtype=float)
    u1 = np.array([item['u1'] for item in contour_data], dtype=float)
    area_inside = np.array([item['a1'] for item in contour_data], dtype=float)
    crit_dim_x = np.array([item['critical_width_m'] for item in contour_data], dtype=float)
    crit_dim_y = np.array([item['critical_height_m'] for item in contour_data], dtype=float)
    locals_out = [item['local'] for item in contour_data]
    ved_gross = df['p'] / 1e3

    soil_reaction_kN = np.zeros(len(df), dtype=float)
    if nodes_csv and Path(nodes_csv).exists():
        nodes_df = pd.read_csv(nodes_csv)
        soil_reaction_kN = np.array([
            _estimate_soil_reaction_kN(nodes_df, row.x, row.y, area, dim_x, dim_y)
            for row, area, dim_x, dim_y in zip(df.itertuples(index=False), area_inside, crit_dim_x, crit_dim_y)
        ])

    ved_net = np.maximum(ved_gross - soil_reaction_kN, 0.0)
    rho = np.full(len(df), 0.001, dtype=float)
    if flexure_design_csv and Path(flexure_design_csv).exists():
        flexure_df = pd.read_csv(flexure_design_csv)
        rho = np.array([
            _estimate_rho_punching(flexure_df, row.x, row.y, row.bx, row.by, d, cfg.Lx, cfg.Ly)
            for row in df.itertuples(index=False)
        ], dtype=float)

    d_cm = d * 100.0
    alpha_v = 1.0 - cfg.fck / 250.0
    fcd = cfg.fck / cfg.gamma_c
    tau_rd2 = 0.27 * alpha_v * fcd
    # k limitado a 2.0 conforme NBR 6118:2023
    k_factor = np.minimum(1.0 + np.sqrt(200.0 / np.maximum(d_cm * 10.0, 1e-9)), 2.0)
    tau_rd1 = (0.18 / cfg.gamma_c) * k_factor * np.power(100.0 * rho * cfg.fck, 1.0 / 3.0)
    
    # Novas métricas de beta e wp
    betas = []
    wps = []
    tau_sds = []
    
    mx_design = df['mx_design'] if 'mx_design' in df.columns else df.get('mx', 0.0)
    my_design = df['my_design'] if 'my_design' in df.columns else df.get('my', 0.0)

    for i, row in enumerate(df.itertuples()):
        wp, beta = _calculate_wp_and_beta(
            locals_out[i], row.bx, row.by, d, 
            ved_net[i] * 1000.0, # N
            mx_design.iloc[i] * 1000.0, # Nm
            my_design.iloc[i] * 1000.0, # Nm
            u1[i]
        )
        betas.append(beta)
        wps.append(wp)
        # Tau_sd = beta * V / (u * d)
        tau_sds.append(beta * (ved_net[i] * 1000.0) / (max(u1[i] * d, 1e-9)))

    vrd2_kN = tau_rd2 * u0 * d * 1000.0
    vrd1_kN = tau_rd1 * u1 * d * 1000.0
    
    out = pd.DataFrame({
        'id': df['id'],
        'Ved_gross_kN': ved_gross,
        'soil_reaction_kN': soil_reaction_kN,
        'Ved_net_kN': ved_net,
        'Msd_x_kNm': mx_design,
        'Msd_y_kNm': my_design,
        'local': locals_out,
        'u0_m': u0,
        'u1_m': u1,
        'beta': betas,
        'Wp_m2': wps,
        'tau_sd_MPa': np.array(tau_sds) / 1e6,
        'tau_rd1_MPa': tau_rd1,
        'tau_rd2_MPa': tau_rd2,
        'VRd1_kN': vrd1_kN,
        'VRd2_kN': vrd2_kN,
        'ratio': np.array(tau_sds) / 1e6 / tau_rd1,
        'ratio_face': (np.array(betas) * (ved_net * 1000.0) / (u0 * d)) / 1e6 / tau_rd2,
        'ratio_gross': ved_gross / vrd1_kN
    })
    # Dimensionamento de Armadura de Punção (Transversal)
    asw_req_cm2 = []
    asw_details = []
    
    # fywd = fyk / 1.15, limitado a 300 MPa para punção (NBR 6118)
    fywd = min(cfg.fyk / cfg.gamma_s, 300.0) 
    
    for i, row in enumerate(out.itertuples()):
        tau_sd = row.tau_sd_MPa
        tau_rd1 = row.tau_rd1_MPa
        
        if tau_sd > tau_rd1:
            # Asw = (tau_sd - 0.10 * tau_rd1) * u1 * d / (0.9 * fywd) -> simplificado
            # NBR 6118: tau_sd <= tau_rd3 = 0.10 * tau_rd1 + 0.90 * rho_w * fywd
            asw = max((tau_sd - 0.10 * tau_rd1) * (u1[i] * 100.0) * d_cm / (0.90 * fywd / 10.0), 0.0)
            asw_req_cm2.append(asw)
            
            # Detalhamento Sugerido: Studs de 10mm (area = 0.785 cm2)
            n_studs = int(np.ceil(asw / 0.785))
            # Garantir mínimo de 2 perímetros
            n_perimeters = 2 if asw > 0 else 0
            asw_details.append(f"{n_studs} Studs d=10mm ({n_perimeters} perim.)")
        else:
            asw_req_cm2.append(0.0)
            asw_details.append("Dispensa Reforço")

    out['Asw_req_cm2'] = asw_req_cm2
    out['detalhamento_puncao'] = asw_details
    out.to_csv(out_csv, index=False)
    return out_csv


def check_angular_distortion(
    columns_csv: str,
    nodes_csv: str,
    out_csv: str = 'output/radier_angular_distortion_v2.csv',
    limit: float = 1.0/500.0
):
    """Calcula a distorção angular entre pilares adjacentes usando triangulação de Delaunay."""
    cols_df = pd.read_csv(columns_csv)
    nodes_df = pd.read_csv(nodes_csv)
    
    if len(cols_df) < 2:
        return None
        
    # Interpolar recalque w nos pilares
    points = nodes_df[['x_m', 'y_m']].to_numpy()
    values = nodes_df['w_m'].to_numpy()
    w_pillars = griddata(points, values, cols_df[['x', 'y']].to_numpy(), method='linear')
    cols_df['w_mm'] = w_pillars * 1000.0
    
    # Triangulação de Delaunay para encontrar vizinhos.
    # Para poucos pilares ou geometria degenerada, usa fallback por pares.
    coords = cols_df[['x', 'y']].to_numpy()
    edges = set()
    try:
        tri = Delaunay(coords)
        # Extrair arestas únicas da triangulação
        for simplex in tri.simplices:
            for i in range(3):
                n1, n2 = sorted([simplex[i], simplex[(i+1)%3]])
                edges.add((n1, n2))
    except QhullError:
        n = len(coords)
        for i in range(n):
            for j in range(i + 1, n):
                edges.add((i, j))
            
    distortions = []
    for i1, i2 in edges:
        p1 = cols_df.iloc[i1]
        p2 = cols_df.iloc[i2]
        
        L = np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
        dw = abs(p1.w_mm - p2.w_mm)
        beta = dw / (L * 1000.0) if L > 0 else 0
        
        distortions.append({
            'p1_id': p1.id,
            'p2_id': p2.id,
            'L_m': L,
            'dw_mm': dw,
            'beta': beta,
            'beta_inv': 1.0/beta if beta > 0 else 0,
            'ok': beta <= limit
        })
        
    res_df = pd.DataFrame(distortions)
    res_df.to_csv(out_csv, index=False)
    return out_csv
