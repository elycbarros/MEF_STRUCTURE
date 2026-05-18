from typing import Any
import math
from .base import MemorialEngine

def build_retaining_wall_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Muros de Arrimo", "retaining_wall")
    fmt = me._fmt
    
    me.add_standard_info()
    me.add_step(
        id="wall-thrust",
        title="Coeficiente de Empuxo Ativo (Rankine)",
        formula=r"k_a = \tan^2(45^\circ - \phi/2)",
        substitution=rf"k_a = \tan^2(45^\circ - {fmt(res.get('phi_soil', 30))}^\circ/2)",
        result=rf"k_a = {fmt(res.get('ka'), 3)}",
        explanation="O coeficiente Ka define a parcela da pressão vertical que se transforma em pressão lateral do solo.",
        norm="NBR 11682",
        diagramData=me.technical_diagram("retaining_wall", "Corte técnico - muro de arrimo", h=res.get("h_wall", 4.0), base=res.get("b_base", 2.5))
    )
    
    me.add_validation_step(
        id="wall-overturning",
        title="Segurança ao Tombamento (FS > 1.5)",
        value=float(res.get("fs_tomb")),
        limit=1.5,
        operator=">=",
        unit="",
        explanation="O momento estabilizador deve ser significativamente maior que o causado pelo empuxo.",
        norm="NBR 11682"
    )
    
    me.add_validation_step(
        id="wall-sliding",
        title="Segurança ao Deslizamento (FS > 1.5)",
        value=float(res.get("fs_desl")),
        limit=1.5,
        operator=">=",
        unit="",
        explanation="Verifica se o atrito na base do muro impede o seu deslocamento horizontal.",
        norm="NBR 11682"
    )
    
    return me.build()

def build_stairs_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Escadas", "stair")
    fmt = me._fmt
    fck = float(res.get("fck", 25))
    fcd = fck / 1.4
    fyd = 500 / 1.15

    me.add_standard_info()
    
    me.add_step(
        id="stairs-materials",
        title="Resistências de Cálculo",
        formula=r"f_{cd} = f_{ck}/1,4, \quad f_{yd} = f_{yk}/1,15",
        substitution=rf"f_{{cd}} = {fck}/1,4, \quad f_{{yd}} = 500/1,15",
        result=rf"f_{{cd}} = {fmt(fcd, 2)}\,MPa, \quad f_{{yd}} = {fmt(fyd, 2)}\,MPa",
        explanation="Redução das resistências características para obtenção dos valores de cálculo no ELU.",
        norm="NBR 6118, 12.3"
    )

    me.add_step(
        id="stairs-geometry",
        title="Geometria Inclinada e Carga Permanente",
        formula=r"g_{pp} = (h/\cos\alpha + p/2)\gamma_c",
        substitution=rf"\alpha = {fmt(res.get('alpha_deg'), 1)}^\circ, \quad \text{{thick}} = {fmt(res.get('thick', 0.15), 2)}\,m",
        result=rf"g_{{pp}} = {fmt(res.get('g_pp', 4.0), 2)}\,kN/m^2",
        explanation="O peso próprio considera a projeção inclinada da laje e o peso médio dos degraus.",
        norm="NBR 6120",
        diagramData=me.technical_diagram("stair", "Corte técnico - escada", L=res.get("L_horizontal", 4.0), alpha=res.get("alpha_deg", 30.0), h=res.get("thick", 0.15))
    )
    
    me.add_step(
        id="stairs-moment",
        title="Momento Fletor de Projeto (Método das Seções)",
        formula=r"M_d(x) = R_a x - \frac{q x^2}{2}",
        substitution=rf"R_a = {fmt(res.get('q_total_kN_m', 10.0) * res.get('L_horizontal', 4.0) / 2.0, 2)}\,kN",
        result=rf"M_{{d,max}} = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="Considerando a projeção horizontal da escada, o Método das Seções permite isolar o corpo livre inclinado e determinar o momento fletor máximo, que ocorre no meio do vão para condições biapoiadas.",
        norm="Resistência dos Materiais"
    )

    # 4. Detalhamento da Armadura
    as_calc = float(res.get('as_calc_cm2', 5.0))
    phi_mm = float(res.get('phi_mm', 10.0))
    # Estimativa de espaçamento
    spacing = min(20.0, (phi_mm**2 * 3.1415 / 400.0) / as_calc * 100) if as_calc > 0 else 20.0
    n_bars = math.ceil(100 / spacing)

    me.add_step(
        id="stairs-detailing",
        title="Detalhamento da Armadura de Flexão (Faixa de 1m)",
        formula=r"A_s = \frac{M_d}{0,9d \cdot f_{yd}}",
        substitution=rf"M_d = {fmt(res.get('m_max_kNm'), 2)}\,kNm/m \quad \phi = {fmt(phi_mm, 1)}\,mm",
        result=rf"\phi{fmt(phi_mm, 1)} \, c/ {fmt(spacing, 1)}\,cm",
        explanation="As barras longitudinais são dispostas na face inferior da laje da escada para resistir aos momentos de tração.",
        norm="NBR 6118, 20.1",
        detailingData={
            "type": "beam_section",
            "b": 1.0, 
            "h": float(res.get('thick', 0.15)), 
            "cover": 0.025,
            "layers": [
                {"position": "bottom", "bars": [{"count": n_bars, "diameter": phi_mm}]}
            ]
        }
    )
    
    return me.build()

