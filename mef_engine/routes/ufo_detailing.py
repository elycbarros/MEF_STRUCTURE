from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ufo_detailing import UFODetailingOrchestrator
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from pydantic import BaseModel

router = APIRouter(prefix="/detailing", tags=["UFO - Detailing"])

class DetailingRequest(BaseModel):
    nodes: List[Dict]
    members: List[Dict]
    loads: List[Dict]
    supports: Dict[str, List[int]]
    fck: float = 30.0

@router.post("/global-summary")
async def get_global_detailing(req: DetailingRequest):
    """
    Gera o detalhamento executivo global para todo o edifício (Modo UFO).
    """
    try:
        # 1. Reconstruir e Resolver
        nodes = [FrameNode(**n) for n in req.nodes]
        members = []
        for m in req.members:
            s_data = m["section"]
            section = FrameSection(b=s_data["b"], h=s_data["h"], E=s_data.get("E", 2.5e10))
            members.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
            
        loads = [FrameLoad(**l) for l in req.loads]
        supports = {int(k): v for k, v in req.supports.items()}
        
        engine = Frame3DEngine(nodes, members)
        # Resolver em 1a ordem (ou 2a se o usuário preferir, mas para detalhamento baseamos em 1a + gama-z ou P-delta)
        solve_res = engine.solve(loads, supports, reduce_stiffness=True)
        
        # 2. Orquestrar Detalhamento
        orchestrator = UFODetailingOrchestrator(engine)
        detailing = orchestrator.generate_building_detailing(solve_res, fck=req.fck)
        
        return detailing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
