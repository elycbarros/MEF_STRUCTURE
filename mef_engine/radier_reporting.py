from __future__ import annotations

from pathlib import Path

import pandas as pd

from platform_reporting import (
    build_artifact_manifest_generic,
    render_benchmark_evidence,
    load_memorial,
    render_maturity_score,
    render_normative_basis,
    render_mode_assessment,
    render_mode_guidance,
    render_professional_checklist,
    render_professional_header,
    render_research_section,
)
from radier_utils import write_json


def _fmt(value, digits: int = 3, suffix: str = '') -> str:
    if value is None:
        return 'n/d'
    try:
        return f'{float(value):.{digits}f}{suffix}'
    except (TypeError, ValueError):
        return str(value)


def _status_label(ok: bool | None) -> str:
    if ok is True:
        return 'ATENDE'
    if ok is False:
        return 'NAO_ATENDE'
    return 'N/D'


def _collect_failed_items(memorial: dict) -> list[str]:
    failed: list[str] = []
    for item in memorial.get('checklist_profissional', {}).get('items', []):
        if not item.get('pass', False):
            failed.append(f"{item['id']}: {item['description']}")
    for item in memorial.get('base_normativa', {}).get('checklist_detalhado', []):
        if item.get('status') in {'NAO_ATENDE', 'ALERTA'}:
            failed.append(f"{item['id']}: {item['theme']} ({item['status']})")
    return failed


def _render_executive_summary(memorial: dict) -> str:
    is_laje = memorial.get('system_type') == 'laje'
    system_label = memorial.get('system_label', 'Radier')
    
    geotech = memorial['verificacoes_geotecnicas']
    structural = memorial['verificacoes_estruturais']
    service = memorial['verificacoes_de_servico']
    score = memorial.get('maturity_score', {})
    checklist = memorial.get('checklist_profissional', {})
    failed_items = _collect_failed_items(memorial)
    
    q_ratio = 0.0
    if not is_laje:
        q_ratio = geotech['pressao_max_modelo_kPa'] / max(geotech['tensao_admissivel_kPa'], 1e-9)

    if checklist.get('status') == 'nao_apto_requer_revisao_tecnica':
        decision = 'Nao apto para detalhamento ate revisao tecnica dos bloqueios normativos.'
    elif failed_items:
        decision = 'Apto com restricoes tecnicas ate tratativa dos itens pendentes.'
    else:
        decision = 'Apto para estudo preliminar profissional, sujeito a revisao do responsavel tecnico.'

    actions = failed_items[:5] or ['Manter rastreabilidade dos dados e avançar para detalhamento por faixas/zonas.']
    foundation_recommendation = memorial.get('foundation_recommendation', {})
    executive_decision = memorial.get('executive_decision', {})
    recommendation_lines = ''
    if executive_decision or foundation_recommendation:
        classification = executive_decision.get('classification') or foundation_recommendation.get('classification', 'sem_diagnostico')
        executive_label = executive_decision.get('executive_label') or foundation_recommendation.get('executive_label', classification)
        main_recommendation = executive_decision.get('main_recommendation') or foundation_recommendation.get('main_recommendation', 'n/d')
        next_step = executive_decision.get('next_step', 'n/d')
        recommendation_lines = (
            f"- decisao: `{executive_label}`\n"
            f"- classificacao: `{classification}`\n"
            f"- go/no-go: `{executive_decision.get('go_no_go', 'n/d')}`\n"
            f"- recomendacao principal: `{main_recommendation}`\n"
            f"- proximo passo executivo: `{next_step}`\n"
        )

    soil_line = ""
    if not is_laje:
        soil_line = f"- pressao maxima / admissivel: `{q_ratio:.3f}` ({_status_label(geotech.get('atende_pressao_max_modelo'))})\n"

    service_label = "recalque" if not is_laje else "flecha"

    return f"""## Resumo Executivo

- decisao tecnica: `{decision}`
- status profissional: `{checklist.get('status', 'n/d')}`
- score de maturidade: `{score.get('score_0_5', 'n/d')}/5` (`{score.get('level', 'n/d')}`)
{soil_line}- puncao: `{_status_label(structural.get('puncao', {}).get('atende'))}` | ratio max `{_fmt(structural.get('puncao', {}).get('ratio_max'))}`
- servico: {service_label} max `{_fmt(service.get('w_max_mm'), 3, ' mm')}`, fissuracao x/y `{_status_label(service.get('wk_x_ok'))}/{_status_label(service.get('wk_y_ok'))}`
{recommendation_lines}

### Acoes Tecnicas Recomendadas

{chr(10).join(f"- {item}" for item in actions)}
"""