def build_elevated_reservoir_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Reservatórios Elevados", "reservoir")
    fmt = me._fmt
    depth = res.get('H', res.get('depth', 3.0))
    
    me.add_standard_info()
    me.add_step(
        id="reservoir-pressure",
        title="Pressão Hidrostática nas Paredes",
        formula=r"p(z) = \gamma_w \cdot z",
        substitution=rf"p_{{max}} = 10 \cdot {fmt(depth, 2)}",
        result=rf"p_{{max}} = {fmt(res.get('p_max_kPa'), 1)}\,kN/m^2",
        explanation="A pressão hidrostática é a principal solicitação em paredes de reservatórios.",
        norm="NBR 6118",
        diagramData=me.technical_diagram("reservoir", "Diagrama técnico - reservatório", depth=depth, pressure=res.get("p_max_kPa", 0.0))
    )
    
    me.add_validation_step(
        id="reservoir-cracking",
        title="Controle de Fissuração (Estanqueidade)",
        value=float(res.get('wk_worst_mm', res.get('wk_limit_mm', 0.05))),
        limit=0.1,
        operator="<=",
        unit="mm",
        explanation="O limite de 0.1mm é rigoroso para garantir a impermeabilidade.",
        norm="NBR 6118, 17.3.3"
    )
    
    return me.build()

def build_corbel_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Consolos Curtos", "corbel")
    fmt = me._fmt
    
    # 1. Modelo de Biela-e-Tirante
    me.add_step(
        id="corbel-model",
        title="Modelo Estrutural: Biela-e-Tirante",
        formula=r"\tan\theta = d/a, \quad F_{tirante} = F_d \cdot (a/d)",
        substitution=rf"a/d = {fmt(res.get('ratio_ad'), 2)}, \quad d = {fmt(res.get('d_eff', 0.45), 2)}\,m, \quad a = {fmt(res.get('a_dist', 0.25), 2)}\,m",
        result=rf"F_{{tirante}} = {fmt(res.get('f_tirante_kN'), 1)}\,kN, \quad \theta = {fmt(res.get('theta_deg'), 1)}^\circ",
        explanation="Em elementos curtos, a analogia de biela-e-tirante substitui a teoria de vigas convencional.",
        norm="NBR 6118, 22.4"
    )
    
    # 2. Armadura Principal
    me.add_step(
        id="corbel-reinforcement",
        title="Armadura do Tirante Principal",
        formula=r"A_s = F_{tirante} / f_{yd}",
        substitution=rf"A_s = {fmt(res.get('f_tirante_kN'))} / 43,48",
        result=rf"A_s = {fmt(res.get('as_principal_cm2'), 2)}\,cm^2",
        explanation="O tirante de aço deve resistir integralmente à componente horizontal de tração.",
        norm="NBR 6118",
        diagramData=me.technical_diagram("corbel", "Biela e tirante - consolo", a=res.get("a_dist", 0.25), d=res.get("d_eff", 0.45))
    )
    
    return me.build()

