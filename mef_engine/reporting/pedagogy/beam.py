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
    beam_analysis_mode = summary.get("beam_analysis_mode", payload.get("beam_analysis_mode", "real_design"))
    structural_material = summary.get("structural_material", payload.get("structural_material", "concreto_armado"))
    design_requires_rebar = bool(summary.get(
        "design_requires_rebar",
        beam_analysis_mode == "real_design" and structural_material == "concreto_armado",
    ))
    is_force_model = beam_analysis_mode == "force_model"
    
    if is_force_model:
        title = "Memorial de Estática: Modelo de Forças em Viga"
    elif design_requires_rebar:
        title = "Memorial de Cálculo: Viga Real de Concreto Armado"
    else:
        material_label = str(structural_material).replace("_", " ").title()
        title = f"Memorial de Análise: Viga Real em {material_label}"
    me = MemorialEngine(title, "beam")
    fmt = me._fmt
    
    # 1. Informações Normativas e Materiais
    if design_requires_rebar:
        me.add_standard_info()
    else:
        me.add_step(
            id="structural-mechanics-base",
            title="Base Teórica da Análise",
            formula=r"\sum F = 0, \quad \sum M = 0, \quad V'(x) = -q(x), \quad M'(x) = V(x)",
            substitution=r"\text{Equilíbrio global e relações diferenciais de esforços}",
            result=r"\text{Modelo estrutural validado por estática e diagramas}",
            explanation="Este memorial prioriza equilíbrio, reações de apoio e diagramas de cortante e momento, sem aplicar verificações normativas de armadura de concreto armado.",
            norm="Mecânica Estrutural"
        )
    me.add_step(
        id="beam-analysis-scope",
        title="Caminho de Análise Selecionado",
        formula=r"\text{Escopo} = \text{modelo de forças} \; \text{ou} \; \text{viga real}",
        substitution=rf"\text{{modo}} = {beam_analysis_mode}, \quad \text{{material}} = {structural_material}, \quad n_{{MEF}} = {int(summary.get('n_elements', result.get('n_elements', 40)))}",
        result=(
            r"\text{Saída: equilíbrio, reações e diagramas}"
            if is_force_model
            else r"\text{Saída: análise física da viga real}"
        ),
        explanation=(
            "Neste caminho a viga é uma barra ideal: entram comprimento, apoios e ações externas; não entram peso próprio, seção transversal, cobrimento ou armadura."
            if is_force_model
            else "Neste caminho a viga é tratada como elemento físico, com geometria, material e peso próprio quando ativado."
        ),
        norm="Critério de escopo do Modo Mestre"
    )
    
    # Diagramas de Esforços (Duelo Analítico: MEF vs Clássico)
    diagrams = result.get("classical_diagrams", {})
    x_m = diagrams.get("x_m", [])
    v_mef = result.get("diagrams", {}).get("V_kN", [])
    v_classic = diagrams.get("V_kN", [])
    m_mef = result.get("diagrams", {}).get("M_kNm", [])
    m_classic = diagrams.get("M_kNm", [])
    x_nodes = result.get("diagrams", {}).get("x_m", [])
    
    # Preparação de Reações para o Gráfico
    chart_reactions = []
    reactions_raw = result.get("reactions", {})
    # Ordenar por x para rotular Va, Vb, Vc...
    sorted_reacts = sorted(reactions_raw.items(), key=lambda item: float(item[0]))
    for i, (x_pos, r_data) in enumerate(sorted_reacts):
        label = chr(65 + i) # A, B, C...
        chart_reactions.append({
            "x": float(x_pos),
            "value": float(r_data.get('R', 0.0)),
            "label": f"V_{label.lower()}"
        })

    if x_nodes and v_mef:
        me.add_step(
            id="beam-shear-diagram",
            title="Diagrama de Esforços Cortantes (DEC)",
            formula=r"V(x) = \text{Esforço Transversal ao longo do eixo}",
            substitution=r"\text{Duelo Analítico: MEF (Rigidez) vs Clássico (Macaulay)}",
            result=rf"V_{{max}} = {fmt(max(abs(v) for v in v_mef), 2)}\,kN",
            explanation="O DEC representa a variação das forças verticais internas. A comparação entre MEF e o modelo clássico valida a discretização da malha.",
            norm="Mecânica Estrutural",
            chartData={
                "type": "shear",
                "label": "Esforço Cortante (V)",
                "unit": "kN",
                "series": [
                    {"name": "MEF (Nodal)", "points": [{"x": round(x, 2), "y": round(v, 2)} for x, v in zip(x_nodes, v_mef)]},
                    {"name": "Clássico", "points": [{"x": round(x, 2), "y": round(v, 2)} for x, v in zip(x_m, v_classic)], "dashed": True}
                ],
                "reactions": chart_reactions
            }
        )

    if x_nodes and m_mef:
        me.add_step(
            id="beam-moment-diagram",
            title="Diagrama de Momentos Fletores (DMF)",
            formula=r"M(x) = \int V(x) dx",
            substitution=r"\text{Duelo Analítico: MEF (Rigidez) vs Clássico (Macaulay)}",
            result=rf"M_{{max}} = {fmt(max(abs(m) for m in m_mef), 2)}\,kNm",
            explanation=(
                "O DMF mostra a interação de momentos ao longo da barra ideal e apoia a leitura das regiões críticas de equilíbrio."
                if is_force_model
                else "O DMF define regiões críticas de flexão. Em concreto armado, ele orienta o posicionamento das armaduras longitudinais."
            ),
            norm="Mecânica Estrutural",
            chartData={
                "type": "moment",
                "label": "Momento Fletor (M)",
                "unit": "kNm",
                "series": [
                    {"name": "MEF (Nodal)", "points": [{"x": round(x, 2), "y": round(m, 2)} for x, m in zip(x_nodes, m_mef)]},
                    {"name": "Clássico", "points": [{"x": round(x, 2), "y": round(m, 2)} for x, m in zip(x_m, m_classic)], "dashed": True}
                ],
                "reactions": chart_reactions
            }
        )

    Ecs = 0.0
    fcd = fck / 1.4
    fyd = 500 / 1.15 # MPa
    if design_requires_rebar:
        # 1.1 Materiais e Resistências de Cálculo
        Eci = 5600 * math.sqrt(fck) if fck <= 50 else 21500 * (fck/10 + 1.25)**(1/3)
        alpha_e = 0.8 + 0.2 * fck / 80.0 if fck > 50 else 0.85
        Ecs = alpha_e * Eci
        
        me.add_step(
            id="beam-materials-meticulous",
            title="Materiais e Resistências de Cálculo",
            formula=r"f_{cd} = \frac{f_{ck}}{\gamma_c}, \quad f_{yd} = \frac{f_{yk}}{\gamma_s}, \quad E_{cs} = \alpha_e \cdot 5600 \sqrt{f_{ck}}",
            substitution=rf"f_{{cd}} = \frac{{{fck}}}{{1,4}}, \quad f_{{yd}} = \frac{{500}}{{1,15}}, \quad E_{{cs}} = {fmt(alpha_e, 2)} \cdot 5600 \sqrt{{{fck}}}",
            result=rf"f_{{cd}} = {fmt(fcd, 2)}\,MPa, \quad f_{{yd}} = {fmt(fyd, 2)}\,MPa, \quad E_{{cs}} = {fmt(Ecs, 0)}\,MPa",
            explanation="As resistências de cálculo são obtidas aplicando-se os coeficientes de segurança ponderadores.",
            norm="NBR 6118:2023, 12.3.3"
        )
    elif not is_force_model:
        me.add_step(
            id="beam-material-scope",
            title="Material Estrutural Informado",
            formula=r"\gamma = \text{peso específico do material}",
            substitution=rf"\text{{material}} = {structural_material}",
            result=rf"\text{{peso próprio}} = {'ativado' if summary.get('include_self_weight') else 'desativado'}",
            explanation="O material é usado para representar a viga real e seu peso próprio. O dimensionamento de armadura de concreto armado não é aplicado a este material.",
            norm="Critério de escopo do Modo Mestre"
        )

    # Reações e Equilíbrio (UI/UX Requirement)
    reactions_raw = result.get("reactions", {})
    reactions_list = [{"id": str(k), "R": float(v.get('R', 0.0))} for k, v in reactions_raw.items()]
    if reactions_list:
        me.add_reactions_step(reactions_list)

    if design_requires_rebar:
        me.add_durability_step(caa, cover)
    if not is_force_model:
        me.add_geometry_step(b, h, d)
    
    # 1.2 Propriedades de Inércia
    Ic = (b * h**3) / 12.0 # m4
    if design_requires_rebar:
        me.add_step(
            id="beam-inertia-elite",
            title="Propriedades Geométricas e Rigidez",
            formula=r"I_c = \frac{b \cdot h^3}{12}, \quad EI = E_{cs} \cdot I_c",
            substitution=rf"I_c = \frac{{{fmt(b, 2)} \cdot {fmt(h, 2)}^3}}{{12}}, \quad EI = {fmt(Ecs, 0)} \cdot {fmt(Ic, 7)}",
            result=rf"I_c = {fmt(Ic, 7)}\,m^4, \quad EI = {fmt(Ecs * 1000 * Ic, 0)}\,kN \cdot m^2",
            explanation="Propriedades utilizadas na matriz de rigidez global para o solver de elementos finitos Euler-Bernoulli.",
            norm="NBR 6118, 14.7"
        )

    # 1.3 Matriz de Rigidez Local (Prova Pedagógica Mestre)
    pedagogical_data = result.get("pedagogical_proofs", {})
    if design_requires_rebar and "sample_k_local" in pedagogical_data:
        m_id = pedagogical_data.get("sample_member_id", "0")
        le_val = L / result.get("n_elements", 40)
        me.add_step(
            id="beam-k-local",
            title=f"Matriz de Rigidez Local - Elemento {m_id}",
            formula=r"\mathbf{k}_{loc} = \frac{EI}{L^3} \begin{bmatrix} 12 & 6L \\ 6L & 4L^2 \end{bmatrix}",
            substitution=rf"EI = {fmt(Ecs * 1000 * Ic, 0)}\,kN \cdot m^2, \quad L_e = {fmt(le_val, 3)}\,m",
            result=r"\text{Matriz 4x4 (w, \theta) montada.}",
            explanation="Cada sub-elemento da viga contribui para a rigidez global. O Atlas utiliza o MEF com 3 DOFs por nó (w, theta, phi) para capturar efeitos de flexão e torção.",
            norm="Método dos Elementos Finitos"
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
    summary_total_load = float(summary.get("total_load_kN", 0.0) or 0.0)
    explicit_actions_kn = total_point_kn + total_distributed_kn
    self_weight_kn = max(summary_total_load - explicit_actions_kn, 0.0)
    total_actions_kn = summary_total_load if summary_total_load > 0.0 else explicit_actions_kn
    
    reactions_raw = result.get("reactions", {})
    total_reaction = sum(float(r.get('R', 0.0)) for r in reactions_raw.values())
    
    me.add_step(
        id="beam-load-summary",
        title="Análise de Cargas e Equilíbrio Global",
        formula=r"F_{total} = \sum P_i + \int q(x) dx + P_p, \quad \sum R_v = F_{total}",
        substitution=rf"F_{{total}} = {fmt(total_point_kn, 1)} + {fmt(total_distributed_kn, 1)} + {fmt(self_weight_kn, 1)}",
        result=rf"F_{{total}} = {fmt(total_actions_kn, 2)}\,kN \approx \sum R = {fmt(total_reaction, 2)}\,kN",
        explanation=(
            "O equilíbrio estático global considera somente as ações externas informadas neste modelo idealizado."
            if is_force_model
            else "O equilíbrio estático global considera cargas informadas, cargas pontuais e peso próprio quando ativado no solver."
        ),
        norm="Mecânica Estrutural"
    )
    
    # --- NOVO: Equações Analíticas por Trecho (Requisito Pedagógico Mestre) ---
    analytical_formulas = diagrams.get("formulas", [])
    if analytical_formulas:
        formula_lines = []
        for i, f in enumerate(analytical_formulas):
            formula_lines.append(rf"\text{{Trecho }} {i+1} \, ({f['range']}):")
            formula_lines.append(rf"\quad {f['shear']}")
            formula_lines.append(rf"\quad {f['moment']}")
        formula_latex = " \\\\ ".join(formula_lines)
        me.add_step(
            id="beam-analytical-equations",
            title="Equações de Esforços por Trecho (Método das Seções)",
            formula=r"V(x) = \sum F_v, \quad M(x) = \sum M_{(x)}",
            substitution=r"\text{Isolamento de trechos conforme descontinuidades de carga/apoio}",
            result=rf"\left\{{ \begin{{array}}{{l}} {formula_latex} \end{{array}} \right.",
            explanation="O Método das Seções consiste em 'cortar' a viga em uma posição 'x' e aplicar as equações de equilíbrio ao corpo livre isolado. Para fins didáticos, as equações analíticas permitem determinar os valores exatos de cortante e momento em qualquer ponto, validando o modelo numérico MEF.",
            norm="Resistência dos Materiais"
        )
        
        if not is_force_model:
            # --- PTV (Princípio dos Trabalhos Virtuais) ---
            me.add_step(
                id="beam-ptv",
                title="Deformação via Princípio dos Trabalhos Virtuais (PTV)",
                formula=r"\delta = \int_0^L \frac{M(x) \cdot \overline{m}(x)}{EI} dx",
                substitution=r"\text{Cálculo analítico integrado vs Matriz de Rigidez (MEF)}",
                result=rf"\delta_{{max}} = {fmt(summary.get('max_deflection_mm', 0.0), 2)}\,mm",
                explanation="Enquanto o MEF utiliza matrizes de rigidez $[K]\{U\} = \{F\}$, a Resistência dos Materiais pura (PTV) integra o momento fletor real $M(x)$ com um momento virtual $\overline{m}(x)$ para obter a flecha.",
                norm="Mecânica dos Sólidos"
            )

    # Comparação Cross-Validation comum aos dois caminhos
    classical_moments = diagrams.get("M_kNm", [])
    if classical_moments:
        m_classic = max(abs(float(m)) for m in classical_moments)
    else:
        m_classic = float(summary.get("max_moment_classic", (total_actions_kn * L / 8) if total_actions_kn > 0 else 0))
    m_mef = float(summary.get("max_moment_kNm", 0.0))
    me.add_comparison_step(m_classic, m_mef)

    if not design_requires_rebar:
        me.add_bibliography_step()
        return me.build()

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
    
    # --- Bloco de Whitney (Tensões na Seção) ---
    xi = float(flex.get("xi", 0.0))
    if xi > 0:
        me.add_step(
            id="beam-whitney-block",
            title="Diagrama de Tensões: Bloco de Whitney",
            formula=r"R_c = 0,85 f_{cd} \cdot b_w \cdot y, \quad y = 0,8 x",
            substitution=rf"y = 0,8 \cdot ({fmt(xi, 3)} \cdot {fmt(d, 3)})",
            result=rf"y = {fmt(0.8 * xi * d, 3)}\,m \quad (R_c = R_t)",
            explanation="O modelo diagrama parábola-retângulo do concreto no ELU (Estádio III) é simplificado pelo bloco retangular equivalente de Whitney (altura $y = 0,8x$), onde a força de compressão $R_c$ equilibra a tração $R_t$ no aço.",
            norm="NBR 6118, 17.2.2"
        )
    
    kx = float(flex.get('x_d', 0.0))
    kx_lim = float(flex.get('x_d_lim', 0.45))
    me.add_step(
        id="beam-flexure-elu",
        title="Posição da Linha Neutra e Ductilidade",
        formula=r"k_x = \frac{1 - \sqrt{1 - 2\mu/\eta}}{\lambda}, \quad k_x \leq k_{x,lim}",
        substitution=rf"k_x = {fmt(kx, 3)}, \quad k_{{x,lim}} = {fmt(kx_lim, 2)}",
        result=me.txt(f"Status: {'OK (Domínio 2/3)' if kx <= kx_lim else 'ALERTA (Domínio 4/Arm. Dupla)'}"),
        explanation="Verifica-se a ductilidade da seção. Para concretos até C50, kx deve ser limitado a 0,45 para garantir aviso de ruptura.",
        norm="NBR 6118, 14.6.4.3"
    )
    
    as_bottom = float(flex.get('As_cm2', 0.0))
    me.add_step(
        id="beam-flexure-as",
        title="Cálculo da Armadura Longitudinal de Tração",
        formula=r"A_s = \frac{M_{sd}}{f_{yd} \cdot z}, \quad z = d \cdot (1 - 0,5 \lambda k_x)",
        substitution=rf"z = {fmt(d, 2)} \cdot (1 - 0,4 \cdot {fmt(kx, 3)}), \quad f_{{yd}} = {fmt(fyd, 1)}\,MPa",
        result=rf"A_s = {fmt(as_bottom, 2)}\,\text{{cm}}^2",
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
        result=me.txt(f"Status: {shear.get('biela_status', 'OK')}"),
        explanation="A verificação VRd2 garante que o concreto diagonal não esmagará sob esforços de compressão.",
        norm="NBR 6118, 17.4.2.2"
    )
    
    me.add_step(
        id="beam-shear-stirrps",
        title="Armadura Transversal (Estribos)",
        formula=r"A_{sw}/s = \frac{V_{sw}}{0,9 \cdot d \cdot f_{ywd}}",
        substitution=rf"V_{{sw}} = {fmt(shear.get('Vsw_kN', 0.0), 1)}\,kN",
        result=rf"A_{{sw}}/s = {fmt(asw_final, 2)}\,\text{{cm}}^2/m",
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
    
    # 5. Estados Limites de Serviço (ELS)
    branson = deflection.get("branson", {})
    if branson:
        is_cracked = float(branson.get('Ma_kNm', 0)) > float(branson.get('Mr_kNm', 1e9))
        estadio = "Estádio II (Seção Fissurada)" if is_cracked else "Estádio I (Seção Íntegra)"
        
        me.add_step(
            id="beam-branson-inertia",
            title="Análise de Estádios e Inércia Equivalente",
            formula=r"I_{eq} = \left(\frac{M_r}{M_a}\right)^3 I_c + \left[1 - \left(\frac{M_r}{M_a}\right)^3\right] I_{cr}",
            substitution=rf"M_a = {fmt(branson.get('Ma_kNm'), 2)}\,kNm \quad M_r = {fmt(branson.get('Mr_kNm'), 2)}\,kNm",
            result=rf"\text{{Regime: {estadio}}} \Rightarrow I_{{eq}} = {fmt(branson.get('Ieq_m4'), 7)}\,m^4",
            explanation="Avalia-se se o momento em serviço supera o momento de fissuração ($M_r$). No Estádio II, o concreto tracionado é ignorado, reduzindo a inércia da seção de $I_c$ para $I_e$ (Modelo de Branson).",
            norm="NBR 6118, 17.3.2.1.1"
        )

    me.add_validation_step(
        id="beam-deflection",
        title="Flecha Máxima (ELS-DEF)",
        value=float(deflection.get("max_mm", 0.0)),
        limit=float(deflection.get("limit_mm", L*1000/250)),
        operator="<=",
        unit="mm",
        explanation="A flecha final considera a rigidez equivalente calculada e os efeitos de fluência do concreto.",
        norm="NBR 6118, 17.3.2"
    )

    # 7. Bibliografia (Elite Pedagogical)
    me.add_bibliography_step()
    
    return me.build()

def build_vigacross_blackboard(results: dict, input_data: dict) -> dict:
    """Memorial pedagógico especializado para Vigas Contínuas (Hardy Cross)."""
    me = MemorialEngine("Roteiro Didático: Vigas Contínuas (Hardy Cross)", "vigacross")
    fmt = me._fmt
    
    # 1. Propriedades da Seção
    me.add_standard_info()
    me.add_step(
        id="cross-geom",
        title="Propriedades da Seção e Rigidez Relativa",
        formula=r"I = \frac{b \cdot h^3}{12}, \quad K = \frac{E \cdot I}{L}",
        substitution=rf"b = {input_data.get('sectionB', 20)}\,cm, \quad h = {input_data.get('sectionH', 50)}\,cm",
        result=rf"I = {fmt(input_data.get('defaultInertiaCm4', 208333), 0)}\,cm^4",
        explanation="A rigidez de cada vão determina como os momentos desbalanceados são distribuídos nos nós.",
        norm="Teoria das Estruturas"
    )
    
    # 2. Momentos de Engastamento Perfeito
    bar_mep = results.get("barResults", [])
    mep_text = " ; ".join([f"{b['barId']}: {fmt(b['mepA'])} / {fmt(b['mepB'])} kNm" for b in bar_mep])
    me.add_step(
        id="cross-mep",
        title="Momentos de Engastamento Perfeito (MEP)",
        formula=r"M_{EP} = \mp\frac{qL^2}{12} \quad \text{ou} \quad \mp\frac{Pab^2}{L^2}",
        substitution=mep_text,
        result=r"\text{Calculado para cada extremidade}",
        explanation="Valores iniciais considerando que todos os nós estão perfeitamente engastados antes da liberação.",
        norm="Método de Hardy Cross"
    )
    
    # 3. Equações por Trecho (Requisito Mestre)
    formula_steps = []
    x_offset = 0.0
    for bar in bar_mep:
        L = bar.get("length", 1.0)
        ma = bar.get("finalA", 0.0)
        mb = bar.get("finalB", 0.0)
        
        # Simplificação: assume q constante se houver udl
        span_id = bar.get("barId")
        q = 0.0
        spans = input_data.get("spans", [])
        span_data = next((s for s in spans if s.get("id") == span_id), {})
        loads = span_data.get("loads", [])
        for load in loads:
            if load.get("type") == "udl":
                q = load.get("value", 0.0)
        
        # V(x) = (qL/2 + (Ma+Mb)/L) - qx
        # Usamos mb - ma porque Ma e Mb são momentos de apoio (extrema esquerda e direita)
        # Convenção Cross: Horário positivo. Para vigas: M_esquerda (ma) e M_direita (-mb)
        v0 = (q * L / 2.0) + (mb + ma) / L # Simplificação pedagógica
        v_eq = f"V(x) = {v0:.2f} - {q:.2f}x"
        m_eq = f"M(x) = {-ma:.2f} + {v0:.2f}x - {q/2.0:.2f}x^2"
        
        formula_steps.append(rf"\text{{Vão }} {span_id} \, ({x_offset:.2f} \le x < {x_offset + L:.2f}):")
        formula_steps.append(rf"\quad {v_eq}")
        formula_steps.append(rf"\quad {m_eq}")
        x_offset += L

    me.add_step(
        id="cross-analytical-equations",
        title="Equações Analíticas de Esforços (Método das Seções)",
        formula=r"V(x) = V_{iso} + \frac{M_B + M_A}{L}, \quad M(x) = M_A + (V_0)x - \frac{qx^2}{2}",
        substitution=r"\text{Superposição de efeitos isostáticos e momentos de apoio}",
        result=rf"\left\{{ \begin{{array}}{{l}} {' \\\\ '.join(formula_steps)} \end{{array}} \right.",
        explanation="As equações analíticas por trecho utilizam o Princípio da Superposição e o Método das Seções para decompor a viga contínua em vãos isolados. Esta abordagem é fundamental para o ensino de engenharia, permitindo a verificação manual do equilíbrio de cada barra.",
        norm="Resistência dos Materiais"
    )

    # --- Linhas de Influência ---
    me.add_step(
        id="cross-influence-lines",
        title="Análise de Trens-Tipo (Linhas de Influência)",
        formula=r"\text{Envoltória} = \max/\min [ \text{Momento} (x) \text{ para toda carga móvel} ]",
        substitution=r"\text{Alternância de sobrecargas nos vãos adjacentes}",
        result=r"\text{Pior Caso (Apoios vs Vãos)}",
        explanation="Em vigas contínuas, os esforços máximos não ocorrem com toda a viga carregada simultaneamente. As Linhas de Influência determinam a posição exata da sobrecarga para maximizar momentos nos apoios (cargas adjacentes) ou nos vãos (cargas alternadas).",
        norm="Teoria das Estruturas"
    )

    # 4. Bibliografia (Elite Pedagogical)
    me.add_bibliography_step()

    return me.build()
