"""
Solver audit tests for critical mathematical invariants.

These tests intentionally avoid pytest-only features so they can also be run with:

    .venv/bin/python tests/test_solver_audit.py

The checks focus on closed-form cases and global equilibrium. Any production solver
path that cannot satisfy these invariants should not be treated as authoritative.
"""
from __future__ import annotations

import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def assert_close(actual: float, expected: float, rel: float = 1e-6, abs_tol: float = 1e-9, label: str = "") -> None:
    limit = max(abs_tol, rel * max(abs(expected), 1.0))
    if abs(actual - expected) > limit:
        prefix = f"{label}: " if label else ""
        raise AssertionError(f"{prefix}{actual:.12g} != {expected:.12g} (tol={limit:.3g})")


def test_beam_simply_supported_uniform_load_equilibrium_and_moment() -> None:
    from beam_solver import run_beam_analysis

    L = 6.0
    q = 20.0
    b = 0.20
    h = 0.50
    self_weight = b * h * 25.0
    q_total = q + self_weight

    result = run_beam_analysis(
        L=L,
        b=b,
        h=h,
        fck=30.0,
        cover=30.0,
        nonlinear=False,
        n_elements=20,
        supports=[{"x": 0.0, "type": "pinned"}, {"x": L, "type": "pinned"}],
        distributed_loads=[{"x_start": 0.0, "x_end": L, "q_start": q, "q_end": q}],
        point_loads=[],
    )

    expected_load = q_total * L
    expected_reaction = expected_load / 2.0
    expected_moment = q_total * L**2 / 8.0

    assert_close(result["summary"]["total_load_kN"], expected_load, rel=1e-9, label="beam total load")
    assert_close(result["summary"]["total_reaction_kN"], expected_load, rel=1e-8, label="beam total reaction")
    assert_close(result["reactions"]["0.0"]["R"], expected_reaction, rel=1e-8, label="left reaction")
    assert_close(result["reactions"][str(float(L))]["R"], expected_reaction, rel=1e-8, label="right reaction")
    assert_close(result["summary"]["max_moment_kNm"], expected_moment, rel=2e-3, label="beam max moment")


def test_frame_cantilever_tip_load_deflection_and_equilibrium() -> None:
    from frame_engine import Frame3DEngine, FrameLoad, FrameMember, FrameNode, FrameSection

    E = 25e9
    nu = 0.20
    b = 0.30
    h = 0.50
    L = 3.0
    force_n = 10_000.0
    section = FrameSection(b=b, h=h, E=E, G=E / (2.0 * (1.0 + nu)))
    nodes = [FrameNode(1, 0.0, 0.0, 0.0), FrameNode(2, 0.0, 0.0, L)]
    members = [FrameMember(1, 1, 2, section)]
    loads = [FrameLoad(2, Fx=force_n)]
    supports = {1: [0, 1, 2, 3, 4, 5]}

    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    result = engine.solve(loads, supports, use_rust=False)
    equilibrium = engine.check_equilibrium(loads, result["displacements"], supports)

    inertia_y = h * b**3 / 12.0
    expected_tip_dx = force_n * L**3 / (3.0 * E * inertia_y)
    actual_tip_dx = result["displacements"][2][0]

    assert_close(actual_tip_dx, expected_tip_dx, rel=1e-6, label="frame cantilever tip dx")
    max_equilibrium_error = max(abs(v) for v in equilibrium["equilibrium_error_kN_m"])
    assert_close(max_equilibrium_error, 0.0, abs_tol=1e-8, label="frame equilibrium")


def test_frame_stiffness_reduction_classifies_columns_and_beams() -> None:
    from frame_engine import Frame3DEngine, FrameMember, FrameNode, FrameSection

    section = FrameSection(b=0.30, h=0.50)
    nodes = [
        FrameNode(1, 0.0, 0.0, 0.0),
        FrameNode(2, 0.0, 0.0, 3.0),
        FrameNode(3, 4.0, 0.0, 3.0),
    ]
    members = [
        FrameMember(1, 1, 2, section),
        FrameMember(2, 2, 3, section),
    ]
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)

    assert engine._get_member_type(members[0]) == "column"
    assert engine._get_member_type(members[1]) == "beam"
    assert engine._get_member_type_code(members[0]) == 0
    assert engine._get_member_type_code(members[1]) == 1


