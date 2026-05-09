from typing import Any
from .base import MemorialEngine

def build_stability_blackboard(res: dict[str, Any]) -> dict[str, Any]:
    me = MemorialEngine("Estabilidade Global e Vento", "stability")
    fmt = me._fmt
    
    me.add_standard_info()
    
    me.add_step(
        id="wind-pressure",
        title="Pressão Dinâmica do Vento",
        formula=r"q(z) = 0,613 \cdot (V_k \cdot S_1 \cdot S_2(z) \cdot S_3)^2",
        substitution=rf"q = 0,613 \cdot ({fmt(res.get('v0'))} \cdot 1,0 \cdot 1,0 \cdot 1,0)^2",
        result=rf"q = {fmt(res.get('q0_kN_m2'))}\,kN/m^2",
        explanation="Cálculo da pressão de obstrução que o vento exerce na fachada conforme a altura.",
        norm="NBR 6123"
    )
    
    me.add_validation_step(
        id="gamma-z-check",
        title="Índice de Estabilidade Gamma-Z",
        value=float(res.get("gamma_z", 1.1)),
        limit=1.1,
        operator="<=",
        unit="",
        explanation="Se Gamma-Z > 1.1, a estrutura é de 'nós móveis' e os efeitos de segunda ordem globais devem ser majorados.",
        norm="NBR 6118, 15.4"
    )
    
    return me.build()

def build_stability_gammaz_blackboard(res: dict) -> dict:
    me = MemorialEngine("Roteiro Didático: Estabilidade Global", "stability")
    fmt = me._fmt
    
    # 1. Coeficiente Gamma-z
    gamma_z = res.get('gamma_z', 1.15)
    me.add_step(
        id="stab-gammaz",
        title="Estabilidade Global: Coeficiente Gamma-z",
        formula=r"\gamma_z = \frac{1}{1 - \frac{\Delta M_{tot}}{M_{1,tot}}}",
        substitution=rf"\gamma_z \approx {fmt(gamma_z, 2)}",
        result=r"\text{Estrutura de Nós Móveis}" if gamma_z > 1.1 else r"\text{Estrutura de Nós Fixos}",
        explanation="O Gamma-z indica a sensibilidade da estrutura aos efeitos de 2ª ordem globais.",
        norm="NBR 6118, 15.4.2"
    )
    
    return me.build()
