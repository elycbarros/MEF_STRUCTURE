import sys
from beam_solver import run_beam_analysis

def test_moment_load():
    # Simple bi-supported beam of 6m, with a concentrated moment of 50 kNm at x = 3.0m
    print("Testing beam with concentrated moment load...")
    res = run_beam_analysis(
        L=6.0,
        supports=[
            {'x': 0.0, 'type': 'pinned'},
            {'x': 6.0, 'type': 'pinned'}
        ],
        distributed_loads=[],
        point_loads=[
            {'x': 3.0, 'P': 0.0, 'M': 50.0} # 50 kNm moment at midspan
        ],
        b=0.20, h=0.50, fck=30,
        nonlinear=False,
        include_self_weight=False
    )
    
    print("\n--- RESULTS ---")
    print("FEM Max Deflection:", res['summary']['max_deflection_mm'], "mm")
    print("FEM Max Moment:", res['summary']['max_moment_kNm'], "kNm")
    print("FEM Max Shear:", res['summary']['max_shear_kN'], "kN")
    print("FEM Reactions:", res['reactions'])
    
    print("\n--- CLASSICAL RESULTS ---")
    classical = res['classical_diagrams']
    print("Classical Max Moment:", classical['max_moment_kNm'], "kNm")
    print("Classical Max Shear:", classical['max_shear_kN'], "kN")
    print("Classical Reactions:", classical['reactions'])
    
    print("\nFEM Bending Moment values:")
    for pt in res['diagrams']['moment']:
        print(f"x={pt['x']:.3f}: M={pt['y']:.3f} kNm")

    print("\nClassical Bending Moment values:")
    for i, x_val in enumerate(classical['x_m']):
        print(f"x={x_val:.3f}: M={classical['M_kNm'][i]:.3f} kNm")

if __name__ == '__main__':
    test_moment_load()
