import numpy as np
import time
from lajes_solver import LajesMindlinSolver, SupportType, LajeModel

def test_rust_solver():
    import structural_core_rs
    print(f"📍 Module structural_core_rs loaded from: {structural_core_rs.__file__}")
    print(f"📂 Attributes: {dir(structural_core_rs)}")
    print("🚀 Iniciando Teste do Motor Rust para Lajes...")
    
    # Criar um modelo de teste
    # Laje 5x5m, h=1.0m (Grossa para evitar shear locking e comparar)
    model = LajeModel(Lx=5.0, Ly=5.0, q_acid=5000.0)
    model.material.h = 1.0
    model.material.E = 25e9
    model.material.nu = 0.20
    
    # Malha 20x20
    model.nx = 20
    model.ny = 20
    solver = LajesMindlinSolver(model)
    
    # Apoios nos 4 cantos
    from lajes_solver import PillarSupport
    model.pillars = [
        PillarSupport(id="P1", x=0.0, y=0.0, support_type=SupportType.PINNED),
        PillarSupport(id="P2", x=5.0, y=0.0, support_type=SupportType.PINNED),
        PillarSupport(id="P3", x=5.0, y=5.0, support_type=SupportType.PINNED),
        PillarSupport(id="P4", x=0.0, y=5.0, support_type=SupportType.PINNED),
    ]
            
    # Resolver com Python (desativando Rust temporariamente)
    import lajes_solver
    lajes_solver.HAS_RUST_CORE = False
    
    start_py = time.time()
    res_py = solver.solve()
    end_py = time.time()
    
    max_w_py = np.max(np.abs(res_py.disp[:, 0]))
    max_mx_py = np.max(np.abs(res_py.mx))
    print(f"✅ Python Resolvido em: {end_py - start_py:.4f}s")
    print(f"   Flecha Máxima (Py): {max_w_py*1000:.4f} mm")
    print(f"   Momento Máximo Mx (Py): {max_mx_py/1000:.4f} kNm/m")
    
    # Resolver com Rust
    lajes_solver.HAS_RUST_CORE = True
    start_rs = time.time()
    res_rs = solver.solve()
    end_rs = time.time()
    
    max_w_rs = np.max(np.abs(res_rs.disp[:, 0]))
    max_mx_rs = np.max(np.abs(res_rs.mx))
    print(f"✅ Rust Resolvido em: {end_rs - start_rs:.4f}s")
    print(f"   Flecha Máxima (Rs): {max_w_rs*1000:.4f} mm")
    print(f"   Momento Máximo Mx (Rs): {max_mx_rs/1000:.4f} kNm/m")
    
    print(f"\n📈 Resumo de Equilíbrio:")
    print(f"   Python: Carga Total={res_py.distributed_load_total/1000:.2f}kN, Reação={res_py.reactions_total/1000:.2f}kN, Resíduo={res_py.residual/1000:.4f}kN")
    print(f"   Rust:   Carga Total={res_rs.distributed_load_total/1000:.2f}kN, Reação={res_rs.reactions_total/1000:.2f}kN, Resíduo={res_rs.residual/1000:.4f}kN")

    # Comparar
    diff_w = abs(max_w_py - max_w_rs)
    print(f"\n📊 Diferença Flecha: {diff_w*1000:.6f} mm")
    
    if diff_w < 1e-6:
        print("🏆 SUCESSO: Os resultados são numericamente idênticos!")
    else:
        print("⚠️ AVISO: Há uma divergência nos resultados.")

if __name__ == "__main__":
    test_rust_solver()
