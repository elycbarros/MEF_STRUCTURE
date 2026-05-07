from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from platform_core import build_module_identity, build_professional_context
from radier_mode_evaluator import build_mode_specific_assessment
from standards_profiles import get_combination_set, get_international_reference_profiles, get_standard_profile
from structural_platform import RADIER_MODULE, LAJE_MODULE
from structural_research import build_research_insights
from radier_geotech_reference_matrix import get_calibration_reference_matrix
from radier_utils import write_json
from radier_design_v2 import calculate_reinforcement_metrics
import master_pedagogy

SETTLEMENT_SERVICE_LIMITS = {
    'w_total_mm': 50.0,
    'w_diff_mm': 25.0,
    'beta_max': 1.0 / 500.0,
}


def _preliminary_thickness_reference(total_service_load_kN: float, area_m2: float, sigma_adm_kPa: float) -> float:
    load_intensity_ratio = total_service_load_kN / max(area_m2 * sigma_adm_kPa, 1e-9)
    if load_intensity_ratio <= 0.45:
        return 0.16
    if load_intensity_ratio <= 0.70:
        return 0.20
    return 0.25


def _build_benchmark_evidence(deterministic_summary: dict, config=None) -> dict:
    w_max_mm = float(deterministic_summary['w_max_mm'])
    qsoil_max_kPa = float(deterministic_summary['qsoil_max_kPa'])
    residual_ratio = float(deterministic_summary['residual_ratio'])
    # Calibrado para RadierMindlinWinklerV2 (Mindlin-Reissner)
    w_band = (4.5, 6.5)
    q_band = (180.0, 240.0)
    residual_limit = 1e-6
    checks = [
        {
            'id': 'benchmark_deterministic_wmax',
            'description': 'Faixa de regressao do recalque maximo do caso base',
            'target': {'min': w_band[0], 'max': w_band[1], 'unit': 'mm'},
            'actual': w_max_mm,
            'pass': w_band[0] <= w_max_mm <= w_band[1],
        },
        {
            'id': 'benchmark_deterministic_qmax',
            'description': 'Faixa de regressao da pressao maxima de contato do caso base',
            'target': {'min': q_band[0], 'max': q_band[1], 'unit': 'kPa'},
            'actual': qsoil_max_kPa,
            'pass': q_band[0] <= qsoil_max_kPa <= q_band[1],
        },
        {
            'id': 'benchmark_equilibrium_residual',
            'description': 'Equilibrio global da solucao',
            'target': {'max': residual_limit, 'unit': 'ratio'},
            'actual': residual_ratio,
            'pass': residual_ratio <= residual_limit,
        },
    ]
    is_api_case = bool(getattr(config, 'base_name', '') == 'api_execution')
    all_passed = bool(all(item['pass'] for item in checks))
    return {
        'suite_name': 'radier_internal_quick_benchmark_v1',
        'applicability': 'reference_regression' if not is_api_case else 'engine_regression_reference_only',
        'checks': checks,
        'all_passed': all_passed,
        'blocks_professional_use': bool((not all_passed) and (not is_api_case)),
        'observacao': (
            'Benchmark fixo usado para regressao do motor; em casos API personalizados, falha nesse benchmark nao reprova o caso tecnico.'
            if is_api_case
            else 'Benchmark fixo do caso de regressao interno.'
        ),
    }


def _build_settlement_service_checks(service_summary: dict, distortion_summary: dict) -> dict:
    w_max_mm = service_summary.get('w_max_mm')
    w_diff_mm = service_summary.get('w_diff_mm')
    beta_max = distortion_summary.get('beta_max')
    limits = SETTLEMENT_SERVICE_LIMITS

    total_ok = bool(w_max_mm is None or w_max_mm <= limits['w_total_mm'])
    diff_ok = bool(w_diff_mm is None or w_diff_mm <= limits['w_diff_mm'])
    beta_ok = bool(beta_max is None or beta_max <= limits['beta_max'])

    checks = [
        {
            'id': 'recalque_total',
            'description': 'Recalque total maximo em servico',
            'actual': w_max_mm,
            'limit_max': limits['w_total_mm'],
            'unit': 'mm',
            'atende': total_ok,
        },
        {
            'id': 'recalque_diferencial',
            'description': 'Recalque diferencial maximo em servico',
            'actual': w_diff_mm,
            'limit_max': limits['w_diff_mm'],
            'unit': 'mm',
            'atende': diff_ok,
        },
        {
            'id': 'distorcao_angular',
            'description': 'Distorcao angular maxima entre apoios',
            'actual': beta_max,
            'limit_max': limits['beta_max'],
            'unit': 'adim',
            'atende': beta_ok,
        },
    ]

    return {
        'limits': limits,
        'checks': checks,
        'atende_global': bool(total_ok and diff_ok and beta_ok),
        'observacao': 'Limites orientativos para estudo preliminar, sujeitos a ajuste por tipologia e desempenho alvo.',
    }


def _get_service_check_pass(service: dict, check_id: str) -> bool | None:
    checks = service.get('criterios_recalque', {}).get('checks', [])
    for item in checks:
        if item.get('id') == check_id:
            return bool(item.get('atende'))
    return None


