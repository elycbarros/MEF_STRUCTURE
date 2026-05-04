import numpy as np
from typing import List, Dict, Any

class AICopilot:
    """
    AI Structural Copilot (M5-Master).
    Analisa resultados de cálculo e fornece heurísticas de otimização e segurança.
    """
    
    def __init__(self, maturity_level: str = "M5-MASTER"):
        self.maturity_level = maturity_level

    def analyze_beam(self, design_data: dict) -> List[str]:
        suggestions = []
        
        # Heurística de Flecha
        deflect = design_data.get('deflection', {})
        if deflect.get('status') == 'EXCEDE':
            suggestions.append("⚠️ Flecha excessiva: Considere aumentar a altura da seção (h) em vez de apenas aumentar a armadura. A rigidez cresce ao cubo com a altura.")
        
        # Heurística de Domínio
        flex = design_data.get('flexure_bottom', {})
        if flex.get('domain') == '4':
            suggestions.append("❌ Seção super-armada (Domínio 4): Risco de ruptura frágil. Aumente a seção de concreto para trazer o design para o Domínio 3.")
        
        # Heurística de Fissuração
        wk = design_data.get('crack_width', {}).get('wk_mm', 0)
        wk_limit = design_data.get('crack_width', {}).get('limit_mm', 0.3)
        if wk > wk_limit * 0.9:
            suggestions.append("🔍 Abertura de fissuras próxima ao limite. Considere usar barras de menor bitola e menor espaçamento para melhorar a distribuição de tensões.")

        # Heurística de Eficiência (Vibe Check)
        if not suggestions:
            suggestions.append("✅ Design eficiente: As tensões e deformações estão bem distribuídas.")
            
        return suggestions

    def analyze_radier(self, analysis_result: dict) -> List[str]:
        suggestions = []
        
        # Heurística de Pressão no Solo
        max_press = analysis_result.get('max_pressure_kpa', 0)
        adm_press = analysis_result.get('adm_pressure_kpa', 1e9)
        
        if max_press > adm_press:
            suggestions.append("🚨 Pressão no solo excede a capacidade de carga. Considere aumentar as dimensões do Radier ou utilizar estacas de reforço.")
        elif max_press < adm_press * 0.3:
            suggestions.append("💡 Radier superdimensionado: A pressão no solo está muito baixa. É possível reduzir a espessura para economizar concreto.")

        # Heurística de Punção
        punching = analysis_result.get('punching_status', 'OK')
        if punching != 'OK':
            suggestions.append("⚠️ Falha por punção detectada. Considere o uso de capitéis ou armadura de punção (studs) para evitar o aumento da espessura total.")

        return suggestions

    def get_efficiency_score(self, design_data: dict) -> float:
        """Retorna uma nota de 0 a 10 para a eficiência da estrutura."""
        # Lógica simplificada: inicia em 10 e penaliza ineficiências
        score = 10.0
        # Exemplo: se houver sugestões críticas, reduz score
        # ... logic ...
        return round(score, 1)

if __name__ == "__main__":
    copilot = AICopilot()
    sample_beam = {
        'deflection': {'status': 'EXCEDE'},
        'flexure_bottom': {'domain': '3'},
        'crack_width': {'wk_mm': 0.1, 'limit_mm': 0.3}
    }
    print("AI COPILOT ANALYSIS:")
    for s in copilot.analyze_beam(sample_beam):
        print(f"- {s}")
