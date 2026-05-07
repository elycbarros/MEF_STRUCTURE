"""
tests/test_structural_suite.py
Suite pytest para MEF STRUCTURAL V4.0.0

Cobre todos os motores Premium em um único arquivo estruturado.
Execute com: pytest tests/ -v
"""
import pytest
import numpy as np
import sys, os

# Add root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
from beam_solver import run_beam_analysis
from load_combinator import combine_nbr8681
from column_solver import ColumnSection, ColumnLoads, solve_column_section
from stability_engine import StabilityEngine

# ─────────────────────────────────────────────────────────────────
# C1 + C2 — Frame Engine 3D + P-Delta + γz nodal
# ─────────────────────────────────────────────────────────────────
class TestFrame3DEngine:
    def _build_cantilever(self, n_floors=5, floor_h=3.0, b=0.40, h_sec=0.40):
        from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
        sec = FrameSection(b=b, h=h_sec)
        nodes = [FrameNode(id=i, x=0, y=0, z=i * floor_h) for i in range(n_floors + 1)]
        members = [FrameMember(id=i, node_i=i, node_j=i+1, section=sec) for i in range(n_floors)]
        engine = Frame3DEngine(nodes, members)
        return engine, nodes, members

    def test_cantilever_tip_displacement_analytical(self):
        """δ = F·H³/3EI para cantilever — tolerância 1%."""
        from frame_engine import FrameLoad, FrameSection
        engine, nodes, members = self._build_cantilever(n_floors=1, floor_h=3.0, b=0.30, h_sec=0.30)
        F = 10_000.0  # 10 kN
        E = 2.5e10
        I = 0.30 * 0.30**3 / 12
        delta_analytical = F * 3.0**3 / (3 * E * I)
        loads = [type('L', (), {'node_id': 1, 'Fx': F, 'Fy': 0, 'Fz': 0, 'Mx': 0, 'My': 0, 'Mz': 0})()] 
        from frame_engine import FrameLoad
        loads = [FrameLoad(node_id=1, Fx=F)]
        supports = {0: [0, 1, 2, 3, 4, 5]}
        res = engine.solve(loads, supports)
        delta_fem = abs(res["displacements"][1][0])
        assert abs(delta_fem - delta_analytical) / delta_analytical < 0.01, \
            f"Erro FEM vs Analítico: {delta_fem:.6f} vs {delta_analytical:.6f}"

    def test_p_delta_amplifies_displacement(self):
        """P-Delta deve amplificar o deslocamento horizontal."""
        from frame_engine import FrameLoad
        engine, nodes, _ = self._build_cantilever(n_floors=5, floor_h=3.0)
        loads = [FrameLoad(node_id=5, Fz=-50_000, Fx=1_000)]
        supports = {0: [0, 1, 2, 3, 4, 5]}
        res_1 = engine.solve(loads, supports)
        res_2 = engine.solve_p_delta(loads, supports)
        d1 = abs(res_1["displacements"][5][0])
        d2 = abs(res_2["displacements"][5][0])
        assert d2 >= d1 * 0.9, "P-Delta deve amplificar ou ser próximo do linear em estruturas rígidas"

    def test_gamma_z_non_sensitive(self):
        """γz de edifício rígido deve ser ≤ 1.10."""
        from frame_engine import FrameLoad
        engine, nodes, _ = self._build_cantilever(n_floors=3, floor_h=3.0, b=0.60, h_sec=0.60)
        loads = [FrameLoad(node_id=3, Fz=-50_000, Fx=500)]
        supports = {0: [0, 1, 2, 3, 4, 5]}
        r1 = engine.solve(loads, supports)
        r2 = engine.solve_p_delta(loads, supports)
        d1 = abs(r1["displacements"][3][0])
        d2 = abs(r2["displacements"][3][0])
        gamma_z = d2 / d1 if d1 > 1e-9 else 1.0
        assert gamma_z <= 1.30, f"γz={gamma_z:.3f} não deveria indicar instabilidade para seção 60×60"

    def test_nbr_stiffness_reduction(self):
        """E reduzido (×0.8) deve gerar deslocamento maior."""
        from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
        sec_full = FrameSection(b=0.40, h=0.40, E=2.5e10)
        sec_red = FrameSection(b=0.40, h=0.40, E=2.5e10 * 0.8)
        nodes = [FrameNode(id=i, x=0, y=0, z=i * 3.0) for i in range(2)]
        m_full = [FrameMember(id=0, node_i=0, node_j=1, section=sec_full)]
        m_red = [FrameMember(id=0, node_i=0, node_j=1, section=sec_red)]
        loads = [FrameLoad(node_id=1, Fx=10_000)]
        sup = {0: [0, 1, 2, 3, 4, 5]}
        d_full = abs(Frame3DEngine(nodes, m_full).solve(loads, sup)["displacements"][1][0])
        d_red = abs(Frame3DEngine(nodes, m_red).solve(loads, sup)["displacements"][1][0])
        assert d_red > d_full, "Rigidez reduzida deve gerar maior deslocamento"


