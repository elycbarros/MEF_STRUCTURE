import numpy as np
from typing import List, Dict, Optional

class SeismicEngine:
    """
    Engine para Análise Sísmica via Espectro de Resposta (RSA) conforme NBR 15421:2023.
    """

    def __init__(self, soil_class: str = "D", seismic_zone: int = 1):
        self.soil_class = soil_class
        self.seismic_zone = seismic_zone
        
        # Parâmetros NBR 15421 (Simplificados para Classe D e Zona 1)
        # ag: aceleração característica (fração de g)
        # S: fator de solo
        self.ag_map = {0: 0.0, 1: 0.025, 2: 0.05, 3: 0.10, 4: 0.15}
        self.s_map = {"A": 1.0, "B": 1.0, "C": 1.15, "D": 1.35, "E": 1.6}
        
        self.ag = self.ag_map.get(seismic_zone, 0.025)
        self.S = self.s_map.get(soil_class, 1.35)

    def get_spectral_acceleration(self, T: float, R: float = 1.0, I: float = 1.0) -> float:
        """
        Retorna a aceleração espectral Sa(T) em m/s2.
        T: Período (s)
        R: Fator de modificação de resposta (ductilidade)
        I: Fator de importância
        """
        if T <= 0: return 0.0
        
        # Períodos característicos (Simplificado)
        TB = 0.10
        TC = 0.60
        TD = 2.0
        
        # g em m/s2
        g = 9.81
        
        # Ordenada de projeto SaD(T)
        # Esta é uma implementação simplificada do espectro da NBR 15421
        if T < TB:
            Sa = self.ag * self.S * (1 + (T/TB) * (2.5 - 1))
        elif T <= TC:
            Sa = 2.5 * self.ag * self.S
        elif T <= TD:
            Sa = 2.5 * self.ag * self.S * (TC / T)
        else:
            Sa = 2.5 * self.ag * self.S * (TC * TD / T**2)
            
        # Aplicar importância e ductilidade
        return (Sa * I / R) * g

    def run_rsa_analysis(self, frame_engine, supports: Dict, num_modes: int = 10, R: float = 1.0, I: float = 1.0) -> Dict:
        """
        Executa a análise de espectro de resposta completa.
        """
        # 1. Análise Modal
        modal = frame_engine.modal_analysis(num_modes=num_modes, supports=supports)
        if not modal["success"]: return modal
        
        # 2. Obter respostas espectrais
        results = []
        for m in modal["modes"]:
            T = m["period_s"]
            sa = self.get_spectral_acceleration(T, R, I)
            
            # Resposta modal (Simplificada: Cortante na base proporcional à massa participante)
            # V_base_modal = Sa(T) * M_part
            v_modal = sa * m["mass_participation_x"] * modal["total_mass_kg"]
            
            results.append({
                "mode": m["mode"],
                "Sa": sa,
                "base_shear_N": v_modal
            })
            
        # 3. Combinação SRSS
        total_v_base = np.sqrt(sum(r["base_shear_N"]**2 for r in results))
        
        return {
            "success": True,
            "total_base_shear_kN": total_v_base / 1000.0,
            "modal_results": results,
            "total_mass_kg": modal["total_mass_kg"],
            "soil_class": self.soil_class,
            "seismic_zone": self.seismic_zone
        }

if __name__ == "__main__":
    # Teste rápido
    engine = SeismicEngine(soil_class="D", seismic_zone=1)
    for t in [0.1, 0.5, 1.0, 2.0, 3.0]:
        sa = engine.get_spectral_acceleration(t)
        print(f"T={t}s -> Sa={sa:.4f} m/s2")
