import numpy as np
from lajes_solver import LajeModel, LajesMindlinSolver, PillarSupport


def test_laje():
    print('Testando solver de Lajes...')
    pillars = [
        PillarSupport('P1', 4.0, 4.0),
        PillarSupport('P2', 20.0, 4.0),
        PillarSupport('P3', 4.0, 20.0),
        PillarSupport('P4', 20.0, 20.0),
    ]
    model = LajeModel(
        Lx=24.0,
        Ly=24.0,
        nx=13,
        ny=13,
        pillars=pillars,
        q_pp=6000.0,  # 6 kN/m2
        q_perm=2000.0,  # 2 kN/m2
        q_acid=3000.0,  # 3 kN/m2
    )

    solver = LajesMindlinSolver(model)
    res = solver.solve(combo_multiplier_pp=1.4, combo_multiplier_perm=1.4, combo_multiplier_acid=1.4)

    print(f'Total Load: {res.distributed_load_total:.1f} N')
    print(f'Total Reactions: {res.reactions_total:.1f} N')
    print(f'Residual: {res.residual:.1f} N')

    w_max = np.max(np.abs(res.disp[:, 0]))
    print(f'Max displacement: {w_max * 1000:.2f} mm')

    mx_max = np.max(res.mx)
    print(f'Max Mx: {mx_max:.1f} Nm/m')


if __name__ == '__main__':
    test_laje()
