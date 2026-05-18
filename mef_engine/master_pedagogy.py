"""
master_pedagogy.py - Dispatcher Central e Seguro para Memoriais de Cálculo.
Arquitetura Blindada: Falhas em módulos específicos não afetam a estabilidade global.
"""
from typing import Any, Dict
from reporting.pedagogy.registry import PedagogyRegistry

# Importação dos builders (descentralizados em /reporting/pedagogy/)
from reporting.pedagogy.beam import build_beam_blackboard, build_vigacross_blackboard
from reporting.pedagogy.column import build_column_blackboard
from reporting.pedagogy.slab import build_lajes_blackboard
from reporting.pedagogy.foundation import build_footing_blackboard, build_pile_blackboard
from reporting.pedagogy.detailing import build_detailing_blackboard, build_column_detailing_blackboard
from reporting.pedagogy.audit import build_audit_blackboard
from reporting.pedagogy.special import (
    build_stairs_blackboard,
    build_retaining_wall_blackboard,
    build_elevated_reservoir_blackboard,
    build_corbel_blackboard,
    build_gerber_tooth_blackboard,
    build_deep_beam_blackboard,
    build_helical_stairs_blackboard,
    build_concrete_wall_blackboard,
    build_pile_cap_blackboard,
    build_beam_opening_blackboard,
    build_tension_pro_blackboard,
    build_exam_auditor_blackboard
)
from reporting.pedagogy.slab import build_lajes_blackboard
from reporting.pedagogy.frame import build_frame_blackboard
from reporting.pedagogy.stability import build_stability_blackboard
from reporting.pedagogy.foundation import build_spt_blackboard

# Registro manual para manter o dispatcher leve e explícito
PedagogyRegistry._builders["beam"] = build_beam_blackboard
PedagogyRegistry._builders["column"] = build_column_blackboard
PedagogyRegistry._builders["slab"] = build_lajes_blackboard
PedagogyRegistry._builders["footing"] = build_footing_blackboard
PedagogyRegistry._builders["pile"] = build_pile_blackboard
PedagogyRegistry._builders["detailing"] = build_detailing_blackboard
PedagogyRegistry._builders["audit"] = build_audit_blackboard
PedagogyRegistry._builders["stair"] = build_stairs_blackboard
PedagogyRegistry._builders["stairs"] = build_stairs_blackboard
PedagogyRegistry._builders["retaining_wall"] = build_retaining_wall_blackboard
PedagogyRegistry._builders["reservoir"] = build_elevated_reservoir_blackboard
PedagogyRegistry._builders["corbel"] = build_corbel_blackboard
PedagogyRegistry._builders["gerber_tooth"] = build_gerber_tooth_blackboard
PedagogyRegistry._builders["deep_beam"] = build_deep_beam_blackboard
PedagogyRegistry._builders["helical_stairs"] = build_helical_stairs_blackboard
PedagogyRegistry._builders["concrete_wall"] = build_concrete_wall_blackboard
PedagogyRegistry._builders["pile_cap"] = build_pile_cap_blackboard
PedagogyRegistry._builders["beam_opening"] = build_beam_opening_blackboard
PedagogyRegistry._builders["tension_pro"] = build_tension_pro_blackboard
PedagogyRegistry._builders["frame"] = build_frame_blackboard
PedagogyRegistry._builders["vigacross"] = build_vigacross_blackboard
PedagogyRegistry._builders["exam_auditor"] = build_exam_auditor_blackboard

def build_structural_blackboard(element_type: str, result: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ponto de entrada único para geração de memoriais.
    Utiliza o Registry para garantir blindagem contra erros de manutenção.
    """
    return PedagogyRegistry.get_blackboard(element_type, result, payload)

def build_composite_pedagogy(element_configs: list) -> Dict[str, Any]:
    """Orquestrador Multi-Mestre para elementos complexos."""
    return PedagogyRegistry.get_composite_blackboard(element_configs)

# Funções de conveniência para manter compatibilidade com routers
def build_beam_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("beam", result, payload or {})

def build_column_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("column", result, payload or {})

def build_slab_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("slab", result, payload or {})

def build_footing_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("footing", result, payload or {})

def build_pile_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("pile", result, payload or {})

def build_vigacross_blackboard(result: Dict[str, Any], payload: Dict[str, Any] = None):
    return build_structural_blackboard("vigacross", result, payload or {})

def build_forensic_audit(element_type: str, mef_res: dict, analytical_res: dict):
    return build_structural_blackboard("audit", mef_res, {"element_type": element_type, "analytical": analytical_res})

def build_structural_audit_trail(config: Any, memorial: Any):
    """
    Função de compatibilidade legado para o pipeline de Lajes.
    Mapeia os dados do memorial para o novo motor de auditoria forense.
    """
    # Tenta extrair resultados do MEF e Analítico do memorial de lajes
    mef_res = memorial.get("master", {}).get("mef_summary", {})
    analytical_res = memorial.get("verificacoes_estruturais", {})
    
    # Se mef_res estiver vazio, tenta no nível superior (fallback)
    if not mef_res:
        mef_res = memorial.get("mef_summary", {})
        
    # Executa a auditoria nova
    res = build_forensic_audit("slab", mef_res, analytical_res)
    
    # Compatibilidade legado: slab_memorial.py espera res['summary']['opinion']
    status = res["metadata"].get("audit_status", "review")
    res["summary"] = {
        "opinion": "APROVADO - O modelo numérico converge e é consistente com a teoria clássica." if status == "approved" else "REVISÃO NECESSÁRIA - Divergência técnica acima do limite normativo."
    }
    
    return res
