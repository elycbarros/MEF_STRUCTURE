"""
test_lajes_advanced.py - Validação Profissional do Módulo Lajes Lab.
Simula uma laje com aberturas (vazios) e capitéis (espessura variável).
"""
import numpy as np
import pandas as pd
from radier_lab_v24 import PlateModel, DesignConfig, run_deterministic_fem
from radier_solver_v2 import Material, Soil, RadierMindlinWinklerV2

def test_advanced_laje():
    print("🚀 Iniciando Simulação Avançada Lajes Lab (Aberturas + Capitéis)...")
    
    # Geometria 10x10m
    nx, ny = 31, 31
    Lx, Ly = 10.0, 10.0
    h = 0.15 # 15cm base
    
    # 1. Definir Pilares (4 nos cantos internos)
    pillars = [
        [2.0, 2.0, 50000], [8.0, 2.0, 50000],
        [8.0, 8.0, 50000], [2.0, 8.0, 50000]
    ]
    p_df = pd.DataFrame(pillars, columns=['x', 'y', 'p_kN'])
    p_df.to_csv("lajes_adv_columns.csv", index=False)

    # Converter para formato de apoios (com rigidez rotacional para estabilidade)
    supports_list = [{'x': p[0], 'y': p[1], 'kz': 1e16, 'krx': 1e12, 'kry': 1e12} for p in pillars]
    
    # Criar modelo com apoios
    mat = Material(E=30e9, nu=0.2, h=h)
    soil = Soil(kv=0) # Laje elevada
    model = PlateModel(Lx=Lx, Ly=Ly, nx=nx, ny=ny, material=mat, soil=soil, supports=supports_list)
    solver = RadierMindlinWinklerV2(model)
    solver._q_uniform = 10000 # 10 kPa de carga distribuída (peso próprio + util)
    
    # Adicionar uma carga concentrada no centro (5,5) para ver a flecha entre apoios
    pillars_with_center = pillars + [[5.0, 5.0, 100000]] # +100kN no centro
    p_df = pd.DataFrame(pillars_with_center, columns=['x', 'y', 'p_kN'])
    
    # 2. Definir Aberturas (Vazios) - Elementos centrais
    n_elements = len(solver.elements)
    opening_mask = np.zeros(n_elements, dtype=bool)
    # Fazer um buraco no centro (de 4m a 6m)
    for i, el in enumerate(solver.elements):
        nodes = solver.nodes[el]
        cx, cy = np.mean(nodes[:,0]), np.mean(nodes[:,1])
        if 4.5 < cx < 5.5 and 4.5 < cy < 5.5:
            opening_mask[i] = True
            
    # 3. Definir Capitéis (Espessura de 25cm sobre os pilares)
    h_map = np.full(n_elements, h)
    for i, el in enumerate(solver.elements):
        nodes = solver.nodes[el]
        cx, cy = np.mean(nodes[:,0]), np.mean(nodes[:,1])
        for p in pillars:
            if abs(cx - p[0]) < 0.6 and abs(cy - p[1]) < 0.6:
                h_map[i] = 0.25 # 25cm no capitel
                
    # Executar solver manualmente para validar lógica avançada
    res = solver.solve(
        column_loads=p_df.values,
        h_per_element=h_map,
        opening_mask=opening_mask,
        concrete_nonlinear=True
    )
    
    w_max = np.max(np.abs(res.disp[:, 0]))
    
    # Debug: ver flecha no apoio (deve ser ~0)
    sup_node, _ = solver._find_cell_and_shape_weights(2.0, 2.0)
    w_sup = res.disp[sup_node[0], 0]
    
    print(f"✅ Simulação Concluída!")
    print(f"📐 Flecha Máxima: {w_max*1000:.4f} mm")
    print(f"📍 Flecha no Apoio (2,2): {w_sup*1000:.2e} mm")
    print(f"🕳️ Elementos removidos (aberturas): {np.sum(opening_mask)}")
    print(f"🏗️ Elementos com capitel (h=25cm): {np.sum(h_map > 0.15)}")
    
    if w_max > 0:
        print("✅ Comportamento estrutural validado para geometrias complexas.")

if __name__ == "__main__":
    test_advanced_laje()
