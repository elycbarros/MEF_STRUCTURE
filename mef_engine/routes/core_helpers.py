import math
from typing import Any

from radier_design_v2 import suggest_commercial_reinforcement
from radier_utils import _as_float
from schemas.core import ConfigInput

FIELD_RISK_CATALOG = {
    'heterogeneous_soil': {
        'label': 'Variabilidade Geotécnica Localizada',
        'severity': 'yellow',
        'action': 'Solo heterogêneo detectado: risco de recalques diferenciais não previstos. Exigir campanha complementar ou mapa de kv por sondagem para calibrar o modelo.',
    },
    'water_in_excavation': {
        'label': 'Presença de Água/Percolação na Cava',
        'severity': 'red',
        'action': 'Risco de carreamento de finos e perda de suporte. Bloquear concretagem até definir sistema de rebaixamento ou drenagem subsuperficial.',
    },
    'boulders': {
        'label': 'Matacões ou Blocos de Rocha Isolados',
        'severity': 'red',
        'action': 'Apoio heterogêneo (rígido/deformável/solo): risco de cisalhamento do elemento. Remover matacões ou tratar com transição de solo compactado.',
    },
    'altered_rock': {
        'label': 'Rocha Alterada ou Decomposta',
        'severity': 'yellow',
        'action': 'Capacidade de carga variável: não herdar valores de rocha sã. Validar tensão admissível pontual via ensaio de penetração ou carga.',
    },
    'expansive_or_collapsible': {
        'label': 'Solo Expansivo ou Colapsível',
        'severity': 'red',
        'action': 'Risco de instabilidade volumétrica severa. Fundação rasa não recomendada sem substituição total de solo ou melhoria profunda validada.',
    },
}

SOIL_PRESET_RISK = {
    'soft_organic': 'red',
    'wet_clay': 'yellow',
    'medium_clay': 'yellow',
    'dry_stiff_clay': 'green',
    'sandy_gravel': 'green',
    'very_stiff_gravel': 'green',
}

DIAGNOSTIC_PROFILES = {
    'permissive': {
        'label': 'Permissivo',
        'pressure_alert_ratio': 0.90,
        'pressure_restriction_ratio': 0.98,
        'punching_alert_ratio': 0.90,
        'punching_restriction_ratio': 0.98,
        'settlement_alert_ratio': 0.90,
        'settlement_restriction_ratio': 0.98,
        'distortion_alert_ratio': 0.90,
        'distortion_restriction_ratio': 0.98,
        'cracking_alert_ratio': 0.90,
        'cracking_restriction_ratio': 0.98,
        'winkler_min_ratio': 0.70,
        'winkler_alert_ratio': 0.85,
        'thick_raft_m': 0.90,
        'very_thick_raft_m': 1.20,
        'below_reference_ratio': 0.80,
        'heavy_column_kN': 5500.0,
    },
    'balanced': {
        'label': 'Equilibrado',
        'pressure_alert_ratio': 0.85,
        'pressure_restriction_ratio': 0.95,
        'punching_alert_ratio': 0.85,
        'punching_restriction_ratio': 0.95,
        'settlement_alert_ratio': 0.85,
        'settlement_restriction_ratio': 0.95,
        'distortion_alert_ratio': 0.85,
        'distortion_restriction_ratio': 0.95,
        'cracking_alert_ratio': 0.85,
        'cracking_restriction_ratio': 0.95,
        'winkler_min_ratio': 0.80,
        'winkler_alert_ratio': 0.90,
        'thick_raft_m': 0.80,
        'very_thick_raft_m': 1.00,
        'below_reference_ratio': 0.85,
        'heavy_column_kN': 5000.0,
    },
    'conservative': {
        'label': 'Conservador',
        'pressure_alert_ratio': 0.75,
        'pressure_restriction_ratio': 0.90,
        'punching_alert_ratio': 0.75,
        'punching_restriction_ratio': 0.90,
        'settlement_alert_ratio': 0.75,
        'settlement_restriction_ratio': 0.90,
        'distortion_alert_ratio': 0.75,
        'distortion_restriction_ratio': 0.90,
        'cracking_alert_ratio': 0.75,
        'cracking_restriction_ratio': 0.90,
        'winkler_min_ratio': 0.90,
        'winkler_alert_ratio': 1.00,
        'thick_raft_m': 0.70,
        'very_thick_raft_m': 0.90,
        'below_reference_ratio': 0.95,
        'heavy_column_kN': 4000.0,
    },
}


def build_field_risk_summary(input: ConfigInput) -> dict[str, Any]:
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    if is_laje:
        return {
            'status': 'green',
            'selected': [],
            'recommendations': [
                'Análise de laje suspensa: riscos geotécnicos de subleito não se aplicam diretamente ao elemento.'
            ],
            'policy': 'As condições de contorno são definidas pelos apoios discretos (pilares/vigas).',
        }

    severity_rank = {'green': 0, 'yellow': 1, 'red': 2}
    soil_risk = SOIL_PRESET_RISK.get(input.soil_preset_id or '', 'green')
    selected = []
    for risk_id in input.field_risk_ids:
        risk = FIELD_RISK_CATALOG.get(risk_id)
        if not risk:
            continue
        selected.append({'id': risk_id, **risk})

    worst = soil_risk
    for item in selected:
        if severity_rank[item['severity']] > severity_rank[worst]:
            worst = item['severity']

    recommendations = [item['action'] for item in selected]
    if soil_risk == 'red':
        recommendations.insert(0, 'Solo do preset exige mitigacao geotecnica antes de liberar fundacao rasa.')
    elif soil_risk == 'yellow':
        recommendations.insert(0, 'Confirmar parametros do solo com sondagem, prova de carga ou correlacao validada.')
    if not recommendations:
        recommendations.append(
            'Manter registro das premissas geotecnicas e controle executivo de compactacao, lastro, lona e cura.'
        )

    return {
        'status': worst,
        'selected': selected,
        'recommendations': list(dict.fromkeys(recommendations)),
        'policy': 'Itens vermelhos sao condicionantes de engenharia e nao devem ser tratados como simples aviso visual.',
    }


