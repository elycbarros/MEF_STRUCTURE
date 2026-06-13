"""
test_property_based.py — Testes baseados em propriedades (Hypothesis)
para verificar invariantes numéricos dos motores MEF.

Propriedades testadas:
  1. Equilíbrio global: ΣR ≈ ΣF (radier, frame, beam)
  2. Monotonicidade: aumentar rigidez reduz deslocamentos
  3. Simetria: estrutura simétrica → resultados simétricos
  4. Superposição linear: caso A + B = caso (A+B) (regime elástico)
  5. Estabilidade: γz decresce com rigidez crescente
  6. Pressão de vento: q > 0 sempre
"""

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# ─────────────────────────────────────────────────────
# Estratégias (strategies) compartilhadas
# ─────────────────────────────────────────────────────

small_floats = st.floats(
    min_value=1e-3,
    max_value=1e3,
    allow_nan=False,
    allow_infinity=False,
)
positive_floats = st.floats(
    min_value=1.0,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)
dimensions = st.floats(
    min_value=0.5,
    max_value=50.0,
    allow_nan=False,
    allow_infinity=False,
)


# ─────────────────────────────────────────────────────
# 1. Equilíbrio global — Radier
# ─────────────────────────────────────────────────────


@given(
    L=dimensions,
    h=st.floats(0.15, 1.5, allow_nan=False, allow_infinity=False),
    kv=st.floats(5e6, 100e6, allow_nan=False, allow_infinity=False),
    q=st.floats(5e3, 200e3, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=15, deadline=None)
def test_radier_global_equilibrium(L, h, kv, q):
    """A soma das reações do solo deve igualar a carga total aplicada."""
    assume(L >= 0.5 and h >= 0.15 and kv >= 1e5 and q >= 1e3)
    try:
        from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

        nx, ny = 7, 7
        model = PlateModel(
            Lx=L,
            Ly=L,
            nx=nx,
            ny=ny,
            material=Material(E=30e9, nu=0.2, h=h),
            soil=Soil(kv=kv, tensionless=False),
        )
        solver = RadierMindlinWinklerV2(model)
        solver._q_uniform = float(q)
        res = solver.solve(max_iter=5)
        total_applied = res.loads_total
        total_reaction = res.reactions_total
        # Tolerância: 5% ou 10kN, o que for maior
        abs_err = abs(total_reaction - total_applied)
        rel_err = abs_err / max(abs(total_applied), 1.0)
        assert rel_err < 0.05 or abs_err < 1e4, (
            f'Equilíbrio violado: aplicado={total_applied:.1f}N, '
            f'reação={total_reaction:.1f}N (erro={abs_err:.1f}N, {rel_err:.2%})'
        )
    except ImportError:
        pytest.skip('radier_solver_v2 não disponível')


# ─────────────────────────────────────────────────────
# 2. Equilíbrio global — Viga
# ─────────────────────────────────────────────────────


@given(
    L=st.floats(2.0, 20.0),
    q=st.floats(5.0, 100.0),
)
@settings(max_examples=20, deadline=None)
def test_beam_global_equilibrium(L, q):
    """Viga biapoiada: V_esq + V_dir = q * L."""
    assume(L >= 2.0 and q >= 1.0)
    try:
        from beam_solver import run_beam_analysis

        res = run_beam_analysis(
            L=L,
            supports=[{'x': 0.0, 'type': 'pinned'}, {'x': L, 'type': 'pinned'}],
            distributed_loads=[{'x_start': 0, 'x_end': L, 'q_start': q}],
            b=0.20,
            h=0.50,
            fck=30,
            nonlinear=False,
            include_self_weight=False,
            gamma_f=1.0,
        )
        reacts = res.get('reactions', {})
        total_shear = sum(float(v['R']) for v in reacts.values())
        expected = q * L
        rel_err = abs(total_shear - expected) / max(expected, 1.0)
        assert rel_err < 0.01, f'Equilíbrio violado: V_total={total_shear:.2f}kN ≠ qL={expected:.2f}kN'
    except ImportError:
        pytest.skip('beam_solver não disponível')


# ─────────────────────────────────────────────────────
# 3. Monotonicidade — aumentar rigidez reduz deslocamentos
# ─────────────────────────────────────────────────────


@given(
    h1=st.floats(0.20, 0.40),
    h2=st.floats(0.50, 1.00),
)
@settings(max_examples=15, deadline=None)
def test_radier_monotonic_stiffness(h1, h2):
    """Aumentar espessura (rigidez) reduz recalque máximo."""
    assume(h1 < h2)
    try:
        from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

        model1 = PlateModel(
            Lx=10.0,
            Ly=10.0,
            nx=7,
            ny=7,
            material=Material(E=30e9, nu=0.2, h=h1),
            soil=Soil(kv=20e6, tensionless=False),
        )
        model2 = PlateModel(
            Lx=10.0,
            Ly=10.0,
            nx=7,
            ny=7,
            material=Material(E=30e9, nu=0.2, h=h2),
            soil=Soil(kv=20e6, tensionless=False),
        )
        s1 = RadierMindlinWinklerV2(model1)
        s1._q_uniform = 50000.0
        s2 = RadierMindlinWinklerV2(model2)
        s2._q_uniform = 50000.0
        r1 = s1.solve(max_iter=5)
        r2 = s2.solve(max_iter=5)
        w_max_1 = float(np.max(np.abs(r1.disp[:, 0])))
        w_max_2 = float(np.max(np.abs(r2.disp[:, 0])))
        assert w_max_2 < w_max_1 * 1.05, (
            f'h={h1:.2f} → w_max={w_max_1 * 1000:.3f}mm, h={h2:.2f} → w_max={w_max_2 * 1000:.3f}mm (esperado redução)'
        )
    except ImportError:
        pytest.skip('radier_solver_v2 não disponível')


# ─────────────────────────────────────────────────────
# 4. Superposição linear (regime elástico, sem tensionless)
# ─────────────────────────────────────────────────────


@given(
    q1=st.floats(20e3, 50e3),
    q2=st.floats(30e3, 80e3),
)
@settings(max_examples=10, deadline=None)
def test_radier_linear_superposition(q1, q2):
    """u(q1+q2) ≈ u(q1) + u(q2) para solo sem descolamento."""
    try:
        from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

        model = PlateModel(
            Lx=6.0,
            Ly=6.0,
            nx=7,
            ny=7,
            material=Material(E=30e9, nu=0.2, h=0.4),
            soil=Soil(kv=40e6, tensionless=False),
        )

        s_sum = RadierMindlinWinklerV2(model)
        s_sum._q_uniform = float(q1 + q2)
        r_sum = s_sum.solve(max_iter=5)

        s1 = RadierMindlinWinklerV2(model)
        s1._q_uniform = float(q1)
        r1 = s1.solve(max_iter=5)

        s2 = RadierMindlinWinklerV2(model)
        s2._q_uniform = float(q2)
        r2 = s2.solve(max_iter=5)

        w_sum = r_sum.disp[:, 0]
        w_separate = r1.disp[:, 0] + r2.disp[:, 0]
        max_diff = float(np.max(np.abs(w_sum - w_separate)))
        relative = max_diff / max(float(np.max(np.abs(w_sum))), 1e-9)
        # Erro por não-linearidade geométrica é pequeno para estas cargas
        assert relative < 0.01, f'Superposição violada: max|diff|={max_diff:.2e}, rel={relative:.2%}'
    except ImportError:
        pytest.skip('radier_solver_v2 não disponível')


# ─────────────────────────────────────────────────────
# 5. Estabilidade — γz decresce com rigidez crescente
# ─────────────────────────────────────────────────────


@given(
    P=st.floats(5000.0, 50000.0),
    H=st.floats(100.0, 1000.0),
)
@settings(max_examples=15, deadline=None)
def test_gamma_z_monotonic(P, H):
    """γz(P1) > γz(P2) se P1 > P2 (mesma estrutura)."""
    try:
        from stability_engine import StabilityEngine

        for P1, P2 in [(P, P * 0.5), (P, P * 0.25)]:
            g1 = StabilityEngine.calculate_advanced_stability(
                total_p_kN=P1,
                height=30.0,
                m1_kNm=5000.0,
                wind_v0=30.0,
                f1_hz=0.5,
                total_h_force_kN=H,
            )
            g2 = StabilityEngine.calculate_advanced_stability(
                total_p_kN=P2,
                height=30.0,
                m1_kNm=5000.0,
                wind_v0=30.0,
                f1_hz=0.5,
                total_h_force_kN=H,
            )
            assert g1.gamma_z > g2.gamma_z or g2.is_divergent, (
                f'γz(P1={P1:.0f})={g1.gamma_z:.4f} <= γz(P2={P2:.0f})={g2.gamma_z:.4f}'
            )
    except ImportError:
        pytest.skip('stability_engine não disponível')


# ─────────────────────────────────────────────────────
# 6. Vento — invariantes físicos
# ─────────────────────────────────────────────────────


@given(
    v0=st.floats(20.0, 50.0),
    altura=st.floats(5.0, 100.0),
)
@settings(max_examples=10, deadline=None)
def test_wind_pressure_positive(v0, altura):
    """Pressão dinâmica q é sempre positiva e cresce com altura."""
    try:
        from wind_engine import WindConfig, WindEngine

        cfg = WindConfig(v0=v0, categoria=2, classe='B', height=altura, width_x=20.0)
        result = WindEngine(cfg).generate_force_profile(
            height=altura,
            width=20.0,
            depth=20.0,
            step=10.0,
        )
        for pt in result['profile']:
            assert pt['q_Pa'] > 0, f'Pressão não positiva em z={pt["z"]}m'
        # q deve ser monotônico crescente com z
        q_vals = [pt['q_Pa'] for pt in result['profile']]
        for i in range(1, len(q_vals)):
            assert q_vals[i] > q_vals[i - 1] * 0.99, f'Pressão decresceu em z={i * 5}m: {q_vals[i - 1]} → {q_vals[i]}'
    except ImportError:
        pytest.skip('wind_engine não disponível')


# ─────────────────────────────────────────────────────
# 7. Simetria — radier quadrado com carga uniforme
# ─────────────────────────────────────────────────────


def test_radier_symmetry_uniform_load():
    """Radier quadrado com carga uniforme: recalques simétricos."""
    try:
        from radier_solver_v2 import Material, PlateModel, RadierMindlinWinklerV2, Soil

        model = PlateModel(
            Lx=10.0,
            Ly=10.0,
            nx=9,
            ny=9,
            material=Material(E=30e9, nu=0.2, h=0.5),
            soil=Soil(kv=20e6, tensionless=False),
        )
        solver = RadierMindlinWinklerV2(model)
        solver._q_uniform = 50000.0
        res = solver.solve(max_iter=5)
        w = res.disp[:, 0].reshape(model.ny, model.nx)
        # w[i,j] deve ser ≈ w[ny-1-i, j] e w[i, nx-1-j]
        for i in range(model.ny):
            for j in range(model.nx):
                wij = w[i, j]
                w_sym_x = w[i, model.nx - 1 - j]
                w_sym_y = w[model.ny - 1 - i, j]
                assert abs(wij - w_sym_x) < 1e-6, f'Simetria X violada em ({i},{j}): {wij:.2e} ≠ {w_sym_x:.2e}'
                assert abs(wij - w_sym_y) < 1e-6, f'Simetria Y violada em ({i},{j}): {wij:.2e} ≠ {w_sym_y:.2e}'
    except ImportError:
        pytest.skip('radier_solver_v2 não disponível')
