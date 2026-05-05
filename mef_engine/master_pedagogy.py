"""
master_pedagogy.py - passos matematicos estruturados para o Engine MESTRE.

Cada passo retorna LaTeX generico, substituicao numerica, resultado,
referencia normativa e uma explicacao curta para uso em UI/PDF didatico.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import math


@dataclass
class MathStep:
    id: str
    title: str
    formula_latex: str
    substitution_latex: str
    result_latex: str
    norm_ref: str
    explanation: str
    status: str = "INFO"
    opinion: str = ""


def _fmt(value: float, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}"


def _step(step: MathStep) -> dict[str, Any]:
    return asdict(step)


def _join_reasons(reasons: list[str]) -> str:
    if not reasons:
        return "Todas as verificacoes principais atendem aos criterios adotados."
    return "; ".join(reasons) + "."


def build_column_blackboard(sec: Any, loads: Any, design: dict[str, Any]) -> dict[str, Any]:
    """
    Cria um roteiro de resolucao didatica para pilares retangulares.

    Unidades internas:
    - dimensoes e comprimentos em m;
    - cargas em kN;
    - momentos em kNm;
    - saidas didaticas em cm, mm, kN e kNm conforme o caso.
    """
    le = sec.L_free * sec.alpha_b
    area = sec.area
    ix = sec.radius_gyration_x
    iy = sec.radius_gyration_y
    lambda_x = le / ix
    lambda_y = le / iy
    lambda_limit = design.get("slenderness", {}).get("limit", 35.0)

    e_min_x = 0.015 + 0.03 * sec.h
    e_min_y = 0.015 + 0.03 * sec.b
    m_min_x = loads.Nd_kN * e_min_x
    m_min_y = loads.Nd_kN * e_min_y

    fcd = sec.fck / 1.4
    fyd = sec.fyk / 1.15
    ac_cm2 = area * 1e4
    as_min_geom = 0.004 * ac_cm2
    as_min_force = 0.15 * loads.Nd_kN / ((fyd * 1000.0) / 10.0) * 1e4
    as_min = max(as_min_geom, as_min_force)
    as_max = 0.08 * ac_cm2
    rho = design.get("rho_pct", 0.0)

    moments_2nd = design.get("moments_2nd_order", {})
    pcx = moments_2nd.get("Pcx_kN", 0.0)
    pcy = moments_2nd.get("Pcy_kN", 0.0)
    m1x = moments_2nd.get("M1d_x", max(abs(loads.Mxd_kNm), m_min_x))
    m_total_x = moments_2nd.get("M_total_x", m1x)
    m1y = max(abs(loads.Myd_kNm), m_min_y)
    m_total_y = moments_2nd.get("M_total_y", m1y)
    factor_x = (m_total_x / m1x) if abs(m1x) > 1e-9 else 1.0
    factor_y = (m_total_y / m1y) if abs(m1y) > 1e-9 else 1.0
    as_calc = design.get("As_calc_cm2", 0.0)
    as_final = design.get("As_final_cm2", 0.0)
    durability = design.get("durability", {})
    cover_required = durability.get("cover_required_mm", 0.0)
    cover_adopted = durability.get("cover_adopted_mm", 0.0)
    column_reasons = []
    if max(lambda_x, lambda_y) > lambda_limit:
        column_reasons.append(f"Esbeltez máxima ({_fmt(max(lambda_x, lambda_y), 2)}) acima do limite didático ({_fmt(lambda_limit, 2)})")
    if as_final > as_max:
        column_reasons.append(f"Armadura final ({_fmt(as_final, 2)} cm²) acima do máximo permitido ({_fmt(as_max, 2)} cm²)")
    if rho > 4.0:
        column_reasons.append(f"Taxa de armadura ({_fmt(rho, 2)}%) alta, com risco de congestionamento")
    if cover_adopted < cover_required:
        column_reasons.append(f"Cobrimento adotado ({_fmt(cover_adopted, 1)} mm) inferior ao mínimo ({_fmt(cover_required, 1)} mm)")
    if design.get("status") != "OK":
        # Se o solver principal falhou (ex: biela ou falta de convergência), pegamos os motivos dele
        solver_reasons = design.get("reasons", [])
        for sr in solver_reasons:
            if sr not in column_reasons: column_reasons.append(sr)

    column_opinion = (
        "Parecer final: pilar aprovado no roteiro pedagógico. As verificações de esbeltez, armadura e cobrimento convergem para aceitação conforme NBR 6118."
        if not column_reasons and design.get("status") == "OK"
        else f"PARECER DE REVISÃO: O dimensionamento do pilar precisa ser ajustado pelos seguintes motivos: \n• " + "\n• ".join(column_reasons) + "\n\nSugestão: Aumentar a seção transversal, reduzir o comprimento livre ou utilizar concreto de maior fck."
    )

    steps = [
        _step(MathStep(
            id="column-effective-length",
            title="Comprimento equivalente de flambagem",
            formula_latex=r"L_e = \alpha_b \cdot L",
            substitution_latex=rf"L_e = {_fmt(sec.alpha_b, 2)} \cdot {_fmt(sec.L_free, 2)}",
            result_latex=rf"L_e = {_fmt(le, 2)}\,m",
            norm_ref="NBR 6118, analise de pilares - comprimento equivalente",
            explanation="O comprimento equivalente ajusta o comprimento livre conforme as condicoes de vinculacao do pilar.",
        )),
        _step(MathStep(
            id="column-inertia-radius-x",
            title="Raio de giracao no eixo x",
            formula_latex=r"i_x = \sqrt{\frac{I_x}{A_c}}, \quad I_x = \frac{b h^3}{12}",
            substitution_latex=rf"i_x = \sqrt{{\frac{{({_fmt(sec.b, 3)})({_fmt(sec.h, 3)})^3/12}}{{{_fmt(area, 4)}}}}}",
            result_latex=rf"i_x = {_fmt(ix, 4)}\,m = {_fmt(ix * 100, 2)}\,cm",
            norm_ref="Mecanica dos solidos aplicada a pilares",
            explanation="O raio de giracao mede a distribuicao da area em relacao ao eixo analisado e entra diretamente na esbeltez.",
        )),
        _step(MathStep(
            id="column-inertia-radius-y",
            title="Raio de giracao no eixo y",
            formula_latex=r"i_y = \sqrt{\frac{I_y}{A_c}}, \quad I_y = \frac{h b^3}{12}",
            substitution_latex=rf"i_y = \sqrt{{\frac{{({_fmt(sec.h, 3)})({_fmt(sec.b, 3)})^3/12}}{{{_fmt(area, 4)}}}}}",
            result_latex=rf"i_y = {_fmt(iy, 4)}\,m = {_fmt(iy * 100, 2)}\,cm",
            norm_ref="Mecanica dos solidos aplicada a pilares",
            explanation="Em secao retangular, os dois eixos podem ter rigidezes diferentes; por isso a verificacao e feita em x e y.",
        )),
        _step(MathStep(
            id="column-slenderness-x",
            title="Indice de esbeltez no eixo x",
            formula_latex=r"\lambda_x = \frac{L_e}{i_x}",
            substitution_latex=rf"\lambda_x = \frac{{{_fmt(le, 2)}}}{{{_fmt(ix, 4)}}}",
            result_latex=rf"\lambda_x = {_fmt(lambda_x, 2)}",
            norm_ref="NBR 6118, Secao 15 - efeitos locais de 2a ordem",
            explanation="Se a esbeltez ultrapassa o limite adotado, os efeitos locais de segunda ordem nao devem ser desprezados.",
            status="ALERTA" if lambda_x > lambda_limit else "OK",
        )),
        _step(MathStep(
            id="column-slenderness-y",
            title="Indice de esbeltez no eixo y",
            formula_latex=r"\lambda_y = \frac{L_e}{i_y}",
            substitution_latex=rf"\lambda_y = \frac{{{_fmt(le, 2)}}}{{{_fmt(iy, 4)}}}",
            result_latex=rf"\lambda_y = {_fmt(lambda_y, 2)}",
            norm_ref="NBR 6118, Secao 15 - efeitos locais de 2a ordem",
            explanation="A direcao com maior esbeltez costuma governar a necessidade de analise de segunda ordem local.",
            status="ALERTA" if lambda_y > lambda_limit else "OK",
        )),
        _step(MathStep(
            id="column-slenderness-decision",
            title="Decisao sobre efeitos locais de 2a ordem",
            formula_latex=r"\lambda \leq \lambda_{lim} \Rightarrow 2a\,ordem\,local\,dispensavel",
            substitution_latex=rf"\lambda_{{max}} = \max({_fmt(lambda_x, 2)}, {_fmt(lambda_y, 2)}) \quad ; \quad \lambda_{{lim}} = {_fmt(lambda_limit, 2)}",
            result_latex=rf"\lambda_{{max}} = {_fmt(max(lambda_x, lambda_y), 2)}",
            norm_ref="NBR 6118, Secao 15 - classificacao de esbeltez",
            explanation="O maior indice entre os dois eixos comanda a necessidade de considerar os efeitos locais de segunda ordem.",
            status="ALERTA" if max(lambda_x, lambda_y) > lambda_limit else "OK",
        )),
        _step(MathStep(
            id="column-minimum-eccentricity-x",
            title="Excentricidade minima no eixo x",
            formula_latex=r"e_{min,x} = 1{,}5\,cm + 0{,}03h",
            substitution_latex=rf"e_{{min,x}} = 1{','}5\,cm + 0{','}03 \cdot {_fmt(sec.h * 100, 1)}\,cm",
            result_latex=rf"e_{{min,x}} = {_fmt(e_min_x * 100, 2)}\,cm = {_fmt(e_min_x * 1000, 1)}\,mm",
            norm_ref="NBR 6118, momento minimo de 1a ordem",
            explanation="Mesmo quando o momento informado e pequeno, a norma exige uma excentricidade minima para cobrir imperfeicoes.",
        )),
        _step(MathStep(
            id="column-minimum-eccentricity-y",
            title="Excentricidade minima no eixo y",
            formula_latex=r"e_{min,y} = 1{,}5\,cm + 0{,}03b",
            substitution_latex=rf"e_{{min,y}} = 1{','}5\,cm + 0{','}03 \cdot {_fmt(sec.b * 100, 1)}\,cm",
            result_latex=rf"e_{{min,y}} = {_fmt(e_min_y * 100, 2)}\,cm = {_fmt(e_min_y * 1000, 1)}\,mm",
            norm_ref="NBR 6118, momento minimo de 1a ordem",
            explanation="A verificacao tambem e feita no eixo y, usando a dimensao transversal correspondente.",
        )),
        _step(MathStep(
            id="column-minimum-moment-x",
            title="Momento minimo de 1a ordem no eixo x",
            formula_latex=r"M_{1d,min,x} = N_d \cdot e_{min,x}",
            substitution_latex=rf"M_{{1d,min,x}} = {_fmt(loads.Nd_kN, 2)} \cdot {_fmt(e_min_x, 4)}",
            result_latex=rf"M_{{1d,min,x}} = {_fmt(m_min_x, 2)}\,kN\,m",
            norm_ref="NBR 6118, momento minimo de 1a ordem",
            explanation="O momento de calculo usado no dimensionamento deve ser pelo menos o momento minimo normativo.",
        )),
        _step(MathStep(
            id="column-minimum-moment-y",
            title="Momento minimo de 1a ordem no eixo y",
            formula_latex=r"M_{1d,min,y} = N_d \cdot e_{min,y}",
            substitution_latex=rf"M_{{1d,min,y}} = {_fmt(loads.Nd_kN, 2)} \cdot {_fmt(e_min_y, 4)}",
            result_latex=rf"M_{{1d,min,y}} = {_fmt(m_min_y, 2)}\,kN\,m",
            norm_ref="NBR 6118, momento minimo de 1a ordem",
            explanation="Este e o momento minimo que deve ser respeitado na direcao y.",
        )),
        _step(MathStep(
            id="column-first-order-governing-x",
            title="Momento de 1a ordem governante no eixo x",
            formula_latex=r"M_{1d,x} = \max(|M_{xd}|, M_{1d,min,x})",
            substitution_latex=rf"M_{{1d,x}} = \max({_fmt(abs(loads.Mxd_kNm), 2)}, {_fmt(m_min_x, 2)})",
            result_latex=rf"M_{{1d,x}} = {_fmt(m1x, 2)}\,kN\,m",
            norm_ref="NBR 6118, verificacao de momento minimo",
            explanation="Este passo impede que o pilar seja dimensionado com momento artificialmente baixo.",
        )),
        _step(MathStep(
            id="column-first-order-governing-y",
            title="Momento de 1a ordem governante no eixo y",
            formula_latex=r"M_{1d,y} = \max(|M_{yd}|, M_{1d,min,y})",
            substitution_latex=rf"M_{{1d,y}} = \max({_fmt(abs(loads.Myd_kNm), 2)}, {_fmt(m_min_y, 2)})",
            result_latex=rf"M_{{1d,y}} = {_fmt(m1y, 2)}\,kN\,m",
            norm_ref="NBR 6118, verificacao de momento minimo",
            explanation="A mesma comparacao e repetida para o outro eixo principal da secao.",
        )),
        _step(MathStep(
            id="column-euler-critical-load-x",
            title="Carga critica de Euler no eixo x",
            formula_latex=r"P_{cr,x} = \frac{\pi^2 EI_x}{L_e^2}",
            substitution_latex=rf"P_{{cr,x}} = \frac{{\pi^2 EI_x}}{{({_fmt(le, 2)})^2}}",
            result_latex=rf"P_{{cr,x}} = {_fmt(pcx, 1)}\,kN",
            norm_ref="Modelo de amplificacao por rigidez nominal",
            explanation="A carga critica serve como referencia para amplificar o momento quando ha sensibilidade de segunda ordem.",
            status="ALERTA" if loads.Nd_kN >= 0.8 * pcx and pcx > 0 else "INFO",
        )),
        _step(MathStep(
            id="column-euler-critical-load-y",
            title="Carga critica de Euler no eixo y",
            formula_latex=r"P_{cr,y} = \frac{\pi^2 EI_y}{L_e^2}",
            substitution_latex=rf"P_{{cr,y}} = \frac{{\pi^2 EI_y}}{{({_fmt(le, 2)})^2}}",
            result_latex=rf"P_{{cr,y}} = {_fmt(pcy, 1)}\,kN",
            norm_ref="Modelo de amplificacao por rigidez nominal",
            explanation="Como as inercias podem ser diferentes, a carga critica tambem precisa ser avaliada nos dois eixos.",
            status="ALERTA" if loads.Nd_kN >= 0.8 * pcy and pcy > 0 else "INFO",
        )),
        _step(MathStep(
            id="column-second-order-factor-x",
            title="Amplificador de 2a ordem no eixo x",
            formula_latex=r"\eta_x = \frac{1}{1 - N_d/P_{cr,x}}",
            substitution_latex=rf"\eta_x = \frac{{1}}{{1 - {_fmt(loads.Nd_kN, 2)}/{_fmt(pcx, 1)}}}",
            result_latex=rf"\eta_x = {_fmt(factor_x, 3)}",
            norm_ref="Metodo da rigidez nominal - amplificacao aproximada",
            explanation="Quando a esbeltez exige 2a ordem, o momento de primeira ordem e amplificado por sensibilidade a instabilidade.",
            status="ALERTA" if factor_x > 1.10 else "OK",
        )),
        _step(MathStep(
            id="column-second-order-total-x",
            title="Momento total de calculo no eixo x",
            formula_latex=r"M_{d,x} = \eta_x \cdot M_{1d,x}",
            substitution_latex=rf"M_{{d,x}} = {_fmt(factor_x, 3)} \cdot {_fmt(m1x, 2)}",
            result_latex=rf"M_{{d,x}} = {_fmt(m_total_x, 2)}\,kN\,m",
            norm_ref="NBR 6118, efeitos locais de 2a ordem",
            explanation="Este e o momento final usado no dimensionamento biaxial no eixo x.",
            status="ALERTA" if factor_x > 1.10 else "OK",
        )),
        _step(MathStep(
            id="column-second-order-factor-y",
            title="Amplificador de 2a ordem no eixo y",
            formula_latex=r"\eta_y = \frac{1}{1 - N_d/P_{cr,y}}",
            substitution_latex=rf"\eta_y = \frac{{1}}{{1 - {_fmt(loads.Nd_kN, 2)}/{_fmt(pcy, 1)}}}",
            result_latex=rf"\eta_y = {_fmt(factor_y, 3)}",
            norm_ref="Metodo da rigidez nominal - amplificacao aproximada",
            explanation="O eixo menos rigido tende a apresentar maior sensibilidade aos efeitos de segunda ordem.",
            status="ALERTA" if factor_y > 1.10 else "OK",
        )),
        _step(MathStep(
            id="column-second-order-total-y",
            title="Momento total de calculo no eixo y",
            formula_latex=r"M_{d,y} = \eta_y \cdot M_{1d,y}",
            substitution_latex=rf"M_{{d,y}} = {_fmt(factor_y, 3)} \cdot {_fmt(m1y, 2)}",
            result_latex=rf"M_{{d,y}} = {_fmt(m_total_y, 2)}\,kN\,m",
            norm_ref="NBR 6118, efeitos locais de 2a ordem",
            explanation="Este e o momento final usado no dimensionamento biaxial no eixo y.",
            status="ALERTA" if factor_y > 1.10 else "OK",
        )),
        _step(MathStep(
            id="column-design-strengths",
            title="Resistencias de calculo dos materiais",
            formula_latex=r"f_{cd} = \frac{f_{ck}}{\gamma_c}, \quad f_{yd} = \frac{f_{yk}}{\gamma_s}",
            substitution_latex=rf"f_{{cd}} = \frac{{{_fmt(sec.fck, 1)}}}{{1{','}4}}, \quad f_{{yd}} = \frac{{{_fmt(sec.fyk, 1)}}}{{1{','}15}}",
            result_latex=rf"f_{{cd}} = {_fmt(fcd, 2)}\,MPa,\quad f_{{yd}} = {_fmt(fyd, 2)}\,MPa",
            norm_ref="NBR 6118, coeficientes parciais de seguranca",
            explanation="Antes de dimensionar, as resistencias caracteristicas sao reduzidas pelos coeficientes de seguranca.",
        )),
        _step(MathStep(
            id="column-reinforcement-calculated",
            title="Armadura calculada por flexo-compressao",
            formula_latex=r"A_{s,calc} = \omega \cdot A_c \cdot \frac{f_{cd}}{f_{yd}}",
            substitution_latex=rf"A_{{s,calc}} = {design.get('omega', 0.0)} \cdot {_fmt(ac_cm2, 2)} \cdot \frac{{{_fmt(fcd, 2)}}}{{{_fmt(fyd, 2)}}}",
            result_latex=rf"A_{{s,calc}} = {_fmt(as_calc, 2)}\,cm^2",
            norm_ref="Flexo-compressao normal/obliqua - superficie de interacao simplificada",
            explanation="O parametro omega representa a demanda adimensional de armadura obtida pelo solver biaxial.",
            status="ALERTA" if as_calc > as_max else "INFO",
        )),
        _step(MathStep(
            id="column-reinforcement-minimum",
            title="Armadura longitudinal minima",
            formula_latex=r"A_{s,min} = \max(0{,}004A_c,\;0{,}15N_d/f_{yd})",
            substitution_latex=rf"A_{{s,min}} = \max({_fmt(as_min_geom, 2)}, {_fmt(as_min_force, 2)})",
            result_latex=rf"A_{{s,min}} = {_fmt(as_min, 2)}\,cm^2",
            norm_ref="NBR 6118, limites de armadura longitudinal em pilares",
            explanation="A armadura minima garante ductilidade e evita uma solucao numericamente suficiente, mas construtivamente pobre.",
        )),
        _step(MathStep(
            id="column-reinforcement-maximum",
            title="Armadura longitudinal maxima",
            formula_latex=r"A_{s,max} = 0{,}08A_c",
            substitution_latex=rf"A_{{s,max}} = 0{','}08 \cdot {_fmt(ac_cm2, 2)}",
            result_latex=rf"A_{{s,max}} = {_fmt(as_max, 2)}\,cm^2",
            norm_ref="NBR 6118, limite maximo de armadura em pilares",
            explanation="O limite maximo controla congestionamento, aderencia e viabilidade de montagem da armadura.",
        )),
        _step(MathStep(
            id="column-reinforcement-adopted",
            title="Armadura longitudinal adotada",
            formula_latex=r"A_s = \max(A_{s,calc}, A_{s,min})",
            substitution_latex=rf"A_s = \max({_fmt(as_calc, 2)}, {_fmt(as_min, 2)})",
            result_latex=rf"A_s = {_fmt(as_final, 2)}\,cm^2",
            norm_ref="NBR 6118, escolha da armadura longitudinal",
            explanation="A armadura final deve atender simultaneamente a demanda resistente e o minimo normativo.",
            status="ALERTA" if as_final > as_max else "OK",
        )),
        _step(MathStep(
            id="column-reinforcement-rate",
            title="Taxa de armadura adotada",
            formula_latex=r"\rho = \frac{A_s}{A_c}\cdot100",
            substitution_latex=rf"\rho = \frac{{{_fmt(design.get('As_final_cm2', 0.0), 2)}}}{{{_fmt(ac_cm2, 2)}}}\cdot100",
            result_latex=rf"\rho = {_fmt(rho, 2)}\%",
            norm_ref="NBR 6118, limites minimo e maximo de taxa de armadura",
            explanation="Taxas muito altas indicam congestionamento de barras e podem exigir aumento de secao.",
            status="ALERTA" if design.get("As_final_cm2", 0.0) > as_max else "OK",
        )),
        _step(MathStep(
            id="column-durability-cover",
            title="Cobrimento nominal por durabilidade",
            formula_latex=r"c_{nom,adotado} \geq c_{nom,min}",
            substitution_latex=rf"{_fmt(cover_adopted, 1)}\,mm \geq {_fmt(cover_required, 1)}\,mm",
            result_latex=r"\text{Atende}" if cover_adopted >= cover_required else r"\text{Nao atende}",
            norm_ref="NBR 6118, durabilidade e classe de agressividade ambiental",
            explanation="O cobrimento protege a armadura contra corrosao e deve respeitar a CAA informada.",
            status="OK" if cover_adopted >= cover_required else "ALERTA",
        )),
        _step(MathStep(
            id="column-final-decision",
            title="Decisao final do dimensionamento",
            formula_latex=r"Status = f(\lambda,\; A_s,\; A_{s,max},\; c_{nom})",
            substitution_latex=rf"\lambda_{{max}}={_fmt(max(lambda_x, lambda_y), 2)},\quad A_s={_fmt(as_final, 2)}\,cm^2,\quad A_{{s,max}}={_fmt(as_max, 2)}\,cm^2",
            result_latex=rf"Status = \text{{{design.get('status', 'n/d')}}}",
            norm_ref="Sintese didatica do Engine MESTRE",
            explanation=column_opinion if design.get("status") != "OK" else "O fechamento mostra se as verificacoes principais convergiram para atender ou revisar.",
            status="OK" if design.get("status") == "OK" else "ALERTA",
            opinion=column_opinion,
        )),
    ]

    return {
        "mode": "MESTRE",
        "element": "column",
        "title": "Roteiro didatico de dimensionamento de pilar",
        "units": {
            "length": "m, cm e mm conforme exibido",
            "force": "kN",
            "moment": "kNm",
            "reinforcement": "cm2",
        },
        "summary": {
            "section_cm": f"{sec.b * 100:.0f}x{sec.h * 100:.0f}",
            "Nd_kN": loads.Nd_kN,
            "Mxd_kNm": loads.Mxd_kNm,
            "Myd_kNm": loads.Myd_kNm,
            "fck_MPa": sec.fck,
            "fyk_MPa": sec.fyk,
            "As_final_cm2": design.get("As_final_cm2"),
            "rho_pct": design.get("rho_pct"),
            "status": design.get("status"),
        },
        "steps": steps,
    }


def build_beam_blackboard(result: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """
    Cria um roteiro didatico para vigas de concreto armado.

    O roteiro usa os resultados do solver premium e os parametros de entrada
    para expor formulas, substituicoes e verificacoes intermediarias.
    """
    summary = result.get("summary", {})
    design = result.get("design", {})
    diagrams = result.get("diagrams", {})
    reactions = result.get("reactions", {})
    flex_bottom = design.get("flexure_bottom", {})
    flex_top = design.get("flexure_top", {})
    shear = design.get("shear", {})
    crack = design.get("crack_width", {})
    deflection = design.get("deflection", {})
    anchorage = design.get("anchorage", {})
    durability = design.get("durability", {})

    L = float(summary.get("L_m", payload.get("L", 0.0)))
    b = float(summary.get("b_m", payload.get("b", 0.0)))
    h = float(summary.get("h_m", payload.get("h", 0.0)))
    fck = float(summary.get("fck_MPa", payload.get("fck", 30.0)))
    fyk = 500.0
    cover_mm = float(summary.get("cover_mm", durability.get("cover_mm", 30.0)))
    cover_m = cover_mm / 1000.0
    d = h - cover_m - 0.010
    fcd = fck / 1.4
    fyd = fyk / 1.15

    distributed = payload.get("distributed_loads") or []
    q_first_N_m = float(distributed[0].get("q_start", 0.0)) if distributed else 0.0
    q_first_kN_m = q_first_N_m / 1000.0
    self_weight_kN_m = b * h * 25.0 if payload.get("include_self_weight", True) else 0.0
    q_total_kN_m = q_first_kN_m + self_weight_kN_m
    gamma_f = float(payload.get("gamma_f", 1.4))

    m_pos = float(design.get("M_max_pos_kNm", 0.0))
    m_neg = abs(float(design.get("M_max_neg_kNm", 0.0)))
    m_max = max(m_pos, m_neg)
    v_sd = float(shear.get("Vsd_kN", 0.0))
    v_rd2 = float(shear.get("Vrd2_kN", 0.0))
    as_bottom = float(flex_bottom.get("As_cm2", 0.0))
    as_top = float(flex_top.get("As_cm2", 0.0))
    as_min = max(float(flex_bottom.get("As_min_cm2", 0.0)), float(flex_top.get("As_min_cm2", 0.0)))
    wk = float(crack.get("wk_mm", 0.0))
    wk_lim = float(crack.get("limit_mm", durability.get("wk_limit_mm", 0.3)))
    w_max = float(deflection.get("max_mm", summary.get("max_deflection_mm", 0.0)))
    w_lim = float(deflection.get("limit_mm", L * 1000 / 250 if L else 0.0))
    lb_cm = float(anchorage.get("lb_cm", 0.0))
    asw = float(shear.get("Asw_cm2_m", 0.0))
    beam_reasons = []
    if flex_bottom.get("domain") == "4":
        beam_reasons.append("Seção super-armada (Domínio 4) na armadura inferior - falta de ductilidade")
    if flex_top.get("domain") == "4":
        beam_reasons.append("Seção super-armada (Domínio 4) na armadura superior")
    if v_sd > v_rd2:
        beam_reasons.append(f"Esmagamento da biela: Vsd ({_fmt(v_sd, 2)} kN) > Vrd2 ({_fmt(v_rd2, 2)} kN)")
    if wk > wk_lim:
        beam_reasons.append(f"Abertura de fissuras excessiva: wk ({_fmt(wk, 3)} mm) > limite ({_fmt(wk_lim, 3)} mm)")
    if w_max > w_lim:
        beam_reasons.append(f"Flecha excessiva: w_max ({_fmt(w_max, 2)} mm) > limite L/250 ({_fmt(w_lim, 2)} mm)")
    if float(design.get("vibration", {}).get("f1_hz", 999.0)) < 4.0:
        beam_reasons.append(f"Vibração excessiva: frequência ({_fmt(design.get('vibration', {}).get('f1_hz'), 2)} Hz) < 4 Hz")
    if not durability.get("cover_ok", True):
        beam_reasons.append(f"Cobrimento insuficiente: adotado ({_fmt(cover_mm, 1)} mm) < exigido ({_fmt(durability.get('cover_required_mm'), 1)} mm)")

    # Unificar com motivos do solver MEF se houver
    solver_reasons = design.get("reasons", [])
    for sr in solver_reasons:
        if sr not in beam_reasons: beam_reasons.append(sr)

    beam_opinion = (
        "Parecer final: viga aprovada no roteiro pedagógico. As verificações de flexão, cisalhamento, fissuração e serviço atendem aos critérios da NBR 6118."
        if not beam_reasons and design.get("overall_status") == "ATENDE"
        else f"PARECER DE REVISÃO: A viga não atende aos critérios normativos pelos seguintes motivos: \n• " + "\n• ".join(beam_reasons) + "\n\nSugestão didática: Aumentar a altura da viga (h), o fck do concreto ou revisar as cargas aplicadas."
    )

    x_values = diagrams.get("x_m") or []
    m_values = diagrams.get("M_kNm") or []
    v_values = diagrams.get("V_kN") or []
    x_mmax = 0.0
    x_vmax = 0.0
    if x_values and m_values:
        m_index = max(range(len(m_values)), key=lambda i: abs(float(m_values[i])))
        x_mmax = float(x_values[m_index])
    if x_values and v_values:
        v_index = max(range(len(v_values)), key=lambda i: abs(float(v_values[i])))
        x_vmax = float(x_values[v_index])

    # Cálculo da carga total aplicada para o cheque de equilíbrio
    reaction_sum = sum(float(r.get("V_kN", 0.0)) for r in reactions.values()) if isinstance(reactions, dict) else 0.0
    applied_dist = 0.0
    for dl in payload.get("distributed_loads", []):
        xs = max(0.0, float(dl.get("x_start", 0.0)))
        xe = min(L, float(dl.get("x_end", L)))
        if xe > xs:
            q_avg = (float(dl.get("q_start", 0.0)) + float(dl.get("q_end", dl.get("q_start", 0.0)))) / 2.0
            applied_dist += (q_avg / 1000.0) * (xe - xs)
    
    applied_point = sum(float(pl.get("P", 0.0)) / 1000.0 for pl in payload.get("point_loads", []))
    applied_total = applied_dist + applied_point + (self_weight_kN_m * L)

    steps = [
        _step(MathStep(
            id="beam-useful-depth",
            title="Altura util da secao",
            formula_latex=r"d = h - c_{nom} - \phi/2",
            substitution_latex=rf"d = {_fmt(h * 100, 1)}\,cm - {_fmt(cover_mm / 10, 1)}\,cm - 1{','}0\,cm",
            result_latex=rf"d = {_fmt(d, 3)}\,m = {_fmt(d * 100, 1)}\,cm",
            norm_ref="NBR 6118, geometria resistente da secao",
            explanation="A altura util e a distancia entre a borda comprimida e o centro aproximado da armadura tracionada.",
        )),
        _step(MathStep(
            id="beam-self-weight",
            title="Peso proprio da viga",
            formula_latex=r"g_{pp} = b \cdot h \cdot \gamma_c",
            substitution_latex=rf"g_{{pp}} = {_fmt(b, 3)} \cdot {_fmt(h, 3)} \cdot 25",
            result_latex=rf"g_{{pp}} = {_fmt(self_weight_kN_m, 2)}\,kN/m",
            norm_ref="Peso especifico usual do concreto armado",
            explanation="O peso proprio entra automaticamente quando a opcao correspondente esta ativa no modelo.",
        )),
        _step(MathStep(
            id="beam-total-line-load",
            title="Carga distribuida total caracteristica",
            formula_latex=r"q_k = q_{aplicada} + g_{pp}",
            substitution_latex=rf"q_k = {_fmt(q_first_kN_m, 2)} + {_fmt(self_weight_kN_m, 2)}",
            result_latex=rf"q_k = {_fmt(q_total_kN_m, 2)}\,kN/m",
            norm_ref="Composicao de acoes verticais",
            explanation="Para uso didatico, a carga total mostra a soma entre a carga informada e o peso proprio.",
        )),
        _step(MathStep(
            id="beam-design-line-load",
            title="Carga distribuida de calculo",
            formula_latex=r"q_d = \gamma_f \cdot q_k",
            substitution_latex=rf"q_d = {_fmt(gamma_f, 2)} \cdot {_fmt(q_total_kN_m, 2)}",
            result_latex=rf"q_d = {_fmt(gamma_f * q_total_kN_m, 2)}\,kN/m",
            norm_ref="ELU fundamental simplificado",
            explanation="O coeficiente parcial de acoes transforma a carga caracteristica em carga de calculo.",
        )),
        _step(MathStep(
            id="beam-equilibrium-check",
            title="Cheque de equilibrio vertical",
            formula_latex=r"\sum R \approx q_k \cdot L",
            substitution_latex=rf"\sum R = {_fmt(reaction_sum, 2)}\,kN \quad ; \quad q_kL = {_fmt(q_total_kN_m, 2)} \cdot {_fmt(L, 2)}",
            result_latex=rf"\sum R = {_fmt(reaction_sum, 2)}\,kN,\quad q_kL = {_fmt(applied_total, 2)}\,kN",
            norm_ref="NBR 6118, Item 11.4 - Equilíbrio estático",
            explanation="Antes do dimensionamento, o professor pode conferir se reacoes e cargas estao na mesma ordem de grandeza.",
            status="OK" if applied_total == 0 or abs(reaction_sum - applied_total) / max(abs(applied_total), 1e-9) < 0.10 else "ALERTA",
        )),
        _step(MathStep(
            id="beam-max-moment-location",
            title="Ponto de momento fletor maximo",
            formula_latex=r"M_{max} = \max |M(x)|",
            substitution_latex=rf"M_{{max}} = \max |M(x_i)|,\quad x_i \in [0,{_fmt(L, 2)}]",
            result_latex=rf"M_{{max}} = {_fmt(m_max, 2)}\,kN\,m \quad em \quad x \approx {_fmt(x_mmax, 2)}\,m",
            norm_ref="NBR 6118, Item 14.6 - Análise linear",
            explanation="O solver percorre o diagrama e seleciona o ponto mais solicitante para a verificacao de flexao.",
        )),
        _step(MathStep(
            id="beam-max-shear-location",
            title="Ponto de cortante maximo",
            formula_latex=r"V_{max} = \max |V(x)|",
            substitution_latex=rf"V_{{max}} = \max |V(x_i)|,\quad x_i \in [0,{_fmt(L, 2)}]",
            result_latex=rf"V_{{max}} = {_fmt(v_sd, 2)}\,kN \quad em \quad x \approx {_fmt(x_vmax, 2)}\,m",
            norm_ref="NBR 6118, Item 14.6 - Análise linear",
            explanation="O cortante maximo governa a verificacao da biela comprimida e a armadura transversal.",
        )),
        _step(MathStep(
            id="beam-design-strengths",
            title="Resistencias de calculo",
            formula_latex=r"f_{cd} = \frac{f_{ck}}{\gamma_c}, \quad f_{yd} = \frac{f_{yk}}{\gamma_s}",
            substitution_latex=rf"f_{{cd}} = \frac{{{_fmt(fck, 1)}}}{{1{','}4}},\quad f_{{yd}} = \frac{{{_fmt(fyk, 1)}}}{{1{','}15}}",
            result_latex=rf"f_{{cd}} = {_fmt(fcd, 2)}\,MPa,\quad f_{{yd}} = {_fmt(fyd, 2)}\,MPa",
            norm_ref="NBR 6118, Item 12.4 - Valores de cálculo",
            explanation="As resistencias caracteristicas sao reduzidas antes do dimensionamento resistente.",
        )),
        _step(MathStep(
            id="beam-flexure-bottom",
            title="Armadura inferior por flexao positiva",
            formula_latex=r"A_s = \frac{M_{sd}}{f_{yd}\,d\,(1-0{,}4x/d)}",
            substitution_latex=rf"A_s = f(M_{{sd}}={_fmt(m_pos, 2)}\,kN\,m,\ d={_fmt(d, 3)}\,m,\ x/d={flex_bottom.get('x_over_d', 0)})",
            result_latex=rf"A_{{s,inf}} = {_fmt(as_bottom, 2)}\,cm^2",
            norm_ref="NBR 6118, Item 17.2.2 - Flexão simples",
            explanation="A armadura inferior resiste aos momentos positivos, normalmente no meio do vao.",
            status="ALERTA" if flex_bottom.get("domain") == "4" else "OK",
        )),
        _step(MathStep(
            id="beam-flexure-top",
            title="Armadura superior por flexao negativa",
            formula_latex=r"A'_s = \frac{|M_{sd,-}|}{f_{yd}\,d\,(1-0{,}4x/d)}",
            substitution_latex=rf"A'_s = f(|M_{{sd,-}}|={_fmt(m_neg, 2)}\,kN\,m,\ d={_fmt(d, 3)}\,m,\ x/d={flex_top.get('x_over_d', 0)})",
            result_latex=rf"A_{{s,sup}} = {_fmt(as_top, 2)}\,cm^2",
            norm_ref="NBR 6118, Item 17.2.2 - Flexão simples",
            explanation="Em vigas continuas, momentos negativos nos apoios exigem armadura superior.",
            status="ALERTA" if flex_top.get("domain") == "4" else "OK",
        )),
        _step(MathStep(
            id="beam-minimum-reinforcement",
            title="Armadura minima de flexao",
            formula_latex=r"A_{s,min} = \rho_{min} \cdot b_w \cdot d",
            substitution_latex=rf"A_{{s,min}} = \rho_{{min}} \cdot ({_fmt(b, 3)} \cdot {_fmt(d, 3)})",
            result_latex=rf"A_{{s,min}} = {_fmt(as_min, 2)}\,cm^2",
            norm_ref="NBR 6118, Item 17.3.5.2 - Armadura mínima",
            explanation="Mesmo com momento pequeno, a viga precisa de armadura minima para comportamento ductil.",
        )),
        _step(MathStep(
            id="beam-shear-biela",
            title="Verificacao da biela comprimida",
            formula_latex=r"V_{sd} \leq V_{Rd2}",
            substitution_latex=rf"{_fmt(v_sd, 2)} \leq {_fmt(v_rd2, 2)}",
            result_latex=r"\text{Atende}" if v_sd <= v_rd2 else r"\text{Nao atende}",
            norm_ref="NBR 6118, Item 17.4.2.2 - Biela comprimida",
            explanation="Se a biela comprimida nao atende, aumentar apenas estribos nao resolve; a secao/concreto deve ser revisto.",
            status="OK" if v_sd <= v_rd2 else "ALERTA",
        )),
        _step(MathStep(
            id="beam-stirrups",
            title="Armadura transversal",
            formula_latex=r"A_{sw}/s = \max(A_{sw,calc}, A_{sw,min})",
            substitution_latex=rf"A_{{sw}}/s = {_fmt(asw, 2)}\,cm^2/m",
            result_latex=rf"\text{{{shear.get('stirrup_spec', 'n/d')}}}",
            norm_ref="NBR 6118, Item 17.4.2.3 - Armadura transversal",
            explanation="O resultado comercial traduz a area por metro para uma sugestao de bitola e espacamento.",
        )),
        _step(MathStep(
            id="beam-crack-width",
            title="Abertura estimada de fissuras",
            formula_latex=r"w_k \leq w_{k,lim}",
            substitution_latex=rf"{_fmt(wk, 3)}\,mm \leq {_fmt(wk_lim, 3)}\,mm",
            result_latex=r"\text{Atende}" if wk <= wk_lim else r"\text{Nao atende}",
            norm_ref="NBR 6118, Item 17.3.3 - Fissuração",
            explanation="A fissuracao e verificada em servico e o limite depende da classe de agressividade ambiental.",
            status="OK" if wk <= wk_lim else "ALERTA",
        )),
        _step(MathStep(
            id="beam-deflection",
            title="Flecha maxima em servico",
            formula_latex=r"w_{max} \leq w_{lim}",
            substitution_latex=rf"{_fmt(w_max, 3)}\,mm \leq {_fmt(w_lim, 2)}\,mm",
            result_latex=r"\text{Atende}" if w_max <= w_lim else r"\text{Nao atende}",
            norm_ref="NBR 6118, Item 13.3 - Deformações excessivas",
            explanation="A flecha e uma verificacao de servico: a peca pode resistir, mas ainda assim deformar demais.",
            status="OK" if w_max <= w_lim else "ALERTA",
        )),
        _step(MathStep(
            id="beam-anchorage",
            title="Comprimento basico de ancoragem",
            formula_latex=r"l_b = \frac{\phi}{4}\frac{f_{yd}}{f_{bd}}",
            substitution_latex=rf"l_b = f(\phi={anchorage.get('phi_mm', 12.5)}\,mm,\ f_{{yd}}={_fmt(fyd, 2)}\,MPa)",
            result_latex=rf"l_b = {_fmt(lb_cm, 1)}\,cm",
            norm_ref="NBR 6118, Item 9.4 - Ancoragem",
            explanation="A barra precisa de comprimento suficiente para transferir tensoes ao concreto por aderencia.",
        )),
        _step(MathStep(
            id="beam-durability-cover",
            title="Cobrimento nominal por durabilidade",
            formula_latex=r"c_{nom,adotado} \geq c_{nom,min}",
            substitution_latex=rf"{_fmt(float(durability.get('cover_mm', cover_mm)), 1)}\,mm \geq {_fmt(float(durability.get('cover_required_mm', cover_mm)), 1)}\,mm",
            result_latex=r"\text{Atende}" if durability.get("cover_ok", True) else r"\text{Nao atende}",
            norm_ref="NBR 6118, Item 7.4 - Cobrimento nominal",
            explanation="O cobrimento adotado e checado contra a classe de agressividade ambiental.",
            status="OK" if durability.get("cover_ok", True) else "ALERTA",
        )),
        _step(MathStep(
            id="beam-final-decision",
            title="Decisao final da viga",
            formula_latex=r"Status = f(A_s,\ V_{sd},\ w_k,\ w_{max})",
            substitution_latex=rf"A_{{s,inf}}={_fmt(as_bottom, 2)},\ A_{{s,sup}}={_fmt(as_top, 2)},\ V_{{sd}}={_fmt(v_sd, 2)},\ w_k={_fmt(wk, 3)},\ w_{{max}}={_fmt(w_max, 3)}",
            result_latex=rf"\text{{{design.get('overall_status', 'n/d')}}}",
            norm_ref="Sintese didatica do Engine MESTRE",
            explanation=beam_opinion if design.get("overall_status") != "ATENDE" else "O fechamento mostra se as verificacoes principais convergiram para atender ou revisar.",
            status="OK" if design.get("overall_status") == "ATENDE" else "ALERTA",
            opinion=beam_opinion,
        )),
    ]

    return {
        "mode": "MESTRE",
        "element": "beam",
        "title": "Roteiro didatico de dimensionamento de viga",
        "units": {
            "length": "m, cm e mm conforme exibido",
            "force": "kN",
            "moment": "kNm",
            "reinforcement": "cm2 ou cm2/m",
        },
        "summary": {
            "L_m": L,
            "section_m": f"{b:.2f}x{h:.2f}",
            "q_kN_m": q_first_kN_m,
            "fck_MPa": fck,
            "As_bottom_cm2": as_bottom,
            "As_top_cm2": as_top,
            "Asw_cm2_m": asw,
            "status": design.get("overall_status"),
        },
        "steps": steps,
    }

def build_radier_audit_trail(config: Any, memorial: dict[str, Any]) -> dict[str, Any]:
    """
    Cria uma trilha de auditoria numerica detalhada para Radiers e Lajes,
    replicando o rigor didatico do Engine MESTRE para o ambiente UFO.
    """
    geotech = memorial.get("verificacoes_geotecnicas", {})
    structural = memorial.get("verificacoes_estruturais", {})
    service = memorial.get("verificacoes_de_servico", {})
    punch = structural.get("puncao", {})
    flex = structural.get("flexao", {})
    
    # Parametros base
    h = float(config.h)
    fck = float(config.fck)
    fcd = fck / 1.4
    sigma_adm = float(geotech.get("tensao_admissivel_kPa", 0.0))
    q_max = float(geotech.get("pressao_max_modelo_kPa", 0.0))
    
    steps = []
    
    # Passo 1: Pressao no Solo
    steps.append(_step(MathStep(
        id="geotech-pressure-check",
        title="Verificacao de pressao maxima no solo",
        formula_latex=r"\sigma_{max} \leq \sigma_{adm}",
        substitution_latex=rf"{_fmt(q_max, 2)}\,kPa \leq {_fmt(sigma_adm, 2)}\,kPa",
        result_latex=r"\text{Atende}" if q_max <= sigma_adm else r"\text{Revisar}",
        norm_ref="NBR 6122:2019, tensao admissivel em fundacoes superficiais",
        explanation="A pressao de contato calculada pelo modelo de Winkler nao deve superar a capacidade de carga do solo.",
        status="OK" if q_max <= sigma_adm else "ALERTA"
    )))
    
    # Passo 2: Puncao (se houver pilares)
    if punch.get("status") != "nao_aplicavel_sem_pilares":
        tau_sd = float(punch.get("tau_sd_MPa", 0.0))
        tau_rd1 = float(punch.get("tau_rd1_MPa", 0.0))
        beta = float(punch.get("beta", 1.0))
        
        steps.append(_step(MathStep(
            id="punching-shear-stress",
            title="Tensao solicitante de puncao (Contorno C')",
            formula_latex=r"\tau_{sd} = \frac{\beta \cdot V_{sd,net}}{u_1 \cdot d}",
            substitution_latex=rf"\tau_{{sd}} = f(\beta={_fmt(beta, 2)},\ u_1={_fmt(punch.get('u1_m', 0.0), 3)},\ d={_fmt(h-0.05, 3)})",
            result_latex=rf"\tau_{{sd}} = {_fmt(tau_sd, 3)}\,MPa",
            norm_ref="NBR 6118, item 19.5 - punção em lajes",
            explanation="A tensao solicitante considera o efeito de momentos via fator beta e a reacao liquida do solo.",
            status="OK" if tau_sd <= tau_rd1 else "ALERTA"
        )))
        
        steps.append(_step(MathStep(
            id="punching-resistance-check",
            title="Verificacao de resistencia a puncao (sem armadura)",
            formula_latex=r"\tau_{sd} \leq \tau_{rd1}",
            substitution_latex=rf"{_fmt(tau_sd, 3)}\,MPa \leq {_fmt(tau_rd1, 3)}\,MPa",
            result_latex=r"\text{Atende}" if tau_sd <= tau_rd1 else r"\text{Requer Reforço}",
            norm_ref="NBR 6118, resistencia a punção sem armadura transversal",
            explanation="Se a tensao ultrapassa tau_rd1, a laje exige armadura de puncao ou aumento de espessura.",
            status="OK" if tau_sd <= tau_rd1 else "ALERTA"
        )))

    # Passo 3: Fissuracao
    wk_max = max(float(service.get("wk_x_max_mm", 0.0)), float(service.get("wk_y_max_mm", 0.0)))
    wk_lim = float(service.get("wk_limit_mm", 0.3))
    steps.append(_step(MathStep(
        id="service-cracking-check",
        title="Abertura maxima de fissuras (ELS-W)",
        formula_latex=r"w_k = \max(w_{k,x}, w_{k,y}) \leq w_{k,lim}",
        substitution_latex=rf"{_fmt(wk_max, 3)}\,mm \leq {_fmt(wk_lim, 1)}\,mm",
        result_latex=r"\text{Atende}" if wk_max <= wk_lim else r"\text{Revisar}",
        norm_ref="NBR 6118, item 17.3.3 - controle da fissuracao",
        explanation="O limite de abertura de fissuras garante a durabilidade da armadura conforme a classe de agressividade.",
        status="OK" if wk_max <= wk_lim else "ALERTA"
    )))

    # Passo Final: Parecer
    reasons = []
    if q_max > sigma_adm: reasons.append("Pressao no solo acima da admissivel")
    if punch.get("ratio_max", 0.0) > 1.0: reasons.append("Resistencia a puncao insuficiente sem reforco")
    if wk_max > wk_lim: reasons.append("Abertura de fissuras acima do limite normativo")
    
    opinion = (
        "Parecer final: Solução validada. As verificações geotécnicas e estruturais atendem aos critérios normativos."
        if not reasons else
        f"PARECER DE REVISÃO: A solução requer ajustes técnicos: \n• " + "\n• ".join(reasons)
    )

    return {
        "mode": "UFO_AUDIT",
        "element": "radier",
        "title": "Trilha de Auditoria Numérica (Forense/UFO)",
        "summary": {
            "status": "OK" if not reasons else "REVISAR",
            "opinion": opinion
        },
        "steps": steps
    }


def build_vigacross_blackboard(results: dict[str, Any], input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Cria um roteiro didatico para o motor Hardy Cross (Viga Cross).
    
    Este blackboard foca no processo de Hardy Cross e na verificacao de flechas.
    """
    spans = results.get("spans", [])
    reactions = results.get("reactions", [])
    max_deflection = results.get("maxDeflection", 0.0)
    audit = results.get("normativeAudit", [])
    
    # Metadados de entrada
    e_gpa = input_data.get("eGPa", 25)
    
    steps = []
    
    # Passo 1: Metodo de Hardy Cross (Sintese)
    steps.append(_step(MathStep(
        id="cross-method-summary",
        title="Distribuicao de Momentos (Hardy Cross)",
        formula_latex=r"M_{final} = M_{engastamento} + \sum (\text{Distribuicao} + \text{Transporte})",
        substitution_latex=rf"\text{{Iteracoes Realizadas: }} {len(results.get('iterations', []))}",
        result_latex=rf"M_{{max,abs}} = {_fmt(max([abs(s.get('moments', {}).get('left', 0)) for s in spans] + [abs(s.get('moments', {}).get('right', 0)) for s in spans]), 2)}\,kNm",
        norm_ref="Metodo de Hardy Cross para Estruturas Hiperestaticas",
        explanation="O metodo de Hardy Cross distribui os momentos de engastamento perfeito atraves de sucessivas iteracoes de equilibrio nos nos.",
        status="OK"
    )))
    
    # Passo 2: Reacoes de Apoio
    reaction_str = ", ".join([f"R{i+1}={_fmt(r.get('value', 0), 2)}kN" for i, r in enumerate(reactions)])
    steps.append(_step(MathStep(
        id="cross-reactions",
        title="Reacoes de Apoio",
        formula_latex=r"\sum V = 0",
        substitution_latex=rf"\text{{Total de Reacoes: }} {len(reactions)}",
        result_latex=rf"\text{{{reaction_str}}}",
        norm_ref="Equilibrio Estatico Global",
        explanation="As reacoes sao obtidas apos a convergencia dos momentos nos apoios.",
        status="OK"
    )))
    
    # Passo 3: Verificacao de Flechas (NBR 6118)
    reasons = []
    for i, span_audit in enumerate(audit):
        l_span = span_audit.get("spanLength", 0)
        f_max = span_audit.get("maxDeflection", 0)
        f_lim = span_audit.get("limit", 0)
        status = span_audit.get("status", "OK")
        
        if status != "OK":
            reasons.append(f"Vao {i+1}: Flecha ({_fmt(f_max, 2)}mm) > Limite ({_fmt(f_lim, 2)}mm)")
            
        steps.append(_step(MathStep(
            id=f"cross-deflection-span-{i+1}",
            title=f"Verificacao de Flecha - Vao {i+1} ({span_audit.get('spanId')})",
            formula_latex=rf"f_{{max}} \leq L/250",
            substitution_latex=rf"{_fmt(f_max, 2)}\,mm \leq {_fmt(l_span * 1000, 0)}/250 = {_fmt(f_lim, 2)}\,mm",
            result_latex=rf"\text{{{status}}}",
            norm_ref="NBR 6118, Item 13.3 - Limites de Deslocamento",
            explanation=f"A flecha maxima no vao de {_fmt(l_span, 1)}m deve respeitar o limite visual/estrutural de L/250.",
            status="OK" if status == "OK" else "ALERTA"
        )))

    # Passo Final: Parecer
    opinion = (
        "Parecer final: A estrutura atende aos criterios de equilibrio e deformacao (NBR 6118)."
        if not reasons else
        f"PARECER DE REVISÃO: A viga apresenta deformacoes excessivas em alguns vãos: \n• " + "\n• ".join(reasons) + "\n\nSugestão: Aumentar a inércia da seção ou reduzir os vãos."
    )

    return {
        "mode": "VIGA_CROSS",
        "element": "beam_continuous",
        "title": "Memorial de Calculo - Viga Continua (Hardy Cross)",
        "summary": {
            "metodo": "Hardy Cross (Iterativo)",
            "vaos": len(spans),
            "E_GPa": e_gpa,
            "flecha_max_mm": max_deflection,
            "status_geral": "OK" if not reasons else "REVISAR",
            "opinion": opinion
        },
        "steps": steps
    }


