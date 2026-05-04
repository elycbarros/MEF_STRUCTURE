import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from laje_lab_v2 import LajeLabV2Config, run_laje_v2_pipeline
from lajes_solver import PillarSupport
from strucpy_adapter import Beam

def test_sobrado_demo():
    print("=== TESTANDO SOBRADO DEMO (INTEGRAÇÃO COMPLETA) ===")
    
    # 1. Definir Geometria
    pillars = [
        PillarSupport("P1", 0.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P2", 5.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P3", 0.0, 5.0, bx=0.3, by=0.3),
        PillarSupport("P4", 5.0, 5.0, bx=0.3, by=0.3),
    ]
    
    # Vigas no topo (conecta nós 2, 4, 8, 6 - IDs gerados pelo laje_lab_v2)
    beams = [
        Beam(id="V1", node1_id=2, node2_id=4, b=0.20, d=0.50),
        Beam(id="V2", node1_id=4, node2_id=8, b=0.20, d=0.50),
        Beam(id="V3", node1_id=8, node2_id=6, b=0.20, d=0.50),
        Beam(id="V4", node1_id=6, node2_id=2, b=0.20, d=0.50),
    ]
    
    # 2. Configurar Cargas e Laje
    config = LajeLabV2Config(
        base_name="sobrado_demo_test",
        pillars=pillars,
        beams=beams,
        q_perm=2500, # 2.5 kN/m2 (Peso próprio + Revestimento)
        q_acid=2000, # 2.0 kN/m2 (Sobrecarga residencial)
        fck=30.0
    )
    
    # 3. Executar Pipeline (Com Autoflooring)
    results = run_laje_v2_pipeline(config)
    
    # 4. Validar Resultados
    if results['success']:
        print("\n✅ Sucesso: Pipeline executado com Autoflooring.")
        design = results['design']
        print(f"   -> Vigas dimensionadas: {len(design['beams'])}")
        print(f"   -> Pilares dimensionados: {len(design['pillars'])}")
        
        # Verificar se as cargas foram aplicadas (q_load > 0)
        # Nota: O adapter pode não retornar o q_load no resultado final do frame,
        print(f"   -> Chaves das vigas: {list(design['beams'][0].keys())}")
        print(f"   -> Chaves dos pilares: {list(design['pillars'][0].keys())}")
        v1_mom = design['beams'][0].get('M (kNm)', 0) # Tentar pegar a chave correta
        print(f"   -> Momento Máximo na V1: {v1_mom:.2f} kNm")
        
        if v1_mom > 0:
            print("✅ Sucesso: Cargas da laje distribuídas para as vigas.")
        else:
            print("❌ Erro: Vigas sem carga (Momento = 0).")
            
        summary = design.get('summary', {})
        print(f"   -> Consumo estimado: {summary.get('total_steel_kg', 0):.1f} kg de aço.")
    else:
        print("❌ Erro: Falha na execução do pipeline.")

if __name__ == "__main__":
    try:
        test_sobrado_demo()
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
