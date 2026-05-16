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
from enum import Enum

try:
    import structural_core_rs
    HAS_RUST_CORE = True
except ImportError:
    HAS_RUST_CORE = False


class SupportType(Enum):
    PINNED = "pinned"   # Apenas w restrito
    FIXED = "fixed"     # w, thx, thy restritos
    SPRING = "spring"   # Rigidez elástica kw


@dataclass
class Material:
    E: float = 32e9
    nu: float = 0.20
    h: float = 0.60


@dataclass
class PillarSupport:
    id: str
    x: float
    y: float
    p_kN: float = 0.0 # Carga concentrada
    bx: float = 0.5
    by: float = 0.5
    support_type: SupportType = SupportType.PINNED
    k_spring: float = 0.0 # Usado se SupportType.SPRING

@dataclass
class LineSupport:
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    support_type: SupportType = SupportType.PINNED
    k_spring: float = 0.0

@dataclass
class Hole:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def contains(self, x: float, y: float) -> bool:
        return (self.x_min - 1e-9 <= x <= self.x_max + 1e-9) and \
               (self.y_min - 1e-9 <= y <= self.y_max + 1e-9)

@dataclass
class LajeModel:
    Lx: float = 24.0
    Ly: float = 24.0
    nx: int = 13
    ny: int = 13
    material: Material = field(default_factory=Material)
    pillars: list[PillarSupport] = field(default_factory=list)
    line_supports: list[LineSupport] = field(default_factory=list)
    holes: list[Hole] = field(default_factory=list)
    q_pp: float = 0.0 # Peso próprio N/m2
    q_perm: float = 0.0 # Carga permanente N/m2
    q_acid: float = 0.0 # Sobrecarga acidental N/m2

    def validate(self) -> None:
        if self.Lx <= 0 or self.Ly <= 0:
            raise ValueError('Lx e Ly devem ser positivos.')
        if self.nx < 2 or self.ny < 2:
            raise ValueError('nx e ny devem ser >= 2.')
        if self.material.E <= 0 or self.material.h <= 0:
            raise ValueError('E e h devem ser positivos.')
        if not (0.0 < self.material.nu < 0.5):
            raise ValueError('nu deve estar entre 0 e 0.5.')


@dataclass
class LajesSolverResult:
    nodes: np.ndarray
    elements: np.ndarray
    disp: np.ndarray
    mx: np.ndarray
    my: np.ndarray
    mxy: np.ndarray
    tributary_areas: np.ndarray
    reactions: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    distributed_load_total: float
    reactions_total: float
    residual: float


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


