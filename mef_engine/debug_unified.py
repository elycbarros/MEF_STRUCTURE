
import os
import sys

# Adicionar o diretório atual ao sys.path para encontrar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mef_engine.radier_lab_v24 import LabConfig
from mef_engine.laje_lab_v2 import LajeLabV2Config, PillarSupport
from mef_engine.unified_pipeline import run_unified_analysis

def test_unified():
    pillars = [PillarSupport(id="P01", x=4.0, y=4.0, p_kN=2200.0, bx=0.5, by=0.5)]
    frame_cfg = LajeLabV2Config(Lx=32.5, Ly=24.8, pillars=pillars)
    radier_cfg = LabConfig(Lx=32.5, Ly=24.8, h=1.15, kv=22000, base_name="test_debug")
    
    # Criar diretório de output se não existir
    if not os.path.exists(radier_cfg.output_dir):
        os.makedirs(radier_cfg.output_dir)
        
    res = run_unified_analysis(frame_cfg, radier_cfg)
    
    print("\n=== TEST RESULT ===")
    print("Success:", res.get("success"))
    radier = res.get("radier", {})
    master = radier.get("master", {})
    print("Master keys:", list(master.keys()))
    print("Lx:", master.get("Lx"))
    print("Ly:", master.get("Ly"))
    print("h:", master.get("h"))
    print("kv:", master.get("kv"))

if __name__ == "__main__":
    test_unified()