def build_winkler_consistency(input: ConfigInput, deterministic: dict[str, Any]) -> dict[str, Any]:
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    if is_laje:
        return {'available': False, 'note': 'Análise de Winkler não aplicável a lajes suspensas.'}

    area_m2 = input.Lx * input.Ly
    q_service_kPa = deterministic.get('loads_total_kN', 0.0) / max(area_m2, 1e-9)
    kv_kN_m3 = input.kv / 1000.0
    w_expected_mm = (q_service_kPa / max(kv_kN_m3, 1e-9)) * 1000.0
    w_max_mm = deterministic.get('w_max_mm')
    ratio = None
    pass_check = False
    if isinstance(w_max_mm, (int, float)) and w_expected_mm > 0:
        ratio = float(w_max_mm) / w_expected_mm
        pass_check = ratio >= 0.8
    return {
        'q_service_mean_kPa': q_service_kPa,
        'kv_kN_m3': kv_kN_m3,
        'w_expected_mean_mm': w_expected_mm,
        'w_max_mm': w_max_mm,
        'wmax_over_expected_mean': ratio,
        'pass': pass_check,
        'note': 'Para base de Winkler uniforme, w_max deve ser compatível com q_media/kv e usualmente nao menor que o recalque medio esperado.',
    }


def build_reinforcement_summary(memorial: dict[str, Any], input_data: ConfigInput | None = None) -> dict[str, Any]:
    is_laje = False
    if input_data:
        is_laje = input_data.system_type == 'laje' or input_data.module_name == 'laje'

    structural = memorial.get('verificacoes_estruturais', {})
    service = memorial.get('verificacoes_de_servico', {})
    flexure = structural.get('flexao', {}) if isinstance(structural, dict) else {}
    punching = structural.get('puncao', {}) if isinstance(structural, dict) else {}
    detailing = memorial.get('detalhamento_final', {})
    ratio_max = _as_float(punching.get('ratio_max'))
    wk_x_ok = service.get('wk_x_ok') if isinstance(service, dict) else None
    wk_y_ok = service.get('wk_y_ok') if isinstance(service, dict) else None

    label_faixa = 'faixas sobre apoios' if is_laje else 'faixas sobre pilares'
    label_puncao = 'punção ou cisalhamento' if is_laje else 'punção ou momento negativo'

    critical_zones = [
        {
            'zone': label_faixa,
            'priority': 'alta' if ratio_max >= 0.85 else 'media',
            'guidance': f'Concentrar armadura superior, conferir ancoragem e prever reforco local quando {label_puncao} governarem.',
        },
        {
            'zone': 'panos centrais',
            'priority': 'media',
            'guidance': 'Distribuir armadura inferior principal nas duas direcoes conforme envelopes de momento positivo.',
        },
        {
            'zone': 'bordas e cantos',
            'priority': 'alta' if ratio_max >= 0.75 else 'media',
            'guidance': 'Revisar cobrimento, comprimento de ancoragem, torcao local e possiveis reforcos de borda.',
        },
    ]
    if wk_x_ok is False or wk_y_ok is False:
        critical_zones.append(
            {
                'zone': 'regioes de fissuracao critica',
                'priority': 'alta',
                'guidance': 'Aumentar taxa local, reduzir espacamento ou revisar espessura antes de fechar detalhamento.',
            }
        )

    return {
        'status': 'available' if flexure else 'not_available',
        'flexure': flexure,
        'punching': punching,
        'serviceability': {
            'wk_x_max_mm': service.get('wk_x_max_mm') if isinstance(service, dict) else None,
            'wk_y_max_mm': service.get('wk_y_max_mm') if isinstance(service, dict) else None,
            'wk_limit_mm': service.get('wk_limit_mm') if isinstance(service, dict) else None,
            'wk_x_ok': service.get('wk_x_ok') if isinstance(service, dict) else None,
            'wk_y_ok': service.get('wk_y_ok') if isinstance(service, dict) else None,
        },
        'detailing_guidance': detailing,
        'critical_zones': critical_zones,
        'notes': [
            'Armadura calculada por flexao em faces superior/inferior e direcoes X/Y.',
            'A sugestao comercial e preliminar; detalhamento executivo deve definir faixas, emendas, ancoragens e reforcos locais.',
            f'{"Punção" if not is_laje else "Cisalhamento"} e fissuracao devem governar engrossamentos, capiteis ou reforcos especificos quando necessario.',
        ],
    }


def _resolve_diagnostic_profile(raw_level: str | None) -> tuple[str, dict[str, Any]]:
    level = (raw_level or 'balanced').strip().lower()
    if level not in DIAGNOSTIC_PROFILES:
        level = 'balanced'
    return level, DIAGNOSTIC_PROFILES[level]


def _service_ratio(checks: list[dict[str, Any]], check_id: str) -> float | None:
    for check in checks:
        if check.get('id') != check_id:
            continue
        actual = _as_float(check.get('actual'), default=float('nan'))
        limit = _as_float(check.get('limit_max'), default=float('nan'))
        if math.isfinite(actual) and math.isfinite(limit) and limit > 0:
            return actual / limit
    return None


