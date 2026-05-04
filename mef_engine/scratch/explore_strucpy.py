import StrucPy
from StrucPy.RCFA import RCF
import pandas as pd

def explore():
    # Nodes: 3 columns, ID as index
    nodes_df = pd.DataFrame({
        'x': [0.0, 5.0, 0.0, 5.0],
        'y': [0.0, 0.0, 0.0, 0.0],
        'z': [0.0, 0.0, 3.0, 3.0]
    }, index=[1, 2, 3, 4])
    
    # Members: 7 columns
    members_df = pd.DataFrame({
        'Node1': [1, 2, 3],
        'Node2': [3, 4, 4],
        'b': [300, 300, 300],
        'd': [500, 500, 500],
        'xUDL': [0, 0, 0],
        'yUDL': [0, 0, 0],
        'zUDL': [0, 0, 0]
    }, index=[1, 2, 3])
    
    # Boundary Conditions: 6 columns, Index matches nodes
    supports_df = pd.DataFrame({
        'x': [1, 1], 'y': [1, 1], 'z': [1, 1],
        'thetax': [1, 1], 'thetay': [1, 1], 'thetaz': [1, 1]
    }, index=[1, 2])
    
    try:
        frame = RCF(nodes_df, members_df, supports_df)
        print("✅ Frame initialized successfully")
        
        # Analyze available methods
        methods = [m for m in dir(frame) if not m.startswith('_')]
        print("\nAvailable Public Methods in RCF:")
        for m in sorted(methods):
            print(f"- {m}")
            
    except Exception as e:
        print(f"❌ Error during RCF init: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explore()
