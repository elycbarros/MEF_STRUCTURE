from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from radier_solver_v21 import Scenario
from radier_solver_v2 import Material, Soil, PlateModel, RadierMindlinWinklerV2, read_column_loads_csv

@dataclass
class CalibrationResult:
    best_kv: float
    best_rmse_mm: float
    best_mae_mm: float

def write_example_measurements_csv(path: str):
    df = pd.DataFrame([
        {'x':4.0,'y':4.0,'w_mm':13.0},
        {'x':12.0,'y':12.0,'w_mm':16.0},
        {'x':20.0,'y':20.0,'w_mm':12.0},
        {'x':12.0,'y':4.0,'w_mm':14.0},
    ])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def read_measurements_csv(path: str):
    return pd.read_csv(path)

class InverseCalibrationAndUQ:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _predict_at_points(self, scenario: Scenario, kv: float, measurements: pd.DataFrame):
        solver = RadierMindlinWinklerV2(PlateModel(Lx=scenario.Lx, Ly=scenario.Ly, nx=scenario.nx, ny=scenario.ny, material=Material(E=scenario.E, nu=scenario.nu, h=scenario.h), soil=Soil(kv=kv, tensionless=scenario.tensionless)))
        solver._q_uniform = scenario.q
        res = solver.solve(read_column_loads_csv(scenario.columns_csv))
        preds = []
        for _, r in measurements.iterrows():
            d = ((res.nodes[:,0]-r['x'])**2 + (res.nodes[:,1]-r['y'])**2)**0.5
            preds.append(float(res.disp[d.argmin(),0]*1000.0))
        return np.array(preds)

    def calibrate_kv_grid(self, scenario: Scenario, measurements: pd.DataFrame, kv_values):
        y = measurements['w_mm'].to_numpy(dtype=float)
        rows = []
        for kv in kv_values:
            yp = self._predict_at_points(scenario, float(kv), measurements)
            err = yp - y
            rmse = float((np.mean(err**2))**0.5)
            mae = float(np.mean(np.abs(err)))
            rows.append({'kv': float(kv), 'rmse_mm': rmse, 'mae_mm': mae})
        df = pd.DataFrame(rows)
        df.to_csv(self.output_dir / 'v22_calibration_grid.csv', index=False)
        best = df.sort_values('rmse_mm').iloc[0]
        return CalibrationResult(best_kv=float(best['kv']), best_rmse_mm=float(best['rmse_mm']), best_mae_mm=float(best['mae_mm']))

    def monte_carlo_uncertainty(self, scenario: Scenario, n: int = 100, seed: int = 123):
        rng = np.random.default_rng(seed)
        rows = []
        for _ in range(n):
            kv = float(rng.normal(scenario.kv, 0.15*scenario.kv))
            kv = max(kv, 5e6)
            q = float(rng.normal(scenario.q, 0.10*scenario.q))
            q = max(q, 1e3)
            solver = RadierMindlinWinklerV2(PlateModel(Lx=scenario.Lx, Ly=scenario.Ly, nx=scenario.nx, ny=scenario.ny, material=Material(E=scenario.E, nu=scenario.nu, h=scenario.h), soil=Soil(kv=kv, tensionless=scenario.tensionless)))
            solver._q_uniform = q
            res = solver.solve(read_column_loads_csv(scenario.columns_csv))
            rows.append({'kv': kv, 'q': q, 'w_max_mm': res.disp[:,0].max()*1000.0, 'qsoil_max_kPa': res.qsoil.max()/1000.0})
        return pd.DataFrame(rows)