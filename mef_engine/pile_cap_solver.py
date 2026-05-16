"""
pile_cap_solver.py - Solver para Blocos sobre Estacas (Modelos de Biela-e-Tirante).
"""
import math
from typing import Dict, Any

def solve_pile_cap_2_piles(nd_kN: float, dist_piles: float, ap: float, bp: float, diam_pile: float, d_height: float, fck: float, fyk: float) -> Dict[str, Any]:
    """
    nd_kN: Carga do pilar de projeto
    dist_piles: Distancia entre eixos das estacas (m)
    ap, bp: Dimensoes do pilar (m)
    d_height: Altura util do bloco (m)
    """
    # 1. Reacao em cada estaca (R)
    r_estaca = nd_kN / 2.0
    
    # 2. Modelo de Biela (Blevot)
    # Distancia da face do pilar ao eixo da estaca
    a = (dist_piles / 2.0) - (ap / 4.0)
    theta = math.atan(d_height / a)
    
    # Forca no Tirante (T)
    f_tirante = r_estaca * (a / d_height)
    
    # 3. Armadura (As)
    fyd = fyk / 1.15
    as_principal = (f_tirante * 100.0) / (fyd / 10.0) # cm2
    
    # 4. Verificacao da Biela (ULS)
    fcd = fck / 1.4
    # Tensao na biela no topo (face do pilar)
    f_biela = r_estaca / math.sin(theta)
    # Area da biela no topo (estimada)
    area_biela = (ap * bp) / 2.0
    tensao_biela = f_biela / area_biela
    v_rd2 = 0.6 * (1 - fck/250.0) * fcd * 1000.0
    
    # Auditoria Forensic: Blevot (Biela) vs Flexão (Viga)
    # No modelo de viga: M = R * a => As = M / (0.9 * d * fyd)
    m_viga = r_estaca * a
    as_viga = (m_viga * 100.0) / (0.9 * d_height * (fyd / 10.0))
    diff = abs(as_principal - as_viga) / max(as_principal, 1e-9) * 100.0

    duel = [
        {
            "parameter": "As_principal",
            "classical_value": f"{as_principal:.2f} cm²",
            "mef_value": f"{as_viga:.2f} cm²",
            "difference_percent": round(diff, 1),
            "insight": "Modelos de Biela (Blevot) são mais precisos para blocos curtos (D/A < 2), enquanto a teoria de vigas tende a subestimar a tração no tirante devido à não-linearidade das deformações."
        }
    ]

    return {
        "type": "pile_cap",
        "n_piles": 2,
        "r_estaca_kN": r_estaca,
        "f_tirante_kN": f_tirante,
        "as_principal_cm2": as_principal,
        "theta_deg": math.degrees(theta),
        "tensao_biela_kPa": tensao_biela,
        "v_rd2_kPa": v_rd2,
        "status": "OK" if (tensao_biela <= v_rd2 and math.degrees(theta) >= 30) else "REVISAR_GEOMETRIA",
        "calculation_trace": {
            "duel": duel
        }
    }