def build_foundation_recommendation(
    input: ConfigInput,
    memorial: dict[str, Any],
    deterministic: dict[str, Any],
    field_risk_summary: dict[str, Any],
    winkler: dict[str, Any],
) -> dict[str, Any]:
    geotech = memorial.get('verificacoes_geotecnicas', {})
    structural = memorial.get('verificacoes_estruturais', {})
    service = memorial.get('verificacoes_de_servico', {})
    predim = memorial.get('pre_dimensionamento', {})
    benchmark = memorial.get('benchmark_evidences', {})
    checklist = memorial.get('checklist_profissional', {})
    punching = structural.get('puncao', {}) if isinstance(structural, dict) else {}
    recalc = service.get('criterios_recalque', {}) if isinstance(service, dict) else {}
    recalc_checks = recalc.get('checks', []) if isinstance(recalc, dict) else []
    recalc_checks = recalc_checks if isinstance(recalc_checks, list) else []

    area_m2 = max(input.Lx * input.Ly, 1e-9)
    aspect_ratio = max(input.Lx, input.Ly) / max(min(input.Lx, input.Ly), 1e-9)
    volume_m3 = area_m2 * input.h
    total_load_kN = _as_float(deterministic.get('loads_total_kN'))
    avg_pressure = total_load_kN / area_m2 if total_load_kN else _as_float(geotech.get('pressao_media_kPa'))
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'

    qmax = _as_float(geotech.get('pressao_max_modelo_kPa'))
    sigma_adm = max(_as_float(geotech.get('tensao_admissivel_kPa'), input.sigma_adm_kPa), 1e-9)
    pressure_ratio = qmax / sigma_adm if not is_laje else 0.0

    punching_ratio = _as_float(punching.get('ratio_max'))

    if is_laje:
        w_max = _as_float(service.get('w_max_mm'), 0.0)
        w_limit = _as_float(service.get('w_limit_mm'), 1.0)
        total_settlement_ratio = w_max / w_limit
        differential_settlement_ratio = 0.0
        angular_distortion_ratio = 0.0
    else:
        total_settlement_ratio = _service_ratio(recalc_checks, 'recalque_total')
        differential_settlement_ratio = _service_ratio(recalc_checks, 'recalque_diferencial')
        angular_distortion_ratio = _service_ratio(recalc_checks, 'distorcao_angular')
    wk_limit = _as_float(service.get('wk_limit_mm'), default=0.0)
    wk_ratio = None
    if wk_limit > 0:
        wk_ratio = max(_as_float(service.get('wk_x_max_mm')), _as_float(service.get('wk_y_max_mm'))) / wk_limit
    thickness_reference = _as_float(predim.get('espessura_referencia_m'))
    thickness_ratio = input.h / max(thickness_reference, 1e-9) if thickness_reference else None
    active_pillars = [] if input.ignore_pillars else (input.pillars or [])
    max_pillar_load = max([pillar.p_kN for pillar in active_pillars], default=0.0)
    diagnostic_level, profile = _resolve_diagnostic_profile(input.diagnostic_conservatism)
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    winkler_ratio = float('nan')
    soil_context = input.soil_parameter_context if isinstance(input.soil_parameter_context, dict) else {}
    kv_source = str(soil_context.get('kv_source') or 'nao_informado')
    kv_source_label = str(soil_context.get('kv_source_label') or kv_source.replace('_', ' '))
    kv_confidence = max(0.0, min(1.0, _as_float(soil_context.get('kv_confidence'), 0.5)))

    triggers: list[dict[str, Any]] = []

    def add_trigger(code: str, technical_level: str, severity: str, message: str, evidence: str) -> None:
        triggers.append(
            {
                'code': code,
                'technical_level': technical_level,
                'severity': severity,
                'message': message,
                'evidence': evidence,
            }
        )

    if not is_laje:
        if geotech.get('atende_pressao_max_modelo') is False:
            add_trigger(
                'soil_pressure_exceeded',
                'bloqueio',
                'red',
                'Capacidade de carga do solo excedida: a pressão de contato no modelo supera a resistência admissível do terreno, gerando risco de ruptura ou recalques excessivos.',
                f'qmax/sigma_adm = {pressure_ratio:.2f}',
            )
        elif pressure_ratio >= profile['pressure_restriction_ratio']:
            add_trigger(
                'soil_pressure_restriction',
                'restricao',
                'yellow',
                'Carga no solo em nível crítico: a pressão está muito próxima do limite de segurança. Recomenda-se prova de carga ou revisão do kv.',
                f'qmax/sigma_adm = {pressure_ratio:.2f}',
            )
        elif pressure_ratio >= profile['pressure_alert_ratio']:
            add_trigger(
                'soil_pressure_high',
                'alerta',
                'yellow',
                'Solicitação do solo elevada: a margem de segurança geotécnica está reduzindo. Monitorar recalques.',
                f'qmax/sigma_adm = {pressure_ratio:.2f}',
            )

    if punching.get('atende') is False:
        add_trigger(
            'punching_failure',
            'bloqueio',
            'red',
            'Risco de punção (furo): a concentração de carga no pilar supera a resistência do concreto à tração diagonal. Requer engrossamento da laje ou armadura de punção.',
            f'eta_puncao = {punching_ratio:.2f}',
        )
    elif punching_ratio >= profile['punching_restriction_ratio']:
        add_trigger(
            'punching_restriction',
            'restricao',
            'yellow',
            'Punção em limite crítico: a reserva de resistência à tração diagonal é mínima. Estudar reforço local ou capitéis.',
            f'eta_puncao = {punching_ratio:.2f}',
        )
    elif punching_ratio >= profile['punching_alert_ratio']:
        add_trigger(
            'punching_high',
            'alerta',
            'yellow',
            'Atenção ao efeito de punção: solicitação alta em torno dos pilares. Pode exigir redução do espaçamento da armadura superior.',
            f'eta_puncao = {punching_ratio:.2f}',
        )

    if not is_laje:
        if recalc.get('atende_global') is False:
            add_trigger(
                'settlement_failure',
                'bloqueio',
                'red',
                'Recalques fora dos limites: os deslocamentos verticais ou distorções angulares superam as tolerâncias da superestrutura (NBR 6118).',
                f'wmax = {_as_float(service.get("w_max_mm")):.2f} mm',
            )
        else:
            service_ratios = [
                (
                    'settlement_total_high',
                    'Recalque total elevado: deslocamento vertical absoluto próximo ao limite de serviço.',
                    total_settlement_ratio,
                ),
                (
                    'settlement_differential_high',
                    'Recalque diferencial elevado: diferença de nível entre apoios pode gerar esforços secundários na estrutura.',
                    differential_settlement_ratio,
                ),
                (
                    'angular_distortion_high',
                    'Distorção angular crítica: a inclinação relativa entre pilares pode causar fissuração em alvenarias e acabamentos.',
                    angular_distortion_ratio,
                ),
            ]
            for code, message, ratio in service_ratios:
                if ratio is None:
                    continue
                alert_threshold = (
                    profile['distortion_alert_ratio']
                    if code == 'angular_distortion_high'
                    else profile['settlement_alert_ratio']
                )
                restriction_threshold = (
                    profile['distortion_restriction_ratio']
                    if code == 'angular_distortion_high'
                    else profile['settlement_restriction_ratio']
                )
                if ratio >= restriction_threshold:
                    add_trigger(
                        code.replace('_high', '_restriction'),
                        'restricao',
                        'yellow',
                        message.replace('elevado:', 'em limite de restrição:'),
                        f'uso/limite = {ratio:.2f}',
                    )
                elif ratio >= alert_threshold:
                    add_trigger(code, 'alerta', 'yellow', message, f'uso/limite = {ratio:.2f}')

    if service.get('wk_x_ok') is False or service.get('wk_y_ok') is False:
        add_trigger(
            'cracking_failure',
            'restricao',
            'yellow',
            'Fissuração excessiva (Estado Limite de Serviço): abertura de frestas acima do permitido para a classe de agressividade ambiental.',
            f'wk_x_ok={service.get("wk_x_ok")} | wk_y_ok={service.get("wk_y_ok")}',
        )
    elif wk_ratio is not None and wk_ratio >= profile['cracking_restriction_ratio']:
        add_trigger(
            'cracking_restriction',
            'restricao',
            'yellow',
            'Fissuração em limite de atenção: risco de durabilidade por exposição da armadura a agentes agressivos.',
            f'wk/limite = {wk_ratio:.2f}',
        )
    elif wk_ratio is not None and wk_ratio >= profile['cracking_alert_ratio']:
        add_trigger(
            'cracking_high',
            'alerta',
            'yellow',
            'Controle de fissuração: abertura de fissuras próxima ao limite normativo. Recomendado reduzir bitolas e espaçamentos.',
            f'wk/limite = {wk_ratio:.2f}',
        )

    # Pula checagens geotécnicas para lajes suspensas
    if is_laje:
        pass
    else:
        if benchmark.get('blocks_professional_use', not benchmark.get('all_passed', False)):
            add_trigger(
                'benchmark_failure',
                'bloqueio',
                'red',
                'Auditoria de precisão: divergência detectada frente ao benchmark de segurança calibrado para este motor. Uso bloqueado para prevenir erros estruturais.',
                f'suite={benchmark.get("suite_name", "n/d")}',
            )

        winkler_ratio = _as_float(winkler.get('wmax_over_expected_mean'), default=float('nan'))
        if math.isfinite(winkler_ratio) and winkler_ratio < profile['winkler_min_ratio']:
            add_trigger(
                'winkler_inconsistency',
                'bloqueio',
                'red',
                'Inconsistência de Winkler: o recalque do modelo é muito inferior à média teórica (q/kv). Verifique rigidez e vinculações.',
                f'wmax/wmedio = {winkler_ratio:.2f}',
            )
        elif not math.isfinite(winkler_ratio) and winkler.get('pass') is False:
            add_trigger(
                'winkler_inconsistency',
                'bloqueio',
                'red',
                'Inconsistência de Winkler: falha na validação de convergência do modelo elástico linear.',
                f'wmax/wmedio = {winkler.get("wmax_over_expected_mean")}',
            )
        elif math.isfinite(winkler_ratio) and winkler_ratio < profile['winkler_alert_ratio']:
            add_trigger(
                'winkler_low_margin',
                'alerta',
                'yellow',
                'Comportamento de Winkler atípico: recalque próximo da média teórica. Avaliar sensibilidade à variação de kv nas bordas.',
                f'wmax/wmedio = {winkler_ratio:.2f}',
            )

        if field_risk_summary.get('status') == 'red':
            add_trigger(
                'field_risk_red',
                'bloqueio',
                'red',
                'Risco de campo vermelho impede liberacao simples de fundacao rasa.',
                'ver triagem geotecnica/executiva',
            )
        elif field_risk_summary.get('status') == 'yellow':
            add_trigger(
                'field_risk_yellow',
                'restricao',
                'yellow',
                'Risco de campo exige confirmacao geotecnica antes do projeto executivo.',
                'ver triagem geotecnica/executiva',
            )

        if input.soil_preset_id in {'soft_organic', 'wet_clay'}:
            add_trigger(
                'soft_soil_preset',
                'alerta',
                'yellow',
                'Preset de solo sugere atenção a recalques e variabilidade do subleito.',
                f'solo={input.soil_preset_id}',
            )

        if kv_confidence < 0.45:
            add_trigger(
                'kv_low_confidence',
                'restricao',
                'yellow',
                'Coeficiente de reação vertical informado com baixa confiabilidade; calibrar por ensaio, correlação ou análise de recalque.',
                f'origem={kv_source_label} | confianca={kv_confidence:.2f}',
            )
        elif kv_confidence < 0.70:
            add_trigger(
                'kv_medium_confidence',
                'alerta',
                'yellow',
                'Coeficiente de reação vertical exige sensibilidade antes de fechar o dimensionamento.',
                f'origem={kv_source_label} | confianca={kv_confidence:.2f}',
            )

    if max_pillar_load >= profile['heavy_column_kN']:
        add_trigger(
            'heavy_columns',
            'alerta',
            'yellow',
            'Cargas concentradas altas podem governar punção e reforços locais.',
            f'Pmax = {max_pillar_load:.0f} kN',
        )

    if input.ignore_pillars or len(active_pillars) == 0:
        add_trigger(
            'uniform_load_only',
            'alerta',
            'yellow',
            'Caso sem pilares/cargas concentradas: recalque uniforme e punção não aplicável; para pátios, verificar roda, fadiga e juntas.',
            'modelo com carga distribuida pura',
        )

    # Robust contact loss fraction calculation
    contact_loss_pct_val = geotech.get('contact_loss_pct')
    if contact_loss_pct_val is not None:
        contact_loss_fraction = _as_float(contact_loss_pct_val) / 100.0
    else:
        contact_loss_fraction = _as_float(deterministic.get('contact_loss_fraction'), default=0.0)
        if contact_loss_fraction == 0.0:
            total_nodes = max(1, input.nx * input.ny)
            active_springs = deterministic.get('active_springs', total_nodes)
            contact_loss_fraction = max(0.0, 1.0 - (active_springs / total_nodes))

    # Robust max settlement retrieval
    w_max_mm = max(
        _as_float(service.get('w_max_mm'), default=0.0), _as_float(deterministic.get('w_max_mm'), default=0.0)
    )
    w_min_mm = _as_float(deterministic.get('w_min_mm'), default=0.0)
    if not is_laje:
        if contact_loss_fraction > 0.05:
            add_trigger(
                'tension_contact_loss',
                'bloqueio',
                'red',
                'Perda de contato solo-radier detectada em mais de 5% da área (tração nas molas). Revisar geometria, rigidez e carregamentos.',
                f'fracao_sem_contato = {contact_loss_fraction:.2f}',
            )
        elif contact_loss_fraction > 0.01:
            add_trigger(
                'tension_contact_loss',
                'restricao',
                'yellow',
                'Indícios de perda de contato solo-radier em região localizada (tração residual). Verificar bordas, variação de kv e cargas excêntricas.',
                f'fracao_sem_contato = {contact_loss_fraction:.2f}',
            )
        elif contact_loss_fraction > 0.0:
            add_trigger(
                'tension_contact_loss',
                'alerta',
                'yellow',
                'Sinal residual de tração pontual nas molas de Winkler. Monitorar em cenários de carga excêntrica.',
                f'fracao_sem_contato = {contact_loss_fraction:.2f}',
            )

        if w_max_mm > 20.0:
            add_trigger(
                'high_settlement_warning',
                'restricao',
                'yellow',
                'Recalque máximo acima de 20 mm: faixa de maior rigor normativo. Exige análise detalhada de compatibilidade com a superestrutura.',
                f'w_max = {w_max_mm:.1f} mm',
            )
        elif w_max_mm > 10.0:
            add_trigger(
                'high_settlement_warning',
                'alerta',
                'yellow',
                'Recalque máximo entre 10 e 20 mm: faixa de atenção. Avaliar sensibilidade ao kv e compatibilidade estrutural.',
                f'w_max = {w_max_mm:.1f} mm',
            )
    else:
        # Lógica específica para flechas de laje (NBR 6118)
        if w_max_mm > 40.0:  # Exemplo de limite agressivo para alerta
            add_trigger(
                'high_deflection_warning',
                'bloqueio',
                'red',
                'Flecha em serviço excessiva detectada. Risco de danos a alvenarias e desconforto visual elevado.',
                f'w_max = {w_max_mm:.1f} mm',
            )
        elif w_max_mm > 20.0:
            add_trigger(
                'high_deflection_warning',
                'restricao',
                'yellow',
                'Flecha acima do limite convencional (L/250 sugerido). Revisar contra-flecha ou espessura da laje.',
                f'w_max = {w_max_mm:.1f} mm',
            )

    red_count = sum(1 for item in triggers if item['severity'] == 'red')
    yellow_count = sum(1 for item in triggers if item['severity'] == 'yellow')
    blocking_count = sum(1 for item in triggers if item['technical_level'] == 'bloqueio')
    restriction_count = sum(1 for item in triggers if item['technical_level'] == 'restricao')
    alert_count = sum(1 for item in triggers if item['technical_level'] == 'alerta')

    if blocking_count >= 2 or checklist.get('status') == 'nao_apto_requer_revisao_tecnica':
        classification = 'estudar_solucao_alternativa'
        main_recommendation = f'Inviabilidade técnica detectada: os limites de segurança ({"Punção/Cisalhamento" if is_laje else "Solo/Punção"}) foram superados. Estudar {"laje nervurada ou protendida" if is_laje else "radier estaqueado ou fundação profunda"}.'
        decision_rank = 4
        executive_label = 'Estudar solução alternativa'
    elif blocking_count == 1:
        classification = f'{"laje" if is_laje else "radier_liso"}_nao_recomendado_sem_revisao'
        main_recommendation = f'Uso não recomendado: existe um bloqueio crítico de engenharia que impede a validação segura da {"laje" if is_laje else "fundação"} neste cenário.'
        decision_rank = 3
        executive_label = f'{"Laje" if is_laje else "Radier"} não liberado'
    elif restriction_count >= 2 or (restriction_count >= 1 and alert_count >= 2):
        classification = f'{"laje" if is_laje else "radier_liso"}_viavel_com_restricoes'
        main_recommendation = f'Viabilidade condicionada: a {"laje" if is_laje else "fundação"} está no limite técnico. Recomenda-se {"avaliar reforços" if is_laje else "comparar com soluções de reforço local (pedestais)"}.'
        decision_rank = 2
        executive_label = 'Viável com restrições'
    elif restriction_count > 0 or alert_count > 0:
        classification = f'{"laje" if is_laje else "radier_liso"}_viavel_com_alertas'
        main_recommendation = f'Viável com ressalvas: solução coerente para estudo preliminar, mas exige refinamento das {"premissas" if is_laje else "premissas de solo e zonas críticas"}.'
        decision_rank = 1
        executive_label = 'Viável com alertas'
    else:
        classification = f'{"laje" if is_laje else "radier_liso"}_viavel_preliminarmente'
        main_recommendation = f'{"Laje validada" if is_laje else "Radier liso validado"}: as métricas estruturais atendem aos critérios de segurança para esta fase de projeto.'
        decision_rank = 0
        executive_label = 'Viável preliminarmente'

    priority_actions = []
    for item in triggers:
        level = item['technical_level']
        if level == 'bloqueio':
            priority_actions.append(f'Mitigação Crítica: {item["message"]} (Bloqueio normativo detectado)')
        elif level == 'restricao':
            priority_actions.append(f'Ação Corretiva: {item["message"]} (Restrição técnica identificada)')
        elif item['code'] == 'uniform_load_only':
            priority_actions.append(
                'Refinamento de Piso: detalhar juntas de retração e verificar fadiga sob cargas móveis cíclicas.'
            )
    if not priority_actions:
        actions = ['Otimização de Detalhamento: definir faixas de reforço superior sobre pilares.']
        if not is_laje:
            actions.extend(
                [
                    'Auditoria Geotécnica: validar o coeficiente kv final com prova de carga real.',
                    'Estudo de Sensibilidade: simular variação de rigidez do solo nas bordas do radier.',
                ]
            )
        else:
            actions.extend(
                [
                    'Auditoria de Flechas: validar contra-flechas e prazos de desforma (NBR 6118).',
                    'Verificação de Punção: detalhar armadura de reforço local nos pilares críticos.',
                ]
            )
        priority_actions.extend(actions)

    diagnostic_thresholds = {
        'pressure_alert_ratio': profile['pressure_alert_ratio'],
        'pressure_restriction_ratio': profile['pressure_restriction_ratio'],
        'punching_alert_ratio': profile['punching_alert_ratio'],
        'punching_restriction_ratio': profile['punching_restriction_ratio'],
        'settlement_alert_ratio': profile['settlement_alert_ratio'],
        'settlement_restriction_ratio': profile['settlement_restriction_ratio'],
        'distortion_alert_ratio': profile['distortion_alert_ratio'],
        'distortion_restriction_ratio': profile['distortion_restriction_ratio'],
        'cracking_alert_ratio': profile['cracking_alert_ratio'],
        'cracking_restriction_ratio': profile['cracking_restriction_ratio'],
        'winkler_min_ratio': profile['winkler_min_ratio'],
        'winkler_alert_ratio': profile['winkler_alert_ratio'],
        'thick_raft_m': profile['thick_raft_m'],
        'very_thick_raft_m': profile['very_thick_raft_m'],
    }

    if is_laje:
        alternatives = [
            {
                'solution': 'Laje nervurada (unidirecional/bidirecional)',
                'when_to_study': 'Vãos elevados onde o peso próprio da laje maciça torna-se excessivo.',
            },
            {
                'solution': 'Laje com capitéis ou engrossamentos',
                'when_to_study': 'Quando a punção nos pilares governa a espessura de todo o pano.',
            },
            {
                'solution': 'Laje protendida',
                'when_to_study': 'Grandes vãos livres com exigência de controle rigoroso de flechas e esbeltez.',
            },
            {
                'solution': 'Laje alveolar / Pré-moldada',
                'when_to_study': 'Agilidade executiva e racionalização de fôrmas em vãos predominantes.',
            },
        ]
    else:
        alternatives = [
            {
                'solution': 'Sapatas isoladas/corridas/associadas',
                'when_to_study': 'Solo superficial competente, cargas moderadas e pilares suficientemente afastados.',
            },
            {
                'solution': 'Radier com pedestais/cogumelos ou engrossamentos',
                'when_to_study': 'Punção ou momentos locais governam, mas o solo e os recalques permanecem aceitaveis.',
            },
            {
                'solution': 'Radier nervurado',
                'when_to_study': 'Necessidade de maior rigidez flexional sem transformar toda a laje em espessura maciça elevada.',
            },
            {
                'solution': 'Radier estaqueado / piled raft',
                'when_to_study': 'Recalques, solo mole/heterogeneo ou cargas concentradas indicam transferencia parcial para camadas profundas.',
            },
            {
                'solution': 'Fundação profunda independente',
                'when_to_study': 'Solo superficial inadequado, risco executivo elevado ou inviabilidade economica/geometrica da fundacao rasa.',
            },
        ]

    return {
        'classification': classification,
        'executive_label': executive_label,
        'decision_rank': decision_rank,
        'main_recommendation': main_recommendation,
        'priority_actions': list(dict.fromkeys(priority_actions))[:6],
        'trigger_counts': {'red': red_count, 'yellow': yellow_count, 'total': len(triggers)},
        'technical_level_counts': {
            'alerta': alert_count,
            'restricao': restriction_count,
            'bloqueio': blocking_count,
            'total': len(triggers),
        },
        'diagnostic_conservatism': {
            'id': diagnostic_level,
            'label': profile['label'],
            'thresholds': diagnostic_thresholds,
        },
        'input_policy': {
            'ignore_pillars': bool(input.ignore_pillars),
            'active_pillar_count': len(active_pillars),
            'kv_source': kv_source,
            'kv_source_label': kv_source_label,
            'kv_confidence': kv_confidence,
        },
        'metrics': {
            'area_m2': area_m2,
            'aspect_ratio': aspect_ratio,
            'volume_m3': volume_m3,
            'avg_pressure_kPa': avg_pressure,
            'pressure_ratio': pressure_ratio,
            'punching_ratio': punching_ratio,
            'total_settlement_ratio': total_settlement_ratio,
            'differential_settlement_ratio': differential_settlement_ratio,
            'angular_distortion_ratio': angular_distortion_ratio,
            'cracking_ratio': wk_ratio,
            'winkler_ratio': winkler_ratio if math.isfinite(winkler_ratio) else None,
            'thickness_reference_m': thickness_reference,
            'thickness_ratio': thickness_ratio,
            'max_pillar_load_kN': max_pillar_load,
            'kv_kN_m3': input.kv / 1000.0,
            'kv_confidence': kv_confidence,
        },
        'triggers': triggers,
        'alternatives': alternatives,
        'scope_note': f'Diagnóstico orientativo. O sistema atual calcula {"laje maciça suspensa (NBR 6118)" if is_laje else "radier liso em Winkler (NBR 6122)"}; {"lajes especiais" if is_laje else "radier estaqueado"} exige modelos de maior complexidade.',
        'contact_loss_fraction': contact_loss_fraction,
        'w_max_mm': w_max_mm,
    }


