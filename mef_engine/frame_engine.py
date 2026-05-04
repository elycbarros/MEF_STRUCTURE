"""
frame_engine.py — Motor de Análise de Pórtico Espacial (3D) Premium.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from scipy.sparse.linalg import eigsh
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

    def _get_m_local(self, m: FrameMember, L: float, density: float = 2500.0):
        """Matriz de Massa Lumped (M5-Master)."""
        A = m.section.b * m.section.h
        mass_total = density * A * L
        m_node = mass_total / 2.0
        me = np.zeros((12,12))
        for i in [0,1,2, 6,7,8]: me[i,i] = m_node
        return me

    def solve(self, loads: List[FrameLoad], supports: Dict[int, List[int]], axial_loads: Optional[Dict[int, float]] = None) -> dict:
        K = np.zeros((self.ndof, self.ndof))
        F = np.zeros(self.ndof)
        
        for m in self.members:
            T, L = self._get_transformation(m)
            P = axial_loads.get(m.id, 0.0) if axial_loads else 0.0
            k_glob = T.T @ self._get_k_local(m, L, P) @ T
            idx_i, idx_j = self.node_map[m.node_i]*6, self.node_map[m.node_j]*6
            ix = list(range(idx_i, idx_i+6)) + list(range(idx_j, idx_j+6))
            for i_l, i_g in enumerate(ix):
                for j_l, j_g in enumerate(ix): K[i_g, j_g] += k_glob[i_l, j_l]
        
        for l in loads: 
            F[self.node_map[l.node_id]*6 : self.node_map[l.node_id]*6+6] += [l.Fx, l.Fy, l.Fz, l.Mx, l.My, l.Mz]
        
        # BCs via big value (Penalty)
        for nid, dofs in supports.items():
            for d in dofs:
                idx = self.node_map[nid]*6 + d
                K[idx, idx] += 1e18
                
        try:
            U = np.linalg.solve(K, F)
        except np.linalg.LinAlgError:
            raise UnstableModelError("Matriz de rigidez do pórtico 3D é singular. Verifique os apoios e conectividade.", module="frame_engine")
        except Exception as e:
            raise NumericalFailureError(f"Erro numérico na resolução do pórtico: {str(e)}", module="frame_engine")
            
        disps = {nid: U[self.node_map[nid]*6 : self.node_map[nid]*6+6] for nid in self.nodes}
        return {'displacements': disps, 'U_raw': U, 'K_raw': K, 'F_raw': F}

    def solve_p_delta(self, loads, supports, max_iter=15, tol=1e-5):
        res = self.solve(loads, supports)
        for i in range(max_iter):
            efforts = self.get_member_efforts(res['displacements'])
            axials = {mid: eff['i']['N'] for mid, eff in efforts.items()}
            
            try:
                new_res = self.solve(loads, supports, axial_loads=axials)
            except UnstableModelError:
                raise UnstableModelError("Pórtico instável sob carregamento vertical (divergência P-Delta).", module="frame_engine")
                
            error = np.max(np.abs(new_res['U_raw'] - res['U_raw']))
            if error < tol: return new_res
            res = new_res
            
            if i == max_iter - 1:
                raise NumericalFailureError(f"Divergência na análise P-Delta após {max_iter} iterações. Estrutura excessivamente flexível.", module="frame_engine")
        return res

    def solve_modal(self, supports: Dict[int, List[int]], n_modes: int = 3) -> dict:
        """Análise Modal: Frequências Naturais e Modos (M5-Master)."""
        K = np.zeros((self.ndof, self.ndof))
        M = np.zeros((self.ndof, self.ndof))
        
        for m in self.members:
            T, L = self._get_transformation(m)
            k_glob = T.T @ self._get_k_local(m, L) @ T
            m_glob = T.T @ self._get_m_local(m, L) @ T
            idx_i, idx_j = self.node_map[m.node_i]*6, self.node_map[m.node_j]*6
            ix = list(range(idx_i, idx_i+6)) + list(range(idx_j, idx_j+6))
            for i_l, i_g in enumerate(ix):
                for j_l, j_g in enumerate(ix):
                    K[i_g, j_g] += k_glob[i_l, j_l]
                    M[i_g, j_g] += m_glob[i_l, j_l]
        
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

    def check_equilibrium(self, loads: List[FrameLoad], displacements: Dict[int, np.ndarray], supports: Dict[int, List[int]]) -> dict:
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
            # Momentos: M_origem = M_no + r x F
            r = np.array([node.x, node.y, node.z])
            sum_loads[3:6] += m + np.cross(r, f)
            
        # Forças internas nos nós (K*U)
        node_internal_forces = {nid: np.zeros(6) for nid in self.nodes}
        for m in self.members:
            T, L = self._get_transformation(m)
            u_e = np.concatenate([displacements[m.node_i], displacements[m.node_j]])
            # f_glob = K_glob * u_glob
            f_glob = T.T @ (self._get_k_local(m, L) @ (T @ u_e))
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
            
            # Somar reações na origem
            node = self.nodes[nid]
            f_r = r_vec[0:3]
            m_r = r_vec[3:6]
            pos = np.array([node.x, node.y, node.z])
            sum_reactions[0:3] += f_r
            sum_reactions[3:6] += m_r + np.cross(pos, f_r)
            
        error = sum_loads + sum_reactions
        
        return {
            "sum_applied_kN_m": (sum_loads / 1000.0).tolist(),
            "sum_reactions_kN_m": (sum_reactions / 1000.0).tolist(),
            "equilibrium_error_kN_m": (error / 1000.0).tolist(),
            "is_equilibrated": bool(np.all(np.abs(error) < 1.0e-2)), # Tolerância de 10 mN
            "reactions": reactions
        }

    def get_detailed_diagrams(self, displacements: Dict[int, np.ndarray], n_points: int = 5) -> Dict[int, List[dict]]:
        """
        Gera dados detalhados para diagramas (N, Vy, Vz, T, My, Mz) ao longo de cada barra.
        n_points: numero de pontos de discretização por barra.
        """
        diagrams = {}
        for m in self.members:
            T, L = self._get_transformation(m)
            u_e = np.concatenate([displacements[m.node_i], displacements[m.node_j]])
            f_loc = self._get_k_local(m, L) @ (T @ u_e)
            
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
