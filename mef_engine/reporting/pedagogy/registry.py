import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

class PedagogyRegistry:
    """
    Registro seguro de roteiros pedagógicos para "blindagem" do sistema.
    Garante que falhas em módulos individuais não derrubem o motor global.
    """
    _builders: Dict[str, Callable] = {}

    @classmethod
    def register(cls, element_type: str):
        def decorator(func: Callable):
            cls._builders[element_type] = func
            return func
        return decorator

    @classmethod
    def get_blackboard(cls, element_type: str, result: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        builder = cls._builders.get(element_type)
        if not builder:
            logger.warning(f"Pedagogy builder for '{element_type}' not found. Using fallback.")
            return cls._fallback_blackboard(element_type, result)
        
        try:
            return builder(result, payload)
        except Exception as e:
            logger.error(f"Error in pedagogy builder '{element_type}': {str(e)}")
            return cls._fallback_blackboard(element_type, result, error=str(e))

    @classmethod
    def get_composite_blackboard(cls, element_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera um memorial composto por múltiplos elementos (Multi-Master).
        Cada config deve ter: {'type': 'beam', 'result': {...}, 'payload': {...}}
        """
        composite_steps = []
        composite_title = "Memorial Estrutural Unificado"
        
        for cfg in element_configs:
            etype = cfg.get('type')
            result = cfg.get('result', {})
            payload = cfg.get('payload', {})
            
            blackboard = cls.get_blackboard(etype, result, payload)
            # Prefixar IDs para evitar colisão no frontend
            for step in blackboard.get("steps", []):
                step["id"] = f"{etype}-{step['id']}"
                composite_steps.append(step)
            
            if len(element_configs) == 1:
                composite_title = blackboard["metadata"]["title"]

        return {
            "metadata": {
                "title": composite_title,
                "is_composite": True,
                "element_count": len(element_configs)
            },
            "steps": composite_steps
        }

    @classmethod
    def _fallback_blackboard(cls, element_type: str, result: Dict[str, Any], error: str = None) -> Dict[str, Any]:
        """Gera um memorial simplificado caso o módulo principal falhe."""
        return {
            "metadata": {
                "title": f"Memorial de Cálculo (Resumo): {element_type.upper()}",
                "element_type": element_type,
                "status": "warning" if error else "simple"
            },
            "steps": [
                {
                    "id": "fallback-info",
                    "title": "Aviso do Sistema",
                    "explanation": f"O memorial detalhado para '{element_type}' está em manutenção ou indisponível." if error else f"Resumo técnico para '{element_type}'.",
                    "result": f"Erro técnico: {error}" if error else "Exibindo apenas dados brutos."
                },
                {
                    "id": "raw-data",
                    "title": "Dados de Saída",
                    "explanation": "Resultados brutos extraídos do solver estrutural.",
                    "result": f"M_max: {result.get('summary', {}).get('max_moment_kNm', 0):.2f} kNm | V_max: {result.get('summary', {}).get('max_shear_kN', 0):.2f} kN"
                }
            ]
        }
