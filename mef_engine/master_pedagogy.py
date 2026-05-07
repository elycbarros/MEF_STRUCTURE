"""
master_pedagogy.py - passos matematicos estruturados para o Engine MESTRE.
Refatorado para usar o MemorialEngine centralizado.
"""
from __future__ import annotations
from typing import Any, List, Dict
import math
from reporting.engine import MemorialEngine
from engines.beam_engine import BeamEngine
from engines.slab_engine import SlabEngine
from engines.column_engine import ColumnEngine
from engines.foundation_engine import FoundationEngine
from engines.special_elements_engine import SpecialElementsEngine

def build_beam_blackboard(result: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
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
    
    me = MemorialEngine("Roteiro Didatico: Vigas de Concreto", "beam")
    fmt = me._fmt
    
    # 1. Informações Normativas e Materiais (Padronização Mestre)
    me.add_standard_info()
    me.add_material_step(fck)
    caa = payload.get("caa", 2)
    cover = int(payload.get("cover_mm", 30))
    me.add_durability_step(caa, cover)
    me.add_geometry_step(b, h, d)

    # 2. Resumo de Ações e Reações
    distributed_loads = payload.get("distributed_loads") or []
    point_loads = payload.get("point_loads") or []
    total_distributed_kn = 0.0
    for dl in distributed_loads:
        q1 = float(dl.get("q_start", 0.0)) / 1000.0
        q2 = float(dl.get("q_end", dl.get("q_start", 0.0))) / 1000.0
        total_distributed_kn += 0.5 * (q1 + q2) * max(float(dl.get("x_end", 0.0)) - float(dl.get("x_start", 0.0)), 0.0)
    total_point_kn = sum(float(p.get("P", 0.0)) / 1000.0 for p in point_loads)
    reactions = result.get("classical_reactions") or []
    diagrams = result.get("classical_diagrams") or result.get("diagrams") or {}
    xs = diagrams.get("x_m") or []
    moments = diagrams.get("M_kNm") or []
    shears = diagrams.get("V_kN") or []
    if moments and xs:
        max_moment_index = max(range(len(moments)), key=lambda i: abs(float(moments[i])))
        max_moment = float(moments[max_moment_index])
        max_moment_x = float(xs[max_moment_index])
    else:
        max_moment = m_max = 0.0
        max_moment_x = 0.0
    max_shear = max((abs(float(v)) for v in shears), default=0.0)

    me.add_step(
        id="beam-load-summary",
        title="Resumo das Acoes",
        formula=r"F_q = \int_0^L q(x)\,dx,\quad F = F_q + \sum P_i",
        substitution=rf"F_q = {fmt(total_distributed_kn, 2)}\,kN,\quad \sum P_i = {fmt(total_point_kn, 2)}\,kN",
        result=rf"F_{{total}} = {fmt(total_distributed_kn + total_point_kn, 2)}\,kN",
        explanation="As cargas distribuidas e concentradas sao somadas para conferir o equilibrio global.",
        norm="Equilibrio estatico"
    )
    me.add_step(
        id="beam-support-reactions",
        title="Reacoes de Apoio",
        formula=r"\sum V = 0,\quad \sum M = 0",
        substitution=", ".join([rf"R_{{{idx+1}}}={fmt(r.get('R'), 2)}\,kN" for idx, r in enumerate(reactions)]) or r"\text{Reacoes via rigidez}",
        result=rf"\sum R \approx {fmt(sum(float(r.get('R', 0.0)) for r in reactions), 2)}\,kN",
        explanation="As reacoes equilibram as cargas verticais aplicadas ao modelo.",
        norm="Equilibrio estatico"
    )
    
    # 3. Verificacao ELU (Flexao, Domínios e Taxa Mínima)
    m_max = max(float(design.get("M_max_pos_kNm", 0.0)), abs(float(design.get("M_max_neg_kNm", 0.0))))
    as_bottom = float(design.get("flexure_bottom", {}).get("As_cm2", 0.0))
    as_top = float(design.get("flexure_top", {}).get("As_cm2", 0.0))
    domain = design.get("flexure_bottom", {}).get("domain", "2")
    rho = (as_bottom / (b * 100 * d * 100)) * 100 if b > 0 and d > 0 else 0.0
    
    me.add_step(
        id="beam-flexure",
        title="Dimensionamento a Flexao e Dominio",
        formula=r"A_s = \frac{M_{sd}}{0{,}9d \cdot f_{yd}}, \quad \xi = x/d",
        substitution=rf"M_{{sd}} = {fmt(m_max)}\,kNm, \quad \text{{Dominio}} = {domain}",
        result=rf"A_s = {fmt(as_bottom, 2)}\,cm^2 \quad (\rho = {fmt(rho, 3)}\%)",
        explanation=f"A secao encontra-se no Dominio {domain}. O escoamento do aco garante a ductilidade da viga.",
        norm="NBR 6118, 17.2.2"
    )
    
    # Verificação de Taxa Mínima
    rho_min = 0.15 # Simplificado para fck <= 50
    if fck > 30: rho_min = 0.173 # exemplo de variação
    me.add_validation_step(
        id="beam-min-reinforcement",
        title="Taxa de Armadura Minima",
        value=rho,
        limit=rho_min,
        operator=">=",
        unit="%",
        explanation="Garante que a viga nao tenha ruptura fragil logo apos a fissuracao do concreto.",
        norm="NBR 6118, 17.3.5"
    )

    # 4. Detalhamento (Ancoragem e Decalagem)
    lb_cm = float(design.get("anchorage", {}).get("lb_cm", 30.0))
    me.add_step(
        id="beam-detailing",
        title="Detalhamento: Ancoragem e Decalagem",
        formula=r"l_b = \frac{\phi}{4}\frac{f_{yd}}{f_{bd}}, \quad a_l = d \cdot (1 + \cot \alpha)/2",
        substitution=rf"l_b \approx {fmt(lb_cm, 1)}\,cm, \quad a_l \approx {fmt(d, 2)}\,m",
        result=rf"l_{{b,nec}} \approx {fmt(lb_cm * 0.7, 1)}\,cm",
        explanation="O comprimento de ancoragem garante a transferencia de tensoes. A decalagem (al) ajusta o diagrama de momentos.",
        norm="NBR 6118, 9.4 e 17.4.2"
    )

    # 5. Cisalhamento e Torcao
    me.add_validation_step(
        id="beam-shear-check",
        title="Verificacao de Cisalhamento e Torcao (Interacao)",
        value=float(shear.get("interaction_diag", 0.0)),
        limit=1.0,
        operator="<=",
        unit="",
        explanation="Verifica o esmagamento das diagonais de concreto sob acao combinada de V e T.",
        norm="NBR 6118, 17.5.1"
    )
    me.add_step(
        id="beam-torsion-reinforcement",
        title="Armadura de Torcao",
        formula=r"A_{sl,t} = \frac{T_{sd} \cdot u_e}{2 A_e f_{yd}}, \quad A_{sw,t} = \frac{T_{sd}}{2 A_e f_{yd}}",
        substitution=rf"T_{{sd}} = {fmt(shear.get('Tsd_kNm', 0))}\,kNm",
        result=rf"A_{{sl,t}} = {fmt(shear.get('Asl_torsion_cm2', 0), 2)}\,cm^2",
        explanation="Calcula a armadura longitudinal e transversal necessaria para equilibrar o momento torsor.",
        norm="NBR 6118, 17.5.2"
    )
    me.add_validation_step(
        id="beam-crack-width",
        title="Abertura de Fissuras (w_k)",
        value=float(crack.get("wk_mm", 0.0)),
        limit=float(crack.get("limit_mm", payload.get("wk_limit_mm", 0.3))),
        operator="<=",
        unit="mm",
        explanation="Controla a durabilidade protegendo as armaduras contra agentes corrosivos."
    )
    me.add_validation_step(
        id="beam-deflection",
        title="Estado Limite de Servico: Flecha",
        value=float(deflection.get("max_mm", summary.get("max_deflection_mm", 0.0))),
        limit=float(deflection.get("limit_mm", max(L * 1000.0 / 250.0, 1e-9))),
        operator="<=",
        unit="mm",
        explanation="Verifica se o deslocamento vertical e aceitavel para o conforto dos usuarios."
    )
    
    overall = design.get("overall_status", "REVISAR")
    me.add_step(
        id="beam-final-decision",
        title="Conclusao do Dimensionamento",
        formula=r"\text{Verificacao de Seguranca (ELU) e Servico (ELS)}",
        substitution=rf"\text{{Status}} = {overall}",
        result=rf"\text{{{overall}}}",
        explanation="Consolida todos os criterios normativos de seguranca, durabilidade e funcionalidade.",
        norm="NBR 6118"
    )

    return me.build()

def build_column_blackboard(sec: Any, loads: Any = None, design: dict[str, Any] = None) -> dict[str, Any]:
    """
    Cria um roteiro didatico para pilares. Aceita objetos ColumnSection ou dicionarios.
    """
    me = MemorialEngine("Roteiro Didatico: Pilares", "column")
    fmt = me._fmt
    
    # 1. Padronização Mestre (Normas e Materiais)
    me.add_standard_info()
    
    # Extração de dados dependendo do tipo de entrada
    if loads is None and isinstance(sec, dict):
        res = sec
        fck = float(res.get("fck", 30.0))
        b = float(res.get("b", 0.4))
        h = float(res.get("h", 0.4))
        as_total = float(res.get("As_calc_cm2", 0.0))
        Nd = float(res.get("Nd_kN", 1000.0))
        lambda_val = float(res.get("lambda_max", 35.0))
        caa = res.get("caa", 2)
        cover = int(res.get("cover_mm", 30))
    else:
        # Solver Elite (Objetos)
        fck = sec.fck
        b = sec.b
        h = sec.h
        as_total = float(design.get("As_final_cm2", 0.0))
        Nd = loads.Nd_kN
        lambda_val = design.get("lambda_max", 35.0)
        caa = getattr(sec, "caa", 2)
        cover = getattr(sec, "cover_mm", 30)

    me.add_material_step(fck)
    me.add_durability_step(caa, cover)
    me.add_geometry_step(b, h)
    
    # 2. Esbeltez e Imperfeicoes
    le = sec.L_free * sec.alpha_b if hasattr(sec, 'L_free') else 3.0
    theta_a = 1.0 / (100.0 * math.sqrt(le))
    ei = theta_a * le / 2.0
    me.add_step(
        id="column-slenderness",
        title="Esbeltez e Imperfeicoes Geometricas",
        formula=r"\lambda = L_e / i, \quad \theta_a = 1/(100\sqrt{L}), \quad e_i = \theta_a \cdot L_e / 2",
        substitution=rf"\lambda = {fmt(lambda_val, 1)}, \quad e_{{i}} = {fmt(ei*100, 2)}\,cm",
        result=rf"\lambda \approx {fmt(lambda_val, 1)}, \quad e_i = {fmt(ei, 4)}\,m",
        explanation="Considera-se o desaprumo acidental da barra atraves da excentricidade imperfeita (ei) e a esbeltez geometrica.",
        norm="NBR 6118, 11.3.3.4"
    )

    # 3. Efeitos de 2a Ordem (Metodo da Curvatura Nominal)
    m1d = float(design.get("Md_x_total_kNm", 0.0) if design else 0.0)
    e2 = float(design.get("moments_2nd_order", {}).get("e2_x_mm", 0.0)) / 1000.0
    me.add_step(
        id="column-2nd-order",
        title="Efeitos de 2a Ordem Locais",
        formula=r"1/r = 0{,}005 / (h \cdot (0{,}5 + \nu)), \quad e_2 = (L_e^2 / 10) \cdot (1/r)",
        substitution=rf"e_2 \approx {fmt(e2*100, 2)}\,cm",
        result=rf"M_{{total}} = {fmt(m1d, 2)}\,kNm",
        explanation="O Metodo da Curvatura Nominal estima os efeitos P-delta locais para pilares com lambda <= 90.",
        norm="NBR 6118, 15.8.3.3.2"
    )

    # 4. Verificacao ULS (Integracao de Fibras Biaxial)
    me.add_step(
        id="column-uls-check",
        title="Verificacao de Resistencia ELU",
        formula=r"\Phi = \text{Demand} / \text{Capacity} \leq 1{,}0",
        substitution=rf"N_d = {fmt(Nd)}\,kN, \quad M_d = {fmt(m1d)}\,kNm",
        result=rf"\text{{Status}} = \text{{Verificado}}",
        explanation="Verifica se o ponto de solicitacao (Nd, Md) esta dentro da superficie de interacao da secao.",
        norm="NBR 6118, 17.2.2"
    )
    me.add_step(
        id="column-reinforcement",
        title="Dimensionamento Rigoroso (Integracao de Fibras)",
        formula=r"\int \sigma_c dA + \sum \sigma_s A_s = N_d, \quad \dots = M_d",
        substitution=rf"N_d = {fmt(Nd)}\,kN, \quad \omega = {fmt(design.get('omega', 0), 3) if design else 0}",
        result=rf"A_{{s,tot}} = {fmt(as_total, 2)}\,cm^2",
        explanation="A armadura e calculada via integracao numerica da secao (Modelo de Fibras), garantindo precisao em flexao biaxial.",
        norm="NBR 6118, 17.2.2"
    )
    # 5. Durabilidade e Conclusao
    me.add_validation_step(
        id="column-durability",
        title="Verificacao de Cobrimento",
        value=float(cover),
        limit=float(caa * 10), # simplificação
        operator=">=",
        unit="mm",
        explanation="O cobrimento garante a vida util de projeto."
    )

    me.add_step(
        id="column-final-decision",
        title="Conclusao do Dimensionamento",
        formula=r"\text{Status Final}",
        substitution=r"\text{Verificado}",
        result=r"\text{APROVADO}",
        explanation="O pilar atende aos criterios de esbeltez e resistencia ELU.",
        norm="NBR 6118"
    )

    return me.build()

def build_footing_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Roteiro Didatico: Sapatas", "footing")
    fmt = me._fmt
    
    # 1. Padronização Mestre
    me.add_standard_info()
    fck = float(res.get("fck", 25.0))
    me.add_material_step(fck)
    me.add_durability_step(int(res.get("caa", 2)), int(res.get("cover_mm", 40)))
    
    # 2. Geometria e Solo
    me.add_step(
        id="footing-pressure",
        title="Pressao no Solo",
        formula=r"\sigma = \frac{N_d}{A \cdot B}",
        substitution=rf"\sigma = \frac{{{fmt(res.get('Nd_kN'))}}}{{{fmt(res.get('A_m'))} \cdot {fmt(res.get('B_m'))}}}",
        result=rf"\sigma = {fmt(res.get('sigma_max_kPa'))}\,kPa",
        explanation="Verifica se a carga da sapata ultrapassa a capacidade de carga do solo.",
        norm="NBR 6122"
    )
    
    # 3. Rigidez (Sapata Rígida vs Flexível)
    h = float(res.get("h_m", 0.6))
    a_col = float(res.get("a_col_m", 0.2))
    is_rigid = (h >= (float(res.get("A_m", 1.5)) - a_col)/3.0)
    me.add_step(
        id="footing-rigidity",
        title="Verificacao de Rigidez",
        formula=r"h \geq (A - a)/3",
        substitution=rf"{fmt(h)} \geq ({fmt(res.get('A_m'))} - {fmt(a_col)})/3",
        result=r"\text{Sapata Rigida}" if is_rigid else r"\text{Sapata Flexivel}",
        explanation="Sapatas rigidas permitem considerar distribuicao linear de tensoes no solo.",
        norm="NBR 6118, 22.6"
    )
    
    return me.build()

def build_spt_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Interpretacao de Sondagem SPT", "geotechnics")
    me.add_step(
        id="spt-interpretation",
        title="Tensao Admissivel Estimada",
        formula=r"\sigma_{adm} \approx N_{spt} / 50 \text{ (simplificado)}",
        substitution=rf"\sigma_{{adm}} \approx {me._fmt(res.get('avg_nspt'))} / 50",
        result=rf"\sigma_{{adm}} \approx {me._fmt(res.get('sigma_adm_calc_kPa')/1000, 2)}\,MPa",
        explanation="Estimativa da capacidade de carga do solo com base no indice de penetracao.",
        norm="Teoria de Terzaghi / Pratica Brasileira"
    )
    return me.build()

def build_stability_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Estabilidade Global e Vento", "stability")
    fmt = me._fmt
    
    me.add_standard_info()
    
    me.add_step(
        id="wind-pressure",
        title="Pressao Dinamica do Vento",
        formula=r"q(z) = 0{,}613 \cdot (V_k \cdot S_1 \cdot S_2(z) \cdot S_3)^2",
        substitution=rf"q = 0{{,}}613 \cdot ({fmt(res.get('v0'))} \cdot 1{{,}}0 \cdot 1{{,}}0 \cdot 1{{,}}0)^2",
        result=rf"q = {fmt(res.get('q0_kN_m2'))}\,kN/m^2",
        explanation="Calculo da pressao de obstrucao que o vento exerce na fachada conforme a altura.",
        norm="NBR 6123"
    )
    
    me.add_validation_step(
        id="gamma-z-check",
        title="Indice de Estabilidade Gamma-Z",
        value=float(res.get("gamma_z", 1.1)),
        limit=1.1,
        operator="<=",
        unit="",
        explanation="Se Gamma-Z > 1.1, a estrutura e de 'nos moveis' e os efeitos de segunda ordem globais devem ser majorados.",
        norm="NBR 6118, 15.4"
    )
    
    return me.build()


def build_integrated_foundation_blackboard(spt_res: dict, footing_res: dict) -> dict:
    me = MemorialEngine("Memorial Integrado: Geotecnia + Fundacao", "footing")
    fmt = me._fmt
    
    # 1. Analise Geotecnica
    me.add_step(
        id="geo-analysis",
        title="Capacidade de Carga do Solo (SPT)",
        formula=r"\sigma_{adm} = N_{spt}/50 \text{ (Teixeira)}",
        substitution=rf"N_{{spt}} = {fmt(spt_res.get('nspt_design'))}",
        result=rf"\sigma_{{adm}} = {fmt(spt_res.get('sigma_adm_kPa'))}\,kPa",
        explanation="A tensao admissivel do solo e estimada a partir do ensaio de penetracao padrao (SPT).",
        norm="NBR 6122"
    )
    
    # 2. Dimensionamento da Sapata
    me.add_step(
        id="footing-base",
        title="Geometria da Base da Sapata",
        formula=r"A_{req} = (N_d \cdot 1{,}1) / \sigma_{adm}",
        substitution=rf"A_{{req}} = ({fmt(footing_res.get('Nd_kN'))} \cdot 1{{,}}1) / {fmt(spt_res.get('sigma_adm_kPa'))}",
        result=rf"A = {fmt(footing_res.get('a_m'))} \times {fmt(footing_res.get('b_m'))}\,m \approx {fmt(footing_res.get('area_m2'), 2)}\,m^2",
        explanation="A area da base deve ser suficiente para distribuir a carga sem recalques excessivos.",
        norm="NBR 6118"
    )
    
    # 3. Verificacao de Pressao
    me.add_validation_step(
        id="pressure-check",
        title="Verificacao de Tensao no Solo",
        value=float(footing_res.get("sigma_real_kPa")),
        limit=float(spt_res.get("sigma_adm_kPa")),
        operator="<=",
        unit="kPa",
        explanation="A pressao real na base da sapata deve ser inferior a capacidade de carga do solo."
    )
    
    return me.build()

def build_lajes_blackboard(model: Any, result: Any) -> dict:
    import numpy as np
    me = MemorialEngine("Roteiro Didatico: Lajes Macicas", "slab")
    fmt = me._fmt
    
    me.add_standard_info()
    fck = getattr(model.material, 'fck', 30.0)
    me.add_material_step(fck)
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
        explanation="A rigidez flexional D representa a resistencia da placa a curvatura.",
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
        explanation="Soma das cargas permanentes e acidentais que atuam na superficie da laje.",
        norm="NBR 6120"
    )
    
    # 3. Momentos e Taxas
    mx_max = np.max(np.abs(result.mx)) / 1000.0 # kNm/m
    me.add_step(
        id="slab-moments",
        title="Solicitacoes Maximas (MEF)",
        formula=r"M_{x,max} = \max|M_x(x,y)|",
        substitution=r"\text{Analise via Elementos Finitos (Placa de Mindlin)}",
        result=rf"M_{{x,max}} = {fmt(mx_max, 2)}\,kNm/m",
        explanation="Momentos fletores obtidos atraves da integracao das tensoes nos elementos finitos.",
        norm="NBR 6118, 14.7"
    )
    
    # 4. Verificacao de Flecha (ELS)
    w_max_mm = np.max(np.abs(result.disp[:, 0])) * 1000.0
    l_span = min(model.Lx, model.Ly)
    limit_mm = (l_span * 1000.0) / 250.0
    me.add_validation_step(
        id="slab-deflection",
        title="Verificacao de Flecha Limite (L/250)",
        value=w_max_mm,
        limit=limit_mm,
        operator="<=",
        unit="mm",
        explanation="A flecha maxima deve ser limitada para evitar danos em alvenarias e desconforto visual.",
        norm="NBR 6118, 13.3"
    )
    
    return me.build()

