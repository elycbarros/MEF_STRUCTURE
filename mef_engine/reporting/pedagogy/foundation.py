from typing import Any
import math
from .base import MemorialEngine

def build_footing_blackboard(res: dict[str, Any], payload: dict = None) -> dict[str, Any]:
    me = MemorialEngine("Roteiro Didático: Sapatas", "footing")
    fmt = me._fmt
    
    # 1. Padronização Mestre
    me.add_standard_info()
    
    # Diagrama de Referência
    me.add_step(
        id="footing-diagram-ref",
        title="Visualização da Fundação Isolada",
        formula=r"\text{Corte Transversal: Sapata e Pilar}",
        substitution=r"\text{Elementos: Sapata, Pescoço e Armadura}",
        result=r"\text{Diagrama Geotécnico}",
        explanation="Esquema gráfico da sapata indicando a profundidade de fundação (NF) e distribuição de pressões.",
        norm="NBR 6122 / NBR 6118",
        diagramData=me.technical_diagram(
            "footing",
            "Vista em corte - sapata isolada",
            A=res.get("A_m", 1.5),
            B=res.get("B_m", 1.5),
            h=res.get("h_m", 0.4),
            ap=res.get("a_col_m", res.get("ap", 0.4)),
            bp=res.get("b_col_m", res.get("bp", 0.4)),
            sigma=res.get("sigma_max_kPa", 0.0),
        )
    )
    
    fck = float(res.get("fck", 25.0))
    
    me.add_step(
        id="footing-materials",
        title="Materiais e Resistências",
        formula=rf"f_{{ck}} = {fmt(fck, 1)}\,MPa",
        substitution=rf"\text{{Concreto C{int(fck)}}}",
        result=rf"f_{{cd}} = {fmt(fck/1.4, 2)}\,\text{{MPa}}",
        explanation="Resistência característica do concreto para fundações.",
        norm="NBR 6118 / NBR 6122"
    )

    me.add_durability_step(int(res.get("caa", 2)), int(res.get("cover_mm", 40)))
    
    # 2. Geometria e Solo
    me.add_step(
        id="footing-pressure",
        title="Pressão no Solo",
        formula=r"\sigma = \frac{N_d}{A \cdot B}",
        substitution=rf"\sigma = \frac{{{fmt(res.get('Nd_kN'))}}}{{{fmt(res.get('A_m'))} \cdot {fmt(res.get('B_m'))}}}",
        result=rf"\sigma = {fmt(res.get('sigma_max_kPa'))}\,\text{{kPa}}",
        explanation="Verifica se a carga da sapata ultrapassa a capacidade de carga do solo.",
        norm="NBR 6122"
    )
    
    # 3. Rigidez (Sapata Rígida vs Flexível)
    h = float(res.get("h_m", 0.6))
    a_col = float(res.get("a_col_m", 0.2))
    is_rigid = (h >= (float(res.get("A_m", 1.5)) - a_col)/3.0)
    me.add_step(
        id="footing-rigidity",
        title="Verificação de Rigidez",
        formula=r"h \geq (A - a)/3",
        substitution=rf"{fmt(h)} \geq ({fmt(res.get('A_m'))} - {fmt(a_col)})/3",
        result=r"\text{Sapata Rígida}" if is_rigid else r"\text{Sapata Flexível}",
        explanation="Sapatas rígidas permitem considerar distribuição linear de tensões no solo.",
        norm="NBR 6118, 22.6"
    )
    
    # 4. Detalhamento da Armadura
    as_x = float(res.get("As_x_cm2", res.get("as_a_cm2", 5.0)))
    as_y = float(res.get("As_y_cm2", res.get("as_b_cm2", 5.0)))
    phi_mm = float(res.get("phi_mm", 10.0))
    n_x = math.ceil(as_x / (phi_mm**2 * 3.1415 / 400.0)) if as_x > 0 else 2
    n_y = math.ceil(as_y / (phi_mm**2 * 3.1415 / 400.0)) if as_y > 0 else 2

    me.add_step(
        id="footing-detailing",
        title="Detalhamento da Armadura de Flexão",
        formula=r"A_s = \frac{M_d}{0,9d \cdot f_{yd}}",
        substitution=rf"A_{{s,x}} = {fmt(as_x)}\,cm^2, \quad A_{{s,y}} = {fmt(as_y)}\,cm^2",
        result=rf"Eixo X: {n_x}\phi{fmt(phi_mm, 1)} \quad Eixo Y: {n_y}\phi{fmt(phi_mm, 1)}",
        explanation="As barras são distribuídas em malha na base da sapata para resistir aos momentos fletores em ambas as direções.",
        norm="NBR 6118, 22.6.4",
        detailingData={
            "type": "beam_section",
            "b": float(res.get("A_m", 1.5)), 
            "h": float(res.get("h_m", 0.4)), 
            "cover": float(res.get("cover_mm", 40)) / 1000.0,
            "layers": [
                {"position": "bottom", "bars": [{"count": n_x, "diameter": phi_mm}]}
            ]
        }
    )
    
    # 5. Auditoria Forensic (Structural Duel)
    if res.get("calculation_trace", {}).get("duel"):
        me.add_step(
            id="footing-forensic-duel",
            title="Duelo Estrutural: Comparação de Modelos",
            formula=r"\text{Bielas vs. Flexão}",
            substitution=r"\text{Auditoria Interna de Paridade}",
            result=res["calculation_trace"]["duel"][0]["verdict"] if isinstance(res["calculation_trace"]["duel"], list) else "Análise Concluída",
            explanation="Comparamos o método clássico de bielas e tirantes com o modelo de viga equivalente para garantir a redundância do cálculo.",
            norm="NBR 6118, 22.6.4"
        )

    return me.build()

