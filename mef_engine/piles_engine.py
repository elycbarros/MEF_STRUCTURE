"""
piles_engine.py - Módulo de cálculo de estacas e rigidez para Radier Estaqueado.
"""
from dataclasses import dataclass
import math
from typing import List, Optional

@dataclass
class Pile:
    id: str
    x: float
    y: float
    diameter_m: float
    length_m: float
    capacity_kN: float
    stiffness_kN_m: Optional[float] = None # Se None, será calculado

class PilesEngine:
    @staticmethod
    def calculate_theoretical_stiffness(diameter: float, length: float, E_concrete_GPa: float = 30.0) -> float:
        """
        Estima a rigidez axial de uma estaca baseada na deformação elástica do fuste.
        K = E * A / L (Simplificado, sem considerar a deformação do solo ao redor)
        Para maior precisão, o usuário pode informar a rigidez real de ensaios de prova de carga.
        """
        area = (math.pi * diameter**2) / 4.0
        E_pa = E_concrete_GPa * 1e9
        # Fator de ajuste para interação com solo (fator de mola equivalente)
        # Em fundações, costuma-se usar uma fração da rigidez teórica ou valores de prova de carga.
        k_axial = (E_pa * area) / length
        return k_axial / 1000.0 # kN/m

    @staticmethod
    def verify_pile_group(piles: List[Pile], reactions_kN: List[float]) -> List[dict]:
        """
        Verifica se as reações nas estacas superam a capacidade admissível.
        """
        results = []
        for i, pile in enumerate(piles):
            reaction = reactions_kN[i]
            utilization = (reaction / pile.capacity_kN) * 100
            results.append({
                "id": pile.id,
                "reaction_kN": round(reaction, 2),
                "capacity_kN": pile.capacity_kN,
                "utilization_pct": round(utilization, 2),
                "status": "OK" if utilization <= 100 else "OVERLOAD"
            })
        return results
