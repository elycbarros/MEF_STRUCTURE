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
    def solve_pile_deep(n_spt: float, diam_m: float, method: str = "Aoki-Velloso") -> Dict[str, Any]:
        """Dimensionamento de Estaca Isolada (Aoki-Velloso / Decourt-Quaresma)."""
        area_base = (math.pi * diam_m**2) / 4.0
        perim = math.pi * diam_m
        
        if method == "Aoki-Velloso":
            # Coeficientes K e alpha dependem do solo. Valores padrão (Areia Siltosa):
            k_solo = 400.0 # kPa
            alpha = 0.02
            f1, f2 = 1.75, 3.5
            r_base = (k_solo * n_spt / f1) * area_base
            # Consideramos 10m de fuste para exemplo
            r_lat = (k_solo * n_spt * alpha / f2) * perim * 10.0
        else:
            # Decourt-Quaresma: Rp = qp * Ap, Rl = qu * Al
            qp = 120.0 * n_spt # kPa
            qu = (n_spt / 3.0 + 1.0) # kPa
            r_base = qp * area_base
            r_lat = qu * perim * 10.0
            
        r_total = r_base + r_lat
        return {
            "method": method,
            "r_base_kN": round(r_base, 2),
            "r_lateral_kN": round(r_lat, 2),
            "r_total_kN": round(r_total, 2),
            "safety_factor": 2.0,
            "r_adm_kN": round(r_total / 2.0, 2)
        }

    @staticmethod
    def solve_pile_cap_2(nd_kN: float, dist_piles: float, d_height: float) -> Dict[str, Any]:
        """Bloco de 2 estacas pelo método das bielas."""
        r_estaca = nd_kN / 2.0
        # f_tirante = R * (a / 2d)
        f_tirante = r_estaca * (dist_piles / (2.0 * d_height))
        return {
            "f_tirante_kN": round(f_tirante, 2),
            "as_cm2": round((f_tirante * 1.15) / (50.0 / 1.15), 2)
        }

    @staticmethod
    def estimate_settlement(p_kN: float, b_m: float, e_modulus_kPa: float) -> float:
        """Estimativa de recalque imediato (Teoria da Elasticidade)."""
        # s = q * B * (1 - nu^2) * I / E
        q = p_kN / (b_m**2)
        nu = 0.3
        s_mm = (q * b_m * (1 - nu**2) * 0.88 / e_modulus_kPa) * 1000.0
        return round(s_mm, 2)

    @staticmethod
    def solve_lever_beam(p1_kN: float, p2_kN: float, l_dist: float, a_col: float) -> Dict[str, Any]:
        """Viga Alavanca - Cálculo de equilíbrio."""
        # Somatório de momentos no pilar 2
        r1 = p1_kN * l_dist / (l_dist - a_col/2.0)
        delta_p = r1 - p1_kN
        return {
            "r1_kN": round(r1, 2),
            "delta_p2_kN": round(-delta_p, 2),
            "explanation": "Carga adicional no pilar 1 e alívio no pilar 2 devido à excentricidade."
        }
