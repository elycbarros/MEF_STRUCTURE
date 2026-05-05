"""
special_elements.py - Solvers para Escadas e Reservatórios.
"""
import math
from dataclasses import dataclass

@dataclass
class StairResult:
    max_moment: float
    required_as: float
    thickness_ok: bool

class SpecialElementsSolver:
    @staticmethod
    def solve_stair(L_horizontal: float, H_vertical: float, load_kN_m2: float, 
                   thickness_cm: float, fck: float, width: float = 1.2) -> dict:
        """
        Dimensiona uma escada de lance único.
        Retorna dicionário completo com esforços e reações.
        """
        L_proj = L_horizontal
        # Carga total considerando peso próprio estimado
        pp = (thickness_cm / 100.0) * 25.0 # kN/m2
        q_total = load_kN_m2 + pp
        
        m_k = (q_total * L_proj**2) / 8.0
        r_k = (q_total * L_proj) / 2.0 # Reação em cada apoio (kN/m)
        
        d = thickness_cm - 2.5
        as_req = (m_k * 1.4 * 100) / (0.8 * d * 43.47)
        
        return {
            "type": "stair",
            "id": "ESC01",
            "L": L_horizontal,
            "q": q_total,
            "Mk": m_k,
            "As_cm2_m": as_req,
            "reaction_kN_m": r_k,
            "total_reaction_kN": r_k * width,
            "status": "ATENDE" if thickness_cm >= (L_proj * 100 / 25) else "REVISAR_ESPESSURA"
        }

    @staticmethod
    def solve_beam(L: float, b: float, h: float, q_kN_m: float, fck: float) -> dict:
        """
        Dimensiona uma viga bi-apoiada isolada.
        """
        # Peso próprio
        pp = (b * h) * 25.0
        q_total = q_kN_m + pp
        
        mk = (q_total * L**2) / 8.0
        vk = (q_total * L) / 2.0
        
        d = h - 0.04 # Estimativa de d
        as_req = (mk * 1.4 * 100) / (0.8 * d * 43.47)
        
        return {
            "type": "beam",
            "id": "V1",
            "L": L,
            "Mk": mk,
            "Vk": vk,
            "As_cm2": as_req,
            "status": "OK" if h >= (L / 12) else "ALTURA_BAIXA"
        }

    @staticmethod
    def solve_column(b: float, h: float, Nd_kN: float, fck: float, L_free: float) -> dict:
        """
        Verifica um pilar isolado sob compressão centrada (simplificado).
        """
        area = b * h
        fcd = fck / 1.4
        
        # Capacidade teórica aproximada (simplificada para ensino)
        n_rd = 0.85 * fcd * area * 1000 # kN (aproximado)
        
        # Índice de esbeltez (lambda = Lf / i)
        i = min(b, h) / math.sqrt(12)
        lambd = L_free / i
        
        return {
            "type": "column",
            "id": "P1",
            "Nd": Nd_kN,
            "NRd": n_rd,
            "lambda": lambd,
            "status": "OK" if Nd_kN < n_rd and lambd < 90 else "REVISAR_SECAO"
        }

    @staticmethod
    def solve_footing(Nd_kN: float, sigma_adm_kPa: float, ap: float, bp: float, fck: float) -> dict:
        """
        Dimensiona uma sapata isolada.
        """
        from footing_solver import solve_isolated_footing, FootingConfig
        cfg = FootingConfig(Nd_kN=Nd_kN, sigma_adm_kPa=sigma_adm_kPa, ap_m=ap, bp_m=bp, fck=fck)
        return solve_isolated_footing(cfg)

    @staticmethod
    def solve_reservoir_wall(height: float, thickness_cm: float, fck: float) -> dict:
        """
        Dimensiona uma parede de reservatório (simplificado para pedagógico).
        """
        from reservoir_pool_solver import analyze_reservoir, ReservoirConfig
        cfg = ReservoirConfig(H=height, wall_thickness=thickness_cm/100.0, fck=fck)
        return analyze_reservoir(cfg)

if __name__ == "__main__":
    solver = SpecialElementsSolver()
    res = solver.solve_stair(L_horizontal=4.0, H_vertical=3.0, load_kN_m2=5.0, thickness_cm=15, fck=25)
    print(f"Escada - Momento: {res.max_moment:.2f} kNm")
    print(f"Escada - As necessário: {res.required_as:.2f} cm2/m")
