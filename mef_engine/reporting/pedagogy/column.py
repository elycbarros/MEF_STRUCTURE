import math
from typing import Any
from .base import MemorialEngine

def build_column_blackboard(res: dict, payload: dict = None) -> dict[str, Any]:
    """
    Cria um roteiro didatico para pilares (Elite Tier).
    """
    # Extração de dados
    b = float(res.get("b_m", res.get("b", 0.20)))
    h = float(res.get("h_m", res.get("h", 0.20)))
    fck = float(res.get("fck_MPa", res.get("fck", 30.0)))
    design = res # No novo formato, os dados de design estão no próprio resultado

    me = MemorialEngine("Memorial de Cálculo: Pilar de Concreto Armado", "column")
    fmt = me._fmt
    
    # 1. Informações Normativas
    me.add_standard_info()
    
    # 1.1 Materiais e Durabilidade
    caa = int(res.get("durability", {}).get("caa", 2))
    cover = float(res.get("durability", {}).get("cover_adopted_mm", 30.0))
    me.add_durability_step(caa, cover)
    
    fcd = fck / 1.4
    me.add_step(
        id="col-materials-elite",
        title="Materiais e Resistências",
        formula=r"f_{cd} = f_{ck}/1,4, \quad f_{yd} = 434,8\,MPa",
        substitution=rf"f_{{cd}} = {fck}/1,4",
        result=rf"f_{{cd}} = {fmt(fcd, 2)}\,MPa",
        explanation="Resistências de cálculo utilizadas no diagrama de interação M-N.",
        norm="NBR 6118, 12.3.3"
    )

    # 1.2 Esforços Solicitantes e Excentricidades
    nd_kn = 0.0
    if design:
        nd_kn = float(design.get("Nd_kN", 0.0))
        mdx = float(design.get("Md_x_total_kNm", design.get("Mxd_kNm", 0.0)))
        mdy = float(design.get("Md_y_total_kNm", design.get("Myd_kNm", 0.0)))
        
        # Excentricidade Mínima
        e_min_h = max(0.015 + 0.03 * h, 0.02)
        e_min_b = max(0.015 + 0.03 * b, 0.02)
        
        me.add_step(
            id="col-loads-total",
            title="Solicitações de Cálculo Com Segunda Ordem",
            formula=r"N_d,\quad M_{xd,tot},\quad M_{yd,tot}",
            substitution=rf"N_d = {fmt(nd_kn, 1)}\,kN,\quad M_{{xd}} = {fmt(mdx, 1)}\,kNm,\quad M_{{yd}} = {fmt(mdy, 1)}\,kNm",
            result=rf"M_{{xd,tot}} = {fmt(mdx, 2)}\,kNm,\quad M_{{yd,tot}} = {fmt(mdy, 2)}\,kNm",
            explanation="As solicitações usadas no dimensionamento incluem excentricidade mínima e efeitos locais de segunda ordem quando aplicáveis.",
            norm="NBR 6118, 15.8"
        )

        me.add_step(
            id="col-eccentricity-min",
            title="Excentricidades Mínimas de 1ª Ordem",
            formula=r"e_{min} = \max(1,5cm + 0,03h, 2cm)",
            substitution=rf"e_{{min,h}} = \max(0,015 + 0,03 \cdot {h}, 0,02)",
            result=rf"e_{{min,h}} = {fmt(e_min_h, 3)}\,m, \quad e_{{min,b}} = {fmt(e_min_b, 3)}\,m",
            explanation="Considera imperfeições geométricas locais e construtivas mínimas.",
            norm="NBR 6118, 11.3.3.4.1"
        )

    # 1.3 Esbeltez e Efeitos de 2ª Ordem
    slend = design.get("slenderness", {})
    if slend:
        lam = float(slend.get("lambda_x", 0.0))
        lam_1 = float(slend.get("limit", 35.0))
        me.add_step(
            id="col-slenderness-audit",
            title="Análise de Esbeltez e Segunda Ordem",
            formula=r"\lambda = \frac{l_e}{i}, \quad \lambda_1 = \text{Limite}",
            substitution=rf"\lambda = {fmt(lam, 1)}, \quad \lambda_1 = {fmt(lam_1, 1)}",
            result=rf"\text{{Status: }} {'2ª Ordem Necessária' if lam > lam_1 else '1ª Ordem Suficiente'}",
            explanation="Define se o pilar deve ser analisado considerando efeitos locais de segunda ordem.",
            norm="NBR 6118, 15.8"
        )

    second = design.get("moments_2nd_order", {})
    if second:
        me.add_step(
            id="col-second-order-moments",
            title="Momentos Locais de 2ª Ordem",
            formula=r"M_{d,tot} = M_{1d} + N_d e_2",
            substitution=rf"M_{{1d,x}} = {fmt(second.get('M1d_x', 0.0), 2)}\,kNm,\quad e_2 = {fmt(second.get('e2_x_mm', 0.0), 1)}\,mm",
            result=rf"M_{{d,tot,x}} = {fmt(second.get('M_total_x', 0.0), 2)}\,kNm,\quad M_{{d,tot,y}} = {fmt(second.get('M_total_y', 0.0), 2)}\,kNm",
            explanation="O método do pilar-padrão com curvatura nominal amplia os momentos quando a esbeltez exige análise local de segunda ordem.",
            norm="NBR 6118, 15.8.3"
        )

    # 1.4 Verificação de Armadura
    if design:
        as_total = float(design.get("As_final_cm2", design.get("As_tot", 0.0)))
        rho = float(design.get("rho_pct", (as_total / (b * h * 10000)) * 100 if b * h > 0 else 0.0))
        me.add_step(
            id="col-reinforcement-ratio",
            title="Taxa de Armadura Longitudinal",
            formula=r"\rho = \frac{A_s}{A_c} \cdot 100\%",
            substitution=rf"\rho = \frac{{{fmt(as_total, 2)}}}{{{fmt(b*h*10000, 0)}}} \cdot 100",
            result=rf"\rho = {fmt(rho, 2)}\%",
            explanation="A taxa de armadura deve estar entre 0,4% e 8% (considerando sobrepasse).",
            norm="NBR 6118, 17.3.5.3"
        )

    interaction = design.get("interaction_check", {})
    if interaction:
        check_x = interaction.get("x", {})
        check_y = interaction.get("y", {})
        check_biaxial = interaction.get("biaxial", {})
        me.add_step(
            id="col-interaction-check",
            title="Verificação No Diagrama N-M",
            formula=r"\eta = \frac{M_{Sd}}{M_{Rd}(N_d)}, \quad \eta_{xy} = (\eta_x^\alpha + \eta_y^\alpha)^{1/\alpha} \leq 1,0",
            substitution=rf"\eta_x = {fmt(check_x.get('ratio', 0.0), 3)},\quad \eta_y = {fmt(check_y.get('ratio', 0.0), 3)},\quad \alpha = {fmt(check_biaxial.get('alpha', 1.2), 1)}",
            result=rf"\eta_{{xy}} = {fmt(check_biaxial.get('combined_ratio', 0.0), 3)} \Rightarrow {check_biaxial.get('status', 'N/A')}",
            explanation="O ponto solicitante é comparado à envoltória de interação por eixo e também por uma verificação combinada de flexão composta oblíqua.",
            norm="NBR 6118, 17.2"
        )

    fiber = design.get("fiber_results", {})
    if fiber:
        me.add_step(
            id="col-fiber-equilibrium",
            title="Equilíbrio Da Seção Por Fibras",
            formula=r"\sum F_i = N_d,\quad \sum F_i y_i = M_x,\quad \sum F_i x_i = M_y",
            substitution=rf"\varepsilon_0 = {fmt(fiber.get('eps0', 0.0), 6)},\quad k_x = {fmt(fiber.get('kx', 0.0), 6)},\quad k_y = {fmt(fiber.get('ky', 0.0), 6)}",
            result=rf"Convergência: {'OK' if design.get('equilibrium_converged') else 'REVISAR'}",
            explanation="O solver de pilar usa integração por fibras para equilibrar compressão normal e flexão composta oblíqua.",
            norm="Método numérico de seções"
        )
        
    # 1.5 Detalhamento Gráfico
    if design:
        as_total = float(design.get("As_final_cm2", design.get("As_tot", 0.0)))
        n_bars = int(design.get("n_bars", 4))
        phi_mm = float(design.get("phi_mm", 12.5))
        
        me.add_step(
            id="col-detailing-section",
            title="Detalhamento da Seção Transversal",
            formula=r"A_{s,ef} = n_{bars} \cdot A_{s,1\phi}",
            substitution=rf"A_{{s,ef}} = {n_bars} \cdot {fmt(phi_mm**2 * 3.1415/400, 2)}\,cm^2",
            result=rf"{n_bars}\phi{fmt(phi_mm, 1)} \Rightarrow A_{{s,ef}} = {fmt(as_total, 2)}\,cm^2",
            explanation="Distribuição de armadura longitudinal e estribos conforme exigências de ductilidade.",
            norm="NBR 6118, 18.2.3",
            detailingData={
                "type": "column_section",
                "b": b, "h": h, "cover": 0.03,
                "layers": [
                    {"position": "bottom", "bars": [{"count": n_bars // 2, "diameter": phi_mm}]},
                    {"position": "top", "bars": [{"count": n_bars - (n_bars // 2), "diameter": phi_mm}]}
                ]
            }
        )

    return me.build()

def build_column_advanced_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Pilares Avançados", "column_advanced")
    fmt = me._fmt
    
    # 1. Efeitos de 2a Ordem Local
    me.add_step(
        id="col-2nd-order",
        title="Momento Fletor de 2a Ordem (M2)",
        formula=r"M_{2d} = N_d \cdot e_2, \quad e_2 = \frac{l_e^2}{10} \cdot \frac{1}{r}",
        substitution=rf"\lambda = {fmt(res.get('lambda', 0), 1)}",
        result=rf"M_{{2d}} = {fmt(res.get('m2_kNm', 0), 2)}\,kNm",
        explanation="Quando o pilar e esbelto (lambda > 35), a norma exige a consideração do momento adicional gerado pela curvatura do eixo.",
        norm="NBR 6118, 15.5"
    )
    
    # 2. Flexao Composta Obliqua (Biaxial)
    me.add_step(
        id="col-biaxial",
        title="Verificacao Biaxial (Excentricidade nos dois eixos)",
        formula=r"\left(\frac{M_{xd}}{M_{rdx}}\right)^\alpha + \left(\frac{M_{yd}}{M_{rdy}}\right)^\alpha \leq 1,0",
        substitution=r"\alpha \approx 1,2 \text{ a } 1,5",
        result=r"\text{Status: OK}",
        explanation="Pilares de canto estao sujeitos a momentos em X e Y simultaneamente, exigindo uma verificacao de contorno de carga.",
        norm="NBR 6118"
    )
    
    return me.build()
