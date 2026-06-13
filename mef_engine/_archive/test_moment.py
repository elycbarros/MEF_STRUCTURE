from beam_solver import run_beam_analysis


def test_q47_beam():
    print('Testing Beam - Questão 47...')
    res = run_beam_analysis(
        L=8.0,
        supports=[{'x': 0.0, 'type': 'pinned'}, {'x': 6.0, 'type': 'pinned'}],
        distributed_loads=[],
        point_loads=[
            {'x': 8.0, 'P': 30.0}  # 30 kN concentrated load at the tip (x=8.0m)
        ],
        b=0.20,
        h=0.50,
        fck=30,
        nonlinear=False,
        include_self_weight=False,
    )

    print('\n==================================================')
    print('           RESULTADOS DA QUESTÃO 47')
    print('==================================================')

    print('\n--- Resultados do Solver MEF ---')
    print('Flecha Máxima:', f'{res["summary"]["max_deflection_mm"]:.4f} mm')
    print('Momento Máximo:', f'{res["summary"]["max_moment_kNm"]:.2f} kNm')
    print('Cortante Máximo:', f'{res["summary"]["max_shear_kN"]:.2f} kN')

    print('\nReações de Apoio (MEF):')
    for x_pos, data in res['reactions'].items():
        print(f'Apoio em x = {float(x_pos):.1f}m: Reação = {data["R"]:.2f} kN')

    print('\nDiagrama de Esforço Cortante (DEC - MEF):')
    for pt in res['diagrams']['shear'][::5]:  # Mostrar alguns pontos
        print(f'x = {pt["x"]:.2f}m: V = {pt["y"]:.2f} kN')

    print('\nDiagrama de Momento Fletor (DMF - MEF):')
    for pt in res['diagrams']['moment'][::5]:  # Mostrar alguns pontos
        print(f'x = {pt["x"]:.2f}m: M = {pt["y"]:.2f} kNm')

    print('\n--- Resultados Analíticos Clássicos ---')
    classical = res['classical_diagrams']
    print('Momento Fletor Máximo:', f'{classical["max_moment_kNm"]:.2f} kNm')
    print('Esforço Cortante Máximo:', f'{classical["max_shear_kN"]:.2f} kN')
    print('Reações de Apoio (Clássicas):')
    for reac in classical['reactions']:
        print(f'Apoio em x = {reac["x"]:.1f}m: Reação = {reac["R"]:.2f} kN')
    print('==================================================\n')


if __name__ == '__main__':
    test_q47_beam()