def build_spt_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Interpretação de Sondagem SPT", "geotechnics")
    me.add_step(
        id="spt-interpretation",
        title="Tensão Admissível Estimada",
        formula=r"\sigma_{adm} \approx N_{spt} / 50 \text{ (simplificado)}",
        substitution=rf"\sigma_{{adm}} \approx {me._fmt(res.get('avg_nspt'))} / 50",
        result=rf"\sigma_{{adm}} \approx {me._fmt(res.get('sigma_adm_calc_kPa')/1000, 2)}\,MPa",
        explanation="Estimativa da capacidade de carga do solo com base no índice de penetração.",
        norm="Teoria de Terzaghi / Prática Brasileira"
    )
    return me.build()

def build_integrated_foundation_blackboard(spt_res: dict, footing_res: dict) -> dict:
    me = MemorialEngine("Memorial Integrado: Geotecnia + Fundação", "footing")
    fmt = me._fmt
    
    # 1. Análise Geotécnica
    me.add_step(
        id="geo-analysis",
        title="Capacidade de Carga do Solo (SPT)",
        formula=r"\sigma_{adm} = N_{spt}/50 \text{ (Teixeira)}",
        substitution=rf"N_{{spt}} = {fmt(spt_res.get('nspt_design'))}",
        result=rf"\sigma_{{adm}} = {fmt(spt_res.get('sigma_adm_kPa'))}\,kPa",
        explanation="A tensão admissível do solo é estimada a partir do ensaio de penetração padrão (SPT).",
        norm="NBR 6122",
        diagramData=me.technical_diagram(
            "footing",
            "Vista em corte - sapata isolada",
            A=footing_res.get("a_m", footing_res.get("A_m", 1.5)),
            B=footing_res.get("b_m", footing_res.get("B_m", 1.5)),
            h=footing_res.get("h_m", 0.4),
            sigma=footing_res.get("sigma_real_kPa", 0.0),
        )
    )
    
    # 2. Dimensionamento da Sapata
    me.add_step(
        id="footing-base",
        title="Geometria da Base da Sapata",
        formula=r"A_{req} = (N_d \cdot 1,1) / \sigma_{adm}",
        substitution=rf"A_{{req}} = ({fmt(footing_res.get('Nd_kN'))} \cdot 1,1) / {fmt(spt_res.get('sigma_adm_kPa'))}",
        result=rf"A = {fmt(footing_res.get('a_m'))} \times {fmt(footing_res.get('b_m'))}\,m \approx {fmt(footing_res.get('area_m2'), 2)}\,m^2",
        explanation="A área da base deve ser suficiente para distribuir a carga sem recalques excessivos.",
        norm="NBR 6118"
    )
    
    # 3. Verificação de Pressão
    me.add_validation_step(
        id="pressure-check",
        title="Verificação de Tensão no Solo",
        value=float(footing_res.get("sigma_real_kPa")),
        limit=float(spt_res.get("sigma_adm_kPa")),
        operator="<=",
        unit="kPa",
        explanation="A pressão real na base da sapata deve ser inferior à capacidade de carga do solo.",
        norm="NBR 6122"
    )
    
    return me.build()

