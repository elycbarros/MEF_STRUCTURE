"""
frame_engine.py — Motor de Análise de Pórtico Espacial (3D) Premium.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from scipy.sparse.linalg import eigsh, spsolve
from scipy.linalg import eigh
from scipy.sparse import coo_matrix, eye
from errors import UnstableModelError, NumericalFailureError, InvalidInputError

@dataclass
class FrameNode:
    id: int; x: float; y: float; z: float

@dataclass
class FrameSection:
    b: float; h: float; E: float = 2.5e10; G: float = 1.0e10

@dataclass
class FrameMember:
    id: int; node_i: int; node_j: int; section: FrameSection
    L: float = 0.0

@dataclass
class FrameLoad:
    node_id: int; Fx: float = 0.0; Fy: float = 0.0; Fz: float = 0.0; Mx: float = 0.0; My: float = 0.0; Mz: float = 0.0

class Frame3DEngine:
    def __init__(self, nodes: List[FrameNode], members: List[FrameMember]):
        self.nodes = {n.id: n for n in nodes}
        self.members = members
        self.node_map = {nid: i for i, nid in enumerate(sorted(self.nodes.keys()))}
        self.ndof = 6 * len(nodes)
        
        # Populate lengths
        for m in self.members:
            _, L = self._get_transformation(m)
            m.L = L

    def _get_transformation(self, m: FrameMember):
        n1, n2 = self.nodes[m.node_i], self.nodes[m.node_j]
        L = np.sqrt((n2.x-n1.x)**2 + (n2.y-n1.y)**2 + (n2.z-n1.z)**2)
        cx, cy, cz = (n2.x-n1.x)/L, (n2.y-n1.y)/L, (n2.z-n1.z)/L
        
        # Orientação do eixo local 'y' (vetor perpendicular ao eixo x-local)
        if abs(cx) < 1e-6 and abs(cy) < 1e-6: # Vertical
            uy = np.array([0, 1, 0]) if cz > 0 else np.array([0, -1, 0])
        else:
            uy = np.array([0, 0, 1])
            
        ux = np.array([cx, cy, cz])
        uz = np.cross(ux, uy); uz /= np.linalg.norm(uz)
        uy = np.cross(uz, ux); uy /= np.linalg.norm(uy)
        
        T_sub = np.vstack([ux, uy, uz])
        T = np.zeros((12, 12))
        for i in range(4): T[3*i:3*i+3, 3*i:3*i+3] = T_sub
        return T, L

    def _get_k_local(self, m: FrameMember, L: float, P: float = 0.0):
        S = m.section
        A, Iy, Iz, J, E, G = S.b*S.h, S.b*S.h**3/12, S.h*S.b**3/12, 0.141*S.b*S.h**3, S.E, S.G
        
        ke = np.zeros((12,12))
        # Axial
        ke[0,0] = ke[6,6] = E*A/L; ke[0,6] = ke[6,0] = -E*A/L
        # Torsional
        ke[3,3] = ke[9,9] = G*J/L; ke[3,9] = ke[9,3] = -G*J/L
        # Bending XY (z-local)
        f = E*Iz/L**3
        ke[1,1]=ke[7,7]=12*f; ke[1,7]=ke[7,1]=-12*f
        ke[1,5]=ke[5,1]=ke[1,11]=ke[11,1]=6*L*f
        ke[7,5]=ke[5,7]=ke[7,11]=ke[11,7]=-6*L*f
        ke[5,5]=ke[11,11]=4*L**2*f; ke[5,11]=ke[11,5]=2*L**2*f
        # Bending XZ (y-local)
        f = E*Iy/L**3
        ke[2,2]=ke[8,8]=12*f; ke[2,8]=ke[8,2]=-12*f
        ke[2,4]=ke[4,2]=ke[2,10]=ke[10,2]=-6*L*f
        ke[8,4]=ke[4,8]=ke[8,10]=ke[10,8]=6*L*f
        ke[4,4]=ke[10,10]=4*L**2*f; ke[4,10]=ke[10,4]=2*L**2*f
        
        if abs(P) > 1e-3:
            phi = P/L
            kg = np.zeros((12,12))
            # Translações
            for i in [1,2,7,8]: kg[i,i] = 1.2*phi
            for i,j in [(1,7),(7,1),(2,8),(8,2)]: kg[i,j] = -1.2*phi
            # Acoplamento Trans-Rot
            for i,j in [(1,5),(5,1),(1,11),(11,1),(8,4),(4,8),(8,10),(10,8)]: kg[i,j] = 0.1*L*phi
            for i,j in [(7,5),(5,7),(7,11),(11,7),(2,4),(4,2),(2,10),(10,2)]: kg[i,j] = -0.1*L*phi
            # Rotações
            for i in [4,5,10,11]: kg[i,i] = 0.133*L**2*phi
            for i,j in [(4,10),(10,4),(5,11),(11,5)]: kg[i,j] = -0.033*L**2*phi
            return ke + kg
        return ke

    def _get_member_type(self, m: FrameMember) -> str:
        """Determina se o elemento é pilar (vertical) ou viga (horizontal/inclinado)."""
        n1, n2 = self.nodes[m.node_i], self.nodes[m.node_j]
        dz = abs(n2.z - n1.z)
        L = m.L if m.L > 0 else 1.0
        return 'column' if dz/L > 0.8 else 'beam'

    def _get_m_local(self, m: FrameMember, L: float, density: float = 2500.0):
        """Matriz de Massa Lumped (M5-Master)."""
        A = m.section.b * m.section.h
        mass_total = density * A * L
        m_node = mass_total / 2.0
        me = np.zeros((12,12))
        for i in [0,1,2, 6,7,8]: me[i,i] = m_node
        # Pequena inércia rotacional para evitar singularidade em eigh (M5-Master)
        for i in [3,4,5, 9,10,11]: me[i,i] = m_node * (L**2 / 100.0) 
        return me

    def solve(self, loads: List[FrameLoad], supports: Dict[int, List[int]], axial_loads: Optional[Dict[int, float]] = None, reduce_stiffness: bool = False, elastic_supports: Optional[Dict[int, List[float]]] = None) -> dict:
        from scipy.sparse import coo_matrix
        from scipy.sparse.linalg import spsolve
        
        row_idx = []
        col_idx = []
        data_val = []
        F = np.zeros(self.ndof)
        
        # ... (same loop as before)
        for m in self.members:
            T, L = self._get_transformation(m)
            P = axial_loads.get(m.id, 0.0) if axial_loads else 0.0
            k_local = self._get_k_local(m, L, P)
            if reduce_stiffness:
                m_type = self._get_member_type(m)
                k_local *= (0.8 if m_type == 'column' else 0.4)
            k_glob = T.T @ k_local @ T
            idx_i, idx_j = self.node_map[m.node_i]*6, self.node_map[m.node_j]*6
            dofs = list(range(idx_i, idx_i+6)) + list(range(idx_j, idx_j+6))
            for i_local in range(12):
                for j_local in range(12):
                    row_idx.append(dofs[i_local]); col_idx.append(dofs[j_local]); data_val.append(k_glob[i_local, j_local])

        # 2. Adicionar Molas Elásticas (SSI / Winkler)
        if elastic_supports:
            for nid, ks_list in elastic_supports.items():
                base_idx = self.node_map[nid]*6
                for d, ks in enumerate(ks_list):
                    if ks > 0:
                        row_idx.append(base_idx + d); col_idx.append(base_idx + d); data_val.append(ks)

        for l in loads: 
            F[self.node_map[l.node_id]*6 : self.node_map[l.node_id]*6+6] += [l.Fx, l.Fy, l.Fz, l.Mx, l.My, l.Mz]
        
        K = coo_matrix((data_val, (row_idx, col_idx)), shape=(self.ndof, self.ndof)).tocsr()
        
        # 3. Penalização para apoios rígidos
        penalty = 1e15
        for nid, dofs in supports.items():
            for d in dofs:
                idx = self.node_map[nid]*6 + d
                K[idx, idx] += penalty
                F[idx] = 0.0 # Reação será K[idx,idx]*U[idx] mas forçamos 0 para deslocamento
        
        try:
            # Regularização mínima
            K_reg = K + eye(self.ndof, format='csr') * 1e-9
            U = spsolve(K_reg, F)
        except Exception as e:
            if "singular" in str(e).lower():
                raise UnstableModelError("Matriz de rigidez do pórtico 3D é singular. Verifique os apoios e conectividade.", module="frame_engine")
            raise NumericalFailureError(f"Erro numérico na resolução do pórtico: {str(e)}", module="frame_engine")
            
        disps = {nid: U[self.node_map[nid]*6 : self.node_map[nid]*6+6] for nid in self.nodes}
        return {'displacements': disps, 'U_raw': U, 'K_raw': K, 'F_raw': F}

    def solve_p_delta(self, loads, supports, max_iter=20, tol=1e-5, reduce_stiffness=True):
        """
        Solver P-Delta Otimizado com Aceleração de Aitken (Elite Tier).
        Ideal para edifícios altos (>30 pavimentos).
        """
        res = self.solve(loads, supports, reduce_stiffness=reduce_stiffness)
        U_prev = res['U_raw']
        U_pprev = None
        
        for i in range(max_iter):
            efforts = self.get_member_efforts(res['displacements'])
            # Converter de kN (get_member_efforts) para N (_get_k_local)
            axials = {mid: eff['i']['N'] * 1000.0 for mid, eff in efforts.items()}
            
            try:
                new_res = self.solve(loads, supports, axial_loads=axials, reduce_stiffness=reduce_stiffness)
            except UnstableModelError:
                raise UnstableModelError("Pórtico instável sob carregamento vertical (divergência P-Delta).", module="frame_engine")
                
            U_curr = new_res['U_raw']
            
            # Aceleração de Aitken para convergência rápida
            if U_pprev is not None:
                diff1 = U_curr - U_prev
                diff2 = U_prev - U_pprev
                denom = diff1 - diff2
                # Evitar divisão por zero
                mask = np.abs(denom) > 1e-12
                U_acc = U_curr.copy()
                U_acc[mask] = U_curr[mask] - (diff1[mask]**2) / denom[mask]
                U_curr = U_acc
            
            error = np.max(np.abs(U_curr - U_prev))
            if error < tol: 
                res = new_res
                res['p_delta_iterations'] = i + 1
                break
            
            U_pprev = U_prev
            U_prev = U_curr
            res = new_res
            
        # Refinamento Final (Garantir Equilíbrio Exato após Aitken)
        efforts = self.get_member_efforts(res['displacements'])
        axials = {mid: eff['i']['N'] * 1000.0 for mid, eff in efforts.items()}
        res_final = self.solve(loads, supports, axial_loads=axials, reduce_stiffness=reduce_stiffness)
        res_final['p_delta_iterations'] = res.get('p_delta_iterations', max_iter)
        return res_final

    def calculate_stability_indices(self, loads: List[FrameLoad], supports: Dict[int, List[int]]) -> dict:
        """
        Calcula os índices de estabilidade global Gama-Z e Alfa (NBR 6118).
        """
        # 1. Análise de 1a Ordem (Rígida)
        res1 = self.solve(loads, supports, reduce_stiffness=True)
        # 2. Análise de 2a Ordem (P-Delta)
        res2 = self.solve_p_delta(loads, supports, reduce_stiffness=True)
        
        # Momento total de 1a ordem (M1d) e acréscimo de 2a ordem (M2d)
        # Calculamos via trabalho virtual ou simplificado via somatório de reações
        # Aqui usaremos a razão de deslocamentos máximos como aproximação de Gama-Z
        d1_max = np.max(np.abs(res1['U_raw']))
        d2_max = np.max(np.abs(res2['U_raw']))
        
        gamma_z = d2_max / d1_max if d1_max > 1e-9 else 1.0
        
        # Alfa (Estimativa baseada em rigidez equivalente)
        # Alfa = H * sqrt(P / EI)
        # Para simplificar no pórtico 3D, usamos a relação empírica com Gamma-Z
        alpha = 0.5 * (gamma_z - 1.0)**0.5 # Aproximação didática
        
        return {
            'gamma_z': round(gamma_z, 3),
            'alpha': round(alpha, 3),
            'is_fixed_node': gamma_z <= 1.10,
            'p_delta_iterations': res2.get('p_delta_iterations', 0),
            'recommendation': "Nós Fixos" if gamma_z <= 1.10 else "Nós Móveis (Considerar 2a Ordem)"
        }

    def solve_modal(self, supports: Dict[int, List[int]], n_modes: int = 3) -> dict:
        """Análise Modal: Frequências Naturais e Modos (M5-Master)."""
        from scipy.sparse import coo_matrix
        
        row_idx_k = []; col_idx_k = []; data_val_k = []
        row_idx_m = []; col_idx_m = []; data_val_m = []
        
        for m in self.members:
            T, L = self._get_transformation(m)
            k_glob = T.T @ self._get_k_local(m, L) @ T
            m_glob = T.T @ self._get_m_local(m, L) @ T
            idx_i, idx_j = self.node_map[m.node_i]*6, self.node_map[m.node_j]*6
            dofs = list(range(idx_i, idx_i+6)) + list(range(idx_j, idx_j+6))
            
            for i_local in range(12):
                for j_local in range(12):
                    row_idx_k.append(dofs[i_local]); col_idx_k.append(dofs[j_local]); data_val_k.append(k_glob[i_local, j_local])
                    row_idx_m.append(dofs[i_local]); col_idx_m.append(dofs[j_local]); data_val_m.append(m_glob[i_local, j_local])
        
        K = coo_matrix((data_val_k, (row_idx_k, col_idx_k)), shape=(self.ndof, self.ndof)).tocsr()
        M = coo_matrix((data_val_m, (row_idx_m, col_idx_m)), shape=(self.ndof, self.ndof)).tocsr()
        
        # Reduzir matrizes (Remover DOFs suportados)
        fixed_dofs = []
        for nid, dofs in supports.items():
            for d in dofs: fixed_dofs.append(self.node_map[nid]*6 + d)
        
        free_dofs = [i for i in range(self.ndof) if i not in fixed_dofs]
        K_free = K[np.ix_(free_dofs, free_dofs)]
        M_free = M[np.ix_(free_dofs, free_dofs)]
        
        try:
            # Resolvendo KU = lambda MU
            vals, vecs = eigsh(K_free, k=min(n_modes, len(free_dofs)-1), M=M_free, which='SM')
            freqs_hz = np.sqrt(vals) / (2 * np.pi)
            periods = 1.0 / freqs_hz
            return {
                'frequencies_hz': freqs_hz.tolist(),
                'periods_s': periods.tolist(),
                'modes': vecs.T.tolist(),
                'status': 'OK'
            }
        except Exception as e:
            raise NumericalFailureError(f"Falha na análise modal: {str(e)}", module="frame_engine")

    def get_member_efforts(self, displacements: Dict[int, np.ndarray]) -> Dict[int, dict]:
        """
        Extrai esforços internos (N, Vy, Vz, T, My, Mz) para cada barra.
        Retorna em kN e kNm (assume entrada em N e Nm).
        """
        efforts = {}
        for m in self.members:
            T, L = self._get_transformation(m)
            u_e = np.concatenate([displacements[m.node_i], displacements[m.node_j]])
            # f_local = K_local * (T * u_global)
            f_loc = self._get_k_local(m, L) @ (T @ u_e)
            
            # Convenção de sinais (Tensão positiva)
            # End i: [Fx1, Fy1, Fz1, Mx1, My1, Mz1]
            # End j: [Fx2, Fy2, Fz2, Mx2, My2, Mz2]
            
            efforts[m.id] = {
                "i": {
                    "N": -f_loc[0] / 1000.0,
                    "Vy": f_loc[1] / 1000.0,
                    "Vz": f_loc[2] / 1000.0,
                    "T": f_loc[3] / 1000.0,
                    "My": f_loc[4] / 1000.0,
                    "Mz": f_loc[5] / 1000.0
                },
                "j": {
                    "N": f_loc[6] / 1000.0,
                    "Vy": -f_loc[7] / 1000.0,
                    "Vz": -f_loc[8] / 1000.0,
                    "T": -f_loc[9] / 1000.0,
                    "My": -f_loc[10] / 1000.0,
                    "Mz": -f_loc[11] / 1000.0
                }
            }
        return efforts

    def check_equilibrium(self, loads: List[FrameLoad], displacements: Dict[int, np.ndarray], supports: Dict[int, List[int]], reduce_stiffness: bool = False, axial_loads: Optional[Dict[int, float]] = None) -> dict:
        """
        Verifica o equilíbrio global somando cargas aplicadas e reações em relação à origem (0,0,0).
        """
        sum_loads = np.zeros(6)
        for l in loads:
            node = self.nodes[l.node_id]
            f = np.array([l.Fx, l.Fy, l.Fz])
            m = np.array([l.Mx, l.My, l.Mz])
            # Forças
            sum_loads[0:3] += f
            # Momentos: M_origem = M_no + r_deformado x F
            u = displacements[l.node_id]
            r = np.array([node.x + u[0], node.y + u[1], node.z + u[2]])
            sum_loads[3:6] += m + np.cross(r, f)
            
        # Forças internas nos nós (K*U)
        node_internal_forces = {nid: np.zeros(6) for nid in self.nodes}
        for m in self.members:
            T, L = self._get_transformation(m)
            u_e = np.concatenate([displacements[m.node_i], displacements[m.node_j]])
            
            P = axial_loads.get(m.id, 0.0) if axial_loads else 0.0
            
            # Usar a mesma rigidez da análise para verificação de equilíbrio
            k_local = self._get_k_local(m, L, P)
            if reduce_stiffness:
                m_type = self._get_member_type(m)
                factor = 0.8 if m_type == 'column' else 0.4
                k_local *= factor
                
            f_glob = T.T @ (k_local @ (T @ u_e))
            node_internal_forces[m.node_i] += f_glob[0:6]
            node_internal_forces[m.node_j] += f_glob[6:12]
        
        # Reações nos nós suportados: R = F_int - F_ext
        loads_dict = {l.node_id: np.array([l.Fx, l.Fy, l.Fz, l.Mx, l.My, l.Mz]) for l in loads}
        reactions = {}
        sum_reactions = np.zeros(6)
        for nid in supports:
            f_int = node_internal_forces[nid]
            f_ext = loads_dict.get(nid, np.zeros(6))
            r_vec = f_int - f_ext
            reactions[str(nid)] = (r_vec / 1000.0).tolist()
            
            # Somar reações na origem (Usando posição deformada para equilíbrio P-Delta)
            node = self.nodes[nid]
            u = displacements[nid]
            f_r = r_vec[0:3]
            m_r = r_vec[3:6]
            pos = np.array([node.x + u[0], node.y + u[1], node.z + u[2]])
            sum_reactions[0:3] += f_r
            sum_reactions[3:6] += m_r + np.cross(pos, f_r)
            
        error = sum_loads + sum_reactions
        
        return {
            "sum_applied_kN_m": (sum_loads / 1000.0).tolist(),
            "sum_reactions_kN_m": (sum_reactions / 1000.0).tolist(),
            "equilibrium_error_kN_m": (error / 1000.0).tolist(),
            "is_equilibrated": bool(np.all(np.abs(error) < 1.0e-2)), # Tolerância de 10 mN/mN.m
            "reactions": reactions
        }

    def modal_analysis(self, num_modes: int = 10, supports: Dict[int, List[int]] = None) -> dict:
        """
        Realiza análise modal (autovetores e autovalores) para extrair frequências e modos de vibração.
        """
        # 1. Montagem de K e M (Versão Dense para Autovalores de pequeno/médio porte)
        K_full = np.zeros((self.ndof, self.ndof))
        M_full = np.zeros((self.ndof, self.ndof))
        
        for m in self.members:
            T, L = self._get_transformation(m)
            k_glob = T.T @ self._get_k_local(m, L) @ T
            m_glob = T.T @ self._get_m_local(m, L) @ T
            
            idx_i, idx_j = self.node_map[m.node_i]*6, self.node_map[m.node_j]*6
            dofs = list(range(idx_i, idx_i+6)) + list(range(idx_j, idx_j+6))
            
            for i_local in range(12):
                for j_local in range(12):
                    K_full[dofs[i_local], dofs[j_local]] += k_glob[i_local, j_local]
                    M_full[dofs[i_local], dofs[j_local]] += m_glob[i_local, j_local]
        
        # 2. Aplicar Condições de Contorno (Eliminar DOFs restringidos)
        fixed_dofs = []
        if supports:
            for nid, dofs in supports.items():
                for d in dofs:
                    fixed_dofs.append(self.node_map[nid]*6 + d)
        
        free_dofs = [i for i in range(self.ndof) if i not in fixed_dofs]
        if not free_dofs:
            return {"success": False, "error": "No free DOFs for modal analysis"}
            
        K_free = K_full[np.ix_(free_dofs, free_dofs)]
        M_free = M_full[np.ix_(free_dofs, free_dofs)]
        
        # 3. Resolver Autovalores (K - omega^2 * M = 0)
        eigenvalues, eigenvectors = eigh(K_free, M_free)
        
        total_mass_x = 0.0
        for i, dof in enumerate(free_dofs):
            if dof % 6 == 0: # X translation
                total_mass_x += M_free[i, i]
        
        # 4. Extrair Resultados
        modes = []
        num_extracted = min(num_modes, len(eigenvalues))
        
        # Direção de participação X
        unit_x = np.zeros(len(free_dofs))
        for i, dof in enumerate(free_dofs):
            if dof % 6 == 0: unit_x[i] = 1.0
            
        for i in range(num_extracted):
            omega2 = eigenvalues[i]
            if omega2 <= 0: continue
            
            omega = np.sqrt(omega2)
            f = omega / (2 * np.pi)
            T_period = 1.0 / f
            
            phi = eigenvectors[:, i]
            # Fator de participação modal (L = phi' * M * unit)
            L_modal = phi.T @ M_free @ unit_x
            M_modal = phi.T @ M_free @ phi
            participation_x = (L_modal**2) / M_modal
            
            modes.append({
                "mode": i + 1,
                "frequency_hz": float(f),
                "period_s": float(T_period),
                "mass_participation_x": float(participation_x / total_mass_x) if total_mass_x > 0 else 0.0
            })
            
        return {
            "success": True,
            "modes": modes,
            "total_mass_kg": float(total_mass_x)
        }

    def get_detailed_diagrams(self, displacements: Dict[int, np.ndarray], n_points: int = 5, reduce_stiffness: bool = False, axial_loads: Optional[Dict[int, float]] = None) -> Dict[int, List[dict]]:
        """
        Gera dados detalhados para diagramas (N, Vy, Vz, T, My, Mz) ao longo de cada barra.
        n_points: numero de pontos de discretização por barra.
        """
        diagrams = {}
        for m in self.members:
            T, L = self._get_transformation(m)
            u_e = np.concatenate([displacements[m.node_i], displacements[m.node_j]])
            
            P = axial_loads.get(m.id, 0.0) if axial_loads else 0.0
            k_local = self._get_k_local(m, L, P)
            if reduce_stiffness:
                m_type = self._get_member_type(m)
                factor = 0.8 if m_type == 'column' else 0.4
                k_local *= factor
                
            f_loc = k_local @ (T @ u_e)
            
            # Esforços nas extremidades (local)
            ei = {
                "N": -f_loc[0], "Vy": f_loc[1], "Vz": f_loc[2],
                "T": f_loc[3], "My": f_loc[4], "Mz": f_loc[5]
            }
            ej = {
                "N": f_loc[6], "Vy": -f_loc[7], "Vz": -f_loc[8],
                "T": -f_loc[9], "My": -f_loc[10], "Mz": -f_loc[11]
            }
            
            points = []
            for i in range(n_points):
                fraction = (i / (n_points - 1)) if n_points > 1 else 0
                x = fraction * L
                # Interpolação linear para momentos
                points.append({
                    "x": round(float(x), 3),
                    "N": round(float(ei["N"]) / 1000.0, 3),
                    "Vy": round(float(ei["Vy"]) / 1000.0, 3),
                    "Vz": round(float(ei["Vz"]) / 1000.0, 3),
                    "T": round(float(ei["T"]) / 1000.0, 3),
                    "My": round((float(ei["My"]) + (float(ej["My"]) - float(ei["My"])) * fraction) / 1000.0, 3),
                    "Mz": round((float(ei["Mz"]) + (float(ej["Mz"]) - float(ei["Mz"])) * fraction) / 1000.0, 3),
                })
            diagrams[m.id] = points
        return diagrams
