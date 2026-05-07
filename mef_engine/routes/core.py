from fastapi import APIRouter, HTTPException
from typing import Any
import time
import os
import pandas as pd

from schemas.core import ConfigInput, DesignOptimizationInput, AnalyticalComparisonResult
from slab_lab import SlabConfig, SlabLab, PillarSupport, LineSupport, Hole
from radier_utils import sanitize_for_json, read_json
from routes.core_helpers import (
    build_field_risk_summary,
    build_winkler_consistency,
    build_reinforcement_summary,
    build_foundation_recommendation,
    build_executive_decision_summary,
    build_regional_reinforcement_map,
    build_thermal_checklist,
    build_solution_comparison
)

class SlabEngineWrapper:
    def __init__(self, input_data: ConfigInput):
        # Mapeia ConfigInput para SlabConfig
        data = input_data.model_dump()
        
        # Converte dicionários para objetos PillarSupport, LineSupport e Hole
        pillars = []
        for p in data.get('pillars', []) or []:
            pillars.append(PillarSupport(
                id=str(p.get('id')),
                x=float(p.get('x')),
                y=float(p.get('y')),
                bx=float(p.get('bx', 0.5)),
                by=float(p.get('by', 0.5))
            ))
            
        line_supports = []
        for ls in data.get('line_supports', []) or []:
            line_supports.append(LineSupport(
                id=str(ls.get('id', 'LS')),
                x1=float(ls.get('x1')),
                y1=float(ls.get('y1')),
                x2=float(ls.get('x2')),
                y2=float(ls.get('y2'))
            ))
            
        holes = []
        for h in data.get('holes', []) or []:
            holes.append(Hole(
                x_min=float(h.get('x_min')),
                y_min=float(h.get('y_min')),
                x_max=float(h.get('x_max')),
                y_max=float(h.get('y_max'))
            ))

        self.config = SlabConfig(
            base_name=data.get('base_name', 'slab_project'),
            Lx=data.get('Lx', 6.0),
            Ly=data.get('Ly', 6.0),
            nx=data.get('nx', 21),
            ny=data.get('ny', 21),
            h=data.get('h', 0.15),
            fck=data.get('fck', 30.0),
            fyk=data.get('fyk', 500.0),
            cover=data.get('cover', 0.02),
            q_perm=data.get('q_perm', 1.5),
            q_acid=data.get('q_acid', 2.0),
            slab_type=data.get('slab_type', 'solid'),
            b_nerv=data.get('b_nerv', 0.10),
            dist_nerv=data.get('dist_nerv', 0.50),
            h_mesa=data.get('h_mesa', 0.05),
            area_voids=data.get('area_voids', 0.04),
            p_force=data.get('p_force', 200.0),
            ecc=data.get('ecc', 0.05),
            filler_type=data.get('filler_type', 'ceramic'),
            pillars=pillars,
            line_supports=line_supports,
            holes=holes
        )
        
    def run_analysis(self):
        lab = SlabLab(self.config)
        return lab.run_full_pipeline()

class RadierEngine:
    def __init__(self, input_data: ConfigInput):
        # Mapeia ConfigInput para RadierConfig
        import inspect
        from radier_lab import LabConfig as RadierConfig

        full_data = input_data.model_dump()
        
        if "system_type" in full_data:
            full_data["module_name"] = full_data["system_type"]
            
        valid_keys = set(inspect.signature(RadierConfig).parameters.keys())
        filtered_data = {k: v for k, v in full_data.items() if k in valid_keys}
        
        if "Lx" in full_data: filtered_data["Lx"] = full_data["Lx"]
        if "Ly" in full_data: filtered_data["Ly"] = full_data["Ly"]
        
        self.config = RadierConfig(**filtered_data)
        
    def run_analysis(self):
        from radier_lab import run_full_pipeline_demo as run_radier_pipeline

        master_summary = run_radier_pipeline(self.config)
        
        out_dir = self.config.output_dir
        det_file = os.path.join(out_dir, f"{self.config.base_name}_deterministic_summary.json")
        memorial_file = os.path.join(out_dir, f"{self.config.base_name}_memorial_summary.json")
        
        results = {
            "master": master_summary,
            "deterministic_results": read_json(det_file) if os.path.exists(det_file) else {},
            "memorial": read_json(memorial_file) if os.path.exists(memorial_file) else {},
        }
        return results