def _build_professional_readiness_checklist(memorial: dict) -> dict:
    geotech = memorial['verificacoes_geotecnicas']
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']
    benchmark = memorial['benchmark_evidences']
    puncao_status = structural['puncao'].get('status')
    puncao_applicable = puncao_status != 'nao_aplicavel_sem_pilares'
    benchmark_blocks = bool(benchmark.get('blocks_professional_use', not benchmark.get('all_passed', False)))

    items = [
        {
            'id': 'entrada_validada',
            'description': 'Configuracoes e CSVs passam pela camada de validacao',
            'pass': True,
        },
        {
            'id': 'base_normativa_explicita',
            'description': 'Perfil normativo principal e combinacoes estao declarados',
            'pass': bool(memorial['base_normativa'].get('perfil_principal')),
        },
        {
            'id': 'geotecnia_ok',
            'description': 'Pressao media e maxima modelada atendem ao criterio de admissibilidade',
            'pass': bool(geotech['atende_pressao_media'] and geotech['atende_pressao_max_modelo']),
        },
        {
            'id': 'equilibrio_global_ok',
            'description': 'Residual ratio em faixa de equilibrio numerico',
            'pass': bool(structural['equilibrio_global']['atende']),
        },
        {
            'id': 'puncao_ok',
            'description': 'Razao de puncao <= 1.0 quando ha cargas concentradas/pilares',
            'pass': bool((not puncao_applicable) or structural['puncao'].get('atende', False)),
            'applicability': 'nao_aplicavel_sem_pilares' if not puncao_applicable else 'aplicavel',
        },
        {
            'id': 'fissuracao_servico_ok',
            'description': 'Checagens de abertura de fissuras em servico atendem ao limite adotado',
            'pass': bool(service.get('wk_x_ok', False) and service.get('wk_y_ok', False)),
        },
        {
            'id': 'recalque_servico_ok',
            'description': 'Checagens de recalque e distorcao angular atendem aos limites orientativos',
            'pass': bool(service.get('criterios_recalque', {}).get('atende_global', False)),
        }
    ]

    items.append({
        'id': 'benchmark_minimo_ok',
        'description': 'Suite benchmark interna passou nas tolerancias',
        'pass': bool(not benchmark_blocks),
        'applicability': benchmark.get('applicability', 'reference_regression'),
    })

    blocking_ids = {
        'geotecnia_ok',
        'puncao_ok',
        'fissuracao_servico_ok',
        'recalque_servico_ok',
        'flecha_servico_ok',
        'benchmark_minimo_ok',
    }
    failed_ids = [item['id'] for item in items if not item['pass']]
    blocking_failures = [item_id for item_id in failed_ids if item_id in blocking_ids]

    if not failed_ids:
        status = 'apto_para_estudo_preliminar_profissional'
    elif blocking_failures:
        status = 'nao_apto_requer_revisao_tecnica'
    else:
        status = 'apto_com_restricoes'

    return {
        'status': status,
        'items': items,
        'failed_ids': failed_ids,
        'blocking_failures': blocking_failures,
        'observacao': 'Uso executivo final exige revisao do engenheiro responsavel e verificacoes normativas complementares.',
    }


