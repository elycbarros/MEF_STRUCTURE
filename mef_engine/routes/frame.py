"""
routes/frame.py — Rota Premium para Análise de Pórtico 3D.

Substitui o strucpy_adapter.py pelo frame_engine.py customizado com:
- Motor MEF 3D com 12 DOF por elemento (C1)
- P-Delta iterativo com Kg real (C1)
- γz calculado via deslocamentos nodais reais do pórtico (C2)
- Vento NBR 6123 distribuído automaticamente por pavimento
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
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


def _run_frame_analysis_logic(req: FrameRequest, job_id: Optional[str] = None):
    """Lógica central de análise desacoplada para suportar execução síncrona e assíncrona."""
    try:
        if job_id:
            from jobs import job_manager, JobStatus
            job_manager.update_job(job_id, status=JobStatus.RUNNING, progress=10)

        from frame_engine import (
            FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
        )
        from frame_memorial import build_frame_memorial

        # 1. Preparar objetos
        nodes = [FrameNode(id=n.id, x=n.x, y=n.y, z=n.z) for n in req.nodes]
        members = [
            FrameMember(
                id=m.id, node_i=m.node_i, node_j=m.node_j,
                section=FrameSection(b=m.section.b, h=m.section.h, E=m.section.E, G=m.section.G)
            )
            for m in req.members
        ]
        loads = [FrameLoad(node_id=l.node_id, Fx=l.Fx, Fy=l.Fy, Fz=l.Fz,
                           Mx=l.Mx, My=l.My, Mz=l.Mz) for l in req.loads]

        if job_id: job_manager.update_job(job_id, progress=30)

        # 2. Vento Automático
        wind_extra = _build_wind_loads(req)
        for wl in wind_extra:
            loads.append(FrameLoad(**wl))

        # 3. Resolver
        engine = Frame3DEngine(nodes, members)
        supports = {int(k): v for k, v in req.supports.items()}

        if job_id: job_manager.update_job(job_id, progress=50)

        # Análise 1ª Ordem
        res_1st = engine.solve(loads, supports, reduce_stiffness=req.nbr_stiffness_reduction)

        if job_id: job_manager.update_job(job_id, progress=70)

        # Análise 2ª Ordem
        if req.use_p_delta:
            res_2nd = engine.solve_p_delta(loads, supports, reduce_stiffness=req.nbr_stiffness_reduction)
        else:
            res_2nd = res_1st

        if job_id: job_manager.update_job(job_id, progress=90)

        # 4. Esforços e Verificações
        efforts = engine.get_member_efforts(res_2nd["displacements"])
        axials = {mid: eff["i"]["N"] * 1000.0 for mid, eff in efforts.items()}
        equilibrium = engine.check_equilibrium(loads, res_2nd["displacements"], supports, reduce_stiffness=req.nbr_stiffness_reduction, axial_loads=axials)
        gamma_z = _compute_gamma_z(res_1st["displacements"], res_2nd["displacements"], loads, req.nodes)

        # 5. Formatar Resposta
        stability_class = "NAO_SENSIVEL" if gamma_z <= 1.10 else ("SENSIVEL" if gamma_z <= 1.30 else "INSTAVEL")
        
        top_node = max(req.nodes, key=lambda n: n.z)
        top_disp_2nd = res_2nd["displacements"].get(top_node.id, np.zeros(6))

        all_disps = {str(nid): disp.tolist() for nid, disp in res_2nd["displacements"].items()}
        detailed_diagrams = engine.get_detailed_diagrams(res_2nd["displacements"], reduce_stiffness=req.nbr_stiffness_reduction, axial_loads=axials)
        
        response = {
            "success": True,
            "analysis_type": "PORTICO_3D_PREMIUM_P_DELTA" if req.use_p_delta else "PORTICO_3D_ELASTICO",
            "gamma_z": gamma_z,
            "stability_class": stability_class,
            "top_displacement_mm": round(abs(float(top_disp_2nd[0])) * 1000, 2),
            "nodal_displacements": all_disps,
            "member_efforts": efforts,
            "equilibrium": equilibrium,
            "diagrams": [
                {
                    "memberId": int(mid),
                    "points": points,
                    "max_N": max(abs(p["N"]) for p in points) if points else 0,
                }
                for mid, points in detailed_diagrams.items()
            ],
        }
        
        sanitized = sanitize_for_json(response)
        if job_id:
            job_manager.update_job(job_id, status=JobStatus.COMPLETED, progress=100, result=sanitized)
        return sanitized

    except Exception as e:
        if job_id:
            job_manager.update_job(job_id, status=JobStatus.FAILED, error=str(e))
        raise e


@router.post("/frame/modal")
async def start_modal_analysis(req: FrameRequest, background_tasks: BackgroundTasks):
    """Inicia análise modal assíncrona (NBR 6118 - Dinâmica)."""
    from jobs import job_manager, JobStatus
    job_id = job_manager.create_job("MODAL_ANALYSIS")
    
    def run_modal():
        try:
            job_manager.update_job(job_id, status=JobStatus.RUNNING, progress=10)
            from frame_engine import FrameNode, FrameMember, FrameSection, Frame3DEngine
            nodes = [FrameNode(id=n.id, x=n.x, y=n.y, z=n.z) for n in req.nodes]
            members = [
                FrameMember(id=m.id, node_i=m.node_i, node_j=m.node_j,
                            section=FrameSection(b=m.section.b, h=m.section.h, E=m.section.E, G=m.section.G))
                for m in req.members
            ]
            engine = Frame3DEngine(nodes, members)
            supports = {int(k): v for k, v in req.supports.items()}
            job_manager.update_job(job_id, progress=50)
            res = engine.solve_modal(n_modes=12, supports=supports)
            job_manager.update_job(job_id, status=JobStatus.COMPLETED, progress=100, result=res)
        except Exception as e:
            job_manager.update_job(job_id, status=JobStatus.FAILED, error=str(e))

    background_tasks.add_task(run_modal)
    return {"job_id": job_id, "status": "queued"}


@router.get("/frame/modal/{job_id}")
async def get_modal_status(job_id: str):
    """Consulta resultados da análise modal."""
    from jobs import job_manager
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job


@router.post("/frame")
async def calculate_frame_premium(req: FrameRequest, request: Request):
    """Análise de Pórtico 3D (Síncrona). Suporta MsgPack via Accept header."""
    res = _run_frame_analysis_logic(req)
    
    accept = request.headers.get("Accept")
    if accept == "application/x-msgpack":
        from api import MsgPackResponse
        return MsgPackResponse(res)
    return res


@router.post("/frame/async")
async def calculate_frame_async(req: FrameRequest, background_tasks: BackgroundTasks):
    """Análise de Pórtico 3D (Assíncrona)."""
    from jobs import job_manager
    job_id = job_manager.create_job("FRAME_3D_ANALYSIS")
    background_tasks.add_task(_run_frame_analysis_logic, req, job_id)
    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
async def get_frame_job_status(job_id: str, request: Request):
    """Consulta status e resultados. Suporta MsgPack via Accept header."""
    from jobs import job_manager
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    accept = request.headers.get("Accept")
    if accept == "application/x-msgpack" and job.get("result"):
        from api import MsgPackResponse
        return MsgPackResponse(job)
    return job
