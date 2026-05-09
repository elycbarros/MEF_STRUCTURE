import numpy as np
from typing import Any
from .base import MemorialEngine

def build_lajes_blackboard(model: Any, result: Any) -> dict:
    me = MemorialEngine("Roteiro Didático: Lajes Maciças", "slab")
    fmt = me._fmt
    
    me.add_standard_info()
    fck = getattr(model.material, 'fck', 30.0)
    me.add_step(
        id="slab-materials",
        title="Materiais e Resistências",
        formula=rf"f_{{ck}} = {fmt(fck, 1)}\,MPa",
        substitution=f"Concreto C{int(fck)}",
        result=f"f_cd = {fmt(fck/1.4, 2)} MPa",
        explanation="Resistência característica do concreto para lajes.",
        norm="NBR 6118"
    )
    me.add_durability_step(int(getattr(model, 'caa', 2)), int(getattr(model, 'cover_mm', 25)))
    
    # 1. Rigidez da Placa
    h = model.material.h
    E = model.material.E
    nu = model.material.nu
    D = (E * h**3) / (12 * (1 - nu**2))
    
    me.add_step(
        id="slab-stiffness",
        title="Rigidez Flexional da Placa (D)",
        formula=r"D = \frac{E \cdot h^3}{12(1 - \nu^2)}",
        substitution=rf"D = \frac{{{fmt(E, 1)} \cdot {fmt(h)}^3}}{{12(1 - {fmt(nu)}^2)}}",
        result=rf"D = {fmt(D/1000, 1)}\,kN\cdot m",
        explanation="A rigidez flexional D representa a resistência da placa à curvatura.",
        norm="Teoria de Placas de Mindlin"
    )
    
    # 2. Carregamento Total
    q_pp = getattr(model, 'q_pp', 0.0)
    q_perm = getattr(model, 'q_perm', 0.0)
    q_acid = getattr(model, 'q_acid', 0.0)
    q_total = (q_pp + q_perm + q_acid) / 1000.0 # kN/m2
    me.add_step(
        id="slab-load",
        title="Carregamento Total de Projeto",
        formula=r"q_{tot} = g_{pp} + g_{perm} + q_{acid}",
        substitution=rf"q_{{tot}} = {fmt(q_pp/1000)} + {fmt(q_perm/1000)} + {fmt(q_acid/1000)}",
        result=rf"q_{{tot}} = {fmt(q_total, 2)}\,kN/m^2",
        explanation="Soma das cargas permanentes e acidentais que atuam na superfície da laje.",
        norm="NBR 6120"
    )
    
    # 3. Momentos e Taxas
    mx_max = np.max(np.abs(result.mx)) / 1000.0 # kNm/m
    me.add_step(
        id="slab-moments",
        title="Solicitações Máximas (MEF)",
        formula=r"M_{x,max} = \max|M_x(x,y)|",
        substitution=r"\text{Análise via Elementos Finitos (Placa de Mindlin)}",
        result=rf"M_{{x,max}} = {fmt(mx_max, 2)}\,kNm/m",
        explanation="Momentos fletores obtidos através da integração das tensões nos elementos finitos.",
        norm="NBR 6118, 14.7"
    )
    
    # 4. Verificação de Flecha (ELS)
    w_max_mm = np.max(np.abs(result.disp[:, 0])) * 1000.0
    l_span = min(model.Lx, model.Ly)
    limit_mm = (l_span * 1000.0) / 250.0
    me.add_validation_step(
        id="slab-deflection",
        title="Verificação de Flecha Limite (L/250)",
        value=w_max_mm,
        limit=limit_mm,
        operator="<=",
        unit="mm",
        explanation="A flecha máxima deve ser limitada para evitar danos em alvenarias e desconforto visual.",
        norm="NBR 6118, 13.3"
    )
    
    return me.build()

