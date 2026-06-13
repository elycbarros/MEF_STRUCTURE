"""
test_radier_rs_benchmark.py - Comparação de desempenho entre
montagem Python vs Rust da matriz de rigidez do radier.
"""

import time

import numpy as np


def _make_model_params(nx=13, ny=13):
    """Cria parâmetros de malha para um radier 24x24m."""
    Lx, Ly = 24.0, 24.0
    xs = np.linspace(0, Lx, nx)
    ys = np.linspace(0, Ly, ny)
    Xg, Yg = np.meshgrid(xs, ys)
    nodes = np.column_stack([Xg.ravel(), Yg.ravel()])
    elements = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            n0 = j * nx + i
            elements.append([n0, n0 + 1, n0 + nx + 1, n0 + nx])
    elements = np.array(elements, dtype=int)
    dx, dy = Lx / (nx - 1), Ly / (ny - 1)
    wx = np.ones(nx)
    wy = np.ones(ny)
    wx[[0, -1]] = 0.5
    wy[[0, -1]] = 0.5
    tributary_areas = (np.outer(wy, wx) * dx * dy).ravel()
    return nodes, elements, tributary_areas, xs, ys


def test_rust_assembly_matches_python():
    """Compara resultado da montagem Rust vs Python para um caso simples."""
    from radier_rs_adapter import PlateModel as RSPlateModel
    from radier_rs_adapter import RadierMindlinWinklerRS
    from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

    # Malha 5x5 (25 nós, 16 elementos)
    py_model = PlateModel(
        Lx=4.0, Ly=4.0, nx=5, ny=5, material=Material(E=32e9, nu=0.2, h=0.5), soil=Soil(kv=40e6, tensionless=False)
    )

    rs_model = RSPlateModel(
        Lx=4.0, Ly=4.0, nx=5, ny=5, material=Material(E=32e9, nu=0.2, h=0.5), soil=Soil(kv=40e6, tensionless=False)
    )

    col_loads = np.array([[2.0, 2.0, 500e3, 0, 0]], dtype=float)

    py_solver = RadierMindlinWinklerV2(py_model)
    py_solver._q_uniform = 30000.0
    py_result = py_solver.solve(column_loads=col_loads, max_iter=1)

    rs_solver = RadierMindlinWinklerRS(rs_model)
    rs_solver._q_uniform = 30000.0
    rs_result = rs_solver.solve(column_loads=col_loads, max_iter=1)

    # Comparar deslocamentos
    w_py = py_result.disp[:, 0]
    w_rs = rs_result.disp[:, 0]
    max_diff = np.max(np.abs(w_py - w_rs))
    relative_diff = max_diff / max(np.max(np.abs(w_py)), 1e-9)
    # Diferença esperada: Rust usa integração seletiva reduzida (1pt shear) →
    # mais flexível e mais preciso que a integração completa 2x2 do Python.
    print(f'Rust vs Python: max|w_py - w_rs| = {max_diff:.2e} (relative: {relative_diff:.2%})')
    assert relative_diff < 0.10, f'Relative error too large: {relative_diff:.2%}'


def test_rust_assembly_speed():
    """Benchmark: compara tempo de montagem Python vs Rust em malha 13x13."""
    from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

    py_model = PlateModel(
        Lx=24.0, Ly=24.0, nx=13, ny=13, material=Material(E=32e9, nu=0.2, h=0.6), soil=Soil(kv=40e6, tensionless=False)
    )

    col_loads = np.array(
        [
            [4, 4, 2000e3],
            [12, 4, 2500e3],
            [20, 4, 2000e3],
            [4, 12, 2500e3],
            [12, 12, 3000e3],
            [20, 12, 2500e3],
            [4, 20, 2000e3],
            [12, 20, 2500e3],
            [20, 20, 2000e3],
        ],
        dtype=float,
    )

    # Medir Python
    py_solver = RadierMindlinWinklerV2(py_model)
    py_solver._q_uniform = 30000.0
    times_py = []
    for _ in range(3):
        t0 = time.perf_counter()
        _ = py_solver.solve(column_loads=col_loads, max_iter=1)
        times_py.append(time.perf_counter() - t0)
    t_py = np.median(times_py)

    # Medir Rust
    from radier_rs_adapter import PlateModel as RSPlateModel
    from radier_rs_adapter import RadierMindlinWinklerRS

    rs_model = RSPlateModel(
        Lx=24.0, Ly=24.0, nx=13, ny=13, material=Material(E=32e9, nu=0.2, h=0.6), soil=Soil(kv=40e6, tensionless=False)
    )
    rs_solver = RadierMindlinWinklerRS(rs_model)
    rs_solver._q_uniform = 30000.0
    times_rs = []
    for _ in range(3):
        t0 = time.perf_counter()
        _ = rs_solver.solve(column_loads=col_loads, max_iter=1)
        times_rs.append(time.perf_counter() - t0)
    t_rs = np.median(times_rs)

    speedup = t_py / t_rs
    print('\n=== BENCHMARK (malha 13x13, 1 iteração) ===')
    print(f'Python: {t_py * 1000:.1f} ms')
    print(f'Rust:   {t_rs * 1000:.1f} ms')
    print(f'Speedup: {speedup:.1f}x')

    # Verificar que os resultados coincidem
    py_solver._q_uniform = 30000.0
    rs_solver._q_uniform = 30000.0
    py_res = py_solver.solve(column_loads=col_loads, max_iter=10)
    rs_res = rs_solver.solve(column_loads=col_loads, max_iter=10)
    max_err = np.max(np.abs(py_res.disp[:, 0] - rs_res.disp[:, 0]))
    relative_err = max_err / max(np.max(np.abs(py_res.disp[:, 0])), 1e-9)
    print(f'Max displacement error (10 iter): {max_err:.2e} (relative: {relative_err:.2%})')
    assert relative_err < 1e-10, f'Converged results differ too much: {relative_err:.2%}'
    print('✅ Results match at machine precision (same integration scheme)')


if __name__ == '__main__':
    test_rust_assembly_matches_python()
    test_rust_assembly_speed()
