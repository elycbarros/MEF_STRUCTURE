"""
verify_piled_raft.py - Script de validação para o novo módulo de Radier Estaqueado.
"""

import os
import sys

# Garantir imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from piles_engine import Pile, PilesEngine
from radier_lab_v24 import LabConfig, run_deterministic_fem
from radier_utils import read_json


def test_piled_raft_validation():
    print('=== TESTANDO RADIER ESTAQUEADO (PILED RAFT) ===')

    # Configuração de estacas
    # Estaca de 60cm de diâmetro, 15m de comprimento
    k_theoretical = PilesEngine.calculate_theoretical_stiffness(diameter=0.60, length=15.0, E_concrete_GPa=30.0)
    print(f'Rigidez Teórica Calculada: {k_theoretical:.2f} kN/m')

    piles = [
        Pile(
            id='EST01', x=5.0, y=5.0, diameter_m=0.60, length_m=15.0, capacity_kN=1500.0, stiffness_kN_m=k_theoretical
        ),
        Pile(
            id='EST02', x=15.0, y=5.0, diameter_m=0.60, length_m=15.0, capacity_kN=1500.0, stiffness_kN_m=k_theoretical
        ),
        Pile(
            id='EST03', x=5.0, y=15.0, diameter_m=0.60, length_m=15.0, capacity_kN=1500.0, stiffness_kN_m=k_theoretical
        ),
        Pile(
            id='EST04', x=15.0, y=15.0, diameter_m=0.60, length_m=15.0, capacity_kN=1500.0, stiffness_kN_m=k_theoretical
        ),
    ]

    cfg = LabConfig(
        base_name='valida_estacas',
        Lx=20.0,
        Ly=20.0,
        nx=21,
        ny=21,
        h=0.60,
        kv=10e6,  # Solo mole para destacar o efeito das estacas
        q=50e3,  # 50 kPa
        piles=piles,
    )

    # Executar análise
    json_path = run_deterministic_fem(cfg)
    results = read_json(json_path)

    print('\nResultados da Simulação:')
    print(f'Recalque Máximo: {results["w_max_mm"]:.2f} mm')
    print(f'Pressão Máxima no Solo: {results["qsoil_max_kPa"]:.2f} kPa')
    print(f'Reação Total nas Estacas: {results["pile_reactions_total_kN"]:.2f} kN')

    # Verificação de Alívio no Solo
    # Sem estacas, a pressão seria q + pp = 50 + (0.6 * 25) = 65 kPa uniforme
    # Com estacas, deve ser menor que 65 kPa nas regiões das estacas
    if results['pile_reactions_total_kN'] > 0:
        print('\n[OK] As estacas estão absorvendo carga!')
    else:
        print('\n[ERRO] Reação nas estacas zerada.')


if __name__ == '__main__':
    test_piled_raft_validation()
