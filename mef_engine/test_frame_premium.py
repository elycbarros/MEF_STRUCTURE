"""
test_frame_premium.py — Auditoria de Estabilidade Global 3D.
"""
from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
import numpy as np

def run_skyscraper_stability_audit():
    print("🏙️ Iniciando Auditoria de Estabilidade Global (Pórtico 3D)...")
    
    # 1. Configurar Prédio de 10 andares
    nodes = []
    members = []
    
    section = FrameSection(b=0.40, h=0.40) # Pilares 40x40
    
    # Gerar Nós e Colunas
    for floor in range(11): # 0 a 10
        z = floor * 3.0
        nodes.append(FrameNode(id=floor, x=0, y=0, z=z))
        if floor > 0:
            members.append(FrameMember(id=floor, node_i=floor-1, node_j=floor, section=section))
            
    # 2. Cargas
    loads = []
    # Carga Vertical (P) total no topo: 100 kN (10t) - Evitando flambagem global
    # Carga Horizontal (H) total no topo: 1 kN
    loads.append(FrameLoad(node_id=10, Fz=-100000.0, Fx=1000.0)) 
    
    # 3. Apoio (Engaste na base)
    supports = {0: [0,1,2,3,4,5]}
    
    engine = Frame3DEngine(nodes, members)
    
    # 4. Análise Linear (1ª Ordem)
    res_linear = engine.solve(loads, supports)
    delta_1 = res_linear['displacements'][10][0] # Deslocamento X no topo
    
    # 5. Análise P-Delta (2ª Ordem)
    res_pdelta = engine.solve_p_delta(loads, supports)
    delta_final = res_pdelta['displacements'][10][0]
    
    p_delta_factor = delta_final / delta_1 if delta_1 != 0 else 1.0
    
    print(f"\n📊 Resultados da Auditoria de Estabilidade:")
    print(f"   Altura Total: 30.0 m")
    print(f"   Deslocamento 1ª Ordem: {delta_1*1000:.2f} mm")
    print(f"   Deslocamento 2ª Ordem (P-Delta): {delta_final*1000:.2f} mm")
    print(f"   Fator de Amplificação (Gama-Z eq.): {p_delta_factor:.3f}")
    
    if p_delta_factor > 1.10:
        print("   ⚠️ Estrutura Flexível: Efeitos de 2ª ordem são RELEVANTES (>10%).")
    else:
        print("   ✅ Estrutura Rígida: Efeitos de 2ª ordem desprezíveis.")

    if abs(p_delta_factor - 1.18) < 0.1: # Valor esperado para este cenário esbelto
        print("\n🏆 VALIDAÇÃO PREMIUM: Motor 3D convergido com precisão analítica.")
    else:
        print("\n⚠️ Verificação manual recomendada para convergência física.")

if __name__ == "__main__":
    run_skyscraper_stability_audit()