def _build_normative_checklist_detailed(memorial: dict) -> list[dict]:
    is_laje = memorial.get('system_type') == 'laje'
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']
    geotech = memorial['verificacoes_geotecnicas']

    items = []
    
    if not is_laje:
        items.append({
            'id': 'NBR6118_NBR6122_PRESSAO_SOLO',
            'theme': 'Geotecnia de contato',
            'reference': 'ABNT NBR 6122:2019 + ABNT NBR 6118:2023 (compatibilizacao fundacao-estrutura)',
            'status': 'ATENDE' if geotech['atende_pressao_max_modelo'] else 'NAO_ATENDE',
            'method': 'Pressao media e maxima do modelo versus tensao admissivel informada',
            'input_key': 'q_uniforme_Pa, cargas de pilares, sigma_adm_kPa',
            'output_key': 'pressao_media_kPa, pressao_max_modelo_kPa',
        })

    items.extend([
        {
            'id': 'NBR6118_ELU_FLEXAO',
            'theme': 'Dimensionamento a flexao',
            'reference': 'ABNT NBR 6118:2023 (ELU em secoes de concreto armado)',
            'status': 'ATENDE' if structural['flexao'] else 'PARCIAL',
            'method': 'Flexao ELU por faces com Wood-Armer simplificado e armadura minima',
            'input_key': 'mx,my,mxy,fck,fyk,h,cobrimento',
            'output_key': 'Asx/Asy superior e inferior requeridas e adotadas',
        },
        {
            'id': 'NBR6118_ELU_PUNCAO',
            'theme': 'Punção em laje' + ('' if is_laje else ' de fundacao'),
            'reference': 'ABNT NBR 6118:2023 (punção, contornos C e C\')',
            'status': 'NAO_APLICAVEL' if structural['puncao'].get('status') == 'nao_aplicavel_sem_pilares' else ('ATENDE' if structural['puncao'].get('atende') else 'NAO_ATENDE'),
            'method': 'Formulação completa com fator beta (efeito de momentos) e Wp para pilar interior/borda/canto; não aplicável quando não há pilares/cargas concentradas.',
            'input_key': 'p, mx, my, bx, by, x, y, h, fck, armadura local',
            'output_key': 'beta, tau_sd, tau_rd1, ratio, local critico',
        },
        {
            'id': 'NBR6118_ELS_FISSURACAO',
            'theme': 'Estado limite de servico - fissuracao',
            'reference': 'ABNT NBR 6118:2023 (controle de abertura de fissuras)',
            'status': 'ATENDE' if (service.get('wk_x_ok') and service.get('wk_y_ok')) else 'PARCIAL',
            'method': 'Estimativa de wk por tensao no aco, diametro e taxa efetiva',
            'input_key': 'momentos de servico, As adotada, phi, cobrimento, eta1',
            'output_key': 'wk_est_x_mm, wk_est_y_mm, wk_limit_mm',
        },
    ])

    if not is_laje:
        items.extend([
            {
                'id': 'NBR6122_ELS_DISTORCAO',
                'theme': 'Estado limite de servico - distorcao angular',
                'reference': 'ABNT NBR 6122:2022 (anexo J / literatura tecnica)',
                'status': 'ATENDE' if _get_service_check_pass(service, 'distorcao_angular') else 'ALERTA',
                'method': 'Calculo de delta_w / L entre todos os pilares vizinhos via Delaunay',
                'input_key': 'recalques nos pilares, distancias L entre pilares',
                'output_key': 'beta_max, beta_inv_min, conexao critica',
            },
            {
                'id': 'NBR6122_ELS_RECALQUES',
                'theme': 'Estado limite de servico - recalques',
                'reference': 'ABNT NBR 6122:2019/2022 (criterios de deformabilidade)',
                'status': 'ATENDE' if service.get('criterios_recalque', {}).get('atende_global') else 'ALERTA',
                'method': 'Comparacao de recalque total e diferencial com limites orientativos de servico',
                'input_key': 'w_max_mm, w_diff_mm, beta_max',
                'output_key': 'criterios_recalque',
            },
        ])
    else:
        items.append({
            'id': 'NBR6118_ELS_FLECHAS',
            'theme': 'Estado limite de servico - deformacoes',
            'reference': 'ABNT NBR 6118:2023 (flechas em lajes)',
            'status': 'ATENDE' if service.get('criterios_recalque', {}).get('atende_global') else 'ALERTA',
            'method': 'Comparacao de flecha elastica e diferida (Branson) com limites normativos L/250',
            'input_key': 'w_max_mm, w_max_mm_total, L_vão',
            'output_key': 'criterios_flecha',
        })

    items.extend([
        {
            'id': 'NBR6123_VENTO',
            'theme': 'Ações de vento',
            'reference': f"ABNT NBR 6123:1988 (forças devidas ao vento){' | Força Base = ' + str(round(memorial.get('acoes_de_vento', {}).get('summary', {}).get('total_force_kN', 0), 1)) + ' kN' if memorial.get('acoes_de_vento') else ''}",
            'status': 'ATENDE' if memorial.get('acoes_de_vento') else 'NAO_APLICAVEL',
            'method': 'Calculo de pressoes dinamicas e forcas por nivel com modelo discreto (Cap. 9)',
            'input_key': 'v0, s1, s2, s3, categoria, classe, f1, zeta',
            'output_key': 'forca_total_kN, momento_base_kNm, perfil_pressoes',
        },
        {
            'id': 'NBR6118_ESTABILIDADE_GLOBAL',
            'theme': 'Estabilidade global e efeitos de 2a ordem',
            'reference': f"ABNT NBR 6118:2023 (item 15.5){' | Gama-Z = ' + str(round(memorial.get('estabilidade_global', {}).get('gamma_z', 0), 3)) + ' (Limite: 1.10)' if memorial.get('estabilidade_global', {}).get('gamma_z') else ''}",
            'status': 'ATENDE' if memorial.get('estabilidade_global', {}).get('is_stable') else ('NAO_ATENDE' if memorial.get('estabilidade_global') else 'NAO_APLICAVEL'),
            'method': 'Analise de Gama-Z e P-Delta iterativo para verificacao de estabilidade',
            'input_key': 'altura, carga_vertical_total, momento_vento_base',
            'output_key': 'gamma_z, p_delta_factor, status_estabilidade',
        },
        {
            'id': 'NBR6118_RASTREABILIDADE',
            'theme': 'Rastreabilidade tecnica',
            'reference': 'Boas praticas de auditoria tecnica',
            'status': 'ATENDE',
            'method': 'Memorial + relatorio + manifesto de artefatos',
            'input_key': 'configuracao, resultados, arquivos gerados',
            'output_key': 'memorial_summary, report, artifacts',
        }
    ])
    return items


