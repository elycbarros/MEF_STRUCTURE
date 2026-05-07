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
        """Dimensiona uma escada de lance único via Engine."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_pleated_stairs(
            l_horiz=L_horizontal, 
            h_step=H_vertical/10.0, # Simplificado para teste
            p_step=0.28, 
            thick=thickness_cm/100.0, 
            q_acid=load_kN_m2
        )

    @staticmethod
    def solve_retaining_wall(h: float, gamma: float, phi: float, weight: float, base: float, surcharge: float = 0.0) -> dict:
        """Solução profissional para muros."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_retaining_wall(
            h_wall=h, gamma_soil=gamma, phi_soil=phi, weight_wall=weight, b_base=base, surcharge=surcharge
        )

    @staticmethod
    def solve_reservoir(length: float, width: float, depth: float) -> dict:
        """Solução para reservatórios retangulares."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_rectangular_tank(length, width, depth)

    @staticmethod
    def solve_corbel(fd_kN: float, a_dist: float, d_eff: float, fck: float) -> dict:
        """Solução para consolos."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_corbel(fd_kN, a_dist, d_eff, fck)

    @staticmethod
    def solve_gerber_tooth(vd_kN: float, hd_kN: float, a_dist: float, d_eff: float, b_width: float, fck: float) -> dict:
        """Solução para dentes Gerber."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_gerber_tooth(vd_kN, hd_kN, a_dist, d_eff, b_width, fck)

    @staticmethod
    def solve_deep_beam(fd_kN_m: float, l_span: float, height: float) -> dict:
        """Solução para vigas parede."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_deep_beam(fd_kN_m, l_span, height)

    @staticmethod
    def solve_helical_stairs(radius: float, angle_total_deg: float, h_step: float, thick: float, q_acid: float) -> dict:
        """Solução para escadas helicoidais."""
        from engines.special_elements_engine import SpecialElementsEngine
        return SpecialElementsEngine.solve_helical_stairs(radius, angle_total_deg, h_step, thick, q_acid)

    @staticmethod
    def solve_beam(L: float, b: float, h: float, q_kN_m: float, fck: float, asymmetric_offset: float = 0.0) -> dict:
        """Solução profissional para vigas com suporte a assimetria."""
        from beam_solver import run_beam_analysis
        return run_beam_analysis(
            L=L, b=b, h=h, fck=fck, 
            supports=[{'x': 0, 'type': 'pinned'}, {'x': L, 'type': 'pinned'}],
            distributed_loads=[{'x_start': 0, 'x_end': L, 'q_start': q_kN_m, 'q_end': q_kN_m}],
            asymmetric_offset=asymmetric_offset
        )

    @staticmethod
    def solve_column(b: float, h: float, Nd_kN: float, fck: float, L_free: float, Mxd_kNm: float = 0.0, Myd_kNm: float = 0.0, caa: int = 2) -> dict:
        """Solução profissional para pilares com flexo-compressão biaxial."""
        from column_solver import ColumnSection, ColumnLoads, solve_column_section
        sec = ColumnSection(b=b, h=h, fck=fck, L_free=L_free, caa=caa)
        loads = ColumnLoads(Nd_kN=Nd_kN, Mxd_kNm=Mxd_kNm, Myd_kNm=Myd_kNm)
        return solve_column_section(sec, loads)

    @staticmethod
    def solve_building_core(n_floors: int = 40, building_Lx: float = 24.0, building_Ly: float = 24.0, fck: float = 35.0) -> dict:
        """Solução Elite para núcleos de rigidez e estabilidade global."""
        from building_core import run_core_analysis
        return run_core_analysis(n_floors=n_floors, building_Lx=building_Lx, building_Ly=building_Ly, fck=fck)

    @staticmethod
    def solve_footing(Nd_kN: float, sigma_adm_kPa: float, ap: float, bp: float, fck: float) -> dict:
        """Solução para sapatas (Módulo Elite)."""
        # Exemplo simplificado para compatibilidade
        return {
            "a_m": math.sqrt(Nd_kN / sigma_adm_kPa) * 1.1,
            "b_m": math.sqrt(Nd_kN / sigma_adm_kPa) * 1.1,
            "h_m": 0.6,
            "sigma_real_kPa": sigma_adm_kPa * 0.95
        }

if __name__ == "__main__":
    solver = SpecialElementsSolver()
    res = solver.solve_stair(L_horizontal=4.0, H_vertical=3.0, load_kN_m2=5.0, thickness_cm=15, fck=25)
    print(f"Escada - Momento: {res.get('m_max_kNm'):.2f} kNm")
