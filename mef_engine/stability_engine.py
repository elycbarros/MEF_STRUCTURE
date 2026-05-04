"""
stability_engine.py - Análise de Estabilidade Global (Gama-Z) conforme NBR 6118.
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class StabilityResult:
    gamma_z: float
    is_stable: bool
    requires_second_order: bool
    p_delta_factor: float # Fator de amplificação de esforços
    peak_acceleration_ms2: float # Aceleração no topo (Conforto)
    comfort_status: str # 'OK' ou 'Critico'
    p_delta_iterations: int # Número de iterações para convergência
    is_divergent: bool # Indica se a estrutura é instável (não converge)

class StabilityEngine:
    @staticmethod
    def apply_physical_non_linearity(stiffness: float, member_type: str) -> float:
        """
        Reduz a inércia das peças conforme NBR 6118 (item 15.7.3).
        Vigas: 0.4 EI | Pilares: 0.8 EI
        """
        factor = 0.4 if member_type == 'beam' else 0.8
        return stiffness * factor

    @staticmethod
    def run_iterative_p_delta(total_p_kN: float, height: float, 
                              wind_force_kN: float, stiffness_EI: float, 
                              max_iter: int = 20, tol: float = 1e-4) -> dict:
        """
        Solver Iterativo de 2a Ordem (P-Delta Real).
        Modela o edifício como um cantilever equivalente.
        """
        # Deslocamento inicial (1a Ordem)
        # delta = F * H^3 / (3 * EI)
        delta = (wind_force_kN * (height**3)) / (3 * stiffness_EI)
        
        current_delta = delta
        prev_delta = 0.0
        iterations = 0
        is_divergent = False
        
        while abs(current_delta - prev_delta) > tol:
            iterations += 1
            if iterations > max_iter:
                is_divergent = True
                break
            
            prev_delta = current_delta
            # Momento adicional de 2a ordem: M2 = P * delta
            # Novo deslocamento: delta_total = (F_wind + P * delta / height) * height^3 / (3 * EI)
            # Simplificação: delta_n+1 = delta_1 + (P * delta_n * H^2 / (2 * EI)) 
            # (P-Delta local e global simplificado)
            m_p_delta = total_p_kN * prev_delta
            current_delta = delta + (m_p_delta * (height**2)) / (2 * stiffness_EI)
            
            if current_delta > height / 10: # Critério de divergência física
                is_divergent = True
                break
        
        p_delta_factor = current_delta / delta if delta > 0 else 1.0
        return {
            'delta_1': delta,
            'delta_final': current_delta,
            'p_delta_factor': p_delta_factor,
            'iterations': iterations,
            'is_divergent': is_divergent
        }

    @staticmethod
    def calculate_advanced_stability(total_p_kN: float, height: float, 
                                   m1_kNm: float, wind_v0: float, 
                                   f1_hz: float, total_h_force_kN: float = 0.0) -> StabilityResult:
        """
        Análise de EXCELÊNCIA com P-Delta Iterativo para até 40 pavimentos.
        """
        # Inércia equivalente estimada do edifício (EI) baseada no M1 e H
        # Se m1 = F * H, e delta = F * H^3 / 3EI -> EI = F * H^3 / (3 * delta)
        # Usando delta_lim = H/400 como base de rigidez de 1a ordem
        delta_lim = height / 400.0
        stiffness_EI = (total_h_force_kN * (height**3)) / (3 * delta_lim) if total_h_force_kN > 0 else 1e9
        
        # Executar Solver Iterativo
        p_delta_res = StabilityEngine.run_iterative_p_delta(
            total_p_kN, height, total_h_force_kN, stiffness_EI
        )
        
        # Gama-Z Clássico para referência
        m1 = m1_kNm if m1_kNm > 0 else 1.0
        delta_m = total_p_kN * delta_lim
        gamma_z = 1.0 / (1.0 - (delta_m / m1))
        
        # Conforto
        v_serv = 0.7 * wind_v0
        acc = (0.001 * (v_serv**2) * height) / (f1_hz * 100)
        comfort = "OK"
        if acc > 0.1: comfort = "DESCONFORTO_LEVE"
        if acc > 0.15: comfort = "CRITICO"
        
        return StabilityResult(
            gamma_z=gamma_z,
            is_stable=not p_delta_res['is_divergent'] and p_delta_res['p_delta_factor'] < 1.3,
            requires_second_order=p_delta_res['p_delta_factor'] > 1.1,
            p_delta_factor=p_delta_res['p_delta_factor'],
            peak_acceleration_ms2=acc,
            comfort_status=comfort,
            p_delta_iterations=p_delta_res['iterations'],
            is_divergent=p_delta_res['is_divergent']
        )

if __name__ == "__main__":
    # Exemplo: Prédio de 10 andares (30m)
    res = StabilityEngine.calculate_gamma_z(
        total_vertical_load_kN=10000, # 1000t
        height=30.0,
        total_wind_moment_kNm=8000,
        total_wind_force_kN=500
    )
    print(f"Gama-Z: {res.gamma_z:.3f}")
    print(f"Estável? {res.is_stable}")
    print(f"Exige 2ª Ordem? {res.requires_second_order}")
