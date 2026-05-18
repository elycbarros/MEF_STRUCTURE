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
    def calculate_seismic_forces(height: float, total_p_kN: float, ag_m_s2: float = 0.5, importance: float = 1.0) -> Dict:
        """
        Análise Sísmica Simplificada (NBR 15421 - Método das Forças Equivalentes).
        ag: Aceleração característica do solo (m/s2)
        """
        # Coeficiente sísmico de resposta (Cs)
        # Cs = (ag/g * I) / R
        # Assumindo R=3.0 (Estrutura de concreto usual)
        g = 9.81
        r_factor = 3.0
        cs = (ag_m_s2 / g * importance) / r_factor
        
        v_base_kN = cs * total_p_kN
        
        # Distribuição triangular de forças nos pavimentos
        return {
            "v_base_kN": round(v_base_kN, 2),
            "cs": round(cs, 4),
            "status": "CALCULO_EQUIVALENTE_CONCLUIDO",
            "norm": "NBR 15421:2006"
        }

    @staticmethod
    def calculate_advanced_stability(total_p_kN: float, height: float, 
                                   m1_kNm: float, wind_v0: float, 
                                   f1_hz: float, total_h_force_kN: float = 0.0,
                                   width_x: float = 20.0, total_mass_kg: float = 0.0) -> StabilityResult:
        """
        Análise de EXCELÊNCIA com P-Delta Iterativo e Dinâmica Davenport.
        """
        delta_lim = height / 400.0
        stiffness_EI = (total_h_force_kN * (height**3)) / (3 * delta_lim) if total_h_force_kN > 0 else 1e9
        
        p_delta_res = StabilityEngine.run_iterative_p_delta(
            total_p_kN, height, total_h_force_kN, stiffness_EI
        )
        
        m1 = m1_kNm if m1_kNm > 0 else 1.0
        delta_m = total_p_kN * delta_lim
        gamma_ratio = delta_m / m1
        gamma_z = float("inf") if gamma_ratio >= 1.0 else 1.0 / (1.0 - gamma_ratio)
        
        # Conforto Dinâmico (NBR 6123 Anexo I / Davenport)
        from wind_engine import WindEngine
        w_engine = WindEngine()
        
        if total_mass_kg > 0:
            acc = w_engine.calculate_top_acceleration(height, width_x, total_mass_kg, f1_hz, wind_v0)
        else:
            # Fallback simplificado
            v_serv = 0.7 * wind_v0
            acc = (0.001 * (v_serv**2) * height) / (max(0.1, f1_hz) * 100)
            
        comfort = "OK"
        if acc > 0.1: comfort = "DESCONFORTO_LEVE"
        if acc > 0.15: comfort = "CRITICO"
        
        return StabilityResult(
            gamma_z=gamma_z,
            is_stable=gamma_ratio < 1.0 and not p_delta_res['is_divergent'] and p_delta_res['p_delta_factor'] < 1.3,
            requires_second_order=gamma_ratio >= 1.0 or p_delta_res['p_delta_factor'] > 1.1,
            p_delta_factor=p_delta_res['p_delta_factor'],
            peak_acceleration_ms2=acc,
            comfort_status=comfort,
            p_delta_iterations=p_delta_res['iterations'],
            is_divergent=gamma_ratio >= 1.0 or p_delta_res['is_divergent']
        )

    @staticmethod
    def calculate_ufo_stability(nodes: list, members: list, loads: list, supports: dict, wind_v0: float = 30.0) -> dict:
        """
        Executa Auditoria UFO (Elite Tier) usando o motor de pórtico 3D.
        Calcula Gama-Z e Alfa reais via P-Delta com redução de rigidez NBR 6118.
        """
        from frame_engine import Frame3DEngine
        engine = Frame3DEngine(nodes, members)
        indices = engine.calculate_stability_indices(loads, supports)
        
        # Auditoria de Conforto (Vibrações)
        try:
            modal = engine.modal_analysis(num_modes=1, supports=supports)
            f1 = modal['modes'][0]['frequency_hz']
            height = max(n.z for n in nodes)
            # Aceleração simplificada (NBR 6123 - Vento)
            v_serv = 0.7 * wind_v0
            acc = (0.001 * (v_serv**2) * height) / (f1 * 100) # m/s2
            comfort = "OK"
            if acc > 0.1: comfort = "DESCONFORTO_LEVE"
            if acc > 0.15: comfort = "CRITICO"
        except Exception as e:
            print(f"Modal fail in UFO: {str(e)}")
            f1 = 0.0
            acc = 0.0
            comfort = "ANALISE_INDISPONIVEL"
        
        return {
            'gamma_z': indices['gamma_z'],
            'alpha': indices['alpha'],
            'is_stable': indices['gamma_z'] < 1.3,
            'p_delta_iterations': indices['p_delta_iterations'],
            'f1_hz': round(f1, 3),
            'peak_acceleration_ms2': round(acc, 4),
            'comfort_status': comfort,
            'recommendation': indices['recommendation'],
            'standard': "NBR 6118:2023 §15 / NBR 6123"
        }

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
