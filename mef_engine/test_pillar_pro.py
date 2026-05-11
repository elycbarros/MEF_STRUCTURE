"""
test_pillar_pro.py — Validação do Módulo Pilar Pro (Alta Fidelidade).
Simula um pilar de base de um edifício de 40 andares com efeitos biaxiais e esbeltez.
"""
import json
from column_solver import ColumnSection, ColumnLoads, solve_column_section
from column_detailing import ColumnDetailer
from load_takedown import LoadTakedownEngine

def run_pro_pillar_audit():
    print("🚀 Iniciando Auditoria Pilar Pro (Nível Forense)...")
    
    # 1. Simulação de Takedown (Carga na base de 40 andares)
    # Área de influência de 30m2 por pavimento
    takedown = LoadTakedownEngine.run_vertical_takedown(n_floors=40, area_influence_m2=30.0)
    base_load = takedown.iloc[-1] # Pavimento 1 (Base)
    
    print(f"📊 Carga Acumulada (Base): Nd = {base_load['total_design_kN']:.1f} kN")
    
    # 2. Configuração do Pilar de Base
    # Pilar de 80x80 cm, C50
    sec = ColumnSection(b=0.80, h=0.80, fck=50, L_free=3.0)
    
    # Cargas incluindo momentos de vento (Biaxial)
    loads = ColumnLoads(
        Nd_kN=base_load['total_design_kN'],
        Mxd_kNm=550.0, # Vento X
        Myd_kNm=280.0  # Vento Y
    )
    
    # 3. Análise Pro (Biaxial + Rigidez Nominal)
    solve_res = solve_column_section(sec, loads)
    
    # 4. Detalhamento Executivo
    detail_res = ColumnDetailer.generate_detailing_summary(solve_res)
    
    # Exibir Resultados
    print("\n✅ Auditoria de Dimensionamento:")
    print(f"   Seção: {solve_res['section']} cm | fck: {solve_res['fck_MPa']} MPa")
    print(f"   Esbeltez (λx): {solve_res['slenderness']['lambda_x']} (Limite: {solve_res['slenderness']['limit']})")
    print(f"   Método 2ª Ordem: {solve_res['moments_2nd_order']['method']}")
    print(f"   Momento Total (Mx): {solve_res['Md_x_total_kNm']} kNm")
    print(f"   Taxa de Armadura (ω): {solve_res['omega']}")
    print(f"   Área de Aço (As): {solve_res['As_final_cm2']} cm²")
    
    print("\n🏗️ Detalhamento Sugerido (Executive Grade):")
    print(f"   Longitudinal: {detail_res['longitudinal']['label']}")
    print(f"   Estribos: {detail_res['transverse']['label']}")
    print(f"   Status: {solve_res['status']}")

    if solve_res['status'] == "OK":
        print("\n✅ Pilar VALIDADO para carga de 40 pavimentos + Vento Biaxial.")
    else:
        print(f"\n⚠️ Alerta: {solve_res['status']}")

def test_pillar_pro():
    run_pro_pillar_audit()

if __name__ == "__main__":
    run_pro_pillar_audit()
