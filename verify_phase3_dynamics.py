import sys
import os

# Adicionar o path para importar os motores
sys.path.append(os.path.join(os.getcwd(), 'mef_engine'))

from stability_engine import StabilityEngine

def test_high_rise_dynamics():
    print("--- Teste de Dinâmica de Alta Precisão (Phase 3) ---")
    
    # Simulação de Prédio de 40 andares (120m)
    res = StabilityEngine.calculate_advanced_stability(
        total_p_kN=120000, # 120 MN
        height=120.0,
        m1_kNm=800000,
        wind_v0=35.0,
        f1_hz=0.25, # Prédio flexível
        total_h_force_kN=4500.0,
        width_x=25.0,
        total_mass_kg=12000000 # 12.000 t
    )
    
    print(f"Gama-Z: {res.gamma_z:.3f}")
    print(f"Status Conforto: {res.comfort_status}")
    print(f"Aceleração de Topo: {res.peak_acceleration_ms2:.4f} m/s²")
    print(f"Estabilidade Global: {'OK' if res.is_stable else 'CRÍTICO'}")
    
    # Teste Sísmico
    seismic = StabilityEngine.calculate_seismic_forces(120.0, 120000.0)
    print(f"Cortante de Base Sísmico: {seismic['v_base_kN']} kN")

if __name__ == "__main__":
    test_high_rise_dynamics()
