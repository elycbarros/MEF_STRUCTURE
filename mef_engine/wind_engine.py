"""
wind_engine.py - Núcleo de Análise de Vento conforme NBR 6123.
Este módulo é independente e pode ser integrado a qualquer solver estrutural.
"""
from dataclasses import dataclass
import math
from typing import Optional

@dataclass
class WindConfig:
    v0: float = 30.0  # Velocidade básica (m/s)
    s1: float = 1.0   # Fator topográfico
    s3: float = 1.0   # Fator estatístico
    categoria: int = 2
    classe: str = 'B'
    
    # Parâmetros Dinâmicos (Para edifícios altos / Cap 9)
    is_dynamic: bool = False
    f1: float = 0.5   # Frequência fundamental (Hz)
    zeta: float = 0.01 # Amortecimento crítico (0.01 a 0.02)
    beta: float = 1.0  # Expoente da forma modal (1.0 = linear)

def get_s2(z: float, categoria: int = 2, classe: str = 'B') -> float:
    """
    Calcula o fator S2 para análise ESTÁTICA (Tabela 2 NBR 6123).
    """
    params = {
        1: {'b': 1.10, 'p': 0.06, 'fr': 1.00},
        2: {'b': 1.00, 'p': 0.09, 'fr': 1.00},
        3: {'b': 0.94, 'p': 0.12, 'fr': 0.98},
        4: {'b': 0.86, 'p': 0.15, 'fr': 0.95},
        5: {'b': 0.74, 'p': 0.19, 'fr': 0.92}
    }
    classe_corr = {'A': 1.0, 'B': 0.95, 'C': 0.85}
    fr_base = params.get(categoria, params[2])['fr']
    b = params.get(categoria, params[2])['b']
    p = params.get(categoria, params[2])['p']
    fr = fr_base * classe_corr.get(classe, 1.0)
    if z <= 5: z = 5.0
    return b * fr * math.pow(z / 10.0, p)

def get_s2_dynamic(z: float, categoria: int = 2) -> float:
    """
    S2 para vento médio (Capítulo 9 - Modelo Discreto).
    S2 = b * (z/10)^p
    """
    params = {
        1: {'b': 1.10, 'p': 0.06},
        2: {'b': 1.00, 'p': 0.09},
        3: {'b': 0.94, 'p': 0.12},
        4: {'b': 0.86, 'p': 0.15},
        5: {'b': 0.74, 'p': 0.19}
    }
    p = params.get(categoria, params[2])['p']
    b = params.get(categoria, params[2])['b']
    if z <= 5:
        z = 5.0
    return b * math.pow(z / 10.0, p)

