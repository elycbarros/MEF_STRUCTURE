"""
generate_skyscraper_demo.py - Simulação de Excelência para Edifício de 40 Andares.
"""
import sys
import os
import math

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wind_engine import WindEngine, WindConfig
from stability_engine import StabilityEngine
from radier_pdf import generate_radier_report_pdf

def simulate_skyscraper():
    print("=== SIMULAÇÃO DE EXCELÊNCIA: SKYSCRAPER 40 ANDARES ===")
    
    # 1. Geometria e Cargas
    n_floors = 40
    floor_height = 3.0
    total_height = n_floors * floor_height # 120m
    width_b = 20.0 # Largura frontal
    depth_d = 20.0 # Profundidade
    
    # Carga vertical estimada: 12 kN/m2 por pavimento
    area_floor = width_b * depth_d
    load_per_floor = area_floor * 12.0 # kN
    total_p_kN = load_per_floor * n_floors
    
    print(f"Altura: {total_height}m | Peso Total: {total_p_kN/10:.0f} tf")

    # 2. Análise de Vento (NBR 6123)
    wind_cfg = WindConfig(v0=35.0, s1=1.0, s3=1.0)
    engine = WindEngine(wind_cfg)
    
    # Gera o perfil de forças discretizado por pavimento
    wind_analysis = engine.generate_force_profile(
        height=total_height, 
        width=width_b, 
        depth=depth_d, 
        step=floor_height
    )
    
    summary = wind_analysis["summary"]
    total_m1_kNm = summary["base_moment_kNm"]
    wind_profile = wind_analysis["profile"]
    cf = summary["cf_used"]

    # 3. Análise de Estabilidade Global e Conforto
    # Frequência estimada para prédio de 120m: f1 = 46/H = 46/120 = 0.38 Hz
    f1_hz = 46.0 / total_height
    stab_engine = StabilityEngine()
    stab_res = stab_engine.calculate_advanced_stability(
        total_p_kN=total_p_kN,
        height=total_height,
        m1_kNm=total_m1_kNm,
        wind_v0=wind_cfg.v0,
        f1_hz=f1_hz
    )

    # 4. Gerar Relatório PDF
    results = {
        "base_name": "skyscraper_40_floors",
        "total_vertical_load_kN": total_p_kN,
        "wind_data": {
            "config": {"v0": wind_cfg.v0, "s1": wind_cfg.s1, "s3": wind_cfg.s3},
            "cf": cf,
            "profile": wind_profile[::5] # Resumo a cada 5 andares
        },
        "stability_data": {
            "gamma_z": stab_res.gamma_z,
            "is_stable": stab_res.is_stable,
            "p_delta_factor": stab_res.p_delta_factor,
            "peak_acceleration_ms2": stab_res.peak_acceleration_ms2,
            "comfort_status": stab_res.comfort_status
        },
        "memorial": {
            "geotecnia": {"status": "ok", "pressao_max_adm_mpa": 0.5},
            "verificacoes_de_servico": {"w_max_mm": 15.0, "w_limite_mm": 25.0}
        }
    }
    
    project_meta = {
        "obra": "SKYSCRAPER TOWER - 40 PAVIMENTOS",
        "local": "Balneário Camboriú, SC",
        "responsavel": "MEF STRUCTURAL AI",
        "data": "2026-05-02"
    }
    
    output_path = "output_api/relatorio_skyscraper_40.pdf"
    generate_radier_report_pdf(output_path, results, project_meta)
    print(f"✅ Simulação concluída! Relatório gerado em: {output_path}")

if __name__ == "__main__":
    simulate_skyscraper()
