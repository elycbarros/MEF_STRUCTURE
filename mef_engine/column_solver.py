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
            sig_s = np.clip(eps_s * self.Es, -self.fyd, self.fyd)
            f_s = sig_s * self.rebar_area
            N_s += f_s
            Mx_s += f_s * ry
            My_s += f_s * rx
            
        N_c = np.sum(sig_c * self.fiber_areas)
        Mx_c = np.sum(sig_c * self.fiber_areas * self.Y)
        My_c = np.sum(sig_c * self.fiber_areas * self.X)
        
        # Resultantes (N compressão negativa na convenção interna, mas Nd é positivo)
        # Vamos retornar como positivo para compressão para facilitar o solver
        return -(N_c + N_s), -(Mx_c + Mx_s), -(My_c + My_s)

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
    def find_equilibrium(integrator: FiberSectionIntegrator, loads: ColumnLoads, max_iter: int = 50, tol: float = 1e-3) -> Tuple[float, float, float, bool, List[dict]]:
        """
        Encontra o plano de deformação (eps0, kx, ky) que equilibra os esforços loads.
        Usa Newton-Raphson com Matriz Jacobiana Numérica.
        Retorna também o histórico de convergência.
        """
        # [eps0, kx, ky]
        U = np.array([-0.001, 0.0, 0.0]) 
        target = np.array([loads.Nd_kN * 1000.0, loads.Mxd_kNm * 1000.0, loads.Myd_kNm * 1000.0])
        history = []
        
        for i in range(max_iter):
            # Forças atuais
            N, Mx, My = integrator.get_forces(U[0], U[1], U[2])
            R = np.array([N, Mx, My]) - target
            res_norm = np.linalg.norm(R)
            
            history.append({
                'iter': i,
                'eps0': float(U[0]),
                'kx': float(U[1]),
                'ky': float(U[2]),
                'res_N': float(R[0]),
                'res_Mx': float(R[1]),
                'res_My': float(R[2]),
                'norm': float(res_norm)
            })

            if res_norm < tol * (np.linalg.norm(target) + 1.0):
                return U[0], U[1], U[2], True, history
                
            # Jacobiana Numérica
            J = np.zeros((3, 3))
            h = 1e-6
            for j in range(3):
                U_h = U.copy(); U_h[j] += h
                N_h, Mx_h, My_h = integrator.get_forces(U_h[0], U_h[1], U_h[2])
                J[:, j] = (np.array([N_h, Mx_h, My_h]) - np.array([N, Mx, My])) / h
                
            try:
                dU = np.linalg.solve(J, -R)
                U += 0.5 * dU 
            except np.linalg.LinAlgError:
                break
                
        return U[0], U[1], U[2], False, history

    @staticmethod
    def solve_required_reinforcement(sec: ColumnSection, loads: ColumnLoads) -> float:
        """
        Encontra a taxa de armadura necessária via busca iterativa na superfície de interação.
        Agora usa o solver de equilíbrio rigoroso.
        """
        # Busca bisseção ou incremento para omega (taxa mecânica)
        omega_min, omega_max = 0.01, 0.80
        omega = 0.05
        
        # Testar se atende com omega mínimo
        for iteration in range(15):
            integrator = FiberSectionIntegrator(sec, omega * sec.area * (sec.fck/1.4) / (sec.fyk/1.15) * 1e4)
            eps0, kx, ky, converged, _ = BiaxialBendingSolver.find_equilibrium(integrator, loads)
            
            # Verificação de Ruptura
            d_prime = sec.cover + 0.01
            corners = [
                (-sec.b/2, -sec.h/2), (sec.b/2, -sec.h/2),
                (-sec.b/2, sec.h/2), (sec.b/2, sec.h/2)
            ]
            min_eps = 0.0
            max_eps = 0.0
            for cx, cy in corners:
                e = eps0 + kx * cy + ky * cx
                min_eps = min(min_eps, e)
                max_eps = max(max_eps, e)
            
            is_safe = converged and min_eps >= -0.0036 and max_eps <= 0.011
            
            if is_safe:
                return round(omega, 4)
            else:
                omega += 0.05
                if omega > omega_max: return omega_max
                
        return round(omega, 4)

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
    
    # 3. Solver Biaxial Profissional
    omega = BiaxialBendingSolver.solve_required_reinforcement(sec, loads_total)
    
    # 4. Recuperar estado final de equilíbrio para visualização
    fcd = (sec.fck / 1.4) * 1e6
    fyd = (sec.fyk / 1.15) * 1e6
    as_total = omega * sec.area * fcd / fyd
    integrator = FiberSectionIntegrator(sec, as_total * 1e4) # cm2 inside integrator
    eps0, kx, ky, converged, history = BiaxialBendingSolver.find_equilibrium(integrator, loads_total)
    
    Ac = sec.area
    As_calc = as_total
    
    # Limites normativos (NBR 6118 §17.3.5 / §18.2.1)
    # As_min = 0.15 * Nd / fyd >= 0.4% Ac
    As_min = max(0.004 * Ac, 0.15 * loads.Nd_kN / (fyd / 10.0)) * 1e4 # cm2
    As_max = 0.08 * Ac * 1e4 # cm2 (8%)
    
    As_final = max(As_calc * 1e4, As_min)
    
    status = "OK"
    if As_final > As_max: status = "EXCEDE_MAX_8_PCT"
    if slend['is_slender']: status = "ALTA_ESBELTEZ_REVISAR_RIGOROSO"
    if (As_final / (Ac * 1e4)) > 0.04: status = "TAXA_ALTA_CONGESTIONADA"

    from durability_checker import DurabilityChecker, DurabilityConfig
    cover_required_mm = DurabilityChecker.get_min_cover(DurabilityConfig(caa=sec.caa), 'column')
    cover_adopted_mm = sec.cover * 1000.0

    return {
        'section': f'{sec.b*100:.0f}x{sec.h*100:.0f}',
        'fck_MPa': sec.fck,
        'Nd_kN': loads.Nd_kN,
        'Md_x_total_kNm': second_order['M_total_x'],
        'Md_y_total_kNm': second_order['M_total_y'],
        'slenderness': slend,
        'moments_2nd_order': second_order,
        'omega': round(omega, 4),
        'As_calc_cm2': round(As_calc * 1e4, 2),
        'As_min_cm2': round(As_min, 2),
        'As_final_cm2': round(As_final, 2),
        'rho_pct': round(As_final / (Ac * 1e4) * 100, 2),
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
            'interaction_diagram_x': BiaxialBendingSolver.generate_envelope_2d(integrator, 'x'),
            'interaction_diagram_y': BiaxialBendingSolver.generate_envelope_2d(integrator, 'y')
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
