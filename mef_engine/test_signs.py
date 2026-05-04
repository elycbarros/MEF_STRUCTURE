import numpy as np
from beam_solver import BeamFEMSolver, BeamModel, BeamSection, BeamSupport, DistributedLoad

def test_signs():
    # Viga bi-apoiada 6m, carga 20kN/m
    section = BeamSection(E=210e9, b=0.2, h=0.5)
    model = BeamModel(L=6.0, section=section, n_elements=40)
    model.supports = [BeamSupport(x=0.0, type='pinned'), BeamSupport(x=6.0, type='roller')]
    model.distributed_loads = [DistributedLoad(x_start=0, x_end=6, q_start=20000, q_end=20000)]
    model.include_self_weight = False
    
    solver = BeamFEMSolver(model)
    result = solver.solve()
    
    # Moment: dashboard expects positive downwards.
    # qL^2/8 = 20 * 36 / 8 = 90 kNm
    mid_idx = 20
    print(f"Moment at center (idx {mid_idx}): {result.M[mid_idx]/1000:.2f} kNm (Expected: 90.00)")
    # Shear: dashboard expects positive upwards at start.
    # qL/2 = 20 * 6 / 2 = 60 kN
    print(f"Shear at start: {result.V[0]/1000:.2f} kN (Expected: 60.00)")
    print(f"Shear at end: {result.V[-1]/1000:.2f} kN (Expected: -60.00)")

if __name__ == "__main__":
    test_signs()
