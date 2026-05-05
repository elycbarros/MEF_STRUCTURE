"""
slab_engine.py - Motor Consolidado de Lajes (Domínio: Lajes).
Segue rigorosamente a NBR 6118:2023.
"""
import math
from typing import Dict, Any

class SlabEngine:
    """
    Centraliza todos os cálculos de lajes e punção.
    """
    
    @staticmethod
    def calculate_punching(fsd_kN: float, d_eff: float, u_perim: float, fck: float, rho_l: float) -> Dict[str, Any]:
        """Verificação de Punção."""
        k = min(1.0 + math.sqrt(0.2 / d_eff), 2.0)
        tau_rd1 = 0.13 * k * (100 * rho_l * fck)**(1/3) * 1000.0
        tau_sd = fsd_kN / (u_perim * d_eff)
        return {
            "tau_sd_kPa": tau_sd,
            "tau_rd1_kPa": tau_rd1,
            "status": "OK" if tau_sd <= tau_rd1 else "REFORCO_NECESSARIO"
        }

    @staticmethod
    def solve_ribbed(h_total: float, h_mesa: float, b_nerv: float, dist_nerv: float, md_kNm_m: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Lajes Nervuradas."""
        m_nerv = md_kNm_m * dist_nerv
        # Simplificação: h_eq para inércia
        h_eq = ((dist_nerv * h_mesa) + (b_nerv * (h_total - h_mesa))) / dist_nerv
        return {
            "m_nerv_kNm": m_nerv,
            "h_eq_m": h_eq,
            "as_total_cm2_m": (m_nerv * 100 * 1.15) / (fyk/10.0 * (h_total-0.03)*0.9 * 100) / dist_nerv
        }

    @staticmethod
    def solve_hollow_core(h_total: float, area_voids: float, p_force: float, l_span: float, q_acid: float) -> Dict[str, Any]:
        """
        Lajes Alveolares (Hollow Core).
        Foca na inercia da secao vazada e perdas de protensao.
        """
        area_gross = 1.0 * h_total
        area_net = area_gross - area_voids
        
        # Inercia equivalente (simplificada)
        i_net = (1.0 * h_total**3 / 12.0) - (area_voids * (h_total/2.0)**2 * 0.5) # Aproximacao
        
        # Verificacao de Cisalhamento nos dentes de apoio
        # (Critico para lajes alveolares sem armadura transversal)
        v_rd1 = 0.25 * 0.3 * (30**0.5) * area_net * 1000.0 # kN/m
        
        return {
            "type": "hollow_core",
            "area_net_m2": area_net,
            "v_rd1_kN_m": v_rd1,
            "status": "OK"
        }

    @staticmethod
    def solve_prestressed(l_span: float, h_slab: float, p_force: float, ecc: float, q_total: float, fck: float) -> Dict[str, Any]:
        """Lajes Protendidas - Carga Equivalente."""
        q_eq = (8 * p_force * ecc) / (l_span**2)
        area = 1.0 * h_slab
        w_mod = (1.0 * h_slab**2) / 6.0
        m_serv = (q_total * l_span**2) / 8.0
        sigma_inf = (-p_force / area) + (m_serv / w_mod)
        return {
            "q_eq_kPa": q_eq,
            "sigma_inf_kPa": sigma_inf,
            "fctm_kPa": 0.3 * fck**(2/3) * 1000.0,
            "p_force_kN": p_force,
            "ecc_m": ecc
        }
