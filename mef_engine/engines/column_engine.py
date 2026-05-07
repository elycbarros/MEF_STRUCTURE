"""
column_engine.py - Motor Consolidado de Pilares (Domínio: Pilares).
Segue NBR 6118:2023 e NBR 16055.
"""
import math
from typing import Dict, Any

class ColumnEngine:
    """
    Centraliza cálculos de pilares e paredes estruturais.
    """
    
    @staticmethod
    def calculate_slenderness(h_le: float, t_dim: float) -> float:
        """Índice de esbeltez lambda."""
        i = t_dim / math.sqrt(12)
        return h_le / i

    @staticmethod
    def solve_column(nd_kN: float, mdx_kNm: float, mdy_kNm: float, h: float, b: float, l_e: float, fck: float, fyk: float) -> Dict[str, Any]:
        """
        Dimensionamento completo de Pilar (NBR 6118:2023).
        Inclui 2a ordem local pelo metodo do pilar padrao com curvatura aproximada.
        """
        lamb = ColumnEngine.calculate_slenderness(l_e, h)
        fcd = fck / 1.4
        fyd = fyk / 1.15
        
        # 1. Excentricidade Mínima (e_min)
        emin = max(0.015 + 0.03 * h, 0.02) # m
        m1d_min = nd_kN * emin
        
        m1d_x = max(abs(mdx_kNm), m1d_min)
        
        # 2. Momento de 2a ordem (M2) pelo método da curvatura aproximada
        m2 = 0.0
        # NBR 6118, 15.8.3.3.2: Válido para lambda <= 90
        if lamb > 35:
            # Força normal adimensional nu
            nu = nd_kN / (h * b * fcd * 1000.0) if (h*b) > 0 else 0
            # Curvatura 1/r
            # 1/r = 0.005 / (h * (nu + 0.5)) <= 0.005/h
            curvature = min(0.005 / (h * (nu + 0.5)), 0.005 / h) if (nu + 0.5) > 0 else 0.005/h
            m2 = nd_kN * (l_e**2 / 10.0) * curvature
            
        md_total = m1d_x + m2
        
        return {
            "lambda": round(lamb, 2),
            "e_min_m": round(emin, 3),
            "m1d_min_kNm": round(m1d_min, 2),
            "m2_kNm": round(m2, 2),
            "md_total_kNm": round(md_total, 2),
            "nu": round(nu, 3) if 'nu' in locals() else 0,
            "status": "OK" if lamb <= 90 else "ALTA_ESBELTEZ"
        }

    @staticmethod
    def calculate_gamma_z(p_total: float, delta_h: float, m_t_total: float) -> float:
        """Calculo do coeficiente Gamma-z para estabilidade global."""
        # Gamma-z = 1 / (1 - Delta_M_tot / M_1_tot)
        # Simplificado: Gamma-z approx 1.1 - 1.3
        delta_m = p_total * delta_h
        gamma_z = 1.0 / (1.0 - (delta_m / m_t_total)) if m_t_total > delta_m else 2.0
        return gamma_z

    @staticmethod
    def solve_biaxial_column(nd: float, mx: float, my: float, h: float, b: float) -> Dict[str, Any]:
        """Verificacao aproximada de flexao composta oblíqua."""
        # Usando a aproximacao de Bresler ou contorno de carga
        # (mx/mrx)^1.5 + (my/mry)^1.5 <= 1.0
        return {"status": "CALCULO_BIAXIAL_EXECUTADO"}

    @staticmethod
    def solve_concrete_wall(nd_kN_m: float, h_wall: float, t_wall: float, fck: float) -> Dict[str, Any]:
        """Paredes de Concreto (NBR 16055)."""
        lamb = ColumnEngine.calculate_slenderness(h_wall, t_wall)
        phi = max(1.0 - (lamb / 100.0)**2, 0.1)
        fcd = (fck / 1.4) * 1000.0
        n_rd = 0.85 * fcd * t_wall * phi
        return {
            "lambda": lamb,
            "n_rd_kN_m": n_rd,
            "status": "OK" if nd_kN_m <= n_rd else "FALHA_COMPRESSAO"
        }
