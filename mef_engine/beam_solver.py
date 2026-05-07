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
from errors import InvalidInputError, UnstableModelError, NumericalFailureError, OutOfScopeError


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
            self.E = 5600.0 * (self.fck ** 0.5) * 1e6  # NBR 6118: Eci
            
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

        # Apoios (Penalidade)
        penalty = 1e16
        for sup in self.model.supports:
            node = int(np.clip(np.round(sup.x / self.Le), 0, self.n_nodes - 1))
            dof_w, dof_t, dof_p = 3*node, 3*node+1, 3*node+2
            if sup.type in ('pinned', 'roller', 'fixed'):
                row_idx.append(dof_w); col_idx.append(dof_w); data_val.append(penalty)
                # Restringir torção (phi) em apoios pinned/roller para evitar instabilidade global
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
        K, F_load = self._assemble(inertias=inertias)
        try:
            U = self._solve_linear_system(K, F_load)
        except Exception as e:
            raise UnstableModelError(f"Erro na resolução da viga: {str(e)}. Verifique os apoios.", module="beam_solver")
        
        w, theta, phi = U[0::3], U[1::3], U[2::3]
        V_res, M_res, T_res = np.zeros(self.n_elem), np.zeros(self.n_elem), np.zeros(self.n_elem)
        
        for e in range(self.n_elem):
            Ie = inertias[e] if inertias is not None else None
            Ke = self._element_stiffness(inertia=Ie)
            ue = U[3*e:3*e+6]
            # Encontrar excentricidade média do elemento se houver carga distribuída
            ecc = 0.0
            for dl in self.model.distributed_loads:
                if dl.x_start <= self.x_elem[e] <= dl.x_end:
                    ecc = dl.eccentricity
                    break
            
            fe = self._element_load_uniform(self.element_q[e], eccentricity=ecc)
            
            # Esforços na face esquerda (Início do elemento)
            f_int = Ke @ ue - fe
            
            # Convenção estrutural: V positivo = para cima na face esquerda
            # M positivo = tração nas fibras inferiores
            # T positivo = momento torsor
            V_res[e] = f_int[0]
            M_res[e] = -f_int[1]
            T_res[e] = -f_int[2] # Momento Torsor no início do elemento

        # Reações de apoio
        reactions = {}
        for sup in self.model.supports:
            node = int(np.clip(np.round(sup.x / self.Le), 0, self.n_nodes - 1))
            dof_w, dof_t, dof_p = 3*node, 3*node+1, 3*node+2
            
            Rv, Rm, Rt = 0.0, 0.0, 0.0
            penalty = 1e16
            
            if sup.type in ('pinned', 'roller', 'fixed'):
                Rv = penalty * (0 - U[dof_w])
            if sup.type == 'fixed':
                Rm = penalty * (0 - U[dof_t])
                Rt = penalty * (0 - U[dof_p])
            if sup.type == 'spring':
                Rv = sup.k_vertical * U[dof_w]
            
            reactions[node] = {'R': round(float(Rv)/1000.0, 2), 'M': round(float(Rm)/1000.0, 2), 'T': round(float(Rt)/1000.0, 2)}

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
            max_torsion_kNm=max_torsion/1000.0
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
    def design_flexure(M_sd_kNm: float, section: BeamSection, N_sd_kN: float = 0.0, gamma_c: float = 1.4, gamma_s: float = 1.15) -> dict:
        """
        Dimensionamento a flexão simples ou composta (NBR 6118).
        Inclui excentricidade mínima se N_sd for compressão.
        """
        bw, bf, d, h = section.b, section.bf, section.d, section.h
        fcd_Pa, fyd_Pa = (section.fck / gamma_c) * 1e6, (section.fyk / gamma_s) * 1e6
        
        # 1. Excentricidade Mínima (NBR 6118 §11.3.3.4.1)
        e_min = 0.015 + 0.03 * h
        M_sd = abs(M_sd_kNm)
        if N_sd_kN > 0: # Compressão
            M_sd += abs(N_sd_kN) * e_min
            
        M_sd_Pa = M_sd * 1000.0
        bw_eff = bf if (M_sd_kNm > 0 and bf > bw) else bw
        
        k = M_sd_Pa / (bw_eff * d**2 * fcd_Pa) if (bw_eff * d**2 * fcd_Pa) > 0 else 0
        discriminant = 1.0 - 2.94 * k
        if discriminant < 0: return {'status': 'SEÇÃO_INSUFICIENTE', 'As_cm2': 0, 'x_over_d': 1.0, 'domain': '4'}
        
        x_d = (1.0 - np.sqrt(discriminant)) / 0.8
        As_m2 = (M_sd_Pa / (fyd_Pa * d * (1.0 - 0.4 * x_d)))
        
        # Ajuste para força axial (N_sd > 0 é compressão, subtrai As; N_sd < 0 é tração, soma As)
        As_m2 -= (N_sd_kN * 1000.0) / fyd_Pa
        
        As_cm2 = As_m2 * 1e4
        As_min = max(0.15/100.0, 0.04 * (section.fck/gamma_c)/(section.fyk/gamma_s)) * bw * d * 1e4
        As_final = max(As_cm2, As_min)
        
        return {
            'As_cm2': round(float(As_final), 2),
            'As_min_cm2': round(As_min, 2),
            'x_over_d': round(x_d, 4),
            'domain': '2' if x_d <= 0.259 else ('3' if x_d <= 0.45 else '4'),
            'M_sd_total_kNm': round(M_sd, 2)
        }

    @staticmethod
    def design_crack_width(M_sk_kNm: float, As_cm2: float, section: BeamSection) -> float:
        if As_cm2 <= 0: return 0.0
        sigma_s = (abs(M_sk_kNm) * 1000.0) / (As_cm2 * 1e-4 * 0.8 * section.d) / 1e6 
        wk = (12.5 / 12.5) * (sigma_s / 210000.0) * (3 * sigma_s / (0.3 * section.fck**(2/3)))
        return round(float(wk), 3)

    @staticmethod
    def design_shear_torsion(V_sd_kN: float, T_sd_kNm: float, section: BeamSection, gamma_c: float = 1.4) -> dict:
        b, h, d, fck = section.b, section.h, section.d, section.fck
        fcd = fck / gamma_c
        V_sd = abs(V_sd_kN)
        T_sd = abs(T_sd_kNm)
        
        # 1. Parâmetros da Seção Vazada Equivalente (NBR 6118 §17.5)
        u = 2 * (b + h)
        A = b * h
        he = max(A / u, 2 * section.cover) # espessura da parede
        Ae = (b - he) * (h - he)
        ue = 2 * ((b - he) + (h - he))
        
        # 2. Verificação de Esmagamento (Diagonais de Concreto)
        Vrd2 = 0.27 * (1.0 - fck/250.0) * fcd * b * d * 1000.0
        Trd2 = 0.50 * (1.0 - fck/250.0) * fcd * Ae * he * 1000.0 * 2 # Simplificado para theta=45
        
        check_diagonal = (V_sd / Vrd2) + (T_sd / Trd2)
        
        # 3. Armadura Transversal (Estribos)
        Vc = 0.6 * (0.15 * (fck**(2/3))/gamma_c) * b * d * 1000.0
        Vsw = max(V_sd - Vc, 0.0)
        Asw_v = (Vsw * 1000.0 / (0.9 * d * min(section.fyk/gamma_c, 435.0))) * 1e-2 # cm2/m
        
        # Torção: Asw,t / s = Tsd / (2 * Ae * fyd)
        fyd = min(section.fyk/1.15, 435.0)
        Asw_t = (T_sd * 1000.0 / (2 * Ae * fyd)) * 1e-2 # cm2/m (por ramo)
        
        # Asw_total = Asw_v/2 + Asw_t (para estribos de 2 ramos)
        Asw_final = (Asw_v/2.0 + Asw_t) * 2.0 # cm2/m (total)
        
        # Taxa mínima
        Asw_min = 0.2 * (fck**0.5) / section.fyk * b * 1e4
        Asw_final = max(Asw_final, Asw_min)
        
        # 4. Armadura Longitudinal de Torção
        Asl_t = (T_sd * 1000.0 * ue / (2 * Ae * fyd)) * 1e-4 # m2 -> cm2
        
        return {
            'Vsd_kN': round(V_sd, 2), 'Tsd_kNm': round(T_sd, 2),
            'Vrd2_kN': round(Vrd2, 2), 'Trd2_kNm': round(Trd2, 2),
            'interaction_diag': round(check_diagonal, 3),
            'Asw_cm2_m': round(Asw_final, 2),
            'Asl_torsion_cm2': round(Asl_t * 1e4, 2),
            'stirrup_spec': _suggest_stirrup(Asw_final, b),
            'biela_status': 'OK' if check_diagonal <= 1.0 else 'ESMAGAMENTO'
        }

    @staticmethod
    def design_anchorage(phi_mm: float, section: BeamSection, gamma_c: float = 1.4, gamma_s: float = 1.15) -> dict:
        """Calcula comprimento de ancoragem básica lb (NBR 6118)."""
        fck = section.fck
        fctd = 0.7 * 0.3 * (fck**(2/3)) / gamma_c
        fbd = 2.25 * 1.0 * fctd 
        fyd = section.fyk / gamma_s
        lb = (phi_mm / 4000.0) * (fyd / fbd)
        return {'phi_mm': phi_mm, 'lb_m': round(lb, 3), 'lb_cm': round(lb * 100, 1)}

    @staticmethod
    def check_vibration(L: float, EI: float, mass_kg_m: float) -> dict:
        if L <= 0 or mass_kg_m <= 0: return {'f1_hz': 0}
        f1 = (np.pi / (2 * L**2)) * np.sqrt(EI / mass_kg_m)
        return {'f1_hz': round(float(f1), 2), 'status': 'CONFORTO_OK' if f1 >= 4.0 else 'REVISAR_VIBRAÇÃO'}

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
        M_max_pos, M_max_neg = np.max(M_design)/1000.0*model.gamma_f, np.min(M_design)/1000.0*model.gamma_f
        V_max = np.max(np.abs(result.V))/1000.0*model.gamma_f
        T_max = np.max(np.abs(result.T))/1000.0*model.gamma_f
        
        flex_bottom = cls.design_flexure(M_max_pos, model.section)
        flex_top = cls.design_flexure(abs(M_max_neg), model.section)
        shear = cls.design_shear_torsion(V_max, T_max, model.section)
        wk = cls.design_crack_width(np.max(np.abs(result.M))/1000.0, max(flex_bottom['As_cm2'], flex_top['As_cm2']), model.section)
        
        mass_pp = model.section.area * 2500.0 
        vibration = cls.check_vibration(model.L, model.section.EI, mass_pp)
        anchorage = cls.design_anchorage(12.5, model.section)
        
        support_xs = sorted([s.x for s in model.supports])
        spans = [support_xs[i+1] - support_xs[i] for i in range(len(support_xs)-1)] if len(support_xs) > 1 else [model.L]
        limite_visual = max(spans) * 1000.0 / 250.0
        
        reasons = []
        if flex_bottom['domain'] == '4': reasons.append("Domínio 4 na armadura inferior (seção super-armada ou x/d > 0.45)")
        if flex_top['domain'] == '4': reasons.append("Domínio 4 na armadura superior")
        if shear['biela_status'] != 'OK': reasons.append("Esmagamento da biela de compressão (Vsd > Vrd2)")
        if wk > model.wk_limit_mm: reasons.append(f"Abertura de fissura (wk={wk:.3f}mm) excede o limite (wlim={model.wk_limit_mm}mm)")
        if vibration['f1_hz'] < 4.0: reasons.append(f"Frequência natural ({vibration['f1_hz']}Hz) abaixo do limite de conforto (4Hz)")
        if result.max_deflection_mm > limite_visual: reasons.append(f"Flecha excessiva ({result.max_deflection_mm:.1f}mm > {limite_visual:.1f}mm)")

        return {
            'flexure_bottom': flex_bottom, 'flexure_top': flex_top, 'shear': shear,
            'crack_width': {'wk_mm': wk, 'limit_mm': model.wk_limit_mm},
            'deflection': {'max_mm': result.max_deflection_mm, 'limit_mm': round(limite_visual, 2), 
                           'status': 'OK' if result.max_deflection_mm <= limite_visual else 'EXCEDE'},
            'vibration': vibration, 'anchorage': anchorage,
            'M_max_pos_kNm': round(M_max_pos, 2), 'M_max_neg_kNm': round(M_max_neg, 2),
            'overall_status': 'ATENDE' if len(reasons) == 0 else 'REVISAR',
            'reasons': reasons
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
                    'R': data.get('V_kN', 0.0) * 1000.0, 
                    'M': -data.get('M_kNm', 0.0) * 1000.0
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
            'reactions': [{'x': r['x'], 'R': r['R']/1000.0} for r in internal_reactions],
            'supports_debug': str([f"x={s.x}" for s in sups])
        }


