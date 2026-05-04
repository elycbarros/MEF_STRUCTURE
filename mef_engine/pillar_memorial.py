"""
pillar_memorial.py - Memorial Markdown Padronizado para pilares de concreto armado.
"""
from __future__ import annotations
from typing import Any
from memorial_factory import build_unified_memorial
from platform_core import PLATFORM_VERSION, generate_payload_hash

def _fmt(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/d"

def build_pillar_memorial(result: dict[str, Any], config: dict[str, Any] = None) -> str:
    p_hash = generate_payload_hash(config or {})
    summary = result.get("summary", {})
    design = result.get("design", {})
    
    hypotheses = [
        "Analise de pilar isolado com efeito de 2a ordem local",
        "Consideracao de imperfeicoes geometricas (NBR 6118)",
        "Metodo do pilar padrao acoplado ou curvatura aproximada",
        "Dimensionamento a flexao composta obliqua"
    ]

    materials = {
        "fck": f"{summary.get('fck_MPa', 30)} MPa",
        "fyk": f"{summary.get('fyk_MPa', 500)} MPa",
        "Cobrimento": f"{summary.get('cover_mm', 30)} mm"
    }

    loads = {
        "Forca Axial (Nd)": f"{_fmt(summary.get('Nd_kN', 0))} kN",
        "Momento Mx": f"{_fmt(summary.get('Mxd_kNm', 0))} kNm",
        "Momento My": f"{_fmt(summary.get('Myd_kNm', 0))} kNm"
    }

    combinations = [
        "ELU Fundamental: 1.4G + 1.4Q",
        "Vento e Desaprumo considerados como acoes adicionais"
    ]

    model_details = {
        "Secao": f"{summary.get('b_cm', 20)}x{summary.get('h_cm', 20)} cm",
        "Comprimento": f"{_fmt(summary.get('L_m', 3.0))} m",
        "Indice de Esbeltez": _fmt(summary.get('lambda_max', 0))
    }

    results_summary = {
        "Armadura Total (As)": f"{_fmt(design.get('As_total_cm2', 0))} cm2",
        "Taxa de Armadura": f"{_fmt(design.get('rho_percent', 0))}%",
        "Status de Esbeltez": "Esbelto" if summary.get('lambda_max', 0) > 35 else "Curto"
    }

    verifications = [
        {
            "label": "Taxa de Armadura Minima",
            "pass": design.get('rho_percent', 0) >= 0.4,
            "value": f"{_fmt(design.get('rho_percent', 0))}%",
            "limit": "0.40%"
        },
        {
            "label": "Esbeltez Limite",
            "pass": summary.get('lambda_max', 0) <= 90,
            "value": _fmt(summary.get('lambda_max', 0)),
            "limit": "90"
        }
    ]

    governing = {
        "Esforço de Calculo": "Flexao Composta Obliqua",
        "Bitola Sugerida": design.get('rebar_suggestion', 'n/d'),
        "Estribos": design.get('stirrup_suggestion', 'n/d')
    }

    alerts = []
    if summary.get('lambda_max', 0) > 90:
        alerts.append("Pilar muito esbelto, exige analise rigorosa de 2a ordem.")

    limitations = [
        "Nao considera flambagem lateral com torcao",
        "Verificacao limitada a secoes retangulares"
    ]

    return build_unified_memorial(
        module_title="Pilar de Concreto Armado Premium",
        engine_name="ColumnSolverM4",
        engine_version="1.1.0",
        hypotheses=hypotheses,
        materials=materials,
        loads=loads,
        combinations=combinations,
        model_details=model_details,
        results=results_summary,
        verifications=verifications,
        governing=governing,
        alerts=alerts,
        limitations=limitations
    )
