"""
beam_engine.py - Motor Consolidado de Vigas (Domínio: Vigas).
Segue rigorosamente a NBR 6118:2023.
"""
import math
from typing import Dict, Any, Optional

class BeamEngine:
    """
    Centraliza todos os cálculos relacionados a vigas e elementos lineares.
    Substitui tabelas por soluções analíticas diretas.
    """
    
    @staticmethod
    def calculate_flexure(md_kNm: float, b_w: float, d: float, fck: float, fyk: float) -> Dict[str, Any]:
        """
        Dimensionamento à flexão simples (ELU).
        Usa o diagrama parábola-retângulo da NBR 6118.
        """
        fcd = fck / 1.4
        fyd = fyk / 1.15
        
        # Coeficientes para fck <= 50 MPa
        eta = 0.85
        lambda_val = 0.8
        
        # Equação: Md = 0.85 * fcd * b * (lambda * x) * (d - 0.5 * lambda * x)
        # Resulta em uma equação de 2º grau para (lambda * x)
        # a = 0.5 * 0.85 * fcd * b
        # b = -0.85 * fcd * b * d
        # c = Md
        
        a_coeff = 0.425 * fcd * b_w * 1000.0 # kPa to kN/m
        b_coeff = -0.85 * fcd * b_w * d * 1000.0
        c_coeff = md_kNm
        
        delta = b_coeff**2 - 4 * a_coeff * c_coeff
        if delta < 0:
            return {"status": "FALHA_COMPRESSAO_CONCRETO", "as_cm2": 0}
            
        lx = (-b_coeff - math.sqrt(delta)) / (2 * a_coeff)
        x = lx / lambda_val
        x_d = x / d
        
        # Braço de alavanca z
        z = d - 0.4 * x
        as_req = md_kNm / (fyd/10.0 * z * 100.0) # cm2 (fyd em kN/cm2, z em cm)
        as_req *= 100.0 # Correção de unidade para cm2
        
        # Simplificação para retorno rápido (cm2)
        as_cm2 = (md_kNm * 100) / (fyd/10.0 * z * 100)
        
        return {
            "x_d": x_d,
            "as_cm2": as_cm2,
            "z_m": z,
            "domain": 2 if x_d <= 0.259 else (3 if x_d <= 0.45 else 4)
        }

    @staticmethod
    def solve_corbel(fd: float, a: float, d: float, b: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Consolos Curtos - Biela e Tirante."""
        theta = math.atan(d / a)
        f_tirante = fd * (a / d)
        as_principal = (f_tirante * 1.15) / (fyk / 10.0)
        return {
            "type": "corbel",
            "f_tirante_kN": f_tirante,
            "as_principal_cm2": as_principal,
            "theta_deg": math.degrees(theta)
        }

    @staticmethod
    def solve_gerber_tooth(vd: float, a: float, d: float, b: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Dente Gerber - Biela e Tirante."""
        as_suspensao = (vd * 1.15) / (fyk / 10.0)
        f_h = vd * (a / d) + 0.2 * vd
        as_tirante = (f_h * 1.15) / (fyk / 10.0)
        return {
            "type": "gerber_tooth",
            "as_suspensao_cm2": as_suspensao,
            "as_tirante_cm2": as_tirante
        }

    @staticmethod
    def solve_deep_beam(fd: float, l_span: float, h_total: float, b_width: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Viga Parede - Analítico."""
        z = 0.2 * (l_span + 2 * h_total)
        z = min(z, 0.6 * l_span)
        m_max = (fd * l_span) / 8.0
        as_principal = (m_max / z * 1.15) / (fyk / 10.0)
        return {
            "type": "deep_beam",
            "z_m": z,
            "as_principal_cm2": as_principal
        }