def _render_foundation_recommendation(memorial: dict, master: dict) -> str:
    is_laje = memorial.get('system_type') == 'laje'
    system_label = memorial.get('system_label', 'Radier')
    
    recommendation = memorial.get('foundation_recommendation') or master.get('foundation_recommendation') or {}
    executive_decision = memorial.get('executive_decision') or master.get('executive_decision') or {}
    if not recommendation:
        return ''

    metrics = recommendation.get('metrics', {})
    trigger_counts = recommendation.get('technical_level_counts', {})
    diagnostic_profile = recommendation.get('diagnostic_conservatism', {})
    input_policy = recommendation.get('input_policy', {})
    triggers = recommendation.get('triggers', [])
    alternatives = recommendation.get('alternatives', [])
    priority_actions = recommendation.get('priority_actions', [])

    trigger_lines = '\n'.join(
        f"- [{item.get('technical_level', 'alerta').upper()}] {item.get('message', item.get('code', 'gatilho'))} | evidencia: {item.get('evidence', 'n/d')}"
        for item in triggers
    ) or '- n/d'
    alternative_lines = '\n'.join(
        f"- {item.get('solution', 'alternativa')}: {item.get('when_to_study', 'n/d')}"
        for item in alternatives
    ) or '- n/d'
    priority_action_lines = '\n'.join(f"- {item}" for item in priority_actions) or '- n/d'
    executive_block = ''
    if executive_decision:
        executive_block = f"""### Quadro de Decisao Executiva

| Campo | Valor |
| :--- | :--- |
| Status | `{executive_decision.get('decision_status', 'n/d')}` |
| Go/No-Go | `{executive_decision.get('go_no_go', 'n/d')}` |
| Decisao | `{executive_decision.get('executive_label', 'n/d')}` |
| Proximo passo | `{executive_decision.get('next_step', 'n/d')}` |
| Primeira acao | `{executive_decision.get('first_priority_action', 'n/d')}` |
"""
        if not is_laje:
            executive_block += f"| Confianca do kv | `{_fmt(executive_decision.get('kv_confidence'))}` |\n"

    soil_line = ""
    if not is_laje:
        soil_line = f"- qmax / sigma_adm: `{_fmt(metrics.get('pressure_ratio'))}`\n"

    return f"""## Diagnostico da Solucao de {system_label}

- decisao executiva: `{recommendation.get('executive_label', 'n/d')}`
- classificacao: `{recommendation.get('classification', 'sem_diagnostico')}`
- recomendacao principal: `{recommendation.get('main_recommendation', 'n/d')}`
- calibracao do diagnostico: `{diagnostic_profile.get('label', 'n/d')}`
- pilares considerados: `{not bool(input_policy.get('ignore_pillars', False))}`
{soil_line}- h / h_ref: `{_fmt(metrics.get('thickness_ratio'))}`
- pilar maximo (kN): `{_fmt(metrics.get('max_pillar_load_kN'))}`
- alertas: `{trigger_counts.get('alerta', 0)}`
- restricoes: `{trigger_counts.get('restricao', 0)}`
- bloqueios: `{trigger_counts.get('bloqueio', 0)}`
- escopo: `{recommendation.get('scope_note', 'n/d')}`

{executive_block}

### Gatilhos do Diagnostico

{trigger_lines}

### Plano de Acao Prioritario

{priority_action_lines}

### Alternativas a Estudar

{alternative_lines}
"""


def _render_reliability_matrix(memorial: dict) -> str:
    benchmark = memorial.get('benchmark_evidences', {})
    checklist = memorial.get('checklist_profissional', {})
    maturity = memorial.get('maturity_score', {})
    structural = memorial.get('verificacoes_estruturais', {})

    score_value = maturity.get('score_0_5')
    try:
        score_ok = float(score_value) >= 4.0
    except (TypeError, ValueError):
        score_ok = None

    rows = [
        ('Validacao de entradas', True, 'CSVs/configuracao passam pela camada de validacao'),
        ('Equilibrio numerico', structural.get('equilibrio_global', {}).get('atende'), f"residual={structural.get('equilibrio_global', {}).get('residual_ratio', 'n/d'):.3e}" if isinstance(structural.get('equilibrio_global', {}).get('residual_ratio'), (int, float)) else 'residual=n/d'),
        ('Benchmark interno', not benchmark.get('blocks_professional_use', not benchmark.get('all_passed')), benchmark.get('observacao', benchmark.get('suite_name', 'n/d'))),
        ('Checklist profissional', checklist.get('status') == 'apto_para_estudo_preliminar_profissional', checklist.get('status', 'n/d')),
        ('Score de maturidade', score_ok, f"{maturity.get('score_0_5', 'n/d')}/5"),
    ]
    table = '\n'.join(f"| {name} | {_status_label(ok)} | {evidence} |" for name, ok, evidence in rows)
    return f"""## Matriz de Confiabilidade

| Controle | Status | Evidencia |
| :--- | :--- | :--- |
{table}
"""


