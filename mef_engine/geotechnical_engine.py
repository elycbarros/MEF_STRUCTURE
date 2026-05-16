"""
geotechnical_engine.py - Motor de Geotecnia (Mestre Lab).
Provê análises de sondagem SPT e correlações para coeficientes de recalque.
"""
from typing import List, Dict, Any
import math

class GeotechnicalEngine:
    @staticmethod
    def analyze_spt(spt_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa dados de sondagem SPT e retorna perfil geotécnico simplificado.
        """
        from radier_geotechnics import nspt_to_kv
        
        profile = []
        total_kv = 0
        max_nspt = 0
        soil_counts = {}
        
        for layer in spt_data:
            depth = layer.get('depth_m', 0)
            nspt = layer.get('nspt', 0)
            soil = layer.get('soil_type', 'misto')
            
            kv = nspt_to_kv(nspt, soil_type=soil)
            total_kv += kv
            
            if nspt > max_nspt:
                max_nspt = nspt
            
            soil_counts[soil] = soil_counts.get(soil, 0) + 1
            
            profile.append({
                "depth_m": depth,
                "nspt": nspt,
                "soil_type": soil,
                "kv_kN_m3": round(kv / 1000, 2)
            })
            
        if soil_counts:
            dominant_soil = max(soil_counts, key=soil_counts.get)
        else:
            dominant_soil = "misto"
            
        avg_nspt = sum(layer.get('nspt', 0) for layer in spt_data) / len(spt_data) if spt_data else 0
        avg_kv = total_kv / len(spt_data) if spt_data else 0
        
        # Tensão Admissível (estimativa empírica Terzaghi/Teixeira)
        # sigma_adm = N_avg / 50 (kgf/cm2) -> N_avg * 20 (kPa)
        sigma_adm_kPa = avg_nspt * 20.0 
        
        return {
            "profile": profile,
            "avg_nspt": round(avg_nspt, 1),
            "avg_kv_kN_m3": round(avg_kv / 1000, 2),
            "sigma_adm_kPa": round(sigma_adm_kPa, 2),
            "max_nspt": max_nspt,
            "dominant_soil": dominant_soil,
            "classification": "Compacto" if max_nspt > 15 else "Medio" if max_nspt > 8 else "Fofo"
        }

class NonLinearWinklerSolver:
    """
    Motor de Interação Solo-Estrutura (ISE) não-linear.
    Implementa a plastificação do solo quando a tensão atinge sigma_adm.
    """
    def __init__(self, q_adm_kPa: float, kv_initial_kN_m3: float):
        self.q_adm = q_adm_kPa
        self.kv_initial = kv_initial_kN_m3

    def solve_iterative_reactions(self, displacements_m: List[float], areas_m2: List[float]) -> Dict:
        """
        Calcula as reações corrigindo pontos que excedem a tensão admissível.
        """
        n = len(displacements_m)
        reactions_kN = [0.0] * n
        is_plastified = [False] * n
        
        total_load_excess_kN = 0.0
        
        # 1. Cálculo inicial (Elástico Linear)
        for i in range(n):
            pressure = displacements_m[i] * self.kv_initial
            if pressure > self.q_adm:
                reactions_kN[i] = self.q_adm * areas_m2[i]
                excess_pressure = pressure - self.q_adm
                total_load_excess_kN += excess_pressure * areas_m2[i]
                is_plastified[i] = True
            else:
                reactions_kN[i] = pressure * areas_m2[i]
                
        # 2. Redistribuição de Carga (Simplificada para Modo Mestre)
        # Em um modelo real, isso exigiria resolver o sistema K.u = F novamente 
        # com rigidez reduzida nos pontos plastificados.
        if total_load_excess_kN > 0:
            elastic_nodes = [i for i, p in enumerate(is_plastified) if not p]
            if elastic_nodes:
                redistributed_per_node = total_load_excess_kN / len(elastic_nodes)
                for idx in elastic_nodes:
                    reactions_kN[idx] += redistributed_per_node
                    
        return {
            "reactions_kN": reactions_kN,
            "is_plastified": is_plastified,
            "plastification_ratio": sum(is_plastified) / n if n > 0 else 0,
            "total_excess_redistributed_kN": round(total_load_excess_kN, 2)
        }
