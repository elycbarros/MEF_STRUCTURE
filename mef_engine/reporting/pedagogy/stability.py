from typing import Any
from .base import MemorialEngine
from wind_engine import WindEngine

def build_stability_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    """
    Constrói o quadro negro pedagógico detalhado para o cálculo de vento (NBR 6123).
    """
    me = MemorialEngine("NBR 6123 — Pressão Dinâmica e Força do Vento", "stability")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Velocidade Básica (V0)
    me.add_step(
        id="wind-v0",
        title="1. Velocidade Básica do Vento (V0)",
        formula=r"V_0 = \text{velocidade de rajada (isópletas)}",
        substitution=rf"V_0 = {fmt(res.get('v0'))} \text{{ m/s}}",
        result=rf"V_0 = {fmt(res.get('v0'))} \text{{ m/s}}",
        explanation="Velocidade de rajada de 3 segundos, que é excedida em média uma vez em 50 anos, a 10 metros acima do solo, em campo aberto e plano.",
        norm="NBR 6123, Item 4.1"
    )
    
    # 2. Fator Topográfico (S1)
    me.add_step(
        id="wind-s1",
        title="2. Fator Topográfico (S1)",
        formula=r"S_1 = \text{fator de relevo}",
        substitution=rf"S_1 = {fmt(res.get('s1'))}",
        result=rf"S_1 = {fmt(res.get('s1'))}",
        explanation="Leva em conta as variações do relevo: 1,0 para terrenos planos/ondulados, 0,9 para vales profundos protegidos e 1,1 para encostas/cristas.",
        norm="NBR 6123, Item 5.1"
    )
    
    # 3. Fator de Rugosidade e Dimensões (S2)
    cat = res.get("categoria", 2)
    cls = res.get("classe", "B")
    params = WindEngine.get_s2_parameters(cat, cls)
    b = params['b']
    p = params['p']
    fr = params['fr']
    z_min = params['z_min']
    h_max = res.get("height", 30.0)
    
    me.add_step(
        id="wind-s2",
        title="3. Fator de Rugosidade, Altura e Dimensões (S2)",
        formula=r"S_2(z) = b \cdot F_r \cdot \left(\frac{z}{10}\right)^p",
        substitution=rf"S_2({fmt(h_max)}) = {fmt(b)} \cdot {fmt(fr)} \cdot \left(\frac{{{fmt(h_max)}}}{{10}}\right)^{{{fmt(p)}}} \quad (z_{{min}} = {fmt(z_min)}\text{{m}})",
        result=rf"S_2(H) = {fmt(res.get('s2_max', 1.0))}",
        explanation=f"Define a variação da velocidade com a altura, conforme a Categoria de Rugosidade {cat} e Classe de Dimensão {cls}. Parâmetros adotados da NBR 6123 Tabela 2: b = {fmt(b)}, p = {fmt(p)}, Fr = {fmt(fr)}.",
        norm="NBR 6123, Item 5.2 / Tabela 2"
    )
    
    # 4. Fator Estatístico (S3)
    me.add_step(
        id="wind-s3",
        title="4. Fator Estatístico (S3)",
        formula=r"S_3 = \text{grau de segurança e vida útil}",
        substitution=rf"S_3 = {fmt(res.get('s3'))}",
        result=rf"S_3 = {fmt(res.get('s3'))}",
        explanation="Baseia-se na confiabilidade requerida e vida útil da edificação (varia de 0,83 a 1,10 conforme os Grupos 1 a 5).",
        norm="NBR 6123, Item 5.3 / Tabela 3"
    )
    
    # 5. Velocidade Característica do Vento (Vk)
    vk_max = res.get('summary', {}).get('max_vk', 0.0)
    me.add_step(
        id="wind-vk",
        title="5. Velocidade Característica do Vento (Vk)",
        formula=r"V_k(z) = V_0 \cdot S_1 \cdot S_2(z) \cdot S_3",
        substitution=rf"V_k(H) = {fmt(res.get('v0'))} \cdot {fmt(res.get('s1'))} \cdot {fmt(res.get('s2_max'))} \cdot {fmt(res.get('s3'))}",
        result=rf"V_k(H) = {fmt(vk_max)} \text{{ m/s}}",
        explanation="Velocidade característica de projeto à altura máxima do topo da edificação.",
        norm="NBR 6123, Equação 2"
    )
    
    # 6. Pressão Dinâmica (q_k)
    q_max = res.get('summary', {}).get('max_q_Pa', 0.0)
    me.add_step(
        id="wind-q",
        title="6. Pressão Dinâmica do Vento (q_k)",
        formula=r"q(z) = 0,613 \cdot V_k(z)^2",
        substitution=rf"q(H) = 0,613 \cdot ({fmt(vk_max)})^2",
        result=rf"q_k(H) = {fmt(q_max)} \text{{ Pa}} \approx {fmt(q_max/1000.0, 3)} \text{{ kN/m}}^2",
        explanation="Pressão dinâmica de obstrução (pressão de referência do vento) no topo da torre.",
        norm="NBR 6123, Item 4.2 / Equação 1"
    )
    
    # 7. Força Total e Fator Dinâmico
    cf = res.get('summary', {}).get('cf_used', 1.2)
    g_dyn = res.get('summary', {}).get('g_dynamic', 1.0)
    f_tot = res.get('summary', {}).get('total_force_kN', 0.0)
    me.add_step(
        id="wind-force",
        title="7. Força Horizontal de Arrasto Global",
        formula=r"F_w(z) = q(z) \cdot A_{exp} \cdot C_f \cdot G",
        substitution=rf"F_{{tot}} = \sum [q(z) \cdot A_{{exp}} \cdot {fmt(cf)} \cdot {fmt(g_dyn)}]",
        result=rf"F_{{tot}} = {fmt(f_tot)} \text{{ kN}}",
        explanation="Força horizontal resultante na fachada. CF é o Coeficiente de Arrasto e G é o Fator de Rajada Dinâmica para modelar flutuações rápidas.",
        norm="NBR 6123, Item 6.1"
    )
    
    # 8. Momento de Tombamento na Base
    m_base = res.get('summary', {}).get('base_moment_kNm', 0.0)
    me.add_step(
        id="wind-moment",
        title="8. Momento de Tombamento Global na Base",
        formula=r"M_{base} = \sum [F_w(z) \cdot z]",
        substitution=rf"M_{{base}} = \sum [F_{{w, i}} \cdot z_i]",
        result=rf"M_{{base}} = {fmt(m_base)} \text{{ kNm}}",
        explanation="Momento fletor global acumulado na base da edificação gerado pela ação do vento.",
        norm="NBR 6123"
    )
    
    return me.build()

