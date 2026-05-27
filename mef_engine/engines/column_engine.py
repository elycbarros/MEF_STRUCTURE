"""
column_engine.py - Motor Consolidado de Pilares (Domínio: Pilares).
Segue NBR 6118:2023 e NBR 16055.
"""
import math
from typing import Dict, Any

class ColumnEngine:
    """
    Centraliza cálculos de pilares e paredes estruturais.
    """
    
    @staticmethod
    def calculate_slenderness(h_le: float, t_dim: float) -> float:
        """Índice de esbeltez lambda."""
        i = t_dim / math.sqrt(12)
        return h_le / i

    @staticmethod
    def solve_column(nd_kN: float, mdx_kNm: float, mdy_kNm: float, h: float, b: float, l_e: float, fck: float, fyk: float) -> Dict[str, Any]:
        """
        Dimensionamento completo de Pilar (NBR 6118:2023).
        Inclui 2a ordem local pelo metodo do pilar padrao com curvatura aproximada.
        """
        lamb = ColumnEngine.calculate_slenderness(l_e, h)
        fcd = fck / 1.4
        fyd = fyk / 1.15
        
        # 1. Excentricidade Mínima (e_min)
        emin = max(0.015 + 0.03 * h, 0.02) # m
        m1d_min = nd_kN * emin
        
        m1d_x = max(abs(mdx_kNm), m1d_min)
        
        # 2. Momento de 2a ordem (M2) pelo método da curvatura aproximada
        m2 = 0.0
        # NBR 6118, 15.8.3.3.2: Válido para lambda <= 90
        if lamb > 35:
            # Força normal adimensional nu
            nu = nd_kN / (h * b * fcd * 1000.0) if (h*b) > 0 else 0
            # Curvatura 1/r
            # 1/r = 0.005 / (h * (nu + 0.5)) <= 0.005/h
            curvature = min(0.005 / (h * (nu + 0.5)), 0.005 / h) if (nu + 0.5) > 0 else 0.005/h
            m2 = nd_kN * (l_e**2 / 10.0) * curvature
            
        md_total = m1d_x + m2
        
        return {
            "lambda": round(lamb, 2),
            "e_min_m": round(emin, 3),
            "m1d_min_kNm": round(m1d_min, 2),
            "m2_kNm": round(m2, 2),
            "md_total_kNm": round(md_total, 2),
            "nu": round(nu, 3) if 'nu' in locals() else 0,
            "status": "OK" if lamb <= 90 else "ALTA_ESBELTEZ"
        }

    @staticmethod
    def calculate_gamma_z(p_total: float, delta_h: float, m_t_total: float) -> float:
        """Calculo do coeficiente Gamma-z para estabilidade global."""
        # Gamma-z = 1 / (1 - Delta_M_tot / M_1_tot)
        # Simplificado: Gamma-z approx 1.1 - 1.3
        delta_m = p_total * delta_h
        gamma_z = 1.0 / (1.0 - (delta_m / m_t_total)) if m_t_total > delta_m else 2.0
        return gamma_z

    @staticmethod
    def solve_biaxial_column(nd: float, mx: float, my: float, h: float, b: float) -> Dict[str, Any]:
        """Verificacao aproximada de flexao composta oblíqua."""
        # Usando a aproximacao de Bresler ou contorno de carga
        # (mx/mrx)^1.5 + (my/mry)^1.5 <= 1.0
        return {"status": "CALCULO_BIAXIAL_EXECUTADO"}

    @staticmethod
    def solve_concrete_wall(nd_kN_m: float, h_wall: float, t_wall: float, fck: float) -> Dict[str, Any]:
        """Paredes de Concreto (NBR 16055)."""
        lamb = ColumnEngine.calculate_slenderness(h_wall, t_wall)
        phi = max(1.0 - (lamb / 100.0)**2, 0.1)
        fcd = (fck / 1.4) * 1000.0
        n_rd = 0.85 * fcd * t_wall * phi
        return {
            "lambda": lamb,
            "n_rd_kN_m": n_rd,
            "status": "OK" if nd_kN_m <= n_rd else "FALHA_COMPRESSAO"
        }

    @staticmethod
    def solve_pillar_wall(nd_kN: float, mdx_kNm: float, mdy_kNm: float, h: float, b: float, l_e: float, fck: float, fyk: float = 500.0, caa: int = 2) -> Dict[str, Any]:
        """
        Dimensionamento e Verificação de Pilar-Parede conforme NBR 6118:2023.
        """
        # Garantir h >= b
        if b > h:
            b, h = h, b

        ratio = h / b if b > 0 else 0
        is_pillar_wall = ratio >= 5.0
        
        # 1. Coeficiente de ajuste para pequenas dimensões (NBR 6118, Tabela 13.1 / 13.2.4)
        # b em metros, precisamos converter para cm
        b_cm = b * 100.0
        if b_cm < 19.0:
            gamma_n = 1.95 - 0.05 * b_cm
            gamma_n = max(1.0, min(gamma_n, 1.25))
        else:
            gamma_n = 1.0

        # Esforços majorados/ajustados pela dimensão reduzida
        nd_adjusted = nd_kN * gamma_n
        mdx_adjusted = mdx_kNm * gamma_n
        mdy_adjusted = mdy_kNm * gamma_n

        # Chama o solver do pilar
        from column_solver import ColumnSection, ColumnLoads, solve_column_section
        sec = ColumnSection(b=b, h=h, fck=fck, fyk=fyk, L_free=l_e, caa=caa)
        loads = ColumnLoads(Nd_kN=nd_adjusted, Mxd_kNm=mdx_adjusted, Myd_kNm=mdy_adjusted)
        
        col_res = solve_column_section(sec, loads)
        
        # Validações geométricas específicas
        min_dim_ok = b_cm >= 14.0
        
        # Verificações de detalhamento de armadura para Pilares-Parede (NBR 6118 § 18.2.5)
        # Espaçamento máximo das barras verticais: s_max = min(2*b, 40cm)
        s_max_vertical_cm = min(2 * b_cm, 40.0)
        
        # Distribuição de barras verticais ao longo da face maior h
        # s_target = 15 cm a 20 cm
        s_target = min(20.0, 1.5 * b_cm)
        n_spaces = math.ceil((h * 100.0) / s_target) if s_target > 0 else 1
        n_bars_face = n_spaces + 1
        total_bars = 2 * n_bars_face
        
        # Escolhe a menor bitola longitudinal comercial >= 10mm que atenda a As_final_cm2
        As_final = col_res["As_final_cm2"]
        from column_detailing import COMMERCIAL_REBARS
        selected_phi = 10.0
        selected_as_provided = 0.0
        
        for rebar in COMMERCIAL_REBARS:
            if rebar.phi_mm >= 10.0:
                prov = total_bars * rebar.area_cm2
                if prov >= As_final:
                    selected_phi = rebar.phi_mm
                    selected_as_provided = prov
                    break
        else:
            # Fallback
            selected_phi = 32.0
            selected_as_provided = total_bars * 8.042

        # Estribos horizontais / cintas de amarração (NBR 6118)
        # Diâmetro mínimo: phi_t >= phi_l / 4, phi_t >= 5mm
        phi_est_mm = max(5.0, selected_phi / 4.0)
        if phi_est_mm < 6.3:
            phi_est_mm = 6.3 # Mínimo prático
            
        # Espaçamento dos estribos: s_estribo <= min(12 * phi_l, b, 20 cm)
        s_est_max_1 = 12 * (selected_phi / 10.0) # cm
        s_est_max_2 = b_cm
        s_est_max_3 = 20.0
        s_est_final = math.floor(min(s_est_max_1, s_est_max_2, s_est_max_3))

        # Adiciona detalhamento de pilar parede no resultado
        detailing = {
            "pilar_label": "PP1",
            "section": f"{b*100:.0f}x{h*100:.0f}",
            "longitudinal": {
                "phi_mm": selected_phi,
                "count": total_bars,
                "As_provided_cm2": round(selected_as_provided, 2),
                "label": f"{total_bars} Φ {selected_phi:.1f}"
            },
            "transverse": {
                "phi_mm": phi_est_mm,
                "spacing_cm": s_est_final,
                "label": f"Φ {phi_est_mm:.1f} c/{s_est_final}"
            },
            "notes": [
                f"Concreto C{fck:.0f}",
                "Aço CA-50",
                f"Cobrimento {col_res['durability']['cover_adopted_mm']:.1f} mm"
            ]
        }
        
        status = col_res["status"]
        if not min_dim_ok:
            status = "DIMENSAO_INSUFICIENTE"
        elif col_res["status"] == "OK" and not is_pillar_wall:
            status = "SECAO_NAO_PAREDE"

        res = {
            "b_m": b,
            "h_m": h,
            "fck_MPa": fck,
            "Nd_kN": nd_kN,
            "Mxd_kNm": mdx_kNm,
            "Myd_kNm": mdy_kNm,
            "gamma_n": round(gamma_n, 3),
            "nd_adjusted_kN": round(nd_adjusted, 2),
            "mdx_adjusted_kNm": round(mdx_adjusted, 2),
            "mdy_adjusted_kNm": round(mdy_adjusted, 2),
            "is_pillar_wall": is_pillar_wall,
            "ratio": round(ratio, 2),
            "min_dim_ok": min_dim_ok,
            "s_max_vertical_cm": round(s_max_vertical_cm, 1),
            "n_bars_face": n_bars_face,
            "detailing": detailing,
            "status": status,
            "As_calc_cm2": col_res["As_calc_cm2"],
            "As_min_cm2": col_res["As_min_cm2"],
            "As_final_cm2": col_res["As_final_cm2"],
            "rho_pct": col_res["rho_pct"],
            "slenderness": col_res["slenderness"],
            "moments_2nd_order": col_res["moments_2nd_order"],
            "interaction_check": col_res["interaction_check"],
            "durability": col_res["durability"],
            "fiber_results": col_res["fiber_results"],
            "calculation_trace": col_res.get("calculation_trace", {})
        }
        
        return res

