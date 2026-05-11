"""
radier_solver_v2.py
Solver simplificado de placa de Mindlin-Reissner sobre solo de Winkler.

Convenção adotada:
- deslocamento vertical w positivo para baixo
- cargas q e p positivas para baixo
- pressão do solo qsoil positiva em compressão (reação escalar do solo)

Melhorias da 2ª rodada:
- distribuição bilinear de cargas concentradas de pilares para os 4 nós do painel
- diagnóstico de equilíbrio com decomposição por carga distribuída e por pilares
- cálculo explícito de razão residual relativa
- exportação nodal com contribuição de carga concentrada equivalente por nó
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class Material:
    E: float = 32e9
    nu: float = 0.20
    h: float = 0.60


@dataclass
class Soil:
    kv: float = 40e6
    tensionless: bool = True
    q_limit: Optional[float] = None  # Pressão limite elasto-plástica (Pa)
    kv_map: Optional[np.ndarray] = None  # Rigidez variável por nó (mesmo tamanho de nodes)


@dataclass
class AreaLoad:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    q_Pa: float


@dataclass
class PlateModel:
    Lx: float = 24.0
    Ly: float = 24.0
    nx: int = 13
    ny: int = 13
    material: Material = field(default_factory=Material)
    soil: Soil = field(default_factory=Soil)
    supports: Optional[list[dict]] = None # [{'x': 1.0, 'y': 2.0, 'kz': 1e12, 'krx': 1e12, 'kry': 1e12}]
    area_loads: Optional[list[AreaLoad]] = None

    def validate(self) -> None:
        if self.Lx <= 0 or self.Ly <= 0:
            raise ValueError('Lx e Ly devem ser positivos.')
        if self.nx < 2 or self.ny < 2:
            raise ValueError('nx e ny devem ser >= 2.')
        if self.material.E <= 0 or self.material.h <= 0:
            raise ValueError('E e h devem ser positivos.')
        if not (0.0 < self.material.nu < 0.5):
            raise ValueError('nu deve estar entre 0 e 0.5.')
        if not self.supports and self.soil.kv <= 0:
            raise ValueError('kv deve ser positivo se nao houver apoios discretos.')


@dataclass
class SolverResult:
    nodes: np.ndarray
    elements: np.ndarray
    disp: np.ndarray
    qsoil: np.ndarray
    mx: np.ndarray
    my: np.ndarray
    mxy: np.ndarray
    tributary_areas: np.ndarray
    active_springs: np.ndarray
    nodal_column_loads: np.ndarray
    distributed_load_total: float
    column_load_total: float
    reactions_total: float
    loads_total: float
    residual: float
    residual_ratio: float
    iterations: int
    pile_reactions: Optional[np.ndarray] = None # Reações individuais em cada estaca
    pile_reactions_total: float = 0.0


def read_column_loads_csv(path: str | Path) -> np.ndarray:
    df = pd.read_csv(path)
    required = {'x', 'y', 'p'}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f'CSV de pilares sem colunas obrigatórias: {sorted(missing)}')
    
    cols = ['x', 'y', 'p']
    if 'mx' in df.columns: cols.append('mx')
    if 'my' in df.columns: cols.append('my')
    
    return df[cols].to_numpy(dtype=float)


class RadierMindlinWinklerV2:
    def __init__(self, model: PlateModel):
        self.model = model
        self.model.validate()
        self._build_mesh()
        self._last_nodal_column_loads = np.zeros(len(self.nodes), dtype=float)
        self._last_distributed_load_total = 0.0
        self._last_column_load_total = 0.0

    def _build_mesh(self) -> None:
        m = self.model
        xs = np.linspace(0.0, m.Lx, m.nx)
        ys = np.linspace(0.0, m.Ly, m.ny)
        Xg, Yg = np.meshgrid(xs, ys)
        self.nodes = np.column_stack([Xg.ravel(), Yg.ravel()])
        self.xs = xs
        self.ys = ys
        elems = []
        for j in range(m.ny - 1):
            for i in range(m.nx - 1):
                n0 = j * m.nx + i
                n1 = n0 + 1
                n2 = n0 + m.nx + 1
                n3 = n0 + m.nx
                elems.append([n0, n1, n2, n3])
        self.elements = np.array(elems, dtype=int)
        self._tributary_areas = self._compute_tributary_areas()

    def _compute_tributary_areas(self) -> np.ndarray:
        m = self.model
        dx = m.Lx / (m.nx - 1)
        dy = m.Ly / (m.ny - 1)
        wx = np.ones(m.nx)
        wy = np.ones(m.ny)
        wx[[0, -1]] = 0.5
        wy[[0, -1]] = 0.5
        return (np.outer(wy, wx) * dx * dy).ravel()

    def _find_cell_and_shape_weights(self, x: float, y: float):
        x = float(np.clip(x, self.xs.min(), self.xs.max()))
        y = float(np.clip(y, self.ys.min(), self.ys.max()))
        ix = int(np.clip(np.searchsorted(self.xs, x, side='right') - 1, 0, len(self.xs) - 2))
        iy = int(np.clip(np.searchsorted(self.ys, y, side='right') - 1, 0, len(self.ys) - 2))
        x1, x2 = self.xs[ix], self.xs[ix + 1]
        y1, y2 = self.ys[iy], self.ys[iy + 1]
        tx = 0.0 if x2 == x1 else (x - x1) / (x2 - x1)
        ty = 0.0 if y2 == y1 else (y - y1) / (y2 - y1)
        n0 = iy * self.model.nx + ix
        n1 = n0 + 1
        n2 = n0 + self.model.nx + 1
        n3 = n0 + self.model.nx
        nodes = np.array([n0, n1, n2, n3], dtype=int)
        weights = np.array([(1-tx)*(1-ty), tx*(1-ty), tx*ty, (1-tx)*ty], dtype=float)
        weights /= weights.sum()
        return nodes, weights

    def _element_stiffness(self, coords: np.ndarray, stiffness_factor: float = 1.0, h: Optional[float] = None) -> np.ndarray:
        m = self.model.material
        h = h if h is not None else m.h
        E, nu = m.E, m.nu
        D = (E * h**3 / (12.0 * (1.0 - nu**2))) * stiffness_factor
        G = E / (2.0 * (1.0 + nu))
        ks = 5.0 / 6.0
        Ds = (ks * G * h) * stiffness_factor
        Db = np.array([
            [D, D * nu, 0.0],
            [D * nu, D, 0.0],
            [0.0, 0.0, D * (1.0 - nu) / 2.0]
        ])
        gp = 1.0 / np.sqrt(3.0)
        gauss = [(-gp, -gp), (gp, -gp), (gp, gp), (-gp, gp)]
        Ke = np.zeros((12, 12))

        def shape(xi: float, eta: float) -> Tuple[np.ndarray, np.ndarray]:
            N = 0.25 * np.array([
                (1-xi)*(1-eta),
                (1+xi)*(1-eta),
                (1+xi)*(1+eta),
                (1-xi)*(1+eta)
            ])
            dNdxi = 0.25 * np.array([
                [-(1-eta), -(1-xi)],
                [ (1-eta), -(1+xi)],
                [ (1+eta),  (1+xi)],
                [-(1+eta),  (1-xi)],
            ])
            return N, dNdxi

        for xi, eta in gauss:
            N, dNdxi = shape(xi, eta)
            J = dNdxi.T @ coords
            detJ = np.linalg.det(J)
            if detJ <= 0:
                raise ValueError('Elemento com Jacobiano não positivo.')
            dNdxy = dNdxi @ np.linalg.inv(J)
            Bb = np.zeros((3, 12))
            Bs = np.zeros((2, 12))
            for i in range(4):
                Bb[0, 3*i+1] = dNdxy[i, 0]
                Bb[1, 3*i+2] = dNdxy[i, 1]
                Bb[2, 3*i+1] = dNdxy[i, 1]
                Bb[2, 3*i+2] = dNdxy[i, 0]

                Bs[0, 3*i] = dNdxy[i, 0]
                Bs[0, 3*i+1] = -N[i]
                Bs[1, 3*i] = dNdxy[i, 1]
                Bs[1, 3*i+2] = -N[i]
            Ke += detJ * (Bb.T @ Db @ Bb + Ds * (Bs.T @ Bs))
        return Ke

    def _assemble_global_nonlinear(
        self, 
        column_loads: Optional[np.ndarray] = None, 
        kv_nodal: Optional[np.ndarray] = None, 
        active_springs: Optional[np.ndarray] = None, 
        piles: Optional[list] = None,
        stiffness_factors: Optional[np.ndarray] = None,
        superstructure_stiffness: Optional[dict] = None,
        h_per_element: Optional[np.ndarray] = None,
        opening_mask: Optional[np.ndarray] = None
    ):
        from scipy.sparse import coo_matrix
        n_nodes = len(self.nodes)
        ndof = 3 * n_nodes
        m = self.model
        
        row_idx = []
        col_idx = []
        data_val = []
        F = np.zeros(ndof)
        nodal_column_loads = np.zeros(n_nodes, dtype=float)

        if stiffness_factors is None:
            stiffness_factors = np.ones(len(self.elements))

        # Identificar nós ativos
        active_node_mask = np.zeros(n_nodes, dtype=bool)
        if opening_mask is not None:
            for ie, el in enumerate(self.elements):
                if not opening_mask[ie]:
                    active_node_mask[el] = True
        else:
            active_node_mask[:] = True
        self._active_node_mask = active_node_mask

        for ie, el in enumerate(self.elements):
            if opening_mask is not None and opening_mask[ie]:
                continue
                
            coords = self.nodes[el, :]
            h_el = h_per_element[ie] if h_per_element is not None else m.material.h
            Ke = self._element_stiffness(coords, stiffness_factor=stiffness_factors[ie], h=h_el)
            dofs = np.array([3*n + d for n in el for d in range(3)])
            
            # Coletar dados para matriz esparsa
            for i_local in range(12):
                for j_local in range(12):
                    row_idx.append(dofs[i_local])
                    col_idx.append(dofs[j_local])
                    data_val.append(Ke[i_local, j_local])

        if active_springs is None:
            active_springs = np.ones(n_nodes, dtype=bool)
        
        kv_eff = kv_nodal if kv_nodal is not None else (m.soil.kv_map if m.soil.kv_map is not None else np.full(n_nodes, m.soil.kv))

        for i in range(n_nodes):
            if not self._active_node_mask[i]:
                # Nó fantasma
                for d in range(3):
                    row_idx.append(3*i+d)
                    col_idx.append(3*i+d)
                    data_val.append(1e12)
            elif active_springs[i]:
                row_idx.append(3*i)
                col_idx.append(3*i)
                data_val.append(kv_eff[i] * self._tributary_areas[i])

        # Adicionar rigidez das estacas
        if piles:
            for p in piles:
                nodes4, weights4 = self._find_cell_and_shape_weights(p.x, p.y)
                k_pile = getattr(p, 'stiffness_kN_m', 0.0) * 1000.0
                for n, w in zip(nodes4, weights4):
                    row_idx.append(3*n)
                    col_idx.append(3*n)
                    data_val.append(k_pile * (w**2))

        # Adicionar apoios discretos
        if m.supports:
            for sup in m.supports:
                nodes4, weights4 = self._find_cell_and_shape_weights(sup['x'], sup['y'])
                kz = sup.get('kz', 1e15)
                krx = sup.get('krx', 0.0)
                kry = sup.get('kry', 0.0)
                for n, w in zip(nodes4, weights4):
                    row_idx.append(3*n)
                    col_idx.append(3*n)
                    data_val.append(kz * (w**2))
                    if krx > 0:
                        row_idx.append(3*n+1)
                        col_idx.append(3*n+1)
                        data_val.append(krx * (w**2))
                    if kry > 0:
                        row_idx.append(3*n+2)
                        col_idx.append(3*n+2)
                        data_val.append(kry * (w**2))

        # Criar matriz esparsa inicial
        K = coo_matrix((data_val, (row_idx, col_idx)), shape=(ndof, ndof)).tocsr()

        # Rigidez da superestrutura
        if superstructure_stiffness:
            from ssi_advanced import apply_superstructure_stiffness
            column_nodes = []
            if column_loads is not None:
                for row in np.asarray(column_loads, dtype=float):
                    n4, _ = self._find_cell_and_shape_weights(row[0], row[1])
                    column_nodes.extend(n4.tolist())
            column_nodes = list(set(column_nodes))
            params = superstructure_stiffness.get('params')
            K = apply_superstructure_stiffness(K, column_nodes, params)

        q = float(getattr(self, '_q_uniform', 0.0))
        distributed_load_total = 0.0

        for i, el in enumerate(self.elements):
            if opening_mask is not None and opening_mask[i]:
                continue
            coords = self.nodes[el, :]
            a_el = (coords[:, 0].max() - coords[:, 0].min()) * (coords[:, 1].max() - coords[:, 1].min())
            fe = q * a_el / 4.0
            distributed_load_total += q * a_el
            for n in el:
                F[3*n] += fe

        # Adicionar Cargas de Área Adicionais
        if m.area_loads:
            for al in m.area_loads:
                for i, el in enumerate(self.elements):
                    if opening_mask is not None and opening_mask[i]:
                        continue
                    coords = self.nodes[el, :]
                    ex_min, ey_min = coords.min(axis=0)
                    ex_max, ey_max = coords.max(axis=0)
                    
                    # Verificar se o elemento está (mesmo que parcialmente) dentro da área
                    # Para simplificar: se o centro do elemento está dentro
                    ecx, ecy = (ex_min + ex_max)/2, (ey_min + ey_max)/2
                    if al.x_min <= ecx <= al.x_max and al.y_min <= ecy <= al.y_max:
                        a_el = (ex_max - ex_min) * (ey_max - ey_min)
                        fe = al.q_Pa * a_el / 4.0
                        distributed_load_total += al.q_Pa * a_el
                        for n in el:
                            F[3*n] += fe

        column_load_total = 0.0
        if column_loads is not None:
            for row in np.asarray(column_loads, dtype=float):
                x, y, p = row[0], row[1], row[2]
                mx = row[3] if len(row) > 3 else 0.0
                my = row[4] if len(row) > 4 else 0.0
                
                nodes4, weights4 = self._find_cell_and_shape_weights(x, y)
                for node, w in zip(nodes4, weights4):
                    v_load = float(p) * float(w)
                    F[3*node] += v_load
                    nodal_column_loads[node] += v_load
                    F[3*node + 1] += float(mx) * float(w)
                    F[3*node + 2] += float(my) * float(w)
                column_load_total += float(p)

        self._last_nodal_column_loads = nodal_column_loads
        self._last_distributed_load_total = float(distributed_load_total)
        self._last_column_load_total = float(column_load_total)
        return K, F

    def _solve_linear_system(self, K, F: np.ndarray) -> np.ndarray:
        from scipy.sparse.linalg import spsolve
        from scipy.sparse import eye
        ndof = len(F)
        # Regularização esparsa mínima para estabilidade numérica
        reg = 1e-9
        K_reg = K + eye(ndof, format='csr') * reg
        return spsolve(K_reg, F)

    def solve(
        self,
        column_loads: Optional[np.ndarray] = None,
        piles: Optional[list] = None,
        max_iter: int = 30,
        tol_active: int = 0,
        concrete_nonlinear: bool = False,
        superstructure_stiffness: Optional[dict] = None,
        stiffness_factors: Optional[np.ndarray] = None,
        h_per_element: Optional[np.ndarray] = None,
        opening_mask: Optional[np.ndarray] = None
    ) -> SolverResult:
        n_nodes = len(self.nodes)
        active = np.ones(n_nodes, dtype=bool)
        # Rigidez efetiva inicial
        kv_base = self.model.soil.kv_map if self.model.soil.kv_map is not None else np.full(n_nodes, self.model.soil.kv)
        kv_iter = kv_base.copy()
        q_limit = self.model.soil.q_limit
        
        if stiffness_factors is None:
            stiffness_factors = np.ones(len(self.elements))

        for it in range(1, max_iter + 1):
            iterations = it
            K, F = self._assemble_global_nonlinear(
                column_loads=column_loads, 
                kv_nodal=kv_iter, 
                active_springs=active, 
                piles=piles,
                stiffness_factors=stiffness_factors,
                superstructure_stiffness=superstructure_stiffness,
                h_per_element=h_per_element,
                opening_mask=opening_mask
            )
            U = self._solve_linear_system(K, F)
            f_norm = np.linalg.norm(F)
            u_norm = np.linalg.norm(U)
            # print(f"DEBUG: iteration {it}, |F|={f_norm:.2e}, |U|={u_norm:.2e}")
            disp = U.reshape(-1, 3)
            
            # 1. Atualizar Active (Tensionless)
            if self.model.soil.tensionless:
                new_active = disp[:, 0] > 1e-9
                if new_active.sum() == 0: new_active[:] = True
            else:
                new_active = active.copy()
            
            # 2. Atualizar Rigidez (Elasto-Plástico) com amortecimento (damping)
            new_kv = kv_base.copy()
            if q_limit is not None:
                # Se p = kv * w > q_limit -> kv_eff = q_limit / w
                pressures = kv_base * disp[:, 0]
                plastic_mask = (pressures > q_limit) & new_active
                new_kv[plastic_mask] = q_limit / np.maximum(disp[plastic_mask, 0], 1e-6)

            # Amortecimento para evitar oscilação
            alpha = 0.5
            kv_iter = alpha * new_kv + (1 - alpha) * kv_iter
            
            # Verificar convergência (mudança no vetor de deslocamento)
            if it > 1:
                diff = np.linalg.norm(disp[:, 0] - prev_disp_w) / max(np.linalg.norm(disp[:, 0]), 1e-9)
                if diff < 1e-4:
                    break
            
            prev_disp_w = disp[:, 0].copy()
            active = new_active
            # kv_iter já foi atualizado com alpha acima

            # 3. Atualizar Rigidez do Concreto (Não-Linearidade Física)
            if concrete_nonlinear:
                # Precisamos dos momentos para Branson
                res_temp = self._extract_moments(disp)
                # M_eq = sqrt(Mx^2 + My^2 + Mxy^2) ou Wood-Armer
                m_max_el = np.sqrt(res_temp['mx']**2 + res_temp['my']**2 + res_temp['mxy']**2)
                
                from concrete_nonlinear import ConcreteNonlinearEngine
                new_factors = ConcreteNonlinearEngine.compute_stiffness_reduction(m_max_el, self.model)
                # Amortecimento para estabilidade
                stiffness_factors = 0.5 * new_factors + 0.5 * stiffness_factors

        # Recupera as pressões de contato finais usando a rigidez convergida
        qsoil = np.where(active, np.maximum(disp[:, 0] * kv_iter, 0.0), 0.0)

        # Cálculo final dos momentos considerando a rigidez convergida
        final_moments = self._extract_moments(disp, stiffness_factors=stiffness_factors)
        mx_el, my_el, mxy_el = final_moments['mx'], final_moments['my'], final_moments['mxy']

        # Cálculo das reações nas estacas
        pile_reactions = np.zeros(len(piles)) if piles else None
        pile_reactions_total = 0.0
        if piles:
            for ip, p in enumerate(piles):
                nodes4, weights4 = self._find_cell_and_shape_weights(p.x, p.y)
                w_pile = np.sum(disp[nodes4, 0] * weights4)
                k_pile = getattr(p, 'stiffness_kN_m', 0.0) * 1000.0
                r_pile = w_pile * k_pile
                pile_reactions[ip] = r_pile
                pile_reactions_total += r_pile

        reactions_total = float(np.sum(qsoil * self._tributary_areas)) + pile_reactions_total
        
        # Somar reações de apoios discretos (pilares rígidos)
        if self.model.supports:
            for sup in self.model.supports:
                nodes4, weights4 = self._find_cell_and_shape_weights(sup['x'], sup['y'])
                kz = sup.get('kz', 1e15)
                # Reação total no apoio = k * w_ponderado
                w_sup = np.sum(disp[nodes4, 0] * weights4)
                reactions_total += w_sup * kz
        loads_total = float(np.sum(F[::3]))
        residual = float(reactions_total - loads_total)
        residual_ratio = float(abs(residual) / max(abs(loads_total), 1.0))

        return SolverResult(
            nodes=self.nodes,
            elements=self.elements,
            disp=disp,
            qsoil=qsoil,
            mx=mx_el,
            my=my_el,
            mxy=mxy_el,
            tributary_areas=self._tributary_areas.copy(),
            active_springs=active.copy(),
            nodal_column_loads=self._last_nodal_column_loads.copy(),
            distributed_load_total=float(self._last_distributed_load_total),
            column_load_total=float(self._last_column_load_total),
            reactions_total=reactions_total,
            loads_total=loads_total,
            residual=residual,
            residual_ratio=residual_ratio,
            iterations=iterations,
            pile_reactions_total=pile_reactions_total,
            pile_reactions=pile_reactions
        )

    def _extract_moments(self, disp: np.ndarray, stiffness_factors: Optional[np.ndarray] = None) -> dict:
        E, nu, h = self.model.material.E, self.model.material.nu, self.model.material.h
        D_base = E * h**3 / (12.0 * (1.0 - nu**2))
        Db_base = np.array([
            [D_base, D_base * nu, 0.0],
            [D_base * nu, D_base, 0.0],
            [0.0, 0.0, D_base * (1.0 - nu) / 2.0]
        ])

        n_elems = len(self.elements)
        mx_el = np.zeros(n_elems)
        my_el = np.zeros(n_elems)
        mxy_el = np.zeros(n_elems)
        
        dNdxi_c = 0.25 * np.array([
            [-1.0, -1.0], [ 1.0, -1.0], [ 1.0,  1.0], [-1.0,  1.0]
        ])

        for ie, el in enumerate(self.elements):
            factor = stiffness_factors[ie] if stiffness_factors is not None else 1.0
            Db = Db_base * factor
            coords = self.nodes[el, :]
            dNdxy = dNdxi_c @ np.linalg.inv(dNdxi_c.T @ coords)
            u_el = disp[el, :]
            kappa = np.zeros(3)
            for i in range(4):
                # theta_x = u_el[i, 1], theta_y = u_el[i, 2]
                kappa[0] += dNdxy[i, 0] * u_el[i, 1]
                kappa[1] += dNdxy[i, 1] * u_el[i, 2]
                kappa[2] += dNdxy[i, 1] * u_el[i, 1] + dNdxy[i, 0] * u_el[i, 2]
            # Momento M = Db * kappa
            M = Db @ kappa
            mx_el[ie], my_el[ie], mxy_el[ie] = M
            
        return {'mx': mx_el, 'my': my_el, 'mxy': mxy_el}

    def export_element_results_csv(self, result: SolverResult, path: str) -> str:
        rows = []
        for ie, el in enumerate(self.elements):
            rows.append({
                'elem': ie,
                'xc_m': float(self.nodes[el, 0].mean()),
                'yc_m': float(self.nodes[el, 1].mean()),
                'mx_Nm_per_m': float(result.mx[ie]),
                'my_Nm_per_m': float(result.my[ie]),
                'mxy_Nm_per_m': float(result.mxy[ie]),
                'qsoil_mean_Pa': float(result.qsoil[el].mean()),
                'w_mean_m': float(result.disp[el, 0].mean()),
            })
        df = pd.DataFrame(rows)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return str(path)

    def export_nodal_results_csv(self, result: SolverResult, path: str) -> str:
        df = pd.DataFrame({
            'node': np.arange(len(result.nodes)),
            'x_m': result.nodes[:, 0],
            'y_m': result.nodes[:, 1],
            'w_m': result.disp[:, 0],
            'thx_rad': result.disp[:, 1],
            'thy_rad': result.disp[:, 2],
            'qsoil_Pa': result.qsoil,
            'area_m2': result.tributary_areas,
            'spring_active': result.active_springs.astype(int),
            'column_load_N': result.nodal_column_loads,
        })
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return str(path)


def write_example_column_csv(path: str | Path) -> None:
    rows = [
        {'id':'P01','x':4,'y':4,'p':2000e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P02','x':12,'y':4,'p':2500e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P03','x':20,'y':4,'p':2000e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P04','x':4,'y':12,'p':2500e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P05','x':12,'y':12,'p':3000e3,'bx':0.7,'by':0.7,'local':'interior'},
        {'id':'P06','x':20,'y':12,'p':2500e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P07','x':4,'y':20,'p':2000e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P08','x':12,'y':20,'p':2500e3,'bx':0.5,'by':0.5,'local':'interior'},
        {'id':'P09','x':20,'y':20,'p':2000e3,'bx':0.5,'by':0.5,'local':'interior'},
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)