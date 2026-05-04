"""
ssi_engine.py - Motor de Interação Solo-Estrutura Avançado.
Implementa o método iterativo Pseudo-Acoplado (Half-space).
"""
import numpy as np
from typing import Optional, Dict, Any
from radier_solver_v2 import RadierMindlinWinklerV2, PlateModel, Soil

class SSIPseudoCoupled:
    def __init__(self, model: PlateModel, Es: float = 20e6, nu_s: float = 0.3):
        """
        Es: Módulo de elasticidade do SOLO (Pa)
        nu_s: Coeficiente de Poisson do SOLO
        """
        self.model = model
        self.Es = Es
        self.nu_s = nu_s
        self.solver = RadierMindlinWinklerV2(model)
        
    def _calculate_halfspace_settlement(self, nodes: np.ndarray, qsoil: np.ndarray, areas: np.ndarray) -> np.ndarray:
        """
        Calcula o recalque em cada nó usando a integração de Boussinesq (meio-espaço elástico).
        w = Sum [ (q * area * (1 - nu^2)) / (pi * E * r) ]
        """
        n_nodes = len(nodes)
        w_ssi = np.zeros(n_nodes)
        coeff = (1.0 - self.nu_s**2) / (np.pi * self.Es)
        
        # Otimização matricial (Cuidado com memória em malhas muito grandes)
        # Para malhas gigantes, usaríamos amostragem ou algoritmos rápidos (FFT)
        for i in range(n_nodes):
            ri = np.linalg.norm(nodes - nodes[i], axis=1)
            # Evitar divisão por zero no próprio nó (aproximação por raio equivalente)
            ri[i] = np.sqrt(areas[i] / np.pi) 
            w_ssi[i] = coeff * np.sum((qsoil * areas) / ri)
            
        return w_ssi

    def solve_iterative(self, column_loads: Optional[np.ndarray] = None, 
                        max_iter: int = 5, tol: float = 0.05) -> Dict[str, Any]:
        """
        Executa o loop de convergência ISE.
        """
        n_nodes = len(self.solver.nodes)
        # Inicializa kv_map se não existir
        if self.model.soil.kv_map is None:
            self.model.soil.kv_map = np.full(n_nodes, self.model.soil.kv)
            
        current_ks = self.model.soil.kv_map.copy()
        
        for it in range(max_iter):
            print(f"Iteração ISE #{it+1}...")
            # 1. Resolve com o kv atual
            res = self.solver.solve(column_loads=column_loads)
            
            # 2. Calcula recalques do Meio-Espaço baseados nas pressões de Winkler
            w_soil = self._calculate_halfspace_settlement(res.nodes, res.qsoil, res.tributary_areas)
            
            # 3. Calcula novo ks = qsoil / w_soil
            # Evita divisão por zero e oscilações bruscas
            new_ks = np.where(w_soil > 1e-6, res.qsoil / w_soil, current_ks)
            
            # Limites físicos para o ks para evitar instabilidade numérica
            new_ks = np.clip(new_ks, 0.2 * self.model.soil.kv, 5.0 * self.model.soil.kv)
            
            # 4. Verifica convergência (Erro relativo no ks médio)
            error = np.mean(np.abs(new_ks - current_ks)) / np.mean(current_ks)
            
            # Atualiza para próxima rodada
            current_ks = 0.7 * current_ks + 0.3 * new_ks # Amortecimento numérico
            self.model.soil.kv_map = current_ks
            
            if error < tol:
                print(f"ISE Convergiu em {it+1} iterações (Erro: {error:.4f})")
                break
                
        return {
            "result": res,
            "final_kv_map": current_ks,
            "ssi_iterations": it + 1,
            "converged": error < tol
        }

if __name__ == "__main__":
    # Teste rápido de integração
    from radier_solver_v2 import PlateModel, Soil, Material
    model = PlateModel(Lx=10, Ly=10, nx=10, ny=10)
    ssi = SSIPseudoCoupled(model)
    res_ssi = ssi.solve_iterative()
    print(f"Concluído. KV médio final: {np.mean(res_ssi['final_kv_map']):.2f}")