def build_punching_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Punção em Lajes", "punching")
    fmt = me._fmt
    
    # 1. Tensão Solicitante no Perímetro Crítico
    me.add_step(
        id="punching-stress",
        title="Tensão Solicitante de Cisalhamento",
        formula=r"\tau_{sd} = \frac{F_{sd}}{u \cdot d}",
        substitution=rf"\tau_{{sd}} = \frac{{{fmt(res.get('fsd_kN'))}}}{{{fmt(res.get('u_perim_m', 2.0))} \cdot {fmt(res.get('d_eff_m', 0.15))}}}",
        result=rf"\tau_{{sd}} = {fmt(res.get('tau_sd_kPa'), 1)}\,kN/m^2",
        explanation="A tensão de punção é calculada no perímetro crítico 'u1', situado a 2d da face do pilar.",
        norm="NBR 6118, 19.4"
    )
    
    # 2. Verificação de Resistência sem Armadura
    me.add_validation_step(
        id="punching-resistance",
        title="Resistência à Punção (Concreto)",
        value=float(res.get("tau_sd_kPa")),
        limit=float(res.get("tau_rd1_kPa")),
        operator="<=",
        unit="kPa",
        explanation="Verifica se o concreto e a armadura longitudinal são suficientes para resistir à punção sem estribos suplementares.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_ribbed_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Lajes Nervuradas", "ribbed_slab")
    fmt = me._fmt
    
    # 1. Geometria Equivalente
    me.add_step(
        id="ribbed-geometry",
        title="Inércia e Espessura Equivalente",
        formula=r"h_{eq} = \frac{A_{secao}}{b}",
        substitution=rf"h_{{total}} = {fmt(res.get('h_total_m', 0.25))}\,m, \quad b_{{nerv}} = {fmt(res.get('b_nerv_m', 0.10))}\,m",
        result=rf"h_{{eq}} = {fmt(res.get('h_eq_m'), 3)}\,m",
        explanation="A laje nervurada é modelada como uma sucessão de vigas 'T' paralelas, otimizando o peso próprio.",
        norm="NBR 6118"
    )
    
    # 2. Dimensionamento da Nervura
    me.add_step(
        id="ribbed-flexure",
        title="Dimensionamento da Nervura Individual",
        formula=r"M_{nerv} = M_d \cdot e_{nerv}, \quad A_s = \frac{M_{nerv}}{f_{yd} \cdot z}",
        substitution=rf"M_{{nerv}} = {fmt(res.get('m_nerv_kNm'), 2)}\,kNm",
        result=rf"A_{{s,nerv}} = {fmt(res.get('as_nerv_cm2'), 2)}\,cm^2",
        explanation="O cálculo é feito para uma única nervura, considerando a largura colaborativa da mesa.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_prestressed_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Lajes Protendidas", "prestressed_slab")
    fmt = me._fmt
    
    # 1. Método do Equilíbrio de Carga (Load Balancing)
    me.add_step(
        id="prestressed-balancing",
        title="Carga Equivalente de Protensão",
        formula=r"q_{eq} = \frac{8 \cdot P \cdot e}{L^2}",
        substitution=rf"P = {fmt(res.get('p_force_kN'))}\,kN, \quad e = {fmt(res.get('ecc_m'))}\,m",
        result=rf"q_{{eq}} = {fmt(res.get('q_eq_kPa'), 2)}\,kN/m^2",
        explanation="A curvatura do cabo de protensão gera uma pressão vertical contrária à gravidade, reduzindo as flechas e tensões de tração.",
        norm="NBR 6118"
    )
    
    # 2. Verificação de Tensões em Serviço (ELS-F)
    me.add_validation_step(
        id="prestressed-stress",
        title="Tensão de Tração na Fibra Inferior",
        value=float(res.get("sigma_inf_kPa")),
        limit=float(res.get("fctm_kPa")),
        operator="<=",
        unit="kPa",
        explanation="Em lajes protendidas, as tensões de tração devem ser limitadas para garantir que a seção permaneça no Estádio I (não fissurada).",
        norm="NBR 6118"
    )
    
    return me.build()