def build_foundation_beam_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Vigas Alavanca", "foundation_beam")
    fmt = me._fmt
    
    # 1. Equilíbrio de Momentos
    me.add_step(
        id="strap-equilibrium",
        title="Equilíbrio de Forças (Viga de Transmissão)",
        formula=r"R_1 = \frac{P_1 \cdot L}{L - e}",
        substitution=rf"R_1 = \frac{{{fmt(res.get('r1_kN'))} \cdot {fmt(res.get('l_m'))}}}{{{fmt(res.get('l_m'))} - {fmt(res.get('ecc_m'))}}}",
        result=rf"R_1 = {fmt(res.get('r1_kN'), 1)}\,kN",
        explanation="A viga alavanca transfere a excentricidade do pilar de divisa para o pilar interno, reequilibrando as reações de apoio.",
        norm="NBR 6122"
    )
    
    # 2. Momento Fletor de Projeto
    me.add_step(
        id="strap-moment",
        title="Momento Fletor na Viga Alavanca",
        formula=r"M = P_1 \cdot e",
        substitution=rf"M = {fmt(res.get('r1_kN'))} \cdot {fmt(res.get('ecc_m'))}",
        result=rf"M = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="O momento fletor máximo ocorre na face do pilar de divisa e deve ser resistido pela viga alavanca.",
        norm="NBR 6118"
    )
    
    # 3. Verificação de Levantamento
    me.add_validation_step(
        id="strap-uplift",
        title="Verificação de Levantamento no Pilar Interno",
        value=float(res.get("r2_kN")),
        limit=0.0,
        operator=">",
        unit="kN",
        explanation="A reação no pilar interno deve ser positiva (compressão). Se for negativa, a sapata interna pode levantar.",
        norm="Equilíbrio"
    )
    
    return me.build()

def build_pile_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Estacas (Capacidade de Carga)", "pile")
    fmt = me._fmt
    
    cfg = res.get("config", {})
    geo = res.get("geotechnical", {})
    av = geo.get("aoki_velloso", {})
    dq = geo.get("decourt_quaresma", {})
    struct = res.get("structural", {})
    
    # 1. Geometria
    me.add_step(
        id="pile-geo",
        title="Geometria da Estaca",
        formula=rf"\phi = {fmt(cfg.get('diameter_m'))}\,m, \quad L = {fmt(cfg.get('length_m'))}\,m",
        substitution=f"Tipo: {cfg.get('type')}",
        result=rf"A_{{ponta}} = {fmt(av.get('area_ponta_m2'), 4)}\,m^2",
        explanation="Definição das dimensões geométricas para cálculo de áreas de fuste e ponta.",
        norm="NBR 6122"
    )
    
    # 2. Aoki-Velloso
    me.add_step(
        id="pile-av",
        title="Método Aoki-Velloso (1975)",
        formula=r"Q_u = \frac{q_p \cdot A_p}{F_1} + \sum \frac{q_s \cdot A_s}{F_2}",
        substitution=rf"F_1 = {fmt(av.get('f1'))}, \quad F_2 = {fmt(av.get('f2'))}",
        result=rf"Q_{{adm}} = {fmt(av.get('q_adm_kN'))}\,kN",
        explanation="O método utiliza coeficientes K e alpha dependentes do tipo de solo e fatores F1/F2 para o tipo de estaca.",
        norm="NBR 6122 / Aoki-Velloso"
    )
    
    # 3. Decourt-Quaresma
    me.add_step(
        id="pile-dq",
        title="Método Decourt-Quaresma (1978)",
        formula=r"Q_u = \alpha \cdot K \cdot N_p \cdot A_p + \beta \cdot 10 \cdot (\frac{N_s}{3} + 1) \cdot A_s",
        substitution=rf"N_{{s, médio}} = {fmt(dq.get('avg_nspt_fuste'))}",
        result=rf"Q_{{adm}} = {fmt(dq.get('q_adm_kN'))}\,kN",
        explanation="Método direto baseado no N_spt médio ao longo do fuste e na ponta.",
        norm="NBR 6122 / Decourt-Quaresma"
    )
    
    # 4. Verificação Estrutural
    me.add_validation_step(
        id="pile-struct",
        title="Verificação Estrutural (Compressão)",
        value=float(struct.get("nd_kN")),
        limit=float(struct.get("nr_concrete_kN")),
        operator="<=",
        unit="kN",
        explanation="A carga aplicada deve ser inferior à resistência do concreto da estaca, considerando os coeficientes de majoração e redução de concretagem.",
        norm="NBR 6118"
    )
    
    # 5. Conclusão Geotécnica
    me.add_validation_step(
        id="pile-geotech-final",
        title="Verificação Geotécnica Final",
        value=float(struct.get("nd_kN")),
        limit=float(geo.get("q_adm_final_kN")),
        operator="<=",
        unit="kN",
        explanation="Adota-se a menor capacidade entre os métodos semi-empíricos para maior segurança.",
        norm="NBR 6122"
    )
    
    # 6. Auditoria Forensic (Structural Duel)
    if res.get("calculation_trace", {}).get("duel"):
        me.add_step(
            id="pile-forensic-duel",
            title="Duelo Estrutural: Métodos Geotécnicos",
            formula=r"\text{Aoki-Velloso vs. Decourt-Quaresma}",
            substitution=rf"\Delta = {res['calculation_trace']['duel'][0].get('difference_percent', 0)}\%",
            result="Convergência" if res["calculation_trace"]["duel"][0].get("difference_percent", 0) < 25 else "Divergência",
            explanation="Verificação de paridade entre os dois métodos semi-empíricos mais difundidos na prática brasileira.",
            norm="NBR 6122"
        )

    return me.build()