class RadierAnalytical:
    def __init__(self, input_data: ConfigInput):
        self.input_data = input_data
        
    def run_comparison(self, mef_results: dict):
        # Esta função agora é legada, os resultados vêm do memorial
        return mef_results.get("memorial", {}).get("comparativo_metodologias", {})

router = APIRouter(tags=["Mestre - Core"])

@router.post("/calculate")
async def calculate_radier(input_data: ConfigInput):
    """Main structural analysis engine for Radier foundations."""
    try:
        is_laje = input_data.system_type == 'laje'
        if is_laje:
            engine = SlabEngineWrapper(input_data)
        else:
            engine = RadierEngine(input_data)
        results = engine.run_analysis()
        
        # Step 2: Extract summaries and diagnostics
        field_risk = build_field_risk_summary(input_data)
        winkler = build_winkler_consistency(input_data, results.get("deterministic_results", {}))
        
        # Step 3: Analytical Comparison
        analytical_results = results.get("memorial", {}).get("comparativo_metodologias")
        
        # Se por algum motivo não estiver no memorial, tenta o fallback (mas agora deve estar sempre lá)
        if not analytical_results:
            try:
                analytical_engine = RadierAnalytical(input_data)
                analytical_results = analytical_engine.run_comparison(results)
            except Exception as e:
                print(f"Warning: Redundant analytical comparison failed: {str(e)}")

        # Step 4: Build Recommendations
        recommendation = build_foundation_recommendation(
            input_data, 
            results.get("memorial", {}), 
            results.get("deterministic_results", {}), 
            field_risk, 
            winkler
        )
        
        executive_decision = build_executive_decision_summary(recommendation)
        reinforcement = build_reinforcement_summary(results.get("memorial", {}), input_data)
        reinforcement_map = build_regional_reinforcement_map(results.get("memorial", {}), input_data)
        thermal = build_thermal_checklist(input_data)
        comparison = build_solution_comparison(input_data, recommendation)

        # Step 5: Consolidate Output
        final_output = {
            "success": True,
            "is_laje": is_laje,
            "master": results.get("master") if is_laje else results.get("master"),
            "deterministic": results.get("master", {}).get("mef_summary") if is_laje else results.get("deterministic_results"),
            "specialized": results.get("master", {}).get("specialized") if is_laje else None,
            "memorial": results.get("master", {}).get("memorial") if is_laje else results.get("memorial"),
            "field_risk_summary": field_risk,
            "winkler_consistency": winkler,
            "analytical_comparison": analytical_results,
            "foundation_recommendation": recommendation,
            "executive_decision": executive_decision,
            "reinforcement_summary": reinforcement,
            "reinforcement_map": reinforcement_map,
            "thermal_checklist": thermal,
            "solution_comparison": comparison,
            "timestamp": time.time(),
            "status": "success"
        }
        
        return sanitize_for_json(final_output)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/estimate_loads")
async def estimate_loads_core(data: dict):
    """Preliminary load estimation based on NBR 6120 typical usage."""
    tipo_uso = data.get("tipo_uso", "residencial")
    num_pavimentos = data.get("num_pavimentos", 1)
    
    # Valores típicos (kN/m2) incluindo peso próprio estimado
    loads = {
        "residencial": 12.0,
        "comercial": 15.0,
        "escritorio": 14.0,
        "garagem": 10.0,
        "laje_cobertura": 8.0
    }
    
    base_q = loads.get(tipo_uso, 12.0)
    total_q_kPa = base_q * num_pavimentos
    
    return {
        "success": True,
        "estimated_q_kPa": total_q_kPa,
        "num_pavimentos": num_pavimentos,
        "tipo_uso": tipo_uso
    }

@router.post("/optimize_design")
async def optimize_design_core(input_data: DesignOptimizationInput):
    """Iterative optimization to find minimum thickness that passes checks."""
    # Placeholder for actual optimization loop
    return {"suggested_h": input_data.current_h, "status": "optimization_module_under_development"}
