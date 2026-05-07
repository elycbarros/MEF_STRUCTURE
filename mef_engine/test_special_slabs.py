
import sys
import os

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.getcwd())

from slab_lab import SlabLab, SlabConfig
from lajes_solver import PillarSupport

def test_comparison():
    print("--- TESTE DE DIFERENCIAÇÃO ESTRUTURAL ---")
    
    # 1. Configuração Comum
    common = {
        "Lx": 6.0, "Ly": 6.0,
        "h": 0.20, # 20 cm
        "fck": 30.0,
        "q_perm": 1.0,
        "q_acid": 2.0,
        "nx": 15, "ny": 15 # Malha rápida para teste
    }
    pillars = [
        PillarSupport("P1", 0.5, 0.5), PillarSupport("P2", 5.5, 0.5),
        PillarSupport("P3", 0.5, 5.5), PillarSupport("P4", 5.5, 5.5)
    ]

    # --- LAJE MACIÇA ---
    cfg_solid = SlabConfig(base_name="test_solid", slab_type="solid", pillars=pillars, **common)
    lab_solid = SlabLab(cfg_solid)
    res_solid = lab_solid.run_full_pipeline()
    w_solid = res_solid['master']['mef_summary']['w_max_mm']
    reac_solid = res_solid['master']['mef_summary']['reactions_total_kN']

    # --- LAJE NERVURADA ---
    # Mesmo h total, mas com cubetas
    cfg_ribbed = SlabConfig(
        base_name="test_ribbed", 
        slab_type="ribbed", 
        pillars=pillars,
        b_nerv=0.10, dist_nerv=0.50, h_mesa=0.05,
        **common
    )
    lab_ribbed = SlabLab(cfg_ribbed)
    res_ribbed = lab_ribbed.run_full_pipeline()
    w_ribbed = res_ribbed['master']['mef_summary']['w_max_mm']
    reac_ribbed = res_ribbed['master']['mef_summary']['reactions_total_kN']

    print(f"\nRESULTADOS:")
    print(f"Maciça   -> Reação Total: {reac_solid:.2f} kN | Flecha Máx: {w_solid:.2f} mm")
    print(f"Nervurada -> Reação Total: {reac_ribbed:.2f} kN | Flecha Máx: {w_ribbed:.2f} mm")

    # Validações
    if reac_ribbed < reac_solid:
        print("✅ SUCESSO: Laje nervurada é mais leve (Peso Próprio reduzido).")
    else:
        print("❌ FALHA: Laje nervurada não reduziu o peso próprio.")

    if w_ribbed > w_solid:
        print("✅ SUCESSO: Laje nervurada deformou mais (Inércia reduzida).")
    else:
        print("❌ FALHA: Laje nervurada não alterou a rigidez.")

    # --- LAJE PROTENDIDA ---
    # Mesmo h total da maciça, mas com força de protensão
    cfg_prest = SlabConfig(
        base_name="test_prestressed", 
        slab_type="prestressed", 
        pillars=pillars,
        p_force=400.0, ecc=0.07, # Valores fortes para ver o efeito
        **common
    )
    lab_prest = SlabLab(cfg_prest)
    res_prest = lab_prest.run_full_pipeline()
    w_prest = res_prest['master']['mef_summary']['w_max_mm']

    print(f"Protendida -> Flecha Máx: {w_prest:.2f} mm")

    if w_prest < w_solid:
        print("✅ SUCESSO: Protensão reduziu a flecha (Carga Balanceada ascendente).")
    else:
        print("❌ FALHA: Protensão não alterou a flecha.")

    # --- LAJE TRELIÇADA ---
    cfg_trussed = SlabConfig(
        base_name="test_trussed", 
        slab_type="trussed", 
        pillars=pillars,
        filler_type="ceramic",
        dist_nerv=0.45, h_mesa=0.05,
        **common
    )
    lab_trussed = SlabLab(cfg_trussed)
    res_trussed = lab_trussed.run_full_pipeline()
    reac_trussed = res_trussed['master']['mef_summary']['reactions_total_kN']

    print(f"Treliçada (Cerâmica) -> Reação Total: {reac_trussed:.2f} kN")

    if reac_trussed < reac_solid:
        print("✅ SUCESSO: Laje treliçada reduziu o peso em relação à maciça.")
    else:
        print("❌ FALHA: Laje treliçada não reduziu o peso.")

if __name__ == "__main__":
    test_comparison()
