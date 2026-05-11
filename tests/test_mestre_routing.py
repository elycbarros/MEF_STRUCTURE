from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "mef_engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from api import app  # noqa: E402


client = TestClient(app, raise_server_exceptions=False)


CASES = [
    (
        "beam",
        {"L": 6.0, "b": 0.2, "h": 0.5, "q": 20.0, "fck": 30.0},
        "beam_solver.run_beam_analysis",
        True,
    ),
    (
        "slab",
        {"Lx": 5.0, "Ly": 4.0, "h": 0.16, "q": 5.0, "fck": 30.0},
        "lajes_solver.LajesMindlinSolver",
        True,
    ),
    (
        "column",
        {"b": 0.4, "h": 0.4, "Nd": 1000.0, "fck": 30.0, "L_free": 3.0},
        "column_solver.solve_column_section",
        False,
    ),
    (
        "footing",
        {"Nd": 500.0, "sigma_adm": 300.0, "ap": 0.2, "bp": 0.2, "fck": 25.0},
        "footing_solver.solve_isolated_footing",
        False,
    ),
    (
        "pile_cap",
        {
            "Nd": 1000.0,
            "dist_piles": 1.6,
            "ap": 0.3,
            "bp": 0.3,
            "diam_pile": 0.4,
            "d_height": 0.65,
            "fck": 30.0,
        },
        "pile_cap_solver.solve_pile_cap_2_piles",
        False,
    ),
    (
        "pile",
        {"diameter": 0.4, "length": 12.0, "Nd": 500.0, "fck": 30.0},
        "piles_engine.PilesEngine.run_full_analysis",
        False,
    ),
    (
        "pile",
        {"diameter": 0.4, "length": 12.0, "Nd": 500.0, "fck": 30.0, "pile_type": "cfa"},
        "piles_engine.PilesEngine.run_full_analysis",
        False,
    ),
    (
        "stair",
        {"L": 4.0, "H": 3.0, "q": 5.0, "fck": 30.0},
        "SpecialElementsSolver.solve_stair",
        False,
    ),
    (
        "helical_stairs",
        {"radius": 2.5, "angle_total_deg": 180.0, "h_step": 0.18, "t": 0.15, "q_acid": 3.0},
        "SpecialElementsSolver.solve_helical_stairs",
        False,
    ),
    (
        "retaining_wall",
        {"h_wall": 4.0, "gamma_soil": 18.0, "phi_soil": 30.0, "b_base": 2.5},
        "SpecialElementsSolver.solve_retaining_wall",
        False,
    ),
    (
        "concrete_wall",
        {"Nd": 500.0, "h": 2.8, "t": 0.12, "fck": 30.0},
        "ColumnEngine.solve_concrete_wall",
        False,
    ),
    (
        "reservoir",
        {"length": 5.0, "width": 3.0, "depth": 3.0},
        "SpecialElementsSolver.solve_reservoir",
        False,
    ),
    (
        "corbel",
        {"fd_kN": 200.0, "a_dist": 0.25, "d_eff": 0.45, "fck": 30.0},
        "SpecialElementsSolver.solve_corbel",
        False,
    ),
    (
        "gerber_tooth",
        {"vd_kN": 150.0, "hd_kN": 30.0, "a_dist": 0.15, "d_eff": 0.4, "fck": 30.0},
        "SpecialElementsSolver.solve_gerber_tooth",
        False,
    ),
    (
        "deep_beam",
        {"L": 4.0, "h": 3.0, "fd_kN_m": 100.0},
        "SpecialElementsSolver.solve_deep_beam",
        False,
    ),
]


def test_mestre_calculation_endpoint_is_registered() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_unknown_mestre_element_returns_400() -> None:
    response = client.post(
        "/api/mestre/calculate/special-elements",
        json={"type": "not_a_real_element", "params": {}},
    )

    assert response.status_code == 400
    assert "não suportado" in response.json()["detail"]


def test_known_mestre_elements_route_to_their_expected_solvers() -> None:
    for element_type, params, expected_solver, expected_mef in CASES:
        response = client.post(
            "/api/mestre/calculate/special-elements",
            json={"type": element_type, "params": params},
        )

        assert response.status_code == 200, (element_type, response.text)
        payload = response.json()
        trace = payload["calculation_trace"]
        blackboard = payload["pedagogical_steps"]
        steps = blackboard["steps"]

        assert payload["success"] is True
        assert trace["requested_type"] == element_type
        assert trace["solver_module"] == expected_solver
        assert trace["blackboard_builder"]
        assert trace["classical_check"] is True
        assert trace["mef_check"] is expected_mef
        assert blackboard["metadata"]["element_type"] == element_type
        assert blackboard["metadata"].get("status") != "warning"
        assert len(steps) > 0
        assert payload["result"]["calculation_trace"] == trace


def test_beam_and_slab_do_not_cross_call_each_other() -> None:
    beam_response = client.post(
        "/api/mestre/calculate/special-elements",
        json={"type": "beam", "params": {"L": 6.0, "b": 0.2, "h": 0.5, "q": 20.0}},
    )
    slab_response = client.post(
        "/api/mestre/calculate/special-elements",
        json={"type": "slab", "params": {"Lx": 5.0, "Ly": 4.0, "h": 0.16, "q": 5.0}},
    )

    assert beam_response.json()["calculation_trace"]["solver_module"] == "beam_solver.run_beam_analysis"
    assert slab_response.json()["calculation_trace"]["solver_module"] == "lajes_solver.LajesMindlinSolver"
    assert "beam_solver" not in slab_response.json()["calculation_trace"]["solver_module"]
    assert "LajesMindlinSolver" not in beam_response.json()["calculation_trace"]["solver_module"]


def test_beam_uses_custom_supports_for_overhangs() -> None:
    response = client.post(
        "/api/mestre/calculate/special-elements",
        json={
            "type": "beam",
            "params": {
                "L": 6.0,
                "b": 0.2,
                "h": 0.5,
                "fck": 30.0,
                "supports": [{"x": 1.2, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
                "distributed_loads": [{"x_start": 0.0, "x_end": 6.0, "q_start": 20.0, "q_end": 20.0}],
            },
        },
    )

    assert response.status_code == 200, response.text
    reactions = response.json()["result"]["reactions"]
    assert "1.2" in reactions
    assert "6.0" in reactions
    assert "0.0" not in reactions