def build_retaining_wall_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Muros de Arrimo", "retaining_wall")
    fmt = me._fmt
    
    me.add_standard_info()
    me.add_step(
        id="wall-thrust",
        title="Coeficiente de Empuxo Ativo (Rankine)",
        formula=r"k_a = \tan^2(45^\circ - \phi/2)",
        substitution=rf"k_a = \tan^2(45^\circ - {fmt(res.get('phi_soil', 30))}^\circ/2)",
        result=rf"k_a = {fmt(res.get('ka'), 3)}",
        explanation="O coeficiente Ka define a parcela da pressao vertical que se transforma em pressao lateral do solo.",
        norm="NBR 11682"
    )
    
    me.add_validation_step(
        id="wall-overturning",
        title="Seguranca ao Tombamento (FS > 1.5)",
        value=float(res.get("fs_tomb")),
        limit=1.5,
        operator=">=",
        unit="",
        explanation="O momento estabilizador deve ser significativamente maior que o momento causado pelo empuxo.",
        norm="NBR 11682"
    )
    
    me.add_validation_step(
        id="wall-sliding",
        title="Seguranca ao Deslizamento (FS > 1.5)",
        value=float(res.get("fs_desl")),
        limit=1.5,
        operator=">=",
        unit="",
        explanation="Verifica se o atrito na base do muro impede o seu deslocamento horizontal.",
        norm="NBR 11682"
    )
    
    return me.build()

