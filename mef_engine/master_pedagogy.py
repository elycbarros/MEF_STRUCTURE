"""
master_pedagogy.py - Dispatcher Central e Seguro para Memoriais de Cálculo.
Arquitetura Blindada: Falhas em módulos específicos não afetam a estabilidade global.
"""
from typing import Any, Dict
from reporting.pedagogy.registry import PedagogyRegistry

# Importação dos builders (descentralizados em /reporting/pedagogy/)
from reporting.pedagogy.beam import build_beam_blackboard
from reporting.pedagogy.column import build_column_blackboard
from reporting.pedagogy.slab import build_lajes_blackboard
from reporting.pedagogy.foundation import build_footing_blackboard
from reporting.pedagogy.detailing import build_detailing_blackboard
from reporting.pedagogy.audit import build_audit_blackboard

# Registro manual para manter o dispatcher leve e explícito
PedagogyRegistry._builders["beam"] = build_beam_blackboard
PedagogyRegistry._builders["column"] = build_column_blackboard
PedagogyRegistry._builders["slab"] = build_lajes_blackboard
PedagogyRegistry._builders["footing"] = build_footing_blackboard
PedagogyRegistry._builders["detailing"] = build_detailing_blackboard
PedagogyRegistry._builders["audit"] = build_audit_blackboard

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
def build_beam_blackboard(result: Dict[str, Any], payload: Dict[str, Any]):
    return build_structural_blackboard("beam", result, payload)

def build_column_blackboard(result: Dict[str, Any], payload: Dict[str, Any]):
    return build_structural_blackboard("column", result, payload)

def build_slab_blackboard(result: Dict[str, Any], payload: Dict[str, Any]):
    return build_structural_blackboard("slab", result, payload)

def build_forensic_audit(element_type: str, mef_res: dict, analytical_res: dict):
    return build_structural_blackboard("audit", mef_res, {"element_type": element_type, "analytical": analytical_res})
