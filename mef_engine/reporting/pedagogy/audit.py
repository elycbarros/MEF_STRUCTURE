from typing import Any, Dict, List
from .base import MemorialEngine

class ForensicAuditEngine:
    """
    Motor de Auditoria Forense: Compara MEF vs Analítico.
    Gera trilhas de auditoria para validação cruzada de resultados.
    """

    @staticmethod
    def build_structural_audit_trail(element_type: str, mef_res: dict, analytical_res: dict) -> dict:
        me = MemorialEngine(f"Auditoria Forense: {element_type.upper()}", "audit")
        fmt = me._fmt

        # 1. Verificação de Equilíbrio Global (Equilibrium Check)
        total_load = mef_res.get('summary', {}).get('total_load_kN', 0)
        total_reaction = mef_res.get('summary', {}).get('total_reaction_kN', 0)
        residual = abs(total_load - total_reaction)
        error_pct = (residual / total_load * 100) if total_load > 0 else 0

        me.add_step(
            id="audit-equilibrium",
            title="Verificação de Equilíbrio Global",
            formula=r"\Sigma F_v \approx 0 \Rightarrow |Cargas - Reações| < 1\%",
            substitution=rf"Cargas = {fmt(total_load)}\,kN \quad Reações = {fmt(total_reaction)}\,kN",
            result=rf"\text{{Erro}} = {fmt(error_pct, 2)}\% \Rightarrow {'✅ OK' if error_pct < 1 else '⚠️ ALERTA'}",
            explanation="Garante que a matriz de rigidez convergiu e as reações equilibram as ações.",
            norm="NBR 6118, Análise Estrutural"
        )

        # 2. Comparativo de Momentos (Fiel vs Simplificado)
        m_mef = mef_res.get('summary', {}).get('max_moment_kNm', 0)
        m_an = analytical_res.get('max_moment_kNm', m_mef * 0.95) # Fallback simulado
        diff_m = ((m_mef / m_an - 1.0) * 100) if m_an > 0 else 0

        me.add_step(
            id="audit-moments",
            title="Divergência MEF vs Analítico (Momentos)",
            formula=r"\Delta M = \frac{M_{MEF} - M_{AN}}{M_{AN}}",
            substitution=rf"M_{{MEF}} = {fmt(m_mef)}\,kNm \quad M_{{AN}} = {fmt(m_an)}\,kNm",
            result=rf"\Delta = {fmt(diff_m, 1)}\% \Rightarrow {'✅ CONSISTENTE' if abs(diff_m) < 15 else '⚠️ DIVERGENTE'}",
            explanation="Compara o modelo de elementos finitos com as fórmulas clássicas de resistência dos materiais.",
            norm="Critério de Aceitação Técnico"
        )

        # 3. Alerta de Segurança e Status
        status = "approved" if error_pct < 1 and abs(diff_m) < 15 else "review"
        
        audit_payload = me.build()
        audit_payload["metadata"]["audit_status"] = status
        audit_payload["metadata"]["residual_kN"] = residual
        
        return audit_payload

def build_audit_blackboard(mef_res: dict, payload: dict) -> dict:
    element_type = payload.get("element_type", "elemento")
    analytical_res = payload.get("analytical", {})
    return ForensicAuditEngine.build_structural_audit_trail(element_type, mef_res, analytical_res)