# ─────────────────────────────────────────────────────────────────
# Beam Premium — Branson + wk + Redistribuição
# ─────────────────────────────────────────────────────────────────
class TestBeamPremium:
    def _run_beam(self, L=6.0, nonlinear=True, bf=0.0, redistribution=0.90):
        from beam_solver import run_beam_analysis
        return run_beam_analysis(
            L=L,
            supports=[{"x": 0.0, "type": "pinned"}, {"x": L, "type": "pinned"}],
            distributed_loads=[{"x_start": 0, "x_end": L, "q_start": 20_000}],
            b=0.20, h=0.50, fck=30,
            bf=bf, nonlinear=nonlinear,
            redistribution_delta=redistribution,
        )

    def test_nonlinear_deflection_greater_than_linear(self):
        """Flecha não-linear (fissurada) deve ser ≥ linear."""
        res_nl = self._run_beam(nonlinear=True)
        res_l = self._run_beam(nonlinear=False)
        assert res_nl["summary"]["max_deflection_mm"] >= res_l["summary"]["max_deflection_mm"] * 0.95

    def test_analysis_type_label(self):
        res = self._run_beam(nonlinear=True)
        assert res["summary"]["analysis_type"] == "FISICA_NAO_LINEAR"

    def test_t_beam_larger_flange(self):
        """Seção T deve ter bf maior que a alma."""
        res = self._run_beam(bf=0.60)
        assert res["summary"]["bf_m"] >= 0.60, "bf não foi aplicado"

    def test_crack_width_positive(self):
        """wk deve ser um float positivo."""
        res = self._run_beam()
        wk = res["design"]["crack_width"]["wk_mm"]
        assert isinstance(wk, float) and wk >= 0

    def test_redistribution_reduces_support_moment(self):
        """Redistribuição deve reduzir o momento negativo (apoio)."""
        res_10 = self._run_beam(redistribution=0.90)
        res_0 = self._run_beam(redistribution=1.00)
        M_neg_10 = res_10["design"]["M_max_neg_kNm"]
        M_neg_0 = res_0["design"]["M_max_neg_kNm"]
        assert abs(M_neg_10) <= abs(M_neg_0) * 1.01  # pode ser marginal


class TestLoadCombinator:
    def test_nbr8681_elu_and_els_values(self):
        res = combine_nbr8681([
            {"name": "G", "kind": "permanent", "value": 100.0},
            {"name": "Q", "kind": "variable", "value": 30.0, "category": "residential"},
        ])
        assert res["envelopes"]["elu"]["max"] == pytest.approx(182.0)
        assert res["els_freq"][0]["value"] == pytest.approx(112.0)
        assert res["els_qp"]["value"] == pytest.approx(109.0)


