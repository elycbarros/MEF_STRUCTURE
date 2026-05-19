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
        """Seleciona barras longitudinais para cobrir a área necessária, suportando múltiplas camadas se necessário."""
        if As_required_cm2 <= 0:
            return {"phi_mm": 10.0, "count": 2, "layers": 1, "area_cm2": 1.57} # Mínimo 2 barras

        # Filtra bitolas usuais para vigas (10mm a 25mm)
        options = [r for r in COMMERCIAL_REBARS if 10.0 <= r.phi_mm <= 25.0]
        
        best_phi = 12.5
        best_count = 2
        best_layers = 1
        min_over_area = 1000.0
        best_rebar = None

        # available_width = b_cm - 2 * cobrimento_e_estribos (aproximado 3.5cm de cada lado)
        available_width = b_cm - 2 * 3.5

        for rebar in options:
            s_h_min = max(2.0, rebar.phi_mm / 10.0)
            n_max_per_layer = math.floor((available_width + s_h_min) / (rebar.phi_mm / 10.0 + s_h_min))
            n_max_per_layer = max(n_max_per_layer, 2) # Sempre pelo menos 2 barras por camada

            total_bars = math.ceil(As_required_cm2 / rebar.area_cm2)
            total_bars = max(total_bars, 2)
            
            layers_count = math.ceil(total_bars / n_max_per_layer)
            
            # Se precisar de mais de 3 camadas, descartamos a não ser que não haja outra opção
            if layers_count > 3:
                continue

            over_area = (total_bars * rebar.area_cm2) - As_required_cm2
            if 0 <= over_area < min_over_area:
                min_over_area = over_area
                best_phi = rebar.phi_mm
                best_count = total_bars
                best_layers = layers_count
                best_rebar = rebar

        # Fallback caso nenhuma bitola caiba em <= 3 camadas (evita falha silenciosa)
        if best_rebar is None:
            # Seleciona a maior bitola disponível (25mm) para minimizar o número de camadas
            rebar = options[-1] # 25mm
            s_h_min = max(2.0, rebar.phi_mm / 10.0)
            n_max_per_layer = math.floor((available_width + s_h_min) / (rebar.phi_mm / 10.0 + s_h_min))
            n_max_per_layer = max(n_max_per_layer, 2)
            total_bars = math.ceil(As_required_cm2 / rebar.area_cm2)
            total_bars = max(total_bars, 2)
            best_phi = rebar.phi_mm
            best_count = total_bars
            best_layers = math.ceil(total_bars / n_max_per_layer)
            best_rebar = rebar

        return {
            "phi_mm": best_phi,
            "count": best_count,
            "layers": best_layers,
            "area_cm2": round(best_count * best_rebar.area_cm2, 2)
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

    def calculate_al(d_cm: float, alpha: float = 45.0, theta: float = 45.0) -> float:
        """
        Calcula a decalagem do diagrama de momentos (al).
        al = 0.5 * d * (cot(theta) - cot(alpha))
        Para estribos verticais (alpha=90) e theta=45: al = 0.5 * d
        """
        # Convert to radians
        a_rad = math.radians(alpha)
        t_rad = math.radians(theta)
        
        # cot(x) = 1/tan(x)
        cot_theta = 1.0 / math.tan(t_rad)
        cot_alpha = 1.0 / math.tan(a_rad) if alpha != 90 else 0.0
        
        al = 0.5 * d_cm * (cot_theta - cot_alpha)
        return round(al, 1)

    @staticmethod
    def calculate_anchorage(phi_mm: float, fck: float, hook: bool = False) -> float:
        """
        Calcula o comprimento de ancoragem básico lb (cm).
        hook: Se True, aplica redução de 0.7 para barras tracionadas com gancho (NBR 6118, 9.4.2.4).
        """
        # fbd = n1 * n2 * n3 * fctd
        # n1=2.25 (boa aderência), n2=1.0 (phi < 32mm), n3=1.0 (CA-50)
        fctd = (0.21 * (fck**(2/3))) / 1.4 # MPa (fctk,inf / gamma_c)
        fbd = 2.25 * 1.0 * 1.0 * fctd # MPa
        
        # lb = (phi/4) * (fyd / fbd)
        lb = (phi_mm / 40.0) * (435.0 / fbd) # cm (fyd = 500/1.15 = 435 MPa)
        
        if hook:
            lb *= 0.7 # Redução normativa para ganchos
            
        return round(lb, 1)

    @staticmethod
    def calculate_lb_nec(lb_basic: float, As_calc: float, As_efet: float, 
                        alpha: float = 1.0, phi_mm: float = 10.0, 
                        is_compressed: bool = False) -> float:
        """
        Calcula o comprimento de ancoragem necessário (lb,nec).
        lb,nec = alpha * lb * (As,calc / As,efet) >= lb,min
        """
        if As_efet <= 0: return lb_basic
        
        # alpha=1.0 para barras sem ganchos, mas lb_basic já pode ter o 0.7 embutido
        ratio = max(As_calc / As_efet, 0.1) # Evitar lb_nec nulo
        lb_nec = alpha * lb_basic * ratio
        
        # lb,min para tração: max(0.3*lb, 10*phi, 10cm)
        # lb,min para compressão: max(0.6*lb, 15*phi, 10cm)
        if is_compressed:
            lb_min = max(0.6 * lb_basic, 1.5 * phi_mm / 10.0, 10.0)
        else:
            lb_min = max(0.3 * lb_basic, 1.0 * phi_mm / 10.0, 10.0)
            
        return round(max(lb_nec, lb_min), 1)

    @staticmethod
    def calculate_executive_geometry(L_beam_m: float, b_m: float, h_m: float, 
                                   det_inf: dict, det_sup: dict, al_cm: float) -> dict:
        """
        Gera as coordenadas (x, y) reais das barras para o desenho executivo.
        Unidades de saída: metros.
        """
        L = L_beam_m
        h = h_m
        cobrimento = 0.03 # 3cm default
        
        # 1. Armadura Inferior (N1)
        # Comprimento total = L + 2 * lb_nec (simplificado como engaste/apoio)
        lb_nec_inf_m = det_inf['lb_nec'] / 100.0
        
        # Coordenadas da barra inferior (incluindo gancho de 15cm se necessário)
        # Segmentos: (x1, y1) -> (x2, y2)
        n1_y = cobrimento + (det_inf['phi_mm']/2000.0)
        n1_coords = [
            {"x": 0.0, "y": n1_y + 0.15}, # Gancho inicial
            {"x": 0.0, "y": n1_y},
            {"x": L,   "y": n1_y},
            {"x": L,   "y": n1_y + 0.15}  # Gancho final
        ]
        
        # 2. Armadura Superior (N2)
        n2_y = h - cobrimento - (det_sup['phi_mm']/2000.0)
        n2_coords = [
            {"x": 0.0, "y": n2_y - 0.15},
            {"x": 0.0, "y": n2_y},
            {"x": L,   "y": n2_y},
            {"x": L,   "y": n2_y - 0.15}
        ]
        
        return {
            "n1": {
                "label": "N1",
                "phi": det_inf['phi_mm'],
                "count": det_inf['count'],
                "coords": n1_coords,
                "total_length_m": round(L + 0.30, 2) # L + 2*gancho
            },
            "n2": {
                "label": "N2",
                "phi": det_sup['phi_mm'],
                "count": det_sup['count'],
                "coords": n2_coords,
                "total_length_m": round(L + 0.30, 2)
            }
        }

    @classmethod
    def generate_detailing_summary(cls, design_res: dict, b_m: float, h_m: float, fck: float, 
                                 L_beam_m: float = 5.0,
                                 hook_inf: bool = True, hook_sup: bool = True) -> dict:
        """Compila o resumo de detalhamento para a viga."""
        b_cm = b_m * 100
        h_cm = h_m * 100
        d_cm = h_cm - 4.0 # Estimativa de d
        
        # Obter áreas calculadas (cm2)
        As_inf_calc = design_res.get('flexure_bottom', {}).get('As_cm2', 0.0)
        As_sup_calc = design_res.get('flexure_top', {}).get('As_cm2', 0.0)
        
        det_inf = cls.select_reinforcement(As_inf_calc, b_cm, h_cm)
        det_sup = cls.select_reinforcement(As_sup_calc, b_cm, h_cm)
        
        # Calcular d real com base na disposição real das camadas
        def calculate_d_real(det: dict) -> float:
            layers = det.get('layers', 1)
            phi = det.get('phi_mm', 10.0)
            phi_cm = phi / 10.0
            if layers <= 1:
                return h_cm - (3.0 + phi_cm / 2.0)
            y_layers = []
            y_current = 3.0 + phi_cm / 2.0
            y_layers.append(y_current)
            for j in range(1, layers):
                y_current += max(2.0, phi_cm) + phi_cm
                y_layers.append(y_current)
            y_G = sum(y_layers) / len(y_layers)
            return max(h_cm - y_G, h_cm * 0.5)
            
        d_inf_cm = calculate_d_real(det_inf)
        d_sup_cm = calculate_d_real(det_sup)
        d_mean_cm = (d_inf_cm + d_sup_cm) / 2.0
        
        # Decalagem (Módulo 7)
        al = cls.calculate_al(d_mean_cm)
        
        # Ancoragens (Módulo 6)
        lb_basic_inf = cls.calculate_anchorage(det_inf['phi_mm'], fck, hook=hook_inf)
        lb_nec_inf = cls.calculate_lb_nec(lb_basic_inf, As_inf_calc, det_inf['area_cm2'], phi_mm=det_inf['phi_mm'])
        det_inf['lb_nec'] = lb_nec_inf
        
        lb_basic_sup = cls.calculate_anchorage(det_sup['phi_mm'], fck, hook=hook_sup)
        lb_nec_sup = cls.calculate_lb_nec(lb_basic_sup, As_sup_calc, det_sup['area_cm2'], phi_mm=det_sup['phi_mm'])
        det_sup['lb_nec'] = lb_nec_sup

        # Geometria Executiva
        exec_geo = cls.calculate_executive_geometry(L_beam_m, b_m, h_m, det_inf, det_sup, al)

        Asl_torsion = design_res.get('shear', {}).get('Asl_torsion_cm2', 0.0)
        
        # ELS - Fissuração
        M_service = design_res.get('flexure_bottom', {}).get('M_service_kNm', 0.0)
        service_inf = ServiceabilityEngine.calculate_crack_width(
            fck, b_cm, h_cm, det_inf['area_cm2'], M_service, det_inf['phi_mm']
        )

        return {
            "geometry": {"b_cm": b_cm, "h_cm": h_cm, "d_cm": round(d_mean_cm, 1), "al_cm": al, "L_m": L_beam_m},
            "inf": {
                "spec": f"{det_inf['count']} Φ {det_inf['phi_mm']}",
                "phi_mm": det_inf['phi_mm'],
                "count": det_inf['count'],
                "area_efet": det_inf['area_cm2'],
                "area_calc": As_inf_calc,
                "lb_basic": lb_basic_inf,
                "lb_nec": lb_nec_inf,
                "service": service_inf
            },
            "sup": {
                "spec": f"{det_sup['count']} Φ {det_sup['phi_mm']}",
                "phi_mm": det_sup['phi_mm'],
                "count": det_sup['count'],
                "area_efet": det_sup['area_cm2'],
                "area_calc": As_sup_calc,
                "lb_basic": lb_basic_sup,
                "lb_nec": lb_nec_sup
            },
            "executive": exec_geo,
            "skin": cls.calculate_skin_reinforcement(h_cm, b_cm),
            "torsion": {
                "Asl_cm2": Asl_torsion,
                "status": "REQUERIDA" if Asl_torsion > 0 else "NÃO REQUERIDA"
            },
            "stirrups": design_res.get('shear', {}).get('stirrup_spec', "N/A")
        }

class ServiceabilityEngine:
    """Motor de Verificação de Estados Limites de Serviço (ELS) — NBR 6118."""

    @staticmethod
    def calculate_crack_width(fck: float, b_cm: float, h_cm: float, As_efet: float, 
                             M_service: float, phi_mm: float) -> Dict:
        """
        Calcula a abertura de fissuras wk (NBR 6118 §17.3.3).
        M_service: Momento fletor de serviço (kN.m)
        """
        if M_service <= 0: return {"wk_mm": 0.0, "status": "OK"}
        
        d_cm = h_cm - 4.0
        # Simplificação: sigma_s (tensão na armadura)
        # z approx 0.85*d
        sigma_s = (M_service * 100.0) / (As_efet * 0.85 * d_cm) # kN/cm2
        sigma_s_mpa = sigma_s * 10.0
        
        # fctm = 0.3 * fck^(2/3)
        fctm = 0.3 * (fck**(2/3))
        # fct,inf = 0.7 * fctm
        fct_inf = 0.7 * fctm
        
        # wk = min(wk1, wk2)
        # Simplificado para ambiente CAA II (wk_max = 0.3mm)
        # wk1 = (phi / (12.5 * eta)) * (sigma_s / E) * (3 * sigma_s / fct_inf)
        # Usaremos formulação simplificada usual de projeto:
        wk = (phi_mm / 12.5) * (sigma_s_mpa / 210000.0) * (450.0 / sigma_s_mpa + 45) / 10.0 # cm -> mm
        wk = round(wk * 10, 3)
        
        return {
            "wk_mm": wk,
            "wk_max_mm": 0.3,
            "status": "OK" if wk <= 0.3 else "VERIFICAR",
            "sigma_s_mpa": round(sigma_s_mpa, 1)
        }

    @staticmethod
    def calculate_effective_inertia(E_mpa: float, fctm_mpa: float, I_gross: float, 
                                   I_cracked: float, M_cracking: float, M_service: float) -> float:
        """
        Calcula a inércia equivalente de Branson (NBR 6118 §17.3.2.1.1).
        Ie = (Mr/Ma)^3 * Ig + [1 - (Mr/Ma)^3] * Icr
        """
        if M_service <= abs(M_cracking):
            return I_gross
            
        ratio = (abs(M_cracking) / abs(M_service))**3
        I_e = ratio * I_gross + (1 - ratio) * I_cracked
        return min(I_e, I_gross)
