from fastapi import APIRouter, HTTPException
from typing import Any
import time
import os
import pandas as pd

from schemas.core import ConfigInput, DesignOptimizationInput, AnalyticalComparisonResult
from radier_lab_v24 import LabConfig, run_full_pipeline_demo, read_column_loads_csv
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

class RadierEngine:
    def __init__(self, input_data: ConfigInput):
        # Mapeia ConfigInput para LabConfig (filtrando campos extras)
        import inspect
        full_data = input_data.model_dump()
        valid_keys = set(inspect.signature(LabConfig).parameters.keys())
        filtered_data = {k: v for k, v in full_data.items() if k in valid_keys}
        self.config = LabConfig(**filtered_data)
        
    def run_analysis(self):
        # Executa o pipeline completo definido em radier_lab_v24
        master_summary = run_full_pipeline_demo(self.config)
        
        # Carrega os resultados detalhados dos arquivos gerados
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
        from radier_analytical import AnalyticalConfig, calculate_analytical_comparison
        
        # Resolve colunas
        out_dir = self.input_data.output_dir
        if self.input_data.columns_csv:
            cols_path = self.input_data.columns_csv
        else:
            cols_path = os.path.join(out_dir, 'columns_example.csv')
            
        if not os.path.exists(cols_path):
            return {"error": "Columns CSV not found for analytical comparison"}
            
        loads = read_column_loads_csv(cols_path)
        cfg = AnalyticalConfig(
            Lx=self.input_data.Lx,
            Ly=self.input_data.Ly,
            loads_kN=loads,
            q_uniform_Pa=self.input_data.q
        )
        
        # Carregar punching results se existirem
        punching_file = os.path.join(out_dir, 'radier_punching_check_v2.csv')
        punching_df = pd.read_csv(punching_file) if os.path.exists(punching_file) else None
        
        comp = calculate_analytical_comparison(
            mef_results.get("deterministic_results", {}),
            cfg,
            punching_mef_df=punching_df
        )
        return comp

router = APIRouter(tags=["Core Analysis"])

@router.post("/calculate")
async def calculate_radier(input_data: ConfigInput):
    """Main structural analysis engine for Radier foundations."""
    try:
        engine = RadierEngine(input_data)
        results = engine.run_analysis()
        
        # Step 2: Extract summaries and diagnostics
        field_risk = build_field_risk_summary(input_data)
        winkler = build_winkler_consistency(input_data, results.get("deterministic_results", {}))
        
        # Step 3: Analytical Comparison
        analytical_results = None
        if input_data.enable_analytical_comparison:
            try:
                analytical_engine = RadierAnalytical(input_data)
                analytical_results = analytical_engine.run_comparison(results)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Warning: Analytical comparison failed: {str(e)}")

        # Step 4: Build Recommendations
        recommendation = build_foundation_recommendation(
            input_data, 
            results.get("memorial", {}), 
            results.get("deterministic_results", {}), 
            field_risk, 
            winkler
        )
        
        executive_decision = build_executive_decision_summary(recommendation)
        reinforcement = build_reinforcement_summary(results.get("memorial", {}))
        reinforcement_map = build_regional_reinforcement_map(results.get("memorial", {}), input_data)
        thermal = build_thermal_checklist(input_data)
        comparison = build_solution_comparison(input_data, recommendation)

        # Step 5: Consolidate Output
        final_output = {
            "results": results,
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
async def estimate_loads_core(input_data: ConfigInput):
    """Preliminary load estimation based on area and typical usage."""
    area = input_data.Lx * input_data.Ly
    typical_load = area * 12.0 # 12 kN/m2 as rule of thumb for residential
    return {"estimated_total_kN": typical_load, "area_m2": area}

@router.post("/optimize_design")
async def optimize_design_core(input_data: DesignOptimizationInput):
    """Iterative optimization to find minimum thickness that passes checks."""
    # Placeholder for actual optimization loop
    return {"suggested_h": input_data.current_h, "status": "optimization_module_under_development"}
