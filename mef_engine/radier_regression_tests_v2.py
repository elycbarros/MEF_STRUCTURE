from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import tempfile

import numpy as np
import pandas as pd

from radier_lab_v24 import (
    LabConfig,
    build_base_scenario,
    run_deterministic_fem,
    run_full_pipeline_demo,
)
from radier_solver_v2 import (
    Material,
    PlateModel,
    RadierMindlinWinklerV2,
    Soil,
    read_column_loads_csv,
    write_example_column_csv,
)
from radier_solver_v22 import CalibrationResult
from radier_solver_v23 import BayesianKvCalibration
from radier_design_v2 import check_angular_distortion
from radier_validation import validate_columns_dataframe, validate_lab_config, validate_measurements_dataframe, validate_spt_dataframe
from radier_geotech_reference_matrix import get_calibration_reference_matrix
from schemas.core import ConfigInput
from routes.core_helpers import build_executive_decision_summary, build_foundation_recommendation


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _build_measurements_from_solver(
    output_dir: Path,
    kv_true: float,
    sample_points: list[tuple[float, float]],
    q: float = 140e3,
) -> pd.DataFrame:
    columns_csv = output_dir / 'columns_example.csv'
    write_example_column_csv(columns_csv)

    solver = RadierMindlinWinklerV2(
        PlateModel(
            Lx=24.0,
            Ly=24.0,
            nx=21,
            ny=21,
            material=Material(E=32e9, nu=0.20, h=0.70),
            soil=Soil(kv=kv_true, tensionless=True),
        )
    )
    solver._q_uniform = q
    result = solver.solve(read_column_loads_csv(columns_csv))

    rows = []
    for x, y in sample_points:
        distances = ((result.nodes[:, 0] - x) ** 2 + (result.nodes[:, 1] - y) ** 2) ** 0.5
        rows.append({'x': x, 'y': y, 'w_mm': float(result.disp[distances.argmin(), 0] * 1000.0)})
    return pd.DataFrame(rows)


def _test_bayesian_recovers_known_kv(output_dir: Path) -> dict:
    kv_true = 40e6
    sample_points = [(4.0, 4.0), (12.0, 4.0), (12.0, 12.0), (20.0, 20.0)]
    measurements = _build_measurements_from_solver(output_dir, kv_true=kv_true, sample_points=sample_points)
    columns_csv = output_dir / 'columns_example.csv'

    scenario = build_base_scenario(LabConfig(output_dir=str(output_dir)), str(columns_csv))
    engine = BayesianKvCalibration(str(output_dir))
    kv_grid = np.array([20e6, 30e6, 40e6, 50e6, 60e6], dtype=float)
    sigma_grid = np.array([0.5, 1.0, 2.0], dtype=float)

    result = engine.run_grid_bayes(scenario, measurements, kv_grid, sigma_grid)

    _assert(result.kv_map == kv_true, f'Bayes MAP esperado {kv_true}, obtido {result.kv_map}')
    _assert(result.kv_p10 <= result.kv_p50 <= result.kv_p90, 'Quantis bayesianos inconsistentes')
    _assert(abs(sum(result.marginal_kv_probs) - 1.0) < 1e-9, 'Probabilidades marginais não somam 1')
    return asdict(result)


def _test_deterministic_regression(output_dir: Path) -> dict:
    config = LabConfig(output_dir=str(output_dir), base_name='regression_case')
    summary_path = Path(run_deterministic_fem(config))
    summary = json.loads(summary_path.read_text(encoding='utf-8'))

    # Calibração para RadierMindlinWinklerV2 (Mindlin-Reissner)
    _assert(4.5 < summary['w_max_mm'] < 6.5, f"w_max_mm fora da faixa: {summary['w_max_mm']}")
    _assert(180.0 < summary['qsoil_max_kPa'] < 240.0, f"qsoil_max_kPa fora da faixa: {summary['qsoil_max_kPa']}")
    _assert(summary['residual_ratio'] < 1e-6, f"Residual ratio alto: {summary['residual_ratio']}")
    _assert(summary['active_springs'] > 0, 'Nenhuma mola ativa no caso determinístico')
    return summary


