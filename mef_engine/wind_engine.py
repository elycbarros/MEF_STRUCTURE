"""
wind_engine.py — Motor de Analise de Vento e Estabilidade Global (NBR 6123 / 6118).
"""
import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class WindConfig:
    v0: float = 30.0    # Velocidade basica (m/s)
    s1: float = 1.0     # Fator topografico
    s2_class: str = "B" # Categoria de rugosidade
    s3: float = 1.0     # Fator estatistico
    height: float = 30.0
    width_x: float = 12.0
    width_y: float = 20.0
    categoria: int = 2
    classe: str = "B"
    is_dynamic: bool = False
    f1: float = 0.5
    zeta: float = 0.01
    beta: float = 1.0

class WindEngine:
    """Motor de analise de vento e estabilidade global."""

    def __init__(self, cfg: WindConfig | None = None):
        self.cfg = cfg or WindConfig()
        self.v0 = self.cfg.v0
        self.s1 = self.cfg.s1
        self.s3 = self.cfg.s3
        self.categoria = self.cfg.categoria
        self.classe = self.cfg.classe

    @staticmethod
    def calculate_s2(z: float, category: str = "II", class_size: str = "B") -> float:
        """Calcula o fator S2 conforme Tabela 1 da NBR 6123."""
        # Valores simplificados para Categoria II, Classe B
        # b = 1.0, p = 0.15, Fr = 1.0
        b, p, fr = 1.0, 0.15, 1.0
        if z < 5: z = 5
        return b * fr * (z / 10.0)**p

    @classmethod
    def calculate_dynamic_pressure(cls, cfg: WindConfig) -> Dict:
        """Calcula a pressao dinamica do vento em varias alturas."""
        results = []
        for z in range(0, int(cfg.height) + 5, 5):
            if z == 0: z = 2 # Evitar zero
            s2 = cls.calculate_s2(z)
            vk = cfg.v0 * cfg.s1 * s2 * cfg.s3
            q = 0.613 * (vk**2) # N/m2
            results.append({"z": z, "vk": round(vk, 2), "q_Pa": round(q, 1)})
        
        # Coeficiente de Arraste (Ca) simplificado para retangulo
        ca = 1.2 
        force_total_kN = (results[-1]['q_Pa'] * cfg.width_x * cfg.height * ca) / 1000.0
        
        return {
            "profile": results,
            "force_total_kN": round(force_total_kN, 1),
            "ca": ca
        }

    @staticmethod
    def estimate_gamma_z(total_height: float, total_load_kN: float, delta_h_mm: float) -> float:
        """Estimativa simplificada do coeficiente gamma_z."""
        if total_height > 40: return 1.12
        if total_height > 20: return 1.07
        return 1.03

    def generate_force_profile(self, height: float, width: float, depth: float, 
                               step: float = 1.0, area_level: float = None, cf_manual: float = None) -> Dict:
        """
        Gera o perfil completo de forças de vento conforme NBR 6123.
        Discretiza a altura em degraus (step).
        """
        results = []
        total_force_kN = 0.0
        base_moment_kNm = 0.0
        
        # Coeficiente de Arraste (Ca) ou Força (Cf)
        cf = cf_manual if cf_manual is not None else 1.2
        
        # Discretização
        z = 0.0
        while z <= height:
            if z == 0: z_calc = 1.0 # Mínimo para cálculo de S2
            else: z_calc = z
            
            s2 = self.calculate_s2(z_calc)
            vk = self.v0 * self.s1 * s2 * self.s3
            q_Pa = 0.613 * (vk**2)
            
            # Força no nível (tributária)
            area = (area_level if area_level else width * step)
            force_kN = (q_Pa * area * cf) / 1000.0
            
            results.append({
                "z": round(z, 2),
                "vk": round(vk, 2),
                "q_Pa": round(q_Pa, 1),
                "force_kN": round(force_kN, 2)
            })
            
            total_force_kN += force_kN
            base_moment_kNm += force_kN * z
            
            z += step
            if z > height and z - step < height:
                z = height # Força o último nível no topo exato

        return {
            "profile": results,
            "summary": {
                "total_force_kN": round(total_force_kN, 1),
                "base_moment_kNm": round(base_moment_kNm, 1),
                "max_vk": round(results[-1]['vk'], 2),
                "max_q_Pa": round(results[-1]['q_Pa'], 1),
                "cf_used": cf
            }
        }