def build_stair_blackboard(result: dict[str, Any]) -> dict[str, Any]:
    """
    Roteiro didatico para dimensionamento de escada de lance unico.
    """
    steps = []
    L = result.get("L", 0.0)
    q = result.get("q", 0.0)
    Mk = result.get("Mk", 0.0)
    As = result.get("As_cm2_m", 0.0)
    
    steps.append(_step(MathStep(
        id="stair-load",
        title="Carga total projetada",
        formula_latex=r"q_{total} = q_{ext} + g_{pp}",
        substitution_latex=rf"q = {_fmt(q, 2)}\,kN/m^2",
        result_latex=rf"q = {_fmt(q, 2)}\,kN/m^2",
        norm_ref="NBR 6120, acoes em escadas",
        explanation="A carga considera o peso proprio da laje inclinada projetado no plano horizontal mais a sobrecarga de uso."
    )))
    
    steps.append(_step(MathStep(
        id="stair-moment",
        title="Momento fletor maximo",
        formula_latex=r"M_k = \frac{q \cdot L^2}{8}",
        substitution_latex=rf"M_k = \frac{{{_fmt(q, 2)} \cdot {_fmt(L, 2)}^2}}{{8}}",
        result_latex=rf"M_k = {_fmt(Mk, 2)}\,kNm/m",
        norm_ref="Modelo de viga bi-apoiada",
        explanation="Para escadas de lance unico, o modelo simplificado de viga bi-apoiada e usualmente adotado."
    )))
    
    steps.append(_step(MathStep(
        id="stair-reinforcement",
        title="Armadura longitudinal",
        formula_latex=r"A_s = \frac{M_d}{0{,}8 \cdot d \cdot f_{yd}}",
        substitution_latex=rf"A_s = f(M_d={_fmt(Mk*1.4, 2)}\,kNm/m)",
        result_latex=rf"A_s = {_fmt(As, 2)}\,cm^2/m",
        norm_ref="NBR 6118, dimensionamento de lajes a flexao",
        explanation="A armadura e calculada para resistir ao momento fletor majorado, garantindo a seguranca no ELU."
    )))

    return {
        "mode": "MESTRE",
        "element": "stair",
        "title": "Roteiro didatico: Escada de Lance Unico",
        "steps": steps
    }


