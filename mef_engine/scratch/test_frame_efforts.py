from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
import numpy as np

def test_efforts_and_equilibrium():
    print("🚀 Testando Esforços e Equilíbrio Global...")
    
    # Simples viga bi-engastada de 5m
    # Nó 0 (0,0,0) - Nó 1 (5,0,0)
    nodes = [
        FrameNode(id=0, x=0, y=0, z=0),
        FrameNode(id=1, x=5, y=0, z=0)
    ]
    
    section = FrameSection(b=0.20, h=0.50) # 20x50
    members = [
        FrameMember(id=0, node_i=0, node_j=1, section=section)
    ]
    
    # Vamos fazer um console de 5m.
    loads = [
        FrameLoad(node_id=1, Fz=-10000.0) # 10 kN para baixo
    ]
    
    supports = {0: [0,1,2,3,4,5]} # Engaste no nó 0
    
    engine = Frame3DEngine(nodes, members)
    res = engine.solve(loads, supports)
    
    # 1. Esforços
    efforts = engine.get_member_efforts(res['displacements'])
    eff0 = efforts[0]
    
    print(f"\nDeslocamento Nó 1: {res['displacements'][1]}")
    
    print(f"\nEsforços na Barra 0 (Local):")
    # Vamos imprimir o f_loc bruto pra ver
    T, L = engine._get_transformation(members[0])
    u_e = np.concatenate([res['displacements'][0], res['displacements'][1]])
    f_loc = engine._get_k_local(members[0], L) @ (T @ u_e)
    print(f"  f_loc raw: {f_loc}")
    
    print(f"  Nó i (Engaste): N={eff0['i']['N']:.2f}, Vy={eff0['i']['Vy']:.2f}, Vz={eff0['i']['Vz']:.2f}, T={eff0['i']['T']:.2f}, My={eff0['i']['My']:.2f}, Mz={eff0['i']['Mz']:.2f}")
    print(f"  Nó j (Livre):   N={eff0['j']['N']:.2f}, Vy={eff0['j']['Vy']:.2f}, Vz={eff0['j']['Vz']:.2f}, T={eff0['j']['T']:.2f}, My={eff0['j']['My']:.2f}, Mz={eff0['j']['Mz']:.2f}")
    
    # 2. Equilíbrio
    eq = engine.check_equilibrium(loads, res['displacements'], supports)
    print(f"\nAuditoria de Equilíbrio:")
    print(f"  Cargas Aplicadas (kN): {eq['sum_applied_kN']}")
    print(f"  Reações (kN):         {eq['sum_reactions_kN']}")
    print(f"  Erro (kN):            {eq['equilibrium_error_kN']}")
    print(f"  Status:               {'✅ OK' if eq['is_equilibrated'] else '❌ FALHA'}")

if __name__ == "__main__":
    test_efforts_and_equilibrium()
