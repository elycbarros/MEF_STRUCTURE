import structural_core_rs


def test_full_solver():
    print('Testando Solver Completo (Rust - MEF)...')

    # Viga de 5m engastada em ambas as extremidades
    # Para carga no meio, usamos 2 elementos de 2.5m
    # E = 25 GPa = 25,000,000 kN/m²
    # I = 200,000 cm⁴ = 0.002 m⁴
    # EI = 50,000 kNm²

    solver = structural_core_rs.BeamSolver(2)
    solver.add_span_stiffness(0, 1, 2.5, 25000000.0, 0.002)
    solver.add_span_stiffness(1, 2, 2.5, 25000000.0, 0.002)

    # Carga de 100 kN no nó central (nó 1)
    solver.add_point_load(1, 100.0)

    # Condições de Contorno: Engaste nos nós 0 e 2
    # DOFs: Nó 0 (0,1), Nó 1 (2,3), Nó 2 (4,5)
    # DOF par: Deslocamento Vertical (Y)
    # DOF ímpar: Rotação (Z)
    fixed_dofs = [0, 1, 4, 5]

    displacements = solver.solve(fixed_dofs)

    # O deslocamento vertical no meio é o DOF 2
    actual_m = displacements[2]
    actual_mm = actual_m * 1000

    # Teoria: delta = (P * L³) / (192 * EI)
    # delta = (100 * 5³) / (192 * 50000) = 0.001302083 m
    expected_mm = -(100 * 5**3) / (192 * 50000) * 1000

    print('Resultados obtidos via Rust Core:')
    print(f'  -> Deslocamento central: {actual_mm:.6f} mm')
    print(f'  -> Valor teórico (Euler): {expected_mm:.6f} mm')

    if abs(actual_mm - expected_mm) < 0.0001:
        print('\n✅ PRECISÃO DE ELITE: O solver Rust atingiu o valor teórico exato!')
    else:
        print(f'\n⚠️ Divergência: {abs(actual_mm - expected_mm):.6f} mm')

    # Teste TensionPro
    print('\nTestando Módulo TensionPro (Protensão)...')
    tension = structural_core_rs.TensionPro(30.0)  # fck 30 MPa
    # P(x) = P0 * e^(-mu * (theta + k*x))
    p_x = tension.calculate_friction_loss(1000.0, 0.20, 0.01, 10.0, 0.1)
    print(f'  -> Força de protensão aos 10m: {p_x:.2f} kN (P0=1000kN)')


if __name__ == '__main__':
    test_full_solver()
