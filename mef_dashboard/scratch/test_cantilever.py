import sys
import os

# Adiciona o diretório mef_engine ao path
sys.path.append(os.path.join(os.getcwd(), "..", "mef_engine"))

from beam_solver import run_beam_analysis

def test_cantilever():
    print("Testing Cantilever Beam...")
    # Left fixed, Right free
    L = 5.0
    supports = [
        {"x": 0.0, "type": "fixed", "k_vertical": 1e12},
        {"x": 5.0, "type": "free", "k_vertical": 0.0}
    ]
    loads = [{"x_start": 0.0, "x_end": 5.0, "q_start": 10.0}] # 10 kN/m
    
    try:
        res = run_beam_analysis(L=L, supports=supports, distributed_loads=loads, nonlinear=False)
        print(f"Success! Max Moment: {res['design']['M_max_neg_kNm']} kNm")
        print(f"Max Deflection: {res['summary']['max_deflection_mm']} mm")
    except Exception as e:
        print(f"Error: {e}")

def test_unstable():
    print("\nTesting Unstable Beam (Both Free)...")
    L = 5.0
    supports = [
        {"x": 0.0, "type": "free", "k_vertical": 0.0},
        {"x": 5.0, "type": "free", "k_vertical": 0.0}
    ]
    loads = [{"x_start": 0.0, "x_end": 5.0, "q_start": 10.0}]
    
    try:
        res = run_beam_analysis(L=L, supports=supports, distributed_loads=loads, nonlinear=False)
        print("Success? (Should have failed)")
    except Exception as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    test_cantilever()
    test_unstable()