def _test_full_pipeline_outputs(output_dir: Path) -> dict:
    config = LabConfig(output_dir=str(output_dir), base_name='pipeline_case')
    result = run_full_pipeline_demo(config)
    _assert('pipeline_sequence' in result, 'Pipeline sem sequência declarada')
    _assert(
        result['pipeline_sequence'][:2] == ['deterministic_service_analysis', 'design_checks_elu_els'],
        'Ordem inicial da esteira não está orientada a dimensionamento',
    )

    deterministic_summary = Path(result['deterministic_summary_file'])
    batch_file = Path(result['batch_kpis_file'])
    flexure_file = Path(result['design_outputs']['flexure_design_file'])
    punching_file = Path(result['design_outputs']['punching_check_file'])
    design_elements_file = Path(result['design_outputs']['design_elements_file'])
    design_columns_file = Path(result['design_outputs']['design_columns_file'])
    serviceability_file = Path(result['design_outputs']['serviceability_check_file'])
    report_file = Path(result['report_file'])
    manifest_file = Path(result['artifact_manifest_file'])
    memorial_file = Path(result['memorial_summary_file'])

    for path in [deterministic_summary, batch_file, flexure_file, punching_file, design_elements_file, design_columns_file, serviceability_file, report_file, manifest_file, memorial_file]:
        _assert(path.exists(), f'Arquivo esperado não encontrado: {path}')

    batch_df = pd.read_csv(batch_file)
    flexure_df = pd.read_csv(flexure_file)
    punching_df = pd.read_csv(punching_file)
    serviceability_df = pd.read_csv(serviceability_file)
    _assert(len(batch_df) == 4, f'Lote paramétrico deveria ter 4 cenários, recebeu {len(batch_df)}')
    _assert((punching_df['ratio'] < 1.0).all(), 'Há relação de punção acima de 1.0 no exemplo')
    _assert(set(punching_df['local']).issubset({'interior', 'borda', 'canto'}), 'Local de punção inválido')
    _assert((flexure_df['Asx_bottom_adot_cm2_m'] >= flexure_df['Asx_bottom_req_cm2_m']).all(), 'Asx inferior adotada ficou abaixo da requerida')
    _assert((flexure_df['Asx_top_adot_cm2_m'] >= flexure_df['Asx_top_req_cm2_m']).all(), 'Asx superior adotada ficou abaixo da requerida')
    _assert((flexure_df['Asy_bottom_adot_cm2_m'] >= flexure_df['Asy_bottom_req_cm2_m']).all(), 'Asy inferior adotada ficou abaixo da requerida')
    _assert((flexure_df['Asy_top_adot_cm2_m'] >= flexure_df['Asy_top_req_cm2_m']).all(), 'Asy superior adotada ficou abaixo da requerida')
    _assert((punching_df['Ved_net_kN'] <= punching_df['Ved_gross_kN']).all(), 'Ved líquido de punção não pode superar Ved bruto')
    _assert((serviceability_df['wk_est_x_mm'] >= 0.0).all(), 'wk x inválido')
    _assert((serviceability_df['wk_est_y_mm'] >= 0.0).all(), 'wk y inválido')
    report_text = report_file.read_text(encoding='utf-8')
    memorial_data = json.loads(memorial_file.read_text(encoding='utf-8'))
    _assert(memorial_data['base_normativa']['perfil_principal']['label'] == 'ABNT NBR 6118:2023', 'Perfil normativo principal inesperado')
    _assert(len(memorial_data['base_normativa'].get('checklist_detalhado', [])) >= 5, 'Checklist normativo detalhado insuficiente')
    _assert('benchmark_evidences' in memorial_data, 'Memorial sem evidências de benchmark')
    _assert('checklist_profissional' in memorial_data, 'Memorial sem checklist profissional')
    _assert('maturity_score' in memorial_data, 'Memorial sem score de maturidade')
    _assert(
        'matriz_calibracao_referencias' in memorial_data.get('dados_do_solo', {}),
        'Memorial sem matriz de calibracao por referencias',
    )
    matrix = memorial_data['dados_do_solo']['matriz_calibracao_referencias']
    _assert('project_weighting' in matrix, 'Matriz sem bloco de pesos por tipo de projeto')
    _assert(matrix['project_weighting']['project_type'] == 'edificios_altos', 'Tipo de projeto padrao inesperado')
    _assert(memorial_data['benchmark_evidences']['all_passed'] is True, 'Benchmark interno não passou no caso de regressão')
    _assert(
        memorial_data['checklist_profissional']['status'] in {
            'apto_para_estudo_preliminar_profissional',
            'apto_com_restricoes',
            'nao_apto_requer_revisao_tecnica',
        },
        'Status profissional inválido',
    )
    maturity = memorial_data['maturity_score']
    _assert(0.0 <= maturity['score_0_5'] <= 5.0, 'Score 0-5 fora da faixa')
    _assert(0.0 <= maturity['score_0_100'] <= 100.0, 'Score 0-100 fora da faixa')
    _assert(maturity['version_id'] == 'pipeline_case', 'Score com version_id inesperado')
    _assert(result['design_outputs']['design_combination']['gamma_g'] >= 1.0, 'Gamma G inválido')
    _assert(result['design_outputs']['design_combination']['gamma_q'] >= 1.0, 'Gamma Q inválido')
    _assert('Verificacoes Geotecnicas' in report_text, 'Relatório não contém seção geotécnica')
    _assert('Base Normativa' in report_text, 'Relatório não contém seção normativa')
    _assert('Sequencia de Calculo' in report_text, 'Relatório não contém sequência de cálculo')
    _assert('Checklist Normativo Detalhado' in report_text, 'Relatório sem checklist normativo detalhado')
    _assert('Verificacoes Estruturais' in report_text, 'Relatório não contém seção estrutural')
    _assert('Leitura Orientada pelo Modo' in report_text, 'Relatório não contém seção orientada por modo')
    _assert('Avaliacao Tecnica do Modo' in report_text, 'Relatório não contém avaliação técnica por modo')
    _assert('Leitura de Pesquisa' in report_text, 'Relatório não contém seção de pesquisa')
    _assert('Evidencias de Benchmark' in report_text, 'Relatório sem evidências de benchmark')
    _assert('Checklist Profissional' in report_text, 'Relatório sem checklist profissional')
    _assert('Score de Maturidade' in report_text, 'Relatório sem score de maturidade')
    _assert('Resumo Executivo' in report_text, 'Relatório sem resumo executivo')
    _assert('Matriz de Confiabilidade' in report_text, 'Relatório sem matriz de confiabilidade')
    _assert('Metodologia Geotecnica' in report_text, 'Relatório sem metodologia geotécnica')
    _assert('Criterios de Servico' in report_text, 'Relatório sem critérios de serviço')
    _assert('Premissas e Limitacoes' in report_text, 'Relatório sem premissas e limitações')
    _assert('Rastreabilidade dos Artefatos' in report_text, 'Relatório sem rastreabilidade dos artefatos')

    return {
        'deterministic_summary_file': str(deterministic_summary),
        'batch_rows': int(len(batch_df)),
        'punching_ratio_max': float(punching_df['ratio'].max()),
        'report_file': str(report_file),
        'memorial_file': str(memorial_file),
    }


