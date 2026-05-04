import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from laje_lab_v2 import LajeLabV2Config, run_laje_v2_pipeline
from lajes_solver import PillarSupport
from strucpy_adapter import Beam
from wind_engine import WindEngine, WindConfig
from radier_pdf import generate_radier_report_pdf

def generate_sobrado_pdf():
    print("=== GERANDO PDF OFICIAL - SOBRADO DEMO ===")
    
    # 1. Configurar o Modelo
    # Sobrado: 5x5m, Altura=6m
    H = 6.0
    B = 5.0
    D = 5.0
    
    pillars = [
        PillarSupport("P1", 0.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P2", 5.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P3", 0.0, 5.0, bx=0.3, by=0.3),
        PillarSupport("P4", 5.0, 5.0, bx=0.3, by=0.3),
    ]
    
    beams = [
        Beam(id="V1", node1_id=2, node2_id=4, b=0.20, d=0.50),
        Beam(id="V2", node1_id=4, node2_id=8, b=0.20, d=0.50),
        Beam(id="V3", node1_id=8, node2_id=6, b=0.20, d=0.50),
        Beam(id="V4", node1_id=6, node2_id=2, b=0.20, d=0.50),
    ]
    
    config = LajeLabV2Config(
        base_name="sobrado_demo_final",
        pillars=pillars,
        beams=beams,
        q_perm=2500,
        q_acid=2000,
        fck=30.0
    )
    
    # 2. Executar Simulação Estrutural
    results = run_laje_v2_pipeline(config)
    
    # 3. Executar Análise de Vento Automática
    print("Executando Análise de Vento (Arrasto Automático)...")
    wind_cfg = WindConfig(v0=40.0) # Vento forte (ex: região costeira)
    engine = WindEngine()
    cf = engine.get_rectangular_drag_coefficient(H, B, D)
    profile = engine.generate_vertical_profile(H, step=3.0, config=wind_cfg) # 0, 3, 6m
    
    # Adicionar força de arrasto ao perfil para o PDF
    for p in profile:
        # Área de influência simplificada para cada nível (pavimento)
        area_ref = B * 3.0 # Largura x Altura do pavimento
        p['f_drag_N'] = engine.get_drag_force(p['z'], area_ref, cf, wind_cfg)
        
    results['wind_data'] = {
        'config': {
            'v0': wind_cfg.v0,
            's1': wind_cfg.s1,
            's3': wind_cfg.s3
        },
        'cf': cf,
        'profile': profile
    }
    
    # 3. Preparar Metadados do Projeto
    project_meta = {
        "obra": "SOBRADO DEMO - RADIER LAB PRO",
        "local": "Florianópolis, SC",
        "responsavel": "Eng. Elyc Barros",
        "registro": "CREA-SC 123456",
        "emissao": "02/05/2026"
    }
    
    # Adicionar dados de design aos resultados para o PDF
    # O gerador de PDF espera 'design_results' ou 'design'
    results['frame_data'] = {
        'design_results': results['design']
    }
    
    # 4. Gerar o PDF
    output_path = "output_api/relatorio_sobrado_demo.pdf"
    os.makedirs("output_api", exist_ok=True)
    
    print(f"Gerando PDF em: {output_path}...")
    generate_radier_report_pdf(output_path, results, project_meta)
    
    print(f"✅ Sucesso! PDF gerado: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    try:
        generate_sobrado_pdf()
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
