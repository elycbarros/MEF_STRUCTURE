"""
radier_rs_adapter.py - Adapter que substitui a montagem da matriz de rigidez
do radier_solver_v2.py pela implementação Rust (structural_core_rs),
mantendo o loop não-linear em Python.

Uso:
  1. Importar RadierMindlinWinklerRS que tem a mesma interface que RadierMindlinWinklerV2
  2. O método solve() usa assemble_radier_system_py do Rust para gerar K e F
  3. A solução do sistema linear usa scipy.sparse.linalg.spsolve (já otimizado em C)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import numpy as np
import numpy.typing as npt
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

try:
    import structural_core_rs as _rs_core

    HAS_RUST = True
except ImportError:
    HAS_RUST = False


@dataclass
class Material:
    E: float = 32e9
    nu: float = 0.20
    h: float = 0.60


@dataclass
class Soil:
    kv: float = 40e6
    tensionless: bool = True
    q_limit: Optional[float] = None
    kv_map: Optional[np.ndarray] = None


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
    supports: Optional[list[dict]] = None
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
    converged: bool = True
    pile_reactions: Optional[np.ndarray] = None
    pile_reactions_total: float = 0.0


class RadierMindlinWinklerRS:
    """
    Versão do solver RadierMindlinWinkler que usa montagem da matriz
    de rigidez em Rust (structural_core_rs.assemble_radier_system_py).

    Mantém o loop não-linear (tensionless, elasto-plástico, Branson) em Python.
    """

    def __init__(self, model: PlateModel):
        if not HAS_RUST:
            raise ImportError(
                'structural_core_rs não está instalado. '
                'Execute: pip install mef_engine/structural_core_rs/target/wheels/*.whl'
            )
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

    def _assemble_via_rust(
        self,
        column_loads: Optional[npt.NDArray[np.float64]] = None,
        kv_nodal: Optional[npt.NDArray[np.float64]] = None,
        active_springs: Optional[npt.NDArray[np.bool_]] = None,
        piles: Optional[list] = None,
        stiffness_factors: Optional[npt.NDArray[np.float64]] = None,
        h_per_element: Optional[npt.NDArray[np.float64]] = None,
        opening_mask: Optional[npt.NDArray[np.bool_]] = None,
    ) -> Tuple[
        Any, npt.NDArray[np.float64], Tuple[npt.NDArray[np.int_], npt.NDArray[np.int_], npt.NDArray[np.float64]]
    ]:
        """
        Chama a montagem Rust.
        Retorna (K_csr, F, K_triplet, nodal_column_loads, distributed_load_total, column_load_total).
        K_triplet = (row, col, val) em formato Python list.
        """
        m = self.model

        # Preparar area loads
        al_xmin, al_ymin, al_xmax, al_ymax, al_q = [], [], [], [], []
        if m.area_loads:
            for al in m.area_loads:
                al_xmin.append(al.x_min)
                al_ymin.append(al.y_min)
                al_xmax.append(al.x_max)
                al_ymax.append(al.y_max)
                al_q.append(al.q_Pa)

        # Column loads flat: [x, y, p, mx, my] repetido
        col_flat = []
        if column_loads is not None:
            for row in np.asarray(column_loads, dtype=float):
                col_flat.extend([row[0], row[1], row[2]])
                col_flat.append(row[3] if len(row) > 3 else 0.0)
                col_flat.append(row[4] if len(row) > 4 else 0.0)

        # Apoios discretos
        supp_x, supp_y, supp_kz, supp_krx, supp_kry = [], [], [], [], []
        if m.supports:
            for sup in m.supports:
                supp_x.append(sup['x'])
                supp_y.append(sup['y'])
                supp_kz.append(sup.get('kz', 1e15))
                supp_krx.append(sup.get('krx', 0.0))
                supp_kry.append(sup.get('kry', 0.0))

        # Estacas
        pile_x, pile_y, pile_k = [], [], []
        if piles:
            for p in piles:
                pile_x.append(p.x)
                pile_y.append(p.y)
                pile_k.append(getattr(p, 'stiffness_kN_m', 0.0))

        # q uniforme
        q = float(getattr(self, '_q_uniform', 0.0))

        res = _rs_core.assemble_radier_system_py(
            nodes_xy=self.nodes.ravel().tolist(),
            elements=self.elements.ravel().tolist(),
            tributary_areas=self._tributary_areas.tolist(),
            xs=self.xs.tolist(),
            ys=self.ys.tolist(),
            nx=m.nx,
            stiffness_factors=(
                stiffness_factors if stiffness_factors is not None else np.ones(len(self.elements))
            ).tolist(),
            h_per_element=(h_per_element if h_per_element is not None else [m.material.h] * len(self.elements)),
            opening_mask=opening_mask.tolist() if opening_mask is not None else [],
            kv_nodal=(
                kv_nodal
                if kv_nodal is not None
                else (m.soil.kv_map if m.soil.kv_map is not None else np.full(len(self.nodes), m.soil.kv))
            ).tolist(),
            active_springs=(
                active_springs if active_springs is not None else np.ones(len(self.nodes), dtype=bool)
            ).tolist(),
            e=m.material.E,
            nu=m.material.nu,
            h_default=m.material.h,
            q_uniform=q,
            column_loads=col_flat,
            area_load_xmin=al_xmin,
            area_load_ymin=al_ymin,
            area_load_xmax=al_xmax,
            area_load_ymax=al_ymax,
            area_load_q=al_q,
            supp_x=supp_x,
            supp_y=supp_y,
            supp_kz=supp_kz,
            supp_krx=supp_krx,
            supp_kry=supp_kry,
            pile_x=pile_x,
            pile_y=pile_y,
            pile_k=pile_k,
            penalty=1e20,
        )

        row_arr = np.array(res['row'], dtype=np.int32)
        col_arr = np.array(res['col'], dtype=np.int32)
        val_arr = np.array(res['val'], dtype=float)
        F = np.array(res['rhs'], dtype=float)

        # Montar matriz CSR para quando for necessário modificar K (ex: superestrutura)
        K = coo_matrix((val_arr, (row_arr, col_arr)), shape=(3 * len(self.nodes), 3 * len(self.nodes))).tocsr()

        self._last_nodal_column_loads = np.array(res['nodal_column_loads'], dtype=float)
        self._last_distributed_load_total = float(res['distributed_load_total'])
        self._last_column_load_total = float(res['column_load_total'])
        self._last_F = F.copy()
        return K, F, (row_arr, col_arr, val_arr)

    def _solve_linear_system(
        self,
        K_triplet: Tuple[npt.NDArray[np.int_], npt.NDArray[np.int_], npt.NDArray[np.float64]],
        F: npt.NDArray[np.float64],
    ) -> npt.NDArray[np.float64]:
        """Resolve usando Rust (faer sparse LU)."""
        row, col, val = K_triplet
        u = _rs_core.solve_radier_sparse_py(
            row.tolist(),
            col.tolist(),
            val.tolist(),
            F.tolist(),
            1e-9,
        )
        return np.array(u, dtype=float)

    @staticmethod
    def _solve_linear_system_py(K: Any, F: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Fallback usando scipy (necessário quando K é modificado em Python, ex: superestrutura)."""
        from scipy.sparse import eye as speye

        ndof = len(F)
        K_reg = K + speye(ndof, format='csr') * 1e-9
        return spsolve(K_reg, F)

    def _extract_moments(
        self, disp: npt.NDArray[np.float64], stiffness_factors: Optional[npt.NDArray[np.float64]] = None
    ) -> Dict[str, npt.NDArray[np.float64]]:
        """Extrai momentos fletores nos centroids dos elementos (mantido em Python)."""
        E, nu, h = self.model.material.E, self.model.material.nu, self.model.material.h
        D_base = E * h**3 / (12.0 * (1.0 - nu**2))
        Db_base = np.array(
            [[D_base, D_base * nu, 0.0], [D_base * nu, D_base, 0.0], [0.0, 0.0, D_base * (1.0 - nu) / 2.0]]
        )

        n_elems = len(self.elements)
        mx_el = np.zeros(n_elems)
        my_el = np.zeros(n_elems)
        mxy_el = np.zeros(n_elems)

        dNdxi_c = 0.25 * np.array([[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0]])

        for ie, el in enumerate(self.elements):
            factor = stiffness_factors[ie] if stiffness_factors is not None else 1.0
            Db = Db_base * factor
            coords = self.nodes[el, :]
            dNdxy = dNdxi_c @ np.linalg.inv(dNdxi_c.T @ coords)
            u_el = disp[el, :]
            kappa = np.zeros(3)
            for i in range(4):
                kappa[0] += dNdxy[i, 0] * u_el[i, 1]
                kappa[1] += dNdxy[i, 1] * u_el[i, 2]
                kappa[2] += dNdxy[i, 1] * u_el[i, 1] + dNdxy[i, 0] * u_el[i, 2]
            M = Db @ kappa
            mx_el[ie], my_el[ie], mxy_el[ie] = M

        return {'mx': mx_el, 'my': my_el, 'mxy': mxy_el}

    def solve(
        self,
        column_loads: Optional[npt.NDArray[np.float64]] = None,
        piles: Optional[list] = None,
        max_iter: int = 30,
        tol_active: int = 0,
        concrete_nonlinear: bool = False,
        superstructure_stiffness: Optional[dict] = None,
        stiffness_factors: Optional[npt.NDArray[np.float64]] = None,
        h_per_element: Optional[npt.NDArray[np.float64]] = None,
        opening_mask: Optional[npt.NDArray[np.bool_]] = None,
    ) -> SolverResult:
        n_nodes = len(self.nodes)
        active = np.ones(n_nodes, dtype=bool)
        kv_base = self.model.soil.kv_map if self.model.soil.kv_map is not None else np.full(n_nodes, self.model.soil.kv)
        kv_iter = kv_base.copy()
        q_limit = self.model.soil.q_limit

        if stiffness_factors is None:
            stiffness_factors = np.ones(len(self.elements))

        converged = False
        for it in range(1, max_iter + 1):
            iterations = it
            K, F, K_trip = self._assemble_via_rust(
                column_loads=column_loads,
                kv_nodal=kv_iter,
                active_springs=active,
                piles=piles,
                stiffness_factors=stiffness_factors,
                h_per_element=h_per_element,
                opening_mask=opening_mask,
            )

            # Aplicar rigidez da superestrutura (Python, após montagem)
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
                U = self._solve_linear_system_py(K, F)
            else:
                U = self._solve_linear_system(K_trip, F)
            disp = U.reshape(-1, 3)

            # Atualizar Active (Tensionless)
            if self.model.soil.tensionless:
                new_active = disp[:, 0] > 1e-9
                if new_active.sum() == 0:
                    new_active[:] = True
            else:
                new_active = active.copy()

            # Atualizar Rigidez (Elasto-Plástico)
            new_kv = kv_base.copy()
            if q_limit is not None:
                pressures = kv_base * disp[:, 0]
                plastic_mask = (pressures > q_limit) & new_active
                new_kv[plastic_mask] = q_limit / np.maximum(disp[plastic_mask, 0], 1e-6)

            alpha = 0.5
            kv_iter = alpha * new_kv + (1 - alpha) * kv_iter

            if it > 1:
                diff = np.linalg.norm(disp[:, 0] - prev_disp_w) / max(np.linalg.norm(disp[:, 0]), 1e-9)
                if diff < 1e-4:
                    converged = True
                    break

            prev_disp_w = disp[:, 0].copy()
            active = new_active

            if concrete_nonlinear:
                res_temp = self._extract_moments(disp)
                m_max_el = np.sqrt(res_temp['mx'] ** 2 + res_temp['my'] ** 2 + res_temp['mxy'] ** 2)
                from concrete_nonlinear import ConcreteNonlinearEngine

                new_factors = ConcreteNonlinearEngine.compute_stiffness_reduction(m_max_el, self.model)
                stiffness_factors = 0.5 * new_factors + 0.5 * stiffness_factors

        qsoil = np.where(active, np.maximum(disp[:, 0] * kv_iter, 0.0), 0.0)
        final_moments = self._extract_moments(disp, stiffness_factors=stiffness_factors)
        mx_el, my_el, mxy_el = final_moments['mx'], final_moments['my'], final_moments['mxy']

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
        if self.model.supports:
            for sup in self.model.supports:
                nodes4, weights4 = self._find_cell_and_shape_weights(sup['x'], sup['y'])
                kz = sup.get('kz', 1e15)
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
            converged=converged,
            pile_reactions_total=pile_reactions_total,
            pile_reactions=pile_reactions,
        )

    def _find_cell_and_shape_weights(self, x: float, y: float) -> Tuple[npt.NDArray[np.int_], npt.NDArray[np.float64]]:
        """Mantido para compatibilidade com pós-processamento (reação de estacas, etc.)."""
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
        weights = np.array([(1 - tx) * (1 - ty), tx * (1 - ty), tx * ty, (1 - tx) * ty], dtype=float)
        weights /= weights.sum()
        return nodes, weights

    def export_element_results_csv(self, result: SolverResult, path: str) -> str:
        import pandas as pd

        rows = []
        for ie, el in enumerate(self.elements):
            rows.append(
                {
                    'elem': ie,
                    'xc_m': float(self.nodes[el, 0].mean()),
                    'yc_m': float(self.nodes[el, 1].mean()),
                    'mx_Nm_per_m': float(result.mx[ie]),
                    'my_Nm_per_m': float(result.my[ie]),
                    'mxy_Nm_per_m': float(result.mxy[ie]),
                    'qsoil_mean_Pa': float(result.qsoil[el].mean()),
                    'w_mean_m': float(result.disp[el, 0].mean()),
                }
            )
        pd.DataFrame(rows).to_csv(path, index=False)
        return str(path)

    def export_nodal_results_csv(self, result: SolverResult, path: str) -> str:
        import pandas as pd

        df = pd.DataFrame(
            {
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
            }
        )
        df.to_csv(path, index=False)
        return str(path)
