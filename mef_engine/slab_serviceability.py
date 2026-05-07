from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ServiceabilityConfig:
    fck: float = 30.0
    fyk: float = 500.0
    E_s: float = 210000.0 # MPa (Aço)
    h: float = 0.15
    bw: float = 1.0 # 1 metro
    bf: float = 1.0 # Largura da mesa (para seções T)
    hf: float = 0.05 # Espessura da mesa
    cover: float = 0.025
    t0_days: int = 28 
    t_inf_days: int = 1800 
    # Protensão
    p_force_kN: float = 0.0
    ecc_m: float = 0.0
    slab_type: str = "solid"

class SlabServiceabilityEngine:
    """
    Engine para Verificação de Estados Limites de Serviço (ELS) em Lajes.
    Focado em Flechas (NBR 6118:2023) com suporte a seções T e Protensão.
    """

    @staticmethod
    def get_Ecs(fck: float) -> float:
        Eci = 5600 * np.sqrt(fck) if fck <= 50 else 21500 * (fck/10 + 1.25)**(1/3)
        alpha_i = 0.8 + 0.2 * fck / 80
        if alpha_i > 1.0: alpha_i = 1.0
        return Eci * alpha_i

    @staticmethod
    def calculate_branson_inertia(ma_knm: float, as_cm2: float, cfg: ServiceabilityConfig) -> Dict[str, Any]:
        """
        Calcula a Inércia Equivalente de Branson (Ie) para seções retangulares ou T.
        """
        E_c = SlabServiceabilityEngine.get_Ecs(cfg.fck)
        n = cfg.E_s / E_c
        d = cfg.h - cfg.cover
        as_m2 = as_cm2 * 1e-4

        # 1. Propriedades da Seção Bruta (Ic)
        if cfg.slab_type in ["ribbed", "trussed"]:
            # Seção T
            area_gross = (cfg.bf * cfg.hf) + cfg.bw * (cfg.h - cfg.hf)
            yt = ((cfg.bf * cfg.hf * (cfg.h - cfg.hf/2)) + (cfg.bw * (cfg.h - cfg.hf) * ((cfg.h - cfg.hf)/2))) / area_gross
            I_c = (cfg.bf * cfg.hf**3)/12.0 + (cfg.bf * cfg.hf) * (cfg.h - cfg.hf/2 - yt)**2 + \
                  (cfg.bw * (cfg.h - cfg.hf)**3)/12.0 + (cfg.bw * (cfg.h - cfg.hf)) * (yt - (cfg.h - cfg.hf)/2)**2
        else:
            # Seção Retangular
            I_c = (cfg.bw * cfg.h**3) / 12.0
            yt = cfg.h / 2.0

        # 2. Momento de Fissuração (Mr) com efeito de Protensão
        fctm = 0.3 * (cfg.fck ** (2/3))
        
        # Pré-compressão na fibra tracionada (sigma_p)
        sigma_p = 0.0
        if cfg.slab_type == "prestressed" and cfg.p_force_kN > 0:
            # sigma = P/A + P*e/W
            area = cfg.bw * cfg.h
            w_inf = I_c / yt
            sigma_p = (cfg.p_force_kN / area) + (cfg.p_force_kN * cfg.ecc_m / w_inf) # kN/m2
            sigma_p /= 1000.0 # MPa

        # Mr = (alpha * fctm + sigma_p) * Ic / yt
        # alpha = 1.5 para seções retangulares, 1.2 para T (simplificado)
        alpha = 1.2 if cfg.slab_type in ["ribbed", "trussed"] else 1.5
        Mr = ((alpha * fctm + sigma_p) * 1e6 * I_c) / yt / 1000.0 # kNm

        # 3. Inércia Fissurada (Icr)
        # Para seção T, verifica se a linha neutra está na mesa ou na alma
        # bw * x^2 / 2 + (bf - bw) * hf * (x - hf/2) - n * As * (d - x) = 0
        # (bw/2) x^2 + ( (bf-bw)*hf + n*As ) x - ( (bf-bw)*hf^2 / 2 + n*As*d ) = 0
        if cfg.slab_type in ["ribbed", "trussed"]:
            A_quad = cfg.bw / 2.0
            B_quad = (cfg.bf - cfg.bw) * cfg.hf + n * as_m2
            C_quad = -((cfg.bf - cfg.bw) * (cfg.hf**2) / 2.0 + n * as_m2 * d)
            x_cr = (-B_quad + np.sqrt(B_quad**2 - 4 * A_quad * C_quad)) / (2 * A_quad)
            
            if x_cr <= cfg.hf:
                # Linha neutra na mesa -> Trata como retangular de largura bf
                A_rect = cfg.bf / 2.0
                B_rect = n * as_m2
                C_rect = -n * as_m2 * d
                x_cr = (-B_rect + np.sqrt(B_rect**2 - 4 * A_rect * C_rect)) / (2 * A_rect)
                I_cr = (cfg.bf * x_cr**3) / 3.0 + n * as_m2 * (d - x_cr)**2
            else:
                I_cr = (cfg.bw * x_cr**3) / 3.0 + (cfg.bf - cfg.bw) * cfg.hf**3 / 12.0 + \
                       (cfg.bf - cfg.bw) * cfg.hf * (x_cr - cfg.hf/2)**2 + n * as_m2 * (d - x_cr)**2
        else:
            # Retangular sólida
            A_rect = cfg.bw / 2.0
            B_rect = n * as_m2
            C_rect = -n * as_m2 * d
            x_cr = (-B_rect + np.sqrt(B_rect**2 - 4 * A_rect * C_rect)) / (2 * A_rect)
            I_cr = (cfg.bw * x_cr**3) / 3.0 + n * as_m2 * (d - x_cr)**2
        
        # 4. Inércia Equivalente (Branson)
        ma_abs = abs(ma_knm)
        if ma_abs <= Mr:
            I_e = I_c
        else:
            ratio = Mr / ma_abs
            I_e = (ratio**3) * I_c + (1 - ratio**3) * I_cr
            I_e = min(I_e, I_c)
            
        return {
            "I_c": float(I_c),
            "I_cr": float(I_cr),
            "I_e": float(I_e),
            "Mr_kNm": float(Mr),
            "is_cracked": bool(ma_abs > Mr),
            "reduction_factor": float(I_e / I_c) if I_c > 0 else 1.0,
            "sigma_p_MPa": float(sigma_p)
        }

    @staticmethod
    def get_alpha_f(rho_prime: float = 0.0) -> float:
        return 2.0 / (1 + 50 * rho_prime)

    def calculate_nonlinear_deflection(self, w_instant: float, Ma: float, As: float, cfg: ServiceabilityConfig) -> Dict[str, Any]:
        """
        Calcula a flecha total (imediata + diferida) usando Branson e Creep.
        """
        branson = self.calculate_branson_inertia(Ma, As, cfg)
        
        # Flecha imediata corrigida
        w_imm_corrected = w_instant / branson['reduction_factor']
        
        # Fator de longo prazo (Creep)
        alpha_f = self.get_alpha_f(0.0)
        w_total = w_imm_corrected * (1 + alpha_f)
        
        return {
            "flecha_imediata_mef_mm": float(w_instant),
            "Ie_Ic_ratio": float(branson['reduction_factor']),
            "flecha_imediata_corr_mm": float(w_imm_corrected),
            "alpha_f_creep": float(alpha_f),
            "flecha_longo_prazo_mm": float(w_total),
            "status_fissuracao": "FISSURADA" if branson['is_cracked'] else "NAO_FISSURADA",
            "Mr_kNm": branson['Mr_kNm'],
            "sigma_p_MPa": branson['sigma_p_MPa']
        }
