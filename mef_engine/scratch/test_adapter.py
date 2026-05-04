from strucpy_adapter import StrucPyAdapter, Beam
import pandas as pd

def test_adapter():
    # Define a simple 2D frame (Portal Frame)
    # Pillars: 3m height. Beam: 5m span.
    # Coordinates (x, y, z) -> StrucPy (x, z, y) where y is height
    nodes = [
        {'id': 1, 'x': 0.0, 'y': 0.0, 'z': 0.0}, # Foundation 1
        {'id': 2, 'x': 5.0, 'y': 0.0, 'z': 0.0}, # Foundation 2
        {'id': 3, 'x': 0.0, 'y': 0.0, 'z': 3.0}, # Top Left
        {'id': 4, 'x': 5.0, 'y': 0.0, 'z': 3.0}  # Top Right
    ]
    
    beams = [
        Beam(id='P1', node1_id=1, node2_id=3, b=0.3, d=0.3), # Pillar 1
        Beam(id='P2', node1_id=2, node2_id=4, b=0.3, d=0.3), # Pillar 2
        Beam(id='B1', node1_id=3, node2_id=4, b=0.3, d=0.5, yUDL=-10.0) # Beam with -10 kN/m load
    ]
    
    supports = [
        {'node_id': 1, 'tx': 1, 'ty': 1, 'tz': 1, 'rx': 1, 'ry': 1, 'rz': 1}, # Fixed
        {'node_id': 2, 'tx': 1, 'ty': 1, 'tz': 1, 'rx': 1, 'ry': 1, 'rz': 1}  # Fixed
    ]
    
    try:
        print("Starting analysis via Adapter...")
        frame = StrucPyAdapter.run_frame_analysis(nodes, beams, supports)
        print("✅ Analysis completed")
        
        forces = StrucPyAdapter.get_member_forces(frame)
        print(f"\nMembros analisados: {len(forces)}")
        
        # Checking RC Design
        print("\nChecking RC Design...")
        beams_rc = frame.beamsD()
        print("Beams RC Data:")
        print(beams_rc)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_adapter()
