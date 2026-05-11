"""
footing_solver.py - Dimensionamento de Sapatas Isoladas (NBR 6118 / NBR 6122).
"""
import math
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class FootingConfig:
    Nd_kN: float        # Carga vertical característica de projeto (Sd = Nd * 1.4)
    sigma_adm_kPa: float # Tensão admissível do solo
    ap_m: float         # Lado maior do pilar
    bp_m: float         # Lado menor do pilar
    fck: float          # Resistência do concreto (MPa)
    caa: int = 2        # Classe de agressividade ambiental
    cover_mm: float = 40.0

class FootingSolver:
    def __init__(self, cfg: FootingConfig):
        self.cfg = cfg
        # Consideramos peso próprio estimado (10% de Nd)
        self.Nd_total = cfg.Nd_kN * 1.10
        self.fcd = cfg.fck / 1.40
        self.fyd = 500.0 / 1.15 # CA-50

    def solve(self) -> Dict[str, Any]:
        # 1. Dimensionamento em Planta
        area_req = self.Nd_total / self.cfg.sigma_adm_kPa
        
        # Proporção: A - B = ap - bp (para manter balanços iguais)
        diff = self.cfg.ap_m - self.cfg.bp_m
        
        # Area = (B + diff) * B = B^2 + diff*B - area_req = 0
        # B = (-diff + sqrt(diff^2 + 4*area_req)) / 2
        b_m = (-diff + math.sqrt(diff**2 + 4 * area_req)) / 2.0
        a_m = b_m + diff
        
        # Arredondamento para múltiplos de 5cm
        a_m = math.ceil(a_m * 20) / 20.0
        b_m = math.ceil(b_m * 20) / 20.0
        
        # 2. Altura (Rigidez)
        # Critério de Rigidez: h >= (A - ap) / 3
        h_min_a = (a_m - self.cfg.ap_m) / 3.0
        h_min_b = (b_m - self.cfg.bp_m) / 3.0
        h_m = max(0.40, h_min_a, h_min_b)
        h_m = math.ceil(h_m * 10) / 10.0 # Arredonda para 10cm
        
        # d (altura útil estimada)
        d_m = h_m - (self.cfg.cover_mm / 1000.0) - 0.01 # 1cm de barra
        
        # 3. Verificação de Tensões
        sigma_real = self.Nd_total / (a_m * b_m)
        
        # 4. Cálculo de Armaduras (Método das Bielas simplificado)
        # Força no tirante (aprox)
        # Fs = Nd * (A - ap) / (8 * d)
        fs_a = (self.cfg.Nd_kN * 1.4 * (a_m - self.cfg.ap_m)) / (8.0 * d_m)
        fs_b = (self.cfg.Nd_kN * 1.4 * (b_m - self.cfg.bp_m)) / (8.0 * d_m)
        
        as_a = (fs_a * 10.0) / (self.fyd / 1.15) # cm2
        as_b = (fs_b * 10.0) / (self.fyd / 1.15) # cm2
        
        # Taxa mínima (0.15% da seção de concreto)
        as_min_a = 0.0015 * b_m * h_m * 10000.0
        as_min_b = 0.0015 * a_m * h_m * 10000.0
        
        return {
            "A_m": a_m,
            "B_m": b_m,
            "h_m": h_m,
            "d_m": d_m,
            "area_m2": a_m * b_m,
            "Nd_kN": self.cfg.Nd_kN,
            "sigma_max_kPa": sigma_real,
            "sigma_adm_kPa": self.cfg.sigma_adm_kPa,
            "a_col_m": self.cfg.ap_m,
            "b_col_m": self.cfg.bp_m,
            "fck": self.cfg.fck,
            "as_a_cm2": max(as_a, as_min_a),
            "as_b_cm2": max(as_b, as_min_b),
            "is_rigid": h_m >= max(h_min_a, h_min_b),
            "status": "OK" if sigma_real <= self.cfg.sigma_adm_kPa else "SOBRECARGA"
        }

def solve_isolated_footing(params: Dict[str, Any]) -> Dict[str, Any]:
    cfg = FootingConfig(
        Nd_kN=params.get('Nd', 500.0),
        sigma_adm_kPa=params.get('sigma_adm', 300.0),
        ap_m=params.get('ap', 0.20),
        bp_m=params.get('bp', 0.20),
        fck=params.get('fck', 25.0)
    )
    solver = FootingSolver(cfg)
    return solver.solve()
