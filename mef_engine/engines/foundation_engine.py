"""
foundation_engine.py - Motor Consolidado de Fundações (Domínio: Fundações).
Segue NBR 6122 e NBR 6118.
"""
import math
from typing import Dict, Any

class FoundationEngine:
    """
    Centraliza cálculos de geotecnia, sapatas, blocos e vigas alavanca.
    """
    
    @staticmethod
    def estimate_capacity_spt(n_spt: float, method: str = "Teixeira") -> float:
        """Estimativa de tensão admissível (kPa) via SPT."""
        if method == "Teixeira":
            return (n_spt / 50.0) * 1000.0 # kPa
        return (n_spt / 40.0) * 1000.0 # Mais conservador

    @staticmethod
    def solve_footing(p_kN: float, sigma_adm: float, a_col: float, b_col: float) -> Dict[str, Any]:
        """Dimensionamento de Sapata Isolada."""
        area_req = (p_kN * 1.1) / sigma_adm
        l_side = math.sqrt(area_req) + (a_col - b_col)/2.0
        b_side = area_req / l_side
        return {
            "l_m": l_side,
            "b_m": b_side,
            "area_m2": area_req
        }

    @staticmethod
    def solve_pile_cap_2(nd_kN: float, dist_piles: float, d_height: float) -> Dict[str, Any]:
        """Bloco de 2 estacas."""
        r_estaca = nd_kN / 2.0
        f_tirante = r_estaca * (dist_piles / (2.0 * d_height))
        return {
            "f_tirante_kN": f_tirante,
            "as_cm2": (f_tirante * 1.15) / (50.0 / 1.15)
        }
