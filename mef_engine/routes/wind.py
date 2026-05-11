from fastapi import APIRouter, HTTPException
from schemas.wind import WindRequest, WindStabilityRequest
from wind_engine import WindEngine, WindConfig
from stability_engine import StabilityEngine
from radier_utils import ensure_directory, write_json
import os

router = APIRouter(prefix="/calculate", tags=["Wind & Stability"])

@router.post("/wind")
async def calculate_wind(input: WindRequest):
    cfg = WindConfig(
        v0=input.v0,
        s1=input.s1,
        s3=input.s3,
        categoria=input.categoria,
        classe=input.classe,
        is_dynamic=input.is_dynamic,
        f1=input.f1,
        zeta=input.zeta,
        beta=input.beta
    )
    
    engine = WindEngine(cfg)
    results = engine.generate_force_profile(
        height=input.altura_total,
        width=input.largura,
        depth=input.profundidade or input.largura,
        step=input.step,
        area_level=input.area_por_nivel_m2,
        cf_manual=input.cf
    )
    
    from reporting.pedagogy.stability import build_stability_blackboard
    
    # Adicionar dados extras para o blackboard
    results.update({
        "v0": input.v0,
        "q0_kN_m2": results['summary']['max_q_Pa'] / 1000.0
    })
    
    blackboard = build_stability_blackboard(results)
    
    # Salvar para debug/cache
    ensure_directory("output_api")
    write_json(os.path.join("output_api", "last_wind_results.json"), results)
    
    return {
        "success": True,
        "pedagogical_steps": blackboard,
        **results
    }

@router.post("/wind-stability")
async def calculate_wind_stability(input: WindStabilityRequest):
    try:
        # 1. Calcular Vento
        cfg = WindConfig(
            v0=input.v0,
            s1=input.s1,
            s3=input.s3,
            categoria=input.categoria,
            classe=input.classe,
            is_dynamic=input.is_dynamic,
            f1=input.f1,
            zeta=input.zeta,
            beta=input.beta
        )
        engine = WindEngine(cfg)
        wind_results = engine.generate_force_profile(
            height=input.altura_total,
            width=input.largura,
            depth=input.profundidade or input.largura,
            step=input.step,
            area_level=input.area_por_nivel_m2,
            cf_manual=input.cf
        )
        
        # 2. Alimentar Estabilidade
        # m1_kNm pode vir do payload ou ser o momento na base do vento
        m1 = input.m1_kNm if input.m1_kNm is not None else wind_results['summary']['base_moment_kNm']
        
        stability = StabilityEngine()
        stability_results = stability.calculate_advanced_stability(
            total_p_kN=input.total_p_kN,
            total_h_force_kN=wind_results['summary']['total_force_kN'],
            m1_kNm=m1,
            height=input.altura_total,
            wind_v0=input.v0,
            f1_hz=input.f1 if input.is_dynamic else 0.5
        )
        
        # 3. Resultado Acoplado
        return {
            "wind": wind_results,
            "stability": stability_results,
            "coupling": {
                "m1_used_kNm": m1,
                "h_force_used_kN": wind_results['summary']['total_force_kN']
            }
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