def build_footing_blackboard(result: dict[str, Any]) -> dict[str, Any]:
    """
    Roteiro didatico para dimensionamento de sapata isolada rigida.
    """
    steps = []
    a = result.get("a_m", 0.0)
    b = result.get("b_m", 0.0)
    h = result.get("h_m", 0.0)
    sigma_adm = result.get("sigma_adm_kPa", 0.0)
    sigma_real = result.get("sigma_real_kPa", 0.0)
    As_a = result.get("As_a_cm2", 0.0)
    
    steps.append(_step(MathStep(
        id="footing-area",
        title="Dimensionamento da base",
        formula_latex=r"A_{req} = \frac{N \cdot 1{,}1}{\sigma_{adm}}",
        substitution_latex=rf"A_{{req}} = \frac{{N \cdot 1{,}1}}{{{_fmt(sigma_adm, 0)}}} \Rightarrow a \cdot b = {_fmt(a*b, 2)}\,m^2",
        result_latex=rf"a \times b = {_fmt(a, 2)} \times {_fmt(b, 2)}\,m",
        norm_ref="NBR 6122, pressao admissivel",
        explanation="A area da base e definida para que a pressao transmitida ao solo nao supere sua capacidade de carga."
    )))
    
    steps.append(_step(MathStep(
        id="footing-rigidity",
        title="Verificacao de rigidez",
        formula_latex=r"h \geq \frac{a - a_p}{3}",
        substitution_latex=rf"h = {_fmt(h, 2)}\,m",
        result_latex=r"\text{Rigida}" if h >= 0.3 else r"\text{Flexivel}",
        norm_ref="NBR 6118, classificacao de sapatas",
        explanation="Sapatas rigidas permitem uma distribuicao linear de pressoes no solo e dispensam verificacao detalhada de puncao se atenderem aos criterios geometricos."
    )))
    
    steps.append(_step(MathStep(
        id="footing-reinforcement",
        title="Armadura de flexao (Direcao a)",
        formula_latex=r"M_d = \sigma_d \cdot b \cdot \frac{l_a^2}{2}",
        substitution_latex=rf"A_s = {_fmt(As_a, 2)}\,cm^2",
        result_latex=rf"A_{{s,a}} = {_fmt(As_a, 2)}\,cm^2",
        norm_ref="Metodo das bielas / flexao simples",
        explanation="A armadura e calculada para resistir aos momentos fletores nas secoes de referencia da sapata."
    )))

    return {
        "mode": "MESTRE",
        "element": "footing",
        "title": "Roteiro didatico: Sapata Isolada Rigida",
        "steps": steps
    }


