"""
beam_memorial.py - Memorial Markdown para vigas premium.
"""

from __future__ import annotations

from typing import Any

from memorial_factory import PLATFORM_VERSION, build_unified_memorial


def _fmt(value: Any, digits: int = 2, unit: str = '') -> str:
    try:
        return f'{float(value):.{digits}f}{unit}'
    except (TypeError, ValueError):
        return 'n/d'


def build_beam_memorial(result: dict[str, Any], project_meta: dict[str, Any] | None = None) -> str:
    meta = project_meta or {}
    summary = result.get('summary', {})
    design = result.get('design', {})
    flex_bottom = design.get('flexure_bottom', {})
    flex_top = design.get('flexure_top', {})
    shear = design.get('shear', {})
    crack = design.get('crack_width', {})
    deflection = design.get('deflection', {})
    durability = design.get('durability', {})

    hypotheses = [
        'Analise de viga continua via MEF (elementos de barra)',
        'Consideracao de mesa colaborante (bf)',
        'Redistribuicao de momentos (opcional)',
        'Modelo de bielas para cisalhamento',
    ]

    materials = {
        'fck': f'{summary.get("fck_MPa", 30)} MPa',
        'E (Modulo)': f'{summary.get("E_GPa", 30)} GPa',
        'Cobrimento': f'{durability.get("cover_mm", 30)} mm',
        'CAA': durability.get('caa', 'II'),
    }

    loads = {
        'Vao Total': f'{_fmt(summary.get("L_m"), 2)} m',
        'Largura b': f'{_fmt(summary.get("b_m"), 2)} m',
        'Altura h': f'{_fmt(summary.get("h_m"), 2)} m',
    }

    combinations = ['ELU Fundamental: 1.4G + 1.4Q', 'ELS Servico: 1.0G + 1.0Q']

    model_details = {
        'Motor': 'BeamFEMSolver',
        'Tipo': 'Viga Continua',
        'Analise': summary.get('analysis_type', 'Linear Elastica'),
    }

    results_summary = {
        'Flecha Maxima': f'{_fmt(summary.get("max_deflection_mm"), 3)} mm',
        'Momento Positivo Max': f'{_fmt(design.get("M_max_pos_kNm"), 2)} kNm',
        'Momento Negativo Max': f'{_fmt(design.get("M_max_neg_kNm"), 2)} kNm',
    }

    verifications = [
        {
            'label': 'Flecha (ELS)',
            'pass': deflection.get('status') == 'ATENDE',
            'value': f'{_fmt(summary.get("max_deflection_mm"), 3)} mm',
            'limit': f'{_fmt(deflection.get("limit_mm"), 2)} mm',
        },
        {
            'label': 'Cisalhamento (Vsd/Vrd2)',
            'pass': shear.get('biela_status') == 'ATENDE',
            'value': f'{_fmt(shear.get("Vsd_kN"), 2)} kN',
            'limit': f'{_fmt(shear.get("Vrd2_kN"), 2)} kN',
        },
    ]

    governing = {
        'Armadura de Tracao (Inf)': f'{_fmt(flex_bottom.get("As_cm2"), 2)} cm2',
        'Armadura de Compressao (Sup)': f'{_fmt(flex_top.get("As_cm2"), 2)} cm2',
        'Estribos': shear.get('stirrup_spec', 'n/d'),
    }

    alerts = []
    if deflection.get('status') != 'ATENDE':
        alerts.append('Flecha acima do limite normativo.')
    if shear.get('biela_status') != 'ATENDE':
        alerts.append('Compressao na biela de concreto excedida.')

    limitations = ['Nao considera efeitos de torcao', 'Nao considera fadiga ou efeitos dinamicos']

    return build_unified_memorial(
        module_title='Memorial de Calculo Padronizado - Viga Premium',
        engine_name='BeamFEMSolver',
        engine_version=PLATFORM_VERSION,
        hypotheses=hypotheses,
        materials=materials,
        loads=loads,
        combinations=combinations,
        model_details=model_details,
        results=results_summary,
        verifications=verifications,
        governing=governing,
        alerts=alerts,
        limitations=limitations,
    )
