from __future__ import annotations

from pathlib import Path

from radier_utils import read_json, write_json


def build_artifact_manifest_generic(config, master: dict, output_dir: str | Path, extra_files: dict | None = None) -> str:
    out = Path(output_dir)
    manifest = {
        'module_name': config.module_name,
        'service_mode': config.service_mode,
        'base_name': config.base_name,
        'output_dir': str(out),
        'master_summary_file': str(out / f'{config.base_name}_master_summary.json'),
        'report_file': master['report_file'],
        'memorial_summary_file': master['memorial_summary_file'],
    }
    if extra_files:
        manifest.update(extra_files)
    return write_json(out / f'{config.base_name}_artifacts.json', manifest)


def render_professional_header(memorial: dict) -> str:
    return f"""## Enquadramento Profissional

- modulo: `{memorial['identidade_do_modulo']['title']}`
- modo de uso: `{memorial['objetivo_profissional']['service_mode_label']}`
- etapa do projeto: `{memorial['objetivo_profissional']['project_stage']}`
- perfil do cliente: `{memorial['objetivo_profissional']['client_profile']}`
- objetivo: `{memorial['objetivo_profissional']['study_goal']}`
- foco do modo: `{memorial['objetivo_profissional']['mode_focus']}`
"""


def render_normative_basis(memorial: dict) -> str:
    normative = memorial['base_normativa']
    principal = normative['perfil_principal']
    refs = normative['referencias_internacionais']
    matrix = normative['matriz_de_verificacoes']
    combos = normative['combinacoes_adotadas']
    detailed = normative.get('checklist_detalhado', [])
    return f"""## Base Normativa

- perfil principal: `{principal['label']}`
- fundações: `{principal['foundation_code']}`
- ações e combinações: `{principal['load_basis']}`
- papel do perfil: `{principal['role']}`
- observação: `{principal['notes']}`

### Referencias Internacionais

{chr(10).join(f"- {item['label']} ({item['role']})" for item in refs)}

### Combinacoes Adotadas

- serviço rara: `{combos['service_rare']}`
- serviço frequente: `{combos['service_frequent']}`
- ELU: `{combos['ultimate']}`

### Matriz de Verificacoes

#### Automatizado no Modulo

{chr(10).join(f"- {item}" for item in matrix['automatizado_no_modulo'])}

#### Parcial ou em Evolucao

{chr(10).join(f"- {item}" for item in matrix['parcial_ou_em_evolucao'])}

#### Exige Validacao de Engenharia

{chr(10).join(f"- {item}" for item in matrix['exige_validacao_de_engenharia'])}

### Checklist Normativo Detalhado

{chr(10).join(f"- [{item['status']}] {item['id']}: {item['theme']} | ref: {item['reference']} | metodo: {item['method']}" for item in detailed)}
"""


def render_mode_guidance(memorial: dict) -> str:
    guidance = memorial['leitura_orientada_por_modo']
    return f"""## Leitura Orientada pelo Modo

- modo: `{guidance['mode_label']}`
- foco: `{guidance['mode_focus']}`
- secoes prioritarias: `{', '.join(guidance['priority_sections'])}`
- vetores de decisao: `{', '.join(guidance['decision_drivers'])}`

### Checagens Criticas

{chr(10).join(f"- {item}" for item in guidance['critical_checks'])}

### Acoes Recomendadas

{chr(10).join(f"- {item}" for item in guidance['recommended_actions'])}
"""


