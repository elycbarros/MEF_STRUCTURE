from typing import Any
from .base import MemorialEngine

def build_retaining_wall_blackboard(res: dict) -> dict:
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
        norm="NBR 11682"
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

def build_stairs_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Escadas", "stairs")
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
        norm="NBR 6120"
    )
    
    me.add_step(
        id="stairs-moment",
        title="Momento Fletor de Projeto",
        formula=r"M_d = \gamma_f \frac{q \cdot L^2}{8}",
        substitution=rf"q = {fmt(res.get('q_total_kN_m', 10.0), 2)}\,kN/m, \quad L = {fmt(res.get('L_horizontal', 4.0), 2)}\,m",
        result=rf"M_d = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="Cálculo do esforço fletor máximo para dimensionamento da armadura longitudinal.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_elevated_reservoir_blackboard(res: dict) -> dict:
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
        norm="NBR 6118"
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

def build_corbel_blackboard(res: dict) -> dict:
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
        norm="NBR 6118"
    )
    
    return me.build()

def build_gerber_tooth_blackboard(res: dict) -> dict:
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
        norm="NBR 6118, 22.5.4.2"
    )
    
    return me.build()

def build_deep_beam_blackboard(res: dict) -> dict:
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
        norm="NBR 6118"
    )
    
    return me.build()

def build_helical_stairs_blackboard(res: dict) -> dict:
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

def build_pile_cap_blackboard(res: dict) -> dict:
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

def build_beam_opening_blackboard(res: dict) -> dict:
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

def build_concrete_wall_blackboard(res: dict) -> dict:
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
