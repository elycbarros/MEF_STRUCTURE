from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

PLATFORM_VERSION = "4.0.0-ELITE"

def build_unified_memorial(
    module_title: str,
    engine_name: str,
    engine_version: str,
    analysis_date: str | None = None,
    hypotheses: list[str] | None = None,
    materials: dict[str, Any] | None = None,
    loads: dict[str, Any] | None = None,
    combinations: list[str] | None = None,
    model_details: dict[str, Any] | None = None,
    results: dict[str, Any] | None = None,
    verifications: list[dict[str, Any]] | None = None,
    governing: dict[str, Any] | None = None,
    alerts: list[str] | None = None,
    limitations: list[str] | None = None,
    payload_hash: str | None = None,
) -> str:
    """
    Gera um memorial descritivo em Markdown seguindo o padrao unificado MEF STRUCTURAL M4.
    """
    date_str = analysis_date or datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    
    sections = []
    sections.append(f"# Memorial de Calculo Padronizado - {module_title}")
    sections.append(f"*Versao do Motor: {engine_name} v{engine_version}*")
    sections.append(f"*Data da Analise: {date_str}*")
    if payload_hash:
        sections.append(f"*Hash do Payload: `{payload_hash}`*")
    
    if hypotheses:
        sections.append("## 1. Hipoteses de Analise")
        for h in hypotheses:
            sections.append(f"- {h}")
            
    if materials:
        sections.append("## 2. Materiais")
        for k, v in materials.items():
            sections.append(f"- {k}: `{v}`")
            
    if loads:
        sections.append("## 3. Acoes e Cargas")
        for k, v in loads.items():
            sections.append(f"- {k}: `{v}`")
            
    if combinations:
        sections.append("## 4. Combinacoes de Acoes")
        for c in combinations:
            sections.append(f"- {c}")
            
    if model_details:
        sections.append("## 5. Resumo do Modelo")
        for k, v in model_details.items():
            sections.append(f"- {k}: `{v}`")
            
    if results:
        sections.append("## 6. Resultados Principais")
        for k, v in results.items():
            sections.append(f"- {k}: `{v}`")
            
    if verifications:
        sections.append("## 7. Verificacoes e Auditoria")
        for v in verifications:
            status = "✅" if v.get('pass') else "❌"
            sections.append(f"- {status} **{v['label']}**: {v['value']} (Limite: {v['limit']})")
            
    if governing:
        sections.append("## 8. Resultados Governantes (Envoltoria)")
        for k, v in governing.items():
            sections.append(f"- {k}: `{v}`")
            
    if alerts:
        sections.append("## 9. Alertas")
        for a in alerts:
            sections.append(f"- ⚠️ {a}")
            
    if limitations:
        sections.append("## 10. Limitacoes e Disclaimer")
        for l in limitations:
            sections.append(f"- {l}")
            
    sections.append("\n---")
    sections.append("*Este documento foi gerado automaticamente pela plataforma MEF STRUCTURAL. O uso executivo exige revisao de engenheiro responsavel.*")
            
    return "\n\n".join(sections)