def build_reservoir_blackboard(result: dict[str, Any]) -> dict[str, Any]:
    """
    Roteiro didatico para reservatorios e piscinas.
    """
    steps = []
    summary = result.get("summary", {})
    vol = summary.get("volume_m3", 0.0)
    wk = summary.get("wk_max_mm", 0.0)
    As = summary.get("As_parede_cm2_m", 0.0)
    
    steps.append(_step(MathStep(
        id="res-volume",
        title="Volume de armazenamento",
        formula_latex=r"V = L_x \cdot L_y \cdot H",
        substitution_latex=rf"V = {_fmt(vol, 1)}\,m^3",
        result_latex=rf"V = {_fmt(vol, 1)}\,m^3 = {int(vol*1000)}\,L",
        norm_ref="Geometria hidraulica",
        explanation="Calculo da capacidade util do reservatorio baseada nas dimensoes internas informadas."
    )))
    
    steps.append(_step(MathStep(
        id="res-crack",
        title="Controle de fissuracao (Estanqueidade)",
        formula_latex=r"w_k \leq w_{k,lim} = 0{,}1\,mm",
        substitution_latex=rf"w_k = {_fmt(wk, 3)}\,mm \leq 0{,}1\,mm",
        result_latex=r"\text{Atende}" if wk <= 0.1 else r"\text{Risco de Vazamento}",
        norm_ref="NBR 6118, ELS-W para Classe IV",
        explanation="Em pecas em contato com agua, o limite de fissuracao e mais rigoroso (0.1mm) para garantir a estanqueidade e durabilidade."
    )))
    
    steps.append(_step(MathStep(
        id="res-reinforcement",
        title="Armadura das paredes (Empuxo)",
        formula_latex=r"A_s = f(M_{hidrostatico}, w_k)",
        substitution_latex=rf"A_s = {_fmt(As, 2)}\,cm^2/m",
        result_latex=rf"A_s = {_fmt(As, 2)}\,cm^2/m",
        norm_ref="Dimensionamento sob pressao de liquidos",
        explanation="A armadura final das paredes e geralmente governada pelo controle de fissuracao, resultando em taxas superiores as de pecas comuns."
    )))

    return {
        "mode": "MESTRE",
        "element": "reservoir",
        "title": "Roteiro didatico: Reservatorios e Estanqueidade",
        "steps": steps
    }