def build_executive_decision_summary(foundation_recommendation: dict[str, Any]) -> dict[str, Any]:
    classification = str(foundation_recommendation.get('classification') or 'sem_diagnostico')
    is_laje = classification.startswith('laje')
    rank = int(_as_float(foundation_recommendation.get('decision_rank'), 99))
    technical_counts = foundation_recommendation.get('technical_level_counts', {})
    metrics = foundation_recommendation.get('metrics', {})
    input_policy = foundation_recommendation.get('input_policy', {})
    priority_actions = foundation_recommendation.get('priority_actions', [])

    if rank >= 4:
        decision_status = 'estudar_alternativa'
        go_no_go = 'no_go'
        next_step = f'Inviabilidade técnica detectada: limites normativos ({"Flecha/Punção" if is_laje else "Solo/Punção"}) excedidos. Recomenda-se interromper o fluxo e avaliar {"laje nervurada/protendida" if is_laje else "fundação profunda ou radier estaqueado"}.'
    elif rank == 3:
        decision_status = 'nao_liberado'
        go_no_go = 'hold'
        next_step = 'Impedimento técnico identificado: requer revisão crítica da geometria ou materiais antes de avançar para o detalhamento.'
    elif rank == 2:
        decision_status = 'viavel_com_restricoes'
        go_no_go = 'conditional_go'
        next_step = 'Condição técnica no limite: trate as restrições identificadas e compare com reforços locais antes da liberação executiva.'
    elif rank == 1:
        decision_status = 'viavel_com_alertas'
        go_no_go = 'conditional_go'
        next_step = f'Prosseguir com cautela: realizar análise de {"serviço (flechas)" if is_laje else "sensibilidade geotécnica"} e detalhar zonas de transição críticas.'
    else:
        decision_status = 'viavel_preliminarmente'
        go_no_go = 'go_preliminar'
        next_step = f'Apto para detalhamento: as premissas {"estruturais (NBR 6118)" if is_laje else "estruturais e geotécnicas"} demonstram conformidade normativa preliminar.'

    return {
        'decision_status': decision_status,
        'go_no_go': go_no_go,
        'executive_label': foundation_recommendation.get('executive_label', classification),
        'classification': classification,
        'decision_rank': rank,
        'main_recommendation': foundation_recommendation.get('main_recommendation'),
        'next_step': next_step,
        'first_priority_action': priority_actions[0]
        if isinstance(priority_actions, list) and priority_actions
        else next_step,
        'alert_count': technical_counts.get('alerta', 0) if isinstance(technical_counts, dict) else 0,
        'restriction_count': technical_counts.get('restricao', 0) if isinstance(technical_counts, dict) else 0,
        'blocking_count': technical_counts.get('bloqueio', 0) if isinstance(technical_counts, dict) else 0,
        'pressure_ratio': metrics.get('pressure_ratio') if isinstance(metrics, dict) else None,
        'punching_ratio': metrics.get('punching_ratio') if isinstance(metrics, dict) else None,
        'settlement_ratio': metrics.get('total_settlement_ratio') if isinstance(metrics, dict) else None,
        'kv_confidence': input_policy.get('kv_confidence') if isinstance(input_policy, dict) else None,
        'scope_note': foundation_recommendation.get('scope_note'),
    }


