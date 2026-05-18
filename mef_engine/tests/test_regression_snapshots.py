"""
tests/test_regression_snapshots.py
Testes de regressão numérica com snapshots e tolerâncias explícitas.
Usa a matriz de validação oficial (Phase 1 Roadmap).
"""
import pytest
import numpy as np
import sys, os

# Add root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.validation_matrix import VALIDATION_BENCHMARKS
from beam_solver import run_beam_analysis
from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine

def test_beam_regression_analytical():
    """Valida a viga contra o benchmark BEAM-001 (Isostática)."""
    benchmark = next(b for b in VALIDATION_BENCHMARKS["beam"] if b["id"] == "BEAM-001")
    inputs = benchmark["inputs"]
    expected = benchmark["expected"]
    
    # Executar solver real
    res = run_beam_analysis(
        L=inputs["L"],
        supports=[{"x": 0.0, "type": "pinned"}, {"x": inputs["L"], "type": "pinned"}],
        distributed_loads=[{"x_start": 0, "x_end": inputs["L"], "q_start": inputs["q"]}],
        b=inputs["bw"], h=inputs["h"], fck=30, nonlinear=False, include_self_weight=False,
        gamma_f=1.0
    )
    
    m_max_fem = res["design"]["M_max_pos_kNm"]
    m_max_analytical = expected["moment_max_kNm"]
    
    # Tolerância explícita: 0.1%
    assert m_max_fem == pytest.approx(m_max_analytical, rel=expected["tolerance_pct"]/100.0)

def test_frame_regression_stability():
    """Valida o pórtico contra o benchmark FRAME-001 (Estabilidade)."""
    benchmark = next(b for b in VALIDATION_BENCHMARKS["frame"] if b["id"] == "FRAME-001")
    inputs = benchmark["inputs"]
    expected = benchmark["expected"]
    
    sec = FrameSection(b=0.40, h=0.40)
    nodes = [FrameNode(1, 0, 0, 0), FrameNode(2, inputs["width"], 0, 0), 
             FrameNode(3, 0, 0, inputs["height"]), FrameNode(4, inputs["width"], 0, inputs["height"])]
    members = [FrameMember(1, 1, 3, sec), FrameMember(2, 2, 4, sec), FrameMember(3, 3, 4, sec)]
    
    engine = Frame3DEngine(nodes, members)
    loads = [FrameLoad(3, Fz=-inputs["vertical_load"]*1000/2, Fx=inputs["horizontal_load"]*1000/2),
             FrameLoad(4, Fz=-inputs["vertical_load"]*1000/2, Fx=inputs["horizontal_load"]*1000/2)]
    supports = {1: [0,1,2,3,4,5], 2: [0,1,2,3,4,5]}
    
    res_1 = engine.solve(loads, supports)
    res_2 = engine.solve_p_delta(loads, supports)
    
    d1 = abs(res_1["displacements"][3][0])
    d2 = abs(res_2["displacements"][3][0])
    gamma_z = d2 / d1
    
    # Tolerância para Gamma-Z
    assert gamma_z >= 1.0
    assert gamma_z == pytest.approx(expected["gamma_z_approx"], abs=0.1)
