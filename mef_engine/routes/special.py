from fastapi import APIRouter
from pydantic import BaseModel
from radier_utils import sanitize_for_json
from typing import Dict, List

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
    from master_pedagogy import (
        build_stair_blackboard, 
        build_footing_blackboard, 
        build_reservoir_blackboard,
        build_beam_blackboard,
        build_column_blackboard,
        build_detailing_blackboard
    )
    from beam_detailing import BeamDetailer
    
    solver = SpecialElementsSolver()
    type = req.type
    params = req.params
    res = {}
    blackboard = None

    if type == "stair":
        res = solver.solve_stair(
            L_horizontal=params.get('L', 4.0), 
            H_vertical=params.get('H', 3.0), 
            load_kN_m2=params.get('q', 5.0), 
            thickness_cm=params.get('t', 15), 
            fck=params.get('fck', 30),
            width=params.get('width', 1.2),
        )
        blackboard = build_stair_blackboard(res)
        
    elif type == "reservoir":
        res = solver.solve_reservoir_wall(
            height=params.get('h', 3.0), 
            thickness_cm=params.get('t', 20), 
            fck=params.get('fck', 30)
        )
        blackboard = build_reservoir_blackboard(res)
        
    elif type == "beam":
        res = solver.solve_beam(
            L=params.get('L', 6.0),
            b=params.get('b', 0.20),
            h=params.get('h', 0.50),
            q_kN_m=params.get('q', 20.0),
            fck=params.get('fck', 30.0)
        )
        
        # Injetar Detalhamento Módulo 6-7
        det_summary = BeamDetailer.generate_detailing_summary(
            res, 
            b_m=params.get('b', 0.20), 
            h_m=params.get('h', 0.50), 
            fck=params.get('fck', 30.0)
        )
        res['detailing'] = det_summary
        
        # Blackboard de Dimensionamento + Blackboard de Detalhamento
        bb_dim = build_beam_blackboard(res)
        bb_det = build_detailing_blackboard(det_summary)
        
        # Unificar passos
        blackboard = bb_dim
        if bb_det:
            # Adicionar título separador se bb_dim existir
            blackboard['steps'].append({
                "title": "--- Detalhamento Executivo ---",
                "latex": r"\text{Módulos 6-7: Ancoragem e Decalagem}",
                "description": "Início do roteiro de detalhamento das armaduras."
            })
            blackboard['steps'].extend(bb_det)

    elif type == "column":
        res = solver.solve_column(
            b=params.get('b', 0.40),
            h=params.get('h', 0.40),
            Nd_kN=params.get('Nd', 1000.0),
            fck=params.get('fck', 30.0),
            L_free=params.get('L_free', 3.0)
        )
        blackboard = build_column_blackboard(res)

    elif type == "footing":
        res = solver.solve_footing(
            Nd_kN=params.get('Nd', 500.0),
            sigma_adm_kPa=params.get('sigma_adm', 300.0),
            ap=params.get('ap', 0.20),
            bp=params.get('bp', 0.40),
            fck=params.get('fck', 25.0)
        )
        blackboard = build_footing_blackboard(res)

    return {
        "success": True if res else False, 
        "result": res, 
        "pedagogical_steps": blackboard
    }

@router.post("/calculate/spt")
async def calculate_spt(req: Dict):
    from geotechnical_engine import GeotechnicalEngine
    from master_pedagogy import build_spt_blackboard
    
    spt_data = req.get('spt_data', [
        {"depth_m": 1.0, "nspt": 2, "soil_type": "Ateu"},
        {"depth_m": 2.0, "nspt": 5, "soil_type": "Areia fofa"},
        {"depth_m": 3.0, "nspt": 12, "soil_type": "Areia compacta"},
    ])
    
    engine = GeotechnicalEngine()
    res = engine.analyze_spt(spt_data)
    blackboard = build_spt_blackboard(res)
    
    return {
        "success": True,
        "result": res,
        "pedagogical_steps": {
            "mode": "MESTRE",
            "element": "geotechnics",
            "title": "Interpretacao de Sondagem SPT",
            "steps": blackboard
        }
    }

@router.post("/calculate/stability")
async def calculate_stability(req: Dict):
    from wind_engine import WindEngine, WindConfig
    from master_pedagogy import build_stability_blackboard
    
    cfg = WindConfig(
        v0=req.get('v0', 30.0),
        height=req.get('height', 30.0),
        width_x=req.get('width_x', 12.0)
    )
    
    engine = WindEngine()
    wind_data = engine.calculate_dynamic_pressure(cfg)
    gamma_z = engine.estimate_gamma_z(cfg.height, 10000, 50)
    
    res = {**wind_data, "gamma_z": gamma_z}
    blackboard = build_stability_blackboard(res)
    
    return {
        "success": True,
        "result": res,
        "pedagogical_steps": {
            "mode": "MESTRE",
            "element": "stability",
            "title": "Estabilidade Global e Vento",
            "steps": blackboard
        }
    }