def build_gerber_tooth_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Dentes Gerber", "gerber_tooth")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Armadura de Suspensão
    me.add_step(
        id="gerber-suspension",
        title="Armadura de Suspensão (Estribos)",
        formula=r"A_{s,susp} = V_d / f_{yd}",
        substitution=rf"A_{{s,susp}} = {fmt(res.get('vd_kN') * 1.4)} / 43,48",
        result=rf"A_{{s,susp}} = {fmt(res.get('as_suspensao_cm2'), 2)}\,cm^2",
        explanation="A armadura de suspensão é vital para ancorar a carga vertical na parte superior da viga principal.",
        norm="NBR 6118, 22.5.4.1"
    )
    
    # 2. Tirante Horizontal
    me.add_step(
        id="gerber-tie",
        title="Tirante Horizontal (Ash)",
        formula=r"A_{sh} = (V_d \cdot a/d + H_d) / f_{yd}",
        substitution=rf"V_d = {fmt(res.get('vd_kN') * 1.4)}, \quad a/d = \text{{projeto}}",
        result=rf"A_{{sh}} = {fmt(res.get('as_tirante_cm2'), 2)}\,cm^2",
        explanation="O tirante horizontal resiste à tração causada pela excentricidade do apoio.",
        norm="NBR 6118, 22.5.4.2",
        diagramData=me.technical_diagram("gerber_tooth", "Dente Gerber - esquema de tirantes", vd=res.get("vd_kN", 0.0), hd=res.get("hd_kN", 0.0))
    )
    
    return me.build()

def build_deep_beam_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Vigas Parede", "deep_beam")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Relação L/h
    me.add_step(
        id="deep-beam-ratio",
        title="Relação de Esbeltez (L/h)",
        formula=r"\lambda = L/h \le 2.0",
        substitution=rf"\lambda = {fmt(res.get('ratio_lh'), 2)}",
        result=r"\text{Viga Parede Validada}" if res.get('is_deep') else r"\text{Viga Convencional}",
        explanation="Vigas com relação L/h <= 2.0 não seguem a hipótese de Bernoulli.",
        norm="NBR 6118, 22.3"
    )
    
    # 2. Braço de Alavanca (z)
    me.add_step(
        id="deep-beam-lever",
        title="Ajuste do Braço de Alavanca (z)",
        formula=r"z = 0,2(L + 2h) \text{ para bi-apoiada}",
        substitution=rf"L = \text{{vão}}, \quad h = \text{{altura}}",
        result=rf"z = {fmt(res.get('z_m'), 2)}\,m",
        explanation="O braço de alavanca é reduzido devido à concentração de tensões na parte inferior da viga parede.",
        norm="NBR 6118",
        diagramData=me.technical_diagram("deep_beam", "Viga parede - fluxo de compressão", L=res.get("l_span", 4.0), h=res.get("height", 3.0))
    )
    
    return me.build()

