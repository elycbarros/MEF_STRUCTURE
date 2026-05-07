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
        build_stairs_blackboard, 
        build_footing_blackboard, 
        build_beam_blackboard,
        build_column_blackboard,
        build_column_detailing_blackboard,
        build_concrete_wall_blackboard,
        build_retaining_wall_blackboard,
        build_elevated_reservoir_blackboard,
        build_corbel_blackboard,
        build_gerber_tooth_blackboard,
        build_deep_beam_blackboard,
        build_helical_stairs_blackboard
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
        blackboard = build_stairs_blackboard(res)
        
    elif type == "beam":
        res = solver.solve_beam(
            L=params.get('L', 6.0),
            b=params.get('b', 0.20),
            h=params.get('h', 0.50),
            q_kN_m=params.get('q', 20.0),
            fck=params.get('fck', 30.0),
            asymmetric_offset=params.get('asymmetric_offset', 0.0)
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
        bb_dim = build_beam_blackboard(res, params)
        bb_det = build_column_detailing_blackboard(det_summary) # Reusando p/ exemplo
        
        # Unificar passos
        blackboard = bb_dim
        if bb_det:
            # Adicionar título separador se bb_dim existir
            blackboard['steps'].append({
                "id": "det-sep",
                "title": "--- Detalhamento Executivo ---",
                "formula_latex": r"\text{Módulos 6-7: Ancoragem e Decalagem}",
                "result_latex": "",
                "explanation": "Início do roteiro de detalhamento das armaduras.",
                "norm_ref": "NBR 6118",
                "status": "INFO"
            })
            blackboard['steps'].extend(bb_det['steps'])

    elif type == "column":
        res = solver.solve_column(
            b=params.get('b', 0.40),
            h=params.get('h', 0.40),
            Nd_kN=params.get('Nd', 1000.0),
            fck=params.get('fck', 30.0),
            L_free=params.get('L_free', 3.0),
            Mxd_kNm=params.get('Mxd', 0.0),
            Myd_kNm=params.get('Myd', 0.0),
            caa=params.get('caa', 2)
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
    
    elif type == "concrete_wall":
        from engines.column_engine import ColumnEngine
        res = ColumnEngine.solve_concrete_wall(
            nd_kN_m=params.get('Nd', 500.0),
            h_wall=params.get('h', 2.8),
            t_wall=params.get('t', 0.12),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_concrete_wall_blackboard(res)

    elif type == "retaining_wall":
        res = solver.solve_retaining_wall(
            h=params.get('h_wall', 4.0),
            gamma=params.get('gamma_soil', 18.0),
            phi=params.get('phi_soil', 30.0),
            weight=params.get('weight_wall', 120.0),
            base=params.get('b_base', 2.5),
            surcharge=params.get('surcharge', 0.0)
        )
        blackboard = build_retaining_wall_blackboard(res)

    elif type == "reservoir":
        res = solver.solve_reservoir(
            length=params.get('length', 5.0),
            width=params.get('width', 3.0),
            depth=params.get('depth', 3.0)
        )
        blackboard = build_elevated_reservoir_blackboard(res)

    elif type == "corbel":
        res = solver.solve_corbel(
            fd_kN=params.get('fd_kN', 200.0),
            a_dist=params.get('a_dist', 0.25),
            d_eff=params.get('d_eff', 0.45),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_corbel_blackboard(res)

    elif type == "gerber_tooth":
        res = solver.solve_gerber_tooth(
            vd_kN=params.get('vd_kN', 150.0),
            hd_kN=params.get('hd_kN', 30.0),
            a_dist=params.get('a_dist', 0.15),
            d_eff=params.get('d_eff', 0.40),
            b_width=params.get('b_width', 0.20),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_gerber_tooth_blackboard(res)

    elif type == "deep_beam":
        res = solver.solve_deep_beam(
            fd_kN_m=params.get('L', 100.0), # Simplificado: usando L como carga para teste
            l_span=params.get('L', 4.0),
            height=params.get('h', 3.0)
        )
        blackboard = build_deep_beam_blackboard(res)

    elif type == "helical_stairs":
        res = solver.solve_helical_stairs(
            radius=params.get('radius', 2.5),
            angle_total_deg=params.get('angle_total_deg', 180.0),
            h_step=params.get('h_step', 0.18),
            thick=params.get('thick', 0.15),
            q_acid=params.get('q_acid', 3.0)
        )
        blackboard = build_helical_stairs_blackboard(res)

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
        "pedagogical_steps": blackboard
    }

@router.post("/calculate/stability-mestre")
async def calculate_stability_mestre(req: Dict):
    from wind_engine import WindEngine, WindConfig
    from master_pedagogy import build_stability_blackboard
    
    v0 = float(req.get('v0', 30.0))
    height = float(req.get('height', 30.0))
    width_x = float(req.get('width_x', 12.0))
    
    cfg = WindConfig(
        v0=v0,
        height=height,
        width_x=width_x
    )
    
    engine = WindEngine()
    wind_data = engine.calculate_dynamic_pressure(cfg)
    gamma_z = engine.estimate_gamma_z(cfg.height, 10000, 50)
    
    # Extrair pressão característica para o memorial
    q0_kN_m2 = (wind_data['profile'][-1]['q_Pa'] if wind_data['profile'] else 0) / 1000.0
    
    res = {
        **wind_data, 
        "gamma_z": gamma_z, 
        "v0": v0, 
        "height": height, 
        "width_x": width_x,
        "q0_kN_m2": q0_kN_m2
    }
    blackboard = build_stability_blackboard(res)
    
    return {
        "success": True,
        "result": res,
        "pedagogical_steps": blackboard
    }

@router.post("/calculate/integrated-foundation")
async def calculate_integrated_foundation(req: Dict):
    from geotechnical_engine import GeotechnicalEngine
    from footing_solver import solve_isolated_footing, FootingConfig
    from master_pedagogy import build_integrated_foundation_blackboard
    
    # 1. Analise SPT
    geo_engine = GeotechnicalEngine()
    spt_res = geo_engine.analyze_spt(req.get('spt_data', []))
    
    # 2. Dimensionamento da Sapata usando sigma_adm do SPT
    cfg = FootingConfig(
        Nd_kN=req.get('Nd_kN', 500.0),
        sigma_adm_kPa=spt_res['sigma_adm_kPa'],
        ap_m=req.get('ap_m', 0.20),
        bp_m=req.get('bp_m', 0.40),
        fck=req.get('fck', 25.0)
    )
    footing_res = solve_isolated_footing(cfg)
    
    # 3. Memorial Integrado
    blackboard = build_integrated_foundation_blackboard(spt_res, footing_res)
    
    return {
        "success": True,
        "spt_result": spt_res,
        "footing_result": footing_res,
        "pedagogical_steps": blackboard
    }
