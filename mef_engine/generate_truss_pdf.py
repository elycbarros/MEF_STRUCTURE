import os
import sys
import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from professional_pdf import generate_professional_memorial

def run_q31_simulation_and_pdf():
    print("Iniciando simulação 2D/3D Treliça para a Questão 31...")
    
    # 1. Definir Nós
    # A (0,0,0), B (3,0,0), C (0,0,3), D (3,0,3), E (0,0,6), F (3,0,6)
    nodes = [
        FrameNode(id=0, x=0.0, y=0.0, z=0.0), # A
        FrameNode(id=1, x=3.0, y=0.0, z=0.0), # B
        FrameNode(id=2, x=0.0, y=0.0, z=3.0), # C
        FrameNode(id=3, x=3.0, y=0.0, z=3.0), # D
        FrameNode(id=4, x=0.0, y=0.0, z=6.0), # E
        FrameNode(id=5, x=3.0, y=0.0, z=6.0)  # F
    ]
    
    # 2. Definir Membros (Barras)
    section = FrameSection(b=0.1, h=0.1, E=2.1e11) # Aço padrão
    members = [
        # Horizontais
        FrameMember(id=0, node_i=0, node_j=1, section=section), # AB
        FrameMember(id=1, node_i=2, node_j=3, section=section), # CD
        FrameMember(id=2, node_i=4, node_j=5, section=section), # EF
        # Verticais
        FrameMember(id=3, node_i=0, node_j=2, section=section), # AC
        FrameMember(id=4, node_i=2, node_j=4, section=section), # CE
        FrameMember(id=5, node_i=1, node_j=3, section=section), # BD
        FrameMember(id=6, node_i=3, node_j=5, section=section), # DF
        # Diagonais
        FrameMember(id=7, node_i=0, node_j=3, section=section), # AD
        FrameMember(id=8, node_i=2, node_j=5, section=section)  # CF
    ]
    
    # 3. Definir Cargas
    # 20 kN horizontal p/ direita em E (4); 20 kN vertical p/ baixo em F (5)
    loads = [
        FrameLoad(node_id=4, Fx=20000.0),
        FrameLoad(node_id=5, Fz=-20000.0)
    ]
    
    # 4. Definir Apoios
    # Bloqueamos Ux, Uy, Uz, Rx, Ry, Rz fora do plano para estabilidade numérica 3D
    supports = {
        0: [0, 1, 2, 3, 4, 5], # Apoio Fixo A
        1: [1, 2, 3, 4, 5]     # Apoio Móvel B
    }
    
    # 5. Instanciar Motor
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    engine.is_truss = True
    
    # 6. Resolver
    res = engine.solve(loads, supports)
    
    # 7. Obter esforços internos e equilíbrio
    efforts = engine.get_member_efforts(res["displacements"])
    equilibrium = engine.check_equilibrium(loads, res["displacements"], supports)
    
    # 8. Formatar dados
    model_3d_payload = {
        "is_truss": True,
        "nodes": [
            {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 1, "x": 3.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 0.0, "y": 0.0, "z": 3.0},
            {"id": 3, "x": 3.0, "y": 0.0, "z": 3.0},
            {"id": 4, "x": 0.0, "y": 0.0, "z": 6.0},
            {"id": 5, "x": 3.0, "y": 0.0, "z": 6.0}
        ],
        "members": [
            {"id": 0, "node_i": 0, "node_j": 1, "section": {"b": 0.1, "h": 0.1}},
            {"id": 1, "node_i": 2, "node_j": 3, "section": {"b": 0.1, "h": 0.1}},
            {"id": 2, "node_i": 4, "node_j": 5, "section": {"b": 0.1, "h": 0.1}},
            {"id": 3, "node_i": 0, "node_j": 2, "section": {"b": 0.1, "h": 0.1}},
            {"id": 4, "node_i": 2, "node_j": 4, "section": {"b": 0.1, "h": 0.1}},
            {"id": 5, "node_i": 1, "node_j": 3, "section": {"b": 0.1, "h": 0.1}},
            {"id": 6, "node_i": 3, "node_j": 5, "section": {"b": 0.1, "h": 0.1}},
            {"id": 7, "node_i": 0, "node_j": 3, "section": {"b": 0.1, "h": 0.1}},
            {"id": 8, "node_i": 2, "node_j": 5, "section": {"b": 0.1, "h": 0.1}}
        ],
        "supports": {
            "0": [0, 1, 2, 3, 4, 5],
            "1": [1, 2, 3, 4, 5]
        },
        "loads": [
            {"node_id": 4, "fx": 20.0},
            {"node_id": 5, "fz": -20.0}
        ]
    }
    
    formatted_disp = {}
    for nid, d_vec in res["displacements"].items():
        formatted_disp[str(nid)] = [float(v) for v in d_vec]
        
    formatted_efforts = {}
    for mid, eff in efforts.items():
        formatted_efforts[str(mid)] = {
            "i": {
                "N": float(eff["i"]["N"])
            }
        }
        
    formatted_reac = {}
    for nid, r_vec in equilibrium["reactions"].items():
        formatted_reac[str(nid)] = [float(v) for v in r_vec]
        
    formatted_equilibrium = {
        "reactions": formatted_reac,
        "sum_applied_kN_m": [float(v) for v in equilibrium["sum_applied_kN_m"]],
        "sum_reactions_kN_m": [float(v) for v in equilibrium["sum_reactions_kN_m"]],
        "equilibrium_error_kN_m": [float(v) for v in equilibrium["equilibrium_error_kN_m"]],
        "is_equilibrated": bool(equilibrium["is_equilibrated"])
    }
    
    results_payload = {
        "model_3d": model_3d_payload,
        "displacements": formatted_disp,
        "efforts": formatted_efforts,
        "equilibrium_audit": formatted_equilibrium
    }
    
    project_meta = {
        "obra": "Memorial Estrutural da Questao 31 (Treliça Cantilever)",
        "local": "Auditoria de Projeto e Recurso de Anulacao",
        "responsavel": "Atlas MEF Structural - Engenharia Premium",
        "registro": "CREA-SP 999999 / Gem-9"
    }
    
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "memorial_questao_31.pdf")
    
    generate_professional_memorial(output_path, results_payload, project_meta)
    
    print(f"\n==================================================")
    print(f"🔥 MEMORIAL DE CÁLCULO DA TRELIÇA EM PDF GERADO COM SUCESSO!")
    print(f"Caminho do arquivo: {output_path}")
    print(f"==================================================")

if __name__ == '__main__':
    run_q31_simulation_and_pdf()
