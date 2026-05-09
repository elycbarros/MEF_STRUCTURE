import math
from typing import Any
from .base import MemorialEngine

def build_beam_blackboard(result: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """
    Geração meticulosa do memorial de cálculo para vigas (Elite Tier).
    """
    summary = result.get("summary", {})
    design = result.get("design", {})
    shear = design.get("shear", {})
    crack = design.get("crack_width", {})
    deflection = design.get("deflection", {})
    
    L = float(summary.get("L_m", payload.get("L", 0.0)))
    b = float(summary.get("b_m", payload.get("b", 0.0)))
    h = float(summary.get("h_m", payload.get("h", 0.0)))
    fck = float(summary.get("fck_MPa", payload.get("fck", 30.0)))
    d = float(summary.get("d_m", h - 0.04))
    caa = int(summary.get("caa", payload.get("caa", 2)))
    cover = int(summary.get("cover_mm", payload.get("cover_mm", 30)))
    
    me = MemorialEngine("Memorial de Cálculo: Viga de Concreto Armado", "beam")
    fmt = me._fmt
    
    # 1. Informações Normativas e Materiais
    me.add_standard_info()
    
    # 1.1 Materiais e Resistências de Cálculo
    fcd = fck / 1.4
    fyd = 500 / 1.15 # MPa
    Eci = 5600 * math.sqrt(fck) if fck <= 50 else 21500 * (fck/10 + 1.25)**(1/3)
    alpha_e = 0.8 + 0.2 * fck / 80.0 if fck > 50 else 0.85
    Ecs = alpha_e * Eci
    
    me.add_step(
        id="beam-materials-meticulous",
        title="Materiais e Resistências de Cálculo",
        formula=r"f_{cd} = \frac{f_{ck}}{\gamma_c}, \quad f_{yd} = \frac{f_{yk}}{\gamma_s}, \quad E_{cs} = \alpha_e \cdot 5600 \sqrt{f_{ck}}",
        substitution=rf"f_{{cd}} = \frac{{{fck}}}{{1,4}}, \quad f_{{yd}} = \frac{{500}}{{1,15}}, \quad E_{{cs}} = {fmt(alpha_e, 2)} \cdot 5600 \sqrt{{{fck}}}",
        result=rf"f_{{cd}} = {fmt(fcd, 2)}\,MPa, \quad f_{{yd}} = {fmt(fyd, 2)}\,MPa, \quad E_{{cs}} = {fmt(Ecs, 0)}\,MPa",
        explanation="As resistências de cálculo (design values) são obtidas aplicando-se os coeficientes de segurança ponderadores.",
        norm="NBR 6118:2023, 12.3.3"
    )

    me.add_durability_step(caa, cover)
    me.add_geometry_step(b, h, d)
    
    # 1.2 Propriedades de Inércia
    Ic = (b * h**3) / 12.0 # m4
    me.add_step(
        id="beam-inertia-elite",
        title="Propriedades Geométricas e Rigidez",
        formula=r"I_c = \frac{b \cdot h^3}{12}, \quad EI = E_{cs} \cdot I_c",
        substitution=rf"I_c = \frac{{{fmt(b, 2)} \cdot {fmt(h, 2)}^3}}{{12}}, \quad EI = {fmt(Ecs, 0)} \cdot {fmt(Ic, 7)}",
        result=rf"I_c = {fmt(Ic, 7)}\,m^4, \quad EI = {fmt(Ecs * 1000 * Ic, 0)}\,kN \cdot m^2",
        explanation="Propriedades utilizadas na matriz de rigidez global para o solver de elementos finitos Euler-Bernoulli.",
        norm="NBR 6118, 14.7"
    )

    # 2. Resumo de Ações e Reações
    distributed_loads = payload.get("distributed_loads") or []
    point_loads = payload.get("point_loads") or []
    total_distributed_kn = 0.0
    for dl in distributed_loads:
        q1 = float(dl.get("q_start", 0.0))
        q2 = float(dl.get("q_end", dl.get("q_start", 0.0)))
        total_distributed_kn += 0.5 * (q1 + q2) * max(float(dl.get("x_end", 0.0)) - float(dl.get("x_start", 0.0)), 0.0)
    total_point_kn = sum(float(p.get("P", 0.0)) for p in point_loads)
    
    reactions_raw = result.get("reactions", {})
    total_reaction = sum(float(r.get('R', 0.0)) for r in reactions_raw.values())
    
    me.add_step(
        id="beam-load-summary",
        title="Análise de Cargas e Equilíbrio Global",
        formula=r"F_{total} = \sum P_i + \int q(x) dx, \quad \sum R_v = F_{total}",
        substitution=rf"F_{{total}} = {fmt(total_point_kn, 1)} + {fmt(total_distributed_kn, 1)}",
        result=rf"F_{{total}} = {fmt(total_point_kn + total_distributed_kn, 2)}\,kN \approx \sum R = {fmt(total_reaction, 2)}\,kN",
        explanation="O equilíbrio estático global é verificado pela soma das reações nodais contra as ações aplicadas.",
        norm="Mecânica Estrutural"
    )

    # 3. Verificação ELU (Flexão e Ductilidade)
    flex = design.get("flexure_bottom", {})
    Md = float(flex.get("Md_kNm", summary.get("max_moment_kNm", 0.0) * 1.4))
    mu = Md / (b * (d**2) * fcd * 1000) if (b * d) > 0 else 0.0
    
    me.add_step(
        id="beam-flexure-mu",
        title="Dimensionamento à Flexão: Momento Adimensional",
        formula=r"\mu = \frac{M_{sd}}{b_w \cdot d^2 \cdot f_{cd}}",
        substitution=rf"\mu = \frac{{{fmt(Md, 2)}}}{{{fmt(b, 2)} \cdot {fmt(d, 2)}^2 \cdot {fmt(fcd * 1000, 0)}}}",
        result=rf"\mu = {fmt(mu, 4)}",
        explanation="O momento reduzido adimensional mu determina a posição da linha neutra no regime III de dimensionamento.",
        norm="NBR 6118, 17.2.2"
    )
    
    kx = float(flex.get('x_d', 0.0))
    kx_lim = float(flex.get('x_d_lim', 0.45))
    me.add_step(
        id="beam-flexure-elu",
        title="Posição da Linha Neutra e Ductilidade",
        formula=r"k_x = \frac{1 - \sqrt{1 - 2\mu/\eta}}{\lambda}, \quad k_x \leq k_{x,lim}",
        substitution=rf"k_x = {fmt(kx, 3)}, \quad k_{{x,lim}} = {fmt(kx_lim, 2)}",
        result=rf"\text{{Status: }} {'OK (Domínio 2/3)' if kx <= kx_lim else 'ALERTA (Domínio 4/Arm. Dupla)'}",
        explanation="Verifica-se a ductilidade da seção. Para concretos até C50, kx deve ser limitado a 0,45 para garantir aviso de ruptura.",
        norm="NBR 6118, 14.6.4.3"
    )
    
    as_bottom = float(flex.get('As_cm2', 0.0))
    me.add_step(
        id="beam-flexure-as",
        title="Cálculo da Armadura Longitudinal de Tração",
        formula=r"A_s = \frac{M_{sd}}{f_{yd} \cdot z}, \quad z = d \cdot (1 - 0,5 \lambda k_x)",
        substitution=rf"z = {fmt(d, 2)} \cdot (1 - 0,4 \cdot {fmt(kx, 3)}), \quad f_{{yd}} = {fmt(fyd, 1)}\,MPa",
        result=rf"A_s = {fmt(as_bottom, 2)}\,cm^2",
        explanation="Área de aço necessária para equilibrar o momento fletor solicitante de cálculo.",
        norm="NBR 6118, 17.2.2"
    )

    # 4. Dimensionamento à Força Cortante (ELU)
    v_sd = float(shear.get("Vsd_kN", summary.get("max_shear_kN", 0.0) * 1.4))
    v_rd2 = float(shear.get("Vrd2_kN", 0.0))
    asw_final = float(shear.get("Asw_cm2_m", 0.0))
    
    me.add_step(
        id="beam-shear-biela",
        title="Cisalhamento: Esmagamento da Biela",
        formula=r"V_{Rd2} = 0,27 \cdot \alpha_{v1} \cdot f_{cd} \cdot b_w \cdot d",
        substitution=rf"V_{{sd}} = {fmt(v_sd, 1)}\,kN, \quad V_{{Rd2}} = {fmt(v_rd2, 1)}\,kN",
        result=rf"\text{{Status: }} {shear.get('biela_status', 'OK')}",
        explanation="A verificação VRd2 garante que o concreto diagonal não esmagará sob esforços de compressão.",
        norm="NBR 6118, 17.4.2.2"
    )
    
    me.add_step(
        id="beam-shear-stirrps",
        title="Armadura Transversal (Estribos)",
        formula=r"A_{sw}/s = \frac{V_{sw}}{0,9 \cdot d \cdot f_{ywd}}",
        substitution=rf"V_{{sw}} = {fmt(shear.get('Vsw_kN', 0.0), 1)}\,kN",
        result=rf"A_{{sw}}/s = {fmt(asw_final, 2)}\,cm^2/m",
        explanation="Os estribos são dimensionados para resistir à parcela de tração diagonal não absorvida pelo concreto.",
        norm="NBR 6118, 17.4.2.2"
    )

    # 5. Estados Limites de Serviço (ELS)
    me.add_validation_step(
        id="beam-crack-width",
        title="Abertura de Fissuras (w_k)",
        value=float(crack.get("wk_mm", 0.0)),
        limit=float(crack.get("limit_mm", 0.3)),
        operator="<=",
        unit="mm",
        explanation="Limitação da abertura de fissuras para garantir a durabilidade e proteção contra corrosão.",
        norm="NBR 6118, 17.3.3"
    )
    
    me.add_validation_step(
        id="beam-deflection",
        title="Flecha Máxima (ELS-DEF)",
        value=float(deflection.get("max_mm", 0.0)),
        limit=float(deflection.get("limit_mm", L*1000/250)),
        operator="<=",
        unit="mm",
        explanation="A flecha é calculada considerando a inércia equivalente de Branson (seção fissurada).",
        norm="NBR 6118, 17.3.2"
    )
    
    return me.build()