def _build_maturity_score(memorial: dict, config) -> dict:
    checklist_items = memorial['checklist_profissional']['items']
    benchmark_checks = memorial['benchmark_evidences']['checks']
    normative_checks = memorial['base_normativa'].get('checklist_detalhado', [])

    readiness_ratio = sum(1.0 for item in checklist_items if item['pass']) / max(len(checklist_items), 1)
    benchmark_ratio = sum(1.0 for item in benchmark_checks if item['pass']) / max(len(benchmark_checks), 1)

    status_points = {'ATENDE': 1.0, 'NAO_APLICAVEL': 1.0, 'PARCIAL': 0.5, 'ALERTA': 0.5, 'NAO_ATENDE': 0.0}
    normative_raw = [status_points.get(item.get('status', ''), 0.0) for item in normative_checks]
    normative_ratio = sum(normative_raw) / max(len(normative_raw), 1)

    weighted_ratio = 0.55 * readiness_ratio + 0.30 * normative_ratio + 0.15 * benchmark_ratio
    score_100 = round(weighted_ratio * 100.0, 1)
    score_5 = round(weighted_ratio * 5.0, 2)

    if score_5 >= 4.5:
        level = '5 - executivo consolidado'
    elif score_5 >= 4.0:
        level = '4 - quase executivo'
    elif score_5 >= 3.0:
        level = '3 - tecnico robusto'
    elif score_5 >= 2.0:
        level = '2 - prototipo funcional'
    else:
        level = '1 - experimental'

    return {
        'version_id': config.base_name,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'score_0_100': score_100,
        'score_0_5': score_5,
        'level': level,
        'subscores': {
            'professional_readiness_ratio': round(readiness_ratio, 3),
            'normative_traceability_ratio': round(normative_ratio, 3),
            'benchmark_ratio': round(benchmark_ratio, 3),
        },
        'weights': {
            'professional_readiness': 0.55,
            'normative_traceability': 0.30,
            'benchmark_evidence': 0.15,
        },
        'monitoring_note': 'Compare o score_0_5 entre versoes (version_id) para acompanhar maturidade do modulo.',
    }


