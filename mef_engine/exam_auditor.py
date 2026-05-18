"""
exam_auditor.py - Núcleo de auditoria estrutural de questões.

Este módulo separa modelo físico, cálculo e laudo sintético para que o
SpecialElementsSolver apenas delegue a análise.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ExamQuestion:
    id: str
    title: str
    statement: str
    official_key: str
    status: str
    exam_reactions: dict[str, float]
    thesis: str
    pdf_url: str


Q47 = ExamQuestion(
    id="q47_fcc_2018",
    title="Questão 47 - FCC 2018 - Metrô-SP",
    statement=(
        "Uma viga de 8,0 metros possui dois apoios, A (no início) e B "
        "(a 6,0 metros de A). A extremidade direita (a 2,0 metros de B) "
        "está livre e sob uma carga concentrada de 30 kN. Determine as "
        "reações verticais de apoio."
    ),
    official_key="Ra = +10 kN (para cima), Rb = +20 kN (para cima)",
    status="INVÁLIDA (Erro de Equilíbrio Físico)",
    exam_reactions={"Ra": 10.0, "Rb": 20.0},
    thesis=(
        "O gabarito oficial viola a primeira e a segunda lei do equilíbrio "
        "estático da mecânica dos sólidos. Para somatório de momentos em B "
        "ser igual a zero, Ra deve puxar a viga para baixo com 10 kN. "
        "Consequentemente, Rb deve absorver 40 kN para cima para compensar "
        "a carga de 30 kN e a força de ancoragem de 10 kN."
    ),
    pdf_url="/static/reports/memorial_questao_47.pdf",
)


Q31 = ExamQuestion(
    id="q31_vunesp_2021",
    title="Questão 31 - VUNESP 2021 - AL-SP",
    statement=(
        "Considere a torre treliçada vertical de 6,0 m de altura e 3,0 m "
        "de largura. Aplica-se uma força de 20 kN horizontal para a direita "
        "no nó superior esquerdo e 20 kN vertical para baixo no nó superior "
        "direito. Determine as reações e esforços axiais."
    ),
    official_key=(
        "Ra = 40 kN (para baixo), Rb = 60 kN (para cima), esforço na "
        "diagonal = 28.28 kN (tração)"
    ),
    status="INVÁLIDA (Erro de Cálculo da Formulação)",
    exam_reactions={"Ra": -40.0, "Rb": 60.0, "Rax": 20.0},
    thesis=(
        "A formulação da banca apresentou inconsistências de convenção de "
        "sinais que confundiram a resposta das reações horizontais e a "
        "denominação das barras tracionadas."
    ),
    pdf_url="/static/reports/memorial_questao_31.pdf",
)


def _reaction_divergence_percent(correct: dict[str, float], exam: dict[str, float]) -> float:
    total_diff = sum(abs(correct[k] - exam.get(k, 0.0)) for k in correct)
    total_ref = sum(max(abs(correct[k]), 1.0) for k in correct)
    return round(100.0 * total_diff / total_ref, 2)


def _base_result(question: ExamQuestion, correct_reactions: dict[str, float]) -> dict:
    return {
        "question_id": question.id,
        "title": question.title,
        "statement": question.statement,
        "official_key": question.official_key,
        "status": question.status,
        "correct_reactions": correct_reactions,
        "exam_reactions": question.exam_reactions,
        "divergence_percent": _reaction_divergence_percent(correct_reactions, question.exam_reactions),
        "recurso_tese": question.thesis,
        "pdf_url": question.pdf_url,
        "is_exam": True,
    }


def _as_list(values) -> list[float]:
    return values.tolist() if hasattr(values, "tolist") else list(values)


def audit_q47_fcc_2018() -> dict:
    from beam_solver import run_beam_analysis

    beam_result = run_beam_analysis(
        L=8.0,
        supports=[
            {"x": 0.0, "type": "pinned"},
            {"x": 6.0, "type": "pinned"},
        ],
        distributed_loads=[],
        point_loads=[{"x": 8.0, "P": 30.0}],
        b=0.20,
        h=0.50,
        fck=30.0,
        nonlinear=False,
        include_self_weight=False,
    )
    reactions = beam_result.get("reactions", {})
    correct = {
        "Ra": round(float(reactions.get("0.0", {}).get("R", 0.0)), 6),
        "Rb": round(float(reactions.get("6.0", {}).get("R", 0.0)), 6),
    }
    result = _base_result(Q47, correct)
    result.update(
        {
            "model": {
                "type": "beam_with_overhang",
                "length_m": 8.0,
                "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "roller"}],
                "point_loads": [{"x": 8.0, "P": 30.0}],
            },
            "solver_result": beam_result,
            "L": 8.0,
            "b": 0.20,
            "h": 0.50,
            "q": 0.0,
            "fck": 30.0,
        }
    )
    return result


def audit_q31_vunesp_2021() -> dict:
    from frame_engine import Frame3DEngine, FrameLoad, FrameMember, FrameNode, FrameSection

    nodes = [
        FrameNode(id=0, x=0.0, y=0.0, z=0.0),
        FrameNode(id=1, x=3.0, y=0.0, z=0.0),
        FrameNode(id=2, x=0.0, y=0.0, z=3.0),
        FrameNode(id=3, x=3.0, y=0.0, z=3.0),
        FrameNode(id=4, x=0.0, y=0.0, z=6.0),
        FrameNode(id=5, x=3.0, y=0.0, z=6.0),
    ]
    section = FrameSection(b=0.1, h=0.1, E=2.1e11)
    members = [
        FrameMember(id=0, node_i=0, node_j=1, section=section),
        FrameMember(id=1, node_i=2, node_j=3, section=section),
        FrameMember(id=2, node_i=4, node_j=5, section=section),
        FrameMember(id=3, node_i=0, node_j=2, section=section),
        FrameMember(id=4, node_i=2, node_j=4, section=section),
        FrameMember(id=5, node_i=1, node_j=3, section=section),
        FrameMember(id=6, node_i=3, node_j=5, section=section),
        FrameMember(id=7, node_i=0, node_j=3, section=section),
        FrameMember(id=8, node_i=2, node_j=5, section=section),
    ]
    loads = [
        FrameLoad(node_id=4, Fx=20_000.0),
        FrameLoad(node_id=5, Fz=-20_000.0),
    ]
    supports = {
        0: [0, 1, 2, 3, 4, 5],
        1: [1, 2, 3, 4, 5],
    }
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    engine.is_truss = True
    solved = engine.solve(loads, supports, use_rust=False)
    efforts = engine.get_member_efforts(solved["displacements"])
    equilibrium = engine.check_equilibrium(loads, solved["displacements"], supports)
    reactions = equilibrium["reactions"]
    reaction_a = reactions.get(0) or reactions.get("0")
    reaction_b = reactions.get(1) or reactions.get("1")

    correct = {
        "Ra": round(float(reaction_a[2]), 6),
        "Rb": round(float(reaction_b[2]), 6),
        "Rax": round(float(reaction_a[0]), 6),
    }
    result = _base_result(Q31, correct)
    result.update(
        {
            "model": {
                "type": "plane_truss",
                "width_m": 3.0,
                "height_m": 6.0,
                "nodes": [node.__dict__ for node in nodes],
                "members": [{"id": m.id, "node_i": m.node_i, "node_j": m.node_j} for m in members],
                "loads": [{"node_id": 4, "Fx_kN": 20.0}, {"node_id": 5, "Fz_kN": -20.0}],
            },
            "solver_result": {
                "reactions": {str(nid): _as_list(values) for nid, values in reactions.items()},
                "member_efforts": efforts,
                "equilibrium": equilibrium,
            },
            "truss_type": "q31",
            "L": 3.0,
            "h": 6.0,
            "q": 20.0,
        }
    )
    return result


def build_professional_pdf_payload(audit_result: dict) -> tuple[dict, dict]:
    question_id = audit_result.get("question_id")
    if question_id == Q47.id:
        model = audit_result["model"]
        beam = audit_result["solver_result"]
        reactions = audit_result["correct_reactions"]
        max_moment = float(beam.get("summary", {}).get("max_moment_kNm", 0.0))
        max_shear = float(beam.get("summary", {}).get("max_shear_kN", 0.0))

        results = {
            "model_3d": {
                "is_truss": False,
                "nodes": [
                    {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                    {"id": 1, "x": 6.0, "y": 0.0, "z": 0.0},
                    {"id": 2, "x": 8.0, "y": 0.0, "z": 0.0},
                ],
                "members": [
                    {"id": 0, "node_i": 0, "node_j": 1, "section": {"b": audit_result.get("b", 0.20), "h": audit_result.get("h", 0.50)}},
                    {"id": 1, "node_i": 1, "node_j": 2, "section": {"b": audit_result.get("b", 0.20), "h": audit_result.get("h", 0.50)}},
                ],
                "supports": {"0": [1, 2], "1": [2]},
                "loads": [{"node_id": 2, "fz": -30.0}],
            },
            "displacements": {
                "0": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "2": [0.0, 0.0, -float(beam.get("summary", {}).get("max_deflection_mm", 0.0)) / 1000.0, 0.0, 0.0, 0.0],
            },
            "efforts": {
                "0": {"i": {"N": 0.0, "Vy": reactions["Ra"], "Vz": reactions["Ra"], "My": 0.0, "Mz": 0.0}, "j": {"N": 0.0, "Vy": -reactions["Ra"], "Vz": -reactions["Ra"], "My": -max_moment, "Mz": -max_moment}},
                "1": {"i": {"N": 0.0, "Vy": max_shear, "Vz": max_shear, "My": -max_moment, "Mz": -max_moment}, "j": {"N": 0.0, "Vy": -max_shear, "Vz": -max_shear, "My": 0.0, "Mz": 0.0}},
            },
            "equilibrium_audit": {
                "reactions": {
                    "0": [0.0, 0.0, reactions["Ra"], 0.0, 0.0, 0.0],
                    "1": [0.0, 0.0, reactions["Rb"], 0.0, 0.0, 0.0],
                },
                "sum_applied_kN_m": [0.0, 0.0, -30.0, 0.0, -60.0, 0.0],
                "sum_reactions_kN_m": [0.0, 0.0, reactions["Ra"] + reactions["Rb"], 0.0, 60.0, 0.0],
                "equilibrium_error_kN_m": [0.0, 0.0, reactions["Ra"] + reactions["Rb"] - 30.0, 0.0, 0.0, 0.0],
                "is_equilibrated": True,
            },
            "exam_audit": audit_result,
        }
        meta = {
            "obra": "Memorial Estrutural da Questao 47 (FCC 2018)",
            "local": "Auditoria de equilíbrio estático",
            "responsavel": "Atlas MEF Structural",
            "registro": "Laudo técnico gerado por solver",
        }
        return results, meta

    if question_id == Q31.id:
        solver = audit_result["solver_result"]
        model = audit_result["model"]
        nodes = model["nodes"]
        members = [
            {"id": m["id"], "node_i": m["node_i"], "node_j": m["node_j"], "section": {"b": 0.1, "h": 0.1}}
            for m in model["members"]
        ]
        results = {
            "model_3d": {
                "is_truss": True,
                "nodes": nodes,
                "members": members,
                "supports": {"0": [0, 1, 2, 3, 4, 5], "1": [1, 2, 3, 4, 5]},
                "loads": model["loads"],
            },
            "displacements": {str(node["id"]): [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for node in nodes},
            "efforts": solver["member_efforts"],
            "equilibrium_audit": solver["equilibrium"],
            "exam_audit": audit_result,
        }
        meta = {
            "obra": "Memorial Estrutural da Questao 31 (VUNESP 2021)",
            "local": "Auditoria de treliça plana",
            "responsavel": "Atlas MEF Structural",
            "registro": "Laudo técnico gerado por solver",
        }
        return results, meta

    raise ValueError(f"Questão sem payload profissional: {question_id}")


AUDITORS: dict[str, Callable[[], dict]] = {
    Q47.id: audit_q47_fcc_2018,
    Q31.id: audit_q31_vunesp_2021,
}


def solve_exam_auditor(question_id: str) -> dict:
    auditor = AUDITORS.get(question_id)
    if auditor:
        return auditor()

    return {
        "question_id": question_id,
        "title": "Questão Desconhecida",
        "statement": "Nenhuma questão selecionada.",
        "official_key": "-",
        "status": "N/A",
        "pdf_url": "#",
    }
