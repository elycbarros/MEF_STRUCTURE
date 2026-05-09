import json
import os
import numpy as np
import sys
from pathlib import Path

# Forçar CWD para a raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "mef_engine"))

from mef_engine.frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def run_pdelta_benchmark():
    # Carregar referência usando caminho absoluto
    ref_path = PROJECT_ROOT / "reference_results" / "pdelta_portico_10_pav.json"
    with open(ref_path, 'r') as f:
        ref_data = json.load(f)
    
    print(f"--- VALIDANDO: {ref_data['benchmark']} ---")
    
    # Criar modelo do pórtico (simplificado para o teste)
    nodes = []
    members = []
    # Base
    nodes.append(FrameNode(id=1, x=0, y=0, z=0))
    nodes.append(FrameNode(id=2, x=6, y=0, z=0))
    
    story_h = 3.0
    section = FrameSection(b=0.2, h=0.4, E=210e6, G=80e6) # Simulado
    
    curr_node = 3
    for s in range(1, 11):
        z = s * story_h
        nodes.append(FrameNode(id=curr_node, x=0, y=0, z=z))
        nodes.append(FrameNode(id=curr_node+1, x=6, y=0, z=z))
        
        # Pilares
        members.append(FrameMember(id=len(members)+1, node_i=curr_node-2, node_j=curr_node, section=section))
        members.append(FrameMember(id=len(members)+1, node_i=curr_node-1, node_j=curr_node+1, section=section))
        
        # Vigas
        members.append(FrameMember(id=len(members)+1, node_i=curr_node, node_j=curr_node+1, section=section))
        
        curr_node += 2
    
    top_node_id = curr_node - 2
    loads = [FrameLoad(node_id=top_node_id, Fx=10.0)] # Carga de topo
    supports = {1: [0,1,2,3,4,5], 2: [0,1,2,3,4,5]}
    
    # Executar Atlas P-Delta
    engine = Frame3DEngine(nodes=nodes, members=members)
    
    print("\n--- ANALISE LINEAR ---")
    res_lin_py = engine.solve(loads=loads, supports=supports, use_rust=False)
    res_lin_rs = engine.solve(loads=loads, supports=supports, use_rust=True)
    print(f"Topo Linear (Python): {abs(res_lin_py['displacements'][top_node_id][0])*1000:.4f} mm")
    print(f"Topo Linear (Rust):   {abs(res_lin_rs['displacements'][top_node_id][0])*1000:.4f} mm")

    print("\n--- ANALISE P-DELTA (2a Ordem) ---")
    # Para P-Delta o motor alterna entre assemble e solve. 
    # Precisamos garantir que ele use Rust em cada iteracao se solicitado.
    res_pd_py = engine.solve_p_delta(loads, supports) 
    # Nota: solve_p_delta chama solve() internamente. 
    # Como len(members) > 20 no teste (10 andares = 30 membros), ele deve usar Rust automaticamente se RUST_AVAILABLE.
    
    print(f"Topo P-Delta (Final): {abs(res_pd_py['displacements'][top_node_id][0])*1000:.4f} mm")
    
    amplificacao = abs(res_pd_py['displacements'][top_node_id][0]) / abs(res_lin_py['displacements'][top_node_id][0])
    print(f"Fator de Amplificacao: {amplificacao:.4f}")

    if abs(res_lin_py['displacements'][top_node_id][0] - res_lin_rs['displacements'][top_node_id][0]) < 1e-7:
        print("\n✅ PARIDADE RUST-PYTHON: OK")
    else:
        print("\n❌ FALHA NA PARIDADE RUST-PYTHON")

if __name__ == "__main__":
    run_pdelta_benchmark()
