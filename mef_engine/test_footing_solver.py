from footing_solver import solve_isolated_footing

def test_footing_analysis():
    params = {
        'Nd': 500.0,
        'sigma_adm': 300.0,
        'ap': 0.20,
        'bp': 0.20,
        'fck': 25.0
    }
    
    res = solve_isolated_footing(params)
    
    print("\n--- Resultados de Análise de Sapata ---")
    print(f"Dimensões: {res['A_m']}m x {res['B_m']}m")
    print(f"Altura h: {res['h_m']}m")
    print(f"Área: {res['area_m2']}m2")
    print(f"Pressão no Solo: {res['sigma_max_kPa']:.2f} kPa (Adm: {res['sigma_adm_kPa']} kPa)")
    print(f"Rigidez: {'Rígida' if res['is_rigid'] else 'Flexível'}")
    print(f"Armadura A: {res['as_a_cm2']:.2f} cm2")
    print(f"Armadura B: {res['as_b_cm2']:.2f} cm2")
    print(f"Status: {res['status']}")

if __name__ == "__main__":
    test_footing_analysis()
