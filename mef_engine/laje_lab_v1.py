"""laje_lab_v1.py – Orquestrador para o módulo Lajes Lab."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd

from lajes_solver import (
    Material,
    PillarSupport,
    LineSupport,
    Hole,
    LajeModel,
    LajesMindlinSolver,
    SupportType
)
from radier_design_v2 import (
    DesignConfig, design_flexure_from_elements, check_serviceability_flexure, check_punching
)
from radier_memorial import write_memorial_summary
from radier_reporting import build_artifact_manifest, build_markdown_report, build_didactic_guide
from radier_utils import dataclass_to_dict, ensure_directory, read_json, write_json
from standards_profiles import get_combination_set

@dataclass
class LajeLabConfig:
    module_name: str = 'laje'
    code_profile: str = 'ABNT_NBR_6118_2023'
    output_dir: str = 'output_laje'
    base_name: str = 'laje_lab_demo'
    Lx: float = 12.0
    Ly: float = 12.0
    nx: int = 21
    ny: int = 21
    E: float = 32e9
    nu: float = 0.20
    h: float = 0.20
    q_pp: float = 0.0 # Será calculado se 0
    q_perm: float = 1.5e3 # N/m2
    q_acid: float = 2.0e3 # N/m2
    fck: float = 30.0
    fyk: float = 500.0
    cover: float = 0.03
    pillars: list[PillarSupport] = field(default_factory=list)
    line_supports: list[LineSupport] = field(default_factory=list)
    holes: list[Hole] = field(default_factory=list)
    sigma_adm_kPa: float = 0.0 # Nao usado em lajes

def _summarize_laje_result(res, config) -> dict:
    pillar_reactions = []
    for p in config.pillars:
        # Encontrar nó mais próximo do pilar
        dists = np.linalg.norm(res.nodes - np.array([p.x, p.y]), axis=1)
        node_idx = np.argmin(dists)
        pillar_reactions.append({
            'id': p.id,
            'x': p.x,
            'y': p.y,
            'reaction_kN': float(res.reactions[node_idx] / 1000.0)
        })

    return {
        'w_max_mm': float(res.disp[:, 0].max() * 1000.0),
        'qsoil_max_kPa': 0.0,
        'mx_abs_max_kNm_m': float(np.abs(res.mx).max() / 1000.0),
        'my_abs_max_kNm_m': float(np.abs(res.my).max() / 1000.0),
        'distributed_load_kN': float(res.distributed_load_total / 1000.0),
        'column_load_kN': float(res.reactions_total / 1000.0),
        'reactions_total_kN': float(res.reactions_total / 1000.0),
        'loads_total_kN': float(res.distributed_load_total / 1000.0),
        'residual_kN': float(res.residual / 1000.0),
        'residual_ratio': float(abs(res.residual) / max(1e-9, res.distributed_load_total)),
        'active_springs': 0,
        'iterations': 1,
        'pillar_reactions': pillar_reactions,
    }

def run_laje_pipeline(config: LajeLabConfig):
    out = ensure_directory(config.output_dir)
    
    # Peso próprio automático se não fornecido
    if config.q_pp == 0:
        config.q_pp = 25000.0 * config.h
        
    model = LajeModel(
        Lx=config.Lx, Ly=config.Ly, nx=config.nx, ny=config.ny,
        material=Material(E=config.E, nu=config.nu, h=config.h),
        pillars=config.pillars,
        line_supports=config.line_supports,
        holes=config.holes,
        q_pp=config.q_pp,
        q_perm=config.q_perm,
        q_acid=config.q_acid
    )
    
    solver = LajesMindlinSolver(model)
    combos = get_combination_set(config.code_profile)
    
    # 1. ELU - Flexão
    res_elu = solver.solve(
        combo_multiplier_pp=combos['ELU']['gamma_g'],
        combo_multiplier_perm=combos['ELU']['gamma_g'],
        combo_multiplier_acid=combos['ELU']['gamma_q']
    )
    elu_nodal_path = out / f"{config.base_name}_elu_nodal.csv"
    elu_elem_path = out / f"{config.base_name}_elu_elem.csv"
    solver.export_nodal_results_csv(res_elu, elu_nodal_path)
    solver.export_element_results_csv(res_elu, elu_elem_path)
    
    # 2. ELS - Recalques e Fissuração
    res_els = solver.solve(
        combo_multiplier_pp=combos['ELS_QUASE_PERM']['gamma_g'],
        combo_multiplier_perm=combos['ELS_QUASE_PERM']['gamma_g'],
        combo_multiplier_acid=combos['ELS_QUASE_PERM']['psi_2']
    )
    els_nodal_path = out / f"{config.base_name}_els_nodal.csv"
    els_elem_path = out / f"{config.base_name}_els_elem.csv"
    solver.export_nodal_results_csv(res_els, els_nodal_path)
    solver.export_element_results_csv(res_els, els_elem_path)
    
    # 3. Design de Armaduras (Flexão)
    d_config = DesignConfig(
        fck=config.fck, fyk=config.fyk, h=config.h,
        Lx=config.Lx, Ly=config.Ly, cover=config.cover
    )
    flexure_path = out / f"{config.base_name}_design_flexure.csv"
    materials_path = out / f"{config.base_name}_materials.json"
    
    # design_flexure_from_elements espera o CSV do ELU
    flexure_results_path, metrics = design_flexure_from_elements(elu_elem_path, d_config, flexure_path)
    write_json(metrics, materials_path)
    
    # 4. Verificação de Fissuração (ELS-W)
    service_path = out / f"{config.base_name}_serviceability.csv"
    check_serviceability_flexure(els_elem_path, flexure_results_path, d_config, service_path)
    
    # 4.1 Verificação de Punção (ELU)
    # Precisamos criar um DataFrame de pilares com as reações do ELU
    pillars_data = []
    for p in config.pillars:
        dists = np.linalg.norm(res_elu.nodes - np.array([p.x, p.y]), axis=1)
        node_idx = np.argmin(dists)
        pillars_data.append({
            'id': p.id,
            'x': p.x,
            'y': p.y,
            'bx': p.bx,
            'by': p.by,
            'fz_kN': float(res_elu.reactions[node_idx] / 1000.0)
        })
    columns_df = pd.DataFrame(pillars_data)
    punching_path = out / f"{config.base_name}_punching.csv"
    check_punching(columns_df, flexure_path, d_config, str(punching_path))
    
    # 5. Memorial
    memorial_path = out / f"{config.base_name}_memorial_summary.json"
    det_summary = _summarize_laje_result(res_elu, config)
    
    # Precisamos garantir que os arquivos CSV que o memorial procura existam com os nomes esperados
    custom_paths = {
        'nodes': elu_nodal_path,
        'flexure': flexure_path,
        'serviceability': service_path,
        'punching': punching_path
    }
    
    memorial = write_memorial_summary(
        config=config,
        deterministic_summary=det_summary,
        output_dir=out,
        analytical_comparison=None,
        geotechnical_profile=None,
        custom_paths=custom_paths
    )
    memorial['_debug_elements'] = res_elu.elements.tolist()
    
    return {
        "success": True,
        "memorial": memorial,
        "metrics": metrics,
        "system_type": "laje",
        "paths": {
            "elu_nodal": str(elu_nodal_path),
            "elu_elem": str(elu_elem_path),
            "flexure": str(flexure_results_path),
            "service": str(service_path)
        }
    }

if __name__ == "__main__":
    pillars = [
        PillarSupport("P1", 2.0, 2.0, support_type=SupportType.FIXED),
        PillarSupport("P2", 10.0, 2.0, support_type=SupportType.PINNED),
        PillarSupport("P3", 2.0, 10.0, support_type=SupportType.PINNED),
        PillarSupport("P4", 10.0, 10.0, support_type=SupportType.PINNED),
    ]
    lines = [
        LineSupport("V1", 0.0, 0.0, 12.0, 0.0, support_type=SupportType.PINNED),
    ]
    config = LajeLabConfig(pillars=pillars, line_supports=lines)
    res = run_laje_pipeline(config)
    print("Pipeline Laje concluído com sucesso.")
