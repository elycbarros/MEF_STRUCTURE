from typing import Any
from .base import MemorialEngine

def build_column_detailing_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Detalhamento de Pilares", "detailing")
    fmt = me._fmt
    
    # 1. Armadura Longitudinal Mínima
    me.add_step(
        id="det-min-as",
        title="Armadura Longitudinal Mínima",
        formula=r"A_{s,min} = 0{,}15 \cdot \frac{N_d}{f_{yd}} \geq 0{,}004 \cdot A_c",
        substitution=rf"A_c = {fmt(res.get('area_cm2', 400))}\,cm^2",
        result=rf"A_{{s,min}} = {fmt(res.get('as_min_cm2', 1.6), 2)}\,cm^2",
        explanation="A armadura mínima garante que o pilar tenha ductilidade e resista a efeitos de temperatura.",
        norm="NBR 6118, 17.3.5"
    )
    
    return me.build()

def build_detailing_blackboard(res: dict, payload: dict = None) -> dict:
    me = MemorialEngine("Roteiro Didático: Detalhamento de Vigas", "beam_detailing")
    fmt = me._fmt
    geometry = res.get("geometry", {})
    inf = res.get("inf", {})
    sup = res.get("sup", {})
    skin = res.get("skin", {})

    # Mapeamento de Geometria para Detalhamento Gráfico
    b_m = geometry.get("b_cm", 20) / 100.0
    h_m = geometry.get("h_cm", 50) / 100.0
    cover_m = geometry.get("cover_mm", 30) / 1000.0

    me.add_step(
        id="beam-detailing-bottom-bars",
        title="Armadura Inferior (Tração)",
        formula=r"A_{s,ef} \geq A_{s,calc}",
        substitution=rf"A_{{s,calc}} = {fmt(inf.get('area_calc'), 2)}\,cm^2",
        result=rf"{inf.get('spec', 'N/D')} \Rightarrow A_{{s,ef}} = {fmt(inf.get('area_efet'), 2)}\,cm^2",
        explanation="Seleciona barras comerciais para cobrir a armadura necessária no vão.",
        norm="NBR 6118, 17.3",
        detailingData={
            "type": "beam_section",
            "b": b_m, "h": h_m, "cover": cover_m,
            "layers": [
                {"position": "bottom", "bars": [{"count": inf.get('count', 2), "diameter": inf.get('phi_mm', 10)}]},
                {"position": "top", "bars": [{"count": sup.get('count', 2), "diameter": sup.get('phi_mm', 10)}]}
            ]
        }
    )
    me.add_step(
        id="beam-detailing-top-bars",
        title="Armadura Superior (Porta-Estribo / Negativa)",
        formula=r"A_{s,ef} \geq A_{s,calc}",
        substitution=rf"A_{{s,calc}} = {fmt(sup.get('area_calc'), 2)}\,cm^2",
        result=rf"{sup.get('spec', 'N/D')} \Rightarrow A_{{s,ef}} = {fmt(sup.get('area_efet'), 2)}\,cm^2",
        explanation="Seleciona armadura superior para regiões de momento negativo ou para suporte dos estribos.",
        norm="NBR 6118, 17.3",
        detailingData={
            "type": "beam_section",
            "b": b_m, "h": h_m, "cover": cover_m,
            "layers": [
                {"position": "top", "bars": [{"count": sup.get('count', 2), "diameter": sup.get('phi_mm', 10)}]},
                {"position": "bottom", "bars": [{"count": inf.get('count', 2), "diameter": inf.get('phi_mm', 10)}]}
            ]
        }
    )
    # Módulo 6: Ancoragem das Barras (NBR 6118, 9.4)
    me.add_step(
        id="beam-detailing-anchorage-basic",
        title="Comprimento de Ancoragem Básico",
        formula=r"l_b = \frac{\phi}{4} \frac{f_{yd}}{f_{bd}}",
        substitution=rf"\phi = {fmt(inf.get('phi_mm'))}\,mm \quad f_{{bd}} = \text{{aderência de cálculo}}",
        result=rf"l_b = {fmt(inf.get('lb_basic', 30), 1)}\,cm",
        explanation="O comprimento básico é o necessário para que a barra atinja sua tensão de escoamento sem escorregar.",
        norm="NBR 6118, 9.4.2"
    )
    me.add_step(
        id="beam-detailing-anchorage-nec",
        title="Comprimento de Ancoragem Necessário",
        formula=r"l_{b,nec} = \alpha l_b \frac{A_{s,calc}}{A_{s,ef}} \geq l_{b,min}",
        substitution=rf"A_{{s,calc}} = {fmt(inf.get('area_calc'), 2)}\,cm^2 \quad A_{{s,ef}} = {fmt(inf.get('area_efet'), 2)}\,cm^2",
        result=rf"l_{{b,nec,inf}} = {fmt(inf.get('lb_nec', 30), 1)}\,cm",
        explanation="Considera o excesso de armadura e o tipo de ancoragem (com ou sem gancho).",
        norm="NBR 6118, 9.4.2.5"
    )

    # Módulo 7: Decalagem do Diagrama de Momentos (NBR 6118, 17.4.2)
    me.add_step(
        id="beam-detailing-moment-shift",
        title="Decalagem do Diagrama de Momentos",
        formula=r"a_l = 0,5 d (\cot\theta - \cot\alpha)",
        substitution=rf"d \approx {fmt(geometry.get('d_cm', 45), 1)}\,cm \quad \theta = 45^\circ \quad \alpha = 90^\circ",
        result=rf"a_l = {fmt(geometry.get('al_cm', 45), 1)}\,cm",
        explanation="A decalagem (al) projeta o diagrama de momentos para compensar o efeito da treliça resistente de cálculo.",
        norm="NBR 6118, 17.4.2.2"
    )

    # Armadura Transversal e Detalhes
    me.add_step(
        id="beam-detailing-stirrups",
        title="Estribos e Armadura Transversal",
        formula=r"A_{sw}/s \geq A_{sw,min}/s",
        substitution=rf"\text{{Armadura transversal adotada}}",
        result=rf"{res.get('stirrups', 'N/D')}",
        explanation="Os estribos garantem a resistência ao esforço cortante e a estabilidade das barras longitudinais.",
        norm="NBR 6118, 17.4.1"
    )
    me.add_step(
        id="beam-detailing-skin",
        title="Armadura de Pele",
        formula=r"A_{s,pele} = 0,10\% A_c \quad (h > 60\,cm)",
        substitution=rf"h = {fmt(geometry.get('h_cm', 50), 1)}\,cm",
        result=rf"{skin.get('suggested', 'Dispensada') if skin.get('needed') else 'Dispensada'}",
        explanation="A armadura de pele controla fissuração lateral em vigas altas.",
        norm="NBR 6118, 17.3.5.2"
    )
    return me.build()
