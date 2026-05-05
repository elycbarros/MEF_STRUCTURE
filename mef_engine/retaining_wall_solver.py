"""
retaining_wall_solver.py - Solver para Muros de Arrimo por Gravidade ou Flexao.
"""
import math
from typing import Dict, Any

def solve_retaining_wall(h: float, b_base: float, gamma_soil: float, phi_soil: float, q_load: float = 0.0) -> Dict[str, Any]:
    """
    Calcula a estabilidade de um muro de arrimo simplificado.
    """
    # 1. Empuxo Ativo (Rankine)
    phi_rad = math.radians(phi_soil)
    ka = (1 - math.sin(phi_rad)) / (1 + math.sin(phi_rad))
    
    # Pressao do solo
    pa_soil = 0.5 * ka * gamma_soil * (h**2)
    # Pressao da sobrecarga
    pa_q = ka * q_load * h
    
    pa_total = pa_soil + pa_q
    # Centro de pressao (estimado)
    y_pa = (pa_soil * (h/3.0) + pa_q * (h/2.0)) / pa_total if pa_total > 0 else 0
    
    # 2. Momento Tombador
    m_tomb = pa_total * y_pa
    
    # 3. Momento Estabilizador (Peso Proprio - assumindo muro de concreto gamma=25)
    # Geometria simplificada: retangulo de base b_base
    weight = b_base * h * 25.0
    m_estab = weight * (b_base / 2.0)
    
    # 4. Fatores de Seguranca
    fs_tomb = m_estab / m_tomb if m_tomb > 0 else 10.0
    
    # Deslizamento (atrito solo-concreto aprox 0.5 * tan(phi))
    fr = weight * math.tan(0.67 * phi_rad)
    fs_desl = fr / pa_total if pa_total > 0 else 10.0
    
    return {
        "type": "retaining_wall",
        "h": h,
        "b_base": b_base,
        "ka": ka,
        "pa_total": pa_total,
        "m_tomb": m_tomb,
        "m_estab": m_estab,
        "fs_tomb": fs_tomb,
        "fs_desl": fs_desl,
        "status": "OK" if (fs_tomb >= 1.5 and fs_desl >= 1.5) else "INSTAVEL"
    }
