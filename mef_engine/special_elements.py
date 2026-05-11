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
        """Solução para sapatas via FootingSolver profissional."""
        from footing_solver import solve_isolated_footing
        return solve_isolated_footing({
            "Nd": Nd_kN,
            "sigma_adm": sigma_adm_kPa,
            "ap": ap,
            "bp": bp,
            "fck": fck
        })

    @staticmethod
    def solve_tension_pro(span: float, q_service: float, p0: float, eccentricity: float) -> dict:
        """Solução pedagógica para protensão (Carga Equivalente e Perdas)."""
        # Carga equivalente: q = 8*P*e / L^2
        q_eq = (8 * p0 * eccentricity) / (span ** 2)
        balance = (q_eq / q_service) * 100 if q_service > 0 else 0
        
        # Perdas imediatas (simplificado: 10%)
        p_eff = p0 * 0.90
        
        # Tensões (simplificado para uma seção retangular b=20, h=50)
        b, h = 0.20, 0.50
        area = b * h
        inertia = (b * h**3) / 12
        y_inf = h / 2
        
        m_total = (q_service - q_eq) * (span**2) / 8
        stress_bottom = (p_eff / area) + (m_total * y_inf / inertia) / 1000 # MPa
        
        return {
            "p0_kN": p0,
            "q_eq_kNm": q_eq,
            "q_service_kNm": q_service,
            "span_m": span,
            "eccentricity_m": eccentricity,
            "balance_ratio": balance,
            "losses_percent": 10.0,
            "stress_bottom_MPa": stress_bottom,
            "fctm_MPa": 2.2, # Exemplo p/ C30
            "summary": {
                "q_eq": q_eq,
                "losses_percent": 10.0,
                "balance_ratio": balance
            }
        }

    @staticmethod
    def solve_advanced_slab(Lx: float, Ly: float, h: float, fck: float, q_dist: float, kv: float = 0, is_raft: bool = True, columns: list = None) -> dict:
        """Solução avançada para lajes e radiers via MEF de Placas (Mindlin)."""
        if is_raft:
            from radier_lab import RadierConfig, run_radier_pipeline
            from radier_solver_v2 import AreaLoad # For possible future use
            
            # Convert MN/m3 to N/m3
            kv_val = kv * 1e6
            
            # Map columns to CSV or direct list if run_radier_pipeline supports it
            # For now, let's use the simplest interface. 
            # If columns is list of {x, y, fz}, we need to format it.
            piles = [] # Could be used for piled raft
            
            config = RadierConfig(
                Lx=Lx, Ly=Ly, h=h, fck=fck, kv=kv_val, q=q_dist * 1000.0,
                nx=min(int(Lx*2)+1, 31), ny=min(int(Ly*2)+1, 31)
            )
            
            # Pedagogical simplification: if no columns, add one central column for stability if needed, 
            # or just rely on distributed load.
            
            res = run_radier_pipeline(config)
            
            # Extra results for summary
            summary = res.get('executive_decision', {})
            summary.update({
                "max_settlement_mm": res.get('mef_summary', {}).get('w_max_mm', 0),
                "mx_pos": res.get('mef_summary', {}).get('mx_abs_max_kNm_m', 0),
                "my_pos": res.get('mef_summary', {}).get('my_abs_max_kNm_m', 0),
                "soil_pressure_kPa": res.get('mef_summary', {}).get('rz_max_kN', 0) / (Lx*Ly) * 100, # Estimativa
                "status_geotech": res.get('executive_decision', {}).get('executive_label', 'OK')
            })
            
            return {
                "success": True,
                "summary": summary,
                "memorial": res.get('memorial_markdown', ''),
                "full_data": res
            }
        else:
            from slab_lab import SlabConfig, SlabLab, PillarSupport
            
            pillars = []
            if columns:
                for i, col in enumerate(columns):
                    pillars.append(PillarSupport(f"P{i+1}", col['x'], col['y'], p_kN=col['fz']))
            
            config = SlabConfig(
                Lx=Lx, Ly=Ly, h=h, fck=fck, q_acid=q_dist,
                pillars=pillars,
                nx=min(int(Lx*2)+1, 31), ny=min(int(Ly*2)+1, 31)
            )
            
            lab = SlabLab(config)
            res = lab.run_full_pipeline()
            
            return {
                "success": True,
                "summary": {
                    "max_settlement_mm": res.get('master', {}).get('mef_summary', {}).get('w_max_mm', 0),
                    "mx_pos": res.get('master', {}).get('mef_summary', {}).get('mx_abs_max_kNm_m', 0),
                    "my_pos": res.get('master', {}).get('mef_summary', {}).get('my_abs_max_kNm_m', 0),
                    "soil_pressure_kPa": 0, # Rigid supports
                    "status_geotech": res.get('executive_decision', {}).get('executive_label', 'OK')
                },
                "memorial": res.get('memorial_markdown', ''),
                "full_data": res
            }

if __name__ == "__main__":
    solver = SpecialElementsSolver()
    res = solver.solve_stair(L_horizontal=4.0, H_vertical=3.0, load_kN_m2=5.0, thickness_cm=15, fck=25)
    print(f"Escada - Momento: {res.get('m_max_kNm'):.2f} kNm")
