"""
frame_memorial.py - Memorial Markdown Padronizado para pórtico 3D premium.
"""
from __future__ import annotations
from typing import Any
from memorial_factory import build_unified_memorial
from platform_core import PLATFORM_VERSION, generate_payload_hash


def _fmt(value: Any, digits: int = 3, unit: str = "") -> str:
    try:
        return f"{float(value):.{digits}f}{unit}"
    except (TypeError, ValueError):
        return "n/d"


def _fmt_list(lst: Any) -> str:
    if not isinstance(lst, list):
        return "n/d"
    return " | ".join([f"{v:.2f}" for v in lst])


def build_frame_memorial(result: dict[str, Any], model_counts: dict[str, int]) -> str:
    eq = result.get('equilibrium', {})
    efforts = result.get('member_efforts', {})
    p_hash = generate_payload_hash(result)
    
    # Encontrar esforços máximos para o resumo governante
    max_n = 0.0
    max_m = 0.0
    max_v = 0.0
    max_t = 0.0
    critical_member = "n/d"
    
    for mid, eff in efforts.items():
        n_local = max(abs(eff['i']['N']), abs(eff['j']['N']))
        m_local = max(abs(eff['i']['Mz']), abs(eff['i']['My']), abs(eff['j']['Mz']), abs(eff['j']['My']))
        v_local = max(abs(eff['i']['Vy']), abs(eff['i']['Vz']), abs(eff['j']['Vy']), abs(eff['j']['Vz']))
        t_local = max(abs(eff['i']['T']), abs(eff['j']['T']))
        
        if n_local > max_n: max_n = n_local; critical_member = mid
        if m_local > max_m: max_m = m_local
        if v_local > max_v: max_v = v_local
        if t_local > max_t: max_t = t_local

    # 1. Hipóteses
    hypotheses = [
        "Analise matricial de portico espacial 3D (12 DOF/barra)",
        "Consideracao de efeitos de 2a ordem via P-Delta iterativo",
        "Modelo linear-elastico para materiais",
        "Nos rigidos com 6 graus de liberdade",
        "Efeito de vento conforme NBR 6123 (forcas equivalentes)"
    ]

    # 2. Materiais
    materials = {
        "fck": f"{result.get('fck', 30)} MPa",
        "E (Modulo de Elasticidade)": f"{_fmt(result.get('E_GPa', 25), 1)} GPa",
        "Poisson": "0.20",
        "Reducao de Rigidez NBR 6118": f"{result.get('nbr_stiffness_reduction', 'Sim (0.4 EI vigas | 0.8 EI pilares)')}"
    }

    # 3. Cargas
    loads = {
        "Carga Vertical Total": f"{_fmt(result.get('total_vertical_load_kN'), 2)} kN",
        "Acoes Horizontais (Vento)": f"{result.get('wind_loads_applied', 0)} pavimentos com carga",
        "Metodo de Vento": "NBR 6123 - Forcas Horizontais por Pavimento"
    }

    # 4. Combinacoes
    combinations = [
        "ELU (Fundamental): 1.4*G + 1.4*Q (Simplificado)",
        "ELS (Servico): 1.0*G + 1.0*Q"
    ]

    # 5. Modelo
    model_details = {
        "Nos": model_counts.get('nodes', 0),
        "Barras": model_counts.get('members', 0),
        "Graus de Liberdade": model_counts.get('nodes', 0) * 6,
        "Tipo de Analise": result.get('analysis_type', 'P-Delta Linear Iterativo')
    }

    # 6. Resultados
    results_summary = {
        "Deslocamento Topo (2a Ordem)": f"{_fmt(result.get('top_displacement_mm'), 2)} mm",
        "Coeficiente Gamma-Z": f"{_fmt(result.get('gamma_z'), 4)}",
        "Classificacao de Estabilidade": result.get('stability_class', 'n/d')
    }

    # 7. Verificacoes
    verifications = [
        {
            "label": "Equilibrio Global (Forcas)",
            "pass": eq.get('is_equilibrated', False),
            "value": f"Erro: {_fmt(sum(abs(x) for x in eq.get('equilibrium_error_kN', [0])), 6)} kN",
            "limit": "< 0.001 kN"
        },
        {
            "label": "Estabilidade Global (Gamma-Z)",
            "pass": result.get('gamma_z', 1.5) <= 1.3,
            "value": _fmt(result.get('gamma_z'), 4),
            "limit": "1.30"
        }
    ]

    # 8. Governantes
    governing = {
        "Esforço Axial Maximo (N)": f"{_fmt(max_n, 2)} kN",
        "Momento Fletor Maximo (M)": f"{_fmt(max_m, 2)} kNm",
        "Esforço Cortante Maximo (V)": f"{_fmt(max_v, 2)} kN",
        "Momento Torsor Maximo (T)": f"{_fmt(max_t, 2)} kNm",
        "Elemento Critico (Barra)": f"ID {critical_member}"
    }

    # 9. Alertas
    alerts = []
    if result.get('gamma_z', 0) > 1.10:
        alerts.append("Efeitos de 2a ordem sao significativos (gamma-z > 1.10).")
    if result.get('gamma_z', 0) > 1.30:
        alerts.append("Estrutura excessivamente flexivel ou instavel (gamma-z > 1.30).")
    if not eq.get('is_equilibrated', False):
        alerts.append("Erro de equilibrio global detectado acima da tolerancia.")

    # 10. Limitacoes
    limitations = [
        "Nao considera nao-linearidade fisica (apenas geometrica P-Delta)",
        "Nao considera efeitos termicos ou de recalque de apoio",
        "Cargas de vento simplificadas conforme entrada do usuario"
    ]

    return build_unified_memorial(
        module_title="Portico 3D Premium",
        engine_name="Frame3DEngine",
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
        payload_hash=p_hash
    )
