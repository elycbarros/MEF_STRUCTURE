from __future__ import annotations

import asyncio
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from routes.mestre_frame import MestreFrameRequest, analyze_mestre_frame
from routes.special import SpecialElementRequest, calculate_special, calculate_spt, calculate_stability_mestre
from routes.wind import calculate_wind
from schemas.wind import WindRequest
from professional_pdf import generate_professional_memorial


REQUIRED_KEYS = {
    "success",
    "result",
    "summary",
    "full_results",
    "pedagogical_steps",
    "calculation_trace",
}

TRACE_KEYS = {
    "requested_type",
    "solver_module",
    "blackboard_builder",
    "classical_check",
    "mef_check",
}


def run(coro):
    return asyncio.run(coro)


def assert_contract(testcase: unittest.TestCase, payload: dict, expected_type: str) -> None:
    missing = REQUIRED_KEYS - set(payload.keys())
    testcase.assertFalse(missing, f"Envelope incompleto para {expected_type}: {sorted(missing)}")
    testcase.assertTrue(payload["success"], f"{expected_type} retornou success falso")
    testcase.assertIsNotNone(payload["result"], f"{expected_type} sem result")
    testcase.assertIsNotNone(payload["summary"], f"{expected_type} sem summary")
    testcase.assertIsNotNone(payload["full_results"], f"{expected_type} sem full_results")

    steps = payload["pedagogical_steps"]
    if isinstance(steps, dict):
        steps = steps.get("steps", [])
    testcase.assertIsInstance(steps, list, f"{expected_type} pedagogical_steps deve ser lista ou dict.steps")
    testcase.assertGreater(len(steps), 0, f"{expected_type} sem passos pedagógicos")

    trace = payload["calculation_trace"]
    testcase.assertIsInstance(trace, dict, f"{expected_type} calculation_trace inválido")
    missing_trace = TRACE_KEYS - set(trace.keys())
    testcase.assertFalse(missing_trace, f"Trace incompleto para {expected_type}: {sorted(missing_trace)}")
    testcase.assertEqual(trace["requested_type"], expected_type)