class WindEngine:
    def __init__(self, config: Optional[WindConfig] = None):
        self.config = config or WindConfig()

    def generate_force_profile(self, height: float, **kwargs) -> dict:
        """Versão de instância para facilitar chamadas com config injetada."""
        if 'config' not in kwargs:
            kwargs['config'] = self.config
        return WindEngine.generate_force_profile_static(height, **kwargs)

    @staticmethod
    def calculate_wind_speed(z: float, config: WindConfig) -> float:
        """
        Calcula a velocidade característica Vk (m/s) no nível z.
        """
        if config.is_dynamic:
            s2 = get_s2_dynamic(z, config.categoria)
        else:
            s2 = get_s2(z, config.categoria, config.classe)
        return config.v0 * config.s1 * s2 * config.s3

    @staticmethod
    def calculate_s2(z: float, config: WindConfig) -> float:
        """
        Retorna o fator S2 utilizado no nível z, mantendo rastreabilidade no perfil.
        """
        if config.is_dynamic:
            return get_s2_dynamic(z, config.categoria)
        return get_s2(z, config.categoria, config.classe)

    @staticmethod
    def calculate_dynamic_pressure(z: float, config: WindConfig) -> float:
        """
        Calcula a pressão dinâmica q (N/m2). 
        Se is_dynamic=True, utiliza o vento médio para posterior análise dinâmica.
        """
        vk = WindEngine.calculate_wind_speed(z, config)
        q = 0.613 * (vk ** 2)
        return q

    @staticmethod
    def calculate_level(
        z: float,
        area: float,
        cf: float,
        config: WindConfig,
        height: Optional[float] = None,
    ) -> dict:
        """
        Calcula os dados completos de um nível: S2, Vk, q e força.
        area em m2, força em N. Se config.is_dynamic=True, aplica o modelo discreto.
        """
        s2 = WindEngine.calculate_s2(z, config)
        vk = WindEngine.calculate_wind_speed(z, config)
        q = 0.613 * (vk ** 2)
        f_mean = q * area * cf
        force = f_mean
        dynamic_factor = 1.0

        if config.is_dynamic:
            ref_height = height if height is not None else max(z, 5.0)
            force = WindEngine.get_dynamic_discrete_force(z, ref_height, area, cf, config)
            dynamic_factor = force / f_mean if f_mean > 0 else 1.0

        return {
            "z": z,
            "s2": s2,
            "vk_m_s": vk,
            "q_Pa": q,
            "area_m2": area,
            "cf": cf,
            "f_mean_N": f_mean,
            "f_total_N": force,
            "f_total_kN": force / 1000.0,
            "moment_base_kNm": (force * z) / 1000.0,
            "dynamic_factor": dynamic_factor,
        }

    @staticmethod
    def get_dynamic_discrete_force(z: float, height: float, area: float, cf: float, config: WindConfig) -> float:
        """
        Implementa o Modelo Discreto (Capítulo 9 da NBR 6123).
        Calcula a força total (Média + Flutuante) no nível z.
        Refinado para edifícios de alta carga.
        """
        if not config.is_dynamic:
            return WindEngine.get_drag_force(z, area, cf, config)

        # 1. Parâmetros do Vento Médio no Topo (NBR 6123 - Cap 9)
        s2_topo = get_s2_dynamic(height, config.categoria)
        v_h = config.v0 * config.s1 * s2_topo * config.s3
        
        # 2. Frequência reduzida (x) e espectro de densidade (Sf)
        # L = 1200m (comprimento de escala de turbulência)
        x = (1200 * config.f1) / v_h
        # Espectro de Kármán simplificado conforme NBR 6123
        s_f = 0.6 * x / math.pow(1 + math.pow(x, 2), 5/6)
        
        # 3. Fator de Resposta Ressonante (R)
        # Considera amortecimento zeta (0.01-0.02)
        r = math.sqrt((math.pi / (4 * config.zeta)) * s_f)
        
        # 4. Fator de Pico (g) - NBR 6123 Eq. 9.11
        # t = 600s (intervalo de 10 min)
        t_sec = 600.0
        # g = sqrt(2 * ln(f1 * t)) + 0.577 / sqrt(2 * ln(f1 * t))
        sqrt_term = math.sqrt(2 * math.log(max(config.f1 * t_sec, 2.0)))
        g = sqrt_term + (0.577 / sqrt_term)
        
        # 5. Fator de Amplificação Dinâmica (xi)
        xi = 1 + (g * r)
        
        # 6. Força média e total no nível z
        q_mean = WindEngine.calculate_dynamic_pressure(z, config)
        f_mean = q_mean * area * cf
        
        # Para prédios altos, a componente ressonante é crítica
        return f_mean * xi

    @staticmethod
    def get_rectangular_drag_coefficient(h: float, b: float, d: float) -> float:
        """
        Calcula o Coeficiente de Arrasto (Cf) para edificações retangulares.
        Baseado na Tabela 4 da NBR 6123.
        h: Altura total
        b: Largura perpendicular ao vento
        d: Profundidade paralela ao vento
        """
        if h <= 0 or b <= 0 or d <= 0:
            raise ValueError("h, b e d devem ser positivos para calcular Cf.")

        lambda_h = h / b
        ratio_db = d / b
        
        # Interpolação simplificada da Tabela 4
        if lambda_h >= 6:
            cf = 1.9 if ratio_db <= 0.5 else 1.5 if ratio_db <= 1.0 else 1.2
        elif lambda_h >= 2:
            cf = 1.6 if ratio_db <= 0.5 else 1.3 if ratio_db <= 1.0 else 1.1
        else:
            cf = 1.3 if ratio_db <= 0.5 else 1.2 if ratio_db <= 1.0 else 1.0
            
        return cf

    @staticmethod
    def get_drag_force(z: float, area: float, cf: float, config: WindConfig) -> float:
        """
        Calcula a força de arrasto (N) em uma área exposta.
        Fa = q * area * Cf
        """
        q = WindEngine.calculate_dynamic_pressure(z, config)
        return q * area * cf

    @staticmethod
    def generate_vertical_profile(height: float, step: float = 1.0, config: WindConfig = WindConfig()):
        """
        Gera o perfil de pressões dinâmicas ao longo da altura.
        """
        profile = []
        z = 0.0
        while z <= height:
            q = WindEngine.calculate_dynamic_pressure(z, config)
            profile.append({"z": z, "q_Pa": q})
            z += step
        return profile

    @staticmethod
    def generate_force_profile_static(
        height: float,
        step: float = 3.0,
        config: Optional[WindConfig] = None,
        width: Optional[float] = None,
        depth: Optional[float] = None,
        cf: Optional[float] = None,
        area_per_level: Optional[float] = None,
        cf_manual: Optional[float] = None, # Alias para cf
        area_level: Optional[float] = None, # Alias para area_per_level
    ) -> dict:
        """
        Gera perfil rastreável de vento por nível, incluindo força e momento na base.

        Se area_per_level não for informado, usa width * step como área tributária.
        Se cf não for informado e width/depth existirem, calcula Cf para planta retangular.
        """
        if height <= 0:
            raise ValueError("height deve ser positivo.")
        if step <= 0:
            raise ValueError("step deve ser positivo.")

        cfg = config or WindConfig()
        effective_width = width if width is not None else 1.0
        effective_depth = depth if depth is not None else effective_width
        
        final_cf = cf if cf is not None else cf_manual
        drag_cf = final_cf if final_cf is not None else WindEngine.get_rectangular_drag_coefficient(
            height, effective_width, effective_depth
        )
        
        final_area = area_per_level if area_per_level is not None else area_level

        levels = []
        z = 0.0
        while z <= height + 1e-9:
            levels.append(round(z, 10))
            z += step
        if levels[-1] < height:
            levels.append(height)

        profile = []
        for idx, z in enumerate(levels):
            prev_z = levels[idx - 1] if idx > 0 else 0.0
            next_z = levels[idx + 1] if idx < len(levels) - 1 else height
            lower_bound = 0.0 if idx == 0 else (prev_z + z) / 2.0
            upper_bound = height if idx == len(levels) - 1 else (z + next_z) / 2.0
            tributary_height = max(upper_bound - lower_bound, 0.0)
            area = final_area if final_area is not None else effective_width * tributary_height
            profile.append(WindEngine.calculate_level(z, area, drag_cf, cfg, height=height))

        total_force_N = sum(item["f_total_N"] for item in profile)
        total_moment_kNm = sum(item["moment_base_kNm"] for item in profile)
        max_q = max((item["q_Pa"] for item in profile), default=0.0)
        max_force_kN = max((item["f_total_kN"] for item in profile), default=0.0)

        return {
            "config": {
                "v0": cfg.v0,
                "s1": cfg.s1,
                "s3": cfg.s3,
                "categoria": cfg.categoria,
                "classe": cfg.classe,
                "is_dynamic": cfg.is_dynamic,
                "f1": cfg.f1,
                "zeta": cfg.zeta,
            },
            "geometry": {
                "height_m": height,
                "step_m": step,
                "width_m": effective_width,
                "depth_m": effective_depth,
                "cf": drag_cf,
                "area_per_level_m2": final_area,
            },
            "summary": {
                "total_force_N": total_force_N,
                "total_force_kN": total_force_N / 1000.0,
                "base_moment_kNm": total_moment_kNm,
                "max_q_Pa": max_q,
                "max_force_level_kN": max_force_kN,
            },
            "profile": profile,
        }

if __name__ == "__main__":
    # Teste rápido
    cfg = WindConfig(v0=45.0) # Região sul do Brasil (ex: Floripa)
    engine = WindEngine()
    print(f"Pressão dinâmica a 10m: {engine.calculate_dynamic_pressure(10, cfg):.2f} Pa")
    print(f"Pressão dinâmica a 30m: {engine.calculate_dynamic_pressure(30, cfg):.2f} Pa")
