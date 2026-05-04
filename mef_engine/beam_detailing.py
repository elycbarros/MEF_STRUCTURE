"""
beam_detailing.py — Motor de Detalhamento Executivo de Vigas (NBR 6118).

Calcula a disposição de barras longitudinais, ancoragens, armaduras de pele 
e estribos para vigas de concreto armado.
"""
import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RebarInfo:
    phi_mm: float
    area_cm2: float
    weight_kg_m: float

COMMERCIAL_REBARS = [
    RebarInfo(5.0,  0.196, 0.154),
    RebarInfo(6.3,  0.312, 0.245),
    RebarInfo(8.0,  0.503, 0.395),
    RebarInfo(10.0, 0.785, 0.617),
    RebarInfo(12.5, 1.227, 0.963),
    RebarInfo(16.0, 2.011, 1.578),
    RebarInfo(20.0, 3.142, 2.466),
    RebarInfo(25.0, 4.909, 3.853),
]

class BeamDetailer:
    """Motor de detalhamento executive-grade para vigas."""

    @staticmethod
    def select_reinforcement(As_required_cm2: float, b_cm: float, h_cm: float) -> Dict:
        """Seleciona barras longitudinais para cobrir a área necessária."""
        if As_required_cm2 <= 0:
            return {"phi_mm": 10.0, "count": 2, "area_cm2": 1.57} # Mínimo 2 barras

        # Filtra bitolas usuais para vigas (10mm a 25mm)
        options = [r for r in COMMERCIAL_REBARS if 10.0 <= r.phi_mm <= 25.0]
        
        best_phi = 12.5
        best_count = 2
        min_over_area = 100.0

        for rebar in options:
            count = math.ceil(As_required_cm2 / rebar.area_cm2)
            count = max(count, 2) # Mínimo 2 barras por camada
            
            # Verificar se cabe na largura b (espaçamento min 2cm ou phi)
            espacamento = (b_cm - 2*3.5 - count*rebar.phi_mm/10.0) / max(count-1, 1)
            if espacamento < 2.0: continue
            
            over_area = (count * rebar.area_cm2) - As_required_cm2
            if 0 <= over_area < min_over_area:
                min_over_area = over_area
                best_phi = rebar.phi_mm
                best_count = count

        return {
            "phi_mm": best_phi,
            "count": best_count,
            "area_cm2": round(best_count * (best_phi**2 * math.pi / 400.0), 2)
        }

    @staticmethod
    def calculate_skin_reinforcement(h_cm: float, b_cm: float) -> Dict:
        """Armadura de pele conforme NBR 6118 §17.3.5.2 (h > 60cm)."""
        if h_cm <= 60:
            return {"needed": False, "As_skin_cm2_face": 0}
            
        # As,skin = 0.1% Ac (por face)
        As_skin = 0.001 * (b_cm * h_cm)
        return {
            "needed": True,
            "As_skin_cm2_face": round(As_skin, 2),
            "suggested": f"Φ 5.0 c/20 (Face)"
        }

    @staticmethod
    def calculate_anchorage(phi_mm: float, fck: float, type: str = "straight") -> float:
        """Calcula o comprimento de ancoragem básico lb (cm)."""
        # fbd = n1 * n2 * n3 * fctd
        # Simplificado para concreto C30, CA-50, boa aderência
        fctd = (0.21 * (fck**(2/3))) / 1.4
        fbd = 2.25 * 1.0 * 1.0 * fctd # MPa
        
        lb = (phi_mm / 40.0) * (500.0 / 1.15) / fbd # cm
        return round(lb, 1)

    @classmethod
    def generate_detailing_summary(cls, design_res: dict, b_m: float, h_m: float, fck: float) -> dict:
        """Compila o resumo de detalhamento para a viga."""
        b_cm = b_m * 100
        h_cm = h_m * 100
        
        As_inf = design_res['flexure_bottom']['As_cm2']
        As_sup = design_res['flexure_top']['As_cm2']
        
        det_inf = cls.select_reinforcement(As_inf, b_cm, h_cm)
        det_sup = cls.select_reinforcement(As_sup, b_cm, h_cm)
        skin = cls.calculate_skin_reinforcement(h_cm, b_cm)
        
        lb_inf = cls.calculate_anchorage(det_inf['phi_mm'], fck)
        lb_sup = cls.calculate_anchorage(det_sup['phi_mm'], fck)

        return {
            "inf": {
                "spec": f"{det_inf['count']} Φ {det_inf['phi_mm']}",
                "area": det_inf['area_cm2'],
                "lb": lb_inf
            },
            "sup": {
                "spec": f"{det_sup['count']} Φ {det_sup['phi_mm']}",
                "area": det_sup['area_cm2'],
                "lb": lb_sup
            },
            "skin": skin,
            "stirrups": design_res['shear']['stirrup_spec']
        }
