"""
unified_pipeline.py - Conexão entre Pórtico 3D (StrucPy) e Radier (MEF).
"""
import sys
import os
from typing import Dict, Any

# Garantir imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from laje_lab_v2 import LajeLabV2Config, run_laje_v2_pipeline
from radier_lab_v24 import LabConfig, run_full_pipeline_demo
from lajes_solver import PillarSupport
from stability_engine import StabilityEngine
from wind_engine import WindEngine, WindConfig

def run_unified_analysis(frame_config: LajeLabV2Config, radier_config: LabConfig, wind_config: WindConfig = None):
    print("\n=== INICIANDO ANÁLISE UNIFICADA (GLOBAL) ===")
    
    # 1. Passo: Análise de Pórtico (StrucPy)
    print("--- FASE 1: Superestrutura (3D Frame) ---")
    frame_results = run_laje_v2_pipeline(frame_config)
    
    if not frame_results['success']:
        return {"success": False, "error": "Falha na análise de pórtico"}

    # 2. Passo: Extrair reações da base
    design_results = frame_results['design']
    pillars_results = design_results.get('pillars', [])
    
    new_pillars_for_radier = []
    for p in pillars_results:
        reaction_kN = p.get('Nd', 100.0) / 1.4 # Simplificação para carga característica
        orig_p = next((op for op in frame_config.pillars if op.id == p['id']), None)
        if orig_p:
            new_pillars_for_radier.append(
                PillarSupport(id=p['id'], x=orig_p.x, y=orig_p.y, p_kN=reaction_kN, bx=orig_p.bx, by=orig_p.by)
            )

    # 2.5 Passo: Elementos Especiais (Escadas/Reservatórios)
    print("--- FASE 1.5: Elementos Especiais ---")
    from special_elements import SpecialElementsSolver
    
    stair = SpecialElementsSolver.solve_stair(L_horizontal=4.0, H_vertical=3.0, load_kN_m2=3.0, thickness_cm=15, fck=30)
    tank = SpecialElementsSolver.solve_reservoir_wall(height=2.5, thickness_cm=20, fck=30)
    
    # Adicionar reações ao Radier como cargas extras
    new_pillars_for_radier.append(PillarSupport(id="ESCADA_A1", x=2.0, y=2.0, p_kN=stair['total_reaction_kN'], bx=0.4, by=1.2))
    new_pillars_for_radier.append(PillarSupport(id="TANK_B1", x=20.0, y=20.0, p_kN=tank['total_load_kN'], bx=1.0, by=1.0))

    # 3. Passo: Análise de Vento
    print("--- FASE 2: Análise de Vento ---")
    w_cfg = wind_config or WindConfig(v0=30.0)
    wind_engine = WindEngine(w_cfg)
    
    # Altura total baseada no número de pavimentos
    num_pavs = getattr(frame_config, 'num_pavimentos', 10)
    floor_height = getattr(frame_config, 'pillar_height', 3.0)
    total_height = floor_height * num_pavs
    
    wind_res = wind_engine.generate_force_profile(
        height=total_height,
        width=radier_config.Lx,
        depth=radier_config.Ly,
        step=floor_height
    )
    
    m1_wind = wind_res['summary']['base_moment_kNm']
    f_wind = wind_res['summary']['total_force_kN']

    # 4. Passo: Análise de Fundação (Radier MEF)
    print("--- FASE 3: Infraestrutura (Radier MEF) ---")
    radier_config.pillars = new_pillars_for_radier
    # Adicionar momento do vento como excentricidade (simplificado)
    total_p_kN = sum(p.p_kN for p in new_pillars_for_radier)
    if total_p_kN > 0:
        radier_config.excentricidade_x = m1_wind / total_p_kN
    
    radier_results = run_full_pipeline_demo(radier_config)
    
    # 5. Passo: Estabilidade Global e Conforto
    print("--- FASE 4: Estabilidade e Conforto ---")
    stability_results = StabilityEngine.calculate_advanced_stability(
        total_p_kN=total_p_kN,
        height=total_height,
        m1_kNm=m1_wind,
        wind_v0=w_cfg.v0,
        f1_hz=w_cfg.f1 if w_cfg.is_dynamic else 0.5,
        total_h_force_kN=f_wind
    )

    return {
        "success": True,
        "frame": frame_results,
        "radier": radier_results,
        "wind": wind_res,
        "stability": stability_results.__dict__ if hasattr(stability_results, '__dict__') else stability_results,
        "special_elements": [stair, tank],
        "coupling": {
            "total_height": total_height,
            "total_p_kN": total_p_kN,
            "m1_wind_kNm": m1_wind,
            "f_wind_kN": f_wind
        }
    }

if __name__ == "__main__":
    # Teste de integração
    print("Teste Unified Pipeline iniciado.")
