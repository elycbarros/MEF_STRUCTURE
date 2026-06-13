"""
verify_advanced_ssi.py - Validação do Efeito de Travamento da Superestrutura.
"""

from pathlib import Path

from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil, read_column_loads_csv
from ssi_advanced import SuperstructureParams


def test_ssi_stiffening():
    print('=== TESTANDO SSI AVANÇADO (EFEITO DE TRAVAMENTO SUPERIOR) ===')

    csv_path = Path('output/test_ssi_columns.csv')
    csv_path.parent.mkdir(exist_ok=True)
    with open(csv_path, 'w') as f:
        f.write('id,x,y,p,mx,my,bx,by\n')
        f.write('P1,10,10,50000,0,0,0.6,0.6\n')
        f.write('P2,14,10,50000,0,0,0.6,0.6\n')
        f.write('P3,10,14,50000,0,0,0.6,0.6\n')
        f.write('P4,14,14,50000,0,0,0.6,0.6\n')

    solver = RadierMindlinWinklerV2(
        PlateModel(Lx=24, Ly=24, nx=15, ny=15, material=Material(E=32e9, nu=0.2, h=0.7), soil=Soil(kv=40e6))
    )
    loads = read_column_loads_csv(csv_path)

    print('\n[1] Rodando SEM Rigidez da Superestrutura...')
    res_no_ssi = solver.solve(loads)
    m_max_no_ssi = abs(res_no_ssi.mx).max()
    w_max_no_ssi = res_no_ssi.disp[:, 0].max()
    print(f'Momento Max: {m_max_no_ssi / 1000:.2f} kNm/m')
    print(f'Recalque Max: {w_max_no_ssi * 1000:.2f} mm')

    print('\n[2] Rodando COM Rigidez da Superestrutura (40 Andares)...')
    ssi_params = {'params': SuperstructureParams(n_floors=40)}
    res_ssi = solver.solve(loads, superstructure_stiffness=ssi_params)
    m_max_ssi = abs(res_ssi.mx).max()
    w_max_ssi = res_ssi.disp[:, 0].max()
    print(f'Momento Max: {m_max_ssi / 1000:.2f} kNm/m')
    print(f'Recalque Max: {w_max_ssi * 1000:.2f} mm')

    reduction = (1 - m_max_ssi / m_max_no_ssi) * 100
    print(f'\nRedução no momento de pico: {reduction:.1f}%')

    if reduction > 10:
        print('✅ SUCESSO: A superestrutura está ajudando a travar o radier!')
    else:
        print('⚠️ AVISO: Redução baixa. Verifique os parâmetros de rigidez.')


if __name__ == '__main__':
    test_ssi_stiffening()
