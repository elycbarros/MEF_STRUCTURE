from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from radier_solver_v2 import Material, Soil, PlateModel, RadierMindlinWinklerV2, read_column_loads_csv

@dataclass
class Scenario:
    name: str
    Lx: float
    Ly: float
    nx: int
    ny: int
    E: float
    nu: float
    h: float
    kv: float
    q: float
    tensionless: bool
    columns_csv: str

def create_research_scenarios(columns_csv: str):
    base = dict(Lx=24.0, Ly=24.0, nx=15, ny=15, E=32e9, nu=0.20, h=0.70, kv=40e6, q=140e3, tensionless=True, columns_csv=columns_csv)
    return [
        Scenario(name='base', **base),
        Scenario(name='kv_low', **{**base, 'kv': 25e6}),
        Scenario(name='kv_high', **{**base, 'kv': 60e6}),
        Scenario(name='thick_80cm', **{**base, 'h': 0.80}),
    ]

class ForensicPostProcessor:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_batch(self, scenarios):
        rows = []
        for sc in scenarios:
            solver = RadierMindlinWinklerV2(PlateModel(Lx=sc.Lx, Ly=sc.Ly, nx=sc.nx, ny=sc.ny, material=Material(E=sc.E, nu=sc.nu, h=sc.h), soil=Soil(kv=sc.kv, tensionless=sc.tensionless)))
            solver._q_uniform = sc.q
            res = solver.solve(read_column_loads_csv(sc.columns_csv))
            rows.append({'scenario': sc.name, 'kv_MN_m3': sc.kv/1e6, 'h_m': sc.h, 'w_max_mm': res.disp[:,0].max()*1000.0, 'qsoil_max_kPa': res.qsoil.max()/1000.0, 'mx_abs_max_kNm_m': abs(res.mx).max()/1000.0, 'my_abs_max_kNm_m': abs(res.my).max()/1000.0, 'residual_ratio': res.residual_ratio})
        return pd.DataFrame(rows)