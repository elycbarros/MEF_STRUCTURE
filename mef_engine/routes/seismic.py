from fastapi import APIRouter, HTTPException
from typing import List, Dict
from seismic_engine import SeismicEngine
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from pydantic import BaseModel

router = APIRouter(prefix="/seismic", tags=["UFO - Seismic"])

class SeismicAnalysisRequest(BaseModel):
    nodes: List[Dict]
    members: List[Dict]
    supports: Dict[str, List[int]]
    soil_class: str = "D"
    seismic_zone: int = 1
    num_modes: int = 10
    R: float = 1.0 # Ductilidade
    I: float = 1.0 # Importância

@router.post("/analyze")
async def analyze_seismic(req: SeismicAnalysisRequest):
    try:
        # 1. Reconstruir Modelo
        nodes = [FrameNode(**n) for n in req.nodes]
        members = []
        for m in req.members:
            s_data = m["section"]
            section = FrameSection(b=s_data["b"], h=s_data["h"], E=s_data.get("E", 2.5e10))
            members.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
            
        supports = {int(k): v for k, v in req.supports.items()}
        
        # 2. Motores
        engine_3d = Frame3DEngine(nodes, members)
        seismic = SeismicEngine(soil_class=req.soil_class, seismic_zone=req.seismic_zone)
        
        # 3. Executar RSA
        results = seismic.run_rsa_analysis(engine_3d, supports, num_modes=req.num_modes, R=req.R, I=req.I)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
