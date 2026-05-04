from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from radier_solver_v21 import Scenario
from radier_solver_v22 import read_measurements_csv
from radier_solver_v2 import Material, Soil, PlateModel, RadierMindlinWinklerV2, read_column_loads_csv

@dataclass
class BayesianResult:
    kv_map: float
    kv_mean: float
    kv_p10: float
    kv_p50: float
    kv_p90: float
    sigma_map: float
    sigma_mean: float
    marginal_kv: list
    marginal_kv_probs: list

class BayesianKvCalibration:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _predict(self, scenario: Scenario, kv: float, measurements: pd.DataFrame):
        solver = RadierMindlinWinklerV2(PlateModel(Lx=scenario.Lx, Ly=scenario.Ly, nx=scenario.nx, ny=scenario.ny, material=Material(E=scenario.E, nu=scenario.nu, h=scenario.h), soil=Soil(kv=kv, tensionless=scenario.tensionless)))
        solver._q_uniform = scenario.q
        res = solver.solve(read_column_loads_csv(scenario.columns_csv))
        vals = []
        for _, r in measurements.iterrows():
            d = ((res.nodes[:,0]-r['x'])**2 + (res.nodes[:,1]-r['y'])**2)**0.5
            vals.append(float(res.disp[d.argmin(),0]*1000.0))
        return np.array(vals)

    def run_grid_bayes(self, scenario: Scenario, measurements: pd.DataFrame, kv_grid, sigma_grid):
        y = measurements['w_mm'].to_numpy(dtype=float)
        kv_grid = np.asarray(kv_grid, dtype=float)
        sigma_grid = np.asarray(sigma_grid, dtype=float)
        log_post = np.full((len(kv_grid), len(sigma_grid)), -np.inf, dtype=float)

        for i, kv in enumerate(kv_grid):
            yp = self._predict(scenario, float(kv), measurements)
            err = y - yp
            for j, sigma in enumerate(sigma_grid):
                sigma = max(float(sigma), 1e-9)
                ll = -0.5 * np.sum((err / sigma) ** 2) - len(err) * np.log(sigma)
                log_prior_kv = -np.log(max(float(kv), 1.0))
                log_prior_sigma = -np.log(max(float(sigma), 1e-6))
                log_post[i, j] = ll + log_prior_kv + log_prior_sigma

        log_post -= np.max(log_post)
        post = np.exp(log_post)
        post = post / post.sum()
        mkv = post.sum(axis=1)
        ms = post.sum(axis=0)
        kv_map = float(kv_grid[np.argmax(mkv)])
        kv_mean = float(np.sum(kv_grid * mkv))
        sigma_map = float(sigma_grid[np.argmax(ms)])
        sigma_mean = float(np.sum(sigma_grid * ms))
        cdf = np.cumsum(mkv)
        kv_p10 = float(kv_grid[np.searchsorted(cdf, 0.10)])
        kv_p50 = float(kv_grid[np.searchsorted(cdf, 0.50)])
        kv_p90 = float(kv_grid[np.searchsorted(cdf, 0.90)])
        pd.DataFrame({'kv': kv_grid, 'prob': mkv}).to_csv(self.output_dir / 'v23_marginal_kv.csv', index=False)
        return BayesianResult(kv_map, kv_mean, kv_p10, kv_p50, kv_p90, sigma_map, sigma_mean, list(map(float, kv_grid)), list(map(float, mkv)))
