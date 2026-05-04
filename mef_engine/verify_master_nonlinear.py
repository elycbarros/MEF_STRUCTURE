"""
verify_master_nonlinear.py - Script de validação para Solo Não-Linear e Reforços de Punção.
"""
from radier_lab_v24 import LabConfig, run_deterministic_fem, run_full_pipeline_demo
from radier_utils import read_json
import pandas as pd
from pathlib import Path

def test_master_capabilities():
    print("=== TESTANDO SOLO NÃO-LINEAR E STUDS DE PUNÇÃO ===")
    
    # 1. Configuração de Solo Elasto-Plástico
    cfg = LabConfig(
        base_name="valida_master",
        output_dir="output_valida",
        Lx=10.0,
        Ly=10.0,
        nx=11,
        ny=11,
        h=0.50,
        kv=20e6,
        q=200e3, # 200 kPa (Carga alta)
        q_limit_kPa=150.0, # Limite plástico
        tensionless=True
    )
    
    print("\nSimulando Solo Elasto-Plástico (q_limit = 150 kPa)...")
    res_path = run_deterministic_fem(cfg)
    results = read_json(res_path)
    
    print(f"Pressão Máxima no Solo: {results['qsoil_max_kPa']:.2f} kPa")
    if results['qsoil_max_kPa'] <= 150.1:
        print("[OK] O solver limitou a pressão ao patamar plástico!")
    else:
        print(f"[ALERTA] Pressão ultrapassou o limite: {results['qsoil_max_kPa']}")

    # 2. Teste de Punção com Studs
    print("\nSimulando Puncionamento com Studs...")
    # Criar um CSV de colunas customizado para forçar puncionamento
    cols_path = Path("output_valida/custom_columns.csv")
    cols_path.parent.mkdir(exist_ok=True)
    pd.DataFrame([
        {'id': 'P_CRITICO', 'x': 5.0, 'y': 5.0, 'p': 5000e3, 'bx': 0.4, 'by': 0.4, 'local': 'interior'}
    ]).to_csv(cols_path, index=False)
    
    cfg.columns_csv = str(cols_path)
    cfg.q = 50e3 
    cfg.q_limit_kPa = None # Desativar não linearidade solo para focar na punção
    
    run_full_pipeline_demo(cfg)
    
    # Verificar no memorial summary
    memorial_path = f"output_valida/valida_master_memorial_summary.json"
    memorial = read_json(memorial_path)
    punching = memorial['verificacoes_estruturais']['puncao']
    
    print(f"Pilar: {punching['critical_local']}")
    print(f"Ratio Punção: {punching['ratio_max']:.2f}")
    print(f"Asw Requerido: {punching['Asw_req_cm2']:.2f} cm2")
    print(f"Detalhamento: {punching['detalhe_reforco']}")
    
    if punching['Asw_req_cm2'] > 0:
        print("[OK] Armadura de punção (Studs) calculada com sucesso!")
    else:
        print("[ERRO] Não foi calculado reforço para carga crítica.")

if __name__ == "__main__":
    test_master_capabilities()