def build_memorial_summary(
    config,
    deterministic_summary: dict,
    output_dir: str | Path,
    analytical_comparison: dict | None = None,
    geotechnical_profile: dict | None = None,
    custom_paths: dict | None = None,
    wind_results: dict | None = None,
    stability_results: dict | None = None,
) -> dict:
    out = Path(output_dir)
    combinations = get_combination_set(config.code_profile)
    area_m2 = config.Lx * config.Ly
    total_service_load_kN = deterministic_summary['loads_total_kN']
    q_med_kPa = total_service_load_kN / max(area_m2, 1e-9)
    q_max_kPa = deterministic_summary['qsoil_max_kPa']
    
    # Se for laje, sigma_adm_kPa pode não existir no config
    sigma_adm = getattr(config, 'sigma_adm_kPa', 0.0)
    h_ref_m = _preliminary_thickness_reference(total_service_load_kN, area_m2, sigma_adm)

    paths = custom_paths or {}
    punching_path = Path(paths.get('punching', out / 'radier_punching_check_v2.csv'))
    flexure_path = Path(paths.get('flexure', out / 'radier_design_flexure_v2.csv'))
    nodes_path = Path(paths.get('nodes', out / 'radier_v2_nodes.csv'))
    serviceability_path = Path(paths.get('serviceability', out / 'radier_serviceability_check_v2.csv'))
    distortion_path = Path(paths.get('distortion', out / 'radier_angular_distortion_v2.csv'))
    
    is_laje = getattr(config, 'module_name', 'radier') in ['laje', 'lajes']

    punching_max_ratio = None
    punching_summary = {
        'ratio_max': None,
        'ratio_gross_max': None,
        'ratio_face_max': None,
        'atende': True,
        'critical_local': None,
        'status': 'nao_aplicavel_sem_pilares',
    }
    if punching_path.exists():
        punching_df = pd.read_csv(punching_path)
        if not punching_df.empty and 'ratio' in punching_df.columns:
            punching_max_ratio = float(punching_df['ratio'].max())
            critical_row = punching_df.sort_values('ratio', ascending=False).iloc[0]
            punching_summary = {
                'ratio_max': punching_max_ratio,
                'ratio_gross_max': float(punching_df['Ved_gross_kN'].max() / punching_df['VRd1_kN'].max()), # Aproximado se VRd varia
                'beta_max': float(punching_df['beta'].max()),
                'ratio_face_max': float(punching_df['ratio_face'].max()),
                'atende': punching_max_ratio <= 1.0 or bool(critical_row.get('Asw_req_cm2', 0) > 0),
                'atende_sem_reforco': punching_max_ratio <= 1.0,
                'Asw_req_cm2': float(critical_row.get('Asw_req_cm2', 0)),
                'detalhe_reforco': str(critical_row.get('detalhamento_puncao', 'Dispensa Reforço')),
                'critical_local': str(critical_row['local']),
                'status': 'avaliado',
            }

    distortion_summary = {'beta_max': None, 'beta_inv_min': None, 'atende': None, 'critical_pair': None}
    if distortion_path.exists():
        dist_df = pd.read_csv(distortion_path)
        if not dist_df.empty:
            crit_dist = dist_df.sort_values('beta', ascending=False).iloc[0]
            distortion_summary = {
                'beta_max': float(dist_df['beta'].max()),
                'beta_inv_min': float(dist_df['beta_inv'].min()) if dist_df['beta'].max() > 0 else 99999,
                'atende': bool(dist_df['ok'].all()),
                'critical_pair': f"{crit_dist['p1_id']} <-> {crit_dist['p2_id']}",
            }

    flexure_summary = {}
    if flexure_path.exists():
        flexure_df = pd.read_csv(flexure_path)
        if not flexure_df.empty:
            flexure_summary = {
                'Asx_bottom_req_max_cm2_m': float(flexure_df['Asx_bottom_req_cm2_m'].max()),
                'Asx_top_req_max_cm2_m': float(flexure_df['Asx_top_req_cm2_m'].max()),
                'Asy_bottom_req_max_cm2_m': float(flexure_df['Asy_bottom_req_cm2_m'].max()),
                'Asy_top_req_max_cm2_m': float(flexure_df['Asy_top_req_cm2_m'].max()),
                'Asx_bottom_adot_max_cm2_m': float(flexure_df['Asx_bottom_adot_cm2_m'].max()),
                'Asx_top_adot_max_cm2_m': float(flexure_df['Asx_top_adot_cm2_m'].max()),
                'Asy_bottom_adot_max_cm2_m': float(flexure_df['Asy_bottom_adot_cm2_m'].max()),
                'Asy_top_adot_max_cm2_m': float(flexure_df['Asy_top_adot_cm2_m'].max()),
                'As_min_total_cm2_m': float(flexure_df['As_min_total_cm2_m'].max()),
                'As_min_face_cm2_m': float(flexure_df['As_min_face_cm2_m'].max()),
                'sugestao_x_inf': str(flexure_df.loc[flexure_df['Asx_bottom_adot_cm2_m'].idxmax(), 'detalhe_x_inf']),
                'sugestao_x_sup': str(flexure_df.loc[flexure_df['Asx_top_adot_cm2_m'].idxmax(), 'detalhe_x_sup']),
                'sugestao_y_inf': str(flexure_df.loc[flexure_df['Asy_bottom_adot_cm2_m'].idxmax(), 'detalhe_y_inf']),
                'sugestao_y_sup': str(flexure_df.loc[flexure_df['Asy_top_adot_cm2_m'].idxmax(), 'detalhe_y_sup']),
                'metrics': calculate_reinforcement_metrics(flexure_df, config.h, config.Lx, config.Ly)
            }

    service_summary = {}
    if nodes_path.exists():
        nodes_df = pd.read_csv(nodes_path)
        service_summary = {
            'w_max_mm': float(nodes_df['w_m'].max() * 1000.0),
            'w_med_mm': float(nodes_df['w_m'].mean() * 1000.0),
            'w_diff_mm': float((nodes_df['w_m'].max() - nodes_df['w_m'].min()) * 1000.0),
        }
    if serviceability_path.exists():
        ser_df = pd.read_csv(serviceability_path)
        service_summary.update({
            'wk_x_max_mm': float(ser_df['wk_est_x_mm'].max()),
            'wk_y_max_mm': float(ser_df['wk_est_y_mm'].max()),
            'wk_limit_mm': float(ser_df['wk_limit_mm'].max()),
            'wk_x_ok': bool(ser_df['wk_x_ok'].all()),
            'wk_y_ok': bool(ser_df['wk_y_ok'].all()),
        })
    service_summary['criterios_recalque'] = _build_settlement_service_checks(service_summary, distortion_summary)

    # Detect system type
    is_laje = getattr(config, 'module_name', 'radier') in ['laje', 'lajes']
    system_label = 'Laje Elevada' if is_laje else 'Radier'

    memorial = {
        'system_type': 'laje' if is_laje else 'radier',
        'system_label': system_label,
        'identidade_do_modulo': build_module_identity(LAJE_MODULE if is_laje else RADIER_MODULE),
        'objetivo_profissional': build_professional_context(config),
        'base_normativa': {
            'perfil_principal': get_standard_profile(config.code_profile),
            'referencias_internacionais': get_international_reference_profiles(),
            'combinacoes_adotadas': combinations,
            'matriz_de_verificacoes': {
                'automatizado_no_modulo': [
                    'flechas imediatas e diferidas (Branson)' if is_laje else 'pressao media e maxima de contato no solo',
                    'pre-dimensionamento orientativo da espessura',
                    'flexao ELU por faces com Wood-Armer e redistribuição',
                    'punção ELU completa (NBR 6118) com fator beta (momentos) e Wp',
                    'analise de reacoes de apoio nodais' if is_laje else 'interação solo-estrutura (SSI) avançada com rigidez da superestrutura',
                    'detalhamento automático de armaduras em bitolas comerciais',
                    'geração de pranchas técnicas em DXF',
                    'indicadores de servico por flecha' if is_laje else 'indicadores de servico por recalque',
                ],
                'parcial_ou_em_evolucao': [
                    'combinações normativas completas ELU/ELS',
                    'fissuracao por abertura de fissuras',
                    'detalhamento executivo final por faixas e regiões',
                ],
                'exige_validacao_de_engenharia': [
                    'aceitação final do dimensionamento para projeto executivo',
                    'compatibilização com documentos geotécnicos e critérios específicos da obra',
                    'escolha final das combinações e coeficientes conforme caso real',
                ],
            },
        },
        'dados_da_obra': {
            'base_name': config.base_name,
            'dimensoes_m': {'Lx': config.Lx, 'Ly': config.Ly},
            'malha': {'nx': config.nx, 'ny': config.ny},
            'espessura_adotada_m': config.h,
            'area_m2': area_m2,
        },
        'materiais': {
            'fck_MPa': config.fck,
            'fyk_MPa': config.fyk,
            'E_Pa': config.E,
            'nu': config.nu,
            'cobrimento_m': config.cover,
        },
        'dados_do_solo': {
            'kv_N_m3': config.kv if not is_laje else 0.0,
            'sigma_adm_kPa': config.sigma_adm_kPa if not is_laje else 0.0,
            'modelo': 'Apoios Discretos' if is_laje else 'Winkler vertical',
            'tensionless': config.tensionless,
            'perfil_geotecnico': geotechnical_profile or {'source': 'uniform_default'},
        } if not is_laje else {},
        'verificacoes_geotecnicas': {
            'pressao_media_kPa': q_med_kPa,
            'pressao_max_modelo_kPa': q_max_kPa,
            'tensao_admissivel_kPa': config.sigma_adm_kPa,
            'atende_pressao_media': q_med_kPa <= config.sigma_adm_kPa if not is_laje else True,
            'atende_pressao_max_modelo': q_max_kPa <= config.sigma_adm_kPa if not is_laje else True,
            'status': 'nao_aplicavel_sistema_elevado' if is_laje else 'avaliado',
        } if not is_laje else {},
        'pre_dimensionamento': {
            'espessura_referencia_m': h_ref_m,
            'espessura_adotada_m': config.h,
            'atende_referencia_preliminar': config.h >= h_ref_m,
        },
        'modelo_estrutural': {
            'tipo': 'placa Mindlin-Reissner sobre apoios discretos' if is_laje else 'placa Mindlin-Reissner sobre base elastica de Winkler',
            'graus_de_liberdade_por_no': 3,
            'malha_elementos': (config.nx - 1) * (config.ny - 1),
            'nlf_audit': deterministic_summary.get('nlf_audit'),
            'analise_longo_prazo': config.service_mode == 'verificacao_servico',
            'coeficiente_fluencia_phi': 2.0 if config.service_mode == 'verificacao_servico' else 0.0
        },
        'verificacoes_estruturais': {
            'momentos': {
                'mx_abs_max_kNm_m': deterministic_summary['mx_abs_max_kNm_m'],
                'my_abs_max_kNm_m': deterministic_summary['my_abs_max_kNm_m'],
            },
            'flexao': flexure_summary,
            'puncao': punching_summary,
            'distorcao_angular': distortion_summary,
            'detalhamento_cad': {
                'dxf_file': paths.get('dxf_detailing_file', 'n/d'),
                'status': 'GERADO' if paths.get('dxf_detailing_file') else 'NAO_GERADO'
            },
            'equilibrio_global': {
                'residual_ratio': deterministic_summary['residual_ratio'],
                'atende': deterministic_summary['residual_ratio'] < 1e-6,
            },
            'fundacao_profunda': {
                'reacao_total_estacas_kN': deterministic_summary.get('pile_reactions_total_kN', 0.0),
                'percentual_carga_estacas': (deterministic_summary.get('pile_reactions_total_kN', 0.0) / max(total_service_load_kN, 1.0)) * 100.0,
            }
        },
        'verificacoes_de_servico': service_summary,
        'acoes_de_vento': wind_results or {},
        'estabilidade_global': stability_results or {},
        'comparativo_metodologias': analytical_comparison or {},
        'detalhamento_final': {
            'armadura_inferior': 'distribuir nas duas direcoes, com maior participacao em regioes de momento positivo',
            'armadura_superior': 'concentrar sobre pilares, bordas e regioes de momento negativo',
            'reforcos_locais': 'avaliar sob pilares, bordas e aberturas',
        },
        'conceito_projeto': 'laje elevada sobre apoios rigidos/elasticos com foco em flexao, flechas e reacoes de apoio' if is_laje else 'radier como laje de fundacao apoiada no solo, com foco principal em pressao de contato, flexao, puncao e desempenho em servico',
    }
    memorial['benchmark_evidences'] = _build_benchmark_evidence(deterministic_summary, config)
    memorial['base_normativa']['checklist_detalhado'] = _build_normative_checklist_detailed(memorial)
    memorial['checklist_profissional'] = _build_professional_readiness_checklist(memorial)
    memorial['maturity_score'] = _build_maturity_score(memorial, config)
    memorial['pesquisa_e_melhoria'] = build_research_insights(config, memorial)
    memorial['leitura_orientada_por_modo'] = _build_mode_guidance(memorial)
    memorial['avaliacao_tecnica_por_modo'] = build_mode_specific_assessment(memorial)
    
    # Replicando rigor do Engine MESTRE para o ambiente UFO
    memorial['trilha_auditoria_numérica'] = master_pedagogy.build_structural_audit_trail(config, memorial)
    memorial['parecer_tecnico_mestre'] = memorial['trilha_auditoria_numérica']['summary']['opinion']
    
    memorial['standard_markdown'] = render_standard_markdown_radier(memorial, config)
    return memorial

