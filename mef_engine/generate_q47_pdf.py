import os
import sys
import numpy as np
from frame_engine import Frame3DEngine, FrameNode, FrameMember, FrameSection, FrameLoad
from professional_pdf import generate_professional_memorial

def run_q47_simulation_and_pdf():
    print("Iniciando simulação 2D/3D Frame de Vigas para a Questão 47...")
    
    # 1. Definir Nós
    # Nó 0: Apoio A (x = 0m)
    # Nó 1: Apoio B (x = 6m)
    # Nó 2: Ponta Livre C (x = 8m)
    nodes = [
        FrameNode(id=0, x=0.0, y=0.0, z=0.0),
        FrameNode(id=1, x=6.0, y=0.0, z=0.0),
        FrameNode(id=2, x=8.0, y=0.0, z=0.0)
    ]
    
    # 2. Definir Membros (Vigas)
    # Membro 0: Trecho AB (0 a 6m)
    # Membro 1: Trecho BC (6 a 8m)
    section = FrameSection(b=0.20, h=0.50, E=2.5e10) # 20x50cm, E = 25 GPa (Concreto padrão)
    members = [
        FrameMember(id=0, node_i=0, node_j=1, section=section),
        FrameMember(id=1, node_i=1, node_j=2, section=section)
    ]
    
    # 3. Definir Cargas
    # Força concentrada de 30 kN para baixo no Nó 2 (Ponta livre C)
    # No sistema de coordenadas global, Z é vertical. Logo, Fz = -30.000 N (-30 kN)
    loads = [
        FrameLoad(node_id=2, Fz=-30000.0)
    ]
    
    # 4. Definir Apoios
    # Apoios restritos nos eixos transladados e de torção/fora-do-plano para estabilidade em 3D
    # Bloqueamos Ux(0), Uy(1), Uz(2), Rx(3), Rz(5) e deixamos Ry(4) livre para flexão.
    supports = {
        0: [0, 1, 2, 3, 5], # Apoio A (Fixo em translação, rotação Y livre)
        1: [0, 1, 2, 3, 5]  # Apoio B (Fixo em translação, rotação Y livre)
    }
    
    # 5. Instanciar Motor de Pórtico 3D
    engine = Frame3DEngine(nodes, members, use_rust_if_available=False)
    engine.is_truss = False # Modo Pórtico/Viga (com momento fletor!)
    
    # 6. Resolver pelo MEF
    res = engine.solve(loads, supports, reduce_stiffness=False)
    
    # 7. Obter esforços internos e equilíbrio estático
    efforts = engine.get_member_efforts(res["displacements"])
    equilibrium = engine.check_equilibrium(loads, res["displacements"], supports)
    
    # 8. Formatar dados de saída exatamente no padrão esperado pelo gerador de PDF profissional
    model_3d_payload = {
        "is_truss": False,
        "nodes": [
            {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 1, "x": 6.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 8.0, "y": 0.0, "z": 0.0}
        ],
        "members": [
            {"id": 0, "node_i": 0, "node_j": 1, "section": {"b": 0.20, "h": 0.50}},
            {"id": 1, "node_i": 1, "node_j": 2, "section": {"b": 0.20, "h": 0.50}}
        ],
        "supports": {
            "0": [0, 1, 2, 3, 5],
            "1": [0, 1, 2, 3, 5]
        },
        "loads": [
            {"node_id": 2, "fz": -30.0}
        ]
    }
    
    # Formatar deslocamentos para [dx, dy, dz, Rx, Ry, Rz]
    formatted_disp = {}
    for nid, d_vec in res["displacements"].items():
        formatted_disp[str(nid)] = [float(v) for v in d_vec]
        
    # Formatar esforços para cada membro
    formatted_efforts = {}
    for mid, eff in efforts.items():
        # Devido à orientação dos eixos locais no Pórtico 3D:
        # - O esforço cortante vertical em Z global está mapeado em local Vy.
        # - O momento fletor em Y global (flexão coplanar) está mapeado em local Mz.
        # Mapeamos local Mz -> global/pedagógico My e local Vy -> global/pedagógico Vz/Vy para exibição perfeita.
        formatted_efforts[str(mid)] = {
            "i": {
                "N": float(eff["i"]["N"]),
                "Vy": float(eff["i"]["Vy"]),
                "Vz": float(eff["i"]["Vy"]), # Duplicado em Vy/Vz para robustez na tabela do PDF
                "My": float(eff["i"]["Mz"]), # Mz local mapeado para My pedagógico
                "Mz": float(eff["i"]["Mz"])
            },
            "j": {
                "N": float(eff["j"]["N"]),
                "Vy": float(eff["j"]["Vy"]),
                "Vz": float(eff["j"]["Vy"]), # Duplicado em Vy/Vz para robustez na tabela do PDF
                "My": float(eff["j"]["Mz"]), # Mz local mapeado para My pedagógico
                "Mz": float(eff["j"]["Mz"])
            }
        }
        
    # Formatar auditoria de equilíbrio estático
    # equilibrium["reactions"] e sum_applied_kN_m já estão divididos por 1000 no check_equilibrium do frame_engine!
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
    
    # Metadados do Projeto para capa e cabeçalhos
    project_meta = {
        "obra": "Memorial Estrutural da Questao 47 (Prova de Concurso)",
        "local": "Auditoria de Projeto e Recurso de Anulacao",
        "responsavel": "Atlas MEF Structural - Engenharia Premium",
        "registro": "CREA-SP 999999 / Gem-9"
    }
    
    # Criar diretório para salvar o PDF
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "memorial_questao_47.pdf")
    
    # Gerar o PDF Oficial Professional
    generate_professional_memorial(output_path, results_payload, project_meta)
    
    print(f"\n==================================================")
    print(f"🔥 MEMORIAL DE CÁLCULO PROFISSIONAL EM PDF GERADO COM SUCESSO!")
    print(f"Caminho do arquivo: {output_path}")
    print(f"==================================================")
    
    # Exibir reações calculadas via Frame3D
    print("\nReações calculadas no Pórtico 3D:")
    for nid, r_vec in formatted_reac.items():
        print(f"Nó {nid} (x={nodes[int(nid)].x:.1f}m): Rz = {r_vec[2]:.2f} kN, My = {r_vec[4]:.2f} kNm")
        
    print("\nDeslocamentos nodais brutos:")
    for nid, disp in res["displacements"].items():
        print(f"Nó {nid}: {disp}")

    print("\nEsforços nos Membros (My nos nós i e j):")
    for mid in efforts.keys():
        # Vamos chamar get_member_efforts de forma a inspecionar os valores brutos retornados pelo solver
        T, L = engine._get_transformation(engine.members[mid])
        u_e = np.concatenate([res["displacements"][engine.members[mid].node_i], res["displacements"][engine.members[mid].node_j]])
        f_loc = engine._get_k_local(engine.members[mid], L) @ (T @ u_e)
        print(f"Membro {mid} - f_loc bruto (N, Nm):")
        print([f"{v:.2f}" for v in f_loc])
        
        eff = formatted_efforts[str(mid)]
        print(f"Membro {mid} formatado: My_i = {eff['i']['My']:.2f} kNm, My_j = {eff['j']['My']:.2f} kNm")
        print(f"          Mz_i = {eff['i']['Mz']:.2f} kNm, Mz_j = {eff['j']['Mz']:.2f} kNm")
        print(f"          Vz_i = {eff['i']['Vz']:.2f} kN, Vz_j = {eff['j']['Vz']:.2f} kN")
        print(f"          Vy_i = {eff['i']['Vy']:.2f} kN, Vy_j = {eff['j']['Vy']:.2f} kN")
        print(f"          N_i = {eff['i']['N']:.2f} kN, N_j = {eff['j']['N']:.2f} kN")

if __name__ == '__main__':
    run_q47_simulation_and_pdf()
