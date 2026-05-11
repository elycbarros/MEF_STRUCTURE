from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from master_pedagogy import build_structural_blackboard
from pydantic import BaseModel

router = APIRouter(prefix="/frame", tags=["Mestre - Frames"])

class MestreFrameRequest(BaseModel):
    nodes: List[Dict]
    members: List[Dict]
    loads: List[Dict]
    supports: Dict[str, List[int]]
    show_matrix_proof: bool = True

@router.post("/analyze")
async def analyze_mestre_frame(req: MestreFrameRequest):
    """
    Análise Pedagógica de Pórticos (Modo Mestre).
    Exibe montagem de matrizes e equilíbrio de nós para fins didáticos.
    """
    try:
        # 1. Reconstruir Modelo (Filtrando campos extras para evitar erros de dataclass)
        nodes = [FrameNode(id=n['id'], x=n['x'], y=n['y'], z=n['z']) for n in req.nodes]
        members = []
        for m in req.members:
            s_data = m["section"]
            section = FrameSection(b=s_data["b"], h=s_data["h"], E=s_data.get("E", 2.5e10))
            members.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
            
        loads = [
            FrameLoad(
                node_id=l['node_id'], 
                Fx=l.get('Fx', 0.0), Fy=l.get('Fy', 0.0), Fz=l.get('Fz', 0.0),
                Mx=l.get('Mx', 0.0), My=l.get('My', 0.0), Mz=l.get('Mz', 0.0)
            ) for l in req.loads
        ]
        supports = {int(k): v for k, v in req.supports.items()}
        
        # 2. Motor (Desabilitar Rust no modo pedagógico para garantir estabilidade máxima em modelos pequenos)
        engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
        
        # 3. Análise (1a Ordem - Mestre é sempre 1a ordem por padrão pedagógico)
        res = engine.solve(loads, supports, reduce_stiffness=False)
        
        # 4. Esforços e Provas Pedagógicas
        efforts = engine.get_member_efforts(res["displacements"])
        equilibrium = engine.check_equilibrium(loads, res["displacements"], supports)
        
        pedagogical_data = {}
        if req.show_matrix_proof:
            # Pegar uma barra de exemplo para mostrar a matriz local (K_local)
            if members:
                m_ex = members[0]
                T, L = engine._get_transformation(m_ex)
                k_loc = engine._get_k_local(m_ex, L)
                pedagogical_data["sample_k_local"] = k_loc.tolist()
                pedagogical_data["sample_member_id"] = m_ex.id
                pedagogical_data["explanation"] = "Matriz de Rigidez Local (12x12) baseada no Método dos Deslocamentos."

        # 5. Gerar Memorial Pedagógico
        payload_dict = {
            "nodes": req.nodes,
            "members": req.members,
            "loads": req.loads,
            "supports": req.supports
        }
        res_to_memorial = {
            "pedagogical_proofs": pedagogical_data,
            "equilibrium_audit": equilibrium
        }
        memorial = build_structural_blackboard("frame", res_to_memorial, payload_dict)

        return {
            "success": True,
            "mode": "MESTRE_PEDAGOGICAL",
            "displacements": res["displacements"],
            "model_3d": req.model_dump(),
            "efforts": efforts,
            "equilibrium_audit": equilibrium,
            "top_displacement_mm": max(abs(d[0]) for d in res["displacements"].values()) * 1000,
            "pedagogical_proofs": pedagogical_data,
            "pedagogical_steps": memorial["steps"],
            "memorial_markdown": "# Memorial de Calculo Padronizado - Portico 3D Premium\n\nAnalise realizada via Metodo de Elementos Finitos (Matriz de Rigidez 12x12).",
            "calculation_trace": {
                "requested_type": "frame",
                "solver_module": "frame_engine",
                "blackboard_builder": "frame_pedagogy",
                "classical_check": False,
                "mef_check": True
            },
            "memorial_citation": "Metodologia Professor Libânio - Análise de Estruturas via MEF."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
