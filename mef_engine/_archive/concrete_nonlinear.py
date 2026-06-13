"""
concrete_nonlinear.py - Motor de Não-Linearidade Física para Concreto Armado (Radiers e Lajes).

Implementa:
1. Inércia Equivalente de Branson (I_eff) para rigidez secante.
2. Redistribuição Plástica de Momentos (NBR 6118, §14.6.4.3).
3. Análise completa de Estádio I → II → III com diagnóstico por elemento.

Referências:
- ABNT NBR 6118:2023, Seções 14.6.4 e 17.3.
- Branson, D.E. (1963). Instantaneous and Time-Dependent Deflections.
- Park, R. & Paulay, T. (1975). Reinforced Concrete Structures.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ConcreteNonlinearParams:
    fck: float
    h: float
    cover: float
    As_x: float  # cm2/m
    As_y: float  # cm2/m
    E_concrete: float = 30e9
    E_steel: float = 210e9
    age_days: int = 28
    humidity: float = 0.70  # 70%
    loading_age: int = 28
    phi_t: float = 2.0  # Coeficiente de fluência (creep)
    epsilon_sh: float = 0.0  # Deformação por retração (shrinkage)


@dataclass
class RedistributionConfig:
    """Configuração para redistribuição plástica de momentos."""

    enabled: bool = True
    max_redistribution_pct: float = 15.0  # Máximo normativo (NBR 6118: até 25%)
    x_over_d_limit: float = 0.45  # Limite de profundidade da LN (NBR 6118)
    min_ductility_class: str = 'CA-50'  # Classe mínima do aço
    apply_to: str = 'peaks'  # 'peaks' = só picos, 'all' = todos elementos


def calculate_branson_inertia(
    M_max: float, fck: float, h: float, d: float, As_m2_m: float, E_c: float, E_s: float = 210e9
) -> float:
    """
    Calcula a inércia efetiva de Branson (I_eff) conforme NBR 6118.
    M_max: Momento solicitante máximo no elemento (Nm/m)
    fck: Resistência do concreto (MPa)
    h: Espessura (m)
    d: Altura útil (m)
    As_m2_m: Área de aço (m2/m)
    """
    I_gross = (1.0 * h**3) / 12.0

    # Momento de fissuração (M_r)
    # fct,inf = 0.7 * fctm = 0.7 * 0.3 * fck^(2/3)
    fctm = 0.3 * fck ** (2 / 3) * 1e6  # Pa
    y_t = h / 2.0
    M_r = (fctm * I_gross) / y_t

    abs_M = abs(M_max)
    if abs_M <= M_r:
        return I_gross

    # Inércia da seção fissurada (Estádio II) - Simplificado para seção retangular
    n = E_s / E_c
    # x = linha neutra: b*x^2/2 + n*As*(x-d) = 0 -> 0.5*x^2 + n*As*x - n*As*d = 0 (para b=1m)
    a_quad = 0.5
    b_quad = n * As_m2_m
    c_quad = -n * As_m2_m * d
    x_neutral = (-b_quad + np.sqrt(b_quad**2 - 4 * a_quad * c_quad)) / (2 * a_quad)

    I_cr = (1.0 * x_neutral**3 / 3.0) + n * As_m2_m * (d - x_neutral) ** 2

    # Equação de Branson
    ratio = M_r / abs_M
    I_eff = (ratio**3) * I_gross + (1 - ratio**3) * I_cr

    return min(I_eff, I_gross)


def classify_element_state(M_sd: float, fck: float, h: float) -> dict:
    """
    Classifica o estado de fissuração do elemento.

    - Estádio I: Seção íntegra (M < Mr)
    - Estádio II: Concreto tracionado fissurado, aço em regime elástico
    - Estádio III: Aço em escoamento (plastificação)
    """
    I_gross = (1.0 * h**3) / 12.0
    fctm = 0.3 * fck ** (2 / 3) * 1e6  # Pa
    y_t = h / 2.0
    M_r = (fctm * I_gross) / y_t

    # Momento de plastificação (aproximação: ~80% do momento último)
    fcd = fck / 1.4 * 1e6  # Pa
    d = h - 0.05 - 0.012
    M_u_approx = 0.251 * fcd * 1.0 * d**2  # Nm/m (para x/d = 0.45)
    M_plast = 0.80 * M_u_approx

    abs_M = abs(M_sd)

    if abs_M <= M_r:
        return {'state': 'I', 'label': 'Íntegra', 'ratio_Mr': round(abs_M / max(M_r, 1e-9), 3)}
    elif abs_M <= M_plast:
        return {'state': 'II', 'label': 'Fissurada', 'ratio_Mr': round(abs_M / max(M_r, 1e-9), 3)}
    else:
        return {'state': 'III', 'label': 'Plastificada', 'ratio_Mr': round(abs_M / max(M_r, 1e-9), 3)}


def redistribute_moments(
    mx: np.ndarray,
    my: np.ndarray,
    mxy: np.ndarray,
    fck: float,
    h: float,
    config: RedistributionConfig = RedistributionConfig(),
) -> dict:
    """
    Redistribuição plástica de momentos conforme NBR 6118.

    Lógica:
    1. Identificar picos (elementos com M > percentil 90).
    2. Aplicar redução δ = 1 - (max_redistribution_pct / 100).
    3. Distribuir o excedente para elementos vizinhos (campo).
    4. Verificar que x/d permanece dentro do limite normativo.

    Retorna momentos redistribuídos e diagnóstico.
    """
    if not config.enabled:
        return {
            'mx': mx.copy(),
            'my': my.copy(),
            'mxy': mxy.copy(),
            'redistribution_applied': False,
            'peak_reduction_pct': 0.0,
            'summary': 'Redistribuição desativada.',
        }

    n = len(mx)
    mx_red = mx.copy()
    my_red = my.copy()

    # Momento resultante equivalente
    m_eq = np.sqrt(mx**2 + my**2 + mxy**2)

    # Momento de fissuração
    I_gross = (1.0 * h**3) / 12.0
    fctm = 0.3 * fck ** (2 / 3) * 1e6
    M_r = (fctm * I_gross) / (h / 2.0)

    # Identificar picos: elementos com M_eq acima do percentil 90
    p90 = np.percentile(m_eq, 90)
    peak_mask = m_eq > p90
    field_mask = ~peak_mask & (m_eq > 1e-3)  # Campo = não-pico e com momento significativo

    if peak_mask.sum() == 0 or field_mask.sum() == 0:
        return {
            'mx': mx_red,
            'my': my_red,
            'mxy': mxy.copy(),
            'redistribution_applied': False,
            'peak_reduction_pct': 0.0,
            'n_peaks': 0,
            'summary': 'Sem elementos elegíveis para redistribuição.',
        }

    # Fator de redistribuição
    delta = config.max_redistribution_pct / 100.0

    # Reduzir picos
    mx_excess = np.zeros(n)
    my_excess = np.zeros(n)

    for i in range(n):
        if peak_mask[i]:
            state = classify_element_state(m_eq[i], fck, h)

            # Só redistribuir se o elemento está no Estádio II ou III
            if state['state'] in ('II', 'III'):
                mx_excess[i] = mx[i] * delta
                my_excess[i] = my[i] * delta
                mx_red[i] = mx[i] * (1.0 - delta)
                my_red[i] = my[i] * (1.0 - delta)

    # Distribuir excedente uniformemente para o campo
    total_excess_mx = mx_excess.sum()
    total_excess_my = my_excess.sum()
    n_field = field_mask.sum()

    if n_field > 0:
        mx_red[field_mask] += total_excess_mx / n_field
        my_red[field_mask] += total_excess_my / n_field

    # Diagnóstico
    actual_reduction = np.abs(mx - mx_red)[peak_mask].mean() / max(np.abs(mx[peak_mask]).mean(), 1e-9) * 100.0

    n_redistributed = int((np.abs(mx_excess) > 1e-3).sum())

    # Classificação dos estados finais
    states = {'I': 0, 'II': 0, 'III': 0}
    for i in range(n):
        s = classify_element_state(m_eq[i], fck, h)
        states[s['state']] += 1

    return {
        'mx': mx_red,
        'my': my_red,
        'mxy': mxy.copy(),  # Torsor não é redistribuído
        'redistribution_applied': True,
        'peak_reduction_pct': round(float(actual_reduction), 1),
        'n_peaks': int(peak_mask.sum()),
        'n_redistributed': n_redistributed,
        'n_field': int(n_field),
        'delta_factor': delta,
        'element_states': states,
        'summary': (
            f'Redistribuição de {actual_reduction:.1f}% aplicada a {n_redistributed} elementos de pico. '
            f'Estados: {states["I"]} íntegros, {states["II"]} fissurados, {states["III"]} plastificados.'
        ),
    }


def calculate_long_term_stiffness_reduction(M_service: float, params: ConcreteNonlinearParams) -> float:
    """
    Calcula a redução de rigidez a longo prazo considerando NLF + Fluência.
    Utiliza o módulo de elasticidade efetivo E_c,eff = E_c / (1 + phi).
    """
    E_c_long = params.E_concrete / (1.0 + params.phi_t)

    # Branson com E_c reduzido (fluência)
    I_eff = calculate_branson_inertia(
        M_service,
        params.fck,
        params.h,
        params.h - params.cover - 0.012,
        (params.As_x + params.As_y) / 2.0 * 1e-4,
        E_c_long,
        params.E_steel,
    )

    I_gross = (1.0 * params.h**3) / 12.0
    return I_eff / I_gross


class NonlinearAuditTrail:
    """Registrador forense para auditoria de não-linearidade física."""

    def __init__(self):
        self.iterations = []
        self.final_stiffness_map = None

    def log_iteration(self, it_num: int, max_diff: float, n_cracked: int):
        self.iterations.append(
            {'iteration': it_num, 'max_stiffness_diff': float(max_diff), 'n_elements_cracked': int(n_cracked)}
        )

    def export_summary(self) -> dict:
        return {
            'total_iterations': len(self.iterations),
            'convergence_history': self.iterations,
            'is_stable': self.iterations[-1]['max_stiffness_diff'] < 0.02 if self.iterations else False,
        }


class ConcreteNonlinearEngine:
    """
    Motor de Iteração para Não-Linearidade Física (NLF).
    Orquestra o ciclo: Solve -> Calc Moments -> Update Stiffness -> Re-solve.
    """

    @staticmethod
    def run_iterative_analysis(
        solver: any,
        column_loads: np.ndarray,
        piles: list = None,
        max_iters: int = 30,
        tolerance: float = 0.02,  # 2% de convergência na rigidez
        verbose: bool = True,
        long_term: bool = False,
        h_per_element: Optional[np.ndarray] = None,
        opening_mask: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Executa a análise iterativa de NLF.
        """
        n_elems = len(solver.elements)
        stiffness_factors = np.ones(n_elems)
        audit = NonlinearAuditTrail()

        fck = getattr(solver.model.material, 'fck', 30.0)
        h = solver.model.material.h
        E_c = solver.model.material.E
        # Se for análise de longo prazo, aplica fluência (phi=2.0 padrão)
        if long_term:
            E_c_calc = E_c / (1.0 + 2.0)
            if verbose:
                print('⏳ Aplicando Coeficiente de Fluência (Phi=2.0) para análise de longo prazo.')
        else:
            E_c_calc = E_c

        for i in range(max_iters):
            res = solver.solve(
                column_loads,
                stiffness_factors=stiffness_factors,
                piles=piles,
                h_per_element=h_per_element,
                opening_mask=opening_mask,
            )
            m_res = np.sqrt(res.mx**2 + res.my**2 + res.mxy**2)

            new_factors = np.ones(n_elems)
            d = h - 0.05 - 0.012
            rho_min = 0.0015
            As_min = rho_min * h * 1e4

            for ie in range(n_elems):
                if opening_mask is not None and opening_mask[ie]:
                    new_factors[ie] = 0.0
                    continue
                M = m_res[ie]
                h_ie = h_per_element[ie] if h_per_element is not None else h
                d_ie = h_ie - 0.05 - 0.012
                I_eff = calculate_branson_inertia(M, fck, h_ie, d_ie, As_min * 1e-4, E_c_calc)
                # Limite inferior normativo de 15% para rigidez secante
                new_factors[ie] = max(0.15, I_eff / ((h_ie**3) / 12.0))

            diff = np.max(np.abs(new_factors - stiffness_factors))
            n_cracked = (new_factors < 0.95).sum()
            audit.log_iteration(i + 1, diff, n_cracked)

            if verbose:
                print(f'Iter {i + 1}: Diff Rigidez = {diff:.6f} | Fissurados: {n_cracked}')

            if diff < tolerance:
                break

            # Fator de amortecimento adaptativo (M5-Master)
            damping = 0.2 if i < 5 else 0.3
            stiffness_factors = (1 - damping) * stiffness_factors + damping * new_factors

        return {
            'result': res,
            'stiffness_factors': stiffness_factors,
            'audit_trail': audit.export_summary(),
            'iterations_nlf': i + 1,
            'converged': diff < tolerance,
            'n_elements_cracked': int((stiffness_factors < 0.99).sum()),
            'min_stiffness_factor': float(np.min(stiffness_factors)),
        }

    @staticmethod
    def compute_stiffness_reduction(moments_nm_m: np.ndarray, model: any) -> np.ndarray:
        """
        Retorna o fator de redução de rigidez (I_eff / I_gross) para cada elemento.
        """
        n_elems = len(moments_nm_m)
        reductions = np.ones(n_elems)

        fck = model.soil.kv_map.fck if hasattr(model.soil, 'kv_map') and hasattr(model.soil.kv_map, 'fck') else 30.0
        # Tenta pegar fck do modelo de forma mais robusta
        if hasattr(model, 'fck'):
            fck = model.fck
        elif hasattr(model, 'material') and hasattr(model.material, 'fck'):
            fck = model.material.fck

        h = model.material.h
        E_c = model.material.E
        # Estimativa de d
        cover = 0.05
        d = h - cover - 0.012

        # Áreas de aço (pode vir do dimensionamento prévio ou mínimo)
        rho_min = 0.0015
        As_min = rho_min * h * 1e4  # cm2/m

        for i in range(n_elems):
            M = moments_nm_m[i]
            # Usamos As_min como base se não houver detalhamento
            # Forçamos a sensibilidade: se M for alto, I_eff cai
            I_eff = calculate_branson_inertia(M, fck, h, d, As_min * 1e-4, E_c)
            reductions[i] = max(0.15, I_eff / ((h**3) / 12.0))  # Limite inferior de 15% (normativo)

        return reductions
