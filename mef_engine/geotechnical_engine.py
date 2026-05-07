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
        dominant_soil = "misto"
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
            
        avg_nspt = sum(layer.get('nspt', 0) for layer in spt_data) / len(spt_data) if spt_data else 0
        avg_kv = total_kv / len(spt_data) if spt_data else 0
        sigma_adm_kPa = avg_nspt * 10 # Estimativa simplificada: 10 kPa por golpe (conservador)
        
        return {
            "profile": profile,
            "avg_nspt": round(avg_nspt, 1),
            "avg_kv_kN_m3": round(avg_kv / 1000, 2),
            "sigma_adm_calc_kPa": round(sigma_adm_kPa, 2),
            "max_nspt": max_nspt,
            "dominant_soil": dominant_soil,
            "safety_factor": 2.0,
            "allowable_pressure_kPa": round(sigma_adm_kPa, 2),
            "classification": "Compacto" if max_nspt > 15 else "Medio" if max_nspt > 8 else "Fofo"
        }
