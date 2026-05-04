"""
autonomous_agent.py — Agente de Design Estrutural Autônomo (M5-PhD).
Implementa o loop Baton-Passing: Análise -> Crítica -> Modificação -> Re-cálculo.
"""
from typing import List, Dict, Any
import time
from radier_lab_v24 import LabConfig, run_full_pipeline_demo
from ai_copilot import AICopilot

class AutonomousDesignAgent:
    def __init__(self, target_cost: float = None):
        self.target_cost = target_cost
        self.history = []
        self.copilot = AICopilot()

    def run_design_cycle(self, initial_config: LabConfig, max_iterations: int = 5):
        current_config = initial_config
        print(f"🤖 Iniciando Ciclo Autônomo para: {initial_config.base_name}")
        
        for i in range(max_iterations):
            print(f"\n🔄 Iteração {i+1}/{max_iterations}...")
            
            # 1. Execução do Engine
            start_time = time.time()
            results = run_full_pipeline_demo(current_config)
            duration = time.time() - start_time
            
            # 2. Coleta de Diagnóstico do Copilot
            diagnosis = results.get('ai_copilot_diagnosis', [])
            w_max = results.get('w_max_mm', 0)
            
            # 3. Log de Estado
            state = {
                "iteration": i + 1,
                "h": current_config.h,
                "fck": current_config.fck,
                "w_max": w_max,
                "diagnosis": diagnosis,
                "duration": duration
            }
            self.history.append(state)
            
            print(f"   [RESULTADO] h={current_config.h}m | w_max={w_max:.2f}mm")
            
            # 4. Critério de Parada
            if "✅ Design eficiente" in diagnosis or not diagnosis:
                print("✨ Design Otimizado Atingido!")
                break
                
            # 5. Modificação Inteligente (Heurística baseada no Copilot)
            # No PhD Real, usaríamos um LLM ou GA aqui. 
            # Aqui simulamos a tomada de decisão do agente:
            new_h = current_config.h
            new_fck = current_config.fck
            
            if any("Flecha excessiva" in d for d in diagnosis) or w_max > 30:
                new_h += 0.05 # Aumenta espessura
            elif any("superdimensionado" in d for d in diagnosis) and w_max < 15:
                new_h -= 0.05 # Reduz espessura para economizar
                
            if new_h == current_config.h: # Se h não mudou, tenta FCK
                if any("super-armada" in d for d in diagnosis):
                    new_fck += 5
            
            # Atualiza config para próxima rodada
            current_config.h = round(new_h, 2)
            current_config.fck = new_fck
            current_config.base_name = f"{initial_config.base_name}_iter_{i+1}"
            
        return {
            "final_config": current_config,
            "history": self.history,
            "total_iterations": len(self.history)
        }

if __name__ == "__main__":
    from radier_lab_v24 import LabConfig
    cfg = LabConfig(Lx=20, Ly=20, h=0.40, kv=30e6, fck=25, base_name="phd_auto_test")
    agent = AutonomousDesignAgent()
    result = agent.run_design_cycle(cfg)
    print("\n🏁 HISTÓRICO DO AGENTE:")
    for h in result['history']:
        print(f"Iter {h['iteration']}: h={h['h']} -> w_max={h['w_max']:.2f}")
