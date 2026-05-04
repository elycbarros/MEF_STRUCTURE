from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import sys
from unittest.mock import MagicMock

@dataclass
class Beam:
    id: str
    node1_id: int
    node2_id: int
    b: float = 0.30  # m
    d: float = 0.50  # m
    xUDL: float = 0.0
    yUDL: float = 0.0
    zUDL: float = 0.0

class StrucPyAdapter:
    """
    Adapter to interface between MEF Structural domain models and StrucPy library.
    
    Coordinate Mapping:
    - MEF Structural (x, y, z_height) -> StrucPy (x, z, y)
    Note: StrucPy uses 'y' as the vertical axis.
    """

    @staticmethod
    def init_env():
        """
        Initializes the environment, mocking Ray if it fails or if on Python 3.14
        to avoid dashboard initialization errors.
        """
        try:
            # If we are on Python 3.14, Ray 2.x dashboard often fails due to Pydantic v1 issues
            if sys.version_info >= (3, 14):
                raise ImportError("Force mock on 3.14")
            import ray
            if not ray.is_initialized():
                ray.init(include_dashboard=False, ignore_reinit_error=True)
        except (ImportError, Exception):
            if 'ray' not in sys.modules:
                mock_ray = MagicMock()
                
                class RemoteWrapper:
                    def __init__(self, func):
                        self.func = func
                    def remote(self, *args, **kwargs):
                        return self.func(*args, **kwargs)
                    def __call__(self, *args, **kwargs):
                        return self.func(*args, **kwargs)

                def mock_remote(*args, **kwargs):
                    if len(args) == 1 and callable(args[0]):
                        return RemoteWrapper(args[0])
                    return lambda f: RemoteWrapper(f)

                mock_ray.remote = mock_remote
                mock_ray.get = lambda x: x
                mock_ray.put = lambda x: x
                mock_ray.init = lambda **kwargs: None
                sys.modules['ray'] = mock_ray
    
    @staticmethod
    def create_nodes_df(nodes: List[Dict[str, float]]) -> pd.DataFrame:
        if not nodes:
            return pd.DataFrame(columns=['x', 'y', 'z'], index=pd.Index([], dtype='int64'))
        data = []
        for n in nodes:
            data.append({
                'node': n['id'],
                'x': n['x'],
                'y': n['z'],  # Height
                'z': n['y']
            })
        df = pd.DataFrame(data)
        df.set_index('node', inplace=True)
        return df[['x', 'y', 'z']]

    @staticmethod
    def create_members_df(beams: List[Beam]) -> pd.DataFrame:
        if not beams:
            return pd.DataFrame(columns=['Node1', 'Node2', 'b', 'd', 'xUDL', 'yUDL', 'zUDL'], index=pd.Index([], dtype='int64'))
        data = []
        for b in beams:
            data.append({
                'Node1': b.node1_id,
                'Node2': b.node2_id,
                'b': b.b * 1000.0,  # mm
                'd': b.d * 1000.0,  # mm
                'xUDL': b.xUDL,
                'yUDL': b.yUDL,
                'zUDL': b.zUDL
            })
        df = pd.DataFrame(data)
        df.index = df.index + 1
        return df[['Node1', 'Node2', 'b', 'd', 'xUDL', 'yUDL', 'zUDL']]

    @staticmethod
    def create_supports_df(supports: List[Dict[str, Any]]) -> pd.DataFrame:
        if not supports:
            return pd.DataFrame(columns=['x', 'y', 'z', 'thetax', 'thetay', 'thetaz'], index=pd.Index([], dtype='int64'))
        data = []
        for s in supports:
            data.append({
                'node': s['node_id'],
                'x': s.get('tx', 1),
                'y': s.get('ty', 1),
                'z': s.get('tz', 1),
                'thetax': s.get('rx', 1),
                'thetay': s.get('ry', 1),
                'thetaz': s.get('rz', 1)
            })
        df = pd.DataFrame(data)
        df.set_index('node', inplace=True)
        return df

    @classmethod
    def run_frame_analysis(cls, nodes, beams, supports, grade_conc=30):
        cls.init_env()
        from StrucPy.RCFA import RCF
        
        nodes_df = cls.create_nodes_df(nodes)
        members_df = cls.create_members_df(beams)
        supports_df = cls.create_supports_df(supports)
        
        # Initialize StrucPy RCF
        frame = RCF(
            nodes_details=nodes_df,
            member_details=members_df,
            boundarycondition=supports_df,
            grade_conc=grade_conc,
            self_weight=True
        )
        
        # Mandatory flow for StrucPy
        frame.preP()
        frame.RCanalysis()
        
        return frame

    @staticmethod
    def get_member_forces(frame: RCF) -> pd.DataFrame:
        """
        Extracts member forces (N, V, M) from the analyzed frame.
        """
        # Based on docs/source, frame.memF() returns internal forces
        return frame.memF()

    @staticmethod
    def get_nodal_displacements(frame: RCF) -> pd.DataFrame:
        """
        Extracts nodal displacements.
        """
        return frame.Gdisp()

    @staticmethod
    def get_design_results(frame: RCF) -> Dict[str, pd.DataFrame]:
        """
        Extracts RC design results for beams and columns.
        """
        return {
            'beams': frame.beamsD(),
            'columns': frame.columnsD()
        }

    @staticmethod
    def get_3d_model_data(frame: RCF):
        """
        Prepares data for 3D visualization.
        """
        return {
            'nodes': frame.modelND(),
            'members': frame.modelMD()
        }
