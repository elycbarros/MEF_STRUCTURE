from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

@dataclass
class SlabDesignConfig:
    fck: float = 30.0
    fyk: float = 500.0
    h: float = 0.15  # Espessura típica de laje suspensa
    Lx: float = 5.0
    Ly: float = 5.0
    cover: float = 0.025 # Cobrimento menor para lajes elevadas (CAA I/II)
    gamma_s: float = 1.15
    gamma_c: float = 1.4
    gamma_f: float = 1.4
    wk_limit_mm: float = 0.30
    bar_diameter_mm: float = 10.0
    eta1: float = 2.25 # Coeficiente de aderência (nervurado)
    slab_type: str = 'solid'
    b_nerv: float = 0.10
    dist_nerv: float = 0.50
    h_mesa: float = 0.05

class SlabDesignEngine:
    """
    Motor de dimensionamento para Lajes Suspensas conforme NBR 6118:2023.
    """
    def __init__(self, config: SlabDesignConfig | None = None):
        self.config = config or SlabDesignConfig()

    @staticmethod
    def get_fctm(fck: float) -> float:
        """Resistência média à tração (MPa)"""
        if fck <= 50:
            return 0.3 * (fck ** (2/3))
        else:
            return 2.12 * np.log(1 + 0.11 * fck)

    @staticmethod
    def calculate_flexure_section(md_knm_m: float, cfg: SlabDesignConfig) -> Dict[str, Any]:
        """
        Dimensionamento da seção (Retangular ou T) à flexão simples (ELU).
        """
        fcd = cfg.fck / cfg.gamma_c
        fyd = cfg.fyk / cfg.gamma_s
        d = cfg.h - cfg.cover - (cfg.bar_diameter_mm / 2000.0)
        
        is_ribbed = cfg.slab_type in ['ribbed', 'trussed', 'hollow_core']
        bf = cfg.dist_nerv if is_ribbed else 1.0 # Largura da mesa (flange)
        bw = cfg.b_nerv if is_ribbed else 1.0    # Largura da nervura (web)
        hf = cfg.h_mesa if is_ribbed else cfg.h # Espessura da mesa
        
        # md_knm_m para Nm (por metro ou por nervura se for T)
        # Se for nervurada, o momento que chega é kNm/m, precisamos do momento por nervura
        md_nm = abs(md_knm_m) * 1000.0 * (cfg.dist_nerv if is_ribbed else 1.0)
        
        alpha_cc = 0.85
        lambda_c = 0.8
        psi = 0.4
        if cfg.fck > 50:
            lambda_c = 0.8 - (cfg.fck - 50) / 400
            psi = 0.4 - (cfg.fck - 50) / 1000
            alpha_cc = 0.85 * (1 - (cfg.fck - 50) / 200)

        # 1. Tenta como seção retangular de largura bf (mesa)
        a = psi * (lambda_c**2) * (alpha_cc * (fcd * 1e6) * bf)
        b = -lambda_c * d * (alpha_cc * (fcd * 1e6) * bf)
        c = md_nm
        
        delta = b**2 - 4 * a * c
        if delta < 0:
            return {"error": "Seção superdimensionada", "as_req": 0}
            
        x = (-b - np.sqrt(delta)) / (2 * a)
        
        # Verifica se a linha neutra está na mesa (x <= hf/lambda_c)
        if x * lambda_c <= hf:
            # Caso 1: Seção retangular de largura bf
            x_d = x / d
            limit_xd = 0.45 if cfg.fck <= 50 else 0.35
            as_req = md_nm / (fyd * 1e6 * (d - psi * lambda_c * x))
        else:
            # Caso 2: Seção T verdadeira (LN na nervura)
            if not is_ribbed:
                # Se não for nervurada mas passou da mesa (impossível se hf=h), trata como erro
                return {"error": "Erro de geometria", "as_req": 0}
            
            # Momento resistido pelas abas (mesa fora da nervura)
            area_abas = (bf - bw) * hf
            md_abas = area_abas * (alpha_cc * fcd * 1e6) * (d - hf/2.0)
            
            # Momento restante para a nervura
            md_nerv = md_nm - md_abas
            
            if md_nerv < 0: # Mesa sozinha já resiste
                 as_req = md_nm / (fyd * 1e6 * (d - hf/2.0))
            else:
                # Dimensiona a nervura como retangular de largura bw
                a_n = psi * (lambda_c**2) * (alpha_cc * (fcd * 1e6) * bw)
                b_n = -lambda_c * d * (alpha_cc * (fcd * 1e6) * bw)
                c_n = md_nerv
                delta_n = b_n**2 - 4 * a_n * c_n
                if delta_n < 0: return {"error": "Nervura superdimensionada", "as_req": 0}
                x = (-b_n - np.sqrt(delta_n)) / (2 * a_n)
                
                as_req_nerv = md_nerv / (fyd * 1e6 * (d - psi * lambda_c * x))
                as_req_abas = md_abas / (fyd * 1e6 * (d - hf/2.0))
                as_req = as_req_nerv + as_req_abas

        as_req_cm2 = as_req * 1e4
        # Se for nervurada, as_req_cm2 é por nervura. Precisamos converter para cm2/m
        if is_ribbed:
            as_req_cm2 = as_req_cm2 / cfg.dist_nerv

        fctm = SlabDesignEngine.get_fctm(cfg.fck)
        rho_min = max(0.0015, 0.233 * fctm / cfg.fyk)
        as_min = rho_min * (bw * cfg.h if is_ribbed else 1.0 * cfg.h) * 1e4
        if is_ribbed: as_min = as_min / cfg.dist_nerv # as_min por metro
        
        return {
            "x_m": x,
            "as_final_cm2": max(as_req_cm2, as_min)
        }

    def design_from_mef(self, res: Any) -> Dict[str, Any]:
        """
        Processa os resultados do solver MEF e calcula armaduras para cada elemento.
        """
        elements = []
        for i in range(len(res.mx)):
            mx = res.mx[i] / 1000.0 # kNm/m
            my = res.my[i] / 1000.0 # kNm/m
            
            # Bottom (Positive) - moments that cause tension at the bottom
            rx_bot = self.calculate_flexure_section(mx if mx > 0 else 0, self.config)
            ry_bot = self.calculate_flexure_section(my if my > 0 else 0, self.config)
            
            # Top (Negative) - moments that cause tension at the top
            rx_top = self.calculate_flexure_section(mx if mx < 0 else 0, self.config)
            ry_top = self.calculate_flexure_section(my if my < 0 else 0, self.config)
            
            elements.append({
                "mx": mx,
                "my": my,
                "Asx_bottom": rx_bot.get("as_final_cm2", 0.0),
                "Asy_bottom": ry_bot.get("as_final_cm2", 0.0),
                "Asx_top": rx_top.get("as_final_cm2", 0.0),
                "Asy_top": ry_top.get("as_final_cm2", 0.0)
            })
            
        as_x_bot_max = max([e["Asx_bottom"] for e in elements])
        as_y_bot_max = max([e["Asy_bottom"] for e in elements])
        as_x_top_max = max([e["Asx_top"] for e in elements])
        as_y_top_max = max([e["Asy_top"] for e in elements])
        
        # Estimativa de Consumo
        area = self.config.Lx * self.config.Ly
        vol_concrete = area * self.config.h
        
        # Média simples para estimativa de peso (kg)
        as_mean_cm2_m2 = (np.mean([e["Asx_bottom"] + e["Asy_bottom"] + e["Asx_top"] + e["Asy_top"] for e in elements]))
        steel_weight_kg = as_mean_cm2_m2 * 1e-4 * area * 7850.0
        
        return {
            "elements": elements,
            "as_x_bottom_max": as_x_bot_max,
            "as_y_bottom_max": as_y_bot_max,
            "as_x_top_max": as_x_top_max,
            "as_y_top_max": as_y_top_max,
            "consumption": {
                "concrete_m3": vol_concrete,
                "steel_kg": steel_weight_kg,
                "steel_tax_kg_m3": steel_weight_kg / vol_concrete if vol_concrete > 0 else 0,
                "steel_tax_kg_m2": steel_weight_kg / area if area > 0 else 0
            }
        }