def build_detailing_blackboard(det_res: dict) -> List[Dict]:
    """Cria o roteiro didático do detalhamento executivo (Módulos 6-7)."""
    steps = [
        {
            "title": "1. Geometria e Decalagem",
            "latex": r"d = h - 4cm = " + f"{det_res['geometry']['h_cm'] - 4}cm" + r" \\ " +
                     r"a_l = 0.5 \cdot d \cdot (\cot \theta - \cot \alpha) = " + f"{det_res['geometry']['al_cm']}cm",
            "description": "Cálculo do deslocamento do diagrama de momentos para considerar a treliça de Mörsch."
        },
        {
            "title": "2. Ancoragem Básica (lb)",
            "latex": r"f_{bd} = 2.25 \cdot f_{ctd} \\ " +
                     r"l_b = \frac{\phi}{4} \cdot \frac{f_{yd}}{f_{bd}} = " + f"{det_res['inf']['lb_basic']}cm",
            "description": "Comprimento básico necessário para transferir os esforços da barra para o concreto."
        },
        {
            "title": "3. Ancoragem Necessária (lb,nec)",
            "latex": r"l_{b,nec} = \alpha \cdot l_b \cdot \frac{A_{s,calc}}{A_{s,efet}} \\ " +
                     r"l_{b,nec} = 1.0 \cdot " + f"{det_res['inf']['lb_basic']} \cdot " + 
                     f"\\frac{{{det_res['inf']['area_calc']}}}{{{det_res['inf']['area_efet']}}} = {det_res['inf']['lb_nec']}cm",
            "description": "Ajuste do comprimento de ancoragem pela taxa de armadura real utilizada."
        },
        {
            "title": "4. Resumo de Armaduras",
            "latex": r"\text{Inferior: } " + det_res['inf']['spec'] + r" \\ " +
                     r"\text{Superior: } " + det_res['sup']['spec'] + r" \\ " +
                     r"\text{Estribos: } " + det_res['stirrups'],
            "description": "Especificação final das bitolas e quantidades para execução."
        }
    ]
    return steps