def build_pile_cap_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Blocos sobre Estacas", "pile_cap")
    fmt = me._fmt
    
    # 1. Geometria e Esforços
    me.add_step(
        id="pile-cap-efforts",
        title="Distribuição de Cargas",
        formula=r"R_{estaca} = N_d / n",
        substitution=rf"R_{{estaca}} = {fmt(res.get('nd_kN'))} / 2",
        result=rf"R_{{estaca}} = {fmt(res.get('r_estaca_kN'))}\,kN",
        explanation="A carga do pilar é distribuída igualmente entre as estacas do bloco.",
        norm="NBR 6118"
    )
    
    # 2. Modelo de Biela (Blevot)
    me.add_step(
        id="pile-cap-blevot",
        title="Modelo de Biela e Tirante (Blevot)",
        formula=r"T = R \cdot \frac{a}{d}",
        substitution=rf"T = {fmt(res.get('r_estaca_kN'))} \cdot \frac{{a}}{{d}}",
        result=rf"T = {fmt(res.get('f_tirante_kN'))}\,kN",
        explanation="O método de Blevot calcula a tração no tirante (armadura principal) baseando-se no equilíbrio de forças na biela de concreto.",
        norm="Blevot & Frémy"
    )
    
    # 3. Verificação de Inclinação
    theta = res.get('theta_deg', 0)
    me.add_validation_step(
        id="pile-cap-theta",
        title="Ângulo da Biela",
        value=float(theta),
        limit=30.0,
        operator=">=",
        unit="°",
        explanation="O ângulo de inclinação da biela deve estar entre 30° e 60° para garantir a validade do modelo de bielas.",
        norm="NBR 6118"
    )
    
    # 4. Detalhamento
    me.add_step(
        id="pile-cap-detailing",
        title="Armadura Principal (Tirante)",
        formula=r"A_s = \frac{T}{f_{yd}}",
        substitution=rf"A_s = \frac{{{fmt(res.get('f_tirante_kN'))}}}{{f_{{yd}}}}",
        result=rf"A_s = {fmt(res.get('as_principal_cm2'), 2)}\,cm^2",
        explanation="Armadura calculada para resistir aos esforços de tração na base do bloco.",
        norm="NBR 6118"
    )

    # 5. Auditoria Forensic (Structural Duel)
    if res.get("calculation_trace", {}).get("duel"):
        me.add_step(
            id="pile-cap-forensic-duel",
            title="Duelo Estrutural: Biela vs. Viga",
            formula=r"\text{Blevot vs. Bernoulli}",
            substitution=r"\text{Auditoria de Modelagem}",
            result="Convergência" if res["calculation_trace"]["duel"][0]["difference_percent"] < 15 else "Divergência",
            explanation="Comparamos o modelo de bielas e tirantes com a teoria de vigas convencional para validar a rigidez do bloco.",
            norm="NBR 6118"
        )
    
    return me.build()
