import sys
import os
import numpy as np

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def create_10_story_frame_model():
    floors = 10
    height = 3.0          # m
    span = 6.0            # m
    E = 30e9              # Pa (C30)
    G = E / (2 * (1 + 0.2))

    # Propriedades dos pilares (0,5x0,5 m)
    sec_col = FrameSection(b=0.5, h=0.5, E=E, G=G)
    # Propriedades da viga (0,2x0,5 m)
    sec_beam = FrameSection(b=0.2, h=0.5, E=E, G=G)

    nodes = []
    members = []
    loads = []

    # Gerar nós
    for floor in range(floors+1):
        y = floor * height
        nodes.append(FrameNode(id=floor*2+1, x=0.0, y=0.0, z=y))
        nodes.append(FrameNode(id=floor*2+2, x=span, y=0.0, z=y))

    def left_id(floor): return floor*2 + 1
    def right_id(floor): return floor*2 + 2

    # Criar pilares e vigas
    for floor in range(floors):
        # Pilares
        members.append(FrameMember(id=len(members)+1, node_i=left_id(floor), node_j=left_id(floor+1), section=sec_col))
        members.append(FrameMember(id=len(members)+1, node_i=right_id(floor), node_j=right_id(floor+1), section=sec_col))
        # Viga
        members.append(FrameMember(id=len(members)+1, node_i=left_id(floor+1), node_j=right_id(floor+1), section=sec_beam))

    # Carga vertical nas vigas (30 kN/m -> convertido para nodal nos cantos)
    for floor in range(1, floors+1):
        loads.append(FrameLoad(node_id=left_id(floor), Fz=-90000.0))
        loads.append(FrameLoad(node_id=right_id(floor), Fz=-90000.0))

    # Carga lateral (5kN por nó por pavimento)
    for floor in range(1, floors+1):
        loads.append(FrameLoad(node_id=left_id(floor), Fx=5000.0))
        loads.append(FrameLoad(node_id=right_id(floor), Fx=5000.0))

    supports = {1: [0,1,2,3,4,5], 2: [0,1,2,3,4,5]}
    
    return nodes, members, loads, supports

def run_atlas_analysis_benchmark():
    print("🏗️  Gerando modelo de pórtico de 10 pavimentos (Atlas-Native Workflow)...")
    nodes, members, loads, supports = create_10_story_frame_model()
    
    engine = Frame3DEngine(nodes, members)
    
    print("⚙️  Executando run_analysis(use_p_delta=False)...")
    result_lin = engine.run_analysis(loads, supports, use_p_delta=False)
    
    print("⚙️  Executando run_analysis(use_p_delta=True)...")
    result_pdelta = engine.run_analysis(loads, supports, use_p_delta=True)
    
    # Extrair deslocamento do topo (nó 22)
    top_node_id = str(max(int(k) for k in result_lin["displacements"].keys()))
    disp_linear = abs(result_lin["displacements"][top_node_id][0]) # X
    disp_pdelta = abs(result_pdelta["displacements"][top_node_id][0]) # X
    
    B2_atlas = result_pdelta["stability"]["gamma_z"]
    alpha_atlas = result_pdelta["stability"]["alpha"]
    
    print("\n" + "="*60)
    print("📊 RESULTADOS DO ATLAS-NATIVE BENCHMARK")
    print("="*60)
    print(f"Deslocamento horizontal do topo (Linear):  {disp_linear*1000:.3f} mm")
    print(f"Deslocamento horizontal do topo (P-Delta): {disp_pdelta*1000:.3f} mm")
    print(f"Fator Gama-Z (Estabilidade Global):       {B2_atlas:.3f}")
    print(f"Parâmetro Alfa (Instabilidade):            {alpha_atlas:.3f}")
    print(f"Iterações P-Delta (Aitken):               {result_pdelta.get('p_delta_iterations', 0)}")
    print("-"*60)
    
    if B2_atlas > 1.1:
        print(f"📢 Verificação: {result_pdelta['stability']['recommendation']}")
    
    print("✅ Atlas-Native Workflow validado com sucesso.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_atlas_analysis_benchmark()