def _render_soil_methodology(memorial: dict) -> str:
    soil = memorial.get('dados_do_solo', {})
    profile = soil.get('perfil_geotecnico', {})
    kv_source = profile.get('source', 'uniform_default')
    lines = [
        f"- modelo de solo: `{soil.get('modelo', 'n/d')}`",
        f"- molas sem tracao: `{soil.get('tensionless', 'n/d')}`",
        f"- origem do kv: `{kv_source}`",
    ]
    if kv_source == 'spt_interpolated':
        lines.extend(
            [
                f"- sondagens: `{profile.get('n_soundings', 'n/d')}`",
                f"- kv mapa min/medio/max (N/m3): `{_fmt(profile.get('kv_min_map_N_m3'), 1)}` / `{_fmt(profile.get('kv_mean_map_N_m3'), 1)}` / `{_fmt(profile.get('kv_max_map_N_m3'), 1)}`",
                f"- interpolacao: `{profile.get('interpolation', {})}`",
            ]
        )
    return "## Metodologia Geotecnica\n\n" + '\n'.join(lines) + '\n'


def _render_service_criteria(memorial: dict) -> str:
    is_laje = memorial.get('system_type') == 'laje'
    service = memorial.get('verificacoes_de_servico', {})
    criteria = service.get('criterios_recalque', {})
    checks = criteria.get('checks', [])
    rows = '\n'.join(
        f"| {item['description']} | {_fmt(item.get('actual'))} | {_fmt(item.get('limit_max'))} | {item.get('unit', '')} | {_status_label(item.get('atende'))} |"
        for item in checks
    )
    if not rows:
        rows = '| n/d | n/d | n/d | n/d | N/D |'
    
    label_verificacao = "Criterios de Servico (Flechas)" if is_laje else "Criterios de Servico (Recalques)"
    
    return f"""## {label_verificacao}

| Verificacao | Valor | Limite | Unidade | Status |
| :--- | ---: | ---: | :--- | :--- |
{rows}

- abertura de fissuras x/y: `{_fmt(service.get('wk_x_max_mm'), 3, ' mm')}` / `{_fmt(service.get('wk_y_max_mm'), 3, ' mm')}` (limite `{_fmt(service.get('wk_limit_mm'), 3, ' mm')}`)
- observacao: `{criteria.get('observacao', 'n/d')}`
"""


def _render_structural_detail(memorial: dict) -> str:
    structural = memorial.get('verificacoes_estruturais', {})
    flex = structural.get('flexao', {})
    punch = structural.get('puncao', {})
    distortion = structural.get('distorcao_angular', {})
    return f"""## Detalhamento Estrutural Sintetico

| Item | Valor |
| :--- | :--- |
| Asx topo adotada max | `{_fmt(flex.get('Asx_top_adot_max_cm2_m'), 3)} cm2/m` |
| Asy topo adotada max | `{_fmt(flex.get('Asy_top_adot_max_cm2_m'), 3)} cm2/m` |
| Asx inferior adotada max | `{_fmt(flex.get('Asx_bottom_adot_max_cm2_m'), 3)} cm2/m` |
| Asy inferior adotada max | `{_fmt(flex.get('Asy_bottom_adot_max_cm2_m'), 3)} cm2/m` |
| Sugestao x topo | `{flex.get('sugestao_x_sup', 'n/d')}` |
| Sugestao y topo | `{flex.get('sugestao_y_sup', 'n/d')}` |
| Puncao ratio max | `{_fmt(punch.get('ratio_max'), 3)}` |
| Puncao local critico | `{punch.get('critical_local', 'n/d')}` |
| Distorcao angular max | `{_fmt(distortion.get('beta_max'), 6)}` |
| Par critico distorcao | `{distortion.get('critical_pair', 'n/d')}` |
"""


def _render_assumptions_and_limits(memorial: dict) -> str:
    matrix = memorial.get('base_normativa', {}).get('matriz_de_verificacoes', {})
    limits = matrix.get('exige_validacao_de_engenharia', [])
    partials = matrix.get('parcial_ou_em_evolucao', [])
    return f"""## Premissas e Limitacoes

### Parcial ou em Evolucao

{chr(10).join(f"- {item}" for item in partials)}

### Exige Validacao de Engenharia

{chr(10).join(f"- {item}" for item in limits)}
"""


