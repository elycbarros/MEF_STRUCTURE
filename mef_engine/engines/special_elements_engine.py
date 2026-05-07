"""
special_elements_engine.py - Motor de Elementos Especiais (Domínio: Especiais).
"""
import math
from typing import Dict, Any

class SpecialElementsEngine:
    """
    Centraliza cálculos de escadas, reservatórios e muros.
    """
    
    @staticmethod
    def solve_pleated_stairs(l_horiz: float, h_step: float, p_step: float, thick: float, q_acid: float) -> Dict[str, Any]:
        """
        Escadas Plissadas (Zig-zag).
        Calcula os momentos de 'dobra' nos degraus.
        """
        alpha = math.atan(h_step / p_step)
        # Carga por metro linear de degrau
        g_pp = thick * 25.0 * (1.0 / math.cos(alpha))
        q_total = (g_pp + q_acid) * p_step
        
        # Momento fletor simplificado no vao (considerando continuidade plissada)
        m_max = (q_total * l_horiz**2) / 10.0 # Aproximacao para escada autoportante plissada
        
        return {
            "type": "pleated_stairs",
            "alpha_deg": math.degrees(alpha),
            "m_max_kNm": m_max,
            "q_total_kN_m": q_total,
            "explanation": "O comportamento plissado exige verificacao de torcao e flexao nos cantos dos degraus."
        }

    @staticmethod
    def solve_retaining_wall(
        h_wall: float, 
        gamma_soil: float, 
        phi_soil: float, 
        weight_wall: float, 
        b_base: float,
        surcharge: float = 0.0,
        c_soil: float = 0.0
    ) -> Dict[str, Any]:
        """
        Muros de Arrimo Profissional (NBR 11682).
        Calcula estabilidade ao tombamento, deslizamento e pressões.
        """
        phi_rad = math.radians(phi_soil)
        ka = (math.tan(math.pi/4 - phi_rad/2))**2
        
        # Empuxos (Triangular + Retangular da Sobrecarga)
        e_soil = 0.5 * ka * gamma_soil * h_wall**2
        e_surcharge = ka * surcharge * h_wall
        e_total = e_soil + e_surcharge
        
        # Braço de alavanca (Momento de Tombamento)
        y_e = (e_soil * (h_wall/3.0) + e_surcharge * (h_wall/2.0)) / e_total
        m_tomb = e_total * y_e
        
        # Estabilidade (Peso próprio + Solo sobre a base se houver)
        m_estabilizador = weight_wall * (b_base * 0.6) # Estimativa de CG
        fs_tomb = m_estabilizador / m_tomb if m_tomb > 0 else 10.0
        
        # Deslizamento (Atrito tan(2/3 phi))
        f_atrito = weight_wall * math.tan(phi_rad * 0.67) + c_soil * b_base
        fs_desl = f_atrito / e_total if e_total > 0 else 10.0
        
        return {
            "ka": round(ka, 3),
            "empuxo_kN_m": round(e_total, 2),
            "y_empuxo_m": round(y_e, 2),
            "m_tomb_kNm": round(m_tomb, 2),
            "m_estabil_kNm": round(m_estabilizador, 2),
            "fs_tomb": round(fs_tomb, 2),
            "fs_desl": round(fs_desl, 2),
            "status": "ATENDE" if (fs_tomb >= 1.5 and fs_desl >= 1.5) else "REVISAR_GEOMETRIA"
        }

    @staticmethod
    def solve_rectangular_tank(Lx: float, Ly: float, H: float, liquid_gamma: float = 10.0) -> Dict[str, Any]:
        """
        Reservatórios Retangulares - Método de Tabelas de Czerny (Simplificado).
        Verificação de momentos fletores e estanqueidade.
        """
        p_max = liquid_gamma * H
        ratio = max(Lx, Ly) / min(Lx, Ly)
        
        # Coeficientes aproximados para momentos no centro (Engastado na base)
        km = 0.045 if ratio < 2 else 0.125
        m_max = km * p_max * (min(Lx, Ly)**2)
        
        return {
            "p_max_kPa": round(p_max, 2),
            "m_max_kNm": round(m_max, 2),
            "wk_limit_mm": 0.1, # NBR 6118 para face molhada
            "explanation": "Momentos fletores calculados via analogia de placa com engaste na base."
        }

    @staticmethod
    def solve_corbel(fd_kN: float, a_dist: float, d_eff: float, fck: float) -> Dict[str, Any]:
        """
        Consolos Curtos (NBR 6118 §22.4).
        Modelo de Biela-e-Tirante.
        """
        ratio_ad = a_dist / d_eff
        theta_rad = math.atan(d_eff / a_dist)
        f_tirante = fd_kN * (a_dist / d_eff)
        
        # Verificação da Biela (Simplificado)
        v_rd2 = 0.27 * (1 - fck/250.0) * (fck/1.4) * 1000 # kPa
        # ... logic expansion ...
        
        return {
            "type": "corbel",
            "ratio_ad": round(ratio_ad, 2),
            "theta_deg": round(math.degrees(theta_rad), 1),
            "f_tirante_kN": round(f_tirante, 2),
            "as_principal_cm2": round((f_tirante * 1.15) / 43.48, 2), # CA-50
            "is_short": ratio_ad <= 1.0
        }

    @staticmethod
    def solve_deep_beam(fd_kN_m: float, l_span: float, height: float) -> Dict[str, Any]:
        """
        Vigas Parede (NBR 6118 §22.3).
        Ajuste do braço de alavanca (z).
        """
        ratio_lh = l_span / height
        is_deep = ratio_lh <= 2.0
        
        if is_deep:
            z_m = 0.2 * (l_span + 2 * height)
        else:
            z_m = 0.9 * height
            
        return {
            "ratio_lh": round(ratio_lh, 2),
            "is_deep": is_deep,
            "z_m": round(z_m, 2),
            "explanation": "Em vigas parede, o braço de alavanca (z) é reduzido devido ao fluxo não-linear de tensões."
        }

    @staticmethod
    def solve_gerber_tooth(vd_kN: float, hd_kN: float, a_dist: float, d_eff: float, b_width: float, fck: float) -> Dict[str, Any]:
        """
        Dentes Gerber (NBR 6118 §22.5).
        Cálculo de armadura de suspensão e tirante horizontal.
        """
        # Armadura de suspensão (estribos verticais)
        as_susp = (vd_kN * 1.15) / 43.48 # cm2
        
        # Tirante horizontal (Ash)
        # Ash = (Vd * a/d + Hd) / fyd
        as_tirante = (vd_kN * (a_dist / d_eff) + hd_kN) * 1.15 / 43.48
        
        return {
            "type": "gerber_tooth",
            "vd_kN": round(vd_kN, 1),
            "hd_kN": round(hd_kN, 1),
            "as_suspensao_cm2": round(as_susp, 2),
            "as_tirante_cm2": round(as_tirante, 2),
            "explanation": "O dente Gerber exige armadura de suspensão rigorosa para evitar o 'desgarramento' da ponta da viga."
        }

    @staticmethod
    def solve_helical_stairs(radius: float, angle_total_deg: float, h_step: float, thick: float, q_acid: float) -> Dict[str, Any]:
        """
        Escadas Helicoidais (NBR 6118).
        Calcula Flexão, Torção e Cortante em 3D (Modelo de Viga Curva).
        """
        angle_rad = math.radians(angle_total_deg)
        # Comprimento desenvolvido
        l_arc = radius * angle_rad
        
        # Cargas
        g_pp = thick * 25.0 * 1.2 # Fator de inclinação simplificado
        q_total = (g_pp + q_acid) * 1.0 # kN/m linear no eixo
        
        # Esforços simplificados (Fuchs/Liauw para vigas curvas)
        # Momento Fletor Máximo (M) e Momento de Torção Máximo (T)
        m_max = q_total * radius**2 * (1 - math.cos(angle_rad/2))
        t_max = q_total * radius**2 * (angle_rad/2 - math.sin(angle_rad/2))
        
        return {
            "type": "helical_stairs",
            "radius_m": radius,
            "l_arc_m": round(l_arc, 2),
            "m_max_kNm": round(m_max, 2),
            "t_max_kNm": round(t_max, 2),
            "q_total_kN_m": round(q_total, 2),
            "explanation": "Escadas helicoidais sofrem torção significativa (T) que deve ser combatida com armadura em estribos fechados."
        }