def build_spt_blackboard(spt_res: dict) -> List[Dict]:
    """Cria o roteiro didático de interpretação de sondagem (Módulo 30-B)."""
    steps = [
        {
            "title": "1. Identificação da Camada Competente",
            "latex": r"N_{SPT, projeto} = " + f"{spt_res['nspt_design']} \\ " +
                     r"\text{Profundidade: } " + f"{spt_res['depth_m']}m",
            "description": "Busca-se a primeira camada com N_SPT >= 8 para assentamento de fundações superficiais."
        },
        {
            "title": "2. Estimativa da Tensão Admissível (Teixeira)",
            "latex": r"\sigma_{adm} = \frac{N_{SPT}}{5} \text{ (kgf/cm}^2) \\ " +
                     r"\sigma_{adm} = \frac{" + f"{spt_res['nspt_design']}" + r"}{5} = " + 
                     f"{spt_res['sigma_adm_kPa']/100.0} \text{ kgf/cm}^2",
            "description": "Correlação empírica clássica para solos brasileiros."
        },
        {
            "title": "3. Parâmetro de Projeto (SI)",
            "latex": r"\sigma_{adm} = " + f"{spt_res['sigma_adm_kPa']} \text{ kPa}",
            "description": "Conversão para quiloPascal para uso nos solvers de sapata e radier."
        }
    ]
    return steps


