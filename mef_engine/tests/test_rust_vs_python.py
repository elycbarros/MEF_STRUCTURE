import sys
import os
import numpy as np
import time

# Adicionar o diretório atual ao path para importar frame_engine
sys.path.append(os.getcwd())

from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def generate_simple_frame(n_stories=2):
    """Gera um pórtico simples para teste de paridade."""
    nodes = []
    members = []
    section = FrameSection(b=0.2, h=0.5, E=2.5e10, G=1.0e10)
    
    # Nós (4 por pavimento)
    for s in range(n_stories + 1):
        z = s * 3.0
        nodes.append(FrameNode(id=s*4+1, x=0, y=0, z=z))
        nodes.append(FrameNode(id=s*4+2, x=5, y=0, z=z))
        nodes.append(FrameNode(id=s*4+3, x=5, y=5, z=z))
        nodes.append(FrameNode(id=s*4+4, x=0, y=5, z=z))
        
    # Membros (Pilares e Vigas)
    mid = 1
    for s in range(n_stories):
        # Pilares
        for i in range(1, 5):
            members.append(FrameMember(id=mid, node_i=s*4+i, node_j=(s+1)*4+i, section=section))
            mid += 1
        # Vigas (no topo do pavimento s+1)
        base = (s+1)*4
        members.append(FrameMember(id=mid, node_i=base+1, node_j=base+2, section=section))
        mid += 1
        members.append(FrameMember(id=mid, node_i=base+2, node_j=base+3, section=section))
        mid += 1
        members.append(FrameMember(id=mid, node_i=base+3, node_j=base+4, section=section))
        mid += 1
        members.append(FrameMember(id=mid, node_i=base+4, node_j=base+1, section=section))
        mid += 1
        
    # Cargas (Vento no topo)
    loads = [FrameLoad(node_id=(n_stories)*4+1, Fx=10000.0)]
    
    # Apoios (Engaste na base)
    supports = {1: [0,1,2,3,4,5], 2: [0,1,2,3,4,5], 3: [0,1,2,3,4,5], 4: [0,1,2,3,4,5]}
    
    return nodes, members, loads, supports

def run_comparison():
    print("🚀 Iniciando Teste de Paridade: Python vs Rust")
    nodes, members, loads, supports = generate_simple_frame(n_stories=5)
    
    engine = Frame3DEngine(nodes, members)
    
    # 1. Resolver com Python
    t0 = time.time()
    res_py = engine.solve(loads, supports, use_rust=False)
    t_py = time.time() - t0
    print(f"⏱️  Python Assembly: {t_py:.4f}s")
    
    # 2. Resolver com Rust
    t0 = time.time()
    res_rs = engine.solve(loads, supports, use_rust=True)
    t_rs = time.time() - t0
    print(f"⏱️  Rust Assembly:   {t_rs:.4f}s")
    
    # 3. Comparação Numérica
    u_py = res_py['U_raw']
    u_rs = res_rs['U_raw']
    
    print(f"📊 Resíduo Python: {res_py['residual']:.2e}")
    print(f"📊 Resíduo Rust:   {res_rs['residual']:.2e}")
    
    diff = np.max(np.abs(u_py - u_rs))
    print(f"🔍 Diferença Máxima: {diff:.2e}")
    
    if diff < 1e-7:
        print("✅ SUCESSO: Os resultados são numericamente idênticos.")
    else:
        print("❌ FALHA: Diferença acima da tolerância.")
        sys.exit(1)

    # 4. Benchmark de Escala
    print("\n⚡ Benchmark de Escala (500 Pavimentos)...")
    nodes_lg, members_lg, loads_lg, supports_lg = generate_simple_frame(n_stories=500)
    engine_lg = Frame3DEngine(nodes_lg, members_lg)
    
    t0 = time.time()
    engine_lg.solve(loads_lg, supports_lg, use_rust=False)
    t_py_lg = time.time() - t0
    print(f"⏱️  Python (Scale): {t_py_lg:.4f}s")
    
    t0 = time.time()
    engine_lg.solve(loads_lg, supports_lg, use_rust=True)
    t_rs_lg = time.time() - t0
    print(f"⏱️  Rust (Scale):   {t_rs_lg:.4f}s")
    
    speedup = t_py_lg / t_rs_lg if t_rs_lg > 0 else 0
    print(f"📈 Speedup: {speedup:.1f}x")

if __name__ == "__main__":
    run_comparison()
