from typing import Any
from .base import MemorialEngine

def build_footing_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Roteiro Didático: Sapatas", "footing")
    fmt = me._fmt
    
    # 1. Padronização Mestre
    me.add_standard_info()
    fck = float(res.get("fck", 25.0))
    # Note: add_material_step is not in base.py yet, but MemorialEngine can be extended
    # For now we use add_step manually for consistency if needed, or I'll update base.py
    
    me.add_step(
        id="footing-materials",
        title="Materiais e Resistências",
        formula=rf"f_{{ck}} = {fmt(fck, 1)}\,MPa",
        substitution=f"Concreto C{int(fck)}",
        result=f"f_cd = {fmt(fck/1.4, 2)} MPa",
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
        title="Verificação de Rigidez",
        formula=r"h \geq (A - a)/3",
        substitution=rf"{fmt(h)} \geq ({fmt(res.get('A_m'))} - {fmt(a_col)})/3",
        result=r"\text{Sapata Rígida}" if is_rigid else r"\text{Sapata Flexível}",
        explanation="Sapatas rígidas permitem considerar distribuição linear de tensões no solo.",
        norm="NBR 6118, 22.6"
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
        norm="NBR 6122"
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
