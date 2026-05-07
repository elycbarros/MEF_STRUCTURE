from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
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
        # 1. Reconstruir Modelo
        nodes = [FrameNode(**n) for n in req.nodes]
        members = []
        for m in req.members:
            s_data = m["section"]
            section = FrameSection(b=s_data["b"], h=s_data["h"], E=s_data.get("E", 2.5e10))
            members.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
            
        loads = [FrameLoad(**l) for l in req.loads]
        supports = {int(k): v for k, v in req.supports.items()}
        
        # 2. Motor
        engine = Frame3DEngine(nodes, members)
        
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

        return {
            "success": True,
            "mode": "MESTRE_PEDAGOGICAL",
            "displacements": res["displacements"],
            "efforts": efforts,
            "equilibrium_audit": equilibrium,
            "pedagogical_proofs": pedagogical_data,
            "memorial_citation": "Metodologia Professor Libânio - Análise de Estruturas via MEF."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
