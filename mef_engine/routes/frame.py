"""
routes/frame.py — Rota Premium para Análise de Pórtico 3D.

Substitui o strucpy_adapter.py pelo frame_engine.py customizado com:
- Motor MEF 3D com 12 DOF por elemento (C1)
- P-Delta iterativo com Kg real (C1)
- γz calculado via deslocamentos nodais reais do pórtico (C2)
- Vento NBR 6123 distribuído automaticamente por pavimento
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import numpy as np

from schemas.frame import FrameRequest
from radier_utils import sanitize_for_json

router = APIRouter(prefix="/calculate", tags=["UFO - Frame"])


# NBR 6118 §15.7.3: Redução de rigidez automatizada no Frame3DEngine.


def _build_wind_loads(req: FrameRequest):
    """Distribui cargas de vento NBR 6123 nos nós de cada pavimento."""
    if req.wind_v0 <= 0 or req.n_floors_for_wind <= 0:
        return []

    from wind_engine import WindEngine, WindConfig
    cfg = WindConfig(v0=req.wind_v0, categoria=req.wind_categoria)

    wind_loads = []
    # Mapear nós por altura (z) — pegar o de menor x como barlavento
    node_by_floor: Dict[int, int] = {}  # z_index → node_id
    nodes_sorted = sorted(req.nodes, key=lambda n: (n.z, n.x))
    for n in nodes_sorted:
        floor_idx = round(n.z / req.floor_height_m)
        if floor_idx not in node_by_floor:
            node_by_floor[floor_idx] = n.id

    for floor_idx, node_id in node_by_floor.items():
        if floor_idx == 0:
            continue  # base não recebe vento
        z = floor_idx * req.floor_height_m
        q = WindEngine.calculate_dynamic_pressure(z, cfg)
        F = q * req.wind_cp * req.wind_width_m * req.floor_height_m
        wind_loads.append({"node_id": node_id, "Fx": F})

    return wind_loads


def _compute_gamma_z(disps_1st: dict, disps_2nd: dict, loads, nodes) -> float:
    """
    γz = δ_2ª / δ_1ª via deslocamentos horizontais nodais reais.
    Usa o nó de maior z (topo) como referência (NBR 6118 §15.5.2).
    """
    top_node = max(nodes, key=lambda n: n.z)
    d1 = abs(disps_1st.get(top_node.id, np.zeros(6))[0])
    d2 = abs(disps_2nd.get(top_node.id, np.zeros(6))[0])
    if d1 < 1e-9:
        return 1.0
    return round(float(d2 / d1), 4)


@router.post("/frame")
async def calculate_frame_premium(req: FrameRequest):
    """
    Análise de Pórtico 3D Premium.
    - Motor MEF 12-DOF customizado (substitui StrucPy)
    - P-Delta iterativo com matriz geométrica Kg
    - γz calculado via deslocamentos nodais reais
    - Vento NBR 6123 por pavimento (opcional)
    """
    from frame_engine import (
        FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
    )
    from frame_memorial import build_frame_memorial

    # 1. Preparar entrada (Redução de rigidez agora é automática no motor)
    members_input = req.members

    # 2. Construir objetos do motor
    nodes = [FrameNode(id=n.id, x=n.x, y=n.y, z=n.z) for n in req.nodes]
    members = [
        FrameMember(
            id=m.id, node_i=m.node_i, node_j=m.node_j,
            section=FrameSection(b=m.section.b, h=m.section.h, E=m.section.E, G=m.section.G)
        )
        for m in members_input
    ]
    loads = [FrameLoad(node_id=l.node_id, Fx=l.Fx, Fy=l.Fy, Fz=l.Fz,
                       Mx=l.Mx, My=l.My, Mz=l.Mz) for l in req.loads]

    # 3. Adicionar vento automático (NBR 6123)
    wind_extra = _build_wind_loads(req)
    for wl in wind_extra:
        loads.append(FrameLoad(**wl))

    # 4. Resolver
    engine = Frame3DEngine(nodes, members)
    supports = {int(k): v for k, v in req.supports.items()}

    # Análise 1ª Ordem
    res_1st = engine.solve(loads, supports, reduce_stiffness=req.nbr_stiffness_reduction)

    # Análise 2ª Ordem (P-Delta iterativo com Aitken Otimizado)
    if req.use_p_delta:
        res_2nd = engine.solve_p_delta(loads, supports, reduce_stiffness=req.nbr_stiffness_reduction)
    else:
        res_2nd = res_1st

    # 5. Esforços nas barras (N, Vy, Vz, T, My, Mz)
    efforts = engine.get_member_efforts(res_2nd["displacements"])
    
    # 6. Verificação de Equilíbrio Global (C3) com mesma rigidez da análise
    axials = {mid: eff["i"]["N"] * 1000.0 for mid, eff in efforts.items()}
    equilibrium = engine.check_equilibrium(loads, res_2nd["displacements"], supports, reduce_stiffness=req.nbr_stiffness_reduction, axial_loads=axials)

    # 7. γz via deslocamentos nodais reais (C2)
    gamma_z = _compute_gamma_z(res_1st["displacements"], res_2nd["displacements"], loads, req.nodes)

    # 8. Classificação NBR 6118 §15.5.2
    if gamma_z <= 1.10:
        stability_class = "NAO_SENSIVEL"
        stability_msg = "Efeitos de 2ª ordem desprezíveis (γz ≤ 1.10)"
    elif gamma_z <= 1.30:
        stability_class = "SENSIVEL"
        stability_msg = "2ª Ordem obrigatória — usar γz para amplificar esforços"
    else:
        stability_class = "INSTAVEL"
        stability_msg = "γz > 1.30 — estrutura instável, rever rigidez lateral"

    # 9. Deslocamentos para o frontend
    top_node = max(req.nodes, key=lambda n: n.z)
    top_disp_1st = res_1st["displacements"].get(top_node.id, np.zeros(6))
    top_disp_2nd = res_2nd["displacements"].get(top_node.id, np.zeros(6))

    all_disps = {
        str(nid): disp.tolist()
        for nid, disp in res_2nd["displacements"].items()
    }
    model_nodes = [
        {
            "node": n.id,
            "id": n.id,
            "x": n.x,
            "y": n.z,
            "z": n.y,
        }
        for n in nodes
    ]
    model_members = [
        {
            "index": m.id,
            "id": m.id,
            "Node1": m.node_i,
            "Node2": m.node_j,
            "b": m.section.b * 1000,
            "d": m.section.h * 1000,
            "Type": "Beam" if source.type == "beam" else "Column",
        }
        for m, source in zip(members, members_input)
    ]

    # 11. Resumo Final
    total_vertical_kN = sum(abs(l.Fz) for l in loads)
    
    # 9. Diagramas detalhados (C4)
    detailed_diagrams = engine.get_detailed_diagrams(res_2nd["displacements"], reduce_stiffness=req.nbr_stiffness_reduction, axial_loads=axials)
    
    response = {
        "success": True,
        "analysis_type": "PORTICO_3D_PREMIUM_P_DELTA" if req.use_p_delta else "PORTICO_3D_ELASTICO",
        "metadata": {
            "units": {
                "forces": "kN",
                "moments": "kNm",
                "displacements": "mm",
                "dimensions": "m"
            }
        },
        "nbr_stiffness_reduction": req.nbr_stiffness_reduction,
        "gamma_z": gamma_z,
        "total_vertical_load_kN": total_vertical_kN,
        "stability_class": stability_class,
        "stability_message": stability_msg,
        "top_node_id": top_node.id,
        "top_displacement_mm": round(abs(float(top_disp_2nd[0])) * 1000, 2),
        "nodal_displacements": all_disps,
        "member_efforts": efforts,
        "equilibrium": equilibrium,
        "model_3d": {
            "nodes": model_nodes,
            "members": model_members,
        },
        "diagrams": [
            {
                "memberId": int(mid),
                "points": points,
                "max_N": max(abs(p["N"]) for p in points),
                "max_V": max(max(abs(p["Vy"]), abs(p["Vz"])) for p in points),
                "max_M": max(max(abs(p["My"]), abs(p["Mz"])) for p in points),
            }
            for mid, points in detailed_diagrams.items()
        ],
    }
    response["memorial_markdown"] = build_frame_memorial(
        response,
        {"nodes": len(model_nodes), "members": len(model_members)},
    )

    return sanitize_for_json(response)