def _test_input_validation() -> dict:
    try:
        validate_lab_config(LabConfig(nx=10))
    except ValueError as exc:
        mesh_error = str(exc)
    else:
        raise AssertionError('Validação de malha ímpar deveria falhar.')

    try:
        validate_columns_dataframe(pd.DataFrame([{'x': 1.0, 'y': 2.0, 'p': 3.0}]))
    except ValueError as exc:
        columns_error = str(exc)
    else:
        raise AssertionError('Validação de pilares deveria falhar sem id/bx/by.')

    try:
        validate_measurements_dataframe(pd.DataFrame(columns=['x', 'y', 'w_mm']))
    except ValueError as exc:
        measurements_error = str(exc)
    else:
        raise AssertionError('Validação de medições vazias deveria falhar.')

    try:
        validate_spt_dataframe(pd.DataFrame([{'x': 1.0, 'y': 2.0}]))
    except ValueError as exc:
        spt_error = str(exc)
    else:
        raise AssertionError("Validação SPT deveria falhar sem 'kv' ou 'nspt'.")

    return {
        'mesh_error': mesh_error,
        'columns_error': columns_error,
        'measurements_error': measurements_error,
        'spt_error': spt_error,
    }


def _test_geotech_override_bounds() -> dict:
    matrix = get_calibration_reference_matrix(
        project_type='edificios_altos',
        custom_group_weights={'academico': -2.0, 'mercado': 9.0},
    )
    weights = matrix['project_weighting']['group_weights']
    _assert(abs(weights['academico'] - 0.5) < 1e-12, 'Peso academico deveria ser limitado a 0.5')
    _assert(abs(weights['mercado'] - 1.5) < 1e-12, 'Peso mercado deveria ser limitado a 1.5')
    clamped = set(matrix['project_weighting'].get('clamped_groups', []))
    _assert({'academico', 'mercado'}.issubset(clamped), 'Grupos limitados nao registrados')
    return {
        'academico': weights['academico'],
        'mercado': weights['mercado'],
        'clamped_groups': sorted(clamped),
    }