def build_regional_reinforcement_map(memorial: dict[str, Any], input: ConfigInput) -> dict[str, Any]:
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    flexure = (
        memorial.get('verificacoes_estruturais', {}).get('flexao', {})
        if isinstance(memorial.get('verificacoes_estruturais'), dict)
        else {}
    )
    asx_top = _as_float(flexure.get('Asx_top_adot_max_cm2_m'))
    asy_top = _as_float(flexure.get('Asy_top_adot_max_cm2_m'))
    asx_bot = _as_float(flexure.get('Asx_bottom_adot_max_cm2_m'))
    asy_bot = _as_float(flexure.get('Asy_bottom_adot_max_cm2_m'))
    as_min = _as_float(flexure.get('As_min_face_cm2_m'))

    fator_pilar_top = 1.0
    fator_pilar_bot = 0.60
    fator_pano_top = 0.50
    fator_pano_bot = 1.0
    fator_borda_top = 0.70
    fator_borda_bot = 0.70

    def _region(asx_f: float, asy_f: float, as_min_v: float) -> dict:
        asx = max(asx_f, as_min_v)
        asy = max(asy_f, as_min_v)
        return {
            'Asx_cm2_m': round(asx, 3),
            'Asy_cm2_m': round(asy, 3),
            'sugestao_x': suggest_commercial_reinforcement(asx),
            'sugestao_y': suggest_commercial_reinforcement(asy),
        }

    zones = {
        'faixa_pilar_superior': _region(asx_top * fator_pilar_top, asy_top * fator_pilar_top, as_min),
        'faixa_pilar_inferior': _region(asx_bot * fator_pilar_bot, asy_bot * fator_pilar_bot, as_min),
        'pano_central_superior': _region(asx_top * fator_pano_top, asy_top * fator_pano_top, as_min),
        'pano_central_inferior': _region(asx_bot * fator_pano_bot, asy_bot * fator_pano_bot, as_min),
        'borda_superior': _region(asx_top * fator_borda_top, asy_top * fator_borda_top, as_min),
        'borda_inferior': _region(asx_bot * fator_borda_bot, asy_bot * fator_borda_bot, as_min),
    }

    # Alerta de reforço local: quando pico pilar > 1.5× pano central
    pico_x = zones['faixa_pilar_superior']['Asx_cm2_m']
    medio_x = zones['pano_central_superior']['Asx_cm2_m']
    requer_reforco_local = pico_x > 1.5 * max(medio_x, 1e-9) if medio_x > 0 else False

    return {
        'zones': zones,
        'as_min_face_cm2_m': as_min,
        'requer_reforco_local': requer_reforco_local,
        'nota': (
            f'Faixas calculadas com fatores regionais típicos de {"lajes suspensas" if is_laje else "radier Winkler"}. '
            'Detalhamento executivo deve ser feito por engenheiro responsável com análise das envoltórias reais.'
        ),
    }


