import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad

def simulate_vigas_q31():
    print("Iniciando Simulação da Questão 31 no Modo Vigas/Pórtico...")
    
    # Mesmos nós da Questão 31
    nodes = [
        FrameNode(id=0, x=0.0, y=0.0, z=0.0),
        FrameNode(id=1, x=3.0, y=0.0, z=0.0),
        FrameNode(id=2, x=0.0, y=0.0, z=3.0),
        FrameNode(id=3, x=3.0, y=0.0, z=3.0),
        FrameNode(id=4, x=0.0, y=0.0, z=6.0),
        FrameNode(id=5, x=3.0, y=0.0, z=6.0),
    ]
    
    # Seção transversal típica de concreto armado (ex: 20x50 cm) para pórtico rígido
    section = FrameSection(b=0.20, h=0.50, E=2.5e10)
    
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
    
    # Cargas da Questão 31
    loads = [
        FrameLoad(node_id=4, Fx=20000.0),  # 20 kN horizontal
        FrameLoad(node_id=5, Fz=-20000.0), # 20 kN vertical
    ]
    
    # Apoios restritos nos eixos transladados e de torção/fora-do-plano para estabilidade em 3D
    # Bloqueamos Ux(0), Uy(1), Uz(2), Rx(3), Rz(5) e deixamos Ry(4) livre para flexão.
    supports = {
        0: [0, 1, 2, 3, 5], # Apoio Fixo (Apoio de 2º Gênero em 2D)
        1: [1, 2, 3, 5]     # Apoio Móvel (Apoio de 1º Gênero em 2D, livre em X)
    }
    
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    engine.is_truss = False # Modo Pórtico/Vigas (Conexões rígidas!)
    
    res = engine.solve(loads, supports, reduce_stiffness=False)
    efforts = engine.get_member_efforts(res["displacements"])
    equilibrium = engine.check_equilibrium(loads, res["displacements"], supports)
    
    print("\n==================================================")
    print("      RESULTADOS MODO PÓRTICO (CONEXÃO RÍGIDA)")
    print("==================================================")
    
    print("\n--- Reações de Apoio (em kN / kNm) ---")
    for nid, r in equilibrium["reactions"].items():
        print(f"Nó {nid}: HA={r[0]:.2f} kN, VA={r[2]:.2f} kN, MA_y={r[4]:.2f} kNm")
        
    print("\n--- Esforços nos Membros (My pedagógico nos nós i e j) ---")
    for mid, eff in efforts.items():
        m = members[mid]
        # Mapeamos Mz local para My pedagógico
        my_i = eff["i"]["Mz"]
        my_j = eff["j"]["Mz"]
        n_i = eff["i"]["N"]
        vy_i = eff["i"]["Vy"]
        print(f"Barra {mid} (Nó {m.node_i} -> {m.node_j}): N={n_i:.2f} kN, V={vy_i:.2f} kN, M_i={my_i:.2f} kNm, M_j={my_j:.2f} kNm")
        
    print("==================================================\n")

if __name__ == '__main__':
    simulate_vigas_q31()
