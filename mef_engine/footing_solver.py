import math
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FootingConfig:
    Nd_kN: float
    sigma_adm_kPa: float
    ap_m: float # Pillar dim in X
    bp_m: float # Pillar dim in Y
    fck: float = 25.0
    fyk: float = 500.0
    cover_m: float = 0.04

def solve_isolated_footing(cfg: FootingConfig) -> Dict[str, Any]:
    """
    Dimensionamento de sapata isolada rígida centrada.
    """
    # 1. Área da base (considerando 10% de peso próprio estimado)
    area_req = (cfg.Nd_kN * 1.1) / cfg.sigma_adm_kPa
    
    # Proporção: (a - ap) = (b - bp) -> balanços iguais
    # a * b = area_req -> (b + ap - bp) * b = area_req
    # b^2 + (ap - bp)b - area_req = 0
    delta_dim = cfg.ap_m - cfg.bp_m
    b = (-delta_dim + math.sqrt(delta_dim**2 + 4 * area_req)) / 2.0
    a = b + delta_dim
    
    # Arredondar para múltiplos de 5cm
    a = math.ceil(a * 20) / 20.0
    b = math.ceil(b * 20) / 20.0
    area_real = a * b
    sigma_real = (cfg.Nd_kN * 1.1) / area_real
    
    # 2. Altura (Rigidez)
    # h >= (a - ap) / 3
    h_min_a = (a - cfg.ap_m) / 3.0
    h_min_b = (b - cfg.bp_m) / 3.0
    h = max(h_min_a, h_min_b, 0.30)
    h = math.ceil(h * 20) / 20.0 # Arredondar para 5cm
    
    d = h - cfg.cover_m - 0.01 # Estimativa de d
    
    # 3. Momentos Fletores (Seção S1 e S2)
    # Balanços
    la = (a - cfg.ap_m) / 2.0
    lb = (b - cfg.bp_m) / 2.0
    
    # Pressão de cálculo (apenas carga do pilar majorada)
    sigma_d = (cfg.Nd_kN * 1.4) / area_real
    
    Ma_d = sigma_d * b * (la**2) / 2.0
    Mb_d = sigma_d * a * (lb**2) / 2.0
    
    # 4. Armadura
    fcd = cfg.fck / 1.4
    fyd = cfg.fyk / 1.15
    
    # Dimensionamento à flexão simplificado
    def calc_as(md, width, depth):
        if depth <= 0: return 0.0
        # md em kNm, width em m, depth em m
        # md * 100 / (0.8 * depth * 100 * fyd/1.15) -> errado, fyd já é de cálculo
        # Aproximação z = 0.9d
        as_cm2 = (md * 100.0) / (0.9 * depth * 100.0 * (fyd / 10.0))
        # Mínimo 0.15% Ac
        as_min = 0.0015 * (width * 100.0) * (h * 100.0)
        return max(as_cm2, as_min)

    as_a = calc_as(Ma_d, b, d)
    as_b = calc_as(Mb_d, a, d)
    
    return {
        "type": "footing",
        "a_m": a,
        "b_m": b,
        "h_m": h,
        "d_m": d,
        "area_m2": area_real,
        "sigma_adm_kPa": cfg.sigma_adm_kPa,
        "sigma_real_kPa": sigma_real,
        "Ma_d_kNm": Ma_d,
        "Mb_d_kNm": Mb_d,
        "As_a_cm2": as_a,
        "As_b_cm2": as_b,
        "status": "OK" if sigma_real <= cfg.sigma_adm_kPa else "REVISAR_AREA"
    }