def _test_angular_distortion_fallback_small_set(output_dir: Path) -> dict:
    columns = pd.DataFrame(
        [
            {'id': 'P01', 'x': 0.0, 'y': 0.0, 'p': 1000.0, 'bx': 0.5, 'by': 0.5},
            {'id': 'P02', 'x': 10.0, 'y': 0.0, 'p': 1000.0, 'bx': 0.5, 'by': 0.5},
        ]
    )
    nodes = pd.DataFrame(
        [
            {'x_m': 0.0, 'y_m': 0.0, 'w_m': 0.001, 'qsoil_Pa': 0.0},
            {'x_m': 10.0, 'y_m': 0.0, 'w_m': 0.002, 'qsoil_Pa': 0.0},
            {'x_m': 0.0, 'y_m': 10.0, 'w_m': 0.0015, 'qsoil_Pa': 0.0},
            {'x_m': 10.0, 'y_m': 10.0, 'w_m': 0.0025, 'qsoil_Pa': 0.0},
        ]
    )
    columns_path = output_dir / 'tmp_small_columns.csv'
    nodes_path = output_dir / 'tmp_small_nodes.csv'
    out_path = output_dir / 'tmp_small_distortion.csv'
    columns.to_csv(columns_path, index=False)
    nodes.to_csv(nodes_path, index=False)

    result_path = check_angular_distortion(str(columns_path), str(nodes_path), out_csv=str(out_path))
    _assert(result_path is not None, 'Fallback de distorcao angular retornou None para 2 pilares.')
    _assert(Path(result_path).exists(), 'Arquivo de distorcao angular nao foi gerado no fallback.')
    dist = pd.read_csv(result_path)
    _assert(len(dist) == 1, f'Esperado 1 par no fallback, obtido {len(dist)}')
    _assert(float(dist['beta'].iloc[0]) > 0.0, 'Beta deveria ser positivo no fallback.')
    return {'rows': int(len(dist)), 'beta': float(dist['beta'].iloc[0])}