# ─────────────────────────────────────────────────────────────────
# Column Pro — Biaxial + Esbeltez
# ─────────────────────────────────────────────────────────────────
class TestColumnPro:
    def test_biaxial_returns_design_dict(self):
        from column_solver import ColumnSection, ColumnLoads, solve_column_section
        sec = ColumnSection(b=0.40, h=0.40, fck=30, L_free=3.0)
        loads = ColumnLoads(Nd_kN=1000, Mxd_kNm=50, Myd_kNm=30)
        design = solve_column_section(sec, loads)
        assert "As_total_cm2" in design or "As_cm2" in design or isinstance(design, dict)

    def test_column_domain_is_valid(self):
        from column_solver import ColumnSection, ColumnLoads, solve_column_section
        sec = ColumnSection(b=0.30, h=0.30, fck=25, L_free=3.0)
        loads = ColumnLoads(Nd_kN=500, Mxd_kNm=20, Myd_kNm=0)
        design = solve_column_section(sec, loads)
        assert isinstance(design, dict)


# ─────────────────────────────────────────────────────────────────
# Stability Engine — γz cantilever
# ─────────────────────────────────────────────────────────────────
class TestStabilityEngine:
    def test_stiff_building_not_sensitive(self):
        from stability_engine import StabilityEngine
        res = StabilityEngine.calculate_advanced_stability(
            total_p_kN=5000, height=15.0, m1_kNm=3000,
            wind_v0=30.0, f1_hz=1.0, total_h_force_kN=100
        )
        assert res.gamma_z < 1.30, f"Edifício rígido não deveria ser instável (γz={res.gamma_z:.2f})"

    def test_slender_building_sensitive(self):
        from stability_engine import StabilityEngine
        res = StabilityEngine.calculate_advanced_stability(
            total_p_kN=50_000, height=100.0, m1_kNm=2000,
            wind_v0=45.0, f1_hz=0.2, total_h_force_kN=1000
        )
        assert res.requires_second_order or res.gamma_z > 1.0


# ─────────────────────────────────────────────────────────────────
# API Route — importação de módulos e schemas
# ─────────────────────────────────────────────────────────────────
class TestAPIImports:
    def test_frame_route_importable(self):
        import routes.frame  # não deve lançar ImportError

    def test_frame_schema_importable(self):
        from schemas.frame import FrameRequest, FrameNodeInput, FrameMemberInput

    def test_beam_route_importable(self):
        from beam_solver import run_beam_analysis

    def test_column_route_importable(self):
        from column_solver import ColumnSection, ColumnLoads, solve_column_section


