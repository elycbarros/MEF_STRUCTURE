"""
ssi_advanced.py - Motor de Interação Solo-Estrutura Avançado.
Implementa a rigidez equivalente da superestrutura para edifícios altos.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class SuperstructureParams:
    n_floors: int = 40
    floor_height: float = 3.0
    concrete_E: float = 30e9
    # Dimensões médias dos pilares (para estimativa axial)
    col_width: float = 0.60
    col_depth: float = 0.60

class AdvancedSSIEngine:
    @staticmethod
    def calculate_column_stiffness(params: SuperstructureParams) -> float:
        """
        Calcula a rigidez axial equivalente de um pilar que sobe N andares.
        k = E * A / L_total
        """
        A = params.col_width * params.col_depth
        L = params.n_floors * params.floor_height
        k_axial = (params.concrete_E * A) / L
        return k_axial

    @staticmethod
    def calculate_rotational_stiffness(params: SuperstructureParams) -> float:
        """
        Estima a rigidez à rotação (k_theta) baseada no efeito pórtico.
        """
        # Assumindo uma viga de 60cm de altura e vão de 6m no primeiro pavimento
        h_beam = 0.60
        b_beam = 0.30
        L_beam = 6.0
        I = (b_beam * h_beam**3) / 12.0
        k_theta_base = (4 * params.concrete_E * I) / L_beam
        # O efeito de travamento em um edifício alto é acumulativo
        return k_theta_base * 5.0

def apply_superstructure_stiffness(K: np.ndarray, column_nodes: list[int], params: SuperstructureParams):
    """
    Injeta a rigidez da superestrutura na matriz global do radier.
    K: Matriz de rigidez global (ndof, ndof)
    column_nodes: Lista de índices dos nós onde existem pilares.
    """
    k_axial = AdvancedSSIEngine.calculate_column_stiffness(params)
    k_rot = AdvancedSSIEngine.calculate_rotational_stiffness(params)

    for node in column_nodes:
        # Rigidez axial (representa o pilar subindo os andares)
        K[3*node, 3*node] += abs(k_axial)
        
        # Rigidez rotacional (efeito pórtico que trava o radier)
        K[3*node + 1, 3*node + 1] += abs(k_rot)
        K[3*node + 2, 3*node + 2] += abs(k_rot)

    return K