def _test_diagnostic_profile_calibration() -> dict:
    memorial = {
        'verificacoes_geotecnicas': {
            'pressao_max_modelo_kPa': 170.0,
            'tensao_admissivel_kPa': 200.0,
            'atende_pressao_max_modelo': True,
        },
        'verificacoes_estruturais': {
            'puncao': {'atende': True, 'ratio_max': 0.82},
        },
        'verificacoes_de_servico': {
            'w_max_mm': 23.0,
            'w_diff_mm': 22.0,
            'wk_x_max_mm': 0.25,
            'wk_y_max_mm': 0.20,
            'wk_limit_mm': 0.30,
            'wk_x_ok': True,
            'wk_y_ok': True,
            'criterios_recalque': {
                'atende_global': True,
                'checks': [
                    {'id': 'recalque_total', 'actual': 23.0, 'limit_max': 50.0},
                    {'id': 'recalque_diferencial', 'actual': 22.0, 'limit_max': 25.0},
                    {'id': 'distorcao_angular', 'actual': 0.0017, 'limit_max': 0.002},
                ],
            },
        },
        'pre_dimensionamento': {'espessura_referencia_m': 0.8},
        'benchmark_evidences': {'all_passed': True, 'blocks_professional_use': False},
        'checklist_profissional': {'status': 'apto_para_estudo_preliminar_profissional'},
    }
    deterministic = {'loads_total_kN': 9000.0}
    field_risk_summary = {'status': 'green'}
    winkler = {'pass': True, 'wmax_over_expected_mean': 0.88}

    conservative_input = ConfigInput(
        h=0.75,
        diagnostic_conservatism='conservative',
        pillars=[{'id': 'P01', 'x': 2.0, 'y': 2.0, 'p_kN': 4200.0, 'bx': 0.5, 'by': 0.5}],
    )
    permissive_input = ConfigInput(
        h=0.75,
        diagnostic_conservatism='permissive',
        pillars=[{'id': 'P01', 'x': 2.0, 'y': 2.0, 'p_kN': 4200.0, 'bx': 0.5, 'by': 0.5}],
    )

    conservative = build_foundation_recommendation(conservative_input, memorial, deterministic, field_risk_summary, winkler)
    permissive = build_foundation_recommendation(permissive_input, memorial, deterministic, field_risk_summary, winkler)
    conservative_decision = build_executive_decision_summary(conservative)
    permissive_decision = build_executive_decision_summary(permissive)

    _assert(
        conservative['technical_level_counts']['total'] > permissive['technical_level_counts']['total'],
        'Perfil conservador deveria gerar mais gatilhos que o permissivo para caso proximo dos limites.',
    )
    _assert(
        conservative['decision_rank'] >= permissive['decision_rank'],
        'Perfil conservador não deveria produzir decisão menos restritiva que o permissivo.',
    )
    _assert(
        conservative['metrics']['differential_settlement_ratio'] is not None,
        'Diagnostico deveria exportar ratio de recalque diferencial.',
    )
    _assert(
        conservative['diagnostic_conservatism']['thresholds']['cracking_alert_ratio'] == 0.75,
        'Limites calibrados de fissuracao não foram exportados.',
    )
    _assert(
        conservative_decision['go_no_go'] in {'hold', 'no_go'},
        'Decisao executiva conservadora deveria segurar ou bloquear avanço.',
    )
    _assert(
        permissive_decision['go_no_go'] in {'conditional_go', 'go_preliminar'},
        'Decisao executiva permissiva deveria permanecer em avanço preliminar ou condicional.',
    )
    return {
        'conservative_triggers': conservative['technical_level_counts']['total'],
        'permissive_triggers': permissive['technical_level_counts']['total'],
        'conservative_classification': conservative['classification'],
        'permissive_classification': permissive['classification'],
        'conservative_go_no_go': conservative_decision['go_no_go'],
        'permissive_go_no_go': permissive_decision['go_no_go'],
    }


def run_tests(output_dir: str) -> dict:
    requested_dir = Path(output_dir)
    requested_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='radier_regression_', dir=requested_dir) as temp_dir:
        temp_path = Path(temp_dir)
        tests = {
            'bayesian_recovers_known_kv': _test_bayesian_recovers_known_kv(temp_path),
            'deterministic_regression': _test_deterministic_regression(temp_path),
            'full_pipeline_outputs': _test_full_pipeline_outputs(temp_path),
            'input_validation': _test_input_validation(),
            'geotech_override_bounds': _test_geotech_override_bounds(),
            'angular_distortion_fallback_small_set': _test_angular_distortion_fallback_small_set(temp_path),
            'diagnostic_profile_calibration': _test_diagnostic_profile_calibration(),
        }

    return {
        'status': 'passed',
        'tests_run': len(tests),
        'output_dir': output_dir,
        'results': tests,
    }
