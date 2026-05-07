import numpy as np
from typing import List, Dict, Optional, Any
import math

class PYCurve:
    """
    Modelagem de curvas p-y para interação lateral solo-estaca.
    """
    def __init__(self, soil_type: str, diameter_m: float, gamma_kN_m3: float = 18.0, 
                 phi_deg: float = 30.0, cu_kPa: float = 50.0, epsilon_50: float = 0.01):
        self.soil_type = soil_type # 'sand' ou 'clay'
        self.D = diameter_m
        self.gamma = gamma_kN_m3
        self.phi = phi_deg
        self.cu = cu_kPa
        self.e50 = epsilon_50

    def get_resistance(self, y_m: float, depth_m: float) -> float:
        """
        Retorna a resistência lateral p (kN/m) para um deslocamento y (m).
        """
        y = abs(y_m)
        if y < 1e-9: return 0.0
        
        if self.soil_type == 'clay':
            # Modelo de Matlock (Soft Clay)
            # p/pu = 0.5 * (y/yc)^0.33
            yc = 2.5 * self.e50 * self.D
            # pu (Resistência última)
            pu_1 = (3 + self.gamma*depth_m/self.cu + 0.5*depth_m/self.D) * self.cu * self.D
            pu_2 = 9 * self.cu * self.D
            pu = min(pu_1, pu_2)
            
            if y < 8 * yc:
                p = 0.5 * pu * (y/yc)**(0.333)
            else:
                p = pu
        else:
            # Modelo de Reese (Sand) - Simplificado
            # p = A * pu * tanh( (k*z / (A*pu)) * y )
            k = 20000 # kN/m3 (Aproximação para areia média)
            alpha = self.phi / 2.0
            pu = self.gamma * depth_m * self.D * (math.tan(math.radians(45+alpha))**2) # Rankine
            p = pu * math.tanh((k * depth_m * y) / (pu + 1e-6))
            
        return p if y_m >= 0 else -p

class NonLinearPileSolver:
    def __init__(self, frame_engine):
        self.engine = frame_engine

    def solve_with_py(self, loads, supports, py_curves: Dict[int, PYCurve], 
                      max_iter: int = 15, tol: float = 0.01) -> Dict[str, Any]:
        """
        Resolve o pórtico iterativamente atualizando as molas laterais via p-y.
        """
        # Inicialização: molas lineares baseadas em um y pequeno (1mm)
        current_ks = {}
        for nid, curve in py_curves.items():
            # [Kx, Ky, Kz, Kmx, Kmy, Kmz]
            # Vamos focar em Kx e Ky (laterais)
            p_initial = curve.get_resistance(0.001, depth_m=self.engine.nodes[self.engine.node_map[nid]].z)
            k_val = abs(p_initial / 0.001)
            current_ks[nid] = [k_val, k_val, 1e9, 0, 0, 0] # Z rígido por enquanto
            
        for it in range(max_iter):
            # 1. Resolver Frame
            res = self.engine.solve(loads, supports, elastic_supports=current_ks)
            
            # 2. Atualizar molas
            max_error = 0.0
            new_ks = {}
            for nid, curve in py_curves.items():
                disp = res["displacements"][nid]
                y_mag = math.sqrt(disp[0]**2 + disp[1]**2)
                y_mag = max(y_mag, 1e-6) # Evitar div zero
                
                depth = abs(self.engine.nodes[self.engine.node_map[nid]].z)
                p_new = curve.get_resistance(y_mag, depth)
                k_new = abs(p_new / y_mag)
                
                # Garantir rigidez mínima para evitar matriz singular
                k_new = max(k_new, 1e1) 
                
                # Suavização (Damping)
                k_updated = 0.7 * current_ks[nid][0] + 0.3 * k_new
                
                # Erro relativo
                error = abs(k_updated - current_ks[nid][0]) / (current_ks[nid][0] + 1e-6)
                max_error = max(max_error, error)
                
                new_ks[nid] = [k_updated, k_updated, 1e9, 0, 0, 0]
                
            current_ks = new_ks
            if max_error < tol:
                break
                
        return {
            "res": res,
            "iterations": it + 1,
            "converged": max_error < tol,
            "final_springs": current_ks
        }
