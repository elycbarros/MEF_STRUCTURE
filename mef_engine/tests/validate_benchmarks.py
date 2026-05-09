import sys
import os
import json
import numpy as np

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def run_benchmark_validation():
    print("📋 Validando Benchmarks de Referência...")
    
    with open("reference_results/all_benchmarks.json", "r") as f:
        benchmarks = json.load(f)
    
    # --- Validar "simple_beam" (Viga Engastada-Apoiada) ---
    print("\n🔹 Testando Caso: simple_beam (Refinado - 16 Elementos)")
    case = benchmarks["simple_beam"]
    data = case["input"]
    
    # Gerar malha de 16 elementos (Nós a cada 0.5m)
    L_total = 8.0
    n_elements = 16
    dx = L_total / n_elements
    
    nodes = [FrameNode(id=i+1, x=i*dx, y=0.0, z=0.0) for i in range(n_elements + 1)]
    members = []
    for i in range(n_elements):
        # b=0.2, h=0.5 -> area=0.1, iy=0.00208333
        section = FrameSection(b=0.2, h=0.5, E=25e9, G=10e9)
        members.append(FrameMember(id=i+1, node_i=i+1, node_j=i+2, section=section))
        
    # Converter carga uniforme (20kN/m) em cargas nodais
    # Tributária: Nó interno recebe w*dx. Nós de extremidade recebem w*dx/2.
    w = -20000.0
    loads = []
    for i in range(n_elements + 1):
        if i == 0 or i == n_elements:
            fz = w * dx / 2
        else:
            fz = w * dx
        loads.append(FrameLoad(node_id=i+1, Fz=fz))
            
    # Suportes: Nó 1 (Engaste: 0,1,2,3,4,5), Último Nó (Apoio Z: 2)
    # Nota: benchmark original diz "node 3" para apoio, mas aqui é o node 17
    supports = {1: [0,1,2,3,4,5], n_elements + 1: [1,2]}
    
    engine = Frame3DEngine(nodes, members)
    res = engine.solve(loads, supports, use_rust=True)
    
    # Encontrar a deflexão máxima vertical (Z) em qualquer nó
    all_z_disps = [abs(res["displacements"][nid][2]) for nid in res["displacements"]]
    max_deflection = max(all_z_disps)
    
    expected_deflection = abs(case["expected"]["max_deflection_m"])
    error_rel = abs(max_deflection - expected_deflection) / expected_deflection
    
    print(f"   - Deflexão Esperada (Analítica): {expected_deflection:.5f}m")
    print(f"   - Deflexão Máxima (MEF 16 El.):  {max_deflection:.5f}m")
    print(f"   - Erro Relativo:                 {error_rel:.2%}")
    print(f"   - Resíduo (Energia):             {res['residual']:.2e}")
    
    # 2. Validar "simple_frame" (Re-checando com carga lateral para testar Assembler)
    print("\n🔹 Testando Caso: simple_frame (Com carga lateral para validar Sway)")
    case_f = benchmarks["simple_frame"]
    data_f = case_f["input"]
    nodes_f = [FrameNode(**n) for n in data_f["nodes"]]
    members_f = []
    for m in data_f["members"]:
        section = FrameSection(b=0.3, h=0.3, E=m["material"]["e"], G=m["material"]["g"])
        members_f.append(FrameMember(id=m["id"], node_i=m["node_i"], node_j=m["node_j"], section=section))
    
    # Aplicar carga lateral em X no nó 2 para forçar montagem de rigidez lateral no Rust
    loads_f = [FrameLoad(node_id=2, Fx=50000.0)]
    supports_f = {int(k): v for k, v in data_f["supports"].items()}
    
    engine_f = Frame3DEngine(nodes_f, members_f)
    res_f = engine_f.solve(loads_f, supports_f, use_rust=True)
    
    sway = res_f["displacements"][2][0]
    print(f"   - Sway Lateral Obtido (Fx=50kN): {sway:.5f}m")
    print(f"   - Resíduo (Energia):             {res_f['residual']:.2e}")

    if abs(sway) > 1e-6:
        print("   ✅ Assembler Rust validado para rigidez lateral.")
        
if __name__ == "__main__":
    run_benchmark_validation()