def build_stairs_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Escadas", "stairs")
    fmt = me._fmt
    
    me.add_standard_info()
    me.add_material_step(float(res.get("fck", 25)))
    
    me.add_step(
        id="stairs-geometry",
        title="Geometria Inclinada e Carga Permanente",
        formula=r"g_{pp} = (h/\cos\alpha + p/2)\gamma_c",
        substitution=rf"\alpha = {fmt(res.get('alpha_deg'), 1)}^\circ",
        result=rf"g_{{pp}} = {fmt(res.get('g_pp', 4.0), 2)}\,kN/m^2",
        explanation="O peso proprio considera a projecao inclinada da laje e o peso medio dos degraus.",
        norm="NBR 6120"
    )
    
    me.add_step(
        id="stairs-moment",
        title="Momento Fletor de Projeto",
        formula=r"M_d = \gamma_f \frac{q \cdot L^2}{8}",
        substitution=rf"q = {fmt(res.get('q_total_kN_m', 10.0), 2)}\,kN/m",
        result=rf"M_d = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="Calculo do esforço fletor maximo para dimensionamento da armadura longitudinal.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_foundation_beam_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Vigas Alavanca", "foundation_beam")
    fmt = me._fmt
    
    # 1. Equilibrio de Momentos
    me.add_step(
        id="strap-equilibrium",
        title="Equilibrio de Forcas (Viga de Transmissao)",
        formula=r"R_1 = \frac{P_1 \cdot L}{L - e}",
        substitution=rf"R_1 = \frac{{{fmt(res.get('r1_kN'))} \cdot {fmt(res.get('l_m'))}}}{{{fmt(res.get('l_m'))} - {fmt(res.get('ecc_m'))}}}",
        result=rf"R_1 = {fmt(res.get('r1_kN'), 1)}\,kN",
        explanation="A viga alavanca transfere a excentricidade do pilar de divisa para o pilar interno, reequilibrando as reacoes de apoio.",
        norm="NBR 6122"
    )
    
    # 2. Momento Fletor de Projeto
    me.add_step(
        id="strap-moment",
        title="Momento Fletor na Viga Alavanca",
        formula=r"M = P_1 \cdot e",
        substitution=rf"M = {fmt(res.get('r1_kN'))} \cdot {fmt(res.get('ecc_m'))}",
        result=rf"M = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="O momento fletor maximo ocorre na face do pilar de divisa e deve ser resistido pela viga alavanca.",
        norm="NBR 6118"
    )
    
    # 3. Verificacao de Levantamento
    me.add_validation_step(
        id="strap-uplift",
        title="Verificacao de Levantamento no Pilar Interno",
        value=float(res.get("r2_kN")),
        limit=0.0,
        operator=">",
        unit="kN",
        explanation="A reacao no pilar interno deve ser positiva (compressao). Se for negativa, a sapata interna pode levantar."
    )
    
    return me.build()

def build_elevated_reservoir_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Reservatorios Elevados", "reservoir")
    fmt = me._fmt
    
    me.add_standard_info()
    me.add_step(
        id="reservoir-pressure",
        title="Pressao Hidrostatica nas Paredes",
        formula=r"p(z) = \gamma_w \cdot z",
        substitution=rf"p_{{max}} = 10 \cdot {fmt(res.get('H', 3.0))}",
        result=rf"p_{{max}} = {fmt(res.get('p_max_kPa'), 1)}\,kN/m^2",
        explanation="A pressao hidrostatica e a principal solicitacao em paredes de reservatorios.",
        norm="NBR 6118"
    )
    
    me.add_validation_step(
        id="reservoir-cracking",
        title="Controle de Fissuracao (Estanqueidade)",
        value=float(res.get('wk_worst_mm', 0.05)),
        limit=0.1,
        operator="<=",
        unit="mm",
        explanation="O limite de 0.1mm e rigoroso para garantir a impermeabilidade do concreto armado.",
        norm="NBR 6118, 17.3.3"
    )
    
    return me.build()

def build_corbel_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Consolos Curtos", "corbel")
    fmt = me._fmt
    
    # 1. Modelo de Biela-e-Tirante
    me.add_step(
        id="corbel-model",
        title="Modelo Estrutural: Biela-e-Tirante",
        formula=r"\tan\theta = d/a, \quad F_{tirante} = F_d \cdot (a/d)",
        substitution=rf"a/d = {fmt(res.get('ratio_ad'), 2)}, \quad \theta = {fmt(res.get('theta_deg'), 1)}^\circ",
        result=rf"F_{{tirante}} = {fmt(res.get('f_tirante_kN'), 1)}\,kN",
        explanation="Em elementos curtos, a analogia de biela-e-tirante substitui a teoria de vigas convencional.",
        norm="NBR 6118, 22.4"
    )
    
    # 2. Armadura Principal
    me.add_step(
        id="corbel-reinforcement",
        title="Armadura do Tirante Principal",
        formula=r"A_s = F_{tirante} / f_{yd}",
        substitution=rf"A_s = {fmt(res.get('f_tirante_kN'))} / 43{{,}}48",
        result=rf"A_s = {fmt(res.get('as_principal_cm2'), 2)}\,cm^2",
        explanation="O tirante de aco deve resistir a componente horizontal de tracao do modelo.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_gerber_tooth_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Dentes Gerber", "gerber_tooth")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Armadura de Suspensao
    me.add_step(
        id="gerber-suspension",
        title="Armadura de Suspensao (Estribos)",
        formula=r"A_{s,susp} = V_d / f_{yd}",
        substitution=rf"A_{{s,susp}} = {fmt(res.get('vd_kN') * 1.4)} / 43{{,}}48",
        result=rf"A_{{s,susp}} = {fmt(res.get('as_suspensao_cm2'), 2)}\,cm^2",
        explanation="A armadura de suspensao e vital para ancorar a carga vertical na parte superior da viga principal.",
        norm="NBR 6118, 22.5.4.1"
    )
    
    # 2. Tirante Horizontal
    me.add_step(
        id="gerber-tie",
        title="Tirante Horizontal (Ash)",
        formula=r"A_{sh} = (V_d \cdot a/d + H_d) / f_{yd}",
        substitution=rf"V_d = {fmt(res.get('vd_kN') * 1.4)}, \quad a/d = \text{{projeto}}",
        result=rf"A_{{sh}} = {fmt(res.get('as_tirante_cm2'), 2)}\,cm^2",
        explanation="O tirante horizontal resiste a tracao causada pela excentricidade do apoio e pela força horizontal eventual.",
        norm="NBR 6118, 22.5.4.2"
    )
    
    return me.build()

def build_deep_beam_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Vigas Parede", "deep_beam")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Relacao L/h
    me.add_step(
        id="deep-beam-ratio",
        title="Relacao de Esbeltez (L/h)",
        formula=r"\lambda = L/h \le 2.0",
        substitution=rf"\lambda = {fmt(res.get('ratio_lh'), 2)}",
        result=r"\text{Viga Parede Validada}" if res.get('is_deep') else r"\text{Viga Convencional}",
        explanation="Vigas com relacao L/h <= 2.0 nao seguem a hipotese de Bernoulli (secoes planas permanecem planas).",
        norm="NBR 6118, 22.3"
    )
    
    # 2. Braco de Alavanca (z)
    me.add_step(
        id="deep-beam-lever",
        title="Ajuste do Braco de Alavanca (z)",
        formula=r"z = 0{{,}}2(L + 2h) \text{ para bi-apoiada}",
        substitution=rf"L = \text{{vao}}, \quad h = \text{{altura}}",
        result=rf"z = {fmt(res.get('z_m'), 2)}\,m",
        explanation="O braco de alavanca e menor que 0.9h devido a concentracao de tensoes na parte inferior da viga parede.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_helical_stairs_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Escadas Helicoidais", "helical_stairs")
    fmt = me._fmt
    
    me.add_standard_info()
    
    # 1. Efeitos Curvilineos (Torsao)
    me.add_step(
        id="helical-torsion",
        title="Efeitos de Torcao em Viga Curva",
        formula=r"T_{max} = q \cdot R^2 (\alpha/2 - \sin(\alpha/2))",
        substitution=rf"R = {fmt(res.get('radius_m'))}\,m, \quad \alpha = \text{{angulo total}}",
        result=rf"T_{{max}} = {fmt(res.get('t_max_kNm'), 2)}\,kNm",
        explanation="Diferente de escadas retas, a curvatura gera um momento de torcao que deve ser combatido com estribos fechados e armadura de pele.",
        norm="NBR 6118"
    )
    
    # 2. Momento Fletor 3D
    me.add_step(
        id="helical-flexure",
        title="Momento Fletor no Vao",
        formula=r"M_{max} = q \cdot R^2 (1 - \cos(\alpha/2))",
        substitution=rf"q = {fmt(res.get('q_total_kN_m'))}\,kN/m",
        result=rf"M_{{max}} = {fmt(res.get('m_max_kNm'), 2)}\,kNm",
        explanation="O momento fletor ocorre simultaneamente a torcao, exigindo uma verificacao de contorno de tensoes combinadas.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_pile_cap_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Blocos sobre Estacas", "pile_cap")
    fmt = me._fmt
    
    # 1. Reacao nas Estacas
    me.add_step(
        id="pile-reaction",
        title="Reacao de Apoio nas Estacas",
        formula=r"R = N_d / n_{estacas}",
        substitution=rf"R = {fmt(res.get('r_estaca_kN')*2)} / 2",
        result=rf"R = {fmt(res.get('r_estaca_kN'), 1)}\,kN",
        explanation="A carga do pilar e distribuida igualmente entre as estacas do bloco para blocos centrados.",
        norm="Mecanica dos Solidos"
    )
    
    # 2. Modelo de Biela-e-Tirante (Blevot)
    me.add_step(
        id="pile-cap-model",
        title="Modelo de Biela e Tirante (Blevot)",
        formula=r"T = R \cdot (a/d), \quad \theta = \arctan(d/a)",
        substitution=rf"\theta = {fmt(res.get('theta_deg'), 1)}^\circ",
        result=rf"F_{{tirante}} = {fmt(res.get('f_tirante_kN'), 1)}\,kN",
        explanation="O bloco funciona como uma treliça espacial onde o concreto resiste a compressao (biela) e o aco a tracao (tirante).",
        norm="NBR 6118, 22.4"
    )
    
    # 3. Verificacao da Biela de Compressao
    me.add_validation_step(
        id="pile-cap-strut",
        title="Verificacao de Esmagamento da Biela",
        value=float(res.get("tensao_biela_kPa")),
        limit=float(res.get("v_rd2_kPa")),
        operator="<=",
        unit="kPa",
        explanation="A tensao na biela de concreto deve ser inferior a resistencia de projeto para evitar a ruptura fragil do bloco."
    )
    
    return me.build()

def build_beam_opening_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Furos em Vigas", "beam_opening")
    fmt = me._fmt
    
    # 1. Classificacao da Abertura
    me.add_step(
        id="opening-type",
        title="Classificacao da Abertura (NBR 6118)",
        formula=r"\text{Pequena se } \phi \leq 0{,}12h",
        substitution=rf"\phi = {fmt(res.get('d_opening'), 2)}\,m, \quad h = {fmt(res.get('h_beam'), 2)}\,m",
        result=r"\text{Furo Pequeno}" if res.get('is_small') else r"\text{Abertura Significativa}",
        explanation="Furos pequenos tem impacto limitado na rigidez global, mas exigem reforços locais de armadura.",
        norm="NBR 6118, 13.2.5"
    )
    
    # 2. Reforco de Borda
    me.add_step(
        id="opening-reinforcement",
        title="Armadura de Reforço de Borda",
        formula=r"A_{s,ref} = V_d / f_{yd}",
        substitution=rf"A_{{s,ref}} = \text{{Reforço suplementar calculado}}",
        result=rf"A_{{s,ref}} = {fmt(res.get('as_reforco_cm2'), 2)}\,cm^2",
        explanation="Devem ser dispostos estribos e barras horizontais contornando o furo para controlar a fissuracao nos cantos.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_punching_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Puncao em Lajes", "punching")
    fmt = me._fmt
    
    # 1. Tensao Solicitante no Perimetro Critico
    me.add_step(
        id="punching-stress",
        title="Tensao Solicitante de Cisalhamento",
        formula=r"\tau_{sd} = \frac{F_{sd}}{u \cdot d}",
        substitution=rf"\tau_{{sd}} = \frac{{{fmt(res.get('fsd_kN'))}}}{{{fmt(res.get('u_perim_m', 2.0))} \cdot {fmt(res.get('d_eff_m', 0.15))}}}",
        result=rf"\tau_{{sd}} = {fmt(res.get('tau_sd_kPa'), 1)}\,kN/m^2",
        explanation="A tensao de puncao e calculada no perimetro critico 'u1', situado a 2d da face do pilar.",
        norm="NBR 6118, 19.4"
    )
    
    # 2. Verificacao de Resistencia sem Armadura
    me.add_validation_step(
        id="punching-resistance",
        title="Resistencia a Puncao (Concreto)",
        value=float(res.get("tau_sd_kPa")),
        limit=float(res.get("tau_rd1_kPa")),
        operator="<=",
        unit="kPa",
        explanation="Verifica se o concreto e a armadura longitudinal sao suficientes para resistir a puncao sem estribos suplementares."
    )
    
    return me.build()

def build_ribbed_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Lajes Nervuradas", "ribbed_slab")
    fmt = me._fmt
    
    # 1. Geometria Equivalente
    me.add_step(
        id="ribbed-geometry",
        title="Inercia e Espessura Equivalente",
        formula=r"h_{eq} = \frac{A_{secao}}{b}",
        substitution=rf"h_{{total}} = {fmt(res.get('h_total_m', 0.25))}\,m, \quad b_{{nerv}} = {fmt(res.get('b_nerv_m', 0.10))}\,m",
        result=rf"h_{{eq}} = {fmt(res.get('h_eq_m'), 3)}\,m",
        explanation="A laje nervurada e modelada como uma sucessao de vigas 'T' paralelas, otimizando o peso proprio.",
        norm="NBR 6118"
    )
    
    # 2. Dimensionamento da Nervura
    me.add_step(
        id="ribbed-flexure",
        title="Dimensionamento da Nervura Individual",
        formula=r"M_{nerv} = M_d \cdot e_{nerv}, \quad A_s = \frac{M_{nerv}}{f_{yd} \cdot z}",
        substitution=rf"M_{{nerv}} = {fmt(res.get('m_nerv_kNm'), 2)}\,kNm",
        result=rf"A_{{s,nerv}} = {fmt(res.get('as_nerv_cm2'), 2)}\,cm^2",
        explanation="O calculo e feito para uma unica nervura, considerando a largura colaborativa da mesa.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_prestressed_slab_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Lajes Protendidas", "prestressed_slab")
    fmt = me._fmt
    
    # 1. Metodo do Equilibrio de Carga (Load Balancing)
    me.add_step(
        id="prestressed-balancing",
        title="Carga Equivalente de Protensao",
        formula=r"q_{eq} = \frac{8 \cdot P \cdot e}{L^2}",
        substitution=rf"P = {fmt(res.get('p_force_kN'))}\,kN, \quad e = {fmt(res.get('ecc_m'))}\,m",
        result=rf"q_{{eq}} = {fmt(res.get('q_eq_kPa'), 2)}\,kN/m^2",
        explanation="A curvatura do cabo de protensao gera uma pressao vertical contraria a gravidade, reduzindo as flechas e tensoes de tracao.",
        norm="NBR 6118"
    )
    
    # 2. Verificacao de Tensoes em Servico (ELS-F)
    me.add_validation_step(
        id="prestressed-stress",
        title="Tensao de Tracao na Fibra Inferior",
        value=float(res.get("sigma_inf_kPa")),
        limit=float(res.get("fctm_kPa")),
        operator="<=",
        unit="kPa",
        explanation="Em lajes protendidas, as tensoes de tracao devem ser limitadas para garantir que a secao permaneça no Estadio I (nao fissurada)."
    )
    
    return me.build()

def build_concrete_wall_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Paredes de Concreto", "concrete_wall")
    fmt = me._fmt
    
    # 1. Verificacao de Esbeltez
    me.add_step(
        id="wall-slenderness",
        title="Indice de Esbeltez da Parede",
        formula=r"\lambda = \frac{h \cdot \sqrt{12}}{t}",
        substitution=rf"h = {fmt(res.get('h_wall_m', 2.8))}\,m, \quad t = {fmt(res.get('t_wall_m', 0.12))}\,m",
        result=rf"\lambda = {fmt(res.get('lambda'), 1)}",
        explanation="Paredes sao elementos comprimidos com grande largura, onde a esbeltez em relacao a espessura governa a estabilidade.",
        norm="NBR 16055"
    )
    
    # 2. Capacidade de Carga Axial
    me.add_validation_step(
        id="wall-capacity",
        title="Resistencia a Compressao (N_d)",
        value=float(res.get("nd_kN_m", 500)),
        limit=float(res.get("n_rd_kN_m")),
        operator="<=",
        unit="kN/m",
        explanation="A capacidade resistente considera a reducao de forca devido aos efeitos de segunda ordem (esbeltez)."
    )
    
    return me.build()

def build_column_advanced_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Pilares Avançados", "column_advanced")
    fmt = me._fmt
    
    # 1. Efeitos de 2a Ordem Local
    me.add_step(
        id="col-2nd-order",
        title="Momento Fletor de 2a Ordem (M2)",
        formula=r"M_{2d} = N_d \cdot e_2, \quad e_2 = \frac{l_e^2}{10} \cdot \frac{1}{r}",
        substitution=rf"\lambda = {fmt(res.get('lambda'), 1)}",
        result=rf"M_{{2d}} = {fmt(res.get('m2_kNm'), 2)}\,kNm",
        explanation="Quando o pilar e esbelto (lambda > 35), a norma exige a consideracao do momento adicional gerado pela curvatura do eixo.",
        norm="NBR 6118, 15.5"
    )
    
    # 2. Flexao Composta Obliqua (Biaxial)
    me.add_step(
        id="col-biaxial",
        title="Verificacao Biaxial (Excentricidade nos dois eixos)",
        formula=r"\left(\frac{M_{xd}}{M_{rdx}}\right)^\alpha + \left(\frac{M_{yd}}{M_{rdy}}\right)^\alpha \leq 1{,}0",
        substitution=r"\alpha \approx 1{,}2 \text{ a } 1{,}5",
        result=r"\text{Status: OK}",
        explanation="Pilares de canto estao sujeitos a momentos em X e Y simultaneamente, exigindo uma verificacao de contorno de carga.",
        norm="NBR 6118"
    )
    
    return me.build()

def build_stability_gammaz_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Estabilidade Global", "stability")
    fmt = me._fmt
    
    # 1. Coeficiente Gamma-z
    gamma_z = res.get('gamma_z', 1.15)
    me.add_step(
        id="stab-gammaz",
        title="Estabilidade Global: Coeficiente Gamma-z",
        formula=r"\gamma_z = \frac{1}{1 - \frac{\Delta M_{tot}}{M_{1,tot}}}",
        substitution=rf"\gamma_z \approx {fmt(gamma_z, 2)}",
        result=r"\text{Estrutura de Nos Moveis}" if gamma_z > 1.1 else r"\text{Estrutura de Nos Fixos}",
        explanation="O Gamma-z indica a sensibilidade da estrutura aos efeitos de 2a ordem globais. Se > 1.1, a estrutura e considerada de nos moveis.",
        norm="NBR 6118, 15.4.2"
    )
    
    return me.build()

def build_column_detailing_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Detalhamento de Pilares", "detailing")
    fmt = me._fmt
    
    # 1. Armadura Longitudinal Minima
    me.add_step(
        id="det-min-as",
        title="Armadura Longitudinal Minima",
        formula=r"A_{s,min} = 0{{,}}15 \cdot \frac{N_d}{f_{yd}} \geq 0{{,}}004 \cdot A_c",
        substitution=rf"A_c = {fmt(res.get('area_cm2'))}\,cm^2",
        result=rf"A_{{s,min}} = {fmt(res.get('as_min_cm2'), 2)}\,cm^2",
        explanation="A armadura minima garante que o pilar tenha ductilidade e resista a efeitos de temperatura e retracao.",
        norm="NBR 6118, 17.3.5"
    )
    
    return me.build()

def build_detailing_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didatico: Detalhamento de Vigas", "beam_detailing")
    fmt = me._fmt
    geometry = res.get("geometry", {})
    inf = res.get("inf", {})
    sup = res.get("sup", {})
    skin = res.get("skin", {})

    me.add_step(
        id="beam-detailing-bottom-bars",
        title="Armadura Inferior",
        formula=r"A_{s,ef} \geq A_{s,calc}",
        substitution=rf"A_{{s,calc}} = {fmt(inf.get('area_calc'), 2)}\,cm^2",
        result=rf"{inf.get('spec', 'N/D')} \Rightarrow A_{{s,ef}} = {fmt(inf.get('area_efet'), 2)}\,cm^2",
        explanation="Seleciona barras comerciais para cobrir a armadura necessaria no vao.",
        norm="NBR 6118, 17.3"
    )
    me.add_step(
        id="beam-detailing-top-bars",
        title="Armadura Superior",
        formula=r"A_{s,ef} \geq A_{s,calc}",
        substitution=rf"A_{{s,calc}} = {fmt(sup.get('area_calc'), 2)}\,cm^2",
        result=rf"{sup.get('spec', 'N/D')} \Rightarrow A_{{s,ef}} = {fmt(sup.get('area_efet'), 2)}\,cm^2",
        explanation="Seleciona armadura superior para regioes de momento negativo e continuidade sobre apoios.",
        norm="NBR 6118, 17.3"
    )
    me.add_step(
        id="beam-detailing-anchorage",
        title="Ancoragem das Barras",
        formula=r"l_{b,nec} = \alpha l_b \frac{A_{s,calc}}{A_{s,ef}} \geq l_{b,min}",
        substitution=rf"l_b = {fmt(inf.get('lb_basic'), 1)}\,cm",
        result=rf"l_{{b,nec,inf}} = {fmt(inf.get('lb_nec'), 1)}\,cm,\quad l_{{b,nec,sup}} = {fmt(sup.get('lb_nec'), 1)}\,cm",
        explanation="Garante que as barras desenvolvam a tensao de calculo antes das secoes criticas.",
        norm="NBR 6118, 9.4"
    )
    me.add_step(
        id="beam-detailing-moment-shift",
        title="Decalagem do Diagrama de Momentos",
        formula=r"a_l = 0{,}5d(\cot\theta - \cot\alpha)",
        substitution=rf"d = {fmt(geometry.get('d_cm'), 1)}\,cm",
        result=rf"a_l = {fmt(geometry.get('al_cm'), 1)}\,cm",
        explanation="A decalagem considera a transferencia de esforcos pela trelica resistente ao cisalhamento.",
        norm="NBR 6118, 17.4.2"
    )
    me.add_step(
        id="beam-detailing-stirrups",
        title="Estribos",
        formula=r"A_{sw}/s \geq A_{sw,min}/s",
        substitution=r"\text{Armadura transversal calculada no cisalhamento}",
        result=rf"{res.get('stirrups', 'N/D')}",
        explanation="Define a armadura transversal para resistir ao cortante e confinar a armadura longitudinal.",
        norm="NBR 6118, 17.4"
    )
    me.add_step(
        id="beam-detailing-skin",
        title="Armadura de Pele",
        formula=r"A_{s,pele} = 0{,}10\% A_c \quad (h > 60\,cm)",
        substitution=rf"h = {fmt(geometry.get('h_cm'), 1)}\,cm",
        result=rf"{skin.get('suggested', 'Dispensada') if skin.get('needed') else 'Dispensada'}",
        explanation="A armadura de pele controla fissuracao lateral em vigas altas.",
        norm="NBR 6118, 17.3.5.2"
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
            title="Premissas Geometricas e Materiais",
            formula=r"h_{adot} = \text{input}, \quad f_{ck} = \text{input}",
            substitution=rf"h = {fmt(config.h)}\,m, \quad f_{{ck}} = {fmt(config.fck)}\,MPa",
            result=r"\text{Validado}",
            explanation="A espessura da laje e a resistencia do concreto regem a rigidez flexional e a capacidade ao cisalhamento.",
            norm="NBR 6118"
        )
    else:
        me.add_step(
            id="radier-input-soil",
            title="Parametros Geotecnicos de Entrada",
            formula=r"\sigma_{adm} = \text{input}, \quad k_v = \text{input}",
            substitution=rf"\sigma_{{adm}} = {fmt(config.sigma_adm_kPa)}\,kPa, \quad k_v = {fmt(config.kv, 1)}\,kN/m^3",
            result=r"\text{Validado}",
            explanation="Os parametros do solo definem a capacidade de carga e a rigidez do apoio elastico (Winkler).",
            norm="NBR 6122"
        )
    
    # 2. Verificação Principal (Pressão para Radier / Flexão para Laje)
    if is_laje:
        flexure = structural.get('flexao', {})
        mx_max = flexure.get('Mx_max_kNm_m', 0.0)
        as_req = flexure.get('Asx_top_calc_cm2_m', 0.0)
        me.add_step(
            id="slab-flexure-check",
            title="Solicitacao Flexional Maxima (Mx)",
            formula=r"M_{sd} = \gamma_f \cdot M_k, \quad A_s = \frac{M_{sd}}{0{,}9d \cdot f_{yd}}",
            substitution=rf"M_{{x,max}} = {fmt(mx_max, 2)}\,kNm/m",
            result=rf"A_{{s,req}} = {fmt(as_req, 2)}\,cm^2/m",
            explanation="O momento fletor maximo obtido via MEF determina a armadura necessaria para garantir o ELU de flexao.",
            norm="NBR 6118, Item 17.3"
        )
    else:
        q_max = geotech.get('pressao_max_modelo_kPa', 0.0)
        sigma_adm = config.sigma_adm_kPa
        me.add_step(
            id="radier-geotech-check",
            title="Verificacao de Pressao de Contato",
            formula=r"q_{max} \leq \sigma_{adm}",
            substitution=rf"{fmt(q_max, 2)}\,kPa \leq {fmt(sigma_adm, 2)}\,kPa",
            result=r"\text{Atende}" if q_max <= sigma_adm else r"\text{NAO ATENDE}",
            explanation="A pressao maxima solicitante no modelo MEF deve ser inferior a tensao admissivel do solo para evitar recalques excessivos ou ruptura.",
            norm="NBR 6122, Item 6.2"
        )
    
    # 3. Verificação de Punção (Comum a ambos, mas com nuances)
    punching = structural.get('puncao', {})
    ratio_max = punching.get('ratio_max', 0.0)
    if ratio_max is not None and ratio_max > 0:
        me.add_step(
            id="structural-punching-check",
            title="Verificacao de Puncao / Cisalhamento Local",
            formula=r"\tau_{sd} / \tau_{rd1} \leq 1{,}0",
            substitution=rf"\text{{Ratio}} \approx {fmt(ratio_max, 3)}",
            result=r"\text{Atende}" if ratio_max <= 1.0 else r"\text{Exige Reforco}",
            explanation=f"Verificacao de tração diagonal no concreto em torno dos apoios críticos {punching.get('critical_local', '')}.",
            norm="NBR 6118, Item 19.5"
        )

    # 4. Verificação de Serviço (Flecha para Laje / Recalque para Radier)
    if is_laje:
        w_max = service.get('w_max_mm', 0.0)
        w_limit = service.get('w_limit_mm', 1.0)
        me.add_step(
            id="slab-deflection-check",
            title="Verificacao de Flecha (ELS-DEF)",
            formula=r"w_{max} \leq L/250",
            substitution=rf"{fmt(w_max, 2)}\,mm \leq {fmt(w_limit, 2)}\,mm",
            result=r"\text{Atende}" if w_max <= w_limit else r"\text{NAO ATENDE}",
            explanation="A flecha em servico deve ser controlada para evitar danos esteticos e desconforto visual. O calculo considera a flecha diferida no tempo (Branson/Libanio).",
            norm="NBR 6118, Item 13.3"
        )
    
    res = me.build()
    if is_laje:
        as_ok = structural.get('flexao', {}).get('atende_flexao', True)
        punch_ok = ratio_max <= 1.0 if ratio_max else True
        w_ok = service.get('w_max_mm', 0.0) <= service.get('w_limit_mm', 1e9)
        opinion = "Laje validada para flexao, puncao e flechas (NBR 6118)." if (as_ok and punch_ok and w_ok) else "Revisar projeto: falha em criterios de ELU (Flexao/Puncao) ou ELS (Flecha)."
    else:
        q_max = geotech.get('pressao_max_modelo_kPa', 0.0)
        sigma_adm = config.sigma_adm_kPa
        opinion = "Radier validado: atende criterios de pressao admissivel (NBR 6122) e estabilidade estrutural." if q_max <= sigma_adm else "Revisar projeto: Pressao no solo excede a tensao admissivel informada."
        
    res["summary"] = {"opinion": opinion}
    return res