def build_stability_gammaz_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    """
    Constrói o roteiro pedagógico completo para a verificação de Estabilidade Global (NBR 6118).
    """
    me = MemorialEngine("NBR 6118 — Estabilidade Global (Gamma-Z)", "stability")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Não-Linearidade Física
    me.add_step(
        id="stab-non-linear",
        title="1. Não-Linearidade Física Equivalente (Rigidez Reduzida)",
        formula=r"(EI)_{eff} = 0,8 \cdot E_c I_p \quad (\text{Pilares}), \quad (EI)_{eff} = 0,4 \cdot E_c I_v \quad (\text{Vigas})",
        substitution=r"\text{Rigidez reduzida para simular a fissuração dos elementos de concreto}",
        result=r"\text{Redução NBR 6118 Aplicada}",
        explanation="Para a análise global de segunda ordem simplificada, a NBR 6118 permite reduzir as rigidezes flexionais dos elementos para simular a perda de rigidez pela fissuração e escoamento do concreto.",
        norm="NBR 6118, Item 15.7.3"
    )
    
    # 2. Momento de Primeira Ordem
    m1_kNm = res.get('m1_kNm', res.get('coupling', {}).get('m1_used_kNm', 1000.0))
    me.add_step(
        id="stab-m1",
        title="2. Momento Fletor Total de 1ª Ordem (M1,tot)",
        formula=r"M_{1,tot} = M_{tombamento}",
        substitution=rf"M_{{1,tot}} = {fmt(m1_kNm)} \text{{ kNm}}",
        result=rf"M_{{1,tot}} = {fmt(m1_kNm)} \text{{ kNm}}",
        explanation="Momento fletor global gerado pelas forças horizontais (vento/sismo) calculadas na base da edificação de 1ª ordem.",
        norm="NBR 6118, Item 15.4.2"
    )
    
    # 3. Efeitos de Segunda Ordem (Delta M)
    # delta_m = M_tot - M1_tot
    gamma_z = res.get('gamma_z', 1.0)
    # Se gamma_z estiver disponível, podemos estimar o Delta M
    delta_m = 0.0
    if gamma_z > 1.0 and gamma_z != float('inf'):
        delta_m = m1_kNm * (gamma_z - 1.0)
    
    me.add_step(
        id="stab-m2",
        title="3. Efeitos Incrementais de 2ª Ordem (Delta M)",
        formula=r"\Delta M_{tot} = \sum [P_{vert} \cdot \delta_{1}]",
        substitution=rf"\Delta M_{{tot}} \approx {fmt(delta_m)} \text{{ kNm}}",
        result=rf"\Delta M_{{tot}} = {fmt(delta_m)} \text{{ kNm}}",
        explanation="Momento adicional gerado pelas cargas verticais permanentes e variáveis atuando na estrutura deslocada lateralmente (efeito P-Delta global).",
        norm="NBR 6118, Item 15.4.2"
    )
    
    # 4. Coeficiente Gamma-Z
    me.add_validation_step(
        id="gamma-z-check",
        title="4. Coeficiente Gamma-Z (Estabilidade Global)",
        value=float(gamma_z),
        limit=1.1,
        operator="<=",
        unit="",
        explanation="Se Gamma-Z <= 1.10, a estrutura é classificada como de 'nós fixos' e os efeitos globais de 2ª ordem podem ser desconsiderados. Se Gamma-Z > 1.10, os efeitos de 2ª ordem devem ser explicitamente considerados na análise estrutural ou majorados.",
        norm="NBR 6118, Item 15.4.2"
    )
    
    return me.build()
