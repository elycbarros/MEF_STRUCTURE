from fastapi import APIRouter
from pydantic import BaseModel
from radier_utils import sanitize_for_json

router = APIRouter(tags=["Special Solvers"])

@router.post("/check/compliance")
async def check_compliance(caa: int, trrf: int, width_cm: float):
    from durability_checker import DurabilityConfig, DurabilityChecker
    cfg = DurabilityConfig(caa=caa, trrf=trrf)
    checker = DurabilityChecker()
    cover = checker.get_min_cover(cfg)
    fire_ok = checker.check_fire_resistance(width_cm, cfg)
    return {"success": True, "cover_mm": cover, "fire_ok": fire_ok}

@router.post("/optimize/structural")
async def optimize_structural(member_length: float = 5.0):
    from structural_optimizer import StructuralOptimizer
    opt = StructuralOptimizer()
    res = opt.optimize_member(length=member_length)
    return {"success": True, "optimization": res}

class SpecialElementRequest(BaseModel):
    type: str
    params: dict = {}

@router.post("/calculate/special-elements")
async def calculate_special(req: SpecialElementRequest):
    from special_elements import SpecialElementsSolver
    solver = SpecialElementsSolver()
    type = req.type
    params = req.params
    if type == "stair":
        res = solver.solve_stair(
            L_horizontal=params.get('L', 4.0), 
            H_vertical=params.get('H', 3.0), 
            load_kN_m2=params.get('q', 5.0), 
            thickness_cm=params.get('t', 15), 
            fck=params.get('fck', 30),
            width=params.get('width', 1.2),
        )
        return {"success": True, "result": res}
    elif type == "reservoir":
        res = solver.solve_reservoir_wall(
            height=params.get('h', 3.0), 
            thickness_cm=params.get('t', 20), 
            fck=params.get('fck', 30)
        )
        return {"success": True, "result": res}
    elif type == "beam":
        res = solver.solve_beam(
            L=params.get('L', 6.0),
            b=params.get('b', 0.20),
            h=params.get('h', 0.50),
            q_kN_m=params.get('q', 20.0),
            fck=params.get('fck', 30.0)
        )
        return {"success": True, "result": res}
    elif type == "column":
        res = solver.solve_column(
            b=params.get('b', 0.40),
            h=params.get('h', 0.40),
            Nd_kN=params.get('Nd', 1000.0),
            fck=params.get('fck', 30.0),
            L_free=params.get('L_free', 3.0)
        )
        return {"success": True, "result": res}
    return {"success": False, "error": "Tipo desconhecido"}
