"""
routes/forensic.py — Router para análise pericial e probabilística (PhD).
"""
from fastapi import APIRouter, HTTPException
from typing import Any, List
from pydantic import BaseModel
from radier_lab_v24 import LabConfig, build_base_scenario
from radier_solver_v22 import InverseCalibrationAndUQ, read_measurements_csv
from radier_utils import sanitize_for_json
import pandas as pd
import numpy as np

router = APIRouter(tags=["Forensic & Uncertainty"])

class MonteCarloRequest(BaseModel):
    config: dict
    n_simulations: int = 100
    seed: int = 123

class CalibrationRequest(BaseModel):
    config: dict
    measurements: List[dict] # [{'x', 'y', 'w_mm'}]

@router.post("/forensic/monte-carlo")
async def run_monte_carlo(req: MonteCarloRequest):
    """Executa simulação de Monte Carlo para quantificar incertezas."""
    try:
        from radier_lab_v24 import LabConfig
        cfg = LabConfig(**req.config)
        scenario = build_base_scenario(cfg, cfg.columns_csv if cfg.columns_csv else "output/columns_example.csv")
        
        uq = InverseCalibrationAndUQ(output_dir=cfg.output_dir)
        df_results = uq.monte_carlo_uncertainty(scenario, n=req.n_simulations, seed=req.seed)
        
        return sanitize_for_json({
            "success": True,
            "data": df_results.to_dict(orient='records'),
            "summary": {
                "w_max_mean": float(df_results['w_max_mm'].mean()),
                "w_max_std": float(df_results['w_max_mm'].std()),
                "q_max_mean": float(df_results['qsoil_max_kPa'].mean()),
                "q_max_std": float(df_results['qsoil_max_kPa'].std()),
            }
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forensic/calibrate")
async def calibrate_soil(req: CalibrationRequest):
    """Calibra o coeficiente de recalque (kv) com base em medições reais."""
    try:
        from radier_lab_v24 import LabConfig
        cfg = LabConfig(**req.config)
        scenario = build_base_scenario(cfg, cfg.columns_csv if cfg.columns_csv else "output/columns_example.csv")
        
        measurements_df = pd.DataFrame(req.measurements)
        uq = InverseCalibrationAndUQ(output_dir=cfg.output_dir)
        
        # Grid de busca de 5MPa/m até 100MPa/m
        kv_grid = np.linspace(5e6, 100e6, 20)
        res = uq.calibrate_kv_grid(scenario, measurements_df, kv_grid)
        
        return sanitize_for_json({
            "success": True,
            "best_kv": res.best_kv,
            "rmse_mm": res.best_rmse_mm,
            "mae_mm": res.best_mae_mm
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