def build_thermal_checklist(input: ConfigInput) -> dict[str, Any]:
    threshold = 0.80
    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    applicable = input.h >= threshold and not is_laje
    items = []
    if applicable:
        items = [
            {
                'id': 'thermal_study',
                'description': 'Estudo térmico prévio à concretagem (simulação de hidratação)',
                'priority': 'alta',
            },
            {
                'id': 'pour_plan',
                'description': 'Plano de concretagem: etapas, juntas de construção e sequência de lançamento',
                'priority': 'alta',
            },
            {
                'id': 'launch_temperature',
                'description': 'Controle de temperatura de lançamento (≤ 30°C recomendado)',
                'priority': 'alta',
            },
            {
                'id': 'maturity_monitoring',
                'description': 'Monitoramento de maturidade e temperatura interna durante a cura',
                'priority': 'media',
            },
            {
                'id': 'ettringite_risk',
                'description': 'Avaliação do risco de fissuração térmica e etringita tardia',
                'priority': 'media',
            },
            {
                'id': 'cooling_measures',
                'description': 'Medidas de resfriamento: agregados pré-resfriados, gelo, ou resfriamento pós-lançamento',
                'priority': 'media',
            },
            {
                'id': 'curing_plan',
                'description': 'Plano de cura úmida por no mínimo 7 dias com controle de gradiente térmico',
                'priority': 'alta',
            },
        ]
    return {
        'applicable': applicable,
        'threshold_m': threshold,
        'h_adopted_m': input.h,
        'items': items,
        'nota': (
            'Radiers com espessura ≥ 0.80 m são classificados como concreto massa segundo critérios técnicos brasileiros. '
            'O calor de hidratação pode causar gradientes térmicos internos superiores a 20°C, gerando fissuras de origem térmica.'
        )
        if applicable
        else (
            'Sistemas de laje suspensa ou espessura abaixo do limiar (0.80 m): Checklist de concreto massa não aplicável.'
        ),
    }


