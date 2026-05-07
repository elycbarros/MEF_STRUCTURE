"""radier_lab_v24.py – Orquestrador integrado para pesquisa e perícia."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd
from slab_design_engine import SlabDesignEngine, SlabDesignConfig
from slab_serviceability import SlabServiceabilityEngine, ServiceabilityConfig
from errors import InvalidInputError, NumericalFailureError, UnstableModelError

from radier_solver_v2 import (
    Material,
    Soil,
    PlateModel,
    RadierMindlinWinklerV2,
    AreaLoad,
    write_example_column_csv,
    read_column_loads_csv,
)
from radier_solver_v21 import Scenario, ForensicPostProcessor, create_research_scenarios
from radier_solver_v22 import read_measurements_csv, write_example_measurements_csv, InverseCalibrationAndUQ
from radier_solver_v23 import BayesianKvCalibration
from radier_design_v2 import DesignConfig, check_serviceability_flexure, design_flexure_from_elements, check_punching
from radier_memorial import write_memorial_summary
from radier_reporting import build_artifact_manifest, build_markdown_report, build_didactic_guide
from radier_utils import dataclass_to_dict, ensure_directory, read_json, write_json
from radier_validation import validate_columns_csv, validate_lab_config, validate_measurements_csv
from standards_profiles import get_combination_set
import radier_analytical as analytical
from ssi_engine import SSIPseudoCoupled


@dataclass
class LabConfig:
    module_name: str = 'radier'
    code_profile: str = 'ABNT_NBR_6118_2023'
    service_mode: str = 'dimensionamento'
    project_stage: str = 'pesquisa_aplicada'
    client_profile: str = 'construtora_talls'
    study_goal: str = 'dimensionamento, analise e pericia de radier com foco didatico e pesquisa aplicada'
    output_dir: str = 'output'
    base_name: str = 'radier_lab_demo'
    Lx: float = 24.0
    Ly: float = 24.0
    nx: int = 21
    ny: int = 21
    E: float = 32e9
    nu: float = 0.20
    h: float = 0.70
    kv: float = 40e6
    q: float = 140e3
    tensionless: bool = True
    fck: float = 30.0
    fyk: float = 500.0
    cover: float = 0.05
    sigma_adm_kPa: float = 200.0
    column_load_is_variable: float = 0.0
    uniform_load_is_variable: float = 1.0
    columns_csv: str | None = None
    measurements_csv: str | None = None
    spt_csv: str | None = None
    spt_correlation_level: str = 'medio'
    spt_default_soil_type: str = 'misto'
    area_loads: list = field(default_factory=list)
    pillars: list[PillarSupport] = field(default_factory=list)
    geotech_project_type: str = 'edificios_altos'
    geotech_profile_overrides: dict[str, float] | None = None
    ssi_enabled: bool = False
    piles: list[any] = None # Lista de objetos Pile
    q_limit_kPa: float | None = None # Limite plástico do solo (elasto-plástico)
    concrete_nonlinear: bool = False # Ativa não-linearidade física do concreto (Branson)
    advanced_ssi_enabled: bool = False # Ativa rigidez da superestrutura (SSI Avançado)
    ssi_n_floors: int = 40
    # Elite Engineering Tier
    pile_group_enabled: bool = False     # Efeito de grupo de estacas (Poulos & Davis)
    pile_group_Es_kPa: float = 30_000.0  # Módulo do solo para interação
    consolidation_enabled: bool = False  # Análise de adensamento temporal
    consolidation_layers: list = None    # Lista de ConsolidationLayer
    consolidation_delta_sigma_kPa: float = 100.0
    moment_redistribution: bool = False  # Redistribuição plástica de momentos
    redistribution_max_pct: float = 15.0 # Máximo % de redistribuição
    openings: list = None                # Lista de Opening para punção complexa
    h_map_csv: str | None = None         # CSV com espessura por elemento
    openings_csv: str | None = None      # CSV com máscara de aberturas

    def __post_init__(self):
        # Converter pilares se forem passados como dicts (API)
        if self.pillars and isinstance(self.pillars, list):
            new_pillars = []
            for p in self.pillars:
                if isinstance(p, dict):
                    # Tenta converter support_type string para Enum se necessário
                    from lajes_solver import PillarSupport, SupportType
                    st = p.get('support_type', 'pinned')
                    if isinstance(st, str):
                        try:
                            st = SupportType(st)
                        except:
                            st = SupportType.PINNED
                    new_pillars.append(PillarSupport(
                        id=p['id'], x=p['x'], y=p['y'], 
                        p_kN=p.get('p_kN', 0.0),
                        bx=p.get('bx', 0.5), by=p.get('by', 0.5),
                        support_type=st, k_spring=p.get('k_spring', 0.0)
                    ))
                else:
                    new_pillars.append(p)
            self.pillars = new_pillars

        # Converter area_loads se forem passados como dicts (API)
        if self.area_loads and isinstance(self.area_loads, list):
            new_al = []
            for al in self.area_loads:
                if isinstance(al, dict):
                    # Aqui area_loads no LabConfig ainda são dicts, 
                    # eles serão convertidos para objetos AreaLoad no _build_solver
                    # mas para manter consistência podemos deixá-los como dicts 
                    # ou criar uma estrutura aqui. 
                    # Como _build_solver já espera dicts/objetos, vamos apenas garantir 
                    # que os campos básicos existam.
                    pass
            # Por enquanto, mantemos como dicts para o _build_solver processar


def _resolve_columns_csv(config: LabConfig) -> Path:
    out = ensure_directory(config.output_dir)
    if config.pillars:
        # Se houver pilares na lista, gera um CSV temporário
        columns_csv = out / f"{config.base_name}_temp_pillars.csv"
        data = []
        for p in config.pillars:
            data.append({
                'id': p.id,
                'x': p.x,
                'y': p.y,
                'p': getattr(p, 'p_kN', 0.0) * 1000.0, # Converte kN para N
                'bx': p.bx,
                'by': p.by
            })
        df = pd.DataFrame(data)
        df.to_csv(columns_csv, index=False)
        return columns_csv

    if config.columns_csv:
        columns_csv = Path(config.columns_csv)
        validate_columns_csv(columns_csv)
        return columns_csv
    columns_csv = out / 'columns_example.csv'
    write_example_column_csv(columns_csv)
    validate_columns_csv(columns_csv)
    return columns_csv


def _resolve_measurements_csv(config: LabConfig) -> Path:
    out = ensure_directory(config.output_dir)
    if config.measurements_csv:
        measurements_csv = Path(config.measurements_csv)
        validate_measurements_csv(measurements_csv)
        return measurements_csv
    measurements_csv = out / 'measurements_example.csv'
    write_example_measurements_csv(measurements_csv)
    validate_measurements_csv(measurements_csv)
    return measurements_csv


def _summarize_solver_result(res) -> dict:
    return {
        'w_max_mm': float(res.disp[:, 0].max() * 1000.0),
        'qsoil_max_kPa': float(res.qsoil.max() / 1000.0),
        'mx_abs_max_kNm_m': float(abs(res.mx).max() / 1000.0),
        'my_abs_max_kNm_m': float(abs(res.my).max() / 1000.0),
        'distributed_load_kN': float(res.distributed_load_total / 1000.0),
        'column_load_kN': float(res.column_load_total / 1000.0),
        'reactions_total_kN': float(res.reactions_total / 1000.0),
        'loads_total_kN': float(res.loads_total / 1000.0),
        'residual_kN': float(res.residual / 1000.0),
        'residual_ratio': float(res.residual_ratio),
        'pile_reactions_total_kN': float(getattr(res, 'pile_reactions_total', 0.0) / 1000.0),
        'active_springs': int(res.active_springs.sum()),
        'iterations': int(res.iterations),
        'nlf_audit': getattr(res, 'nlf_audit', None),
    }


def build_base_scenario(config: LabConfig, columns_csv: str) -> Scenario:
    return Scenario(
        name='base_lab',
        Lx=config.Lx,
        Ly=config.Ly,
        nx=config.nx,
        ny=config.ny,
        E=config.E,
        nu=config.nu,
        h=config.h,
        kv=config.kv,
        q=config.q,
        tensionless=config.tensionless,
        columns_csv=columns_csv,
    )


def _build_solver(config: LabConfig, kv: float | None = None, q: float | None = None) -> RadierMindlinWinklerV2:
    is_laje = config.module_name == 'lajes'
    mat = Material(E=config.E, nu=config.nu, h=config.h)
    
    # Se for laje, kv é zero (não há solo)
    # API envia kN/m³, solver quer N/m³
    soil_kv = 0.0 if is_laje else (kv if kv is not None else config.kv)
    if soil_kv < 1e6: # Heurística: se for < 1M, provavelmente está em kN/m³
        soil_kv *= 1000.0
        
    soil = Soil(
        kv=soil_kv, 
        tensionless=config.tensionless if not is_laje else False,
        q_limit=config.q_limit_kPa * 1000.0 if (config.q_limit_kPa and not is_laje) else None
    )

    supports = None
    if is_laje:
        # Carrega pilares como apoios discretos
        col_path = _resolve_columns_csv(config)
        col_df = pd.read_csv(col_path)
        supports = []
        for _, row in col_df.iterrows():
            supports.append({
                'x': row['x'], 'y': row['y'], 
                'kz': 1e16, # Apoio rígido Z
                'krx': 0.0, 'kry': 0.0 # Por enquanto rotulações livres
            })

    # Trata solo heterogêneo se spt_csv existir (apenas para radier)
    kv_map = None
    if not is_laje and config.spt_csv and Path(config.spt_csv).exists():
        from radier_geotechnics import interpolate_kv_map
        tmp_solver = RadierMindlinWinklerV2(PlateModel(Lx=config.Lx, Ly=config.Ly, nx=config.nx, ny=config.ny))
        spt_df = pd.read_csv(config.spt_csv)
        kv_map = interpolate_kv_map(
            tmp_solver.nodes,
            spt_df,
            soil_kv,
            correlation_level=config.spt_correlation_level,
            default_soil_type=config.spt_default_soil_type,
        )

    solver = RadierMindlinWinklerV2(
        PlateModel(
            Lx=config.Lx,
            Ly=config.Ly,
            nx=config.nx,
            ny=config.ny,
            material=mat,
            soil=Soil(
                kv=soil_kv, 
                tensionless=soil.tensionless,
                q_limit=soil.q_limit,
                kv_map=kv_map
            ),
            supports=supports,
            area_loads=[AreaLoad(
                x_min=al['x_min'], 
                y_min=al['y_min'], 
                x_max=al['x_max'], 
                y_max=al['y_max'], 
                q_Pa=al['q_kN'] * 1000.0
            ) for al in config.area_loads] if config.area_loads else None
        )
    )
    
    # Peso próprio do radier: h(m) * 25 kN/m³ * 1000 = Pa
    g_pp = config.h * 25.0 * 1000.0
    
    # Carga acidental: se for < 1000, provavelmente está em kN/m² (API)
    q_val = q if q is not None else config.q
    if q_val < 1000.0:
        q_val *= 1000.0

    solver._q_uniform = q_val + g_pp
        
    return solver


def _build_geotechnical_profile(config: LabConfig) -> dict | None:
    if not config.spt_csv or not Path(config.spt_csv).exists():
        return None

    from radier_geotechnics import build_kv_map_and_metadata

    tmp_solver = RadierMindlinWinklerV2(PlateModel(Lx=config.Lx, Ly=config.Ly, nx=config.nx, ny=config.ny))
    spt_df = pd.read_csv(config.spt_csv)
    _, metadata = build_kv_map_and_metadata(
        tmp_solver.nodes,
        spt_df,
        default_kv=config.kv,
        correlation_level=config.spt_correlation_level,
        default_soil_type=config.spt_default_soil_type,
    )
    metadata['spt_csv'] = str(config.spt_csv)
    return metadata


def _factor_action(service_value: float, gamma_g: float, gamma_q: float, variable_share: float) -> float:
    permanent_share = max(0.0, 1.0 - variable_share)
    return service_value * (permanent_share * gamma_g + variable_share * gamma_q)


def _build_factored_column_loads(columns_csv: Path, gamma_g: float, gamma_q: float, variable_share: float) -> tuple[pd.DataFrame, np.ndarray]:
    df = pd.read_csv(columns_csv).copy()
    
    # Majorando forças verticais
    df['p_design'] = _factor_action(df['p'].to_numpy(dtype=float), gamma_g, gamma_q, variable_share)
    
    # Majorando momentos se existirem
    for m in ['mx', 'my']:
        if m in df.columns:
            df[f'{m}_design'] = _factor_action(df[m].to_numpy(dtype=float), gamma_g, gamma_q, variable_share)
        else:
            df[f'{m}_design'] = 0.0

    loads_cols = ['x', 'y', 'p_design', 'mx_design', 'my_design']
    return df, df[loads_cols].to_numpy(dtype=float)


def run_deterministic_fem(config: LabConfig) -> str:
    validate_lab_config(config)
    out = ensure_directory(config.output_dir)
    columns_csv = _resolve_columns_csv(config)
    
    # Carregar Mapas Geométricos Avançados (Lajes Lab)
    h_per_element = None
    if config.h_map_csv and Path(config.h_map_csv).exists():
        h_per_element = np.loadtxt(config.h_map_csv, delimiter=',')
        
    opening_mask = None
    if config.openings_csv and Path(config.openings_csv).exists():
        opening_mask = np.loadtxt(config.openings_csv, delimiter=',').astype(bool)

    solver = _build_solver(config)
    column_loads = read_column_loads_csv(columns_csv)
    
    if config.concrete_nonlinear:
        from concrete_nonlinear import ConcreteNonlinearEngine
        nlf_res = ConcreteNonlinearEngine.run_iterative_analysis(
            solver, 
            column_loads, 
            piles=config.piles,
            long_term=config.service_mode == 'verificacao_servico',
            h_per_element=h_per_element,
            opening_mask=opening_mask
        )
        res = nlf_res['result']
        # Anexa auditoria NLF ao resultado para o relatório
        res.nlf_audit = nlf_res['audit_trail']
    elif config.ssi_enabled:
        ssi = SSIPseudoCoupled(solver.model)
        ssi_res = ssi.solve_iterative(column_loads=column_loads)
        res = ssi_res['result']
    else:
        superstructure_stiffness = None
        if config.advanced_ssi_enabled:
            from ssi_advanced import SuperstructureParams
            superstructure_stiffness = {
                'params': SuperstructureParams(n_floors=config.ssi_n_floors)
            }
            
        res = solver.solve(
            column_loads, 
            piles=config.piles, 
            superstructure_stiffness=superstructure_stiffness
        )

    solver.export_element_results_csv(res, out / 'radier_v2_elements.csv')
    solver.export_nodal_results_csv(res, out / 'radier_v2_nodes.csv')

    summary = _summarize_solver_result(res)
    
    # Verificação de estabilidade numérica do radier
    if summary['residual_ratio'] > 0.01:
        raise NumericalFailureError(f"O modelo de radier não convergiu (resíduo: {summary['residual_ratio']:.2%}). Verifique as cargas e rigidez do solo.", module="radier_solver")

    return write_json(out / f'{config.base_name}_deterministic_summary.json', summary)


def run_research_batch(config: LabConfig) -> str:
    validate_lab_config(config)
    out = ensure_directory(config.output_dir)
    columns_csv = _resolve_columns_csv(config)

    scenarios = create_research_scenarios(str(columns_csv))
    df = ForensicPostProcessor(str(out)).run_batch(scenarios)

    csv_path = out / f'{config.base_name}_batch_kpis.csv'
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def run_sensitivity_analysis(config: LabConfig) -> str:
    """Executa cenários kv/2, kv, 2*kv e gera envoltória."""
    out = ensure_directory(config.output_dir)
    columns_csv = _resolve_columns_csv(config)
    loads = read_column_loads_csv(columns_csv)
    
    factors = {'solo_mole': 0.5, 'solo_medio': 1.0, 'solo_rigido': 2.0}
    results = []
    
    for name, f in factors.items():
        solver = _build_solver(config, kv=config.kv * f)
        res = solver.solve(loads)
        summary = _summarize_solver_result(res)
        summary['scenario'] = name
        summary['kv_factor'] = f
        results.append(summary)
        
        # Salva resultados nodais de cada um para envoltória futura se necessário
        solver.export_nodal_results_csv(res, out / f'sensitivity_{name}_nodes.csv')

    env_df = pd.DataFrame(results)
    path = out / f'{config.base_name}_sensitivity_envelope.csv'
    env_df.to_csv(path, index=False)
    return str(path)


def run_inverse_and_uq(config: LabConfig) -> dict:
    validate_lab_config(config)
    out = ensure_directory(config.output_dir)
    columns_csv = _resolve_columns_csv(config)
    measurements_csv = _resolve_measurements_csv(config)
    measurements = read_measurements_csv(measurements_csv)

    base = build_base_scenario(config, str(columns_csv))
    engine = InverseCalibrationAndUQ(str(out))

    calib = engine.calibrate_kv_grid(
        base,
        measurements,
        kv_values=list(np.geomspace(15e6, 80e6, 10)),
    )

    uq_df = engine.monte_carlo_uncertainty(base, n=80, seed=123)
    uq_df.to_csv(out / f'{config.base_name}_v22_uq_samples.csv', index=False)

    summary = {
        'best_kv': calib.best_kv,
        'best_rmse_mm': calib.best_rmse_mm,
        'best_mae_mm': calib.best_mae_mm,
        'mc_wmax_p95_mm': float(np.percentile(uq_df['w_max_mm'], 95)),
        'mc_qmax_p95_kPa': float(np.percentile(uq_df['qsoil_max_kPa'], 95)),
    }

    write_json(out / f'{config.base_name}_v22_summary.json', summary)
    return summary


def run_bayesian(config: LabConfig) -> dict:
    validate_lab_config(config)
    out = ensure_directory(config.output_dir)
    columns_csv = _resolve_columns_csv(config)
    measurements_csv = _resolve_measurements_csv(config)
    measurements = read_measurements_csv(measurements_csv)

    base = build_base_scenario(config, str(columns_csv))
    engine = BayesianKvCalibration(str(out))

    res = engine.run_grid_bayes(
        base,
        measurements,
        np.geomspace(15e6, 80e6, 16),
        np.linspace(0.5, 6.0, 18),
    )

    summary = dataclass_to_dict(res)
    write_json(out / f'{config.base_name}_v23_bayes_summary.json', summary)
    return summary


def run_design_checks(config: LabConfig) -> dict:
    validate_lab_config(config)
    out = ensure_directory(config.output_dir)
    results = {}
    is_laje = config.module_name.lower() in ['laje', 'lajes']
    design_cfg = DesignConfig(fck=config.fck, fyk=config.fyk, h=config.h, cover=config.cover)
    columns_csv = _resolve_columns_csv(config)
    nodes_csv = out / 'radier_v2_nodes.csv'
    service_elements_csv = out / 'radier_v2_elements.csv'
    combinations = get_combination_set(config.code_profile)
    gamma_g = combinations['ultimate'].get('G', 1.4)
    gamma_q = combinations['ultimate'].get('Q', 1.4)
    
    # Peso próprio do radier: h(m) * 25 kN/m³ * 1000 = N/m²
    g_pp = config.h * 25.0 * 1000.0
    
    # Fatoração das ações (q do usuário majorado conforme variável/permanente, e peso próprio sempre permanente)
    q_user_elu = _factor_action(config.q, gamma_g, gamma_q, config.uniform_load_is_variable)
    q_elu = q_user_elu + (g_pp * gamma_g)
    columns_df, factored_column_loads = _build_factored_column_loads(
        columns_csv,
        gamma_g,
        gamma_q,
        config.column_load_is_variable,
    )
    design_columns_csv = out / 'columns_design_elu.csv'
    columns_df.to_csv(design_columns_csv, index=False)

    design_solver = _build_solver(config, q=q_elu)
    
    if config.ssi_enabled:
        ssi = SSIPseudoCoupled(design_solver.model)
        ssi_res = ssi.solve_iterative(column_loads=factored_column_loads)
        design_res = ssi_res['result']
    else:
        # Aplicar efeito de grupo nas estacas antes do solve
        piles_for_solve = config.piles
        if config.pile_group_enabled and config.piles and len(config.piles) >= 2:
            from pile_group_interaction import PileGroupConfig, apply_group_effect_to_piles, compute_group_efficiency
            pg_cfg = PileGroupConfig(Es_kPa=config.pile_group_Es_kPa)
            pg_result = compute_group_efficiency(config.piles, pg_cfg)
            piles_for_solve = apply_group_effect_to_piles(config.piles, pg_cfg)
            results['pile_group_analysis'] = {
                'group_efficiency': pg_result['group_efficiency'],
                'settlement_amplification': pg_result['settlement_amplification'],
                'classification': pg_result['classification'],
                'summary': pg_result['summary'],
                'efficiency_per_pile': pg_result['efficiency_per_pile'],
            }
            write_json(out / f'{config.base_name}_pile_group.json', results['pile_group_analysis'])

        design_res = design_solver.solve(factored_column_loads, piles=piles_for_solve)
    design_elements_csv = out / 'radier_design_elements_elu.csv'
    design_solver.export_element_results_csv(design_res, design_elements_csv)

    if design_elements_csv.exists():
        # Redistribuição de Momentos (Estádio III) — se habilitada
        if config.moment_redistribution:
            from concrete_nonlinear import redistribute_moments, RedistributionConfig
            design_df = pd.read_csv(design_elements_csv)
            redist_cfg = RedistributionConfig(
                enabled=True,
                max_redistribution_pct=config.redistribution_max_pct
            )
            redist = redistribute_moments(
                design_df['mx_Nm_per_m'].to_numpy(),
                design_df['my_Nm_per_m'].to_numpy(),
                design_df['mxy_Nm_per_m'].to_numpy(),
                config.fck, config.h, redist_cfg
            )
            # Sobrescrever momentos no CSV com os redistribuídos
            design_df['mx_Nm_per_m'] = redist['mx']
            design_df['my_Nm_per_m'] = redist['my']
            design_df.to_csv(design_elements_csv, index=False)
            results['moment_redistribution'] = {
                'applied': redist['redistribution_applied'],
                'peak_reduction_pct': redist['peak_reduction_pct'],
                'n_peaks': redist.get('n_peaks', 0),
                'element_states': redist.get('element_states', {}),
                'summary': redist['summary'],
            }
            write_json(out / f'{config.base_name}_redistribution.json', results['moment_redistribution'])

        flex_csv, steel_metrics = design_flexure_from_elements(
            str(design_elements_csv),
            design_cfg,
            out_csv=str(out / 'radier_design_flexure_v2.csv'),
        )
        results['flexure_design_file'] = flex_csv
        results['design_elements_file'] = str(design_elements_csv)
        results['reinforcement_metrics'] = steel_metrics
        write_json(out / f'{config.base_name}_reinforcement_metrics.json', steel_metrics)

    if service_elements_csv.exists():
        check_serviceability_flexure(
            str(service_elements_csv),
            str(out / 'radier_design_flexure_v2.csv'),
            design_cfg,
            out_csv=str(out / 'radier_serviceability_check_v2.csv'),
        )
        results['serviceability_check_file'] = str(out / 'radier_serviceability_check_v2.csv')

    if columns_csv.exists():
        check_punching(
            str(design_columns_csv),
            design_cfg,
            out_csv=str(out / 'radier_punching_check_v2.csv'),
            nodes_csv=str(nodes_csv),
            flexure_design_csv=str(out / 'radier_design_flexure_v2.csv'),
        )
        results['punching_check_file'] = str(out / 'radier_punching_check_v2.csv')
        results['design_columns_file'] = str(design_columns_csv)

    # 5.5 Refinamento de Lajes (NBR 6118:2023) — Se for Laje
    if is_laje:
        from slab_design_engine import SlabDesignEngine, SlabDesignConfig
        from slab_serviceability import SlabServiceabilityEngine, ServiceabilityConfig
        
        # Recalcular flecha com Branson
        if results.get('serviceability_check_file'):
            df_serv = pd.read_csv(results['serviceability_check_file'])
            # Exemplo: aplicando Branson no ponto de flecha máxima
            # No futuro iterar sobre todos os elementos para mapa de rigidez
            max_w_idx = df_serv['w_m'].idxmax()
            ma_max = df_serv.loc[max_w_idx, 'mx_Nm_per_m'] / 1000.0 # kNm/m
            as_max = df_serv.loc[max_w_idx, 'Asx_bottom_adot_cm2_m']
            
            serv_cfg = ServiceabilityConfig(fck=config.fck, h=config.h)
            branson = SlabServiceabilityEngine.calculate_branson_inertia(ma_max, as_max, serv_cfg)
            alpha_f = SlabServiceabilityEngine.get_alpha_f()
            
            results['branson_audit'] = {
                'ma_kNm_m': ma_max,
                'as_cm2_m': as_max,
                'Ie_Ic_ratio': branson['reduction_factor'],
                'alpha_f_creep': alpha_f,
                'flecha_imediata_corr_mm': df_serv.loc[max_w_idx, 'w_m'] * 1000.0 / branson['reduction_factor'],
                'flecha_longo_prazo_mm': (df_serv.loc[max_w_idx, 'w_m'] * 1000.0 / branson['reduction_factor']) * (1 + alpha_f)
            }
    # 6. Geração de Prancha DXF (Detalhamento)
    try:
        from dxf_engine import RadierDXFEngine
        from radier_detailing import DetailingEngine
        
        # Pega as armaduras médias/adotadas para a malha base
        df_flex = pd.read_csv(out / 'radier_design_flexure_v2.csv')
        as_inf_x = df_flex['Asx_bottom_adot_cm2_m'].median()
        as_inf_y = df_flex['Asy_bottom_adot_cm2_m'].median()
        
        det_inf_x = DetailingEngine.suggest_reinforcement(as_inf_x, 12.5)
        
        dxf_path = out / f'{config.base_name}_detailing.dxf'
        dxf = RadierDXFEngine(str(dxf_path), config.Lx, config.Ly)
        dxf.draw_outline()
        dxf.draw_columns(factored_column_loads)
        dxf.draw_dimensions()
        
        # Desenha malha inferior
        dxf.draw_mesh('ARM_INF', det_inf_x['spacing'] / 100.0, det_inf_x['text'] + " INF")
        
        # Novo: Prancha Executiva (Carimbo e Listagem)
        dxf.draw_title_block(config.base_name, config.client_profile, "Radier Lab Professional")
        dxf.draw_bar_list(steel_metrics)
        
        # Desenha reforços de punção se existirem
        if 'punching_check_file' in results:
            df_puncao = pd.read_csv(results['punching_check_file'])
            df_cols = pd.read_csv(design_columns_csv)
            puncao_list = []
            for _, row in df_puncao.iterrows():
                if row['Asw_req_cm2'] > 0:
                    c_row = df_cols[df_cols['id'] == row['id']].iloc[0]
                    puncao_list.append({
                        'x': c_row['x'], 'y': c_row['y'], 
                        'bx': c_row['bx'], 'by': c_row['by'], 
                        'status': 'REFORÇO'
                    })
            dxf.draw_punching_reinforcement(puncao_list, config.h - config.cover)

        dxf.save()
        results['dxf_detailing_file'] = str(dxf_path)

        # Novo: Manifesto BIM
        from bim_engine import BIMCoordinator
        bim = BIMCoordinator(config.output_dir)
        results['bim_manifest_file'] = bim.export_structural_manifest(config, results)

    except Exception as e:
        print(f"Erro no Detalhamento CAD/BIM: {e}")
        print(f"Erro ao gerar DXF: {e}")

    # 7. Punção Complexa (Aberturas/Shafts)
    if config.openings and 'punching_check_file' in results:
        try:
            from punching_complex import Opening, check_complex_punching, format_complex_punching_report
            df_punch = pd.read_csv(results['punching_check_file'])
            df_cols = pd.read_csv(design_columns_csv)
            
            openings_objs = [Opening(**o) if isinstance(o, dict) else o for o in config.openings]
            complex_results = check_complex_punching(
                df_cols, openings_objs, design_cfg,
                df_punch['u1_m'].to_numpy(),
                df_punch['tau_sd_MPa'].to_numpy(),
                df_punch['tau_rd1_MPa'].to_numpy() if 'tau_rd1_MPa' in df_punch.columns else np.full(len(df_punch), df_punch['tau_rd1_MPa'].iloc[0]),
            )
            report = format_complex_punching_report(complex_results)
            results['complex_punching'] = report
            write_json(out / f'{config.base_name}_complex_punching.json', report)
        # --- Fase: AI Structural Copilot (M5-Master) ---
        except Exception as e:
            # Erro silencioso para não quebrar o pipeline principal
            results['complex_punching_error'] = str(e)
            
    # --- Fase: AI Structural Copilot (M5-Master) ---
    if config.service_mode == 'dimensionamento':
        try:
            from ai_copilot import AICopilot
            copilot = AICopilot()
            # Simplificando dados para o diagnóstico AI
            diag_data = {
                "w_max": float(results.get('w_max_mm', 0)),
                "fck": float(config.fck),
                "h": float(config.h),
                "max_bar_diam": 25.0,
                "min_bar_diam": 10.0
            }
            results['ai_copilot_diagnosis'] = copilot.generate_expert_report(diag_data)
        except Exception as e:
            results['ai_copilot_error'] = f"Falha no diagnóstico AI: {str(e)}"
    
    # 8. Análise de Adensamento Temporal
    if config.consolidation_enabled:
        try:
            from consolidation_engine import ConsolidationConfig, ConsolidationLayer, run_consolidation_analysis
            layers = config.consolidation_layers or [ConsolidationLayer()]
            consol_cfg = ConsolidationConfig(
                layers=layers,
                delta_sigma_kPa=config.consolidation_delta_sigma_kPa
            )
            consol_result = run_consolidation_analysis(consol_cfg)
            results['consolidation_analysis'] = consol_result
            write_json(out / f'{config.base_name}_consolidation.json', consol_result)
        except Exception as e:
            print(f"Erro na análise de adensamento: {e}")

    results['design_combination'] = {'gamma_g': gamma_g, 'gamma_q': gamma_q, 'q_elu': q_elu}

    return results


def run_full_pipeline_demo(config: LabConfig | None = None) -> dict:
    config = config or LabConfig()
    validate_lab_config(config)

    # Sequência orientada a dimensionamento:
    # 1) análise de serviço determinística
    # 2) verificações e dimensionamento (ELU + ELS)
    # 3) trilhas de pesquisa (batch, inversa, bayes)
    det_file = run_deterministic_fem(config)
    design_files = run_design_checks(config)
    sensitivity_file = run_sensitivity_analysis(config)
    batch_file = run_research_batch(config)
    inv_summary = run_inverse_and_uq(config)
    bayes_summary = run_bayesian(config)

    det_summary = read_json(det_file)
    is_laje = config.module_name.lower() in ['laje', 'lajes']
    master = {
        'pipeline_sequence': [
            'deterministic_service_analysis',
            'design_checks_elu_els',
            'sensitivity_envelope',
            'research_batch',
            'inverse_and_uq',
            'bayesian_calibration',
        ],
        # Keys para o frontend (Case Sensitive)
        'Lx': config.Lx,
        'Ly': config.Ly,
        'h': config.h,
        'kv': config.kv,
        'lx': config.Lx,
        'ly': config.Ly,
        'fck': config.fck,
        'area_m2': config.Lx * config.Ly,
        'volume_m3': config.Lx * config.Ly * config.h,
        'line_supports': [ls.model_dump() if hasattr(ls, 'model_dump') else ls for ls in (config.line_supports or [])],
        'pillars': [p.model_dump() if hasattr(p, 'model_dump') else p for p in (config.pillars or [])],
        'system_type': 'laje' if is_laje else 'radier',
        'total_load_kN': det_summary.get('loads_total_kN', 0.0),
        'total_p_kN': det_summary.get('column_load_kN', 0.0),
        'deterministic_summary_file': det_file,
        'sensitivity_envelope_file': sensitivity_file,
        'design_outputs': design_files,
        'batch_kpis_file': batch_file,
        'inverse_and_uq_summary': inv_summary,
        'bayesian_summary': bayes_summary,
    }
    print(f"DEBUG: Master Summary built for {master['system_type']} - Lx={master['Lx']}, h={master['h']}")
    is_laje_internal = config.module_name.lower() in ['laje', 'lajes']
    geotechnical_profile = _build_geotechnical_profile(config) if not is_laje_internal else None

    # Cálculo do Comparativo Analítico (Normativo Simplificado)
    analytical_comp = {}
    try:
        punching_df = pd.read_csv(design_files['punching_check_file']) if 'punching_check_file' in design_files else None
        # Carga total uniforme em kPa (Acidental + Peso Próprio)
        q_accidental_kPa = config.q / 1000.0
        q_self_weight_kPa = config.h * 25.0
        q_total_kPa = q_accidental_kPa + q_self_weight_kPa
        
        analytical_comp = analytical.calculate_analytical_comparison(
            det_summary,
            analytical.AnalyticalConfig(
                Lx=config.Lx, 
                Ly=config.Ly, 
                q_uniform_Pa=q_total_kPa * 1000.0,
                pillars=config.pillars,
                area_loads=config.area_loads
            ),
            punching_mef_df=punching_df
        )
    except Exception as e:
        print(f"Erro ao calcular comparativo analitico: {e}")

    master['memorial_summary_file'] = write_memorial_summary(
        config, 
        det_summary, 
        config.output_dir,
        analytical_comparison=analytical_comp,
        geotechnical_profile=geotechnical_profile,
    )
    master['report_file'] = build_markdown_report(config, master, config.output_dir)
    master['didactic_guide_file'] = build_didactic_guide(config, master, config.output_dir)
    master['artifact_manifest_file'] = build_artifact_manifest(config, master, config.output_dir)
    write_json(Path(config.output_dir, f'{config.base_name}_master_summary.json'), master)
    return master


if __name__ == '__main__':
    print(write_json(Path('output') / 'radier_lab_console_summary.json', run_full_pipeline_demo()))