def build_helical_stairs_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Escadas Helicoidais", "helical_stairs")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Efeitos Curvilíneos (Torção)
    me.add_step(
        id="helical-torsion",
        title="Efeitos de Torção em Viga Curva",
        formula=r"T_{max} = q \cdot R^2 (\alpha/2 - \sin(\alpha/2))",
        substitution=rf"R = {fmt(res.get('radius_m'))}\,m, \quad \alpha = \text{{ângulo total}}",
        result=rf"T_{{max}} = {fmt(res.get('t_max_kNm'), 2)}\,kNm",
        explanation="A curvatura gera um momento de torção que deve ser combatido com estribos fechados.",
        norm="NBR 6118"
    )
    
    # 2. Momento Fletor 3D
    me.add_step(
        id="helical-flexure",
        title="Momento Fletor no Vão",
        formula=r"M_{max} = q \cdot R^2 (1 - \cos(\alpha/2))",
        substitution=rf"q = {fmt(res.get('q_total_kN_m'))}\,kN/m",
        result=rf"M_{{max}} = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="O momento fletor ocorre simultaneamente à torção.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_pile_cap_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Blocos sobre Estacas", "pile_cap")
    fmt = me._fmt
    
    # 1. Reação nas Estacas
    me.add_step(
        id="pile-reaction",
        title="Reação de Apoio nas Estacas",
        formula=r"R = N_d / n_{estacas}",
        substitution=rf"R = {fmt(res.get('r_estaca_kN')*2)} / 2",
        result=rf"R = {fmt(res.get('r_estaca_kN'), 1)}\,kN",
        explanation="A carga do pilar é distribuída igualmente entre as estacas.",
        norm="Mecânica dos Sólidos"
    )
    
    # 2. Modelo de Biela-e-Tirante (Blevot)
    me.add_step(
        id="pile-cap-model",
        title="Modelo de Biela e Tirante (Blevot)",
        formula=r"T = R \cdot (a/d), \quad \theta = \arctan(d/a)",
        substitution=rf"\theta = {fmt(res.get('theta_deg'), 1)}^\circ",
        result=rf"F_{{tirante}} = {fmt(res.get('f_tirante_kN'), 1)}\,kN",
        explanation="O bloco funciona como uma treliça espacial.",
        norm="NBR 6118, 22.4"
    )
    
    # 3. Verificação da Biela de Compressão
    me.add_validation_step(
        id="pile-cap-strut",
        title="Verificação de Esmagamento da Biela",
        value=float(res.get("tensao_biela_kPa", 0)),
        limit=float(res.get("v_rd2_kPa", 1000)),
        operator="<=",
        unit="kPa",
        explanation="A tensão na biela de concreto deve ser inferior à resistência de projeto.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_beam_opening_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Furos em Vigas", "beam_opening")
    fmt = me._fmt
    
    # 1. Classificação da Abertura
    me.add_step(
        id="opening-type",
        title="Classificação da Abertura (NBR 6118)",
        formula=r"\text{Pequena se } \phi \leq 0,12h",
        substitution=rf"\phi = {fmt(res.get('d_opening'), 2)}\,m, \quad h = {fmt(res.get('h_beam'), 2)}\,m",
        result=r"\text{Furo Pequeno}" if res.get('is_small') else r"\text{Abertura Significativa}",
        explanation="Furos pequenos têm impacto limitado na rigidez global.",
        norm="NBR 6118, 13.2.5"
    )
    
    # 2. Reforço de Borda
    me.add_step(
        id="opening-reinforcement",
        title="Armadura de Reforço de Borda",
        formula=r"A_{s,ref} = V_d / f_{yd}",
        substitution=rf"A_{{s,ref}} = \text{{Reforço suplementar calculado}}",
        result=rf"A_{{s,ref}} = {fmt(res.get('as_reforco_cm2'), 2)}\,cm^2",
        explanation="Devem ser dispostos estribos e barras horizontais contornando o furo.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_concrete_wall_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Paredes de Concreto", "concrete_wall")
    fmt = me._fmt
    
    # 1. Verificação de Esbeltez
    me.add_step(
        id="wall-slenderness",
        title="Índice de Esbeltez da Parede",
        formula=r"\lambda = \frac{h \cdot \sqrt{12}}{t}",
        substitution=rf"h = {fmt(res.get('h_wall_m', 2.8))}\,m, \quad t = {fmt(res.get('t_wall_m', 0.12))}\,m",
        result=rf"\lambda = {fmt(res.get('lambda'), 1)}",
        explanation="Paredes são elementos comprimidos com grande largura.",
        norm="NBR 16055"
    )
    
    # 2. Capacidade de Carga Axial
    me.add_validation_step(
        id="wall-capacity",
        title="Resistência à Compressão (N_d)",
        value=float(res.get("nd_kN_m", 500)),
        limit=float(res.get("n_rd_kN_m", 1000)),
        operator="<=",
        unit="kN/m",
        explanation="A capacidade resistente considera a redução devido aos efeitos de segunda ordem.",
        norm="NBR 16055"
    )
    
    return me.build()

def build_tension_pro_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Protensão (Tension Pro)", "tension_pro")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Carga Equivalente
    me.add_step(
        id="tension-equivalent",
        title="Carga Equivalente de Protensão",
        formula=r"q_{eq} = \frac{8 \cdot P \cdot e}{L^2}",
        substitution=rf"P = {fmt(res.get('p0_kN'))}\,kN, \quad e = {fmt(res.get('eccentricity_m'))}\,m",
        result=rf"q_{{eq}} = {fmt(res.get('q_eq_kNm'), 2)}\,kN/m",
        explanation="A curvatura do cabo gera uma força distribuída ascendente que combate a carga gravitacional.",
        norm="NBR 6118"
    )
    
    # 2. Balanço de Cargas
    me.add_step(
        id="tension-balance",
        title="Grau de Balanceamento",
        formula=r"\text{Balanço} = \frac{q_{eq}}{q_{serv}} \cdot 100\%",
        substitution=rf"q_{{serv}} = {fmt(res.get('q_service_kNm'))}\,kN/m",
        result=rf"\text{Balanço} = {fmt(res.get('balance_ratio'), 1)}\%",
        explanation="Indica quanto da carga de serviço é compensada pela protensão.",
        norm="Prática de Projeto"
    )
    
    # 3. Tensões em Serviço
    me.add_validation_step(
        id="tension-stress",
        title="Tensão na Fibra Inferior (Tração)",
        value=float(res.get("stress_bottom_MPa", 0)),
        limit=float(res.get("fctm_MPa", 2.0)),
        operator="<=",
        unit="MPa",
        explanation="Verifica se a seção permanece comprimida ou com tração controlada.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_exam_auditor_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Laudo Pericial: Auditoria de Questões de Exames", "exam_auditor")
    fmt = me._fmt
    
    question_id = res.get("question_id", "q47_fcc_2018")
    correct = res.get("correct_reactions", {})
    exam = res.get("exam_reactions", {})
    model = res.get("model", {})
    solver_result = res.get("solver_result", {})
    
    me.add_standard_info()
    
    if question_id == "q47_fcc_2018":
        length = float(model.get("length_m", res.get("L", 8.0)))
        supports = model.get("supports", [])
        loads = model.get("point_loads", [])
        x_a = float(supports[0].get("x", 0.0)) if len(supports) > 0 else 0.0
        x_b = float(supports[1].get("x", 6.0)) if len(supports) > 1 else 6.0
        load = loads[0] if loads else {"x": length, "P": 30.0}
        x_p = float(load.get("x", length))
        p = float(load.get("P", 30.0))
        span_ab = abs(x_b - x_a)
        overhang = abs(x_p - x_b)
        ra = float(correct.get("Ra", 0.0))
        rb = float(correct.get("Rb", 0.0))
        rb_exam = float(exam.get("Rb", 0.0))
        divergence = abs(rb_exam - rb)
        max_moment = float(solver_result.get("summary", {}).get("max_moment_kNm", abs(ra * span_ab)))

        me.add_step(
            id="q47-moments",
            title="1. Equilíbrio de Momentos no Apoio B",
            formula=r"\sum M_B = 0 \Rightarrow R_A \cdot L_{AB} + P \cdot a = 0",
            substitution=rf"R_A \cdot {fmt(span_ab, 1)} + {fmt(p, 1)} \cdot {fmt(overhang, 1)} = 0",
            result=rf"R_A = {fmt(ra, 1)}\,kN \quad (\text{{{'Para baixo' if ra < 0 else 'Para cima'}}})",
            explanation=f"Modelo calculado: viga total de {fmt(length, 1)} m, apoio A em x={fmt(x_a, 1)} m, apoio B em x={fmt(x_b, 1)} m e carga pontual de {fmt(p, 1)} kN em x={fmt(x_p, 1)} m.",
            norm="Mecânica Clássica (Equilíbrio Estático)"
        )
        
        me.add_step(
            id="q47-vertical",
            title="2. Equilíbrio de Forças Verticais",
            formula=r"\sum F_z = 0 \Rightarrow R_A + R_B - P = 0",
            substitution=rf"{fmt(ra, 1)} + R_B - {fmt(p, 1)} = 0",
            result=rf"R_B = {fmt(rb, 1)}\,kN \quad (\text{{{'Para baixo' if rb < 0 else 'Para cima'}}})",
            explanation=f"O solver retorna momento máximo de {fmt(max_moment, 2)} kNm, coerente com o binário criado pela carga no balanço.",
            norm="Newton - 3ª Lei"
        )
        
        me.add_validation_step(
            id="q47-audit",
            title="Divergência Física no Gabarito Oficial (Erro da FCC)",
            value=divergence,
            limit=0.001,
            operator="<=",
            unit="kN",
            explanation=f"A banca informa Rb = {fmt(rb_exam, 1)} kN, enquanto o modelo físico calculado exige Rb = {fmt(rb, 1)} kN.",
            norm="Auditoria de Projetos"
        )
        
    elif question_id == "q31_vunesp_2021":
        reactions = solver_result.get("reactions", {})
        efforts = solver_result.get("member_efforts", {})
        ra = float(correct.get("Ra", 0.0))
        rb = float(correct.get("Rb", 0.0))
        rax = float(correct.get("Rax", 0.0))
        rax_exam = float(exam.get("Rax", 0.0))
        top_effort = efforts.get(2, efforts.get("2", {}))
        diagonal_effort = efforts.get(7, efforts.get("7", {}))
        top_member_n = float(top_effort.get("i", {}).get("N", 0.0))
        diagonal_n = float(diagonal_effort.get("i", {}).get("N", 0.0))
        width = float(model.get("width_m", res.get("L", 3.0)))
        height = float(model.get("height_m", res.get("h", 6.0)))
        divergence = abs(rax_exam - rax)

        me.add_step(
            id="q31-reactions",
            title="1. Reações de Apoio Globais",
            formula=r"\sum F_x = 0,\quad \sum F_z = 0,\quad \sum M = 0",
            substitution=rf"b = {fmt(width, 1)}\,m,\quad h = {fmt(height, 1)}\,m",
            result=rf"R_A = {fmt(ra, 1)}\,kN,\quad R_B = {fmt(rb, 1)}\,kN,\quad R_{{Ax}} = {fmt(rax, 1)}\,kN",
            explanation=f"As reações foram extraídas diretamente do solver de treliça. Nós de apoio retornados: {', '.join(reactions.keys()) if isinstance(reactions, dict) else 'A e B'}.",
            norm="Estática das Estruturas"
        )
        
        me.add_step(
            id="q31-axial",
            title="2. Esforço Axial nos Membros Superiores (EF)",
            formula=r"N_i = \mathbf{f}_{local}\cdot\mathbf{x}_{local}",
            substitution=rf"N_{{sup}} = {fmt(top_member_n, 2)}\,kN,\quad N_{{diag}} = {fmt(diagonal_n, 2)}\,kN",
            result=rf"N_{{sup}} = {fmt(top_member_n, 1)}\,kN \quad (\text{{{'Compressão' if top_member_n < 0 else 'Tração'}}})",
            explanation=f"A diagonal auditada retorna {fmt(diagonal_n, 2)} kN, valor compatível com a decomposição vetorial da malha treliçada.",
            norm="Método dos Nós / MEF"
        )
        
        me.add_validation_step(
            id="q31-audit",
            title="Divergência de Sinal na Reação Horizontal",
            value=divergence,
            limit=0.1,
            operator="<=",
            unit="kN",
            explanation=f"O gabarito usa Rax = {fmt(rax_exam, 1)} kN, mas o equilíbrio global do solver retorna Rax = {fmt(rax, 1)} kN.",
            norm="Auditoria Estrutural"
        )
        
    return me.build()
