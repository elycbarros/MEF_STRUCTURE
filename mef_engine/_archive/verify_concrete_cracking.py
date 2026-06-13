"""
verify_concrete_cracking.py - Validação da Não-Linearidade Física do Concreto.
Compara a rigidez bruta vs rigidez trincada.
"""

from pathlib import Path

from radier_lab_v24 import LabConfig, run_deterministic_fem
from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil


def test_cracking_effect():
    print('=== TESTANDO NÃO-LINEARIDADE FÍSICA (CONCRETO TRINCADO) ===')

    # 1. Configuração de carga pesada para forçar fissuração
    csv_path = Path('output/test_heavy_columns.csv')
    csv_path.parent.mkdir(exist_ok=True)
    # 4 colunas pesadas no centro (125000 kN cada - ABSURDO TOTAL para forçar trinca em 20cm)
    with open(csv_path, 'w') as f:
        f.write('id,x,y,p,mx,my,bx,by\n')
        f.write('P1,10,10,125000,0,0,0.5,0.5\n')
        f.write('P2,14,10,125000,0,0,0.5,0.5\n')
        f.write('P3,10,14,125000,0,0,0.5,0.5\n')
        f.write('P4,14,14,125000,0,0,0.5,0.5\n')

    cfg = LabConfig(
        base_name='test_cracking',
        h=0.20,  # Ultra esbelto para trincar com certeza
        nx=15,
        ny=15,
        columns_csv=str(csv_path),
        concrete_nonlinear=False,  # Primeiro Linear
    )

    print('\n[1] Rodando Análise Linear (Inércia Bruta)...')
    res_linear_path = run_deterministic_fem(cfg)

    # Pegamos os resultados diretamente para comparar
    from radier_solver_v2 import read_column_loads_csv

    solver = RadierMindlinWinklerV2(
        PlateModel(Lx=24, Ly=24, nx=15, ny=15, material=Material(E=32e9, nu=0.2, h=0.2), soil=Soil(kv=40e6))
    )
    loads = read_column_loads_csv(csv_path)

    res_linear = solver.solve(loads, concrete_nonlinear=False)
    print(f'Deslocamento Max Linear: {res_linear.disp[:, 0].max() * 1000:.2f} mm')
    print(f'Momento Max Linear: {res_linear.mx.max() / 1000:.2f} kNm/m')

    print('\n[2] Rodando Análise Não-Linear (Branson - Trincado)...')
    res_nonlinear = solver.solve(loads, concrete_nonlinear=True, max_iter=10)
    print(f'Deslocamento Max Não-Linear: {res_nonlinear.disp[:, 0].max() * 1000:.2f} mm')
    print(f'Momento Max Não-Linear: {res_nonlinear.mx.max() / 1000:.2f} kNm/m')

    delta_w = (res_nonlinear.disp[:, 0].max() / res_linear.disp[:, 0].max() - 1) * 100
    print(f'\nAumento no recalque devido à fissuração: {delta_w:.1f}%')

    if delta_w > 5:
        print('✅ SUCESSO: A redistribuição de rigidez foi detectada.')
    else:
        print('❌ FALHA: A rigidez não mudou significativamente.')


if __name__ == '__main__':
    test_cracking_effect()
