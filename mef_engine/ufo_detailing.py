from typing import List, Dict, Any
from column_detailing import ColumnDetailer
from beam_detailing import BeamDetailer
import math

class UFODetailingOrchestrator:
    def __init__(self, engine_3d):
        self.engine = engine_3d

    def generate_building_detailing(self, solve_res: dict, fck: float = 30.0) -> dict:
        """
        Gera o detalhamento executivo para todos os elementos do pórtico 3D.
        """
        efforts = self.engine.get_member_efforts(solve_res["displacements"])
        
        column_reports = []
        beam_reports = []
        total_steel_kg = 0.0
        
        for m in self.engine.members:
            m_efforts = efforts.get(m.id)
            if not m_efforts: continue
            
            # Identificar tipo de elemento (Simples: vertical = pilar, horizontal = viga)
            node_i = self.engine.nodes[m.node_i]
            node_j = self.engine.nodes[m.node_j]
            is_column = abs(node_i.x - node_j.x) < 0.01 and abs(node_i.y - node_j.y) < 0.01
            
            if is_column:
                # 1. Dimensionamento de Pilar (Simplificado para o Detalhador)
                # Nd = Max axial load, Md = Max moment
                nd = max(abs(m_efforts["i"]["N"]), abs(m_efforts["j"]["N"]))
                md_x = max(abs(m_efforts["i"]["My"]), abs(m_efforts["j"]["My"]))
                md_y = max(abs(m_efforts["i"]["Mz"]), abs(m_efforts["j"]["Mz"]))
                
                # Mock solver call (Para obter As_req)
                ac = m.section.b * m.section.h * 10000 # cm2
                as_min = 0.004 * ac
                as_calc = (nd / (50.0/1.15)) + (max(md_x, md_y)*100 / (50.0/1.15 * 0.8 * m.section.h * 100))
                as_final = max(as_min, as_calc)
                
                col_res = {
                    'As_final_cm2': round(as_final, 2),
                    'section': f"{int(m.section.b*100)}x{int(m.section.h*100)}",
                    'fck_MPa': fck,
                    'Nd_kN': round(nd, 2)
                }
                
                det = ColumnDetailer.generate_detailing_summary(col_res)
                det['member_id'] = m.id
                column_reports.append(det)
                total_steel_kg += det['steel_ca50_kg']
            else:
                # 2. Dimensionamento de Viga
                # M_max para flexão, V_max para cisalhamento
                m_max = max(abs(m_efforts["i"]["Mz"]), abs(m_efforts["j"]["Mz"]))
                v_max = max(abs(m_efforts["i"]["Vy"]), abs(m_efforts["j"]["Vy"]))
                
                # Estimativa de As_viga
                d = (m.section.h - 0.04) * 100 # cm
                as_flex = (m_max * 100) / (0.8 * d * (50/1.15)) # kN.cm / (0.8*d*f_yd)
                
                beam_design = {
                    'flexure_bottom': {'As_cm2': round(as_flex, 2)},
                    'flexure_top': {'As_cm2': round(as_flex * 0.3, 2)}, # Porta estribos
                    'shear': {'stirrup_spec': f"Φ 6.3 c/{int(min(d, 20.0))}"}
                }
                
                det = BeamDetailer.generate_detailing_summary(beam_design, m.section.b, m.section.h, fck)
                det['member_id'] = m.id
                beam_reports.append(det)
                # Estimativa de peso viga (aprox 10kg/m)
                total_steel_kg += 10.0 * math.sqrt((node_i.x-node_j.x)**2 + (node_i.y-node_j.y)**2 + (node_i.z-node_j.z)**2)

        return {
            "columns": column_reports,
            "beams": beam_reports,
            "total_steel_kg": round(total_steel_kg, 2),
            "summary": {
                "count_columns": len(column_reports),
                "count_beams": len(beam_reports),
                "avg_steel_density": round(total_steel_kg / (len(column_reports) + len(beam_reports) + 1), 2)
            }
        }
