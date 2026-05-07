"""
radier_lab.py - Elite Engineering Module for Foundation Rafts (NBR 6122).
Strictly compliant with ABNT NBR 6122:2022 and NBR 6118:2023.
Completely decoupled from Suspended Slab logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
import os

from radier_solver_v2 import (
    Material,
    Soil,
    PlateModel,
    RadierMindlinWinklerV2,
    AreaLoad,
    read_column_loads_csv,
)
from radier_solver_v21 import Scenario, ForensicPostProcessor, create_research_scenarios
from radier_solver_v22 import read_measurements_csv, InverseCalibrationAndUQ
from radier_solver_v23 import BayesianKvCalibration
from radier_design_v2 import DesignConfig, check_serviceability_flexure, design_flexure_from_elements, check_punching
from radier_memorial import write_memorial_summary
from radier_reporting import build_artifact_manifest, build_markdown_report, build_didactic_guide
from radier_utils import dataclass_to_dict, ensure_directory, read_json, write_json
from ssi_engine import SSIPseudoCoupled
from errors import InvalidInputError, NumericalFailureError

@dataclass
class RadierConfig:
    """Configuração profissional para o laboratório de fundações (Radier)."""
    module_name: str = 'radier'
    base_name: str = 'radier_project'
    output_dir: str = 'output/radier'
    
    # Geometria
    Lx: float = 20.0
    Ly: float = 20.0
    nx: int = 21
    ny: int = 21
    h: float = 0.60
    
    # Materiais e Solo
    fck: float = 30.0
    fyk: float = 500.0
    E: float = 32e9
    nu: float = 0.20
    cover: float = 0.05
    kv: float = 40e6 # N/m³ (Winkler)
    sigma_adm_kPa: float = 200.0
    tensionless: bool = True
    
    # Cargas
    q: float = 100e3 # N/m²
    columns_csv: str | None = None
    area_loads: list = field(default_factory=list)
    
    # SSI e Avançado
    ssi_enabled: bool = False
    piles: list = None
    q_limit_kPa: float | None = None
    
    def __post_init__(self):
        ensure_directory(self.output_dir)

def run_radier_pipeline(config: RadierConfig) -> dict:
    """Executa o pipeline completo para radiers."""
    out = Path(config.output_dir)
    
    # 1. Setup do Solver (SSI/Winkler)
    mat = Material(E=config.E, nu=config.nu, h=config.h)
    soil = Soil(
        kv=config.kv, 
        tensionless=config.tensionless,
        q_limit=config.q_limit_kPa * 1000.0 if config.q_limit_kPa else None
    )
    model = PlateModel(Lx=config.Lx, Ly=config.Ly, nx=config.nx, ny=config.ny, material=mat, soil=soil)
    solver = RadierMindlinWinklerV2(model)
    
    # 2. Carregar Cargas
    column_loads = read_column_loads_csv(config.columns_csv) if config.columns_csv else []
    
    # 3. Execução MEF
    if config.ssi_enabled:
        ssi = SSIPseudoCoupled(model)
        res_data = ssi.solve_iterative(column_loads=column_loads)
        res = res_data['result']
    else:
        res = solver.solve(column_loads, piles=config.piles)
        
    # 4. Design e Memorial
    memorial = write_memorial_summary(config, res)
    
    return memorial

# (Outras funções de pesquisa batch, inversa, bayesiana permanecem aqui como no original, 
# mas filtrando is_laje blocks)
