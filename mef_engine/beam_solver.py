"""
beam_solver.py — Solver de Vigas Contínuas por Método dos Elementos Finitos.

Elemento de viga Euler-Bernoulli com 2 nós e 4 DOFs (w, θ) por nó.
Suporta análise física não-linear (fissuração), redistribuição de momentos,
e seções em T (NBR 6118).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np
import math
from errors import InvalidInputError, UnstableModelError, NumericalFailureError, OutOfScopeError

try:
    import structural_core_rs
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False


# ──────────────────────── Data Models ────────────────────────

@dataclass
class BeamSection:
    """Seção transversal retangular ou T."""
    b: float = 0.20       # largura da alma (m)
    h: float = 0.50       # altura total (m)
    bf: float = 0.0       # largura da mesa (m) — se 0, usa b
    hf: float = 0.0       # espessura da mesa (m)
    cover: float = 0.035  # cobrimento (m)
    fck: float = 30.0     # MPa
    fyk: float = 500.0    # MPa
    E: float = 0.0        # Pa — se 0, calcula via fck
    asymmetric_offset: float = 0.0 # m (distancia do centroide ao centro de torção, p/ seções L)

    def __post_init__(self):
        if self.bf <= 0:
            self.bf = self.b
        if self.E <= 0:
            # NBR 6118:2023 - Módulo de Elasticidade Tangencial (Eci)
            alpha_e = 1.0 # Granito por padrão
            if self.fck <= 50:
                self.E_ci = alpha_e * 5600.0 * (self.fck ** 0.5) * 1e6
            else:
                self.E_ci = 21500.0 * alpha_e * ((self.fck + 8) / 10.0)**(1/3.0) * 1e6
            
            # Módulo de Elasticidade Secante (Ecs) para análise de deformações
            alpha_i = min(0.8 + 0.2 * (self.fck / 80.0), 1.0)
            self.E = self.E_ci * alpha_i
            
        # Momento de inércia e torção
        if self.bf > self.b and self.hf > 0:
            area_f = (self.bf - self.b) * self.hf
            area_w = self.b * self.h
            y_cg = (area_f * (self.hf / 2.0) + area_w * (self.h / 2.0)) / (area_f + area_w)
            self.I = (self.bf * self.hf**3 / 12.0 + area_f * (y_cg - self.hf/2.0)**2 +
                      self.b * self.h**3 / 12.0 + area_w * (self.h/2.0 - y_cg)**2)
            # Torção simplificada para seção T (Soma dos retângulos)
            self.J = (1/3.0) * (self.bf * self.hf**3 + self.b * (self.h - self.hf)**3)
        else:
            self.I = self.b * self.h**3 / 12.0
            # Torção retangular (aproximação de St. Venant)
            # J = beta * b * h^3 (onde b > h)
            b_max = max(self.b, self.h)
            h_min = min(self.b, self.h)
            self.J = (b_max * h_min**3) * (1/3.0 - 0.21 * (h_min/b_max) * (1 - (h_min**4)/(12 * b_max**4)))
            
        self.d = self.h - self.cover - 0.010  # altura útil
        self.G = self.E / (2 * (1 + 0.2)) # v=0.2
        self.EI = self.E * self.I
        self.GJ = self.G * self.J
        self.area = self.b * self.h + (self.bf - self.b) * self.hf


@dataclass
class BeamSupport:
    x: float                           
    type: str = 'pinned'               
    k_vertical: float = 1e12           
    k_rotational: float = 0.0          


@dataclass
class PointLoad:
    x: float         
    P: float = 0.0   
    M: float = 0.0   
    eccentricity: float = 0.0 # m (offset lateral)


@dataclass
class DistributedLoad:
    x_start: float       
    x_end: float         
    q_start: float       
    q_end: Optional[float] = None   
    eccentricity: float = 0.0 # m (offset lateral)

    def __post_init__(self):
        if self.q_end is None:
            self.q_end = self.q_start


@dataclass
class BeamModel:
    L: float                                      
    section: BeamSection = field(default_factory=BeamSection)
    supports: List[BeamSupport] = field(default_factory=list)
    point_loads: List[PointLoad] = field(default_factory=list)
    distributed_loads: List[DistributedLoad] = field(default_factory=list)
    n_elements: int = 40                          
    gamma_c: float = 1.4
    gamma_s: float = 1.15
    gamma_f: float = 1.4                          
    caa: int = 2
    wk_limit_mm: float = 0.3
    include_self_weight: bool = True


@dataclass
class BeamResult:
    x: np.ndarray              
    w: np.ndarray              
    theta: np.ndarray          
    V: np.ndarray              
    M: np.ndarray              
    T: np.ndarray              # Torsional Moment (kNm)
    x_elem: np.ndarray         
    reactions: dict             
    n_elements: int
    max_deflection_mm: float
    max_moment_kNm: float
    max_shear_kN: float
    max_torsion_kNm: float
    pedagogical_proofs: dict = field(default_factory=dict)


# ──────────────────────── FEM Solver ────────────────────────

class BeamFEMSolver:
    """Solver de vigas contínuas por Elementos Finitos."""

    def __init__(self, model: BeamModel):
        self.model = model
        self.n_elem = model.n_elements
        self.n_nodes = self.n_elem + 1
        self.ndof = 3 * self.n_nodes # w, theta, phi
        self.Le = model.L / self.n_elem
        self.x_nodes = np.linspace(0, model.L, self.n_nodes)
        self.x_elem = (self.x_nodes[:-1] + self.x_nodes[1:]) / 2.0
        
        # Validação básica de estabilidade (pelo menos 1 apoio vertical)
        if not any(s.type in ('pinned', 'roller', 'fixed', 'spring') for s in model.supports):
            raise UnstableModelError("Viga sem vínculos verticais detectada. Hipostática.", module="beam_solver")

    def _element_stiffness(self, inertia: float | None = None) -> np.ndarray:
        Ie = inertia if inertia is not None else self.model.section.I
        EI = self.model.section.E * Ie
        GJ = self.model.section.GJ
        L = self.Le
        
        # Rigidez Flexão
        kf = (EI / L**3) * np.array([
            [ 12,    6*L,   -12,    6*L  ],
            [  6*L,  4*L**2, -6*L,  2*L**2],
            [-12,   -6*L,    12,   -6*L  ],
            [  6*L,  2*L**2, -6*L,  4*L**2],
        ])
        
        # Rigidez Torção
        kt = (GJ / L) * np.array([
            [ 1, -1],
            [-1,  1]
        ])
        
        # Combinar 3 DOFs por nó (w, theta, phi)
        ke = np.zeros((6, 6))
        # Flexão (w, theta) -> indices 0,1 e 3,4
        for i, idx_i in enumerate([0, 1, 3, 4]):
            for j, idx_j in enumerate([0, 1, 3, 4]):
                ke[idx_i, idx_j] = kf[i, j]
        # Torção (phi) -> indices 2 e 5
        for i, idx_i in enumerate([2, 5]):
            for j, idx_j in enumerate([2, 5]):
                ke[idx_i, idx_j] = kt[i, j]
                
        return ke

    def _element_load_uniform(self, q: float, eccentricity: float = 0.0) -> np.ndarray:
        """Equivalente nodal para carga uniforme q (N/m) com excentricidade e (m)."""
        L = self.Le
        e_total = eccentricity + self.model.section.asymmetric_offset
        return np.array([
            -q*L/2.0,    q*L**2/12.0,  q*e_total*L/2.0, # Node 1: w, theta, phi
            -q*L/2.0,   -q*L**2/12.0,  q*e_total*L/2.0  # Node 2: w, theta, phi
        ])

    def _assemble(self, inertias: np.ndarray | None = None):
        from scipy.sparse import coo_matrix
        row_idx = []
        col_idx = []
        data_val = []
        F = np.zeros(self.ndof)

        for e in range(self.n_elem):
            Ie = inertias[e] if inertias is not None else None
            Ke = self._element_stiffness(inertia=Ie)
            # dofs: [w1, theta1, phi1, w2, theta2, phi2]
            dofs = [3*e, 3*e+1, 3*e+2, 3*e+3, 3*e+4, 3*e+5]
            for i_local in range(6):
                for j_local in range(6):
                    row_idx.append(dofs[i_local])
                    col_idx.append(dofs[j_local])
                    data_val.append(Ke[i_local, j_local])

        # Cargas distribuídas
        element_q = np.zeros(self.n_elem)
        for dl in self.model.distributed_loads:
            for e in range(self.n_elem):
                x1, x2 = self.x_nodes[e], self.x_nodes[e+1]
                xs, xe = max(x1, dl.x_start), min(x2, dl.x_end)
                if xs >= xe: continue
                
                frac_s = (xs - dl.x_start) / max(dl.x_end - dl.x_start, 1e-9)
                frac_e = (xe - dl.x_start) / max(dl.x_end - dl.x_start, 1e-9)
                q_avg = (dl.q_start + frac_s * (dl.q_end - dl.q_start) + 
                         dl.q_start + frac_e * (dl.q_end - dl.q_start)) / 2.0
                
                coverage = (xe - xs) / self.Le
                q_elemental = q_avg * coverage
                element_q[e] += q_elemental
                
                fe = self._element_load_uniform(q_elemental, eccentricity=dl.eccentricity)
                dofs = [3*e, 3*e+1, 3*e+2, 3*e+3, 3*e+4, 3*e+5]
                for i in range(6): F[dofs[i]] += fe[i]

        # Peso próprio
        if getattr(self.model, "include_self_weight", True):
            pp = self.model.section.area * 25000.0
            for e in range(self.n_elem):
                element_q[e] += pp
                fe = self._element_load_uniform(pp) # pp sem excentricidade
                dofs = [3*e, 3*e+1, 3*e+2, 3*e+3, 3*e+4, 3*e+5]
                for i in range(6): F[dofs[i]] += fe[i]
        
        self.element_q = element_q

        # Cargas concentradas
        for pl in self.model.point_loads:
            node = int(np.clip(np.round(pl.x / self.Le), 0, self.n_nodes - 1))
            F[3 * node] -= pl.P 
            e_total = pl.eccentricity + self.model.section.asymmetric_offset
            F[3 * node + 2] += pl.P * e_total  # Torsor por excentricidade
            F[3 * node + 1] += pl.M             # Momento fletor concentrado
            # pl.eccentricity já está em e_total, não somar de novo!

        # Penalidade baseada na rigidez máxima para evitar instabilidade numérica
        # P = max(diag(K)) * 1e6 é uma boa regra, mas aqui usaremos um valor alto e fixo seguro para double precision
        penalty = 1e18 
        for sup in self.model.supports:
            node = int(np.clip(np.round(sup.x / self.Le), 0, self.n_nodes - 1))
            dof_w, dof_t, dof_p = 3*node, 3*node+1, 3*node+2
            if sup.type in ('pinned', 'roller', 'fixed'):
                row_idx.append(dof_w); col_idx.append(dof_w); data_val.append(penalty)
                # Restringir torção (phi) em apoios pinned/fixed para evitar instabilidade global (mecanismo)
                if sup.type in ('pinned', 'fixed'):
                    row_idx.append(dof_p); col_idx.append(dof_p); data_val.append(penalty)
            if sup.type == 'fixed':
                row_idx.append(dof_t); col_idx.append(dof_t); data_val.append(penalty)
            if sup.type == 'spring':
                row_idx.append(dof_w); col_idx.append(dof_w); data_val.append(sup.k_vertical)
                if sup.k_rotational > 0:
                    row_idx.append(dof_t); col_idx.append(dof_t); data_val.append(sup.k_rotational)

        K = coo_matrix((data_val, (row_idx, col_idx)), shape=(self.ndof, self.ndof)).tocsr()
        return K, F

    def _solve_linear_system(self, K, F: np.ndarray) -> np.ndarray:
        from scipy.sparse.linalg import spsolve
        from scipy.sparse import eye
        ndof = len(F)
        K_reg = K + eye(ndof, format='csr') * 1e-9
        return spsolve(K_reg, F)

    def solve(self, inertias: np.ndarray | None = None) -> BeamResult:
        pedagogical_proofs = {}
        if RUST_AVAILABLE and inertias is None:
            try:
                from structural_core_rs import (
                    Beam1DModel, Beam1DSupportPy, Beam1DPointLoadPy, 
                    Beam1DDistLoadPy, solve_beams_from_model
                )
                
                rust_supports = []
                for sup in self.model.supports:
                    kw = 1.0 if sup.type in ('pinned', 'roller', 'fixed', 'spring') else 0.0
                    kt = 1.0 if sup.type == 'fixed' or (sup.type == 'spring' and sup.k_rotational > 0) else 0.0
                    kp = 1.0 if sup.type in ('pinned', 'fixed') else 0.0 
                    rust_supports.append(Beam1DSupportPy(sup.x, kw, kt, kp))
                
                rust_points = [
                    Beam1DPointLoadPy(pl.x, pl.P, pl.M, pl.eccentricity)
                    for pl in self.model.point_loads
                ]
                
                rust_dists = [
                    Beam1DDistLoadPy(dl.x_start, dl.x_end, dl.q_start, dl.q_end, dl.eccentricity)
                    for dl in self.model.distributed_loads
                ]
                if self.model.include_self_weight:
                    pp = self.model.section.area * 25000.0
                    rust_dists.append(Beam1DDistLoadPy(0.0, self.model.L, pp, pp, 0.0))
                
                model_rust = Beam1DModel(
                    self.model.L, self.n_elem, self.model.section.E, self.model.section.G,
                    self.model.section.I, self.model.section.J,
                    rust_supports, rust_points, rust_dists,
                    self.model.section.asymmetric_offset
                )
                
                rust_res = solve_beams_from_model(model_rust)
                U = rust_res['u']
                pedagogical_proofs = rust_res.get('pedagogical_proofs', {})
                
            except Exception as e:
                import traceback
                print(f"Rust Beam Solver Error: {e}. Falling back to Python.")
                traceback.print_exc()
                K, F = self._assemble(inertias=inertias)
                U = self._solve_linear_system(K, F)
        else:
            K, F = self._assemble(inertias=inertias)
            U = self._solve_linear_system(K, F)
            pedagogical_proofs = {}

        # Cálculo de esforços e reações em Python (Garante paridade total)
        V_res, M_res, T_res = np.zeros(self.n_elem), np.zeros(self.n_elem), np.zeros(self.n_elem)
        
        # Garantir que element_q esteja calculado (se não foi pelo _assemble)
        if not hasattr(self, "element_q"):
            self._assemble(inertias=inertias) # Apenas para popular element_q
            
        for e in range(self.n_elem):
            Ie = inertias[e] if inertias is not None else None
            Ke = self._element_stiffness(inertia=Ie)
            ue = U[3*e:3*e+6]
            ecc = 0.0
            for dl in self.model.distributed_loads:
                if dl.x_start <= self.x_elem[e] <= dl.x_end:
                    ecc = dl.eccentricity
                    break
            fe = self._element_load_uniform(self.element_q[e], eccentricity=ecc)
            f_int = Ke @ ue - fe
            V_res[e] = f_int[0]
            M_res[e] = -f_int[1]
            T_res[e] = -f_int[2]

        reactions = {}
        for sup in self.model.supports:
            node = int(np.clip(np.round(sup.x / self.Le), 0, self.n_nodes - 1))
            dof_w, dof_t, dof_p = 3*node, 3*node+1, 3*node+2
            Rv, Rm, Rt = 0.0, 0.0, 0.0
            penalty = 1e18
            if sup.type in ('pinned', 'roller', 'fixed'):
                Rv = penalty * (0 - U[dof_w])
            if sup.type == 'fixed':
                Rm = penalty * (0 - U[dof_t])
                Rt = penalty * (0 - U[dof_p])
            if sup.type == 'spring':
                Rv = sup.k_vertical * (0 - U[dof_w])
            reactions[str(float(sup.x))] = {
                'x': float(sup.x),
                'type': sup.type,
                'R': float(Rv)/1000.0, 
                'M': float(Rm)/1000.0, 
                'T': float(Rt)/1000.0
            }
            
        return self._build_result(U, V_res, M_res, T_res, reactions, pedagogical_proofs)
        
        # DEBUG
        # print(f"DEBUG SOLVER REACTIONS: {reactions}")

    def _build_result(self, U, V_res, M_res, T_res, reactions, pedagogical_proofs=None):
        """Helper para construir o objeto BeamResult padronizado."""
        w, theta = U[0::3], U[1::3]
        max_deflection = np.max(np.abs(w)) * 1000.0
        max_moment = np.max(np.abs(M_res))
        max_shear = np.max(np.abs(V_res))
        max_torsion = np.max(np.abs(T_res))

        return BeamResult(
            x=self.x_nodes, w=w, theta=theta, V=V_res, M=M_res, T=T_res,
            x_elem=self.x_elem, reactions=reactions, n_elements=self.n_elem,
            max_deflection_mm=max_deflection,
            max_moment_kNm=max_moment/1000.0,
            max_shear_kN=max_shear/1000.0,
            max_torsion_kNm=max_torsion/1000.0,
            pedagogical_proofs=pedagogical_proofs
        )


class NonlinearBeamEngine:
    @staticmethod
    def solve_iterative(solver: BeamFEMSolver, max_iters: int = 15, tol: float = 0.01) -> BeamResult:
        n_elem = solver.n_elem
        current_inertias = np.full(n_elem, solver.model.section.I)
        fctm = 0.3 * (solver.model.section.fck ** (2/3))
        Mr = (fctm * 1e6) * solver.model.section.I / (solver.model.section.h / 2.0)
        
        res = solver.solve()
        for i in range(max_iters):
            new_inertias = np.zeros(n_elem)
            for e in range(n_elem):
                Ma = abs(res.M[e])
                if Ma <= Mr: new_inertias[e] = solver.model.section.I
                else:
                    I_cr = 0.3 * solver.model.section.I
                    ratio = (Mr / Ma) ** 3
                    new_inertias[e] = max(ratio * solver.model.section.I + (1 - ratio) * I_cr, 0.2 * solver.model.section.I)
            
            diff = np.max(np.abs(new_inertias - current_inertias)) / np.mean(current_inertias)
            current_inertias = new_inertias
            res = solver.solve(inertias=current_inertias)
            if diff < tol: break
        return res


# ──────────────────────── Design NBR 6118 ────────────────────────

class BeamDesigner:
    @staticmethod
    def design_flexure(md_kNm: float, section: BeamSection, gamma_f: float = 1.4) -> dict:
        """Dimensionamento à flexão (ELU) - NBR 6118."""
        fck = section.fck
        fcd = fck / 1.4
        fyd = section.fyk / 1.15
        bw = section.b
        d = section.d
        
        # Parâmetros para fck <= 50
        eta = 0.85
        lamb = 0.8
        x_d_lim = 0.45 if fck <= 50 else 0.35
        
        md_d = abs(md_kNm) * 1000.0 # N.m
        
        # Seleção da largura de compressão (bf para momento positivo em viga T)
        # Assumimos que md_kNm > 0 significa tração na face inferior (vão)
        is_t_compression = md_kNm > 0 and section.bf > section.b and section.hf > 0
        b_calc = section.bf if is_t_compression else section.b
        
        # Coeficiente adimensional k = Md / (bw * d^2 * fcd)
        k = md_d / (b_calc * d**2 * fcd * 1e6) if (b_calc * d) > 0 else 0
        
        # k_limite para dutilidade
        k_lim = eta * lamb * x_d_lim * (1 - 0.5 * lamb * x_d_lim)
        
        as_compression = 0.0
        if k > k_lim:
            # Armadura Dupla
            m_lim = k_lim * (bw * d**2 * fcd * 1e6)
            m_delta = md_d - m_lim
            d_prime = section.cover + 0.010
            as_compression = m_delta / (fyd * 1e6 * (d - d_prime))
            as_tension_lim = m_lim / (fyd * 1e6 * d * (1 - 0.5 * lamb * x_d_lim))
            as_tension = as_tension_lim + as_compression
            xi = x_d_lim
            status = "ARMADURA_DUPLA"
        else:
            # Armadura Simples
            discriminant = 1.0 - (2.0 * k / eta)
            xi = (1.0 - math.sqrt(max(0, discriminant))) / lamb if k > 0 else 0
            
            # Verificação de Seção T Verdadeira (x > hf)
            if is_t_compression and (xi * d) > section.hf:
                # Seção T Verdadeira - Cálculo mais complexo (Aproximação: soma de alma e abas)
                m_mesa = eta * fcd * 1e6 * (section.bf - section.b) * section.hf * (d - 0.5 * section.hf)
                m_alma = md_d - m_mesa
                k_alma = m_alma / (section.b * d**2 * fcd * 1e6)
                disc_alma = 1.0 - (2.0 * k_alma / eta)
                xi_alma = (1.0 - math.sqrt(max(0, disc_alma))) / lamb if k_alma > 0 else 0
                as_tension = (m_mesa / (fyd * 1e6 * (d - 0.5 * section.hf))) + (m_alma / (fyd * 1e6 * d * (1 - 0.5 * lamb * xi_alma)))
                xi = xi_alma # Aproximação para status
                status = "T_VERDADEIRA"
            else:
                z = d * (1.0 - 0.5 * lamb * xi)
                as_tension = md_d / (fyd * 1e6 * z) if z > 0 else 0
                status = "OK"
            
        # Armadura Mínima (0.15% para C25/C30)
        as_min = 0.0015 * bw * section.h * 1e4 # cm2
        as_cm2 = max(as_tension * 1e4, as_min)
        
        return {
            'Md_kNm': round(md_kNm, 2),
            'As_cm2': round(as_cm2, 2),
            'As_prime_cm2': round(as_compression * 1e4, 2),
            'x_d': round(xi, 3),
            'x_d_lim': x_d_lim,
            'k': round(k, 3),
            'status': status,
            'domain': 2 if xi <= 0.259 else (3 if xi <= x_d_lim else 4)
        }

    @staticmethod
    def design_shear_torsion(v_sd_kN: float, t_sd_kNm: float, section: BeamSection) -> dict:
        """Verificação de cisalhamento e torção combinados - NBR 6118."""
        fck = section.fck
        fcd = fck / 1.4
        fyd = section.fyk / 1.15
        b = section.b
        d = section.d
        h = section.h
        
        # 1. Biela de Compressão (Cisalhamento)
        alpha_v = (1 - fck / 250.0)
        vrd2 = 0.27 * alpha_v * fcd * b * d * 1000.0 # kN
        
        # 2. Biela de Compressão (Torção)
        # Seção vazada equivalente Ae, ue
        c = section.cover + 0.010
        be = b - 2*c
        he = h - 2*c
        Ae = be * he
        ue = 2 * (be + he)
        trd2 = 0.5 * alpha_v * fcd * Ae * (Ae / ue) * 1000.0 # kNm (simplificado)
        
        check_diagonal = (v_sd_kN / vrd2) + (t_sd_kNm / trd2) if vrd2 > 0 and trd2 > 0 else 0
        
        # 3. Armadura Transversal (Estribos)
        fctd = 0.7 * 0.3 * (fck**(2/3)) / 1.4
        vc = 0.6 * fctd * b * d * 1000.0 # kN
        vsw = max(0, v_sd_kN - vc)
        asw_v = (vsw / (0.9 * d * fyd / 10.0)) # cm2/m
        
        # Torção
        asw_t = (t_sd_kNm * 100.0 / (2 * Ae * 1e4 * fyd / 10.0)) * 100.0 # cm2/m (por ramo)
        
        asw_total = asw_v + 2 * asw_t # Total de ramos
        as_min = 0.2 * (fctd/fck*10) * b * 100.0 # cm2/m
        asw_final = max(asw_total, as_min)
        
        return {
            'Vsd_kN': round(v_sd_kN, 2),
            'Tsd_kNm': round(t_sd_kNm, 2),
            'Vrd2_kN': round(vrd2, 2),
            'Vc_kN': round(vc, 2),
            'Vsw_kN': round(vsw, 2),
            'Asw_cm2_m': round(asw_final, 2),
            'biela_status': 'OK' if check_diagonal <= 1.0 else 'FALHA',
            'interaction_diag': round(check_diagonal, 3)
        }

    @staticmethod
    def design_crack_width(mk_kNm: float, as_cm2: float, section: BeamSection) -> float:
        """Estimativa simplificada de abertura de fissuras (wk) conforme NBR 6118."""
        if as_cm2 <= 0: return 0.5
        rho_p = as_cm2 / (section.b * section.h * 10000.0)
        phi = 12.5 # mm
        fctm = 0.3 * (section.fck**(2/3))
        sigma_s = (abs(mk_kNm) * 1000.0) / (0.9 * section.d * as_cm2 / 10000.0) / 1e6 # MPa
        wk1 = (phi / (12.5 * 2.25)) * (sigma_s / 210000.0) * (3 * sigma_s / fctm)
        return min(0.4, max(0.01, wk1))

    @staticmethod
    def apply_moment_redistribution(M_elem: np.ndarray, support_nodes: List[int], delta: float = 0.90) -> np.ndarray:
        M_red = M_elem.copy()
        for node in support_nodes:
            if node < len(M_elem) and M_red[node] < 0: M_red[node] *= delta
            if node > 0 and M_red[node-1] < 0: M_red[node-1] *= delta
        return M_red

    @classmethod
    def full_design(cls, result: BeamResult, model: BeamModel, redistribution_delta: float = 0.90) -> dict:
        support_nodes = [int(np.round(s.x / (model.L / result.n_elements))) for s in model.supports]
        M_design = cls.apply_moment_redistribution(result.M, support_nodes, delta=redistribution_delta)
        
        gamma_f = model.gamma_f
        M_max_pos = np.max(M_design) / 1000.0 * gamma_f
        M_max_neg = np.min(M_design) / 1000.0 * gamma_f
        V_max = np.max(np.abs(result.V)) / 1000.0 * gamma_f
        T_max = np.max(np.abs(result.T)) / 1000.0 * gamma_f
        
        flex_bottom = cls.design_flexure(M_max_pos, model.section, gamma_f)
        flex_top = cls.design_flexure(-abs(M_max_neg), model.section, gamma_f) # Negativo força uso da alma (bw)
        shear = cls.design_shear_torsion(V_max, T_max, model.section)
        
        # ELS - Abertura de fissuras
        mk_serv = np.max(np.abs(result.M)) / 1000.0
        wk = cls.design_crack_width(mk_serv, max(flex_bottom['As_cm2'], flex_top['As_cm2']), model.section)
        deflection_limit_mm = round(model.L * 1000 / 250, 2)
        deflection_status = 'OK' if result.max_deflection_mm <= deflection_limit_mm else 'REVISAR'
        
        # Inteligência de Custo
        from cost_engine import CostEngine
        c_engine = CostEngine()
        total_as = flex_bottom['As_cm2'] + flex_top['As_cm2']
        cost_data = c_engine.calculate_beam_cost(
            model.section.b, model.section.h, model.L, total_as, model.section.fck
        )

        crack_status = 'OK' if wk <= model.wk_limit_mm else 'REVISAR'
        flexure_status = (
            flex_bottom['x_d'] <= flex_bottom['x_d_lim']
            and flex_top['x_d'] <= flex_top['x_d_lim']
        )
        overall_status = (
            'ATENDE'
            if shear['biela_status'] == 'OK'
            and flexure_status
            and crack_status == 'OK'
            and deflection_status == 'OK'
            else 'REVISAR'
        )
        
        return {
            'redistribution_applied': redistribution_delta,
            'M_max_pos_kNm': round(M_max_pos, 2),
            'M_max_neg_kNm': round(M_max_neg, 2),
            'flexure_bottom': flex_bottom,
            'flexure_top': flex_top,
            'shear': shear,
            'crack_width': {'wk_mm': wk, 'limit_mm': model.wk_limit_mm, 'status': crack_status},
            'deflection': {
                'max_mm': result.max_deflection_mm, 
                'limit_mm': deflection_limit_mm, 
                'status': deflection_status
            },
            'cost_analysis': cost_data,
            'overall_status': overall_status
        }

    @staticmethod
    def optimize_section(model: BeamModel, md_pos: float, md_neg: float, vd: float) -> dict:
        """
        Busca a seção transversal mais econômica (b x h) que satisfaz as normas.
        """
        from cost_engine import CostEngine
        c_engine = CostEngine()
        
        best_cost = float('inf')
        best_section = None
        
        # Espaço de busca: b de 15 a 40cm, h de 30 a 90cm
        for b in [0.15, 0.20, 0.25]:
            for h in np.linspace(0.30, 0.90, 13):
                test_sec = BeamSection(b=b, h=h, fck=model.section.fck)
                
                # Verifica ELU
                flex_p = BeamDesigner.design_flexure(md_pos, test_sec)
                flex_n = BeamDesigner.design_flexure(md_neg, test_sec)
                shear = BeamDesigner.design_shear_torsion(vd, 0.0, test_sec)
                
                if (flex_p['status'] == 'OK' and flex_n['status'] == 'OK' and 
                    shear['biela_status'] == 'OK' and flex_p['x_d'] < 0.45):
                    
                    as_total = flex_p['As_cm2'] + flex_n['As_cm2']
                    cost = c_engine.calculate_beam_cost(b, h, model.L, as_total, test_sec.fck)['total_cost']
                    
                    if cost < best_cost:
                        best_cost = cost
                        best_section = {'b': b, 'h': h, 'as_total': as_total}
        
        return {
            'best_section': best_section,
            'savings_potential': 'ALTO' if best_section else 'BAIXO'
        }


def _suggest_stirrup(Asw_cm2_m: float, bw: float) -> str:
    options = [(5.0, 0.196), (6.3, 0.312), (8.0, 0.503), (10.0, 0.785)]
    for phi, area_bar in options:
        s = min(2 * area_bar / max(Asw_cm2_m / 100.0, 1e-9), 30.0)
        commercial = [s_c for s_c in [5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30] if s_c <= s]
        if commercial: return f"φ{phi} c/{max(commercial)}"
    return "φ10 c/5"


class ClassicalBeamSolver:
    @staticmethod
    def _distributed_load_resultant(dl: DistributedLoad, a: float, b: float) -> tuple[float, float]:
        """Resultante e centroide de uma carga linear no intervalo [a, b]."""
        length_total = max(dl.x_end - dl.x_start, 1e-9)
        qa = dl.q_start + (dl.q_end - dl.q_start) * ((a - dl.x_start) / length_total)
        qb = dl.q_start + (dl.q_end - dl.q_start) * ((b - dl.x_start) / length_total)
        load_len = b - a
        force = 0.5 * (qa + qb) * load_len
        if abs(force) < 1e-12:
            return 0.0, 0.5 * (a + b)
        centroid_from_a = load_len * (qa + 2.0 * qb) / (3.0 * (qa + qb)) if abs(qa + qb) > 1e-12 else 0.5 * load_len
        return force, a + centroid_from_a

    @staticmethod
    def _total_distributed_load(dl: DistributedLoad) -> tuple[float, float]:
        return ClassicalBeamSolver._distributed_load_resultant(dl, dl.x_start, dl.x_end)

    @staticmethod
    def generate_diagrams(model: 'BeamModel', fea_reactions: dict = None):
        L = model.L
        pts = model.point_loads or []
        dloads = model.distributed_loads or []
        sups = model.supports or []
        
        if not sups:
            return {
                'x_m': np.linspace(0, L, 100).tolist(),
                'V_kN': np.zeros(100).tolist(),
                'M_kNm': np.zeros(100).tolist(),
                'reactions': []
            }

        # Peso Próprio
        all_dloads = list(dloads)
        if getattr(model, "include_self_weight", True):
            pp = model.section.area * 25000.0
            all_dloads.append(DistributedLoad(x_start=0.0, x_end=L, q_start=pp, q_end=pp))

        # Reações de Apoio
        internal_reactions = []
        if fea_reactions:
            for x_pos, data in fea_reactions.items():
                internal_reactions.append({
                    'x': float(x_pos), 
                    'R': data.get('R', data.get('V_kN', 0.0)) * 1000.0, 
                    'M': -data.get('M', 0.0) * 1000.0
                })
        else:
            s_sorted = sorted(sups, key=lambda s: s.x)
            if len(sups) >= 2:
                s1, s2 = s_sorted[0], s_sorted[-1]
                x1, x2 = s1.x, s2.x
                dist = x2 - x1
                if dist > 0:
                    load_resultants = [ClassicalBeamSolver._total_distributed_load(dl) for dl in all_dloads]
                    M_loads_x1 = sum(p.P * (p.x - x1) for p in pts) + \
                                 sum(force * (centroid - x1) for force, centroid in load_resultants)
                    R2 = M_loads_x1 / dist
                    R1 = (sum(force for force, _ in load_resultants) + sum(p.P for p in pts)) - R2
                    internal_reactions = [{'x': x1, 'R': R1}, {'x': x2, 'R': R2}]
            elif len(sups) == 1:
                s1 = sups[0]
                x1 = s1.x
                load_resultants = [ClassicalBeamSolver._total_distributed_load(dl) for dl in all_dloads]
                R1 = (sum(force for force, _ in load_resultants) + sum(p.P for p in pts))
                M1 = sum(p.P * (p.x - x1) for p in pts) + \
                     sum(force * (centroid - x1) for force, centroid in load_resultants)
                internal_reactions = [{'x': x1, 'R': R1, 'M': -M1}]

        # Geração dos pontos por Método das Seções
        n_points = 100
        x = np.linspace(0, L, n_points)
        V = np.zeros(n_points)
        M = np.zeros(n_points)
        
        for i, xi in enumerate(x):
            curr_v = 0.0
            curr_m = 0.0
            
            for dl in all_dloads:
                x_end = min(xi, dl.x_end)
                if x_end > dl.x_start:
                    force, centroid = ClassicalBeamSolver._distributed_load_resultant(dl, dl.x_start, x_end)
                    curr_v -= force
                    curr_m -= force * (xi - centroid)
            
            for p in pts:
                if xi > p.x + 1e-6:
                    curr_v -= p.P
                    curr_m -= p.P * (xi - p.x)
            
            for r in internal_reactions:
                if xi > r['x'] - 1e-6:
                    curr_v += r['R']
                    curr_m += r['R'] * (xi - r['x'])
                    if 'M' in r:
                        curr_m += r['M']
            
            V[i] = curr_v
            M[i] = curr_m

        return {
            'x_m': x.tolist(),
            'V_kN': (V / 1000.0).tolist(),
            'M_kNm': (M / 1000.0).tolist(),
            'max_shear_kN': float(np.max(np.abs(V)) / 1000.0),
            'max_moment_kNm': float(np.max(np.abs(M)) / 1000.0),
            'reactions': [{'x': r['x'], 'R': r['R']/1000.0} for r in internal_reactions],
            'supports_debug': str([f"x={s.x}" for s in sups]),
            'formulas': ClassicalBeamSolver.generate_formulas(model, internal_reactions)
        }

    @staticmethod
    def generate_formulas(model: 'BeamModel', internal_reactions: list):
        """Gera as equações simbólicas de V(x) e M(x) por trecho (Método de Macaulay)."""
        pts = {0.0, model.L}
        for s in model.supports: pts.add(s.x)
        for p in model.point_loads: pts.add(p.x)
        for dl in model.distributed_loads:
            pts.add(dl.x_start)
            pts.add(dl.x_end)
        
        sorted_pts = sorted(list(pts))
        trechos = []
        
        for i in range(len(sorted_pts) - 1):
            x1, x2 = sorted_pts[i], sorted_pts[i+1]
            if x2 - x1 < 1e-4: continue
            
            v_parts = []
            m_parts = []
            
            # Macaulay-style: somar termos que iniciam em a <= x1
            # 1. Reações
            for r in internal_reactions:
                if r['x'] <= x1 + 1e-4:
                    rv = r['R'] / 1000.0
                    if abs(rv) > 1e-3:
                        v_parts.append(f"{rv:+.2f}")
                        m_parts.append(f"{rv:+.2f}(x - {r['x']:.2f})")
                    if 'M' in r and abs(r['M']) > 1e-3:
                        rm = r['M'] / 1000.0
                        m_parts.append(f"{rm:+.2f}")

            # 2. Cargas Pontuais
            for p in model.point_loads:
                if p.x <= x1 + 1e-4:
                    pv = p.P / 1000.0
                    if abs(pv) > 1e-3:
                        v_parts.append(f"{-pv:+.2f}")
                        m_parts.append(f"{-pv:+.2f}(x - {p.x:.2f})")
                    if abs(p.M) > 1e-3:
                        pm = p.M / 1000.0
                        m_parts.append(f"{pm:+.2f}")
            
            # 3. Cargas Distribuídas
            pp = (model.section.area * 25000.0 / 1000.0) if getattr(model, "include_self_weight", True) else 0.0
            if pp > 0:
                v_parts.append(f"{-pp:+.2f}(x - 0.00)")
                m_parts.append(f"{-pp/2.0:+.2f}(x - 0.00)^2")
                if model.L <= x1 + 1e-4:
                    v_parts.append(f"{pp:+.2f}(x - {model.L:.2f})")
                    m_parts.append(f"{pp/2.0:+.2f}(x - {model.L:.2f})^2")

            for dl in model.distributed_loads:
                if dl.x_start <= x1 + 1e-4:
                    q = dl.q_start / 1000.0
                    v_parts.append(f"{-q:+.2f}(x - {dl.x_start:.2f})")
                    m_parts.append(f"{-q/2.0:+.2f}(x - {dl.x_start:.2f})^2")
                    if dl.x_end <= x1 + 1e-4:
                        v_parts.append(f"{q:+.2f}(x - {dl.x_end:.2f})")
                        m_parts.append(f"{q/2.0:+.2f}(x - {dl.x_end:.2f})^2")
            
            # Limpeza e formatação final
            def clean_expr(parts):
                if not parts: return "0.00"
                s = " ".join(parts).replace("+", " + ").replace("-", " - ").strip()
                if s.startswith("+ "): s = s[2:]
                return s

            trechos.append({
                "range": f"{x1:.2f} \le x < {x2:.2f}",
                "shear": f"V(x) = {clean_expr(v_parts)}",
                "moment": f"M(x) = {clean_expr(m_parts)}"
            })
        return trechos


def _durability_params(caa: int, member_type: str) -> dict:
    from durability_checker import DurabilityChecker, DurabilityConfig
    caa_int = int(max(1, min(4, caa)))
    cover_mm = DurabilityChecker.get_min_cover(DurabilityConfig(caa=caa_int), member_type)
    wk_limits = {1: 0.4, 2: 0.3, 3: 0.2, 4: 0.2}
    return {'caa': caa_int, 'cover_m': cover_mm / 1000.0, 'cover_mm': cover_mm, 'wk_limit_mm': wk_limits[caa_int]}


def run_beam_analysis(L, supports, distributed_loads=None, point_loads=None, b=0.20, h=0.50, fck=30.0, bf=0.0, hf=0.0, n_elements=40, nonlinear=True, redistribution_delta=0.90, caa=2, cover=None, include_self_weight=True, gamma_f=1.4, asymmetric_offset=0.0):
    # --- Hardening e Sanitização de Inputs ---
    try:
        L = float(L)
        b = float(b)
        h = float(h)
        fck = float(fck)
        n_elements = int(n_elements)
        include_self_weight = bool(include_self_weight)
        nonlinear = bool(nonlinear)
        gamma_f = float(gamma_f)
    except (ValueError, TypeError):
        raise InvalidInputError("Parâmetros geométricos ou de materiais inválidos.", module="beam_solver")

    durability = _durability_params(caa, 'beam')
    cover_m = float(cover) if cover is not None else durability['cover_m']
    section = BeamSection(b=b, h=h, fck=fck, bf=bf, hf=hf, cover=cover_m, asymmetric_offset=asymmetric_offset)
    
    proc_dist = []
    for dl in (distributed_loads or []):
        try:
            qs = float(dl.get('q_start', 0.0))
            qe = float(dl.get('q_end', qs))
            xs = float(dl.get('x_start', 0.0))
            xe = float(dl.get('x_end', L))
            if xe > xs:
                proc_dist.append({
                    'x_start': xs, 'x_end': xe, 
                    'q_start': qs * 1000.0, 'q_end': qe * 1000.0
                })
        except: continue

    proc_points = []
    for pl in (point_loads or []):
        try:
            proc_points.append({
                'x': float(pl.get('x', 0.0)), 
                'P': float(pl.get('P', 0.0)) * 1000.0, 
                'M': float(pl.get('M', 0.0)) * 1000.0
            })
        except: continue

    # Converter suportes explicitamente para garantir tipos (blindagem contra strings do frontend)
    beam_supports = []
    for s in (supports or []):
        try:
            beam_supports.append(BeamSupport(
                x=float(s.get('x', 0.0)),
                type=str(s.get('type', 'pinned')),
                k_vertical=float(s.get('k_vertical', 1e14)),
                k_rotational=float(s.get('k_rotational', 0.0))
            ))
        except: continue

    model = BeamModel(L=L, section=section, 
                      supports=beam_supports,
                      distributed_loads=[DistributedLoad(**dl) for dl in proc_dist],
                      point_loads=[PointLoad(**pl) for pl in proc_points], 
                      caa=durability['caa'], 
                      wk_limit_mm=durability['wk_limit_mm'],
                      include_self_weight=include_self_weight,
                      gamma_f=gamma_f)

    solver = BeamFEMSolver(model)
    linear_result = solver.solve()
    result = NonlinearBeamEngine.solve_iterative(solver) if nonlinear else linear_result
    
    # Sincronização de Reações e Diagramas Clássicos
    # Usamos result.reactions que já está em kN e garantimos chaves string
    reactions_dict = {str(float(k)): v for k, v in result.reactions.items()}
    classical_res = ClassicalBeamSolver.generate_diagrams(model, fea_reactions=reactions_dict)
    
    design = BeamDesigner.full_design(result, model, redistribution_delta=redistribution_delta)
    design['durability'] = {
        'caa': durability['caa'],
        'cover_required_mm': durability['cover_mm'],
        'cover_mm': round(cover_m * 1000, 1),
        'cover_ok': cover_m * 1000.0 >= durability['cover_mm'],
    }

    # Balanço de Cargas para Auditoria (Soma de módulos para evitar cancelamento em análise linear)
    total_load_n = 0.0
    for dl in model.distributed_loads:
        total_load_n += 0.5 * (dl.q_start + dl.q_end) * (dl.x_end - dl.x_start)
    for pl in model.point_loads:
        total_load_n += abs(pl.P)
    if include_self_weight:
        total_load_n += section.area * 25000.0 * L
    
    total_reaction_kn = sum(abs(r['R']) for r in result.reactions.values())
    
    # Gerar Resumo de Detalhamento 3D (Módulo 6-7)
    from beam_detailing import BeamDetailer
    detailing_summary = BeamDetailer.generate_detailing_summary(design, L, h, fck)

    # Gerar Memorial Pedagógico (Mestre) via dispatcher seguro
    from master_pedagogy import build_beam_blackboard, build_forensic_audit, build_composite_pedagogy
    
    # 1. Memorial de Dimensionamento
    pedagogical_steps = build_beam_blackboard({
        'summary': {
            'L_m': L, 'b_m': b, 'h_m': h, 'bf_m': section.bf,
            'max_moment_kNm': result.max_moment_kNm,
            'max_shear_kN': result.max_shear_kN,
            'max_deflection_mm': result.max_deflection_mm,
            'total_load_kN': round(total_load_n / 1000.0, 2),
            'total_reaction_kN': round(total_reaction_kn, 2),
        },
        'design': design,
        'classical_diagrams': classical_res,
        'reactions': result.reactions
    }, {
        'L': L, 'b': b, 'h': h, 'fck': fck, 'caa': caa, 'cover_mm': round(cover_m * 1000, 1),
        'distributed_loads': distributed_loads,
        'point_loads': point_loads
    })

    # 2. Auditoria Forense (MEF vs Analítico)
    analytical_baseline = {
        'max_moment_kNm': abs(classical_res.get('max_moment_kNm', result.max_moment_kNm)),
        'max_shear_kN': abs(classical_res.get('max_shear_kN', result.max_shear_kN))
    }
    audit_trail = build_forensic_audit("beam", {
        'summary': {
            'total_load_kN': total_load_n / 1000.0,
            'total_reaction_kN': total_reaction_kn,
            'max_moment_kNm': result.max_moment_kNm,
        }
    }, analytical_baseline)

    # 4. Composição Multi-Mestre (Unifica Dimensionamento + Detalhamento + Auditoria)
    # Passamos os dados completos para que os builders tenham acesso aos diagramas e cargas
    beam_result_context = {
        "summary": {
            "L_m": L, "b_m": b, "h_m": h, "fck_MPa": fck,
            "max_moment_kNm": result.max_moment_kNm,
            "max_shear_kN": result.max_shear_kN,
            "total_load_kN": round(total_load_n / 1000.0, 2),
            "total_reaction_kN": round(total_reaction_kn, 2),
        },
        "design": design,
        "classical_diagrams": classical_res,
        "reactions": result.reactions
    }
    
    full_pedagogy = build_composite_pedagogy([
        {"type": "beam", "result": beam_result_context, "payload": {"distributed_loads": distributed_loads, "point_loads": point_loads, "L": L}},
        {"type": "detailing", "result": detailing_summary, "payload": {}},
        {"type": "audit", "result": {"summary": {"total_load_kN": total_load_n/1000, "total_reaction_kN": total_reaction_kn, "max_moment_kNm": result.max_moment_kNm}}, "payload": {"analytical": analytical_baseline}}
    ])

    return {
        'id': 'beam_1',
        'success': True,
        'L': model.L,
        'summary': {
            'L_m': L, 'b_m': b, 'h_m': h, 'bf_m': section.bf, 
            'max_deflection_mm': result.max_deflection_mm,
            'max_moment_kNm': result.max_moment_kNm,
            'max_shear_kN': result.max_shear_kN,
            'analysis_type': 'FISICA_NAO_LINEAR' if nonlinear else 'ELASTICA_LINEAR',
            'fck_MPa': fck, 'caa': durability['caa'], 'cover_mm': round(cover_m * 1000, 1),
            'total_load_kN': round(total_load_n / 1000.0, 2),
            'total_reaction_kN': round(total_reaction_kn, 2),
            'residual_kN': round((total_load_n/1000.0) - total_reaction_kn, 3),
            'overall_status': design.get('overall_status', 'ATENDE')
        },
        'design': design, 
        'detailing': detailing_summary,
        'forensic_audit': audit_trail,
        'reactions': reactions_dict,
        'overall_status': design.get('overall_status', 'ATENDE'),
        'diagrams': {
            'shear': [{'x': float(x), 'y': float(y)} for x, y in zip(result.x_elem, result.V / 1000.0)],
            'moment': [{'x': float(x), 'y': float(y)} for x, y in zip(result.x_elem, result.M / 1000.0)],
            'deflection': [{'x': float(x), 'y': float(y)} for x, y in zip(result.x, result.w * 1000.0)]
        },
        'classical_diagrams': classical_res,
        'classical_reactions': classical_res.get('reactions', []),
        'pedagogical_steps': full_pedagogy,
        'torsion_audit': {
            'asymmetric_offset': asymmetric_offset,
            'is_asymmetric': asymmetric_offset != 0,
            'citation': "NBR 6118:2023, 17.5 / Libânio Módulo 22"
        },
        'model_info': {
            'L': L, 'fck': fck, 'bw': b, 'h': h, 'd': round(section.d, 3), 'EI': float(section.EI)
        }
    }