def _durability_params(caa: int, member_type: str) -> dict:
    from durability_checker import DurabilityChecker, DurabilityConfig
    caa_int = int(max(1, min(4, caa)))
    cover_mm = DurabilityChecker.get_min_cover(DurabilityConfig(caa=caa_int), member_type)
    wk_limits = {1: 0.4, 2: 0.3, 3: 0.2, 4: 0.2}
    return {'caa': caa_int, 'cover_m': cover_mm / 1000.0, 'cover_mm': cover_mm, 'wk_limit_mm': wk_limits[caa_int]}


def run_beam_analysis(L, supports, distributed_loads=None, point_loads=None, b=0.20, h=0.50, fck=30.0, bf=0.0, hf=0.0, n_elements=40, nonlinear=True, redistribution_delta=0.90, caa=2, cover=None, include_self_weight=True, gamma_f=1.4):
    durability = _durability_params(caa, 'beam')
    cover_m = float(cover) if cover is not None else durability['cover_m']
    section = BeamSection(b=b, h=h, fck=fck, bf=bf, hf=hf, cover=cover_m)
    model = BeamModel(L=L, section=section, supports=[BeamSupport(**s) for s in supports],
                      distributed_loads=[DistributedLoad(**dl) for dl in (distributed_loads or [])],
                      point_loads=[PointLoad(**pl) for pl in (point_loads or [])], n_elements=n_elements,
                      caa=durability['caa'], wk_limit_mm=durability['wk_limit_mm'],
                      include_self_weight=include_self_weight, gamma_f=gamma_f)
    solver = BeamFEMSolver(model)
    linear_result = solver.solve()
    result = NonlinearBeamEngine.solve_iterative(solver) if nonlinear else linear_result
    design = BeamDesigner.full_design(result, model, redistribution_delta=redistribution_delta)
    design['durability'] = {
        'caa': durability['caa'],
        'cover_required_mm': durability['cover_mm'],
        'cover_mm': round(cover_m * 1000, 1),
        'cover_ok': cover_m * 1000.0 >= durability['cover_mm'],
    }
    classical_res = ClassicalBeamSolver.generate_diagrams(model, fea_reactions=linear_result.reactions)
    return {
        'id': 'beam_1',
        'L': model.L,
        'summary': {'L_m': L, 'b_m': b, 'h_m': h, 'bf_m': section.bf, 'max_deflection_mm': result.max_deflection_mm,
                    'analysis_type': 'FISICA_NAO_LINEAR' if nonlinear else 'ELASTICA_LINEAR', 'fck_MPa': fck,
                    'caa': durability['caa'], 'cover_mm': round(cover_m * 1000, 1)},
        'design': design, 'reactions': result.reactions,
        'diagrams': {'x_m': result.x_elem.tolist(), 'V_kN': (result.V/1000.0).tolist(), 'M_kNm': (result.M/1000.0).tolist(),
                     'x_nodes_m': result.x.tolist(), 'w_mm': (result.w*1000.0).tolist()},
        'classical_diagrams': classical_res,
        'classical_reactions': classical_res.get('reactions', []),
        'debug_info': {
            'x1': classical_res.get('reactions', [{}])[0].get('x') if len(classical_res.get('reactions', [])) > 0 else None,
            'x2': classical_res.get('reactions', [{}, {}])[1].get('x') if len(classical_res.get('reactions', [])) > 1 else None,
            'L_total': model.L,
            'n_supports': len(model.supports)
        }
    }
