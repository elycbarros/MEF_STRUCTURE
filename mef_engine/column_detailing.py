"""
column_detailing.py — Detalhamento Executivo de Pilares de Concreto Armado.
Transforma áreas de aço em bitolas e posições reais para pranchas DXF.
"""
import math
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RebarInfo:
    phi_mm: float
    area_cm2: float
    weight_kgm: float

# Bitolas comerciais brasileiras (CA-50)
COMMERCIAL_REBARS = [
    RebarInfo(10.0, 0.785, 0.617),
    RebarInfo(12.5, 1.227, 0.963),
    RebarInfo(16.0, 2.011, 1.578),
    RebarInfo(20.0, 3.142, 2.466),
    RebarInfo(25.0, 4.909, 3.853),
    RebarInfo(32.0, 8.042, 6.313),
]

class ColumnDetailer:
    @staticmethod
    def select_longitudinal_rebar(As_required_cm2: float, min_phi: float = 10.0) -> dict:
        """
        Escolhe a bitola e quantidade de barras para atingir a área necessária.
        Prefere bitolas entre 12.5mm e 25mm para pilares.
        """
        best_phi = 12.5
        best_count = 4
        min_over_area = 1000.0
        
        # Filtrar bitolas para preferir maiores em áreas grandes
        rebars_to_check = COMMERCIAL_REBARS
        if As_required_cm2 > 50:
            rebars_to_check = [r for r in COMMERCIAL_REBARS if r.phi_mm >= 16.0]
        if As_required_cm2 > 150:
            rebars_to_check = [r for r in COMMERCIAL_REBARS if r.phi_mm >= 25.0]

        for rebar in rebars_to_check:
            # Pilares retangulares precisam de pelo menos 4 barras (cantos)
            count = math.ceil(As_required_cm2 / rebar.area_cm2)
            count = max(count, 4)
            if count % 2 != 0: count += 1 # Garante simetria
            
            # Penalizar excesso de barras (mais de 24 barras é congestionado para pilares padrão)
            congestion_penalty = (count / 12.0) * 1.5 
            
            over_area = (count * rebar.area_cm2) - As_required_cm2 + congestion_penalty
            if 0 <= over_area < min_over_area:
                min_over_area = over_area
                best_phi = rebar.phi_mm
                best_count = count
                
        return {
            'phi_mm': best_phi,
            'count': best_count,
            'As_provided_cm2': round(best_count * (math.pi * (best_phi/10.0)**2 / 4.0), 2),
            'label': f'{best_count} Φ {best_phi:.1f}'
        }

    @staticmethod
    def calculate_stirrups(b_m: float, h_m: float, phi_long_mm: float, Nd_kN: float) -> dict:
        """
        Cálculo de estribos conforme NBR 6118 §18.2.3.
        - Espaçamento s <= 12 * phi_long
        - Espaçamento s <= b (menor dimensão)
        - Espaçamento s <= 20 cm
        """
        phi_est_mm = max(5.0, phi_long_mm / 4.0)
        if phi_est_mm < 6.3: phi_est_mm = 6.3 # Mínimo prático em pilares
        
        s_max_1 = 12 * (phi_long_mm / 10.0) # cm
        s_max_2 = min(b_m, h_m) * 100.0 # cm
        s_max_3 = 20.0 # cm (Regra geral para pilares usuais)
        
        s_final = min(s_max_1, s_max_2, s_max_3)
        s_final = math.floor(s_final)
        
        return {
            'phi_mm': phi_est_mm,
            'spacing_cm': s_final,
            'label': f'Φ {phi_est_mm:.1f} c/{s_final}'
        }

    @staticmethod
    def calculate_executive_geometry(b_m: float, h_m: float, longit: dict) -> dict:
        """
        Gera coordenadas (x, y) reais para as barras do pilar em planta.
        """
        cover = 0.03 # 3cm
        phi_m = longit['phi_mm'] / 1000.0
        count = longit['count']
        
        # Posicionamento simplificado (cantos + distribuição)
        coords = []
        
        # Cantos
        corners = [
            (cover + phi_m/2, cover + phi_m/2),
            (b_m - cover - phi_m/2, cover + phi_m/2),
            (b_m - cover - phi_m/2, h_m - cover - phi_m/2),
            (cover + phi_m/2, h_m - cover - phi_m/2)
        ]
        coords.extend(corners)
        
        # Se houver mais de 4, distribuir nos lados (simplificado para o sketch)
        if count > 4:
            remaining = count - 4
            # Distribuir nas faces maiores
            for i in range(remaining):
                side_x = cover + phi_m/2 + (i+1)*(b_m - 2*cover - phi_m)/(remaining+1)
                coords.append((side_x, cover + phi_m/2))
                
        return {
            'rebar_coords': [{'x': round(c[0], 3), 'y': round(c[1], 3)} for c in coords],
            'cover_m': cover
        }

    @staticmethod
    def generate_detailing_summary(solve_result: dict) -> dict:
        """
        Gera o resumo completo de detalhamento para um pilar.
        """
        As_req = solve_result.get('As_final_cm2', 12.0)
        # Parse dimensões: "60x60" -> 0.6, 0.6
        section = solve_result.get('section', '40x40')
        parts = section.split('x')
        b = float(parts[0]) / 100.0
        h = float(parts[1]) / 100.0
        
        longit = ColumnDetailer.select_longitudinal_rebar(As_req)
        stirrup = ColumnDetailer.calculate_stirrups(b, h, longit['phi_mm'], solve_result.get('Nd_kN', 1000))
        
        # Nova Geometria Executiva
        exec_geo = ColumnDetailer.calculate_executive_geometry(b, h, longit)
        
        return {
            'pilar_label': "P1",
            'section': section,
            'longitudinal': longit,
            'transverse': stirrup,
            'executive': exec_geo,
            'steel_ca50_kg': round(longit['count'] * 3.0 * 0.00617 * (longit['phi_mm']**2), 2),
            'notes': [
                "Concreto C" + str(solve_result.get('fck_MPa', 30)),
                "Aço CA-50",
                "Cobrimento 3.0 cm"
            ]
        }

if __name__ == "__main__":
    # Teste rápido
    mock_res = {
        'As_final_cm2': 18.5,
        'section': '40x40',
        'fck_MPa': 30,
        'Nd_kN': 2500
    }
    det = ColumnDetailer.generate_detailing_summary(mock_res)
    import json
    print(json.dumps(det, indent=2))
