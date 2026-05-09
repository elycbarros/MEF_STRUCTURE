import time
import os
import sys
from pathlib import Path

# Forçar CWD para a raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "mef_engine"))

from mef_engine.frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

try:
    import psutil
except ImportError:
    print("Aviso: 'psutil' não instalado. Medição de memória será ignorada.")
    psutil = None

def create_frame_model(n_stories):
    nodes = []
    members = []
    story_h = 3.0
    section = FrameSection(b=0.2, h=0.4, E=210e6, G=80e6)
    
    # Base
    nodes.append(FrameNode(id=1, x=0, y=0, z=0))
    nodes.append(FrameNode(id=2, x=6, y=0, z=0))
    
    curr_node = 3
    for s in range(1, n_stories + 1):
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
    loads = [FrameLoad(node_id=top_node_id, Fx=10.0)]
    supports = {1: [0,1,2,3,4,5], 2: [0,1,2,3,4,5]}
    
    return {
        "nodes": nodes,
        "members": members,
        "loads": loads,
        "supports": supports
    }

def run_scale_test():
    print("="*60)
    print("ATLAS STRUCTURAL ENGINE - TESTE DE ESCALA E PERFORMANCE")
    print("="*60)
    
    for n_stories in [5, 10, 20, 30, 40, 50]:
        model_data = create_frame_model(n_stories)
        engine = Frame3DEngine(nodes=model_data["nodes"], members=model_data["members"])
        
        ndof = engine.ndof
        solver_type = "RUST NATIVE (DENSE)" if ndof <= 2000 else "SCIPY (SPARSE)"
        
        start = time.time()
        # Executar análise linear simples para teste de carga
        res = engine.solve(loads=model_data["loads"], supports=model_data["supports"], use_rust=True)
        elapsed = time.time() - start
        
        mem_mb = 0
        if psutil:
            mem_mb = psutil.Process().memory_info().rss / 1024**2
            
        print(f"{n_stories:2} andares ({ndof:4} DOF) | Solver: {solver_type:<20} | Tempo: {elapsed:5.3f}s | Memória: {mem_mb:4.0f} MB")

if __name__ == "__main__":
    run_scale_test()
