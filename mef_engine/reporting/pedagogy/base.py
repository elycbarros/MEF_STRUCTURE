import math
from typing import Any, Optional

class MemorialEngine:
    """
    Motor de geração de memoriais didáticos (Elite Tier).
    Garante LaTeX puro, citações normativas e visual premium.
    """
    def __init__(self, title: str, element_type: str = "general"):
        self.title = title
        self.element_type = element_type
        self.steps = []
        self._fmt = lambda val, prec=2: f"{float(val):.{prec}f}".replace(".", ",")

    def add_step(self, id: str, title: str, formula: str, substitution: str, result: str, explanation: str, norm: str = "NBR 6118"):
        self.steps.append({
            "id": id,
            "title": title,
            "formula": formula,
            "substitution": substitution,
            "result": result,
            "explanation": explanation,
            "norm": norm
        })

    def add_standard_info(self):
        self.add_step(
            id="normative-base",
            title="Base Normativa e Critérios de Segurança",
            formula=r"\gamma_c = 1{,}4, \quad \gamma_s = 1{,}15, \quad \gamma_f = 1{,}4",
            substitution="Valores padrão para combinações normais.",
            result="Conformidade NBR 6118:2023",
            explanation="O dimensionamento segue o método dos Estados Limites (ELU e ELS).",
            norm="NBR 6118, Cap. 12"
        )

    def add_durability_step(self, caa: int, cover: float):
        self.add_step(
            id="durability-check",
            title="Durabilidade e Proteção (CAA)",
            formula=rf"CAA = {caa}, \quad c_{{nom}} = {cover}\,mm",
            substitution=f"Classe de Aggressividade Ambiental {caa}",
            result=f"Cobrimento nominal: {cover} mm",
            explanation="Cobrimento definido em função da agressividade do meio.",
            norm="NBR 6118, Tab. 6.1 e 7.1"
        )

    def add_geometry_step(self, b: float, h: float, d: float):
        self.add_step(
            id="geometry-info",
            title="Geometria da Seção Transversal",
            formula=rf"b_w = {self._fmt(b, 2)}\,m, \quad h = {self._fmt(h, 2)}\,m, \quad d = {self._fmt(d, 2)}\,m",
            substitution=f"Seção Retangular",
            result=f"Altura útil (d) estimada",
            explanation="A altura útil é a distância da fibra mais comprimida ao centro de gravidade da armadura de tração.",
            norm="Geometria"
        )

    def add_validation_step(self, id: str, title: str, value: float, limit: float, operator: str, unit: str, explanation: str, norm: str):
        status = "OK" if eval(f"{value} {operator} {limit}") else "ALERTA"
        self.add_step(
            id=id,
            title=title,
            formula=rf"V = {self._fmt(value, 3)}\,{unit} \quad {operator} \quad L = {self._fmt(limit, 3)}\,{unit}",
            substitution=f"Valor calculado vs Limite normativo",
            result=f"Status: {status}",
            explanation=explanation,
            norm=norm
        )

    def build(self, summary: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return {
            "metadata": {
                "title": self.title,
                "element_type": self.element_type,
                "summary": summary or {}
            },
            "steps": self.steps
        }
