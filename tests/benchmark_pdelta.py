import time
import numpy as np
from mef_engine.frame_engine import Frame3DEngine

def create_tower_model(n_stories=20, n_bays_x=3, n_bays_z=3, bay_width=6.0, story_height=3.0):
    """Gera um modelo de edifício torre 3D."""
    nodes = []
    members = []
    node_id_map = {}
    
    # Gerar nós
    node_counter = 1
    for level in range(n_stories + 1):
        y = level * story_height
        for i in range(n_bays_x + 1):
            x = i * bay_width
            for j in range(n_bays_z + 1):
                z = j * bay_width
                nodes.append({"id": node_counter, "x": x, "y": y, "z": z})
                node_id_map[(level, i, j)] = node_counter
                node_counter += 1
                
    # Gerar membros (vigas e pilares)
    member_counter = 1
    for level in range(n_stories + 1):
        for i in range(n_bays_x + 1):
            for j in range(n_bays_z + 1):
                # Pilares
                if level < n_stories:
                    n1 = node_id_map[(level, i, j)]
                    n2 = node_id_map[(level + 1, i, j)]
                    members.append({
                        "id": member_counter, "node_i": n1, "node_j": n2,
                        "section": {"area": 0.16, "iy": 0.0021, "iz": 0.0021, "j": 0.004, "ey": 0.2, "ez": 0.2},
                        "material": {"e": 30e9, "g": 12e9, "nu": 0.2, "rho": 2500},
                        "member_type": "column"
                    })
                    member_counter += 1
                
                # Vigas X
                if i < n_bays_x:
                    n1 = node_id_map[(level, i, j)]
                    n2 = node_id_map[(level, i + 1, j)]
                    members.append({
                        "id": member_counter, "node_i": n1, "node_j": n2,
                        "section": {"area": 0.12, "iy": 0.001, "iz": 0.0016, "j": 0.002, "ey": 0.1, "ez": 0.1},
                        "material": {"e": 30e9, "g": 12e9, "nu": 0.2, "rho": 2500},
                        "member_type": "beam"
                    })
                    member_counter += 1
                
                # Vigas Z
                if j < n_bays_z:
                    n1 = node_id_map[(level, i, j)]
                    n2 = node_id_map[(level, i, j + 1)]
                    members.append({
                        "id": member_counter, "node_i": n1, "node_j": n2,
                        "section": {"area": 0.12, "iy": 0.0016, "iz": 0.001, "j": 0.002, "ey": 0.1, "ez": 0.1},
                        "material": {"e": 30e9, "g": 12e9, "nu": 0.2, "rho": 2500},
                        "member_type": "beam"
                    })
                    member_counter += 1
                    
    # Apoios (engastes no nível 0)
    supports = {n["id"]: [1, 1, 1, 1, 1, 1] for n in nodes if n["y"] == 0}
    
    # Cargas (gravitacional simples em todos os nós)
    loads = [{"node_id": n["id"], "fx": 0, "fy": -10000, "fz": 0, "mx": 0, "my": 0, "mz": 0} for n in nodes]
    
    return nodes, members, loads, supports

def run_benchmark():
    stories_list = [5, 10, 20, 30, 40, 50]
    print(f"{'Stories':<10} | {'Nodes':<10} | {'Members':<10} | {'DOFs':<10} | {'Time (s)':<10}")
    print("-" * 60)
    
    for n in stories_list:
        nodes, members, loads, supports = create_tower_model(n)
        n_dofs = len(nodes) * 6
        
        engine = Frame3DEngine(nodes, members, loads, supports, use_rust_if_available=True)
        
        start = time.time()
        results = engine.solve(loads, supports, use_rust=True)
        elapsed = time.time() - start
        
        print(f"{n:<10} | {len(nodes):<10} | {len(members):<10} | {n_dofs:<10} | {elapsed:.3f}")

if __name__ == "__main__":
    run_benchmark()
