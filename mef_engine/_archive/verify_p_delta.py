"""
verify_p_delta.py - Script de validação para o novo Solver P-Delta Iterativo.
"""

from stability_engine import StabilityEngine


def test_p_delta_stability():
    print('=== TESTANDO P-DELTA ITERATIVO (ARRANHA-CÉU) ===')

    # Caso 1: Prédio Rígido (Convergência Rápida)
    # 40 andares (120m), carga axial moderada
    print('\nCenário 1: Prédio de 40 andares estável')
    res1 = StabilityEngine.calculate_advanced_stability(
        total_p_kN=100000.0,  # 10.000 toneladas
        height=120.0,
        m1_kNm=50000.0,
        wind_v0=30.0,
        f1_hz=0.3,
        total_h_force_kN=1000.0,
    )
    print(f'Gama-Z (1a Ordem): {res1.gamma_z:.3f}')
    print(f'P-Delta (Iterativo): {res1.p_delta_factor:.3f}')
    print(f'Iterações: {res1.p_delta_iterations}')
    print(f'Estável? {res1.is_stable}')

    # Caso 2: Prédio Esbelto/Instável (Divergência)
    # Aumentando drasticamente a carga vertical para forçar instabilidade
    print('\nCenário 2: Prédio instável (Excesso de carga vertical)')
    res2 = StabilityEngine.calculate_advanced_stability(
        total_p_kN=500000.0,  # 50.000 toneladas (exagerado para testar)
        height=120.0,
        m1_kNm=50000.0,
        wind_v0=30.0,
        f1_hz=0.3,
        total_h_force_kN=1000.0,
    )
    print(f'P-Delta (Iterativo): {res2.p_delta_factor:.3f}')
    print(f'Divergiu? {res2.is_divergent}')

    if res2.is_divergent:
        print('[OK] Sistema detectou instabilidade global com sucesso.')
    else:
        print('[ERRO] Sistema não detectou a instabilidade esperada.')


if __name__ == '__main__':
    test_p_delta_stability()
