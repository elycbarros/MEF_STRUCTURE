from __future__ import annotations

from dataclasses import asdict, dataclass

REFERENCE_GROUPS = {
    'academico_aplicado': 'academico',
    'academico_classico': 'academico',
    'mercado_academia': 'hibrido',
    'mercado_pratico': 'mercado',
    'estrutural_fundacoes': 'estrutural',
    'mercado_execucao': 'execucao',
    'pericia_diagnostico': 'pericia',
    'analise_numerica': 'analise',
}

PROJECT_WEIGHT_PROFILES = {
    'edificios_altos': {
        'academico': 1.12,
        'hibrido': 1.08,
        'mercado': 0.95,
        'estrutural': 1.08,
        'execucao': 0.90,
        'pericia': 0.92,
        'analise': 1.15,
    },
    'residencial_baixa_media_altura': {
        'academico': 1.00,
        'hibrido': 1.05,
        'mercado': 1.05,
        'estrutural': 1.00,
        'execucao': 1.05,
        'pericia': 0.92,
        'analise': 0.95,
    },
    'industrial_logistico': {
        'academico': 0.95,
        'hibrido': 1.05,
        'mercado': 1.12,
        'estrutural': 1.08,
        'execucao': 1.10,
        'pericia': 0.90,
        'analise': 0.95,
    },
    'infraestrutura_especial': {
        'academico': 1.05,
        'hibrido': 1.02,
        'mercado': 0.98,
        'estrutural': 1.10,
        'execucao': 0.95,
        'pericia': 0.95,
        'analise': 1.12,
    },
    'retrofit_pericia': {
        'academico': 0.95,
        'hibrido': 1.00,
        'mercado': 0.95,
        'estrutural': 1.00,
        'execucao': 0.92,
        'pericia': 1.20,
        'analise': 1.05,
    },
}

WEIGHT_MIN = 0.5
WEIGHT_MAX = 1.5
RECOMMENDED_WEIGHT_MIN = 0.8
RECOMMENDED_WEIGHT_MAX = 1.2


@dataclass(frozen=True)
class AuthorReference:
    reference_id: str
    title: str
    author_or_org: str
    profile: str
    intended_use: str
    reliability_weight: float
    notes: str


def _references() -> list[AuthorReference]:
    # Matriz interna de calibração orientativa (não é citação literal de trechos).
    return [
        AuthorReference(
            reference_id='cintra_aoki_albiero_fundacoes_diretas',
            title='Fundacoes Diretas - Projeto Geotecnico',
            author_or_org='Cintra, Aoki e Albiero',
            profile='academico_aplicado',
            intended_use='criterios de estimativa e verificacao preliminar de fundacoes rasas',
            reliability_weight=0.92,
            notes='Boa aderencia para solo estratificado simples e checagens de admissibilidade.',
        ),
        AuthorReference(
            reference_id='velloso_lopes_vol1',
            title='Fundacoes - Vol. I',
            author_or_org='Velloso e Lopes',
            profile='academico_classico',
            intended_use='fundamentacao teorica para modelagem geotecnica e capacidade de carga',
            reliability_weight=0.95,
            notes='Referencia forte para consolidacao teorica e consistencia de hipoteses.',
        ),
        AuthorReference(
            reference_id='falconi_fundacoes_teoria_pratica',
            title='Fundacoes Teoria e Pratica',
            author_or_org='Falconi et al.',
            profile='mercado_academia',
            intended_use='ponte entre abordagem de obra e modelagem tecnico-cientifica',
            reliability_weight=0.90,
            notes='Equilibrio entre viabilidade de campo e racional de calculo.',
        ),
        AuthorReference(
            reference_id='berberian_passo_a_passo',
            title='Engenharia de Fundacoes - Passo a Passo',
            author_or_org='Dickran Berberian',
            profile='mercado_pratico',
            intended_use='diretrizes de engenharia aplicada e tomada de decisao de obra',
            reliability_weight=0.85,
            notes='Enfase em pragmatismo e robustez para pre-dimensionamento.',
        ),
        AuthorReference(
            reference_id='campos_elementos_fundacoes_concreto',
            title='Elementos de Fundacoes em Concreto',
            author_or_org='Joao Carlos de Campos',
            profile='estrutural_fundacoes',
            intended_use='compatibilizacao entre solicitacoes estruturais e bloco/radier',
            reliability_weight=0.82,
            notes='Apoia transicao entre resposta do solo e verificacoes do concreto.',
        ),
        AuthorReference(
            reference_id='lorenzi_fundacoes_na_pratica',
            title='Fundacoes na Pratica',
            author_or_org='Vinicius Lorenzi',
            profile='mercado_execucao',
            intended_use='boas praticas de detalhamento e execucao em obra',
            reliability_weight=0.78,
            notes='Complementa calibracao com percepcao de construtibilidade.',
        ),
        AuthorReference(
            reference_id='patologia_fundacoes',
            title='Patologia das Fundacoes',
            author_or_org='Referencia tecnica de patologia',
            profile='pericia_diagnostico',
            intended_use='interpretacao de mecanismos de dano e limites de deformacao',
            reliability_weight=0.84,
            notes='Forte para avaliacao de risco de recalque diferencial.',
        ),
        AuthorReference(
            reference_id='interacao_solo_estrutura_edificios',
            title='Interacao Solo-Estrutura e sua Aplicacao na Analise de Estruturas de Edificios',
            author_or_org='Referencia de ISE em edificios',
            profile='analise_numerica',
            intended_use='refino da leitura de rigidez relativa solo-estrutura',
            reliability_weight=0.88,
            notes='Apoia ajustes de calibracao com foco em comportamento global.',
        ),
    ]


