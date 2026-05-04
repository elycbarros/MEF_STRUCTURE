import structural_core_rs

def test_beam():
    print("Iniciando teste do Core Rust...")
    
    # 2 vãos -> 3 nós -> 6 graus de liberdade
    solver = structural_core_rs.BeamSolver(2)
    size = solver.get_matrix_size()
    print(f"Tamanho da Matriz de Rigidez: {size}")
    
    # Vão 1: L=4m, E=25GPa (25000 MPa), I=200000cm4 (0.002 m4)
    # add_span_stiffness(node_i, node_j, L, E, I)
    solver.add_span_stiffness(0, 1, 4.0, 25000.0, 0.002)
    print("Vão 1 (4m) processado em Rust.")
    
    # Vão 2: L=5m
    solver.add_span_stiffness(1, 2, 5.0, 25000.0, 0.002)
    print("Vão 2 (5m) processado em Rust.")
    
    print("\n✅ Teste de integração Rust-Python concluído com sucesso!")

if __name__ == "__main__":
    test_beam()
