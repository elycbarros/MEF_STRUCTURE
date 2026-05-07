"""
footing_solver.py - Wrapper para dimensionamento de sapatas.
"""
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class FootingConfig:
    Nd_kN: float
    sigma_adm_kPa: float
    ap_m: float
    bp_m: float
    fck: float

def solve_isolated_footing(cfg: FootingConfig) -> Dict[str, Any]:
    """
    Interface simplificada para o motor de fundações.
    """
    from engines.foundation_engine import FoundationEngine
    
    res = FoundationEngine.solve_footing(
        p_kN=cfg.Nd_kN,
        sigma_adm=cfg.sigma_adm_kPa,
        a_col=cfg.ap_m,
        b_col=cfg.bp_m
    )
    
    # Adicionando verificação de rigidez e altura
    a = res['l_m']
    b = res['b_m']
    h = max(0.40, (a - cfg.ap_m)/3.0, (b - cfg.bp_m)/3.0)
    
    return {
        "a_m": round(a, 2),
        "b_m": round(b, 2),
        "h_m": round(h, 2),
        "area_m2": round(a * b, 2),
        "sigma_real_kPa": round(cfg.Nd_kN / (a * b), 2),
        "status": "OK" if h >= 0.40 else "REVISAR"
    }