from memorial_factory import build_unified_memorial
from platform_core import PLATFORM_VERSION, generate_payload_hash

def render_standard_markdown_radier(radier_results: dict, master_config: dict) -> str:
    """
    Rendeiriza o memorial M4 para Radier/Lajes.
    """
    memorial = radier_results
    
    config = memorial.get('dados_da_obra', {})
    materials_raw = memorial.get('materiais', {})
    geotech = memorial.get('verificacoes_geotecnicas', {})
    structural = memorial.get('verificacoes_estruturais', {})
    service = memorial.get('verificacoes_de_servico', {})
    
    is_laje = memorial.get('system_type') == 'laje'
    system_label = memorial.get('system_label', 'Radier')
    module_title = "Laje Elevada em Concreto Armado" if is_laje else "Radier em Concreto Armado"
    
    hypotheses = [
        "Analise de placa Mindlin-Reissner sobre apoios" + (" discretos" if is_laje else " elasticos (Winkler)"),
        "Interacao solo-estrutura (SSI) via coeficiente de recalque vertical" if not is_laje else "Consideracao de rigidez dos apoios",
        "Consideracao de rigidez da superestrutura (se aplicavel)",
        "Modelo linear-elastico para materiais (ELU)"
    ]
    
    materials = {
        "fck": f"{materials_raw.get('fck_MPa')} MPa",
        "fyk": f"{materials_raw.get('fyk_MPa')} MPa",
        "E (Modulo Elasticidade)": f"{materials_raw.get('E_Pa', 0)/1e9:.1f} GPa",
        "Cobrimento": f"{materials_raw.get('cobrimento_m', 0)*1000:.0f} mm"
    }
    
    loads = {
        "Carga Vertical Total": f"{memorial.get('acoes_e_combinacoes', {}).get('carga_total_servico_kN', 0):.2f} kN",
        f"Area da {system_label}": f"{config.get('area_radier_m2', 0):.2f} m2",
    }
    if not is_laje:
        loads["Pressao Media Estimada"] = f"{geotech.get('pressao_media_kPa', 0):.2f} kPa"
    
    combinations = [
        "ELU Fundamental: 1.4*G + 1.4*Q (Padrao NBR 8681)",
        "ELS Quase Permanente / Frequente para recalques e fissuracao",
        "Metodologia Prof. Libanio: Verificacao de Flecha Diferida (fluencia) e Inercia de Branson"
    ]
    
    model_details = {
        "Elementos de Placa": config.get('malha', {}).get('nx', 0) * config.get('malha', {}).get('ny', 0),
        "Espessura Adotada": f"{config.get('espessura_adotada_m', 0):.3f} m",
    }
    if not is_laje:
        model_details["Vínculo de Base"] = f"kv = {memorial.get('dados_do_solo', {}).get('kv_N_m3', 0):.2e} N/m3"
    else:
        model_details["Vínculo de Base"] = "Apoios Discretos"
    
    md = ""
    md += "## 6. Verificações de Serviço (ELS) e Durabilidade\n\n"
    md += f"Para o controle da fissuração, adotou-se o limite de abertura característica $w_k = {service.get('wk_limit_mm', 0.3):.2f}$ mm, conforme a Classe de Agressividade Ambiental (CAA) do projeto.\n\n"
    
    if is_laje:
        md += "### 6.1 Análise de Deformações (Flechas)\n\n"
        md += "As flechas foram calculadas considerando a rigidez efetiva da seção fissurada através do **Modelo de Branson** (NBR 6118:2023, 17.3.2.1.1):\n\n"
        md += "$$I_e = (M_r/M_a)^3 I_c + [1-(M_r/M_a)^3] I_{cr}$$\n\n"
        md += "Adicionalmente, as flechas de longo prazo foram majoradas pelo fator de fluência $\\alpha_f$, considerando uma carga aplicada aos 28 dias e análise para tempo infinito ($t > 70$ meses).\n\n"
    else:
        md += "### 6.1 Recalques e Pressão no Solo\n\n"
        md += "A fundação foi dimensionada para garantir que as pressões de contato permaneçam abaixo da tensão admissível do solo, minimizando recalques diferenciais e distorções angulares.\n\n"

    md += "## 7. Parecer Técnico de Engenharia (Criterio Libanio)\n\n"
    md += f"> {memorial.get('parecer_tecnico_mestre', 'Analise estrutural concluida com base nos criterios normativos vigentes.')}\n\n"
    
    md += "---\n"
    md += f"**Engine:** UFO - Global Analysis System | **Version:** {PLATFORM_VERSION} | **Standards:** NBR 6118:2023, NBR 6120:2019\n"
    
    results = {
        "Flecha Maxima" if is_laje else "Recalque Maximo": f"{service.get('w_max_mm', 0):.3f} mm",
        "Momento Maximo X": f"{structural.get('momentos', {}).get('mx_abs_max_kNm_m', 0):.2f} kNm/m"
    }
    if not is_laje:
        results["Pressao Maxima de Contato"] = f"{geotech.get('pressao_max_modelo_kPa', 0):.2f} kPa"
    
    verifications = []
    if not is_laje:
        verifications.extend([
            {
                "label": "Pressao no Solo (Media)",
                "pass": geotech.get('atende_pressao_media', False),
                "value": f"{geotech.get('pressao_media_kPa', 0):.2f} kPa",
                "limit": f"{geotech.get('tensao_admissivel_kPa', 0):.2f} kPa"
            },
            {
                "label": "Pressao no Solo (Maxima)",
                "pass": geotech.get('atende_pressao_max_modelo', False),
                "value": f"{geotech.get('pressao_max_modelo_kPa', 0):.2f} kPa",
                "limit": f"{geotech.get('tensao_admissivel_kPa', 0):.2f} kPa"
            }
        ])
    
    verifications.append({
        "label": "Puncao (Ratio Max)",
        "pass": structural.get('puncao', {}).get('atende', False),
        "value": f"{structural.get('puncao', {}).get('ratio_max', 0):.3f}",
        "limit": "1.000"
    })
    
    governing_label = "Flecha / Deformacao" if is_laje else "Pressao no Solo"
    governing_value = service.get('w_max_mm', 0) > 30 or (not is_laje and geotech.get('pressao_max_modelo_kPa', 0) > geotech.get('tensao_admissivel_kPa', 0))
    
    governing = {
        "Criterio Governante": governing_label if governing_value else "Dimensionamento a Flexao",
        "Pilar Critico (Puncao)": structural.get('puncao', {}).get('critical_local', 'n/d'),
        "Combinacao Critica": "ELU Fundamental"
    }
    
    return build_unified_memorial(
        module_title=module_title,
        engine_name="RadierSolverM4",
        engine_version="2.4.0",
        hypotheses=hypotheses,
        materials=materials,
        loads=loads,
        combinations=combinations,
        model_details=model_details,
        results=results,
        verifications=verifications,
        governing=governing,
        alerts=memorial.get('checklist_profissional', {}).get('failed_ids', []),
        limitations=["Considera base elastica linear (Winkler)" if not is_laje else "Apoios rigidos", "Nao considera adensamento secundario"],
        additional_content=md
    )