def _resolve_project_profile(
    project_type: str,
    custom_group_weights: dict[str, float] | None = None,
) -> tuple[str, dict[str, float], list[str]]:
    key = str(project_type).strip().lower()
    if key not in PROJECT_WEIGHT_PROFILES:
        key = 'edificios_altos'
    profile = dict(PROJECT_WEIGHT_PROFILES[key])
    clamped_groups: list[str] = []
    if custom_group_weights:
        for group, weight in custom_group_weights.items():
            g = str(group).strip().lower()
            if g in profile:
                w = float(weight)
                bounded = min(max(w, WEIGHT_MIN), WEIGHT_MAX)
                if bounded != w:
                    clamped_groups.append(g)
                profile[g] = bounded
    return key, profile, clamped_groups


def _weighted_references(profile_weights: dict[str, float]) -> list[dict]:
    rows: list[dict] = []
    for ref in _references():
        row = asdict(ref)
        group = REFERENCE_GROUPS.get(ref.profile, 'academico')
        group_weight = float(profile_weights.get(group, 1.0))
        row['weight_group'] = group
        row['project_weight_factor'] = group_weight
        row['calibrated_weight'] = float(ref.reliability_weight * group_weight)
        rows.append(row)
    return rows


def get_calibration_reference_matrix(
    project_type: str = 'edificios_altos',
    custom_group_weights: dict[str, float] | None = None,
) -> dict:
    # Envelope orientativo por tipo de solo para k_v = fator * N_spt (MPa/m).
    # Valores calibrados para uso interno de estudos preliminares.
    envelopes = {
        'argila_mole': {'min': 8.0, 'target': 12.0, 'max': 16.0},
        'argila_rija': {'min': 14.0, 'target': 20.0, 'max': 28.0},
        'silte': {'min': 12.0, 'target': 18.0, 'max': 25.0},
        'areia_fofa': {'min': 18.0, 'target': 28.0, 'max': 40.0},
        'areia_media': {'min': 25.0, 'target': 40.0, 'max': 55.0},
        'areia_compacta': {'min': 35.0, 'target': 55.0, 'max': 80.0},
        'misto': {'min': 20.0, 'target': 30.0, 'max': 45.0},
    }

    usage_policy = {
        'conservador': 'Use fator minimo para avaliacao cautelosa e maior margem de seguranca.',
        'medio': 'Use fator target para caso base de estudo preliminar.',
        'agressivo': 'Use fator maximo apenas com suporte de dados de campo e/ou instrumentacao.',
    }
    project_key, profile_weights, clamped_groups = _resolve_project_profile(project_type, custom_group_weights)
    weighted_refs = _weighted_references(profile_weights)

    return {
        'version': 'geotech_ref_matrix_v2',
        'model': 'k_v = fator * N_spt (MPa/m)',
        'envelopes_MPa_per_m': envelopes,
        'usage_policy': usage_policy,
        'project_weighting': {
            'project_type': project_key,
            'group_weights': profile_weights,
            'custom_override_applied': bool(custom_group_weights),
            'bounds': {'min': WEIGHT_MIN, 'max': WEIGHT_MAX},
            'recommended_band': {'min': RECOMMENDED_WEIGHT_MIN, 'max': RECOMMENDED_WEIGHT_MAX},
            'clamped_groups': clamped_groups,
        },
        'references': weighted_refs,
        'governance_note': (
            'Matriz interna consolidada para calibracao preliminar; '
            'nao substitui investigacao geotecnica local, parecer tecnico e validacao de engenharia.'
        ),
    }
