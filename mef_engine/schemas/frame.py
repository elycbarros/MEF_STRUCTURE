from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FrameNodeInput(BaseModel):
    id: int
    x: float = Field(..., description="Coordenada global X do nó (m)")
    y: float = Field(..., description="Coordenada global Y do nó (m)")
    z: float = Field(..., ge=0.0, description="Coordenada global Z/altura do nó (m)")

class FrameSectionInput(BaseModel):
    b: float = Field(0.40, gt=0.05, le=5.0, description="Largura da seção (m)")
    h: float = Field(0.40, gt=0.05, le=5.0, description="Altura da seção (m)")
    E: float = Field(2.5e10, ge=1.0e9, le=1.0e12, description="Módulo de elasticidade longitudinal (Pa)")
    G: float = Field(1.0e10, ge=1.0e8, le=5.0e11, description="Módulo de cisalhamento (Pa)")

class FrameMemberInput(BaseModel):
    id: int
    node_i: int
    node_j: int
    section: FrameSectionInput
    type: str = "column"   # 'column' | 'beam'

class FrameLoadInput(BaseModel):
    node_id: int
    Fx: float = Field(0.0, description="Força nodal global X (N)")
    Fy: float = Field(0.0, description="Força nodal global Y (N)")
    Fz: float = Field(0.0, description="Força nodal global Z (N)")
    Mx: float = Field(0.0, description="Momento nodal global X (N.m)")
    My: float = Field(0.0, description="Momento nodal global Y (N.m)")
    Mz: float = Field(0.0, description="Momento nodal global Z (N.m)")

class FrameRequest(BaseModel):
    nodes: List[FrameNodeInput]
    members: List[FrameMemberInput]
    loads: List[FrameLoadInput]
    supports: Dict[int, List[int]]   # {node_id: [blocked_dofs 0-5]}
    use_p_delta: bool = True
    nbr_stiffness_reduction: bool = True
    wind_v0: float = Field(0.0, ge=0.0, le=80.0, description="Velocidade básica do vento (m/s); se > 0, adiciona vento NBR 6123")
    wind_categoria: int = Field(2, ge=1, le=5, description="Categoria de rugosidade NBR 6123")
    wind_cp: float = Field(0.8, ge=-3.0, le=3.0, description="Coeficiente aerodinâmico equivalente")
    wind_width_m: float = Field(5.0, gt=0.1, le=300.0, description="Largura tributária para vento (m)")
    n_floors_for_wind: int = Field(0, ge=0, le=200, description="Número de pavimentos para vento automático; 0 = não aplica")
    floor_height_m: float = Field(3.0, gt=1.0, le=8.0, description="Altura típica de pavimento (m)")