def _render_artifact_traceability(master: dict) -> str:
    design = master.get('design_outputs', {})
    rows = [
        ('Memorial JSON', master.get('memorial_summary_file', 'n/d')),
        ('Relatorio Markdown', master.get('report_file', 'n/d')),
        ('Resumo deterministico', master.get('deterministic_summary_file', 'n/d')),
        ('Sensibilidade', master.get('sensitivity_envelope_file', 'n/d')),
        ('Flexao', design.get('flexure_design_file', 'n/d')),
        ('Puncao', design.get('punching_check_file', 'n/d')),
        ('Servico', design.get('serviceability_check_file', 'n/d')),
        ('Manifesto', master.get('artifact_manifest_file', 'n/d')),
    ]
    table = '\n'.join(f"| {name} | `{path}` |" for name, path in rows)
    return f"""## Rastreabilidade dos Artefatos

| Artefato | Caminho |
| :--- | :--- |
{table}
"""


def render_analytical_comparison(memorial: dict) -> str:
    is_laje = memorial.get('system_type') == 'laje'
    comp = memorial.get('comparativo_metodologias', {})
    if not comp:
        return "## Comparativo de Metodologias\n\nNao disponivel para este processamento.\n"

    punching = comp.get('punching_comparison', [])
    punching_rows = ""
    for p in punching:
        diff = p['diff_percent']
        diff_str = f"{diff:+.1f}%" if diff is not None else "n/d"
        punching_rows += f"| {p['local']} | {p['mef_ratio']:.3f} | {p['analytical_ratio']:.3f} | {diff_str} |\n"

    soil_rows = ""
    if not is_laje:
        soil_rows = f"| Pressao Media (kPa) | {memorial['verificacoes_geotecnicas']['pressao_media_kPa']:.2f} | {comp['pressao_media_analitica_kPa']:.2f} | {comp['ratio_pressao_media']:.2f} |\n"
        soil_rows += f"| Pressao Maxima (kPa) | {memorial['verificacoes_geotecnicas']['pressao_max_modelo_kPa']:.2f} | {comp['pressao_max_analitica_kPa']:.2f} | {comp['ratio_pressao_max']:.2f} |\n"
    else:
        # Para lajes podemos mostrar o momento máximo como comparativo se disponível
        soil_rows = f"| Momento Max (kNm/m) | {comp.get('mef', {}).get('m_max_kNm_m', 0.0):.2f} | {comp.get('analytical', {}).get('m_ref_kNm_m', 0.0):.2f} | {comp.get('ratio_momento', 1.0):.2f} |\n"

    return f"""## Comparativo de Metodologias (MEF vs. Analitico)

| Grandeza | MEF | Analitico (Rigido) | Razao (MEF/An) |
| :--- | :--- | :--- | :--- |
{soil_rows}
### Comparativo de Puncao (NBR 6118)

| Local do Pilar | Ratio MEF | Ratio Analitico | Diferenca (%) |
| :--- | :--- | :--- | :--- |
{punching_rows}

> [!NOTE]
> O calculo analitico adota a hipotese de {"placa rigida" if not is_laje else "metodo das faixas/tabelas"} simplificado, enquanto o MEF considera a flexibilidade real do elemento. Divergencias sao esperadas e indicam o ganho de precisao do modelo numerico.
"""


def _render_geotech_calibration_matrix(memorial: dict) -> str:
    matrix = memorial.get('dados_do_solo', {}).get('matriz_calibracao_referencias', {})
    if not matrix:
        return ''

    refs = matrix.get('references', [])
    envelopes = matrix.get('envelopes_MPa_per_m', {})
    project_weighting = matrix.get('project_weighting', {})
    reference_lines = '\n'.join(
        f"- `{item['author_or_org']}` | {item['title']} | base={_fmt(item['reliability_weight'], 3)} | "
        f"fator={_fmt(item.get('project_weight_factor', 1.0), 3)} | calibrado={_fmt(item.get('calibrated_weight', item['reliability_weight']), 3)}"
        for item in refs
    )
    envelope_lines = '\n'.join(
        f"- `{soil}`: min={vals['min']} | alvo={vals['target']} | max={vals['max']} MPa/m"
        for soil, vals in envelopes.items()
    )
    return f"""
## Matriz de Calibracao por Livros/Autores

- versao: `{matrix.get('version', 'n/d')}`
- modelo: `{matrix.get('model', 'n/d')}`
- tipo de projeto: `{project_weighting.get('project_type', 'n/d')}`
- perfil de pesos: `{project_weighting.get('group_weights', {})}`

### Envelope N-SPT -> k_v (MPa/m)

{envelope_lines}

### Referencias Consolidadas

{reference_lines}

- governanca: `{matrix.get('governance_note', 'n/d')}`
"""

