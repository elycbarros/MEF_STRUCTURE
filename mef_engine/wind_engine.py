"""
wind_engine.py — Motor de Analise de Vento e Estabilidade Global (NBR 6123 / 6118).
"""
import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class WindConfig:
    v0: float = 30.0    # Velocidade basica (m/s)
    s1: float = 1.0     # Fator topografico
    s2_class: str = "B" # Categoria de rugosidade
    s3: float = 1.0     # Fator estatistico
    height: float = 30.0
    width_x: float = 12.0
    width_y: float = 20.0
    categoria: int = 2
    classe: str = "B"
    is_dynamic: bool = False
    f1: float = 0.5
    zeta: float = 0.01
    beta: float = 1.0

class WindEngine:
    """Motor de analise de vento e estabilidade global."""

    def __init__(self, cfg: WindConfig | None = None):
        self.cfg = cfg or WindConfig()
        self.v0 = self.cfg.v0
        self.s1 = self.cfg.s1
        self.s3 = self.cfg.s3
        self.categoria = self.cfg.categoria
        self.classe = self.cfg.classe

    @staticmethod
    def get_s2_parameters(category: str | int = "II", class_size: str = "B") -> dict:
        """Obtém os parâmetros b, p, fr conforme a Tabela 2 da NBR 6123."""
        cat_map = {
            "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5
        }
        
        cat_str = str(category).upper().replace("CAT", "").replace("EGORIA", "").strip()
        cat_idx = cat_map.get(cat_str, cat_map.get(category, 2))
        
        cls_str = str(class_size).upper()
        if cls_str not in ["A", "B", "C"]:
            cls_str = "B"
            
        # NBR 6123 Tabela 2
        params = {
            'A': {
                1: {'b': 1.10, 'p': 0.06, 'fr': 1.06},
                2: {'b': 1.00, 'p': 0.085, 'fr': 1.00},
                3: {'b': 0.94, 'p': 0.10, 'fr': 0.94},
                4: {'b': 0.86, 'p': 0.125, 'fr': 0.86},
                5: {'b': 0.74, 'p': 0.17, 'fr': 0.74}
            },
            'B': {
                1: {'b': 1.10, 'p': 0.075, 'fr': 1.04},
                2: {'b': 1.00, 'p': 0.10, 'fr': 0.98},
                3: {'b': 0.94, 'p': 0.115, 'fr': 0.92},
                4: {'b': 0.86, 'p': 0.14, 'fr': 0.84},
                5: {'b': 0.74, 'p': 0.19, 'fr': 0.72}
            },
            'C': {
                1: {'b': 1.10, 'p': 0.10, 'fr': 1.01},
                2: {'b': 1.00, 'p': 0.12, 'fr': 0.95},
                3: {'b': 0.94, 'p': 0.14, 'fr': 0.89},
                4: {'b': 0.86, 'p': 0.17, 'fr': 0.80},
                5: {'b': 0.74, 'p': 0.23, 'fr': 0.67}
            }
        }
        
        p_dict = params[cls_str][cat_idx]
        
        # Limite inferior de altura conforme tabela 2
        z_min_map = {1: 2.0, 2: 5.0, 3: 10.0, 4: 15.0, 5: 20.0}
        z_min = z_min_map.get(cat_idx, 5.0)
        
        return {
            'b': p_dict['b'],
            'p': p_dict['p'],
            'fr': p_dict['fr'],
            'z_min': z_min,
            'cat_idx': cat_idx,
            'cls_str': cls_str
        }

    @staticmethod
    def calculate_s2(z: float, category: str | int = "II", class_size: str = "B") -> float:
        """Calcula o fator S2 conforme NBR 6123 Tabela 2."""
        params = WindEngine.get_s2_parameters(category, class_size)
        z_calc = max(z, params['z_min'])
        return params['b'] * params['fr'] * (z_calc / 10.0)**params['p']


    @classmethod
    def calculate_dynamic_pressure(cls, z_or_cfg, cfg: WindConfig | None = None) -> float | Dict:
        """
        Calcula a pressão dinâmica (q = 0.613 * vk^2).
        Suporta duas assinaturas:
        1. cls.calculate_dynamic_pressure(cfg) -> Retorna Dict (perfil completo de pressões)
        2. cls.calculate_dynamic_pressure(z, cfg) -> Retorna float (pressão em z específica)
        """
        if isinstance(z_or_cfg, WindConfig):
            cfg_obj = z_or_cfg
            results = []
            for z in range(0, int(cfg_obj.height) + 5, 5):
                if z == 0: z = 2.0 # Evitar zero
                s2 = cls.calculate_s2(z, category=cfg_obj.categoria, class_size=cfg_obj.classe)
                vk = cfg_obj.v0 * cfg_obj.s1 * s2 * cfg_obj.s3
                q = 0.613 * (vk**2) # N/m2
                results.append({"z": z, "vk": round(vk, 2), "q_Pa": round(q, 1)})
            
            # Coeficiente de Arraste (Ca) simplificado para retangulo
            ca = 1.2 
            force_total_kN = (results[-1]['q_Pa'] * cfg_obj.width_x * cfg_obj.height * ca) / 1000.0
            
            return {
                "profile": results,
                "force_total_kN": round(force_total_kN, 1),
                "ca": ca
            }
        else:
            z = float(z_or_cfg)
            cfg_obj = cfg
            s2 = cls.calculate_s2(z, category=cfg_obj.categoria, class_size=cfg_obj.classe)
            vk = cfg_obj.v0 * cfg_obj.s1 * s2 * cfg_obj.s3
            q = 0.613 * (vk**2)
            return q

    @staticmethod
    def estimate_gamma_z(total_height: float, total_load_kN: float, delta_h_mm: float) -> float:
        """Estimativa simplificada do coeficiente gamma_z."""
        if total_height > 40: return 1.12
        if total_height > 20: return 1.07
        return 1.03

    def calculate_dynamic_gust_factor(self, height: float, width: float, f1_hz: float, zeta: float = 0.01) -> float:
        """
        Calcula o fator de rajada dinâmico (G) conforme NBR 6123 Anexo I.
        f1_hz: Frequência natural fundamental
        zeta: Coeficiente de amortecimento crítico (ex: 0.01 para concreto)
        """
        # Parâmetros simplificados para vento Davenport
        v_h = self.v0 * self.calculate_s2(height, category=self.categoria, class_size=self.classe)
        
        # 1. Parâmetro de escala (L)
        l_scale = 1200.0 # m (Escala de turbulência)
        
        # 2. Frequência reduzida (xL)
        xL = (f1_hz * l_scale) / v_h if v_h > 0 else 1.0
        
        # 3. Densidade espectral (S)
        s_spect = (2/3) * (xL**2) / (1 + xL**2)**(4/3)
        
        # 4. Admitância aerodinâmica (Rh, Rb)
        rh = 1 / (1 + 2 * f1_hz * height / v_h) if v_h > 0 else 1.0
        rb = 1 / (1 + 2 * f1_hz * width / v_h) if v_h > 0 else 1.0
        
        # 5. Fator de rajada G
        # G = 1 + r * sqrt(B + R) onde B é background e R é ressonância
        # Simplificação para laboratório estrutural:
        r_turb = 0.15 # Intensidade de turbulência
        b_background = 0.6
        res_resonance = (math.pi / (4 * zeta)) * s_spect * rh * rb
        
        g_factor = 1 + 2 * r_turb * math.sqrt(b_background + res_resonance)
        return round(g_factor, 3)

    def calculate_top_acceleration(self, height: float, width: float, total_mass_kg: float, 
                                 f1_hz: float, v0: float) -> float:
        """
        Calcula a aceleração de pico no topo para conforto humano (m/s2).
        Conforme ISO 10137 e NBR 6123.
        """
        v_h = v0 * self.calculate_s2(height, category=self.categoria, class_size=self.classe)
        q_h = 0.613 * (v_h**2)
        
        # Força RMS aproximada
        # acc = (Force_rms * Resonant_factor) / Mass
        # Simplificado para projeto pedagógico de alta fidelidade:
        rho_air = 1.225
        cf = 1.2
        
        # Fator dinâmico simplificado (Davenport)
        acc_rms = (q_h * width * cf * 0.15) / total_mass_kg
        acc_peak = acc_rms * 3.5 # Peak factor g ≈ 3.5
        
        return round(acc_peak, 4)

    def generate_force_profile(self, height: float, width: float, depth: float, 
                               step: float = 1.0, area_level: float = None, 
                               cf_manual: float = None, is_dynamic: bool = False,
                               f1_hz: float = 0.5) -> Dict:
        """
        Gera o perfil completo de forças de vento conforme NBR 6123.
        Se is_dynamic=True, aplica o fator de rajada dinâmico.
        """
        results = []
        total_force_kN = 0.0
        base_moment_kNm = 0.0
        
        cf = cf_manual if cf_manual is not None else 1.2
        g_dynamic = self.calculate_dynamic_gust_factor(height, width, f1_hz) if is_dynamic else 1.0
        
        z = 0.0
        while z <= height:
            z_calc = max(1.0, z)
            s2 = self.calculate_s2(z_calc, category=self.categoria, class_size=self.classe)
            vk = self.v0 * self.s1 * s2 * self.s3
            q_Pa = 0.613 * (vk**2)
            
            area = (area_level if area_level else width * step)
            # Aplica G se dinâmico
            force_kN = (q_Pa * area * cf * g_dynamic) / 1000.0
            
            results.append({
                "z": round(z, 2),
                "vk": round(vk, 2),
                "q_Pa": round(q_Pa, 1),
                "force_kN": round(force_kN, 2)
            })
            
            total_force_kN += force_kN
            base_moment_kNm += force_kN * z
            
            z += step
            if z > height and z - step < height: z = height

        return {
            "profile": results,
            "summary": {
                "total_force_kN": round(total_force_kN, 1),
                "base_moment_kNm": round(base_moment_kNm, 1),
                "max_vk": round(results[-1]['vk'], 2),
                "max_q_Pa": round(results[-1]['q_Pa'], 1),
                "cf_used": cf,
                "g_dynamic": g_dynamic
            }
        }
