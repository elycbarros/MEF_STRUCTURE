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

class WindEngine:
    """Motor de analise de vento e estabilidade global."""

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
        """
        Estimativa simplificada do coeficiente gamma_z.
        gamma_z = 1 / (1 - M2 / M1)
        Aqui usaremos a regra pratica: se delta_h / H < limite, gamma_z e baixo.
        """
        # Valor dummy para fins pedagogicos (Mestre)
        if total_height > 40: return 1.12
        if total_height > 20: return 1.07
        return 1.03