def build_didactic_guide(config, master: dict, output_dir: str | Path) -> str:
    out = Path(output_dir)
    memorial = load_memorial(master['memorial_summary_file'])
    is_laje = memorial.get('system_type') == 'laje'
    system_label = memorial.get('system_label', 'Radier')
    
    guide_path = out / f'{config.base_name}_guia_didatico.md'
    geotech = memorial.get('verificacoes_geotecnicas', {})
    predim = memorial.get('pre_dimensionamento', {})
    structural = memorial.get('verificacoes_estruturais', {})
    service = memorial.get('verificacoes_de_servico', {})
    foundation_recommendation = memorial.get('foundation_recommendation', {}) or master.get('foundation_recommendation', {})
    checklist = memorial.get('checklist_profissional', {})
    combos = memorial.get('base_normativa', {}).get('combinacoes_adotadas', {})
    actions = memorial.get('acoes_e_combinacoes', {})
    soil = memorial.get('dados_do_solo', {})

    soil_section = ""
    if not is_laje:
        soil_section = f"""## 3. Analise de servico no solo

Primeiro o solver calcula deslocamentos, pressoes de contato e esforcos fletores para a combinacao de servico. Essa etapa responde perguntas basicas:

- qual e o recalque maximo esperado
- como a pressao se distribui no contato solo-radier
- onde aparecem os maiores momentos

Resultados sinteticos do caso:

- pressao media no solo: `{_fmt(geotech.get('pressao_media_kPa'), 3)} kPa`
- pressao maxima no modelo: `{_fmt(geotech.get('pressao_max_modelo_kPa'), 3)} kPa`
- recalque maximo: `{_fmt(service.get('w_max_mm'), 3)} mm`
- recalque diferencial: `{_fmt(service.get('w_diff_mm'), 3)} mm`

Interpretacao didatica:

- se a pressao maxima se aproxima muito de `sigma_adm`, o radier pode ainda funcionar estruturalmente, mas o solo passa a comandar a viabilidade
- se os recalques sobem demais, a preocupacao deixa de ser apenas resistencia e passa a ser desempenho em servico
"""
    else:
        soil_section = f"""## 3. Analise de Servico (Flechas)

O solver calcula os deslocamentos verticais (flechas) considerando a rigidez do elemento. Em lajes elevadas, a verificação de serviço é focada no conforto visual e integridade das alvenarias.

Resultados sinteticos:

- flecha maxima elástica: `{_fmt(service.get('w_max_mm'), 3)} mm`
- flecha diferida (longo prazo): `{_fmt(service.get('w_max_mm_total', 0.0), 3)} mm`
- atende limite normativo: `{service.get('criterios_recalque', {}).get('atende_global')}`
"""

    text = f"""# Guia Didatico de Dimensionamento de {system_label}

## Finalidade

Este texto e um anexo de consulta opcional. Ele explica, em linguagem tecnica e didatica, como o modulo percorre o dimensionamento de uma {system_label.lower()} em concreto armado. Nao substitui o memorial de calculo nem a revisao do engenheiro responsavel.

## 1. Conceito estrutural adotado

{"O radier e tratado como uma laje de fundacao que distribui as cargas da superestrutura ao solo." if not is_laje else "A laje é tratada como um elemento estrutural suspenso apoiado em pilares/vigas."}
No modelo atual, {"a laje trabalha sobre molas verticais de Winkler" if not is_laje else "a laje trabalha com apoios discretos rigidamente vinculados"}.

- geometria do caso: `{config.Lx:.2f} m x {config.Ly:.2f} m`
- espessura adotada: `{config.h:.3f} m`
- concreto: `fck = {config.fck:.2f} MPa`
- aco: `fyk = {config.fyk:.2f} MPa`

## 2. Entradas principais do problema

O fluxo usa quatro grupos de entrada:

1. geometria
2. materiais
3. carregamentos
4. {"rigidez e limite admissivel do solo" if not is_laje else "vínculos de apoio"}

No caso atual:

- carga distribuida de servico: `{config.q:.2f} Pa`
- carga total de servico: `{_fmt(actions.get('carga_total_servico_kN'), 3)} kN`
- carga de pilares considerada: `{_fmt(actions.get('carga_pilares_kN'), 3)} kN`
"""
    if not is_laje:
        text += f"""- `k_v`: `{_fmt(soil.get('kv_N_m3'), 1)} N/m3`
- `sigma_adm`: `{_fmt(soil.get('sigma_adm_kPa'), 2)} kPa`
"""

    text += soil_section

    text += f"""
## 4. Pre-dimensionamento da espessura

Antes do detalhamento de armadura, o sistema compara a espessura adotada com uma referencia preliminar baseada no nivel de carregamento por area.

- espessura de referencia: `{_fmt(predim.get('espessura_referencia_m'), 3)} m`
- espessura adotada: `{_fmt(predim.get('espessura_adotada_m'), 3)} m`
- atende referencia preliminar: `{predim.get('atende_referencia_preliminar')}`

Didaticamente, essa comparacao nao encerra o projeto. Ela serve como triagem inicial. Mesmo uma espessura acima da referencia pode ser inadequada se houver punção, {"recalque" if not is_laje else "flecha"} ou construtibilidade ruim.

## 5. Combinacoes para verificacoes

O modulo registra combinacoes de servico e ELU para rastreabilidade:

- servico rara: `{combos.get('service_rare', 'n/d')}`
- ELU: `{combos.get('ultimate', 'n/d')}`

Em termos de ensino, isso mostra que o elemento nao e verificado apenas com uma unica fotografia de carga. A leitura correta separa:

- servico: {"recalque" if not is_laje else "flecha"}, fissuracao e comportamento global
- ELU: resistencia a flexao e {"punção" if not is_laje else "punção/cisalhamento"}

## 6. Flexao e armadura

Com os momentos obtidos pelo modelo, o sistema estima armaduras nas direcoes X e Y, em faces superior e inferior.

- Asx topo adotada max: `{_fmt(structural.get('flexao', {}).get('Asx_top_adot_max_cm2_m'), 3)} cm2/m`
- Asy topo adotada max: `{_fmt(structural.get('flexao', {}).get('Asy_top_adot_max_cm2_m'), 3)} cm2/m`
- Asx inferior adotada max: `{_fmt(structural.get('flexao', {}).get('Asx_bottom_adot_max_cm2_m'), 3)} cm2/m`
- Asy inferior adotada max: `{_fmt(structural.get('flexao', {}).get('Asy_bottom_adot_max_cm2_m'), 3)} cm2/m`

Ponto didatico importante:

- armadura inferior costuma responder pelas regioes de momento positivo
- armadura superior aparece com mais intensidade sobre pilares, bordas e faixas de momento negativo
- o resultado atual e uma base de dimensionamento, nao um detalhamento executivo final por faixas

## 7. Punção

A punção e uma verificacao critica em elementos com cargas concentradas. O sistema calcula a razao entre solicitacao e resistencia normativa.

- razao maxima de punção: `{_fmt(structural.get('puncao', {}).get('ratio_max'), 3)}`
- atende: `{structural.get('puncao', {}).get('atende')}`
- local critico: `{structural.get('puncao', {}).get('critical_local', 'n/d')}`

Interpretacao didatica:

- `ratio < 1.0` indica atendimento no criterio adotado
- valores altos, mesmo abaixo de 1.0, sugerem estudar reforcos locais, pedestais, cogumelos ou engrossamentos
- quando a punção governa, a solucao deixa de ser um simples elemento maciço economico

## 8. Verificacoes de servico

{"O radier" if not is_laje else "A laje"} nao deve ser lida apenas pela resistencia. O modulo tambem verifica desempenho em uso:

- fissuracao em X atende: `{service.get('wk_x_ok')}`
- fissuracao em Y atende: `{service.get('wk_y_ok')}`
- criterio global de {"recalque" if not is_laje else "deformação"} atende: `{service.get('criterios_recalque', {}).get('atende_global')}`

Ensino pratico:

- um elemento pode atender a flexao e ainda ser ruim em {"recalque" if not is_laje else "flecha"}
- um elemento pode ter {"pressao no solo" if not is_laje else "armadura"} aceitavel e ainda demandar revisao por punção local
- e a combinacao dessas leituras que sustenta a decisao tecnica final

## 9. Diagnostico final da solucao

Ao fim da cadeia, o sistema consolida um diagnostico orientativo para a viabilidade da solucao.

- classificacao: `{foundation_recommendation.get('classification', 'sem_diagnostico')}`
- recomendacao principal: `{foundation_recommendation.get('main_recommendation', 'n/d')}`
- status profissional do checklist: `{checklist.get('status', 'n/d')}`

Como ler esse diagnostico:

- `viavel preliminarmente` significa que o caminho segue aberto
- `viavel com alertas` indica que ainda e uma opcao, mas com pontos de atencao
- `viavel com restricoes` mostra que a solucao exige comparacao com alternativas
- `nao recomendado` ou `estudar solucao alternativa` indica que a solucao perdeu protagonismo tecnico no caso

## 10. Quando estudar outra tipologia

Didaticamente, o projetista deve sair da solucao atual quando o caso mostrar sinais como:

- espessura muito alta para manter desempenho
{"- pressao de contato muito proxima ou acima da admissivel" if not is_laje else ""}
- punção em margem curta ou nao atendente
- {"recalques" if not is_laje else "flechas"} ou distorcoes incompatíveis com a estrutura
{"- riscos de campo ou de solo que inviabilizam fundacao rasa simples" if not is_laje else ""}

Alternativas tipicas:

{"- sapatas" if not is_laje else "- laje nervurada"}
{"- radier com reforcos locais" if not is_laje else "- laje com capitéis"}
{"- radier nervurado" if not is_laje else "- laje alveolar"}
{"- radier estaqueado" if not is_laje else "- laje protendida"}
{"- fundacao profunda" if not is_laje else ""}

## 11. Limites deste guia

Este texto e propositalmente pedagogico. Ele explica o racional do modulo atual, mas nao substitui:

- verificacoes normativas complementares
{"- julgamento geotecnico da obra real" if not is_laje else ""}
- detalhamento executivo de armaduras
- compatibilizacao com a superestrutura e com a execucao

## 12. Fechamento

Em resumo, dimensionar uma {system_label.lower()} nao e apenas escolher uma espessura e calcular aço. O processo correto passa por:

1. entender cargas {"e solo" if not is_laje else ""}
2. modelar a interacao laje-{"solo" if not is_laje else "apoio"}
3. verificar {"pressoes e recalques" if not is_laje else "flechas"}
4. dimensionar flexao
5. verificar punção
6. consolidar um diagnostico tecnico da viabilidade da solucao

Esse e exatamente o encadeamento que o modulo procura ensinar neste caso.
"""
    guide_path.write_text(text, encoding='utf-8')
    return str(guide_path)
