from fastapi import APIRouter, HTTPException
from typing import Any
import pandas as pd

from schemas.core import ConfigInput
from schemas.elite import (
    EstimateLoadsRequest, 
    BeamAnalysisRequest, 
    CoreAnalysisRequest, 
    ReservoirRequest, 
    ColumnRequest,
    OptimizationRequest,
    CopilotRequest
)
from radier_utils import sanitize_for_json

router = APIRouter(tags=["Elite Modules"])

@router.post("/optimize")
async def run_optimization(req: OptimizationRequest):
    from structural_optimizer import GeneticOptimizer
    # Mock logic: Get project data from persistence (simplified for this example)
    optimizer = GeneticOptimizer(pop_size=req.population_size, generations=req.generations)
    # No M5-Master real, passaríamos o solver aqui
    result = optimizer.run_optimization() 
    return sanitize_for_json({"success": True, "result": result})

@router.post("/copilot/diagnose")
async def get_copilot_diagnosis(req: CopilotRequest):
    from ai_copilot import AICopilot
    # Mock data for demonstration
    mock_data = {
        "w_max": 35.0, "w_limit": 30.0,
        "fck": 30, "h": 0.50,
        "max_bar_diam": 25.0, "min_bar_diam": 10.0
    }
    copilot = AICopilot()
    report = copilot.generate_expert_report(mock_data)
    return sanitize_for_json({"success": True, "report": report})

@router.post("/estimate_loads")
async def estimate_loads_elite(request: EstimateLoadsRequest):
    """NBR 6120 simplified parameters for building loads."""
    cargas = {
        "residencial": 2.0, "comercial": 3.0, "escritorio": 2.5,
        "garagem": 3.0, "deposito": 5.0
    }
    pp_laje = 3.75; revestimento = 1.0; paredes = 2.0
    sobrecarga = cargas.get(request.tipo_uso.lower(), 2.0)
    carga_total = (pp_laje + revestimento + paredes + sobrecarga) * max(1, request.num_pavimentos) + 1.5
    return {
        "success": True, "estimated_q_kPa": carga_total,
        "breakdown": {
            "permanente_por_pavimento": pp_laje + revestimento + paredes,
            "acidental_por_pavimento": sobrecarga,
            "num_pavimentos": request.num_pavimentos,
            "carga_cobertura": 1.5
        }
    }

@router.post("/calculate/beam")
async def calculate_beam(req: BeamAnalysisRequest):
    from beam_solver import run_beam_analysis
    from beam_memorial import build_beam_memorial
    from master_pedagogy import build_beam_blackboard
    result = run_beam_analysis(**req.model_dump())
    memorial = build_beam_memorial(result)
    pedagogical_steps = build_beam_blackboard(result, req.model_dump())
    return sanitize_for_json({
        "success": True,
        **result,
        "memorial_markdown": memorial,
        "pedagogical_steps": pedagogical_steps,
    })

@router.post("/calculate/building-core")
async def calculate_building_core(req: CoreAnalysisRequest):
    from building_core import (
        create_elevator_shaft, create_stair_core, create_shear_wall, run_core_analysis
    )
    cores = []
    for i, shaft in enumerate(req.elevator_shafts or []):
        cores.append(create_elevator_shaft(**shaft, fck=req.fck, n_floors=req.n_floors, name=f'FOSSO_ELEV_{i+1:02d}'))
    for i, stair in enumerate(req.stair_cores or []):
        cores.append(create_stair_core(**stair, fck=req.fck, n_floors=req.n_floors, name=f'CAIXA_ESC_{i+1:02d}'))
    for i, wall in enumerate(req.shear_walls or []):
        cores.append(create_shear_wall(**wall, fck=req.fck, n_floors=req.n_floors, name=f'PAREDE_{i+1:02d}'))
    result = run_core_analysis(
        cores=cores if cores else None,
        building_Lx=req.building_Lx, building_Ly=req.building_Ly,
        n_floors=req.n_floors, floor_height=req.floor_height,
        floor_weight_kN=req.floor_weight_kN, fck=req.fck,
    )
    return sanitize_for_json({"success": True, **result})

@router.post("/calculate/concrete_wall")
async def calculate_concrete_wall(req: dict):
    from engines.column_engine import ColumnEngine
    res = ColumnEngine.solve_concrete_wall(
        nd_kN_m=req.get('Nd', 500.0),
        h_wall=req.get('h', 2.8),
        t_wall=req.get('t', 0.12),
        fck=req.get('fck', 30.0)
    )
    from master_pedagogy import build_concrete_wall_blackboard
    pedagogical_steps = build_concrete_wall_blackboard(res)
    return sanitize_for_json({
        "success": True, 
        **res,
        "pedagogical_steps": pedagogical_steps
    })

