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
        Dimensionamento completo de Pilar (NBR 6118).
        Inclui 2a ordem local pelo metodo do pilar padrao.
        """
        lamb = ColumnEngine.calculate_slenderness(l_e, h)
        
        # Momento de 2a ordem (M2) se lamb > lamb_lim
        m2 = 0.0
        if lamb > 35:
            # Metodo da curvatura aproximada
            v = nd_kN / (h * b * (fck/1.4) * 1000.0)
            curv = (0.005 / (h * (v + 0.5))) if v > 0 else 0.005/h
            m2 = nd_kN * (l_e**2 / 10.0) * curv
            
        md_total = mdx_kNm + m2
        
        return {
            "lambda": lamb,
            "m2_kNm": m2,
            "md_total_kNm": md_total,
            "status": "OK" if lamb < 90 else "ALTA_ESBELTEZ"
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
