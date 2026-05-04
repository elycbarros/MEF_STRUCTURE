from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import structural_core_rs

router = APIRouter(tags=["Structural Rust Core"])

class SpanInputRS(BaseModel):
    length: float
    e_gpa: float
    inertia_m4: float

class SolverRequestRS(BaseModel):
    spans: List[SpanInputRS]
    point_loads: List[dict] # {node_idx: int, value: float}
    fixed_dofs: List[int]

class TensionProRequest(BaseModel):
    fck: float
    p0: float
    mu: float
    k: float
    x: float
    theta: float

@router.post("/solve/beam")
async def solve_beam_rs(request: SolverRequestRS):
    try:
        n_spans = len(request.spans)
        solver = structural_core_rs.BeamSolver(n_spans)
        
        for i, span in enumerate(request.spans):
            solver.add_span_stiffness(i, i+1, span.length, span.e_gpa * 1e6, span.inertia_m4)
            
        for load in request.point_loads:
            solver.add_point_load(load['node_idx'], load['value'])
            
        displacements = solver.solve(request.fixed_dofs)
        
        return {
            "status": "success",
            "matrix_size": solver.get_matrix_size(),
            "displacements": displacements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tension-pro/friction-loss")
async def calculate_friction(request: TensionProRequest):
    try:
        tp = structural_core_rs.TensionPro(request.fck)
        p_x = tp.calculate_friction_loss(
            request.p0, request.mu, request.k, request.x, request.theta
        )
        return {"p_x": p_x}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
