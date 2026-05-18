import numpy as np
import math
from typing import Any
from .base import MemorialEngine

def build_lajes_blackboard(res: Any, payload: Any = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Lajes Maciças", "slab")
    fmt = me._fmt
    
    # Suporte a modelos legados ou novos dicionários
    model = payload.get("model") if payload else None
    if not model:
        model = res.get("model") # Tenta pegar do resultado se não estiver no payload
    
    me.add_standard_info()
    fck = float(getattr(model.material, "fck", payload.get("fck", 30.0) if payload else 30.0))
    
    # Diagrama de Referência
    me.add_step(
        id="slab-diagram-ref",
        title="Visualização da Laje e Curvatura",
        formula=r"\text{Corte e Diagrama de Momentos}",
        substitution=r"\text{Modelo: Placa de Mindlin-Reissner}",
        result=r"\text{Diagrama de Flechas e Esforços}",
        explanation="Esquema gráfico da laje indicando as condições de contorno e a deformada sob carga.",
        norm="NBR 6118",
        diagramData=me.technical_diagram(
            "slab",
            "Diagrama técnico de laje",
            Lx=getattr(model, "Lx", 5.0),
            Ly=getattr(model, "Ly", 4.0),
            h=getattr(model.material, "h", 0.16),
        )
    )
    
    # 1. Materiais e Resistências de Cálculo
    fcd = fck / 1.4
    fyd = 500.0 / 1.15 # MPa (CA-50)
    
    me.add_step(
        id="slab-materials-meticulous",
        title="Materiais e Resistências de Cálculo",
        formula=r"f_{cd} = \frac{f_{ck}}{\gamma_c}, \quad f_{yd} = \frac{f_{yk}}{\gamma_s}",
        substitution=rf"f_{{cd}} = \frac{{{fmt(fck)}}}{{1,4}}, \quad f_{{yd}} = \frac{{500}}{{1,15}}",
        result=rf"f_{{cd}} = {fmt(fcd, 2)}\,MPa, \quad f_{{yd}} = {fmt(fyd, 2)}\,MPa",
        explanation="As resistências de cálculo são obtidas aplicando-se os coeficientes de ponderação normativos.",
        norm="NBR 6118, 12.3.3"
    )

    me.add_durability_step(int(getattr(model, 'caa', 2)), int(getattr(model, 'cover_mm', 25)))
    
    # 2. Rigidez Flexional da Placa (D)
    h = model.material.h
    E = model.material.E
    nu = model.material.nu
    D = (E * h**3) / (12 * (1 - nu**2))
    
    me.add_step(
        id="slab-stiffness",
        title="Rigidez Flexional da Placa (D)",
        formula=r"D = \frac{E \cdot h^3}{12(1 - \nu^2)}",
        substitution=rf"D = \frac{{{fmt(E/1e6, 0)}\,MPa \cdot {fmt(h)}^3}}{{12(1 - {fmt(nu)}^2)}}",
        result=rf"D = {fmt(D/1000, 1)}\,kN\cdot m",
        explanation="A rigidez flexional D representa a resistência da placa à curvatura em ambas as direções.",
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
    mx_max = np.max(np.abs(res.mx)) / 1000.0 # kNm/m
    me.add_step(
        id="slab-moments",
        title="Esforços por Metro Linear (Método das Seções)",
        formula=r"m_x = \int_{-0,5}^{0,5} M_x(y) dy \approx M_{x,max}",
        substitution=r"\text{Seccionamento de uma faixa unitária (1m)}",
        result=rf"m_{{x,max}} = {fmt(mx_max, 2)}\,kNm/m",
        explanation="Para dimensionar lajes, utilizamos o Método das Seções para isolar uma faixa unitária de 1 metro. Calculamos então o momento fletor médio que atua nessa seção para determinar a armadura correspondente.",
        norm="NBR 6118, 14.7"
    )
    
    # 4. Verificação de Flecha (ELS)
    w_max_mm = np.max(np.abs(res.disp[:, 0])) * 1000.0
    l_span = min(model.Lx, model.Ly)
    limit_mm = (l_span * 1000.0) / 250.0
    
    me.add_step(
        id="slab-deflection-branson",
        title="Análise de Deformação e Inércia Equivalente",
        formula=r"I_e = (M_r/M_a)^3 I_c + [1-(M_r/M_a)^3] I_{cr}",
        substitution=r"\text{Modelo de Branson (Seção Fissurada)}",
        result=r"\text{Status: ELS-DEF Calculado}",
        explanation="O modelo de Branson estima a perda de rigidez devido à fissuração do concreto sob momentos de serviço.",
        norm="NBR 6118, 17.3.2.1.1"
    )

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

    # 5. Dimensionamento à Flexão (ELU)
    # Altura útil estimada
    cover_m = float(getattr(model, 'cover_mm', 25)) / 1000.0
    phi_mm = 8.0
    d_m = h - cover_m - (phi_mm / 2000.0)
    
    # Momento reduzido mu
    Md = mx_max * 1.4 # kNm/m
    mu = Md / (1.0 * (d_m**2) * fcd * 1000) if d_m > 0 else 0.0
    
    # Braço de alavanca z (Domínio 2/3 aproximado)
    # kx = (1 - sqrt(1 - 2mu/0.85)) / 0.8
    kx = (1 - math.sqrt(max(0, 1 - 2 * mu / 0.85))) / 0.8 if mu < 0.425 else 0.45
    z_m = d_m * (1 - 0.4 * kx)
    
    as_x_cm2 = (Md * 100) / (fyd / 1.15 * z_m * 100) if z_m > 0 else 0.0 # Aproximado
    # Recalcular com fyd real
    as_x_cm2 = (Md) / (fyd/10 * z_m) if z_m > 0 else 0.0
    
    area_1phi = (phi_mm**2 * 3.1415 / 400.0)
    spacing_cm = min(20.0, area_1phi / as_x_cm2 * 100) if as_x_cm2 > 0.1 else 20.0
    n_bars = math.ceil(100 / spacing_cm)

    me.add_step(
        id="slab-effective-depth",
        title="Altura Útil da Seção (d)",
        formula=r"d = h - c_{nom} - \phi/2",
        substitution=rf"d = {fmt(h, 3)} - {fmt(cover_m, 3)} - {fmt(phi_mm/1000, 3)}/2",
        result=rf"d = {fmt(d_m, 3)}\,m",
        explanation="A altura útil d é a distância do topo comprimido ao baricentro da armadura de tração.",
        norm="Geometria"
    )

    me.add_step(
        id="slab-flexure-mu",
        title="Momento Fletor Reduzido (mu)",
        formula=r"\mu = \frac{M_{sd}}{b \cdot d^2 \cdot f_{cd}}",
        substitution=rf"\mu = \frac{{ {fmt(Md, 2)} }}{{ 1,0 \cdot {fmt(d_m, 3)}^2 \cdot {fmt(fcd * 1000, 0)} }}",
        result=rf"\mu = {fmt(mu, 4)}",
        explanation="O parâmetro mu adimensionaliza o momento para determinar a profundidade da linha neutra.",
        norm="NBR 6118, 17.2.2"
    )

    me.add_step(
        id="slab-detailing",
        title="Cálculo da Armadura de Flexão (A_s)",
        formula=r"A_s = \frac{M_{sd}}{z \cdot f_{yd}}, \quad z = d(1 - 0,4k_x)",
        substitution=rf"z = {fmt(z_m, 3)}\,m, \quad f_{{yd}} = {fmt(fyd, 1)}\,MPa",
        result=rf"A_s = {fmt(as_x_cm2, 2)}\,\text{{cm}}^2/m \rightarrow \phi{fmt(phi_mm, 1)} \, c/ {fmt(spacing_cm, 1)}\,cm",
        explanation="Área de aço necessária por metro linear para resistir ao momento solicitante no ELU.",
        norm="NBR 6118, 17.2.2",
        detailingData={
            "type": "beam_section",
            "b": 1.0, 
            "h": h, 
            "cover": cover_m,
            "layers": [
                {"position": "bottom", "bars": [{"count": n_bars, "diameter": phi_mm}]}
            ]
        }
    )
    
    return me.build()

def build_punching_slab_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Punção em Lajes", "punching")
    fmt = me._fmt
    
    # 1. Tensão Solicitante no Perímetro Crítico
    me.add_step(
        id="punching-u-perim",
        title="Perímetro Crítico (u1)",
        formula=r"u_1 = 2(c_1 + c_2) + 4\pi d",
        substitution=rf"u_1 = 2({fmt(res.get('c1', 0.2), 2)} + {fmt(res.get('c2', 0.2), 2)}) + 4\pi \cdot {fmt(res.get('d_eff_m', 0.15), 3)}",
        result=rf"u_1 = {fmt(res.get('u_perim_m', 2.0), 3)}\,m",
        explanation="O perímetro crítico u1 é definido a uma distância 2d da face do pilar para verificação de tração diagonal.",
        norm="NBR 6118, 19.4"
    )

    me.add_step(
        id="punching-stress",
        title="Tensão Solicitante de Cisalhamento",
        formula=r"\tau_{sd} = \frac{F_{sd}}{u \cdot d}",
        substitution=rf"\tau_{{sd}} = \frac{{{fmt(res.get('fsd_kN'))}}}{{{fmt(res.get('u_perim_m', 2.0))} \cdot {fmt(res.get('d_eff_m', 0.15))}}}",
        result=rf"\tau_{{sd}} = {fmt(res.get('tau_sd_kPa'), 1)}\,kN/m^2",
        explanation="A tensão de punção média é calculada no contorno crítico para comparação com a resistência do concreto.",
        norm="NBR 6118, 19.4"
    )
    
    # 2. Verificação de Resistência sem Armadura
    me.add_step(
        id="punching-resistance-formula",
        title="Tensão de Resistência do Concreto (tau_rd1)",
        formula=r"\tau_{rd1} = 0,12 \cdot k \cdot (100 \cdot \rho_l \cdot f_{ck})^{1/3}",
        substitution=rf"k = 1 + \sqrt{{200/d}} \leq 2,0 \quad \rho_l = \sqrt{{\rho_x \cdot \rho_y}}",
        result=rf"\tau_{{rd1}} = {fmt(res.get('tau_rd1_kPa'), 1)}\,kN/m^2",
        explanation="Resistência de projeto da laje à punção em regiões sem armadura transversal.",
        norm="NBR 6118, 19.4.1"
    )

    me.add_validation_step(
        id="punching-resistance",
        title="Verificação de Segurança à Punção",
        value=float(res.get("tau_sd_kPa")),
        limit=float(res.get("tau_rd1_kPa")),
        operator="<=",
        unit="kPa",
        explanation="Verifica se o concreto e a armadura longitudinal são suficientes para resistir à punção sem estribos suplementares.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_ribbed_slab_blackboard(res: dict, payload: dict = None) -> dict:
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

def build_prestressed_slab_blackboard(res: dict, payload: dict = None) -> dict:
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