def render_mode_assessment(memorial: dict) -> str:
    mode = memorial['objetivo_profissional']['service_mode']
    assessment = memorial['avaliacao_tecnica_por_modo']

    if mode == 'dimensionamento':
        return f"""## Avaliacao Tecnica do Modo

### Base de Combinacoes

- serviço: `{assessment['combination_basis']['service_combination']}`
- ELU simplificado: `{assessment['combination_basis']['ultimate_combination']}`

### Checagens de Projeto

- pre-dimensionamento atende: `{assessment['design_checks']['pre_dimensioning_ok']}`
- Asx topo governante (cm²/m): `{assessment['design_checks']['flexure_governing_Asx_top_cm2_m']}`
- Asx base governante (cm²/m): `{assessment['design_checks']['flexure_governing_Asx_bottom_cm2_m']}`
- Asy topo governante (cm²/m): `{assessment['design_checks']['flexure_governing_Asy_top_cm2_m']}`
- Asy base governante (cm²/m): `{assessment['design_checks']['flexure_governing_Asy_bottom_cm2_m']}`
- punção atende: `{assessment['design_checks']['punching_ok']}`
- posição crítica de punção: `{assessment['design_checks']['punching_critical_local']}`

### Diretrizes Executivas

{chr(10).join(f"- {item}" for item in assessment['executive_recommendations'])}
"""

    if mode == 'analise':
        return f"""## Avaliacao Tecnica do Modo

### Interpretacao da Resposta

- pressão média (kPa): `{assessment['response_interpretation']['average_contact_pressure_kPa']}`
- pressão máxima (kPa): `{assessment['response_interpretation']['max_contact_pressure_kPa']}`
- recalque máximo (mm): `{assessment['response_interpretation']['max_settlement_mm']}`
- recalque diferencial (mm): `{assessment['response_interpretation']['differential_settlement_mm']}`
- wk x máximo (mm): `{assessment['response_interpretation']['wk_x_max_mm']}`
- wk y máximo (mm): `{assessment['response_interpretation']['wk_y_max_mm']}`

### Trilhas de Sensibilidade

{chr(10).join(f"- {item}" for item in assessment['sensitivity_tracks'])}

### Recomendações Analíticas

{chr(10).join(f"- {item}" for item in assessment['analysis_recommendations'])}
"""

    if mode == 'pericia':
        flags = assessment['evidence_chain']['consistency_flags']
        return f"""## Avaliacao Tecnica do Modo

### Cadeia de Evidencias

- rastreabilidade: `{assessment['evidence_chain']['input_traceability']}`
- limitações do modelo: `{assessment['evidence_chain']['model_limitations']}`
- pressão no solo atende: `{flags['soil_pressure_ok']}`
- equilíbrio global atende: `{flags['global_equilibrium_ok']}`
- compatibilidade de serviço: `{flags['service_compatibility']}`
- fissuração x atende: `{flags['cracking_check_x_ok']}`
- fissuração y atende: `{flags['cracking_check_y_ok']}`

### Hipoteses Periciais

{chr(10).join(f"- {item}" for item in assessment['forensic_hypotheses'])}

### Recomendações Periciais

{chr(10).join(f"- {item}" for item in assessment['forensic_recommendations'])}
"""

    return f"""## Avaliacao Tecnica do Modo

### Alvos de Benchmark

- métricas centrais: `{', '.join(assessment['benchmark_targets']['core_metrics'])}`
- bases de comparação: `{', '.join(assessment['benchmark_targets']['comparison_bases'])}`

### Vetores de Pesquisa

{chr(10).join(f"- {item}" for item in assessment['research_vectors'])}

### Recomendações de Pesquisa

{chr(10).join(f"- {item}" for item in assessment['research_recommendations'])}
"""


def render_research_section(memorial: dict) -> str:
    return f"""## Leitura de Pesquisa

### O que esta sendo feito

{chr(10).join(f"- {item}" for item in memorial['pesquisa_e_melhoria']['o_que_esta_sendo_feito'])}

### Oportunidades de Melhoria

{chr(10).join(f"- {item}" for item in memorial['pesquisa_e_melhoria']['oportunidades_de_melhoria'])}

### Questoes para Novas Solucoes

{chr(10).join(f"- {item}" for item in memorial['pesquisa_e_melhoria']['questoes_de_pesquisa'])}
"""


def render_benchmark_evidence(memorial: dict) -> str:
    benchmark = memorial['benchmark_evidences']
    checks = benchmark['checks']
    return f"""## Evidencias de Benchmark

- suite: `{benchmark['suite_name']}`
- status global: `{benchmark['all_passed']}`
- aplicabilidade: `{benchmark.get('applicability', 'reference_regression')}`
- bloqueia uso profissional: `{benchmark.get('blocks_professional_use', not benchmark['all_passed'])}`
- observacao: `{benchmark.get('observacao', 'n/d')}`

### Checagens

{chr(10).join(f"- [{ 'PASS' if item['pass'] else 'FAIL' }] {item['id']}: {item['description']} | atual={item['actual']} | alvo={item['target']}" for item in checks)}
"""


def render_professional_checklist(memorial: dict) -> str:
    checklist = memorial['checklist_profissional']
    return f"""## Checklist Profissional

- status: `{checklist['status']}`
- observacao: `{checklist['observacao']}`

### Itens

{chr(10).join(f"- [{ 'OK' if item['pass'] else 'PENDENTE' }] {item['id']}: {item['description']}" for item in checklist['items'])}
"""


def render_maturity_score(memorial: dict) -> str:
    score = memorial['maturity_score']
    subs = score['subscores']
    return f"""## Score de Maturidade

- versao monitorada: `{score['version_id']}`
- data UTC: `{score['generated_at_utc']}`
- score global 0-5: `{score['score_0_5']}`
- score global 0-100: `{score['score_0_100']}`
- nivel: `{score['level']}`

### Subscores

- prontidao profissional: `{subs['professional_readiness_ratio']}`
- rastreabilidade normativa: `{subs['normative_traceability_ratio']}`
- evidencia benchmark: `{subs['benchmark_ratio']}`

### Nota de Monitoramento

- `{score['monitoring_note']}`
"""


def load_memorial(path: str | Path) -> dict:
    return read_json(path)