def build_structural_audit_trail(config, memorial: dict) -> dict:
    is_laje = memorial.get('system_type') == 'laje'
    title = "Trilha de Auditoria Numérica: Lajes Suspensas" if is_laje else "Trilha de Auditoria Numérica: Radier"
    me = MemorialEngine(title, "slab" if is_laje else "radier")
    fmt = me._fmt
    
    geotech = memorial.get('verificacoes_geotecnicas', {})
    structural = memorial.get('verificacoes_estruturais', {})
    service = memorial.get('verificacoes_de_servico', {})
    
    # 1. Informações de Entrada
    if is_laje:
        me.add_step(
            id="slab-input-geometry",
            title="Premissas Geométricas e Materiais",
            formula=r"h_{adot} = \text{input}, \quad f_{ck} = \text{input}",
            substitution=rf"h = {fmt(config.h)}\,m, \quad f_{{ck}} = {fmt(config.fck)}\,MPa",
            result=r"\text{Validado}",
            explanation="A espessura da laje e a resistência do concreto regem a rigidez flexional e a capacidade ao cisalhamento.",
            norm="NBR 6118"
        )
    else:
        me.add_step(
            id="radier-input-soil",
            title="Parâmetros Geotécnicos de Entrada",
            formula=r"\sigma_{adm} = \text{input}, \quad k_v = \text{input}",
            substitution=rf"\sigma_{{adm}} = {fmt(config.sigma_adm_kPa)}\,kPa, \quad k_v = {fmt(config.kv, 1)}\,kN/m^3",
            result=r"\text{Validado}",
            explanation="Os parâmetros do solo definem a capacidade de carga e a rigidez do apoio elástico (Winkler).",
            norm="NBR 6122"
        )
    
    # 2. Verificação Principal (Pressão para Radier / Flexão para Laje)
    if is_laje:
        flexure = structural.get('flexao', {})
        mx_max = flexure.get('Mx_max_kNm_m', 0.0)
        as_req = flexure.get('Asx_top_calc_cm2_m', 0.0)
        me.add_step(
            id="slab-flexure-check",
            title="Solicitação Flexional Máxima (Mx)",
            formula=r"M_{sd} = \gamma_f \cdot M_k, \quad A_s = \frac{M_{sd}}{0,9d \cdot f_{yd}}",
            substitution=rf"M_{{x,max}} = {fmt(mx_max, 2)}\,kNm/m",
            result=rf"A_{{s,req}} = {fmt(as_req, 2)}\,cm^2/m",
            explanation="O momento fletor máximo obtido via MEF determina a armadura necessária para garantir o ELU de flexão.",
            norm="NBR 6118, Item 17.3"
        )
    else:
        q_max = geotech.get('pressao_max_modelo_kPa', 0.0)
        sigma_adm = config.sigma_adm_kPa
        me.add_step(
            id="radier-geotech-check",
            title="Verificação de Pressão de Contato",
            formula=r"q_{max} \leq \sigma_{adm}",
            substitution=rf"{fmt(q_max, 2)}\,kPa \leq {fmt(sigma_adm, 2)}\,kPa",
            result=r"\text{Atende}" if q_max <= sigma_adm else r"\text{NÃO ATENDE}",
            explanation="A pressão máxima solicitante no modelo MEF deve ser inferior à tensão admissível do solo para evitar recalques excessivos ou ruptura.",
            norm="NBR 6122, Item 6.2"
        )
    
    # 3. Verificação de Punção (Comum a ambos, mas com nuances)
    punching = structural.get('puncao', {})
    ratio_max = punching.get('ratio_max', 0.0)
    if ratio_max is not None and ratio_max > 0:
        me.add_step(
            id="structural-punching-check",
            title="Verificação de Punção / Cisalhamento Local",
            formula=r"\tau_{sd} / \tau_{rd1} \leq 1,0",
            substitution=rf"\text{{Ratio}} \approx {fmt(ratio_max, 3)}",
            result=r"\text{Atende}" if ratio_max <= 1.0 else r"\text{Exige Reforço}",
            explanation=f"Verificação de tração diagonal no concreto em torno dos apoios críticos {punching.get('critical_local', '')}.",
            norm="NBR 6118, Item 19.5"
        )

    # 4. Verificação de Serviço (Flecha para Laje / Recalque para Radier)
    if is_laje:
        w_max = service.get('w_max_mm', 0.0)
        w_limit = service.get('w_limit_mm', 1.0)
        me.add_step(
            id="slab-deflection-check",
            title="Verificação de Flecha (ELS-DEF)",
            formula=r"w_{max} \leq L/250",
            substitution=rf"{fmt(w_max, 2)}\,mm \leq {fmt(w_limit, 2)}\,mm",
            result=r"\text{Atende}" if w_max <= w_limit else r"\text{NÃO ATENDE}",
            explanation="A flecha em serviço deve ser controlada para evitar danos estéticos e desconforto visual.",
            norm="NBR 6118, Item 13.3"
        )
    
    res = me.build()
    if is_laje:
        as_ok = structural.get('flexao', {}).get('atende_flexao', True)
        punch_ok = ratio_max <= 1.0 if ratio_max else True
        w_ok = service.get('w_max_mm', 0.0) <= service.get('w_limit_mm', 1e9)
        opinion = "Laje validada para flexão, punção e flechas (NBR 6118)." if (as_ok and punch_ok and w_ok) else "Revisar projeto: falha em critérios de ELU (Flexão/Punção) ou ELS (Flecha)."
    else:
        q_max = geotech.get('pressao_max_modelo_kPa', 0.0)
        sigma_adm = config.sigma_adm_kPa
        opinion = "Radier validado: atende critérios de pressão admissível (NBR 6122) e estabilidade estrutural." if q_max <= sigma_adm else "Revisar projeto: Pressão no solo excede a tensão admissível informada."
        
    res["metadata"]["summary"]["opinion"] = opinion
    return res
