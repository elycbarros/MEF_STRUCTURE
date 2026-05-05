from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
import math

@dataclass
class MathStep:
    id: str
    title: str
    formula_latex: str
    substitution_latex: str
    result_latex: str
    explanation: str
    norm_ref: str = "NBR 6118"
    opinion: Optional[str] = None
    status: str = "OK"  # OK, ALERTA, INFO

class MemorialEngine:
    """
    Motor centralizado para geracao de memoriais de calculo pedagogicos e forenses.
    Simplifica a criacao de passos matematicos e garante a padronizacao visual.
    """
    def __init__(self, title: str, element_type: str, mode: str = "MESTRE"):
        self.title = title
        self.element_type = element_type
        self.mode = mode
        self.steps: List[MathStep] = []
        self.metadata: Dict[str, Any] = {}
        self.precision = 2

    def set_metadata(self, **kwargs):
        self.metadata.update(kwargs)
        return self

    def _fmt(self, value: Any, p: Optional[int] = None) -> str:
        """Formatacao padrao de numeros para LaTeX brasileiro (virgula)."""
        if value is None: return "n/d"
        try:
            val = float(value)
            prec = p if p is not None else self.precision
            formatted = f"{val:.{prec}f}"
            return formatted.replace(".", ",")
        except (ValueError, TypeError):
            return str(value)

    def add_step(self, 
                 id: str, 
                 title: str, 
                 formula: str, 
                 substitution: str, 
                 result: str, 
                 explanation: str, 
                 norm: str = "NBR 6118",
                 opinion: Optional[str] = None,
                 status: str = "OK"):
        """Adiciona um passo matematico ao memorial."""
        step = MathStep(
            id=id,
            title=title,
            formula_latex=formula,
            substitution_latex=substitution,
            result_latex=result,
            explanation=explanation,
            norm_ref=norm,
            opinion=opinion,
            status=status
        )
        self.steps.append(step)
        return self

    def add_validation_step(self, 
                            id: str, 
                            title: str, 
                            value: float, 
                            limit: float, 
                            operator: str, 
                            unit: str,
                            explanation: str,
                            norm: str = "NBR 6118"):
        """
        Adiciona automaticamente um passo de verificacao (ex: Vsd <= Vrd2).
        Gera o status ALERTA se a condicao falhar.
        """
        passed = False
        if operator == "<=": passed = value <= limit
        elif operator == ">=": passed = value >= limit
        elif operator == "<": passed = value < limit
        elif operator == ">": passed = value > limit
        elif operator == "==": passed = abs(value - limit) < 1e-6
        
        status = "OK" if passed else "ALERTA"
        res_text = r"\text{Atende}" if passed else r"\text{Nao atende / Revisar}"
        
        formula = rf"Value {operator} Limit" # Placeholder to be replaced by actual logic in caller or improved here
        
        return self.add_step(
            id=id,
            title=title,
            formula=rf"Verification: \text{{Value}} {operator} \text{{Limit}}",
            substitution=rf"{self._fmt(value)} {operator} {self._fmt(limit)}",
            result=rf"{res_text} \quad ({self._fmt(value)}\,{unit})",
            explanation=explanation,
            norm=norm,
            status=status
        )

    def add_material_step(self, fck: float, fyk: float = 500.0):
        """Adiciona automaticamente o passo de propriedades dos materiais."""
        fcd = fck / 1.4
        fyd = fyk / 1.15
        ecs = 0.8 * 5600 * (fck ** 0.5)
        
        return self.add_step(
            id="materials",
            title="Propriedades dos Materiais",
            formula=r"f_{cd} = \frac{f_{ck}}{1{,}4}, \quad f_{yd} = \frac{f_{yk}}{1{,}15}, \quad E_{cs} = 0{,}8 \cdot 5600\sqrt{f_{ck}}",
            substitution=rf"f_{{cd}} = \frac{{{self._fmt(fck, 1)}}}{{1{{,}}4}},\quad f_{{yd}} = \frac{{{self._fmt(fyk, 1)}}}{{1{{,}}15}}",
            result=rf"f_{{cd}} = {self._fmt(fcd, 2)}\,MPa,\quad f_{{yd}} = {self._fmt(fyd, 2)}\,MPa,\quad E_{{cs}} \approx {self._fmt(ecs, 0)}\,MPa",
            explanation="As resistencias e o modulo de elasticidade sao a base para as verificacoes de ELU e ELS.",
            norm="NBR 6118, Itens 8.2 e 8.3"
        )

    def add_geometry_step(self, b_m: float, h_m: float, d_m: Optional[float] = None):
        """Adiciona passo de geometria da secao."""
        ac = b_m * h_m
        d_val = d_m if d_m else h_m - 0.04 # fallback simplificado
        return self.add_step(
            id="geometry",
            title="Geometria da Secao",
            formula=r"A_c = b \cdot h, \quad d \approx h - d'",
            substitution=rf"A_c = {self._fmt(b_m)} \cdot {self._fmt(h_m)}",
            result=rf"A_c = {self._fmt(ac, 4)}\,m^2, \quad d = {self._fmt(d_val, 3)}\,m",
            explanation="A area bruta e a altura util definem a capacidade rigida e o braco de alavanca da secao.",
            norm="Geometria Resistente"
        )

    def build(self) -> Dict[str, Any]:
        """Gera o dicionario final compativel com o frontend e o PDF."""
        return {
            "mode": self.mode,
            "element": self.element_type,
            "title": self.title,
            "metadata": self.metadata,
            "steps": [
                {
                    "id": s.id,
                    "title": s.title,
                    "formula_latex": s.formula_latex,
                    "substitution_latex": s.substitution_latex,
                    "result_latex": s.result_latex,
                    "explanation": s.explanation,
                    "norm_ref": s.norm_ref,
                    "opinion": s.opinion,
                    "status": s.status
                } for s in self.steps
            ]
        }