class TestMestreResponseContract(unittest.TestCase):
    def test_special_element_modules_follow_contract(self):
        fixtures = [
            ("beam", {"L": 6.0, "b": 0.20, "h": 0.50, "q": 20.0, "fck": 30.0}),
            ("column", {"b": 0.40, "h": 0.40, "Nd": 1000.0, "L_free": 3.0, "Mxd": 25.0, "Myd": 10.0}),
            ("slab", {"Lx": 4.0, "Ly": 3.0, "h": 0.15, "q": 5.0, "nx": 5, "ny": 5}),
            ("footing", {"Nd": 500.0, "sigma_adm": 300.0, "ap": 0.20, "bp": 0.20, "fck": 25.0}),
            ("pile", {"diameter": 0.40, "length": 10.0, "Nd": 500.0, "pile_type": "bored"}),
            ("pile_cap", {"Nd": 1000.0, "dist_piles": 1.6, "ap": 0.30, "bp": 0.30}),
            ("advanced_slab", {"Lx": 6.0, "Ly": 5.0, "h": 0.25, "q_dist": 5.0, "kv": 30.0, "columns": []}),
            ("tension_pro", {"span": 10.0, "q_service": 20.0, "p0": 1200.0, "eccentricity": 0.15}),
            ("exam_auditor", {"question_id": "q47_fcc_2018"}),
        ]

        for element_type, params in fixtures:
            with self.subTest(element_type=element_type):
                payload = run(calculate_special(SpecialElementRequest(type=element_type, params=params)))
                assert_contract(self, payload, element_type)

    def test_beam_force_model_disables_self_weight_and_rebar_detailing(self):
        payload = run(calculate_special(SpecialElementRequest(type="beam", params={
            "beam_analysis_mode": "force_model",
            "L": 6.0,
            "q": 20.0,
            "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
            "distributed_loads": [{"x_start": 0.0, "x_end": 6.0, "q_start": 20.0, "q_end": 20.0}],
            "point_loads": [],
            "include_self_weight": True,
            "structural_material": "concreto_armado",
            "n_elements": 7,
        })))
        assert_contract(self, payload, "beam")

        result = payload["result"]
        summary = payload["summary"]
        self.assertEqual(summary["beam_analysis_mode"], "force_model")
        self.assertFalse(summary["include_self_weight"])
        self.assertFalse(summary["design_requires_rebar"])
        self.assertEqual(summary["n_elements"], 7)
        self.assertEqual(result["model_info"]["n_elements"], 7)
        self.assertEqual(len(result["diagrams"]["moment"]), 7)
        self.assertAlmostEqual(result["diagrams"]["shear"][0]["x"], 0.0)
        self.assertAlmostEqual(result["diagrams"]["shear"][0]["y"], 0.0, places=6)
        self.assertAlmostEqual(result["diagrams"]["shear"][-1]["x"], 6.0)
        self.assertAlmostEqual(result["diagrams"]["shear"][-1]["y"], 0.0, places=3)
        self.assertNotIn("detailing", result)

        steps = payload["pedagogical_steps"].get("steps", payload["pedagogical_steps"])
        step_text = " ".join(f"{step.get('id', '')} {step.get('title', '')}".lower() for step in steps)
        self.assertNotIn("armadura", step_text)
        self.assertIn("escopo da análise", step_text)

        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "beam_force_model.pdf"
            generate_professional_memorial(str(output), result, {
                "obra": "Teste Modelo de Forças",
                "local": "Laboratório",
                "responsavel": "ATLAS",
                "registro": "N/A",
            })
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)

    def test_frame_and_truss_follow_contract(self):
        frame_payload = MestreFrameRequest(
            nodes=[
                {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 0.0, "y": 0.0, "z": 3.0},
                {"id": 3, "x": 4.0, "y": 0.0, "z": 3.0},
            ],
            members=[
                {"id": 1, "node_i": 1, "node_j": 2, "section": {"b": 0.30, "h": 0.50, "E": 25e9}},
                {"id": 2, "node_i": 2, "node_j": 3, "section": {"b": 0.30, "h": 0.50, "E": 25e9}},
            ],
            loads=[{"node_id": 3, "fz": -10000.0}],
            supports={"1": [0, 1, 2, 3, 4, 5], "3": [1, 2, 3, 4, 5]},
        )
        assert_contract(self, run(analyze_mestre_frame(frame_payload)), "frames")

        truss_payload = MestreFrameRequest(
            nodes=[
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "x": 3.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 0.0, "y": 0.0, "z": 3.0},
                {"id": 3, "x": 3.0, "y": 0.0, "z": 3.0},
                {"id": 4, "x": 0.0, "y": 0.0, "z": 6.0},
                {"id": 5, "x": 3.0, "y": 0.0, "z": 6.0},
            ],
            members=[
                {"id": 0, "node_i": 0, "node_j": 1, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 1, "node_i": 2, "node_j": 3, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 2, "node_i": 4, "node_j": 5, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 3, "node_i": 0, "node_j": 2, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 4, "node_i": 2, "node_j": 4, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 5, "node_i": 1, "node_j": 3, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 6, "node_i": 3, "node_j": 5, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 7, "node_i": 0, "node_j": 3, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
                {"id": 8, "node_i": 2, "node_j": 5, "section": {"b": 0.1, "h": 0.1, "E": 210e9}},
            ],
            loads=[{"node_id": 4, "fx": 20000.0}, {"node_id": 5, "fz": -20000.0}],
            supports={"0": [0, 1, 2, 3, 4, 5], "1": [1, 2, 3, 4, 5]},
            is_truss=True,
        )
        assert_contract(self, run(analyze_mestre_frame(truss_payload)), "trusses")

    def test_geotechnical_stability_and_wind_follow_contract(self):
        spt_payload = run(calculate_spt({
            "spt_data": [
                {"depth_m": 1.0, "nspt": 4, "soil_type": "Areia fofa"},
                {"depth_m": 2.0, "nspt": 10, "soil_type": "Areia media"},
                {"depth_m": 3.0, "nspt": 18, "soil_type": "Areia compacta"},
            ]
        }))
        assert_contract(self, spt_payload, "spt")

        stability_payload = run(calculate_stability_mestre({
            "v0": 30.0,
            "height": 30.0,
            "width_x": 12.0,
            "f1_hz": 0.5,
            "total_p_kN": 10000.0,
            "m1_kNm": 5000.0,
        }))
        assert_contract(self, stability_payload, "stability")

        wind_payload = run(calculate_wind(WindRequest(
            v0=30.0,
            altura_total=15.0,
            largura=10.0,
            profundidade=10.0,
            step=3.0,
        )))
        assert_contract(self, wind_payload, "wind")


if __name__ == "__main__":
    unittest.main()