def build_markdown_report(config, master: dict, output_dir: str | Path) -> str:
    out = Path(output_dir)
    det_summary_path = Path(master['deterministic_summary_file'])
    det = pd.read_json(det_summary_path, typ='series').to_dict()
    batch = pd.read_csv(master['batch_kpis_file'])
    memorial = load_memorial(master['memorial_summary_file'])
    inverse = master.get('inverse_and_uq_summary') or {}
    bayes = master.get('bayesian_summary') or {}
    
    is_laje = memorial.get('system_type') == 'laje'
    system_label = memorial.get('system_label', 'Radier')
    
    report_path = out / f'{config.base_name}_report.md'
    manifest_path = out / f'{config.base_name}_artifacts.json'
    master_for_report = {
        **master,
        'report_file': str(report_path),
        'artifact_manifest_file': master.get('artifact_manifest_file', str(manifest_path)),
    }

    worst_batch = batch.sort_values('w_max_mm', ascending=False).iloc[0].to_dict()
    
    soil_data_block = ""
    if not is_laje:
        soil_data_block = f"""## Dados do Solo

- `kv`: `{config.kv:.2f} N/m³`
- `sigma_adm`: `{config.sigma_adm_kPa:.2f} kPa`
- modelo: `Winkler vertical`

{_render_soil_methodology(memorial)}
"""

    geotech_ver_block = ""
    if not is_laje:
        geotech_ver_block = f"""## Verificacoes Geotecnicas

- `pressao_media_kPa`: `{memorial['verificacoes_geotecnicas']['pressao_media_kPa']:.3f}`
- `pressao_max_modelo_kPa`: `{memorial['verificacoes_geotecnicas']['pressao_max_modelo_kPa']:.3f}`
- atende pressao media: `{memorial['verificacoes_geotecnicas']['atende_pressao_media']}`
- atende pressao maxima: `{memorial['verificacoes_geotecnicas']['atende_pressao_max_modelo']}`

{_render_geotech_calibration_matrix(memorial)}
"""

    service_label = "recalque" if not is_laje else "flecha"

    report = f"""# Relatorio {system_label} Lab

{_render_executive_summary(memorial)}

{_render_reliability_matrix(memorial)}

{render_professional_header(memorial)}

{render_normative_basis(memorial)}

## Sequencia de Calculo

- ordem da esteira: `{', '.join(master.get('pipeline_sequence', []))}`

## Dados da Obra

- Base name: `{config.base_name}`
- Geometria: `{config.Lx} m x {config.Ly} m`
- Malha: `{config.nx} x {config.ny}`
- Espessura: `{config.h:.2f} m`

## Materiais

- `fck`: `{config.fck:.2f} MPa`
- `fyk`: `{config.fyk:.2f} MPa`
- cobrimento: `{config.cover:.3f} m`

{soil_data_block}

## Acoes e Combinacoes

- `q`: `{config.q:.2f} Pa`
- carga total de servico: `{memorial['acoes_e_combinacoes']['carga_total_servico_kN']:.3f} kN`

## Caso Deterministico

- `{service_label}_max_mm`: `{det['w_max_mm']:.3f}`
"""
    if not is_laje:
        report += f"- `qsoil_max_kPa`: `{det['qsoil_max_kPa']:.3f}`\n"
        
    report += f"""- `mx_abs_max_kNm_m`: `{det['mx_abs_max_kNm_m']:.3f}`
- `my_abs_max_kNm_m`: `{det['my_abs_max_kNm_m']:.3f}`
- `residual_ratio`: `{det['residual_ratio']:.3e}`

{geotech_ver_block}

{render_analytical_comparison(memorial)}

{_render_foundation_recommendation(memorial, master)}

## Pre-dimensionamento

- `espessura_referencia_m`: `{memorial['pre_dimensionamento']['espessura_referencia_m']:.3f}`
- `espessura_adotada_m`: `{memorial['pre_dimensionamento']['espessura_adotada_m']:.3f}`
- atende referencia preliminar: `{memorial['pre_dimensionamento']['atende_referencia_preliminar']}`

## Modelo Estrutural

- tipo: `{memorial['modelo_estrutural']['tipo']}`
- elementos: `{memorial['modelo_estrutural']['malha_elementos']}`

## Lote Parametrico

- Cenarios avaliados: `{len(batch)}`
- Maior recalque do lote: `{worst_batch['scenario']}` com `{worst_batch['w_max_mm']:.3f} mm`

## Calibracao Inversa e UQ

- `best_kv`: `{inverse['best_kv']:.3f}`
- `best_rmse_mm`: `{inverse['best_rmse_mm']:.3f}`
- `best_mae_mm`: `{inverse['best_mae_mm']:.3f}`
- `mc_wmax_p95_mm`: `{inverse['mc_wmax_p95_mm']:.3f}`
- `mc_qmax_p95_kPa`: `{inverse['mc_qmax_p95_kPa']:.3f}`

## Calibracao Bayesiana

- `kv_map`: `{bayes['kv_map']:.3f}`
- `kv_mean`: `{bayes['kv_mean']:.3f}`
- `kv_p10`: `{bayes['kv_p10']:.3f}`
- `kv_p50`: `{bayes['kv_p50']:.3f}`
- `kv_p90`: `{bayes['kv_p90']:.3f}`
- `sigma_map`: `{bayes['sigma_map']:.3f}`
- `sigma_mean`: `{bayes['sigma_mean']:.3f}`

## Verificacoes Estruturais

- `puncao_ratio_max`: `{memorial['verificacoes_estruturais']['puncao']['ratio_max']}`
- `puncao_atende`: `{memorial['verificacoes_estruturais']['puncao']['atende']}`
- `Asx_top_adot_max_cm2_m`: `{memorial['verificacoes_estruturais']['flexao'].get('Asx_top_adot_max_cm2_m', 'n/d')}`
- `Asy_top_adot_max_cm2_m`: `{memorial['verificacoes_estruturais']['flexao'].get('Asy_top_adot_max_cm2_m', 'n/d')}`

{_render_structural_detail(memorial)}

## Verificacoes de Servico

- `w_max_mm`: `{memorial['verificacoes_de_servico'].get('w_max_mm', 'n/d')}`
- `w_med_mm`: `{memorial['verificacoes_de_servico'].get('w_med_mm', 'n/d')}`
- `w_diff_mm`: `{memorial['verificacoes_de_servico'].get('w_diff_mm', 'n/d')}`
- `wk_x_max_mm`: `{memorial['verificacoes_de_servico'].get('wk_x_max_mm', 'n/d')}`
- `wk_y_max_mm`: `{memorial['verificacoes_de_servico'].get('wk_y_max_mm', 'n/d')}`
- `wk_x_ok`: `{memorial['verificacoes_de_servico'].get('wk_x_ok', 'n/d')}`
- `wk_y_ok`: `{memorial['verificacoes_de_servico'].get('wk_y_ok', 'n/d')}`

{_render_service_criteria(memorial)}

{render_mode_guidance(memorial)}

{render_mode_assessment(memorial)}

{render_research_section(memorial)}

{render_benchmark_evidence(memorial)}

{render_professional_checklist(memorial)}

{render_maturity_score(memorial)}

{_render_assumptions_and_limits(memorial)}

{_render_artifact_traceability(master_for_report)}

## Memorial Padronizado M4

{memorial.get('standard_markdown', 'n/d')}
"""
    report_path.write_text(report, encoding='utf-8')
    return str(report_path)


def build_artifact_manifest(config, master: dict, output_dir: str | Path) -> str:
    extra_files = {
        'deterministic_summary_file': master['deterministic_summary_file'],
        'batch_kpis_file': master['batch_kpis_file'],
        'didactic_guide_file': master.get('didactic_guide_file'),
        'v22_summary_file': str(Path(output_dir) / f'{config.base_name}_v22_summary.json'),
        'v22_uq_samples_file': str(Path(output_dir) / f'{config.base_name}_v22_uq_samples.csv'),
        'v23_summary_file': str(Path(output_dir) / f'{config.base_name}_v23_bayes_summary.json'),
        'v23_marginal_file': str(Path(output_dir) / 'v23_marginal_kv.csv'),
        'nodes_file': str(Path(output_dir) / 'radier_v2_nodes.csv'),
        'elements_file': str(Path(output_dir) / 'radier_v2_elements.csv'),
        'design_outputs': master['design_outputs'],
    }
    return build_artifact_manifest_generic(config, master, output_dir, extra_files=extra_files)