class LajesMindlinSolver:
    def __init__(self, model: LajeModel):
        self.model = model
        self.model.validate()
        self._build_mesh()
        self._last_distributed_load_total = 0.0

    def _build_mesh(self) -> None:
        m = self.model
        xs = np.linspace(0.0, m.Lx, m.nx)
        ys = np.linspace(0.0, m.Ly, m.ny)
        Xg, Yg = np.meshgrid(xs, ys)
        self.nodes = np.column_stack([Xg.ravel(), Yg.ravel()])
        self.xs = xs
        self.ys = ys
        
        # Identificar nós que estão dentro de furos
        node_in_hole = np.zeros(len(self.nodes), dtype=bool)
        for hole in m.holes:
            for i, (nx, ny) in enumerate(self.nodes):
                if hole.contains(nx, ny):
                    node_in_hole[i] = True

        elems = []
        for j in range(m.ny - 1):
            for i in range(m.nx - 1):
                n0 = j * m.nx + i
                n1 = n0 + 1
                n2 = n0 + m.nx + 1
                n3 = n0 + m.nx
                
                # Calcular centro do elemento
                ex = (self.nodes[n0, 0] + self.nodes[n2, 0]) / 2.0
                ey = (self.nodes[n0, 1] + self.nodes[n2, 1]) / 2.0
                
                # Se o centro estiver num furo, ignora o elemento
                skip = False
                for hole in m.holes:
                    if hole.contains(ex, ey):
                        skip = True
                        break
                if not skip:
                    elems.append([n0, n1, n2, n3])
                    
        self.elements = np.array(elems, dtype=int)
        self._tributary_areas = self._compute_tributary_areas()

    def _compute_tributary_areas(self) -> np.ndarray:
        m = self.model
        # Para malha com furos, a área tributária simplificada (np.outer) não funciona perfeitamente
        # se houver furos. Vamos calcular com base nos elementos ativos.
        areas = np.zeros(len(self.nodes))
        for el in self.elements:
            coords = self.nodes[el, :]
            # Área do elemento (retangular)
            dx = coords[1, 0] - coords[0, 0]
            dy = coords[3, 1] - coords[0, 1]
            el_area = abs(dx * dy)
            for n in el:
                areas[n] += el_area / 4.0
        return areas

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

    def _element_stiffness(self, coords: np.ndarray) -> np.ndarray:
        m = self.model.material
        h = m.h
        E, nu = m.E, m.nu
        D = E * h**3 / (12.0 * (1.0 - nu**2))
        G = E / (2.0 * (1.0 + nu))
        ks = 5.0 / 6.0
        Ds = ks * G * h
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

    def _assemble_global(self, combo_multiplier_pp=1.0, combo_multiplier_perm=1.0, combo_multiplier_acid=1.0):
        from scipy.sparse import coo_matrix
        n_nodes = len(self.nodes)
        ndof = 3 * n_nodes
        m = self.model
        
        row_idx = []
        col_idx = []
        data_val = []
        F = np.zeros(ndof)

        for el in self.elements:
            coords = self.nodes[el, :]
            Ke = self._element_stiffness(coords)
            dofs = np.array([3*n + d for n in el for d in range(3)])
            
            for i_local in range(12):
                for j_local in range(12):
                    row_idx.append(dofs[i_local])
                    col_idx.append(dofs[j_local])
                    data_val.append(Ke[i_local, j_local])
            
        K_unpenalized = coo_matrix((data_val, (row_idx, col_idx)), shape=(ndof, ndof)).tocsr()

        # Aplicar cargas distribuídas
        q_total = (m.q_pp * combo_multiplier_pp + 
                   m.q_perm * combo_multiplier_perm + 
                   m.q_acid * combo_multiplier_acid)
        
        distributed_load_total = 0.0
        for el in self.elements:
            coords = self.nodes[el, :]
            a_el = abs((coords[:, 0].max() - coords[:, 0].min()) * (coords[:, 1].max() - coords[:, 1].min()))
            fe = q_total * a_el / 4.0
            distributed_load_total += q_total * a_el
            for n in el:
                F[3*n] += fe

        # Aplicar Método de Penalidade para apoios (Pilares e Vigas)
        penalty = 1e14
        support_nodes = set()
        
        # Pilares (Área do Pilar)
        for p in m.pillars:
            # Encontrar nós dentro da área do pilar
            half_bx = p.bx / 2.0
            half_by = p.by / 2.0
            
            x_min, x_max = p.x - half_bx, p.x + half_bx
            y_min, y_max = p.y - half_by, p.y + half_by
            
            found_any = False
            for i, node in enumerate(self.nodes):
                if (x_min - 1e-4 <= node[0] <= x_max + 1e-4) and \
                   (y_min - 1e-4 <= node[1] <= y_max + 1e-4):
                    
                    support_nodes.add(i)
                    found_any = True
                    if p.support_type == SupportType.PINNED:
                        row_idx.append(3*i); col_idx.append(3*i); data_val.append(penalty)
                    elif p.support_type == SupportType.FIXED:
                        for d in range(3):
                            row_idx.append(3*i+d); col_idx.append(3*i+d); data_val.append(penalty)
                    elif p.support_type == SupportType.SPRING:
                        row_idx.append(3*i); col_idx.append(3*i); data_val.append(p.k_spring)
            
            # Fallback: se nenhum nó foi encontrado (malha muito grossa), pega o mais próximo
            if not found_any:
                distances = np.linalg.norm(self.nodes - np.array([p.x, p.y]), axis=1)
                i_closest = np.argmin(distances)
                support_nodes.add(i_closest)
                if p.support_type == SupportType.PINNED:
                    row_idx.append(3*i_closest); col_idx.append(3*i_closest); data_val.append(penalty)
                elif p.support_type == SupportType.FIXED:
                    for d in range(3):
                        row_idx.append(3*i_closest+d); col_idx.append(3*i_closest+d); data_val.append(penalty)

        # Vigas (Apoios de Linha)
        for line in m.line_supports:
            import math
            dx = line.x2 - line.x1
            dy = line.y2 - line.y1
            length = math.sqrt(dx**2 + dy**2)
            if length < 1e-9: continue
            
            tol = 0.05
            for i, node in enumerate(self.nodes):
                dist = abs(dy*node[0] - dx*node[1] + line.x2*line.y1 - line.y2*line.x1) / length
                dot = ((node[0] - line.x1)*dx + (node[1] - line.y1)*dy) / (length**2)
                
                if dist < tol and 0.0 <= dot <= 1.0:
                    support_nodes.add(i)
                    if line.support_type == SupportType.PINNED:
                        row_idx.append(3*i); col_idx.append(3*i); data_val.append(penalty)
                    elif line.support_type == SupportType.FIXED:
                        for d in range(3):
                            row_idx.append(3*i+d); col_idx.append(3*i+d); data_val.append(penalty)
                    elif line.support_type == SupportType.SPRING:
                        row_idx.append(3*i); col_idx.append(3*i); data_val.append(line.k_spring)

        K = coo_matrix((data_val, (row_idx, col_idx)), shape=(ndof, ndof)).tocsr()
        self._last_distributed_load_total = float(distributed_load_total)
        self.support_nodes = list(support_nodes)
        return K, F, K_unpenalized

    def _solve_linear_system(self, K, F: np.ndarray) -> np.ndarray:
        from scipy.sparse.linalg import spsolve
        from scipy.sparse import eye
        ndof = len(F)
        reg = 1e-9
        K_reg = K + eye(ndof, format='csr') * reg
        return spsolve(K_reg, F)

    def solve(
        self,
        combo_multiplier_pp=1.0,
        combo_multiplier_perm=1.0,
        combo_multiplier_acid=1.0
    ) -> LajesSolverResult:
        if HAS_RUST_CORE:
            return self._solve_with_rust(combo_multiplier_pp, combo_multiplier_perm, combo_multiplier_acid)
        
        K, F, K_unpenalized = self._assemble_global(combo_multiplier_pp, combo_multiplier_perm, combo_multiplier_acid)
        U = self._solve_linear_system(K, F)
        disp = U.reshape(-1, 3)
        
        # Reações de apoio (cortante) R = K_unpenalized * U - F
        # No equilíbrio global (sem apoios), K*U = F => R = 0.
        # Em nós apoiados, K*U (força interna) - F (força externa) = R (reação do apoio)
        # Usamos o sinal negativo para que a reação aponte para cima (contra a gravidade)
        R_nodal = K_unpenalized @ U - F
        reactions = np.zeros(len(self.nodes))
        reactions[self.support_nodes] = -R_nodal[3 * np.array(self.support_nodes)]
            
        reactions_total = np.sum(reactions)
        
        E, nu, h = self.model.material.E, self.model.material.nu, self.model.material.h
        D = E * h**3 / (12.0 * (1.0 - nu**2))
        Db = np.array([
            [D, D * nu, 0.0],
            [D * nu, D, 0.0],
            [0.0, 0.0, D * (1.0 - nu) / 2.0]
        ])

        mx_el = np.zeros(len(self.elements))
        my_el = np.zeros(len(self.elements))
        mxy_el = np.zeros(len(self.elements))
        vx_el = np.zeros(len(self.elements))
        vy_el = np.zeros(len(self.elements))
        
        dNdxi_c = 0.25 * np.array([
            [-1.0, -1.0],
            [ 1.0, -1.0],
            [ 1.0,  1.0],
            [-1.0,  1.0]
        ])

        for ie, el in enumerate(self.elements):
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

            # Esforços Cortantes (Vx, Vy)
            G = E / (2.0 * (1.0 + nu))
            ks = 5.0 / 6.0
            Ds = ks * G * h
            
            # vx = Ds * (thx + dw/dx), vy = Ds * (thy + dw/dy)
            # No centro (xi=0, eta=0), N = [0.25, 0.25, 0.25, 0.25]
            w_c = np.mean(u_el[:, 0])
            thx_c = np.mean(u_el[:, 1])
            thy_c = np.mean(u_el[:, 2])
            
            dwdx = dNdxy[:, 0] @ u_el[:, 0]
            dwdy = dNdxy[:, 1] @ u_el[:, 0]
            
            vx_el[ie] = Ds * (thx_c + dwdx)
            vy_el[ie] = Ds * (thy_c + dwdy)

        return LajesSolverResult(
            nodes=self.nodes,
            elements=self.elements,
            disp=disp,
            mx=mx_el,
            my=my_el,
            mxy=mxy_el,
            vx=vx_el,
            vy=vy_el,
            tributary_areas=self._tributary_areas.copy(),
            reactions=reactions,
            distributed_load_total=float(self._last_distributed_load_total),
            reactions_total=float(reactions_total),
            residual=float(reactions_total - self._last_distributed_load_total)
        )

    def _solve_with_rust(self, combo_pp=1.0, combo_perm=1.0, combo_acid=1.0) -> LajesSolverResult:
        m = self.model
        
        # Preparar material para o Rust
        rust_material = structural_core_rs.SlabMaterial(
            e=float(m.material.E),
            nu=float(m.material.nu),
            h=float(m.material.h)
        )
        
        # Preparar furos
        rust_holes = [
            structural_core_rs.RustHole(float(h.x_min), float(h.y_min), float(h.x_max), float(h.y_max))
            for h in m.holes
        ]
        
        # Preparar pilares
        rust_pillars = [
            structural_core_rs.RustPillar(str(p.id), float(p.x), float(p.y), float(p.p_kN), float(p.bx), float(p.by))
            for p in m.pillars
        ]
        
        q_total = float(m.q_pp * combo_pp + m.q_perm * combo_perm + m.q_acid * combo_acid)
        
        # Criar modelo de laje de alto nível
        rust_model = structural_core_rs.SlabModel(
            lx=float(m.Lx),
            ly=float(m.Ly),
            nx=int(m.nx),
            ny=int(m.ny),
            holes=rust_holes,
            pillars=rust_pillars,
            q_total=q_total
        )
        
        # Resolver em Rust (Geração de malha + Assemblagem + Solver + Esforços)
        res = structural_core_rs.solve_slabs_from_model(rust_model, rust_material)
        
        # Sincronizar malha gerada pelo Rust
        self.nodes = np.array(res["nodes"])
        self.elements = np.array(res["elements"], dtype=int)
        self._tributary_areas = self._compute_tributary_areas()
        
        # Extrair resultados
        u = np.array(res["u"])
        disp = u.reshape(-1, 3)
        mx = np.array(res["mx"])
        my = np.array(res["my"])
        mxy = np.array(res["mxy"])
        vx = np.array(res["vx"])
        vy = np.array(res["vy"])
        
        # Reações de apoio
        reactions_raw = np.array(res["reactions"])
        reactions = np.zeros(len(self.nodes))
        for i in range(len(self.nodes)):
            reactions[i] = -reactions_raw[i * 3]
            
        distributed_load_total = q_total * np.sum(self._tributary_areas)
        reactions_total = np.sum(reactions)
        residual = abs(distributed_load_total - reactions_total)
        
        return LajesSolverResult(
            nodes=self.nodes,
            elements=self.elements,
            disp=disp,
            mx=mx,
            my=my,
            mxy=mxy,
            vx=vx,
            vy=vy,
            tributary_areas=self._tributary_areas,
            reactions=reactions,
            distributed_load_total=distributed_load_total,
            reactions_total=reactions_total,
            residual=residual
        )
    def export_element_results_csv(self, result: LajesSolverResult, path: str) -> str:
        rows = []
        for ie, el in enumerate(self.elements):
            rows.append({
                'elem': ie,
                'xc_m': float(self.nodes[el, 0].mean()),
                'yc_m': float(self.nodes[el, 1].mean()),
                'mx_Nm_per_m': float(result.mx[ie]),
                'my_Nm_per_m': float(result.my[ie]),
                'mxy_Nm_per_m': float(result.mxy[ie]),
                'w_mean_m': float(result.disp[el, 0].mean()),
            })
        df = pd.DataFrame(rows)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return str(path)

    def export_nodal_results_csv(self, result: LajesSolverResult, path: str) -> str:
        df = pd.DataFrame({
            'node': np.arange(len(result.nodes)),
            'x_m': result.nodes[:, 0],
            'y_m': result.nodes[:, 1],
            'w_m': result.disp[:, 0],
            'thx_rad': result.disp[:, 1],
            'thy_rad': result.disp[:, 2],
            'reactions_N': result.reactions,
            'area_m2': result.tributary_areas,
        })
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return str(path)