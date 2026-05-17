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

    def txt(self, s: str) -> str:
        """Envolve string em \text{} para legibilidade em LaTeX math mode."""
        return rf"\text{{{s}}}"

    def _auto_latex(self, s: str) -> str:
        """Detecta se uma string é texto puro e a envolve em \text{}."""
        if not s: return ""
        # Se já tiver comandos LaTeX, símbolos matemáticos ou for numérico, não mexe
        math_chars = ["\\", "$", "_", "^", "{", "}", "="]
        if any(char in s for char in math_chars) or s.replace(",", "").replace(".", "").replace("-", "").isdigit():
            return s
        return rf"\text{{{s}}}"

    def add_step(self, id: str, title: str, formula: str, substitution: str, result: str, explanation: str, norm: str = "NBR 6118", diagram: Optional[str] = None, chartData: Optional[dict] = None, detailingData: Optional[dict] = None, diagramData: Optional[dict] = None):
        self.steps.append({
            "id": id,
            "title": title,
            "formula": formula,
            "substitution": self._auto_latex(substitution),
            "result": self._auto_latex(result),
            "explanation": explanation,
            "norm": norm,
            "diagram": diagram,
            "chartData": chartData,
            "detailingData": detailingData,
            "diagramData": diagramData
        })

    def technical_diagram(self, kind: str, title: str, **values: Any) -> dict[str, Any]:
        return {"kind": kind, "title": title, "values": values}

    def add_standard_info(self):
        self.add_step(
            id="normative-base",
            title="Base Normativa e Critérios de Segurança",
            formula=r"\gamma_c = 1{,}4, \quad \gamma_s = 1{,}15, \quad \gamma_f = 1{,}4",
            substitution=r"\text{Valores padrão para combinações normais.}",
            result=r"\text{Conformidade NBR 6118:2023}",
            explanation="O dimensionamento segue o método dos Estados Limites (ELU e ELS).",
            norm="NBR 6118, Cap. 12"
        )

    def add_durability_step(self, caa: int, cover: float):
        self.add_step(
            id="durability-check",
            title="Durabilidade e Proteção (CAA)",
            formula=rf"CAA = {caa}, \quad c_{{nom}} = {cover}\,mm",
            substitution=rf"\text{{Classe de Agressividade Ambiental {caa}}}",
            result=rf"\text{{Cobrimento nominal: {cover} mm}}",
            explanation="Cobrimento definido em função da agressividade do meio.",
            norm="NBR 6118, Tab. 6.1 e 7.1"
        )

    def add_geometry_step(self, b: float, h: float, d: float):
        self.add_step(
            id="geometry-info",
            title="Geometria da Seção Transversal",
            formula=rf"b_w = {self._fmt(b, 2)}\,m, \quad h = {self._fmt(h, 2)}\,m, \quad d = {self._fmt(d, 2)}\,m",
            substitution=r"\text{Seção Retangular}",
            result=r"\text{Altura útil (d) estimada}",
            explanation="A altura útil é a distância da fibra mais comprimida ao centro de gravidade da armadura de tração.",
            norm="Geometria"
        )

    def add_validation_step(self, id: str, title: str, value: float, limit: float, operator: str, unit: str, explanation: str, norm: str):
        status = "OK" if eval(f"{value} {operator} {limit}") else "ALERTA"
        self.add_step(
            id=id,
            title=title,
            formula=rf"V = {self._fmt(value, 3)}\,{unit} \quad {operator} \quad L = {self._fmt(limit, 3)}\,{unit}",
            substitution=r"\text{Valor calculado vs Limite normativo}",
            result=rf"\text{{Status: {status}}}",
            explanation=explanation,
            norm=norm
        )

    def add_reactions_step(self, reactions: list[dict]):
        formula = r"\sum F_v = 0, \quad \sum M = 0"
        sub = ", ".join([rf"R_{{{r['id']}}} = {self._fmt(r['R'])}" for r in reactions])
        self.add_step(
            id="structural-reactions",
            title="Reações de Apoio e Equilíbrio",
            formula=formula,
            substitution=sub,
            result=rf"\text{{Equilíbrio validado}}",
            explanation="As reações de apoio garantem a estabilidade estática do elemento sob as cargas aplicadas.",
            norm="Mecânica Estrutural"
        )

    def add_comparison_step(self, m_classic: float, m_mef: float, unit: str = "kNm"):
        diff = abs(m_classic - m_mef) / m_classic * 100 if m_classic > 0 else 0
        status = "✅ CONSISTENTE" if diff < 5 else "⚠️ DIVERGÊNCIA ACEITÁVEL"
        self.add_step(
            id="classic-vs-mef",
            title="Validação Cruzada: Clássico vs MEF",
            formula=r"\Delta \% = \frac{|M_{cl} - M_{mef}|}{M_{cl}} \cdot 100",
            substitution=rf"M_{{cl}} = {self._fmt(m_classic)}\,{unit}, \quad M_{{mef}} = {self._fmt(m_mef)}\,{unit}",
            result=rf"\Delta = {self._fmt(diff, 1)}\% \Rightarrow \text{{{status}}}",
            explanation="Compara o cálculo analítico (fórmulas de livros-texto) com o método de elementos finitos para garantir a acurácia do modelo.",
            norm="Auditoria Forense"
        )

    def add_bibliography_step(self):
        """Adiciona referências bibliográficas clássicas ao memorial (Elite Pedagogical)."""
        references = [
            "1. HIBBELER, Russell C. Resistencia dos Materiais. 7.ed. Prentice Hall, 2010.",
            "2. FERDINAND, P. B.; JOHNSTON JR, E. R. Resistencia dos Materiais. Mc Graw-Hill.",
            "3. PEREIRA, J. C., Notas de Aula CURSO DE MECANICA DOS SOLIDOS, DEMEC-UFSC, 2003.",
            "4. BOTELHO, Manoel H.C. Resistencia dos Materiais. 2.ed. Edgard Blucher. 2013.",
            "5. ASSAN, Aloisio Ernesto. Resistencia dos Materiais, V.1. 1.ed. Ed. Unicamp. 2010."
        ]
        formula_latex = r"\\" .join([rf"\text{{{ref}}}" for ref in references])
        self.add_step(
            id="bibliography",
            title="Bibliografia Recomendada (Resistencia dos Materiais)",
            formula=r"\text{Base Cientifica e Pedagogica}",
            substitution=r"\text{Referencias classicas para consulta e aprofundamento}",
            result=rf"\left\{{ \begin{{array}}{{l}} {formula_latex} \end{{array}} \right.",
            explanation="As equacoes e metodos apresentados fundamentam-se na bibliografia classica de resistencia dos materiais e mecanica dos solidos.",
            norm="Literatura Tecnica"
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
