"""
reservoir_pool_solver.py — Dimensionamento de Reservatórios e Piscinas de Concreto Armado.

Análise de paredes sob empuxo hidrostático/solo, laje de fundo, controle de
fissuração rigoroso (wk ≤ 0.1mm face molhada), e verificação de estanqueidade.

Referências:
- ABNT NBR 6118:2023 — Projeto de estruturas de concreto.
- ABNT NBR 6120:2019 — Cargas para cálculo de estruturas.
- PCA — Rectangular Concrete Tanks (Portland Cement Association).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import math


# ──────────────────────── Data Models ────────────────────────

@dataclass
class ReservoirConfig:
    """Configuração do reservatório ou piscina."""
    name: str = 'RES_01'
    type: str = 'elevated'            # 'elevated', 'ground', 'buried', 'pool'
    # Geometria interna
    Lx: float = 5.0                   # comprimento interno (m)
    Ly: float = 4.0                   # largura interna (m)
    H: float = 3.0                    # altura da água (m)
    freeboard: float = 0.20           # folga acima da água (m)
    # Piscina / Barrilete
    wall_thickness: float = 0.20      # espessura das paredes (m)
    slab_thickness: float = 0.20      # espessura da laje de fundo (m)
    top_slab_thickness: float = 0.12   # espessura da laje de tampa (m)
    n_chambers: int = 1               # número de células
    infinity_edge: bool = False       # possui borda infinita (calha de transbordo)
    column_spacing_x: float = 5.0     # espaçamento entre pilares de suporte X
    column_spacing_y: float = 5.0     # espaçamento entre pilares de suporte Y
    # Materiais
    fck: float = 30.0                 # MPa
    fyk: float = 500.0                # MPa
    cover_internal: float = 0.040     # cobrimento face molhada (m)
    cover_external: float = 0.030     # cobrimento face seca (m)
    # Cargas adicionais
    soil_gamma: float = 18.0          # peso específico do solo (kN/m³) — para buried
    soil_ka: float = 0.33             # coeficiente de empuxo ativo
    soil_depth: float = 0.0           # profundidade de aterro externo (m)
    surcharge_kPa: float = 0.0        # sobrecarga no terreno adjacente (kPa)
    live_load_top_kPa: float = 2.0     # sobrecarga na tampa (manutenção/bombas)
    # Líquido
    liquid_gamma: float = 10.0        # peso específico do líquido (kN/m³)
    # Limites normativos
    wk_limit_wet: float = 0.10        # abertura de fissura face molhada (mm)
    wk_limit_dry: float = 0.20        # abertura de fissura face seca (mm)
    gamma_c: float = 1.4
    gamma_s: float = 1.15
    gamma_f: float = 1.4


# ──────────────────────── Wall Analysis ────────────────────────

def _analyze_wall(H: float, t: float, fck: float, fyk: float, cover: float,
                  p_max_int: float, p_max_ext: float,
                  support_top: str, support_bottom: str,
                  gamma_c: float, gamma_s: float, gamma_f: float,
                  wk_limit: float, wall_id: str) -> dict:
    """
    Análise de parede sob pressão triangular (empuxo hidrostático ou solo).
    
    support_top: 'free' ou 'hinged'
    support_bottom: 'fixed' ou 'hinged'
    """
    # Pressão líquida (interna - externa ou vice-versa, a mais desfavorável)
    p_net = max(abs(p_max_int), abs(p_max_ext))

    # Momento fletor conforme condição de apoio (por metro de largura)
    # Carga triangular: p(z) = p_max × z/H
    if support_bottom == 'fixed' and support_top == 'free':
        # Engastado-livre: M_base = p_max × H² / 6
        M_base = p_net * H**2 / 6.0
        M_vao = p_net * H**2 / 15.0
        V_base = p_net * H / 2.0
    elif support_bottom == 'hinged' and support_top == 'free':
        # Apoiado-livre: M_max ≈ p_max × H² / 9.4 (a ~0.58H)
        M_base = 0.0
        M_vao = p_net * H**2 / 9.4
        V_base = p_net * H / 6.0
    elif support_bottom == 'fixed' and support_top == 'hinged':
        # Engastado-apoiado: M_base = p_max × H² / 15
        M_base = p_net * H**2 / 15.0
        M_vao = p_net * H**2 / 23.3
        V_base = p_net * H * 0.4
    else:
        # Bi-apoiado
        M_base = 0.0
        M_vao = p_net * H**2 / 12.5
        V_base = p_net * H / 3.0

    M_design = max(M_base, M_vao) * gamma_f  # kNm/m (majorado)
    V_design = V_base * gamma_f               # kN/m (majorado)

    # Dimensionamento à flexão
    d = t - cover - 0.008  # altura útil (m) — φ16
    fcd = fck / gamma_c * 1e3  # kPa
    fyd = fyk / gamma_s * 1e3  # kPa

    M_Nm = M_design * 1000.0  # N·m/m
    k = M_Nm / (1.0 * d**2 * fcd * 1000.0) if d > 0 else 0
    disc = 1.0 - 2.94 * k
    if disc < 0:
        x_d = 1.0
        As_cm2 = 99.9
        domain = '4'
    else:
        x_d = (1.0 - math.sqrt(disc)) / 0.8
        z = d * (1.0 - 0.4 * x_d)
        As_m2 = M_Nm / (fyd * 1000.0 * z) if z > 0 else 0
        As_cm2 = max(As_m2 * 1e4, 0.15 * 1.0 * d * 100)  # mínimo 0.15%
        domain = '2' if x_d <= 0.259 else ('3' if x_d <= 0.45 else '4')

    # Controle de Fissuração (simplificado — NBR 6118 §17.3.3)
    # wk = (φ / 12.5 × η1) × (σs / Es) × (3 × σs / fctm)
    # Simplificação: verificar se As atende wk_limit
    fctm = 0.3 * fck**(2/3)  # MPa
    phi_bar = 12.5  # mm — bitola de referência
    Es = 210_000.0  # MPa
    sigma_s = M_Nm / (As_cm2 * 1e-4 * d) / 1e6 if As_cm2 > 0 else 999  # MPa
    wk_calc = (phi_bar / (12.5 * 2.25)) * (sigma_s / Es) * (3 * sigma_s / fctm)
    wk_ok = wk_calc <= wk_limit

    # Se fissuração não atende, aumentar As até atender
    As_fissura = As_cm2
    if not wk_ok and wk_calc < 10:
        # Iteração para encontrar As que atenda wk
        for factor in np.arange(1.1, 3.0, 0.1):
            As_test = As_cm2 * factor
            sig_test = M_Nm / (As_test * 1e-4 * d) / 1e6 if As_test > 0 else 999
            wk_test = (phi_bar / (12.5 * 2.25)) * (sig_test / Es) * (3 * sig_test / fctm)
            if wk_test <= wk_limit:
                As_fissura = round(As_test, 2)
                wk_calc = wk_test
                wk_ok = True
                break

    As_final = max(As_cm2, As_fissura)

    return {
        'wall_id': wall_id,
        'H_m': H,
        't_m': t,
        'p_max_int_kPa': round(p_max_int, 2),
        'p_max_ext_kPa': round(p_max_ext, 2),
        'M_base_kNm_m': round(M_base, 2),
        'M_vao_kNm_m': round(M_vao, 2),
        'M_design_kNm_m': round(M_design, 2),
        'V_design_kN_m': round(V_design, 2),
        'As_flexure_cm2_m': round(As_cm2, 2),
        'As_fissura_cm2_m': round(As_fissura, 2),
        'As_final_cm2_m': round(As_final, 2),
        'x_over_d': round(x_d, 4),
        'domain': domain,
        'wk_calc_mm': round(wk_calc, 3),
        'wk_limit_mm': wk_limit,
        'wk_status': 'OK' if wk_ok else 'EXCEDE',
        'governed_by': 'FISSURACAO' if As_fissura > As_cm2 else 'FLEXAO',
    }


# ──────────────────────── Slab Analysis ────────────────────────

def _analyze_floor_slab(Lx: float, Ly: float, t: float, H_water: float,
                        liquid_gamma: float, fck: float, fyk: float,
                        cover: float, gamma_c: float, gamma_s: float,
                        gamma_f: float, wk_limit: float) -> dict:
    """Análise da laje de fundo sob peso da água + peso próprio."""
    # Pressão na laje
    q_water = liquid_gamma * H_water     # kN/m²
    q_pp = t * 25.0                       # kN/m² (concreto)
    q_total = q_water + q_pp
    q_design = q_total * gamma_f

    # Relação de lados
    ratio = Ly / Lx if Lx <= Ly else Lx / Ly
    L_menor = min(Lx, Ly)

    # Momentos — tabela de Bares (laje engastada nos 4 lados)
    if ratio <= 1.2:
        coef_vao = 0.024
        coef_eng = 0.046
    elif ratio <= 1.5:
        coef_vao = 0.034
        coef_eng = 0.058
    elif ratio <= 2.0:
        coef_vao = 0.042
        coef_eng = 0.065
    else:
        # Armada em uma direção
        coef_vao = 0.042
        coef_eng = 0.083

    M_vao = coef_vao * q_design * L_menor**2
    M_eng = coef_eng * q_design * L_menor**2

    # Dimensionamento
    d = t - cover - 0.008
    fcd = fck / gamma_c * 1e3
    fyd = fyk / gamma_s * 1e3
    M_max = max(M_vao, M_eng)
    M_Nm = M_max * 1000.0

    k = M_Nm / (1.0 * d**2 * fcd * 1000.0) if d > 0 else 0
    disc = max(1.0 - 2.94 * k, 0)
    x_d = (1.0 - math.sqrt(disc)) / 0.8 if disc > 0 else 1.0
    z = d * (1.0 - 0.4 * x_d)
    As_m2 = M_Nm / (fyd * 1000.0 * z) if z > 0 else 0
    As_cm2 = max(As_m2 * 1e4, 0.15 * 1.0 * d * 100)

    # Flecha
    E = 5600 * fck**0.5 * 1e3  # kPa
    I = 1.0 * t**3 / 12.0
    EI = E * I
    flecha = (5 * q_total * L_menor**4) / (384 * EI)
    flecha_lim = L_menor / 250.0

    return {
        'Lx_m': Lx,
        'Ly_m': Ly,
        't_m': t,
        'q_water_kPa': round(q_water, 2),
        'q_pp_kPa': round(q_pp, 2),
        'q_design_kPa': round(q_design, 2),
        'M_vao_kNm_m': round(M_vao, 2),
        'M_eng_kNm_m': round(M_eng, 2),
        'As_cm2_m': round(As_cm2, 2),
        'ratio_Ly_Lx': round(ratio, 2),
        'flecha_mm': round(flecha * 1000, 2),
        'flecha_lim_mm': round(flecha_lim * 1000, 2),
        'flecha_status': 'OK' if flecha <= flecha_lim else 'EXCEDE',
    }


# ──────────────────────── Volume & Dimensionamento Hidráulico ────────────────────────

def _hydraulic_summary(cfg: ReservoirConfig) -> dict:
    """Resumo hidráulico: volume, peso, pressões."""
    vol = cfg.Lx * cfg.Ly * cfg.H
    peso_agua = vol * cfg.liquid_gamma
    area_fundo = cfg.Lx * cfg.Ly
    p_fundo = cfg.liquid_gamma * cfg.H

    # Volume de concreto
    H_total = cfg.H + cfg.freeboard
    vol_perimetro = 2 * (cfg.Lx + cfg.Ly) * H_total * cfg.wall_thickness
    # Paredes internas (divisórias) - assume divisão paralela ao lado menor Ly
    vol_divisorias = (cfg.n_chambers - 1) * cfg.Ly * H_total * cfg.wall_thickness
    vol_fundo = area_fundo * cfg.slab_thickness
    vol_tampa = area_fundo * cfg.top_slab_thickness
    vol_concreto = vol_perimetro + vol_divisorias + vol_fundo + vol_tampa

    # Pesos
    peso_concreto = vol_concreto * 25.0
    peso_sobrecarga_tampa = area_fundo * cfg.live_load_top_kPa
    
    # Adicional para Borda Infinita (calha externa de ~40x40cm)
    peso_borda_infinita = 0.0
    if cfg.infinity_edge:
        # Perímetro da borda (assume lado maior Lx)
        vol_calha = cfg.Lx * 0.4 * 0.4
        peso_borda_infinita = (vol_calha * 25.0) + (vol_calha * 10.0) # concreto + água na calha

    peso_total_operacional = peso_agua + peso_concreto + peso_sobrecarga_tampa + peso_borda_infinita

    # Carga pontual nos pilares de suporte (estimativa por área de influência)
    carga_por_pilar = (peso_total_operacional / area_fundo) * (cfg.column_spacing_x * cfg.column_spacing_y)

    return {
        'volume_liquido_m3': round(vol, 2),
        'volume_litros': round(vol * 1000, 0),
        'peso_liquido_kN': round(peso_agua, 2),
        'pressao_fundo_kPa': round(p_fundo, 2),
        'area_fundo_m2': round(area_fundo, 2),
        'volume_concreto_m3': round(vol_concreto, 2),
        'peso_concreto_kN': round(peso_concreto, 2),
        'peso_total_operacional_kN': round(peso_total_operacional, 2),
        'carga_estimada_por_pilar_kN': round(carga_por_pilar, 1),
        'H_total_m': round(H_total, 2),
        'n_chambers': cfg.n_chambers,
        'has_infinity_edge': cfg.infinity_edge,
    }


# ──────────────────────── Load Cases ────────────────────────

def _get_load_cases(cfg: ReservoirConfig) -> list:
    """Define os casos de carga conforme tipo de reservatório."""
    cases = []
    H = cfg.H + cfg.freeboard
    p_water = cfg.liquid_gamma * cfg.H

    # Caso 1: Cheio (sempre)
    cases.append({
        'name': 'CHEIO',
        'description': 'Reservatório cheio, sem empuxo externo',
        'p_int': p_water,
        'p_ext': 0.0,
        'critical_for': 'paredes internas',
    })

    # Caso 2: Vazio + Empuxo (para enterrado)
    if cfg.type == 'buried' and cfg.soil_depth > 0:
        p_soil = cfg.soil_gamma * cfg.soil_ka * cfg.soil_depth + cfg.surcharge_kPa * cfg.soil_ka
        cases.append({
            'name': 'VAZIO_COM_EMPUXO',
            'description': 'Reservatório vazio com empuxo de solo externo',
            'p_int': 0.0,
            'p_ext': p_soil,
            'critical_for': 'paredes externas',
        })

    # Caso 3: Cheio + Empuxo (para enterrado)
    if cfg.type == 'buried' and cfg.soil_depth > 0:
        p_soil = cfg.soil_gamma * cfg.soil_ka * cfg.soil_depth + cfg.surcharge_kPa * cfg.soil_ka
        cases.append({
            'name': 'CHEIO_COM_EMPUXO',
            'description': 'Cheio internamente com empuxo externo (balanceado)',
            'p_int': p_water,
            'p_ext': p_soil,
            'critical_for': 'verificar lado mais carregado',
        })

    return cases


# ──────────────────────── Pipeline Principal ────────────────────────

def analyze_reservoir(cfg: ReservoirConfig = None) -> dict:
    """
    Análise completa de reservatório ou piscina.

    Exemplo:
        result = analyze_reservoir(ReservoirConfig(
            Lx=8.0, Ly=5.0, H=3.0, type='buried',
            soil_depth=2.5, wall_thickness=0.25,
        ))
    """
    if cfg is None:
        cfg = ReservoirConfig()

    hydraulic = _hydraulic_summary(cfg)
    load_cases = _get_load_cases(cfg)
    H_total = cfg.H + cfg.freeboard

    # Analisar paredes para cada caso de carga (pior caso governa)
    wall_results = []
    for case in load_cases:
        # Paredes longas (Ly)
        w = _analyze_wall(
            H=H_total, t=cfg.wall_thickness,
            fck=cfg.fck, fyk=cfg.fyk, cover=cfg.cover_internal,
            p_max_int=case['p_int'], p_max_ext=case['p_ext'],
            support_top='free', support_bottom='fixed',
            gamma_c=cfg.gamma_c, gamma_s=cfg.gamma_s, gamma_f=cfg.gamma_f,
            wk_limit=cfg.wk_limit_wet,
            wall_id=f'PAREDE_Lx_{case["name"]}',
        )
        wall_results.append(w)

        # Paredes curtas (Lx)
        w2 = _analyze_wall(
            H=H_total, t=cfg.wall_thickness,
            fck=cfg.fck, fyk=cfg.fyk, cover=cfg.cover_internal,
            p_max_int=case['p_int'], p_max_ext=case['p_ext'],
            support_top='free', support_bottom='fixed',
            gamma_c=cfg.gamma_c, gamma_s=cfg.gamma_s, gamma_f=cfg.gamma_f,
            wk_limit=cfg.wk_limit_wet,
            wall_id=f'PAREDE_Ly_{case["name"]}',
        )
        wall_results.append(w2)

    # Envoltória (máximos de todas as paredes)
    As_max_wall = max(w['As_final_cm2_m'] for w in wall_results)
    wk_worst = max(w['wk_calc_mm'] for w in wall_results)

    # Laje de fundo
    slab = _analyze_floor_slab(
        Lx=cfg.Lx, Ly=cfg.Ly, t=cfg.slab_thickness, H_water=cfg.H,
        liquid_gamma=cfg.liquid_gamma, fck=cfg.fck, fyk=cfg.fyk,
        cover=cfg.cover_internal, gamma_c=cfg.gamma_c, gamma_s=cfg.gamma_s,
        gamma_f=cfg.gamma_f, wk_limit=cfg.wk_limit_wet,
    )

    # Subpressão (para enterrado)
    subpressao = {}
    if cfg.type in ('buried', 'ground'):
        p_sub = cfg.liquid_gamma * cfg.soil_depth  # simplificação
        peso_estrutura = hydraulic['volume_concreto_m3'] * 25.0
        peso_agua = hydraulic['peso_liquido_kN']
        fator_flutuacao = (peso_estrutura + peso_agua) / max(p_sub * cfg.Lx * cfg.Ly, 1)
        subpressao = {
            'subpressao_kPa': round(p_sub, 2),
            'peso_estrutura_kN': round(peso_estrutura, 2),
            'fator_flutuacao': round(fator_flutuacao, 2),
            'status': 'OK' if fator_flutuacao >= 1.2 else 'RISCO_FLUTUACAO',
        }

    # Classificação geral
    issues = []
    if any(w['wk_status'] != 'OK' for w in wall_results):
        issues.append('FISSURACAO_PAREDE')
    if any(w['domain'] == '4' for w in wall_results):
        issues.append('DOMINIO_4')
    if slab.get('flecha_status') != 'OK':
        issues.append('FLECHA_LAJE')
    if subpressao.get('status') == 'RISCO_FLUTUACAO':
        issues.append('FLUTUACAO')

    overall = 'ATENDE' if not issues else 'REVISAR: ' + ', '.join(issues)

    return {
        'config': {
            'name': cfg.name, 'type': cfg.type,
            'Lx': cfg.Lx, 'Ly': cfg.Ly, 'H': cfg.H,
            'wall_t': cfg.wall_thickness, 'slab_t': cfg.slab_thickness,
            'fck': cfg.fck,
        },
        'hydraulic': hydraulic,
        'load_cases': load_cases,
        'walls': wall_results,
        'wall_envelope': {
            'As_max_cm2_m': round(As_max_wall, 2),
            'wk_worst_mm': round(wk_worst, 3),
            'governing': max(wall_results, key=lambda w: w['As_final_cm2_m'])['wall_id'],
        },
        'floor_slab': slab,
        'subpressao': subpressao,
        'overall_status': overall,
        'summary': {
            'volume_m3': hydraulic['volume_liquido_m3'],
            'As_parede_cm2_m': round(As_max_wall, 2),
            'As_laje_cm2_m': slab['As_cm2_m'],
            'wk_max_mm': round(wk_worst, 3),
            'concreto_m3': hydraulic['volume_concreto_m3'],
            'status': overall,
        },
    }


if __name__ == '__main__':
    import json

    # Demo 1: Reservatório elevado (5×4×3m)
    r1 = analyze_reservoir(ReservoirConfig(
        name='RES_ELEVADO', type='elevated',
        Lx=5.0, Ly=4.0, H=3.0,
        wall_thickness=0.20, slab_thickness=0.20, fck=30,
    ))
    print('=== RESERVATÓRIO ELEVADO ===')
    print(json.dumps(r1['summary'], indent=2))

    # Demo 2: Piscina enterrada (10×5×1.5m)
    r2 = analyze_reservoir(ReservoirConfig(
        name='PISCINA_01', type='buried',
        Lx=10.0, Ly=5.0, H=1.50, freeboard=0.10,
        wall_thickness=0.20, slab_thickness=0.15, fck=30,
        soil_depth=1.6, soil_gamma=18.0, soil_ka=0.33,
    ))
    print('\n=== PISCINA ENTERRADA ===')
    print(json.dumps(r2['summary'], indent=2))
    print(json.dumps(r2['subpressao'], indent=2))
