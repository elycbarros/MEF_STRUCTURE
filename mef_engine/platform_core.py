import hashlib
import json
from dataclasses import dataclass

PLATFORM_VERSION = "5.0.0-M5-PLENO"
ENGINE_NAME = "MEF STRUCTURAL CORE"

def generate_payload_hash(payload: dict) -> str:
    """Gera um hash único para o payload de entrada para garantir imutabilidade do memorial."""
    try:
        # Remove campos que podem variar (como data/hora se existirem no payload de entrada)
        clean_payload = {k: v for k, v in payload.items() if k not in ['timestamp', 'request_id']}
        payload_str = json.dumps(clean_payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:12]
    except Exception:
        return "hash-error"

def get_engine_metadata():
    return {
        "version": PLATFORM_VERSION,
        "engine": ENGINE_NAME,
        "standard_compliance": ["NBR 6118:2023", "NBR 6122:2022", "NBR 6123", "NBR 8681"],
        "maturity_level": "M5-MASTER",
        "status": "High-End-Engine-Elite"
    }


@dataclass(frozen=True)
class ModuleDescriptor:
    module_name: str
    title: str
    scope: str
    current_stage: str
    professional_uses: tuple[str, ...]
    future_modules: tuple[str, ...]


@dataclass(frozen=True)
class ProfessionalContext:
    service_mode: str
    project_stage: str
    client_profile: str
    study_goal: str


def get_service_mode_profile(service_mode: str) -> dict:
    profiles = {
        'dimensionamento': {
            'label': 'Dimensionamento',
            'focus': 'dimensionamento preliminar, verificacoes de resistencia e definicao de espessura/armaduras',
            'priority_sections': ['pre_dimensionamento', 'verificacoes_estruturais', 'detalhamento_final'],
            'decision_drivers': [
                'espessura preliminar',
                'armadura adotada',
                'punção',
                'equilibrio global',
            ],
        },
        'analise': {
            'label': 'Analise',
            'focus': 'compreensao do comportamento estrutural e geotecnico, resposta global e sensibilidade do modelo',
            'priority_sections': ['modelo_estrutural', 'verificacoes_geotecnicas', 'verificacoes_de_servico'],
            'decision_drivers': [
                'pressao de contato',
                'recalque diferencial',
                'momentos maximos',
                'sensibilidade a kv',
            ],
        },
        'pericia': {
            'label': 'Pericia',
            'focus': 'rastreabilidade, comparacao entre comportamento esperado e observado, e identificacao de anomalias',
            'priority_sections': ['acoes_e_combinacoes', 'verificacoes_geotecnicas', 'verificacoes_de_servico'],
            'decision_drivers': [
                'rastreabilidade das entradas',
                'compatibilidade entre solo e estrutura',
                'anomalías de recalque',
                'equilibrio e consistencia de resultados',
            ],
        },
        'pesquisa': {
            'label': 'Pesquisa',
            'focus': 'avaliacao critica do modelo, benchmark, oportunidades de melhoria e novas solucoes',
            'priority_sections': ['modelo_estrutural', 'pesquisa_e_melhoria', 'verificacoes_de_servico'],
            'decision_drivers': [
                'hipoteses do modelo',
                'limites do metodo',
                'comparacoes parametricas',
                'questoes de pesquisa',
            ],
        },
    }
    return profiles.get(service_mode, profiles['dimensionamento'])


def build_module_identity(module: ModuleDescriptor) -> dict:
    return {
        'module_name': module.module_name,
        'title': module.title,
        'scope': module.scope,
        'current_stage': module.current_stage,
        'professional_uses': list(module.professional_uses),
        'future_modules': list(module.future_modules),
    }


def build_professional_context(config) -> dict:
    ctx = ProfessionalContext(
        service_mode=config.service_mode,
        project_stage=config.project_stage,
        client_profile=config.client_profile,
        study_goal=config.study_goal,
    )
    mode_profile = get_service_mode_profile(ctx.service_mode)
    return {
        'service_mode': ctx.service_mode,
        'service_mode_label': mode_profile['label'],
        'project_stage': ctx.project_stage,
        'client_profile': ctx.client_profile,
        'study_goal': ctx.study_goal,
        'mode_focus': mode_profile['focus'],
        'priority_sections': mode_profile['priority_sections'],
        'decision_drivers': mode_profile['decision_drivers'],
    }