@router.post("/calculate/column")
async def calculate_column(req: ColumnRequest):
    from column_solver import ColumnSection, ColumnLoads, solve_column_section, analyze_shortening
    from durability_checker import DurabilityChecker, DurabilityConfig
    from master_pedagogy import build_column_blackboard
    cover_m = req.cover if req.cover is not None else DurabilityChecker.get_min_cover(DurabilityConfig(caa=req.caa), 'column') / 1000.0
    sec = ColumnSection(b=req.b, h=req.h, fck=req.fck, cover=cover_m, caa=req.caa, L_free=req.L_free)
    loads = ColumnLoads(Nd_kN=req.Nd_kN, Mxd_kNm=req.Mxd_kNm, Myd_kNm=req.Myd_kNm)
    design = solve_column_section(sec, loads)
    shortening = analyze_shortening(sec, req.Nd_kN, req.n_floors_for_shortening)
    pedagogical_steps = build_column_blackboard(sec, loads, design)
    return sanitize_for_json({
        "success": True,
        "design": design,
        "shortening": shortening,
        "pedagogical_steps": pedagogical_steps,
    })

@router.post("/calculate/frame-legacy")
async def calculate_frame(input: ConfigInput):
    """Executa análise de pórtico 3D via StrucPy (legado)."""
    try:
        from lajes_solver import PillarSupport
        from laje_lab_v2 import LajeLabV2Config, run_laje_v2_pipeline
        from strucpy_adapter import Beam, StrucPyAdapter
        
        pillars = [PillarSupport(p.id, p.x, p.y, bx=p.bx, by=p.by) for p in (input.pillars or [])]
        config_v2 = LajeLabV2Config(
            base_name=f"api_frame_{input.analysis_mode}",
            Lx=input.Lx, Ly=input.Ly, fck=input.fck,
            pillar_height=input.pillar_height, pillars=pillars
        )
        if input.beams:
            config_v2.beams = [Beam(**b.dict()) for b in input.beams]
        result = run_laje_v2_pipeline(config_v2)
        frame = result['frame']
        model_3d = StrucPyAdapter.get_3d_model_data(frame)
        design = result['design']
        
        # Obter diagramas
        member_forces_df = StrucPyAdapter.get_member_forces(frame)
        # StrucPy memF() costuma retornar um DataFrame longo ou lista de DFs. 
        # Aqui simplificamos para retorno do records.
        diagrams = member_forces_df.to_dict(orient='records') if hasattr(member_forces_df, 'to_dict') else []
        
        return sanitize_for_json({
            "success": True, 
            "model_3d": {
                "nodes": model_3d['nodes'].reset_index().to_dict(orient='records'),
                "members": model_3d['members'].reset_index().to_dict(orient='records')
            },
            "design": design, 
            "diagrams": diagrams
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate_v2_unified")
async def calculate_unified(input: ConfigInput):
    """Executa análise unificada Pórtico -> Radier."""
    try:
        from lajes_solver import PillarSupport
        from laje_lab_v2 import LajeLabV2Config
        from unified_pipeline import run_unified_analysis
        from radier_lab_v24 import LabConfig
        
        from wind_engine import WindConfig
        
        pillars = [PillarSupport(p.id, p.x, p.y, bx=p.bx, by=p.by) for p in (input.pillars or [])]
        frame_cfg = LajeLabV2Config(
            pillars=pillars, 
            fck=input.fck, 
            pillar_height=input.pillar_height, 
            q_perm=input.q*0.6, 
            q_acid=input.q*0.4
        )
        frame_cfg.num_pavimentos = input.num_floors
        
        radier_cfg = LabConfig(Lx=input.Lx, Ly=input.Ly, h=input.h, kv=input.kv, fck=input.fck, base_name="unified_demo")
        
        wind_cfg = WindConfig(
            v0=input.wind_v0,
            categoria=input.wind_categoria,
            is_dynamic=input.wind_is_dynamic,
            f1=input.wind_f1_hz,
            zeta=input.wind_zeta
        )
        
        res = run_unified_analysis(frame_cfg, radier_cfg, wind_config=wind_cfg)
        return sanitize_for_json(res)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
