"""
piles_engine.py - Módulo de cálculo de capacidade de carga para estacas (Fundação Profunda).
Implementa métodos de Aoki-Velloso e Decourt-Quaresma.
"""
from dataclasses import dataclass, field
import math
from typing import List, Optional, Dict, Any

@dataclass
class SoilLayer:
    depth_m: float
    thickness_m: float
    nspt: float
    soil_type: str # 'areia', 'silte', 'argila', 'misto'
    
@dataclass
class PileConfig:
    type: str # 'pre-cast', 'bored', 'cfa', 'strauss', 'franki', 'steel'
    diameter_m: float
    length_m: float
    fck: float = 30.0
    layers: List[SoilLayer] = field(default_factory=list)

class PilesEngine:
    # Coeficientes Aoki-Velloso (1975)
    # Solo: (K [kgf/cm2], alpha [%])
    AOKI_VELLOSO_COEFFS = {
        'areia': (10.0, 0.014),
        'areia_siltosa': (8.0, 0.020),
        'areia_argilosa': (7.0, 0.024),
        'silte': (4.0, 0.030),
        'silte_arenoso': (5.5, 0.022),
        'silte_argiloso': (2.3, 0.034),
        'argila': (2.0, 0.060),
        'argila_arenosa': (3.5, 0.024),
        'argila_siltosa': (2.2, 0.040),
        'misto': (5.0, 0.030)
    }
    
    # Fatores F1 (Ponta) e F2 (Fuste) por tipo de estaca
    PILE_TYPE_FACTORS = {
        'pre-cast': (1.0, 2.0),
        'bored': (3.0, 6.0),
        'cfa': (3.0, 6.0),  # Hélice contínua monitorada
        'strauss': (2.4, 4.8),
        'franki': (2.5, 5.0),
        'steel': (1.0, 1.75)
    }

    @staticmethod
    def calculate_theoretical_stiffness(diameter: float, length: float, E_concrete_GPa: float = 30.0) -> float:
        area = (math.pi * diameter**2) / 4.0
        E_pa = E_concrete_GPa * 1e9
        k_axial = (E_pa * area) / length
        return k_axial / 1000.0 # kN/m

    def solve_aoki_velloso(self, config: PileConfig) -> Dict[str, Any]:
        """
        Método de Aoki-Velloso (1975).
        """
        f1, f2 = self.PILE_TYPE_FACTORS.get(config.type, (1.0, 2.0))
        area_ponta = (math.pi * config.diameter_m**2) / 4.0
        perimetro = math.pi * config.diameter_m
        
        # 1. Resistência de Ponta (Rp)
        # Pega a camada na profundidade da ponta
        base_layer = config.layers[-1] if config.layers else SoilLayer(0, 0, 0, 'misto')
        K, alpha = self.AOKI_VELLOSO_COEFFS.get(base_layer.soil_type, (5.0, 0.030))
        
        # qp = K * Np / F1 (Convertendo K de kgf/cm2 para kN/m2: * 100)
        qp_kN_m2 = (K * 100.0 * base_layer.nspt) / f1
        rp_kN = qp_kN_m2 * area_ponta
        
        # 2. Resistência de Fuste (Rs)
        rs_total_kN = 0
        current_depth = 0
        for layer in config.layers:
            if current_depth >= config.length_m: break
            
            # Espessura efetiva na camada (limitada ao comprimento da estaca)
            effective_thickness = min(layer.thickness_m, config.length_m - current_depth)
            if effective_thickness <= 0: continue
            
            layer_K, layer_alpha = self.AOKI_VELLOSO_COEFFS.get(layer.soil_type, (5.0, 0.030))
            # qs = K * alpha * N / F2
            qs_kN_m2 = (layer_K * 100.0 * layer_alpha * layer.nspt) / f2
            rs_layer_kN = qs_kN_m2 * (perimetro * effective_thickness)
            rs_total_kN += rs_layer_kN
            current_depth += layer.thickness_m
            
        qu_kN = rp_kN + rs_total_kN
        q_adm_kN = qu_kN / 2.0 # FS = 2.0
        
        return {
            "method": "Aoki-Velloso",
            "rp_kN": round(rp_kN, 2),
            "rs_kN": round(rs_total_kN, 2),
            "qu_kN": round(qu_kN, 2),
            "q_adm_kN": round(q_adm_kN, 2),
            "f1": f1,
            "f2": f2,
            "area_ponta_m2": round(area_ponta, 4),
            "perimetro_m": round(perimetro, 3)
        }

    def solve_decourt_quaresma(self, config: PileConfig) -> Dict[str, Any]:
        """
        Método de Decourt-Quaresma (1978/1996).
        """
        # Fatores alpha (ponta) e beta (fuste)
        # Simplificado para estacas comuns
        alpha_dq = 1.0 
        beta_dq = 1.0
        if config.type in ('bored', 'cfa'):
            alpha_dq = 0.85
            beta_dq = 0.80
        
        area_ponta = (math.pi * config.diameter_m**2) / 4.0
        perimetro = math.pi * config.diameter_m
        
        # 1. Ponta (qp = K * Np)
        # K depende do tipo de solo: Argila=120, Silte=200, Areia=400 (kN/m2)
        soil_k = {'argila': 120.0, 'silte': 200.0, 'areia': 400.0, 'misto': 250.0}
        base_layer = config.layers[-1] if config.layers else SoilLayer(0, 0, 0, 'misto')
        k_val = soil_k.get(base_layer.soil_type, 250.0)
        
        qp_kN_m2 = k_val * base_layer.nspt * alpha_dq
        rp_kN = qp_kN_m2 * area_ponta
        
        # 2. Fuste (qs = 10 * (Nspt/3 + 1))
        # Nspt médio no fuste
        avg_nspt = sum(l.nspt for l in config.layers) / len(config.layers) if config.layers else 0
        qs_kN_m2 = 10.0 * (avg_nspt / 3.0 + 1.0) * beta_dq
        rs_kN = qs_kN_m2 * perimetro * config.length_m
        
        qu_kN = rp_kN + rs_kN
        q_adm_kN = qu_kN / 2.0
        
        return {
            "method": "Decourt-Quaresma",
            "rp_kN": round(rp_kN, 2),
            "rs_kN": round(rs_kN, 2),
            "qu_kN": round(qu_kN, 2),
            "q_adm_kN": round(q_adm_kN, 2),
            "avg_nspt_fuste": round(avg_nspt, 1)
        }

    def verify_structural_capacity(self, config: PileConfig, Nd_kN: float) -> Dict[str, Any]:
        """
        Verificação estrutural NBR 6118.
        """
        area_c = (math.pi * config.diameter_m**2) / 4.0
        fcd = (config.fck * 1000.0) / 1.4 # kN/m2
        
        # Capacidade teórica do concreto (apenas 85% para considerar efeitos de concretagem)
        # E reduzido para fundações (fator 0.85 * 0.85 approx 0.7)
        nr_concrete_kN = 0.85 * 0.85 * fcd * area_c
        
        utilization = (Nd_kN / nr_concrete_kN) * 100
        
        return {
            "nd_kN": Nd_kN,
            "nr_concrete_kN": round(nr_concrete_kN, 2),
            "utilization_pct": round(utilization, 2),
            "status": "OK" if utilization <= 100 else "EXCEEDS_STRUCTURAL_LIMIT"
        }

    def run_full_analysis(self, config: PileConfig, applied_load_kN: float = 0.0) -> Dict[str, Any]:
        av = self.solve_aoki_velloso(config)
        dq = self.solve_decourt_quaresma(config)
        
        # Adota a menor das duas como conservadora para o mestre
        q_adm_geotech = min(av['q_adm_kN'], dq['q_adm_kN'])
        
        struct = self.verify_structural_capacity(config, applied_load_kN)
        
        return {
            "config": {
                "type": config.type,
                "diameter_m": config.diameter_m,
                "length_m": config.length_m,
                "fck": config.fck
            },
            "geotechnical": {
                "aoki_velloso": av,
                "decourt_quaresma": dq,
                "q_adm_final_kN": q_adm_geotech
            },
            "structural": struct,
            "geotech_status": "OK" if applied_load_kN <= q_adm_geotech else "OVERLOAD_GEOTECH",
            "overall_status": "OK" if (applied_load_kN <= q_adm_geotech and struct['status'] == 'OK') else "FAIL"
        }