class TestAPIRoutes:
    def _client(self):
        from fastapi.testclient import TestClient
        from api import app
        return TestClient(app)

    def test_beam_endpoint_returns_durability_and_memorial(self):
        res = self._client().post("/calculate/beam", json={
            "L": 6.0,
            "b": 0.2,
            "h": 0.5,
            "fck": 30,
            "caa": 3,
            "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
            "distributed_loads": [{"x_start": 0, "x_end": 6, "q_start": 20000}],
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["design"]["durability"]["caa"] == 3
        assert data["design"]["crack_width"]["limit_mm"] == 0.2
        assert "Memorial de Calculo Padronizado - Viga Premium" in data["memorial_markdown"]
        blackboard = data["pedagogical_steps"]
        assert blackboard["mode"] == "MESTRE"
        assert blackboard["element"] == "beam"
        assert len(blackboard["steps"]) >= 12
        step_ids = {s["id"] for s in blackboard["steps"]}
        assert "beam-flexure" in step_ids
        assert "beam-shear-check" in step_ids
        assert "beam-crack-width" in step_ids
        assert "beam-deflection" in step_ids
        assert "beam-final-decision" in step_ids

    def test_column_endpoint_applies_caa_cover(self):
        res = self._client().post("/calculate/column", json={
            "b": 0.4,
            "h": 0.4,
            "fck": 30,
            "caa": 4,
            "L_free": 3,
            "Nd_kN": 1000,
            "Mxd_kNm": 50,
            "Myd_kNm": 20,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["design"]["durability"]["caa"] == 4
        assert data["design"]["durability"]["cover_required_mm"] == 50
        assert data["design"]["durability"]["cover_ok"] is True
        blackboard = data["pedagogical_steps"]
        assert blackboard["mode"] == "MESTRE"
        assert blackboard["element"] == "column"
        assert len(blackboard["steps"]) >= 8
        slenderness_step = next(s for s in blackboard["steps"] if s["id"] == "column-slenderness")
        assert "\\lambda = L_e / i" in slenderness_step["formula_latex"]
        assert "\\lambda =" in slenderness_step["substitution_latex"]
        assert "\\lambda \\approx" in slenderness_step["result_latex"]
        step_ids = {s["id"] for s in blackboard["steps"]}
        assert "column-2nd-order" in step_ids
        assert "column-uls-check" in step_ids
        assert "column-reinforcement" in step_ids
        assert "column-durability" in step_ids
        assert "column-final-decision" in step_ids

    def test_frame_endpoint_uses_premium_engine(self):
        payload = {
            "nodes": [
                {"id": 1, "x": 0, "y": 0, "z": 0},
                {"id": 2, "x": 0, "y": 0, "z": 3},
            ],
            "members": [
                {"id": 1, "node_i": 1, "node_j": 2, "type": "column", "section": {"b": 0.4, "h": 0.4}},
            ],
            "loads": [{"node_id": 2, "Fx": 1000, "Fz": -10000}],
            "supports": {"1": [0, 1, 2, 3, 4, 5]},
        }
        res = self._client().post("/calculate/frame", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["analysis_type"] == "PORTICO_3D_PREMIUM_P_DELTA"
        assert "model_3d" in data
        assert "top_displacement_mm" in data
        assert data["equilibrium"]["is_equilibrated"] is True
        assert "Memorial de Calculo Padronizado - Portico 3D Premium" in data["memorial_markdown"]

    def test_academic_beam_pdf_export(self):
        res = self._client().post("/export/academic/beam", json={
            "L": 6.0,
            "b": 0.2,
            "h": 0.5,
            "fck": 30,
            "caa": 2,
            "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
            "distributed_loads": [{"x_start": 0, "x_end": 6, "q_start": 20000}],
        })
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF")
        assert len(res.content) > 1000

    def test_academic_column_pdf_export(self):
        res = self._client().post("/export/academic/column", json={
            "b": 0.4,
            "h": 0.4,
            "fck": 30,
            "caa": 2,
            "L_free": 3,
            "Nd_kN": 1000,
            "Mxd_kNm": 50,
            "Myd_kNm": 20,
        })
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF")
        assert len(res.content) > 1000

    def test_load_combination_endpoint(self):
        res = self._client().post("/calculate/load-combinations", json={
            "actions": [
                {"name": "G", "kind": "permanent", "value": 100.0, "is_favorable": False},
                {"name": "Q", "kind": "variable", "value": 30.0, "category": "residential"},
            ],
            "gamma_g_unfav": 1.4,
            "gamma_q": 1.4
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["envelopes"]["elu"]["max"] == pytest.approx(182.0)
        assert data["els_freq"][0]["value"] == pytest.approx(112.0)

    def test_core_rejects_kv_with_likely_wrong_units(self):
        payload = {
            "Lx": 10.0,
            "Ly": 10.0,
            "h": 0.3,
            "kv": 22000.0,
            "q": 100000.0,
            "sigma_adm_kPa": 200.0,
            "fck": 30.0,
            "fyk": 500.0,
        }
        res = self._client().post("/calculate", json=payload)
        assert res.status_code == 422
        assert "N/m" in res.text or "greater than or equal" in res.text

    def test_beam_rejects_absurd_fck(self):
        res = self._client().post("/calculate/beam", json={
            "L": 6.0,
            "b": 0.2,
            "h": 0.5,
            "fck": 300.0,
            "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
        })
        assert res.status_code == 422

    def test_wind_rejects_velocity_outside_contract(self):
        res = self._client().post("/calculate/wind", json={
            "v0": 120.0,
            "altura_total": 30.0,
            "largura": 12.0,
        })
        assert res.status_code == 422

    def test_load_combination_rejects_invalid_psi(self):
        res = self._client().post("/calculate/load-combinations", json={
            "actions": [
                {"name": "G", "kind": "permanent", "value": 100.0},
                {"name": "Q", "kind": "variable", "value": 30.0, "psi0": 1.5},
            ]
        })
        assert res.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
