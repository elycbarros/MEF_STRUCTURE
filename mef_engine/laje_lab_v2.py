"""laje_lab_v2.py – Orquestrador para o módulo Lajes Lab com integração StrucPy."""
from __future__ import annotations
import sys
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import pandas as pd

from lajes_solver import (
    Material, PillarSupport, LineSupport, Hole, LajeModel, LajesMindlinSolver, SupportType
)
from radier_design_v2 import (
    DesignConfig, design_flexure_from_elements, check_serviceability_flexure, check_punching
)
from strucpy_adapter import StrucPyAdapter, Beam

@dataclass
class LajeLabV2Config:
    module_name: str = 'laje_v2'
    code_profile: str = 'ABNT_NBR_6118_2023'
    output_dir: str = 'output_laje_v2'
    base_name: str = 'laje_strucpy_demo'
    
    # Geometria da Laje (MEF)
    Lx: float = 6.0
    Ly: float = 6.0
    nx: int = 15
    ny: int = 15
    h_slab: float = 0.15
    
    # Propriedades Concreto
    E: float = 30e9
    fck: float = 30.0
    
    # Estrutura 3D (StrucPy)
    pillar_height: float = 3.0
    pillars: list[PillarSupport] = field(default_factory=list)
    beams: list[Beam] = field(default_factory=list)
    
    # Cargas
    q_perm: float = 1.5e3
    q_acid: float = 2.0e3

def run_laje_v2_pipeline(config: LajeLabV2Config):
    print(f"--- Iniciando Pipeline Laje V2 ({config.base_name}) ---")
    
    # 1. Montar Modelo StrucPy (3D Frame)
    nodes = []
    strucpy_beams = []
    supports = []
    
    # Criar nós de fundação e topo
    for i, p in enumerate(config.pillars, 1):
        f_id = i * 2 - 1
        t_id = i * 2
        nodes.append({'id': f_id, 'x': p.x, 'y': p.y, 'z': 0.0}) # Fundação
        nodes.append({'id': t_id, 'x': p.x, 'y': p.y, 'z': config.pillar_height}) # Topo
        
        # Criar Pilar como Beam vertical
        strucpy_beams.append(Beam(id=p.id, node1_id=f_id, node2_id=t_id, b=p.bx, d=p.by))
        
        # Apoio na fundação
        supports.append({'node_id': f_id, 'tx': 1, 'ty': 1, 'tz': 1, 'rx': 1, 'ry': 1, 'rz': 1})

    # Adicionar vigas de projeto
    for b in config.beams:
        strucpy_beams.append(b)

    # --- AUTOFLOORING LOGIC ---
    # Distribuição de carga da laje para as vigas (Simplificado por área de influência)
    q_total = (config.q_perm + config.q_acid) / 1000.0 # kN/m2
    
    # Se não houver vigas explícitas, criar conectividade automática entre pilares próximos
    if len(config.beams) == 0 and len(config.pillars) >= 2:
        print("Gerando conectividade automática de vigas...")
        # Conectar P1-P2, P2-P4, P4-P3, P3-P1 se houver 4 pilares
        if len(config.pillars) == 4:
            pairs = [(2,4), (4,8), (8,6), (6,2)] 
            for i, (n1, n2) in enumerate(pairs):
                strucpy_beams.append(Beam(id=f"V{i+1}", node1_id=n1, node2_id=n2, b=0.20, d=0.40))

    # Aplicar cargas nas vigas (Autoflooring)
    # Estimativa: Carga linear = q_total * (L_influencia)
    # L_influencia aproximado como 2.5m (metade de um vão médio de 5m)
    # No StrucPy, 'y' é o eixo vertical. Carga de gravidade é negativa em yUDL.
    for b in strucpy_beams:
        if b.id.startswith("V"): # Somente vigas (não pilares)
            b.yUDL = -q_total * 2.5 # kN/m

    # 2. Executar Análise de Pórtico (StrucPy)
    print("Executando Análise de Pórtico 3D (StrucPy)...")
    frame = StrucPyAdapter.run_frame_analysis(nodes, strucpy_beams, supports, grade_conc=config.fck)
    
    # 3. Obter Resultados de Dimensionamento de Vigas e Pilares
    design_results_raw = StrucPyAdapter.get_design_results(frame)
    
    # Converter DataFrames para List[Dict] para facilitar JSON e iteração
    design_results = {
        'beams': design_results_raw['beams'].to_dict('records'),
        'pillars': design_results_raw['columns'].to_dict('records') # Renomeado para 'pillars'
    }
    print(f"Dimensionamento concluído para {len(design_results['beams'])} vigas e {len(design_results['pillars'])} pilares.")
    
    # 4. Resultados Adicionais para o Memorial
    design_results['summary'] = {
        'total_concrete_m3': sum(b.b * b.d * 1.0 for b in strucpy_beams), # Simplificado
        'total_steel_kg': sum(p['As'] * 7850 * 3.0 / 10000 for p in design_results['pillars'] if 'As' in p)
    }
    
    return {
        "success": True,
        "frame": frame,
        "design": design_results,
        "system_type": "laje"
    }

if __name__ == "__main__":
    pillars = [
        PillarSupport("P1", 0.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P2", 5.0, 0.0, bx=0.3, by=0.3),
        PillarSupport("P3", 0.0, 5.0, bx=0.3, by=0.3),
        PillarSupport("P4", 5.0, 5.0, bx=0.3, by=0.3),
    ]
    config = LajeLabV2Config(pillars=pillars)
    res = run_laje_v2_pipeline(config)
    print("Pipeline V2 finalizado.")