def build_stability_blackboard(wind_res: dict) -> List[Dict]:
    """Cria o roteiro didático de Estabilidade Global e Vento (Módulos 20+)."""
    steps = [
        {
            "title": "1. Velocidade Característica (Vk)",
            "latex": r"V_k = V_0 \cdot S_1 \cdot S_2 \cdot S_3 \\ " +
                     r"V_k = 30 \cdot 1.0 \cdot 0.95 \cdot 1.0 = 28.5 \text{ m/s}",
            "description": "Cálculo da velocidade do vento ajustada pela rugosidade do terreno e altura da edificação."
        },
        {
            "title": "2. Pressão Dinâmica (q)",
            "latex": r"q = 0.613 \cdot V_k^2 \\ " +
                     r"q = 0.613 \cdot 28.5^2 = 498 \text{ N/m}^2",
            "description": "Transformação da energia cinética do vento em pressão estática sobre as faces do edifício."
        },
        {
            "title": "3. Estabilidade Global (Gamma-Z)",
            "latex": r"\gamma_z \approx " + f"{wind_res['gamma_z']} \\ " +
                     r"\text{Status: } " + ("Estável" if wind_res['gamma_z'] <= 1.1 else "Sensível a 2ª Ordem"),
            "description": "O coeficiente Gamma-Z indica se os efeitos de segunda ordem globais podem ser desprezados (< 1.1)."
        }
    ]
    return steps
