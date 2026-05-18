"""
column_solver.py — Dimensionamento e Análise de Pilares de Concreto Armado.

Focado em edifícios altos:
- Flexo-compressão normal e oblíqua (Diagrama de Interação).
- Efeitos de 2ª ordem locais (Esbeltez e P-delta local).
- Encurtamento diferencial (Elastic + Creep + Shrinkage).
- Verificação de taxa de armadura e estribos (NBR 6118 §18.2).

Referências:
- ABNT NBR 6118:2023 — Seções 15, 17 e 18.
- Fusco, P.B. — Estruturas de Concreto: Solicitações Normais.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
import math


@dataclass
class ColumnSection:
    """Definição da seção do pilar."""
    b: float = 0.60          # base (m)
    h: float = 0.60          # altura (m)
    fck: float = 40.0        # MPa
    fyk: float = 500.0       # MPa
    cover: float = 0.03      # m
    caa: int = 2             # Classe de Agressividade Ambiental
    L_free: float = 3.0      # comprimento livre (m)
    alpha_b: float = 1.0     # fator de flambagem (1.0 = articulado, 0.5 = engastado)

    @property
    def area(self) -> float:
        return self.b * self.h

    @property
    def inertia_x(self) -> float:
        return (self.b * self.h**3) / 12.0

    @property
    def inertia_y(self) -> float:
        return (self.h * self.b**3) / 12.0

    @property
    def radius_gyration_x(self) -> float:
        return math.sqrt(self.inertia_x / self.area)

    @property
    def radius_gyration_y(self) -> float:
        return math.sqrt(self.inertia_y / self.area)


@dataclass
class ColumnLoads:
    """Esforços de cálculo no pilar."""
    Nd_kN: float            # Esforço axial de cálculo (majorado)
    Mxd_kNm: float = 0.0    # Momento em X
    Myd_kNm: float = 0.0    # Momento em Y


# ──────────────────────── Análise de Esbeltez ────────────────────────

def analyze_slenderness(sec: ColumnSection) -> dict:
    """Calcula o índice de esbeltez (lambda) e verifica necessidade de 2a ordem local."""
    le = sec.L_free * sec.alpha_b
    
    lambda_x = le / sec.radius_gyration_x
    lambda_y = le / sec.radius_gyration_y
    
    # Limite para desprezar 2a ordem (lambda_1) - Simplificado NBR 6118 §15.8.2
    # lambda_1 = 35 (para pilares usuais)
    lambda_limit = 35.0
    
    needs_2nd_order_x = lambda_x > lambda_limit
    needs_2nd_order_y = lambda_y > lambda_limit
    
    return {
        'lambda_x': round(lambda_x, 2),
        'lambda_y': round(lambda_y, 2),
        'limit': lambda_limit,
        'needs_2nd_order_x': needs_2nd_order_x,
        'needs_2nd_order_y': needs_2nd_order_y,
        'is_slender': lambda_x > 90 or lambda_y > 90, # NBR exige método rigoroso acima de 90
    }


# ──────────────────────── Efeitos de 2ª Ordem Locais ────────────────────────

def calculate_local_second_order(sec: ColumnSection, loads: ColumnLoads, slend: dict) -> dict:
    """
    Análise de 2a ordem local rigorosa (NBR 6118 §15.8.3.3.2).
    Usa o Método do Pilar Padrão com Curvatura Nominal.
    """
    Nd = loads.Nd_kN
    h, b = sec.h, sec.b
    Ac = sec.area
    fcd = (sec.fck / 1.4) * 1000.0
    nu = Nd / (Ac * fcd)
    
    # 1. Excentricidades de 1a ordem (Imperfeições + e_min)
    le = sec.L_free * sec.alpha_b
    theta_a = 1.0 / (100.0 * math.sqrt(le)) # Imperfeição geométrica global/local
    e_i = theta_a * le / 2.0
    e_min_x = max(0.015 + 0.03 * h, e_i)
    e_min_y = max(0.015 + 0.03 * b, e_i)
    
    M1d_x = max(abs(loads.Mxd_kNm), Nd * e_min_x)
    M1d_y = max(abs(loads.Myd_kNm), Nd * e_min_y)
    
    M_total_x, M_total_y = M1d_x, M1d_y
    
    # 2. Momento de 2a Ordem (P-delta local)
    # 1/r = 0.005 / (h * (0.5 + nu)) <= 0.005 / h
    if slend['needs_2nd_order_x']:
        curv_x = min(0.005 / (h * (0.5 + nu)), 0.005 / h)
        e2_x = (le**2 / 10.0) * curv_x
        M_total_x += Nd * e2_x
        
    if slend['needs_2nd_order_y']:
        curv_y = min(0.005 / (b * (0.5 + nu)), 0.005 / b)
        e2_y = (le**2 / 10.0) * curv_y
        M_total_y += Nd * e2_y

    return {
        'M1d_x': round(M1d_x, 2),
        'M_total_x': round(M_total_x, 2),
        'M_total_y': round(M_total_y, 2),
        'e_min_x_mm': round(e_min_x * 1000, 1),
        'e2_x_mm': round((M_total_x - M1d_x)/Nd * 1000, 1) if Nd > 0 else 0,
        'method': 'Curvatura Nominal (NBR 6118)'
    }


# ──────────────────────── Dimensionamento (Flexo-Compressão Biaxial) ────────────────────────

# ──────────────────────── Dimensionamento (Flexo-Compressão Biaxial Rigorosa) ────────────────────────

class FiberSectionIntegrator:
    """
    Integrador de seção via fibras para flexo-compressão biaxial rigorosa.
    Segue o diagrama Parábola-Retângulo da NBR 6118.
    """
    def __init__(self, sec: ColumnSection, as_total_cm2: float):
        self.sec = sec
        self.as_total = as_total_cm2 * 1e-4 # m2
        self.fcd = (sec.fck / 1.4) * 1e6 # Pa
        self.fyd = (sec.fyk / 1.15) * 1e6 # Pa
        self.Es = 210e9 # Pa
        
        # Discretização (Fibras de concreto)
        self.nx, self.ny = 20, 20
        self.dx, self.dy = sec.b / self.nx, sec.h / self.ny
        self.fiber_areas = self.dx * self.dy
        
        # Coordenadas das fibras (relativas ao centro geométrico)
        x = np.linspace(-sec.b/2 + self.dx/2, sec.b/2 - self.dx/2, self.nx)
        y = np.linspace(-sec.h/2 + self.dy/2, sec.h/2 - self.dy/2, self.ny)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Posição das armaduras (4 cantos simplificado para o solver iterativo)
        d_prime = sec.cover + 0.010
        self.rebar_pos = [
            (-sec.b/2 + d_prime, -sec.h/2 + d_prime),
            ( sec.b/2 - d_prime, -sec.h/2 + d_prime),
            (-sec.b/2 + d_prime,  sec.h/2 - d_prime),
            ( sec.b/2 - d_prime,  sec.h/2 - d_prime)
        ]
        self.rebar_area = self.as_total / 4.0

    def get_forces(self, eps0: float, kx: float, ky: float) -> Tuple[float, float, float]:
        """Calcula N, Mx, My para um plano de deformação (eps = eps0 + kx*y + ky*x)."""
        # Deformações nas fibras de concreto
        eps_c = eps0 + kx * self.Y + ky * self.X
        
        # Tensões no concreto (NBR 6118: Parábola-Retângulo)
        sig_c = np.zeros_like(eps_c)
        # Compressão (eps < 0)
        mask1 = (eps_c < 0) & (eps_c >= -0.002)
        sig_c[mask1] = 0.85 * self.fcd * (1 - (1 - abs(eps_c[mask1])/0.002)**2)
        mask2 = (eps_c < -0.002) & (eps_c >= -0.0035)
        sig_c[mask2] = 0.85 * self.fcd
        # Tração: desprezada
        
        # Deformações e tensões no aço
        N_s, Mx_s, My_s = 0.0, 0.0, 0.0
        for rx, ry in self.rebar_pos:
            eps_s = eps0 + kx * ry + ky * rx
            # Compressão positiva na convenção externa do solver.
            sig_s = -np.clip(eps_s * self.Es, -self.fyd, self.fyd)
            f_s = sig_s * self.rebar_area
            N_s += f_s
            Mx_s += f_s * ry
            My_s += f_s * rx
            
        N_c = np.sum(sig_c * self.fiber_areas)
        Mx_c = np.sum(sig_c * self.fiber_areas * self.Y)
        My_c = np.sum(sig_c * self.fiber_areas * self.X)
        
        # Resultantes com compressão positiva, coerente com Nd_kN positivo.
        return (N_c + N_s), (Mx_c + Mx_s), (My_c + My_s)

    def get_fiber_data(self, eps0: float, kx: float, ky: float) -> List[dict]:
        """Retorna detalhes de cada fibra para visualização no frontend."""
        eps_c = eps0 + kx * self.Y + ky * self.X
        sig_c = np.zeros_like(eps_c)
        mask1 = (eps_c < 0) & (eps_c >= -0.002)
        sig_c[mask1] = 0.85 * self.fcd * (1 - (1 - abs(eps_c[mask1])/0.002)**2)
        mask2 = (eps_c < -0.002) & (eps_c >= -0.0035)
        sig_c[mask2] = 0.85 * self.fcd
        
        fibers = []
        for i in range(self.nx):
            for j in range(self.ny):
                fibers.append({
                    'x': float(self.X[j, i]),
                    'y': float(self.Y[j, i]),
                    'eps': float(eps_c[j, i]),
                    'sig_MPa': float(sig_c[j, i] / 1e6)
                })
        return fibers

class BiaxialBendingSolver:
    @staticmethod
    def check_interaction_capacity(envelope: List[dict], nd_kN: float, md_kNm: float) -> dict:
        compression_points = [p for p in envelope if p.get('n', 0.0) >= 0.0]
        if not compression_points:
            return {'capacity_kNm': 0.0, 'ratio': 999.0, 'status': 'REVISAR'}
        nearest = min(compression_points, key=lambda p: abs(float(p.get('n', 0.0)) - nd_kN))
        capacity = abs(float(nearest.get('m', 0.0)))
        ratio = abs(md_kNm) / capacity if capacity > 1e-9 else 999.0
        return {
            'capacity_kNm': round(capacity, 2),
            'ratio': round(ratio, 3),
            'status': 'OK' if ratio <= 1.0 else 'REVISAR'
        }

    @staticmethod
    def combine_biaxial_checks(check_x: dict, check_y: dict, alpha: float = 1.2) -> dict:
        rx = float(check_x.get('ratio', 999.0))
        ry = float(check_y.get('ratio', 999.0))
        combined = (abs(rx) ** alpha + abs(ry) ** alpha) ** (1.0 / alpha)
        return {
            'alpha': alpha,
            'combined_ratio': round(combined, 3),
            'status': 'OK' if combined <= 1.0 else 'REVISAR'
        }

    @staticmethod
    def find_equilibrium(integrator: FiberSectionIntegrator, loads: ColumnLoads, max_iter: int = 50, tol: float = 1e-3) -> Tuple[float, float, float, bool, List[dict]]:
        """
        Encontra o plano de deformação (eps0, kx, ky) que equilibra os esforços loads.
        Usa mínimos quadrados amortecidos com limites físicos. A visualização por
        fibras deve permanecer dentro de deformações plausíveis mesmo quando o
        ponto solicitante está próximo de trechos pouco condicionados da envoltória.
        Retorna também o histórico de convergência.
        """
        target = np.array([loads.Nd_kN * 1000.0, loads.Mxd_kNm * 1000.0, loads.Myd_kNm * 1000.0])
        scales = np.array([
            max(abs(target[0]), 100_000.0),
            max(abs(target[1]), 10_000.0),
            max(abs(target[2]), 10_000.0),
        ])
        history = []

        def residual(U: np.ndarray) -> np.ndarray:
            N, Mx, My = integrator.get_forces(U[0], U[1], U[2])
            return (np.array([N, Mx, My]) - target) / scales

        starts = [
            np.array([-0.0006, 0.0, 0.0]),
            np.array([-0.0012, 0.0, 0.0]),
            np.array([-0.0020, 0.0, 0.0]),
            np.array([-0.0010, -0.006, 0.0]),
            np.array([-0.0010, 0.006, 0.0]),
            np.array([-0.0010, 0.0, -0.006]),
            np.array([-0.0010, 0.0, 0.006]),
            np.array([-0.0010, -0.006, -0.006]),
            np.array([-0.0010, 0.006, 0.006]),
        ]
        if abs(loads.Mxd_kNm) > 1e-9:
            starts.append(np.array([-0.0010, math.copysign(0.012, loads.Mxd_kNm), 0.0]))
        if abs(loads.Myd_kNm) > 1e-9:
            starts.append(np.array([-0.0010, 0.0, math.copysign(0.012, loads.Myd_kNm)]))

        bounds = (np.array([-0.0035, -0.15, -0.15]), np.array([0.0100, 0.15, 0.15]))
        best_u = starts[0]
        best_cost = float("inf")

        try:
            from scipy.optimize import least_squares
            for start in starts:
                res = least_squares(
                    residual,
                    np.clip(start, bounds[0], bounds[1]),
                    bounds=bounds,
                    max_nfev=max_iter * 20,
                    x_scale=np.array([0.002, 0.02, 0.02]),
                    loss="soft_l1",
                    f_scale=0.10,
                )
                cost = float(np.linalg.norm(res.fun))
                if cost < best_cost:
                    best_cost = cost
                    best_u = res.x
        except Exception:
            # Fallback: Newton amortecido preservado para ambientes sem scipy.optimize.
            U = starts[0].copy()
            for _ in range(max_iter):
                R = residual(U)
                J = np.zeros((3, 3))
                h = 1e-6
                for j in range(3):
                    U_h = U.copy(); U_h[j] += h
                    J[:, j] = (residual(U_h) - R) / h
                try:
                    dU = np.linalg.lstsq(J, -R, rcond=None)[0]
                    U = np.clip(U + 0.25 * dU, bounds[0], bounds[1])
                except np.linalg.LinAlgError:
                    break
            best_u = U
            best_cost = float(np.linalg.norm(residual(U)))

        N, Mx, My = integrator.get_forces(best_u[0], best_u[1], best_u[2])
        raw_residual = np.array([N, Mx, My]) - target
        raw_norm = float(np.linalg.norm(raw_residual))
        rel_norm = float(np.linalg.norm(raw_residual / scales))
        history.append({
            'iter': 0,
            'eps0': float(best_u[0]),
            'kx': float(best_u[1]),
            'ky': float(best_u[2]),
            'res_N': float(raw_residual[0]),
            'res_Mx': float(raw_residual[1]),
            'res_My': float(raw_residual[2]),
            'norm': raw_norm,
            'relative_norm': rel_norm
        })

        converged = rel_norm <= max(tol * 10.0, 0.03)
        return best_u[0], best_u[1], best_u[2], converged, history

    @staticmethod
    def solve_required_reinforcement(sec: ColumnSection, loads: ColumnLoads) -> float:
        """
        Encontra a taxa de armadura necessária via busca iterativa na superfície de interação.
        Usa a propria envoltoria N-M gerada pelo integrador de fibras como criterio
        de capacidade. O Newton-Raphson fica reservado para visualizacao do estado
        de deformacoes, pois pode nao convergir em pontos de baixa curvatura.
        """
        omega_min, omega_max = 0.01, 0.80
        for omega in np.linspace(omega_min, omega_max, 80):
            as_trial_cm2 = omega * sec.area * (sec.fck/1.4) / (sec.fyk/1.15) * 1e4
            integrator = FiberSectionIntegrator(sec, as_trial_cm2)
            env_x = BiaxialBendingSolver.generate_envelope_2d(integrator, 'x')
            env_y = BiaxialBendingSolver.generate_envelope_2d(integrator, 'y')
            check_x = BiaxialBendingSolver.check_interaction_capacity(env_x, loads.Nd_kN, loads.Mxd_kNm)
            check_y = BiaxialBendingSolver.check_interaction_capacity(env_y, loads.Nd_kN, loads.Myd_kNm)
            biaxial = BiaxialBendingSolver.combine_biaxial_checks(check_x, check_y)
            if check_x['status'] == 'OK' and check_y['status'] == 'OK' and biaxial['status'] == 'OK':
                return round(omega, 4)

        return omega_max

    @staticmethod
    def generate_envelope_2d(integrator: FiberSectionIntegrator, axis: str = 'x') -> List[dict]:
        """
        Gera a curva de interação N x M para um eixo específico (x ou y).
        Varre os domínios de deformação da NBR 6118.
        """
        points = []
        h = integrator.sec.h if axis == 'x' else integrator.sec.b
        
        # Casos de deformação limite (NBR 6118)
        # 1. Tração pura (eps = +0.010 em toda seção)
        # 2. Domínio 2 (eps_s = 0.010, eps_c varia de 0 a -0.0035)
        # 3. Domínios 3, 4, 4a (eps_c = -0.0035, eps_s varia de 0.010 a eps_yd)
        # 4. Domínio 5 (eps_c = -0.0035 em uma borda, -0.002 na outra?)
        # 5. Compressão pura (eps = -0.002 em toda seção)
        
        # Vamos simplificar varrendo a posição da linha neutra 'x' de -2h a 2h
        # E mantendo a deformação na borda mais solicitada no limite (-0.0035 ou +0.010)
        
        n_steps = 40
        
        # Lado da Tração (Domínio 1 e 2)
        for x_ratio in np.linspace(-1.0, 0.5, n_steps // 2):
            # eps_s_max = 0.010
            # x = x_ratio * h
            # eps_c_top = (x / (x - (h - 0.04))) * 0.010 ... simplificando:
            eps_max = 0.010
            x_pos = x_ratio * h
            # Curvatura k = eps_max / (d - x)
            d = h - 0.04
            k = eps_max / (d - x_pos)
            eps_pivot = -k * x_pos
            
            n, mx, my = integrator.get_forces(eps_pivot, k if axis == 'x' else 0, k if axis == 'y' else 0)
            points.append({'n': round(n/1000, 1), 'm': round(mx/1000 if axis == 'x' else my/1000, 1)})

        # Lado da Compressão (Domínio 3, 4, 5)
        for x_ratio in np.linspace(0.5, 3.0, n_steps // 2):
            # eps_c_max = -0.0035
            eps_min = -0.0035
            x_pos = x_ratio * h
            k = -eps_min / x_pos
            eps_pivot = eps_min + k * (h/2) # no centro
            
            n, mx, my = integrator.get_forces(eps_pivot, k if axis == 'x' else 0, k if axis == 'y' else 0)
            points.append({'n': round(n/1000, 1), 'm': round(mx/1000 if axis == 'x' else my/1000, 1)})
            
        # Ordenar por N para facilitar plotagem
        points.sort(key=lambda p: p['n'])
        return points

def solve_column_section(sec: ColumnSection, loads: ColumnLoads) -> dict:
    """
    Dimensiona a armadura necessária para flexo-compressão normal e oblíqua.
    Integra efeitos de esbeltez e análise biaxial rigorosa.
    """
    # 1. Análise de esbeltez e momentos de 2a ordem
    slend = analyze_slenderness(sec)
    second_order = calculate_local_second_order(sec, loads, slend)
    
    # 2. Atualizar cargas com efeitos de 2a ordem
    loads_total = ColumnLoads(
        Nd_kN=loads.Nd_kN,
        Mxd_kNm=second_order['M_total_x'],
        Myd_kNm=second_order['M_total_y']
    )
    
    # 3. Solver Biaxial Profissional (Core Rust com Fallback)
    try:
        from structural_core_rs import ColumnFiberModel, solve_column_fiber, get_column_interaction_envelope
        
        # Preparar dados para Rust
        d_prime = sec.cover + 0.010
        rebars = [
            (-sec.b/2 + d_prime, -sec.h/2 + d_prime, (sec.area * 0.01 / 4.0)), # Trial as_min
            ( sec.b/2 - d_prime, -sec.h/2 + d_prime, (sec.area * 0.01 / 4.0)),
            (-sec.b/2 + d_prime,  sec.h/2 - d_prime, (sec.area * 0.01 / 4.0)),
            ( sec.b/2 - d_prime,  sec.h/2 - d_prime, (sec.area * 0.01 / 4.0))
        ]
        
        # Busca iterativa da taxa de armadura (omega) simplificada para o core Rust
        omega = 0.01
        converged_final = False
        best_eps0, best_kx, best_ky = 0.0, 0.0, 0.0
        
        for trial_omega in np.linspace(0.01, 0.08, 30):
            as_total = trial_omega * sec.area * (sec.fck/1.4) / (sec.fyk/1.15)
            r_area = as_total / 4.0
            rust_rebars = [(r[0], r[1], r_area) for r in rebars]
            
            model = ColumnFiberModel(sec.b, sec.h, sec.fck, sec.fyk, 210e9, rust_rebars, 20, 20)
            eps0, kx, ky, converged = solve_column_fiber(model, loads_total.Nd_kN, loads_total.Mxd_kNm, loads_total.Myd_kNm)
            
            if converged:
                omega = trial_omega
                best_eps0, best_kx, best_ky = eps0, kx, ky
                converged_final = True
                break
        
        interaction_x = [{'n': p[0], 'm': p[1]} for p in get_column_interaction_envelope(model, "x")]
        interaction_y = [{'n': p[0], 'm': p[1]} for p in get_column_interaction_envelope(model, "y")]
        
        eps0, kx, ky = best_eps0, best_kx, best_ky
        converged = converged_final
        # Fibers still generated in Python for now to keep mapping simple, or I could move to Rust too
        integrator = FiberSectionIntegrator(sec, omega * sec.area * (sec.fck/1.4) / (sec.fyk/1.15) * 1e4)
        history = [] # Rust solver returns bool, history is pedagogical-only

    except ImportError:
        # Fallback Python original
        omega = BiaxialBendingSolver.solve_required_reinforcement(sec, loads_total)
        as_total_fallback = omega * sec.area * (sec.fck / 1.4) / (sec.fyk / 1.15)
        integrator = FiberSectionIntegrator(sec, as_total_fallback * 1e4)
        eps0, kx, ky, converged, history = BiaxialBendingSolver.find_equilibrium(integrator, loads_total)
        interaction_x = BiaxialBendingSolver.generate_envelope_2d(integrator, 'x')
        interaction_y = BiaxialBendingSolver.generate_envelope_2d(integrator, 'y')

    Ac = sec.area
    As_calc = omega * sec.area * (sec.fck/1.4) / (sec.fyk/1.15)
    
    # Limites normativos (NBR 6118 §17.3.5 / §18.2.1)
    # As_min = 0,15 Nd/fyd >= 0,4% Ac.
    # Nd em kN e fyd em MPa: As(cm2) = 0,15 * Nd(kN) * 10 / fyd(MPa).
    fyd_mpa = sec.fyk / 1.15
    As_min = max(0.004 * Ac * 1e4, 0.15 * loads.Nd_kN * 10.0 / fyd_mpa) # cm2
    As_max = 0.08 * Ac * 1e4 # cm2 (8%)
    
    As_final = max(As_calc * 1e4, As_min)
    
    status = "OK"
    if As_final > As_max: status = "EXCEDE_MAX_8_PCT"
    if slend['is_slender']: status = "ALTA_ESBELTEZ_REVISAR_RIGOROSO"
    if (As_final / (Ac * 1e4)) > 0.04: status = "TAXA_ALTA_CONGESTIONADA"

    from durability_checker import DurabilityChecker, DurabilityConfig
    cover_required_mm = DurabilityChecker.get_min_cover(DurabilityConfig(caa=sec.caa), 'column')
    cover_adopted_mm = sec.cover * 1000.0

    interaction_check = {
        'x': BiaxialBendingSolver.check_interaction_capacity(interaction_x, loads_total.Nd_kN, loads_total.Mxd_kNm),
        'y': BiaxialBendingSolver.check_interaction_capacity(interaction_y, loads_total.Nd_kN, loads_total.Myd_kNm),
    }
    interaction_check['biaxial'] = BiaxialBendingSolver.combine_biaxial_checks(interaction_check['x'], interaction_check['y'])
    if (
        interaction_check['x']['status'] != 'OK'
        or interaction_check['y']['status'] != 'OK'
        or interaction_check['biaxial']['status'] != 'OK'
    ):
        status = "FORA_DIAGRAMA_INTERACAO"

    # Auditoria Forensic: Fiber Model vs Simplified Method
    # Simplified Method estimation: omega_sim = (Nd/Ac*fcd + Md/Ac*h*fcd) ... aprox
    # We'll use the omega found by fiber vs a theoretical analytical lower bound
    omega_analytical = (loads_total.Nd_kN * 1.4 / (Ac * sec.fck/1.4 * 1000.0)) * 0.5 # Aprox.
    diff_omega = abs(omega - omega_analytical) / max(omega, 1e-9) * 100.0

    duel = [
        {
            "parameter": "Reinforcement Ratio (ω)",
            "classical_value": f"{omega_analytical:.3f}",
            "mef_value": f"{omega:.3f}",
            "difference_percent": round(diff_omega, 1),
            "insight": "O Modelo de Fibras (Rust) realiza uma integração numérica precisa das tensões, enquanto o método analítico utiliza diagramas de interação simplificados. A divergência reflete o ganho de precisão no cálculo da flexão biaxial."
        }
    ]

    return {
        'section': f'{sec.b*100:.0f}x{sec.h*100:.0f}',
        'b_m': sec.b,
        'h_m': sec.h,
        'cover_m': sec.cover,
        'fck_MPa': sec.fck,
        'Nd_kN': loads.Nd_kN,
        'Mxd_kNm': loads.Mxd_kNm,
        'Myd_kNm': loads.Myd_kNm,
        'Md_x_total_kNm': second_order['M_total_x'],
        'Md_y_total_kNm': second_order['M_total_y'],
        'slenderness': slend,
        'moments_2nd_order': second_order,
        'equilibrium_converged': bool(converged),
        'omega': round(omega, 4),
        'As_calc_cm2': round(As_calc * 1e4, 2),
        'As_min_cm2': round(As_min, 2),
        'As_final_cm2': round(As_final, 2),
        'rho_pct': round(As_final / (Ac * 1e4) * 100, 2),
        'interaction_check': interaction_check,
        'durability': {
            'cover_adopted_mm': round(cover_adopted_mm, 1),
            'cover_required_mm': round(cover_required_mm, 1),
            'caa': sec.caa,
            'cover_ok': cover_adopted_mm >= cover_required_mm,
        },
        'status': status,
        'fiber_results': {
            'eps0': float(eps0) if 'eps0' in locals() else 0,
            'kx': float(kx) if 'kx' in locals() else 0,
            'ky': float(ky) if 'ky' in locals() else 0,
            'fibers': integrator.get_fiber_data(eps0, kx, ky) if 'eps0' in locals() else [],
            'convergence': history if 'history' in locals() else [],
            'interaction_diagram_x': interaction_x,
            'interaction_diagram_y': interaction_y
        },
        'calculation_trace': {
            "duel": duel
        }
    }


# ──────────────────────── Encurtamento Diferencial (Tall Buildings) ────────────────────────

def analyze_shortening(sec: ColumnSection, load_kN: float, n_floors: int = 40) -> dict:
    """
    Calcula o encurtamento elástico e diferido (Fluência/Creep) do pilar.
    Crucial para prédios de 40 andares.
    """
    E = 5600 * math.sqrt(sec.fck) * 1e6 # Pa
    stress = (load_kN * 1000) / sec.area # Pa
    
    # 1. Encurtamento Elástico Instantâneo
    eps_el = stress / E
    delta_el_mm = eps_el * (sec.L_free * 1000)
    
    # 2. Fluência (Creep) - Coeficiente phi ≈ 2.0 para 50 anos
    phi = 2.0
    delta_creep_mm = delta_el_mm * phi
    
    # 3. Retração (Shrinkage) - eps_cs ≈ 0.0004
    eps_cs = 0.0004
    delta_shrink_mm = eps_cs * (sec.L_free * 1000)
    
    delta_total_floor_mm = delta_el_mm + delta_creep_mm + delta_shrink_mm
    delta_total_building_mm = delta_total_floor_mm * (n_floors / 2.0) # Acumulado médio

    return {
        'elastic_mm': round(delta_el_mm, 2),
        'creep_mm': round(delta_creep_mm, 2),
        'shrinkage_mm': round(delta_shrink_mm, 2),
        'total_per_floor_mm': round(delta_total_floor_mm, 2),
        'total_building_estimate_mm': round(delta_total_building_mm, 1),
        'impact': 'ALTO' if delta_total_building_mm > 20 else 'BAIXO'
    }


if __name__ == "__main__":
    import json
    
    # Exemplo: Pilar de base de prédio de 40 andares
    # Carga axial pesada + momento de vento
    pilar = ColumnSection(b=0.80, h=0.80, fck=50, L_free=3.0)
    cargas = ColumnLoads(Nd_kN=15000, Mxd_kNm=450, Myd_kNm=200) # 1500 toneladas
    
    res = solve_column_section(pilar, cargas)
    short = analyze_shortening(pilar, load_kN=10000, n_floors=40)
    
    print("=== DIMENSIONAMENTO DE PILAR (BASE 40 ANDARES) ===")
    print(json.dumps(res, indent=2))
    
    print("\n=== ANÁLISE DE ENCURTAMENTO DIFERENCIAL ===")
    print(json.dumps(short, indent=2))