def build_solution_comparison(input: ConfigInput, foundation_recommendation: dict[str, Any]) -> dict[str, Any]:
    rank = int(_as_float(foundation_recommendation.get('decision_rank'), 99))
    triggers = foundation_recommendation.get('triggers', [])
    blocking = sum(1 for t in triggers if t.get('technical_level') == 'bloqueio')
    pressure_ratio = _as_float(foundation_recommendation.get('metrics', {}).get('pressure_ratio'))
    punching_ratio = _as_float(foundation_recommendation.get('metrics', {}).get('punching_ratio'))

    radier_liso_viability = foundation_recommendation.get('executive_label', 'N/D')
    sapatas_hint = 'Estudar' if blocking >= 1 or pressure_ratio > 0.90 else 'Alternativa madura'
    radier_reforcos_hint = 'Estudar' if punching_ratio > 0.80 else 'Reserva técnica'
    nervurado_hint = 'Estudar' if input.h > 0.90 else 'Reserva técnica'

    is_laje = input.system_type == 'laje' or input.module_name == 'laje'
    if is_laje:
        solutions = [
            {
                'id': 'laje_macica',
                'nome': 'Laje Maciça (MEF)',
                'maturidade': 'implementado',
                'viabilidade': foundation_recommendation.get('executive_label', 'N/D'),
                'quando_estudar': 'Solução atual. Ideal para vãos moderados e cargas convencionais.',
                'disponivel': True,
            },
            {
                'id': 'laje_nervurada',
                'nome': 'Laje Nervurada',
                'maturidade': 'orientativo',
                'viabilidade': 'Estudar se vãos > 7m',
                'quando_estudar': 'Vãos elevados e necessidade de redução de peso próprio.',
                'disponivel': False,
            },
            {
                'id': 'laje_protendida',
                'nome': 'Laje Protendida',
                'maturidade': 'fora_do_escopo',
                'viabilidade': 'Alta performance',
                'quando_estudar': 'Grandes vãos livres e controle rigoroso de flechas.',
                'disponivel': False,
            },
        ]
    else:
        solutions = [
            {
                'id': 'radier_liso',
                'nome': 'Radier liso (Winkler)',
                'maturidade': 'implementado',
                'viabilidade': radier_liso_viability,
                'quando_estudar': 'Solução atual calculada. Viável quando solo uniforme, cargas distribuídas e recalques dentro dos limites.',
                'disponivel': True,
            },
            {
                'id': 'sapatas',
                'nome': 'Sapatas isoladas / corridas',
                'maturidade': 'orientativo',
                'viabilidade': sapatas_hint,
                'quando_estudar': 'Solo superficial competente, pilares suficientemente afastados e cargas moderadas.',
                'disponivel': False,
            },
            {
                'id': 'radier_reforcos',
                'nome': 'Radier com pedestais / cogumelos',
                'maturidade': 'orientativo',
                'viabilidade': radier_reforcos_hint,
                'quando_estudar': 'Punção ou momentos locais governam mas solo e recalques permanecem aceitáveis.',
                'disponivel': False,
            },
            {
                'id': 'radier_nervurado',
                'nome': 'Radier nervurado',
                'maturidade': 'planejado',
                'viabilidade': nervurado_hint,
                'quando_estudar': 'Necessidade de rigidez flexional maior sem transformar toda a laje em espessura maciça elevada.',
                'disponivel': False,
            },
            {
                'id': 'radier_estaqueado',
                'nome': 'Radier estaqueado (piled raft)',
                'maturidade': 'fora_do_escopo',
                'viabilidade': 'Fora do escopo atual',
                'quando_estudar': 'Solo mole/heterogêneo, recalques inaceitáveis ou cargas muito concentradas exigindo transferência para camadas profundas.',
                'disponivel': False,
            },
            {
                'id': 'fundacao_profunda',
                'nome': 'Fundação profunda independente',
                'maturidade': 'fora_do_escopo',
                'viabilidade': 'Fora do escopo atual',
                'quando_estudar': 'Solo superficial inadequado, risco executivo elevado ou inviabilidade econômica/geométrica de fundação rasa.',
                'disponivel': False,
            },
        ]

    return {
        'solutions': solutions,
        'nota': (
            f'Comparativo qualitativo orientativo. Somente o {"sistema de laje maciça" if is_laje else "radier liso"} está implementado e calculado neste módulo. '
            'As demais soluções requerem modelos físicos distintos e análise de engenheiro responsável.'
        ),
        'decision_rank': rank,
    }
