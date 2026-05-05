"""
special_elements_engine.py - Motor de Elementos Especiais (Domínio: Especiais).
"""
import math
from typing import Dict, Any

class SpecialElementsEngine:
    """
    Centraliza cálculos de escadas, reservatórios e muros.
    """
    
    @staticmethod
    def solve_pleated_stairs(l_horiz: float, h_step: float, p_step: float, thick: float, q_acid: float) -> Dict[str, Any]:
        """
        Escadas Plissadas (Zig-zag).
        Calcula os momentos de 'dobra' nos degraus.
        """
        alpha = math.atan(h_step / p_step)
        # Carga por metro linear de degrau
        g_pp = thick * 25.0 * (1.0 / math.cos(alpha))
        q_total = (g_pp + q_acid) * p_step
        
        # Momento fletor simplificado no vao (considerando continuidade plissada)
        m_max = (q_total * l_horiz**2) / 10.0 # Aproximacao para escada autoportante plissada
        
        return {
            "type": "pleated_stairs",
            "alpha_deg": math.degrees(alpha),
            "m_max_kNm": m_max,
            "q_total_kN_m": q_total,
            "explanation": "O comportamento plissado exige verificacao de torcao e flexao nos cantos dos degraus."
        }

    @staticmethod
    def solve_retaining_wall(h_wall: float, gamma_soil: float, phi_soil: float) -> Dict[str, Any]:
        """Muros de Arrimo - Estabilidade."""
        ka = (1 - math.sin(math.radians(phi_soil))) / (1 + math.sin(math.radians(phi_soil)))
        e_total = 0.5 * gamma_soil * ka * h_wall**2
        return {
            "ka": ka,
            "empuxo_kN_m": e_total
        }
