"""
slab_engine.py - Motor Consolidado de Lajes (Domínio: Lajes).
Segue rigorosamente a NBR 6118:2023.
"""
import math
from typing import Dict, Any

class SlabEngine:
    """
    Centraliza todos os cálculos de lajes e punção.
    """
    
    @staticmethod
    def validate_geometry(slab_type: str, h: float, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida requisitos geométricos mínimos (NBR 6118).
        h: Altura total em metros.
        """
        reasons = []
        
        # 1. Requisitos de Espessura Mínima (NBR 6118 §13.2.4)
        if slab_type == "solid":
            if h < 0.07: reasons.append("Espessura mínima para lajes de cobertura é 7cm.")
            if h < 0.08: reasons.append("Espessura mínima para lajes de piso é 8cm.")
        elif slab_type == "ribbed":
            h_mesa = params.get("h_mesa", 0.05)
            if h_mesa < 0.04: reasons.append("Espessura da mesa (hf) deve ser >= 4cm.")
            dist_nerv = params.get("dist_nerv", 0.50)
            if h_mesa < dist_nerv / 15.0: reasons.append(f"Espessura da mesa ({h_mesa*100}cm) < 1/15 da distância entre nervuras ({round(dist_nerv*100/15.0, 1)}cm).")
        elif slab_type == "prestressed":
            if h < 0.15: reasons.append("Lajes protendidas (planas) recomendam-se h >= 15cm para garantir ancoragem e punção.")
        elif slab_type == "hollow_core":
            if h < 0.10: reasons.append("Lajes alveolares comerciais tipicamente iniciam em 10-12cm.")
            
        return {
            "valid": len(reasons) == 0,
            "reasons": reasons
        }

    @staticmethod
    def calculate_shear_resistance(ved_kN_m: float, d_eff: float, bw: float, fck: float, rho_l: float = 0.005) -> Dict[str, Any]:
        """
        Cisalhamento em Lajes (NBR 6118, 19.4.1) - Sem armadura transversal.
        ved_kN_m: Esforço cortante de cálculo (kN/m)
        bw: Largura da alma (m)
        """
        # fctd = fct,inf / 1.4 = 0.7 * fctm / 1.4 = 0.5 * fctm
        fctm = 0.3 * (fck**(2/3))
        fctd = (0.7 * fctm) / 1.4
        
        k = min(1.0 + math.sqrt(0.2 / d_eff), 2.0)
        
        # VRd1 = [tau_rd * k * (1.2 + 40*rho1) + 0.15*sigma_cp] * bw * d
        tau_rd = 0.25 * fctd * 1000.0 # kPa
        v_rd1 = tau_rd * k * (1.2 + 40.0 * rho_l) * bw * d_eff # kN
        
        return {
            "ved_kN_m": round(ved_kN_m, 2),
            "v_rd1_kN_m": round(v_rd1, 2),
            "ratio": round(ved_kN_m / v_rd1, 3) if v_rd1 > 0 else 999,
            "status": "OK" if ved_kN_m <= v_rd1 else "FALHA_CISALHAMENTO"
        }

    @staticmethod
    def calculate_punching(fsd_kN: float, d_eff: float, u_perim: float, fck: float, rho_l: float, u0_perim: float = 0.0) -> Dict[str, Any]:
        """
        Verificação de Punção (NBR 6118, 19.5).
        u0: Perímetro de controle junto ao pilar (esmagamento).
        u_perim: Perímetro de controle a 2d do pilar.
        """
        fcd = fck / 1.4
        # 1. Verificação da biela de compressão (u0)
        tau_rd2 = 0.27 * (1.0 - fck/250.0) * fcd * 1000.0 # kPa
        tau_sd0 = fsd_kN / (u0_perim * d_eff) if u0_perim > 0 else 0
        
        # 2. Verificação sem armadura de punção (u1)
        k = min(1.0 + math.sqrt(0.2 / d_eff), 2.0)
        tau_rd1 = 0.13 * k * (100 * rho_l * fck)**(1/3) * 1000.0 # kPa
        tau_sd1 = fsd_kN / (u_perim * d_eff)
        
        ratio_max = max(tau_sd0 / tau_rd2 if tau_rd2 > 0 else 0, tau_sd1 / tau_rd1 if tau_rd1 > 0 else 0)
        
        return {
            "tau_sd0_kPa": round(tau_sd0, 2),
            "tau_rd2_kPa": round(tau_rd2, 2),
            "tau_sd1_kPa": round(tau_sd1, 2),
            "tau_rd1_kPa": round(tau_rd1, 2),
            "ratio_max": round(ratio_max, 3),
            "status_biela": "OK" if tau_sd0 <= tau_rd2 else "ESMAGAMENTO",
            "status_puncao": "OK" if tau_sd1 <= tau_rd1 else "REFORCO_NECESSARIO"
        }

    @staticmethod
    def solve_ribbed(h_total: float, h_mesa: float, b_nerv: float, dist_nerv: float, md_kNm_m: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Lajes Nervuradas."""
        m_nerv = md_kNm_m * dist_nerv
        
        # Volume Equivalente (para Peso Próprio)
        area_secao = (dist_nerv * h_mesa) + b_nerv * (h_total - h_mesa)
        h_eq_vol = area_secao / dist_nerv
        
        # Inércia Equivalente (para rigidez MEF)
        y_cg = ((dist_nerv * h_mesa * (h_total - h_mesa/2)) + (b_nerv * (h_total - h_mesa) * ((h_total - h_mesa)/2))) / area_secao
        i_mesa = (dist_nerv * h_mesa**3)/12.0 + (dist_nerv * h_mesa) * (h_total - h_mesa/2 - y_cg)**2
        i_nerv = (b_nerv * (h_total - h_mesa)**3)/12.0 + (b_nerv * (h_total - h_mesa)) * (y_cg - (h_total - h_mesa)/2)**2
        i_total = i_mesa + i_nerv
        
        i_por_metro = i_total / dist_nerv
        h_eq_i = (12.0 * i_por_metro / 1.0)**(1/3)
        
        return {
            "m_nerv_kNm": m_nerv,
            "h_eq_vol_m": h_eq_vol,
            "h_eq_i_m": h_eq_i,
            "as_total_cm2_m": (m_nerv * 100 * 1.15) / (fyk/10.0 * (h_total-0.03)*0.9 * 100) / dist_nerv
        }

    @staticmethod
    def solve_hollow_core(h_total: float, area_voids: float, p_force: float, l_span: float, q_acid: float, fck: float) -> Dict[str, Any]:
        """
        Lajes Alveolares (Hollow Core).
        """
        area_gross = 1.0 * h_total
        area_net = area_gross - area_voids
        
        h_eq_vol = area_net / 1.0
        
        # Inercia equivalente (simplificada)
        i_net = (1.0 * h_total**3 / 12.0) - (area_voids * (h_total/2.0)**2 * 0.5)
        h_eq_i = (12.0 * i_net / 1.0)**(1/3)
        
        # Verificacao de Cisalhamento nos dentes de apoio
        v_rd1 = 0.25 * 0.3 * (fck**0.5) * area_net * 1000.0 # kN/m
        
        return {
            "type": "hollow_core",
            "area_net_m2": area_net,
            "h_eq_vol_m": h_eq_vol,
            "h_eq_i_m": h_eq_i,
            "v_rd1_kN_m": v_rd1,
            "status": "OK"
        }

    @staticmethod
    def solve_prestressed(l_span: float, h_slab: float, p_force: float, ecc: float, q_total: float, fck: float) -> Dict[str, Any]:
        """Lajes Protendidas - Carga Equivalente."""
        q_eq = (8 * p_force * ecc) / (l_span**2)
        area = 1.0 * h_slab
        w_mod = (1.0 * h_slab**2) / 6.0
        m_serv = (q_total * l_span**2) / 8.0
        sigma_inf = (-p_force / area) + (m_serv / w_mod)
        return {
            "q_eq_kPa": q_eq,
            "sigma_inf_kPa": sigma_inf,
            "fctm_kPa": 0.3 * fck**(2/3) * 1000.0,
            "p_force_kN": p_force,
            "ecc_m": ecc
        }
    @staticmethod
    def solve_trussed(h_total: float, h_mesa: float, b_nerv: float, dist_nerv: float, filler_type: str, md_kNm_m: float, fck: float, fyk: float) -> Dict[str, Any]:
        """Lajes Treliçadas (NBR 14859)."""
        # Semelhante a nervurada, mas com peso do enchimento
        m_nerv = md_kNm_m * dist_nerv
        
        # Volume de concreto
        area_concreto = (dist_nerv * h_mesa) + b_nerv * (h_total - h_mesa)
        h_eq_vol_concreto = area_concreto / dist_nerv
        
        # Peso do enchimento
        gamma_filler = 8.0 if filler_type == "ceramic" else 0.2
        area_filler = (dist_nerv - b_nerv) * (h_total - h_mesa)
        q_filler = (area_filler / dist_nerv) * gamma_filler # kN/m2
        
        # Inércia
        y_cg = ((dist_nerv * h_mesa * (h_total - h_mesa/2)) + (b_nerv * (h_total - h_mesa) * ((h_total - h_mesa)/2))) / area_concreto
        i_concreto = (dist_nerv * h_mesa**3)/12.0 + (dist_nerv * h_mesa) * (h_total - h_mesa/2 - y_cg)**2 + \
                      (b_nerv * (h_total - h_mesa)**3)/12.0 + (b_nerv * (h_total - h_mesa)) * (y_cg - (h_total - h_mesa)/2)**2
        
        h_eq_i = (12.0 * (i_concreto / dist_nerv))**(1/3)

        return {
            "type": "trussed",
            "h_eq_vol_m": h_eq_vol_concreto,
            "q_filler_kNm2": q_filler,
            "h_eq_i_m": h_eq_i,
            "m_nerv_kNm": m_nerv,
            "as_total_cm2_m": (m_nerv * 100 * 1.15) / (fyk/10.0 * (h_total-0.03)*0.9 * 100) / dist_nerv
        }
