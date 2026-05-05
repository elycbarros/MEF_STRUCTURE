
import numpy as np
from dataclasses import dataclass, field
from typing import List

@dataclass
class BeamSupport:
    x: float
    type: str = 'pinned'

@dataclass
class PointLoad:
    x: float
    P: float = 0.0

@dataclass
class DistributedLoad:
    x_start: float
    x_end: float
    q_start: float
    q_end: float = 0.0

class ClassicalBeamSolver:
    @staticmethod
    def generate_diagrams(L: float, distributed_loads: list, point_loads: list = None, supports: list = None, n_points: int = 100) -> dict:
        x = np.linspace(0, L, n_points)
        V = np.zeros_like(x)
        M = np.zeros_like(x)
        sups = supports or []
        pts = point_loads or []
        dloads = distributed_loads or []
        
        if len(sups) >= 2:
            s1, s2 = sorted(sups, key=lambda s: s.x)[:2]
            x1, x2 = s1.x, s2.x
            dist = x2 - x1
            if dist > 0:
                M_loads_x1 = sum(p.P * (p.x - x1) for p in pts) + \
                             sum(dl.q_start * (dl.x_end - dl.x_start) * ((dl.x_start + dl.x_end)/2.0 - x1) for dl in dloads)
                R2 = M_loads_x1 / dist
                R1 = (sum(dl.q_start * (dl.x_end - dl.x_start) for dl in dloads) + sum(p.P for p in pts)) - R2
                for i, xi in enumerate(x):
                    curr_v, curr_m = 0.0, 0.0
                    if xi > x1:
                        curr_v += R1
                        curr_m += R1 * (xi - x1)
                    if xi > x2:
                        curr_v += R2
                        curr_m += R2 * (xi - x2)
                    for dl in dloads:
                        load_len = max(0, min(xi, dl.x_end) - dl.x_start)
                        if load_len > 0:
                            force = dl.q_start * load_len
                            arm = xi - (dl.x_start + load_len/2.0)
                            curr_v -= force
                            curr_m -= force * arm
                    for p in pts:
                        if xi > p.x:
                            curr_v -= p.P
                            curr_m -= p.P * (xi - p.x)
                    V[i], M[i] = curr_v, curr_m
        return {'V': V, 'M': M}

# Test Case: L=6, supports at 1 and 5, q=20
L = 6.0
sups = [BeamSupport(x=1.0), BeamSupport(x=5.0)]
dloads = [DistributedLoad(x_start=0.0, x_end=6.0, q_start=20000.0)]
res = ClassicalBeamSolver.generate_diagrams(L, dloads, [], sups)

print(f"V(0): {res['V'][0]}")
print(f"V(1.1): {res['V'][int(1.1/6*100)]}")
print(f"M(1.0): {res['M'][int(1.0/6*100)]}")
print(f"M(3.0): {res['M'][int(3.0/6*100)]}")