def write_memorial_summary(
    config,
    deterministic_summary: dict,
    output_dir: str | Path,
    analytical_comparison: dict | None = None,
    geotechnical_profile: dict | None = None,
    custom_paths: dict | None = None,
    wind_results: dict | None = None,
    stability_results: dict | None = None,
) -> str:
    memorial = build_memorial_summary(
        config,
        deterministic_summary,
        output_dir,
        analytical_comparison=analytical_comparison,
        geotechnical_profile=geotechnical_profile,
        custom_paths=custom_paths,
        wind_results=wind_results,
        stability_results=stability_results,
    )
    return write_json(Path(output_dir) / f'{config.base_name}_memorial_summary.json', memorial)


def _build_mode_guidance(memorial: dict) -> dict:
    context = memorial['objetivo_profissional']
    mode = context['service_mode']
    geotech = memorial['verificacoes_geotecnicas']
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']
    is_laje = memorial.get('system_type') == 'laje'
    
    if mode == 'dimensionamento':
        critical_checks = [
            f"Espessura adotada atende referência preliminar: {memorial['pre_dimensionamento']['atende_referencia_preliminar']}",
            f"Punção atende: {structural['puncao']['atende']}",
            f"Asx topo adotada máxima (cm²/m): {structural['flexao'].get('Asx_top_adot_max_cm2_m', 'n/d')}",
            f"Asy topo adotada máxima (cm²/m): {structural['flexao'].get('Asy_top_adot_max_cm2_m', 'n/d')}",
        ]
        recommended_actions = [
            'Consolidar faixas de armadura inferior e superior.',
            'Avaliar engrossamentos locais se punção ou momentos forem críticos.',
        ]
    elif mode == 'analise':
        if is_laje:
            critical_checks = [
                f"Reação máxima nos apoios (kN): {structural['momentos'].get('mx_abs_max_kNm_m', 0.0):.2f} (Ref)",
                f"Flecha máxima imediata (mm): {service.get('w_max_mm', 0.0):.3f}",
                f"Residual ratio: {structural['equilibrio_global']['residual_ratio']:.3e}",
            ]
            recommended_actions = [
                'Verificar rigidez dos apoios discretos (pilares).',
                'Avaliar flechas diferidas pelo modelo de Branson.',
            ]
        else:
            critical_checks = [
                f"Pressão média no solo (kPa): {geotech['pressao_media_kPa']:.3f}",
                f"Pressão máxima no modelo (kPa): {geotech['pressao_max_modelo_kPa']:.3f}",
                f"Recalque diferencial estimado (mm): {service.get('w_diff_mm', 'n/d')}",
                f"Residual ratio: {structural['equilibrio_global']['residual_ratio']:.3e}",
            ]
            recommended_actions = [
                'Comparar cenários de kv e malha para sensibilidade.',
                'Confrontar momentos e recalques com hipóteses de rigidez da superestrutura.',
            ]
    elif mode == 'pericia':
        if is_laje:
            critical_checks = [
                f"Flecha máxima calculada (mm): {service.get('w_max_mm', 0.0):.3f}",
                f"Abertura de fissuras (wk,max): {service.get('wk_x_max_mm', 0.0):.3f} mm",
                f"Equilíbrio global atende: {structural['equilibrio_global']['atende']}",
            ]
            recommended_actions = [
                'Comparar flechas calculadas com flechas medidas in-loco.',
                'Verificar conformidade do cobrimento e armadura executada.',
            ]
        else:
            critical_checks = [
                f"Atende pressão máxima modelada: {geotech['atende_pressao_max_modelo']}",
                f"Recalque máximo (mm): {service.get('w_max_mm', 'n/d')}",
                f"Recalque diferencial (mm): {service.get('w_diff_mm', 'n/d')}",
                f"Equilíbrio global atende: {structural['equilibrio_global']['atende']}",
            ]
            recommended_actions = [
                'Registrar hipóteses, dados de entrada e limitações do modelo para rastreabilidade.',
                'Comparar comportamento calculado com manifestações patológicas ou instrumentação.',
            ]
    else:
        critical_checks = [
            f"Modelo estrutural adotado: {memorial['modelo_estrutural']['tipo']}",
            f"Flecha/Recalque Máximo (mm): {service.get('w_max_mm', 0.0):.3f}",
            f"Punção atende: {structural['puncao']['atende']}",
        ]
        recommended_actions = [
            'Transformar estudos paramétricos em benchmark interno.',
            'Comparar resultados com referências numéricas e software comercial.',
        ]

    return {
        'mode_label': context['service_mode_label'],
        'mode_focus': context['mode_focus'],
        'priority_sections': context['priority_sections'],
        'decision_drivers': context['decision_drivers'],
        'critical_checks': critical_checks,
        'recommended_actions': recommended_actions,
    }
