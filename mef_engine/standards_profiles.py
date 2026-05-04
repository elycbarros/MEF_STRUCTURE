from __future__ import annotations


def get_standard_profile(code_profile: str) -> dict:
    profiles = {
        'ABNT_NBR_6118_2023': {
            'label': 'ABNT NBR 6118:2023',
            'jurisdiction': 'Brasil',
            'role': 'principal',
            'foundation_code': 'ABNT NBR 6122:2019',
            'load_basis': 'ABNT NBR 8681',
            'serviceability_focus': ['recalques', 'fissuracao', 'deformacoes'],
            'strength_focus': ['flexao', 'punção', 'equilibrio global'],
            'default_combinations': {
                'servico_rara': {'G': 1.0, 'Q': 1.0},
                'servico_frequente': {'G': 1.0, 'Q': 0.7},
                'elu_fundamental': {'G': 1.4, 'Q': 1.4},
            },
            'notes': 'Perfil principal do dimensionador. Aderência normativa deve ser auditada cláusula a cláusula durante a evolução do motor.',
        },
        'ACI_318_25': {
            'label': 'ACI 318-25',
            'jurisdiction': 'Estados Unidos / internacional',
            'role': 'comparativo',
            'foundation_code': 'integração com critérios geotécnicos do projeto',
            'load_basis': 'ASCE 7 / combinação do projeto aplicável',
            'serviceability_focus': ['strength/serviceability/durability'],
            'strength_focus': ['strength design', 'punching shear', 'detailing'],
            'default_combinations': {
                'service_reference': {'G': 1.0, 'Q': 1.0},
                'strength_reference': {'G': 1.2, 'Q': 1.6},
            },
            'notes': 'Perfil comparativo internacional para benchmarking e leitura paralela.',
        },
        'EN_1992_1_1_2004': {
            'label': 'EN 1992-1-1:2004 Eurocode 2',
            'jurisdiction': 'Europa / internacional',
            'role': 'comparativo',
            'foundation_code': 'EN 1997',
            'load_basis': 'EN 1990 + EN 1991',
            'serviceability_focus': ['SLS', 'durability', 'detailing'],
            'strength_focus': ['ULS bending', 'shear', 'punching'],
            'default_combinations': {
                'sls_characteristic': {'G': 1.0, 'Q': 1.0},
                'uls_persistent': {'G': 1.35, 'Q': 1.5},
            },
            'notes': 'Perfil comparativo para alinhamento internacional e estudos benchmark.',
        },
    }
    return profiles.get(code_profile, profiles['ABNT_NBR_6118_2023'])


def get_international_reference_profiles() -> list[dict]:
    return [
        get_standard_profile('ACI_318_25'),
        get_standard_profile('EN_1992_1_1_2004'),
    ]


def get_combination_set(code_profile: str) -> dict:
    profile = get_standard_profile(code_profile)
    combinations = profile['default_combinations']
    return {
        'service_rare': combinations.get('servico_rara', combinations.get('service_reference')),
        'service_frequent': combinations.get('servico_frequente', combinations.get('service_reference')),
        'ultimate': combinations.get('elu_fundamental', combinations.get('strength_reference')),
    }


def get_crack_width_limit_mm(caa: str) -> float:
    caa = str(caa).strip().upper()
    limits = {
        'CAA_I': 0.40,
        'CAA_II': 0.30,
        'CAA_III': 0.30,
        'CAA_IV': 0.20,
    }
    return limits.get(caa, 0.30)
