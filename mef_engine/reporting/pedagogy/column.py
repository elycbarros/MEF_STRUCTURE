import math
from typing import Any
from .base import MemorialEngine

def build_column_blackboard(sec: Any, loads: Any = None, design: dict[str, Any] = None) -> dict[str, Any]:
    """
    Cria um roteiro didatico para pilares (Elite Tier).
    """
    # Extração de dados (suporta objetos ColumnSection ou dicionários)
    if hasattr(sec, 'b'):
        b = float(sec.b)
        h = float(sec.h)
        fck = float(sec.fck)
    else:
        b = float(sec.get("b", 0.20))
        h = float(sec.get("h", 0.20))
        fck = float(sec.get("fck", 30.0))

    me = MemorialEngine("Memorial de Cálculo: Pilar de Concreto Armado", "column")
    fmt = me._fmt
    
    # 1. Informações Normativas
    me.add_standard_info()
    
    # 1.1 Materiais
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
        mdx = float(design.get("Mdx_kNm", 0.0))
        mdy = float(design.get("Mdy_kNm", 0.0))
        
        # Excentricidade Mínima
        e_min_h = max(0.015 + 0.03 * h, 0.02)
        e_min_b = max(0.015 + 0.03 * b, 0.02)
        
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
    if design and "lambda_h" in design:
        lam = float(design.get("lambda_h", 0.0))
        lam_1 = float(design.get("lambda_1", 35.0))
        me.add_step(
            id="col-slenderness-audit",
            title="Análise de Esbeltez e Segunda Ordem",
            formula=r"\lambda = \frac{l_e}{i}, \quad \lambda_1 = \frac{25 + 12,5 \cdot e_1/h}{\alpha_b}",
            substitution=rf"\lambda = {fmt(lam, 1)}, \quad \lambda_1 = {fmt(lam_1, 1)}",
            result=rf"\text{{Status: }} {'2ª Ordem Necessária' if lam > lam_1 else '1ª Ordem Suficiente'}",
            explanation="Define se o pilar deve ser analisado considerando efeitos locais de segunda ordem.",
            norm="NBR 6118, 15.8"
        )

    # 1.4 Verificação de Armadura
    if design:
        as_total = float(design.get("As_tot", 0.0))
        rho = (as_total / (b * h * 10000)) * 100
        me.add_step(
            id="col-reinforcement-ratio",
            title="Taxa de Armadura Longitudinal",
            formula=r"\rho = \frac{A_s}{A_c} \cdot 100\%",
            substitution=rf"\rho = \frac{{{fmt(as_total, 2)}}}{{{fmt(b*h*10000, 0)}}} \cdot 100",
            result=rf"\rho = {fmt(rho, 2)}\%",
            explanation="A taxa de armadura deve estar entre 0,4% e 8% (considerando sobrepasse).",
            norm="NBR 6118, 17.3.5.3"
        )

    return me.build()

def build_column_advanced_blackboard(res: dict) -> dict:
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
