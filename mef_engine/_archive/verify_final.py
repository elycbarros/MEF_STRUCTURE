import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from durability_checker import DurabilityChecker, DurabilityConfig
from special_elements import SpecialElementsSolver
from stability_engine import StabilityEngine


def run_final_tests():
    print('=== INICIANDO TESTES FINAIS DOS NOVOS MÓDULOS ===')

    # 1. Teste de Estabilidade
    print('\n[TESTE 1] Estabilidade Global (Gama-Z)')
    res_stab = StabilityEngine.calculate_gamma_z(15000, 45, 12000, 800)
    print(f'   -> Gama-Z: {res_stab.gamma_z:.3f} (Estável: {res_stab.is_stable})')

    # 2. Teste de Durabilidade
    print('\n[TESTE 2] Durabilidade e Conformidade')
    cfg = DurabilityConfig(caa=4)  # Ambiente muito agressivo
    checker = DurabilityChecker()
    cover = checker.get_min_cover(cfg, 'slab')
    fire_ok = checker.check_fire_resistance(15, cfg)
    print(f'   -> Recobrimento mínimo (Laje CAA IV): {cover} mm')
    print(f'   -> Viga de 15cm atende TRRF 60min? {fire_ok}')

    # 3. Teste de Elementos Especiais
    print('\n[TESTE 3] Elementos Especiais')
    solver = SpecialElementsSolver()
    res_stair = solver.solve_stair(3.5, 2.8, 4.0, 12, 25)
    print(f'   -> Escada (As necessário): {res_stair.required_as:.2f} cm2/m')
    print(f'   -> Espessura de 12cm ok? {res_stair.thickness_ok}')

    print('\n✅ Todos os módulos operacionais!')


if __name__ == '__main__':
    run_final_tests()