def test_slab_uniform_load_edge_supports_global_equilibrium() -> None:
    import lajes_solver
    from lajes_solver import LajeModel, LajesMindlinSolver, LineSupport, Material, SupportType

    # Force the auditable Python path; Rust parity should be covered by a separate
    # native-vs-Python suite before re-enabling it as authoritative.
    lajes_solver.HAS_RUST_CORE = False

    Lx = 4.0
    Ly = 3.0
    q = 5_000.0
    model = LajeModel(
        Lx=Lx,
        Ly=Ly,
        nx=5,
        ny=5,
        material=Material(E=25e9, nu=0.20, h=0.15),
        q_acid=q,
        line_supports=[
            LineSupport("bottom", 0.0, 0.0, Lx, 0.0, SupportType.PINNED),
            LineSupport("top", 0.0, Ly, Lx, Ly, SupportType.PINNED),
            LineSupport("left", 0.0, 0.0, 0.0, Ly, SupportType.PINNED),
            LineSupport("right", Lx, 0.0, Lx, Ly, SupportType.PINNED),
        ],
    )
    result = LajesMindlinSolver(model).solve()
    expected_load = q * Lx * Ly

    assert_close(result.distributed_load_total, expected_load, rel=1e-12, label="slab distributed load")
    assert_close(result.reactions_total, expected_load, rel=1e-8, label="slab total reaction")
    assert_close(result.residual, 0.0, abs_tol=1e-5, label="slab residual")


def test_footing_area_keeps_soil_pressure_within_allowable() -> None:
    from footing_solver import solve_isolated_footing

    result = solve_isolated_footing({"Nd": 500.0, "sigma_adm": 300.0, "ap": 0.20, "bp": 0.20, "fck": 25.0})
    demand_with_self_weight = 500.0 * 1.10

    assert result["area_m2"] >= demand_with_self_weight / 300.0
    assert result["sigma_max_kPa"] <= result["sigma_adm_kPa"]
    assert result["status"] == "OK"


def test_column_solver_returns_design_without_name_errors() -> None:
    from column_solver import ColumnLoads, ColumnSection, solve_column_section

    result = solve_column_section(
        ColumnSection(b=0.40, h=0.40, fck=30.0, L_free=3.0, caa=2),
        ColumnLoads(Nd_kN=1_000.0, Mxd_kNm=50.0, Myd_kNm=20.0),
    )

    assert result["status"] in {"OK", "ALTA_ESBELTEZ_REVISAR_RIGOROSO", "TAXA_ALTA_CONGESTIONADA", "FORA_DIAGRAMA_INTERACAO"}
    assert result["As_final_cm2"] > 0.0
    assert result["durability"]["cover_ok"] is True


def test_stability_gamma_z_never_becomes_negative_for_unstable_case() -> None:
    from stability_engine import StabilityEngine

    result = StabilityEngine.calculate_advanced_stability(
        total_p_kN=50_000.0,
        height=100.0,
        m1_kNm=2_000.0,
        wind_v0=45.0,
        f1_hz=0.2,
        total_h_force_kN=1_000.0,
    )

    assert math.isinf(result.gamma_z)
    assert result.is_stable is False
    assert result.requires_second_order is True
    assert result.is_divergent is True


def run_all() -> None:
    tests = [
        test_beam_simply_supported_uniform_load_equilibrium_and_moment,
        test_frame_cantilever_tip_load_deflection_and_equilibrium,
        test_frame_stiffness_reduction_classifies_columns_and_beams,
        test_slab_uniform_load_edge_supports_global_equilibrium,
        test_footing_area_keeps_soil_pressure_within_allowable,
        test_column_solver_returns_design_without_name_errors,
        test_stability_gamma_z_never_becomes_negative_for_unstable_case,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_all()
