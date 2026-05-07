from fastapi import APIRouter, HTTPException
from typing import List, Dict
from nonlinear_ssi import NonLinearPileSolver, PYCurve
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from pydantic import BaseModel

router = APIRouter(prefix="/ssi", tags=["UFO - Geotechnics"])

class SSINonLinearRequest(BaseModel):
    nodes: List[Dict]
    members: List[Dict]
    loads: List[Dict]
    supports: Dict[str, List[int]]
    pile_configs: Dict[str, Dict] # {node_id: {soil_type: 'sand', diameter: 0.8, ...}}
    max_iter: int = 15
    tol: float = 0.01

@router.post("/pile-nonlinear")
async def analyze_pile_nonlinear(req: SSINonLinearRequest):
    """
    Análise Não-Linear de Estacas via curvas p-y (Modo UFO).
    """
    try:
        nodes = [FrameNode(**n) for n in req.nodes]
        members = []
        for m in req.members:
            s_data = m["section"]
            section = FrameSection(b=s_data["b"], h=s_data["h"], E=s_data.get("E", 2.5e10))
            members.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
            
        loads = [FrameLoad(**l) for l in req.loads]
        supports = {int(k): v for k, v in req.supports.items()}
        
        engine = Frame3DEngine(nodes, members)
        
        # Criar curvas p-y
        curves = {}
        for nid_str, config in req.pile_configs.items():
            curves[int(nid_str)] = PYCurve(**config)
            
        solver = NonLinearPileSolver(engine)
        results = solver.solve_with_py(loads, supports, curves, max_iter=req.max_iter, tol=req.tol)
        
        return {
            "success": results["converged"],
            "iterations": results["iterations"],
            "displacements": results["res"]["displacements"],
            "final_springs_kN_m": results["final_springs"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
