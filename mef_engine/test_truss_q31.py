import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def test_q31():
    # Nodes:
    # 0: (0,0,0) - Pinned
    # 1: (3,0,0) - Roller
    # 2: (0,0,3)
    # 3: (3,0,3)
    # 4: (0,0,6)
    # 5: (3,0,6)
    nodes = [
        FrameNode(id=0, x=0.0, y=0.0, z=0.0),
        FrameNode(id=1, x=3.0, y=0.0, z=0.0),
        FrameNode(id=2, x=0.0, y=0.0, z=3.0),
        FrameNode(id=3, x=3.0, y=0.0, z=3.0),
        FrameNode(id=4, x=0.0, y=0.0, z=6.0),
        FrameNode(id=5, x=3.0, y=0.0, z=6.0),
    ]
    
    section = FrameSection(b=0.1, h=0.1, E=2.1e11) # Aço padrão
    members = [
        # Horizontais
        FrameMember(id=0, node_i=0, node_j=1, section=section),
        FrameMember(id=1, node_i=2, node_j=3, section=section),
        FrameMember(id=2, node_i=4, node_j=5, section=section),
        # Verticais
        FrameMember(id=3, node_i=0, node_j=2, section=section),
        FrameMember(id=4, node_i=2, node_j=4, section=section),
        FrameMember(id=5, node_i=1, node_j=3, section=section),
        FrameMember(id=6, node_i=3, node_j=5, section=section),
        # Diagonais
        FrameMember(id=7, node_i=0, node_j=3, section=section),
        FrameMember(id=8, node_i=2, node_j=5, section=section),
    ]
    
    loads = [
        FrameLoad(node_id=4, Fx=20000.0),  # 20 kN horizontal p/ direita
        FrameLoad(node_id=5, Fz=-20000.0), # 20 kN vertical p/ baixo
    ]
    
    # Condições de apoio
    supports = {
        0: [0, 1, 2, 3, 4, 5], # Apoio Fixo em 2D (bloqueia X e Z) + todos os DOFs fora do plano/rotação
        1: [1, 2, 3, 4, 5]     # Apoio Móvel em 2D (bloqueia Z, livre em X)
    }
    
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    engine.is_truss = True
    
    res = engine.solve(loads, supports)
    efforts = engine.get_member_efforts(res["displacements"])
    eq = engine.check_equilibrium(loads, res["displacements"], supports)
    
    print("\n==================================================")
    print("           RESULTADOS DA QUESTÃO 31")
    print("==================================================")
    
    print("\n--- Reações de Apoio (em kN) ---")
    for nid, r in eq["reactions"].items():
        print(f"Nó {nid}: HA={r[0]:.2f} kN, VA={r[2]:.2f} kN")
        
    print("\n--- Esforços Axiais nas Barras (em kN) ---")
    for mid, eff in efforts.items():
        m = members[mid]
        print(f"Barra {mid} (Nó {m.node_i} -> {m.node_j}): N={eff['i']['N']:.2f} kN")
    print("==================================================\n")

if __name__ == "__main__":
    test_q31()
