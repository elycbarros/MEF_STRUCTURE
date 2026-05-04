from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class EstimateLoadsRequest(BaseModel):
    tipo_uso: str = "residencial" # residencial, comercial, garagem, deposito, escritorio
    num_pavimentos: int = Field(1, ge=1, le=200, description="Número de pavimentos")

class BeamAnalysisRequest(BaseModel):
    L: float = Field(6.0, gt=0.2, le=100.0, description="Comprimento total da viga (m)")
    b: float = Field(0.20, gt=0.05, le=5.0, description="Largura da viga (m)")
    h: float = Field(0.50, gt=0.05, le=5.0, description="Altura da viga (m)")
    fck: float = Field(30.0, ge=10.0, le=120.0, description="Resistência característica do concreto (MPa)")
    caa: int = Field(2, ge=1, le=4, description="Classe de Agressividade Ambiental")
    cover: Optional[float] = Field(None, gt=0.0, le=0.20, description="Cobrimento nominal (m); se ausente, vem da CAA")
    supports: List[Dict] = [
        {"x": 0.0, "type": "pinned"},
        {"x": 6.0, "type": "pinned"},
    ]
    distributed_loads: Optional[List[Dict]] = None
    point_loads: Optional[List[Dict]] = None
    n_elements: int = Field(40, ge=2, le=500, description="Número de elementos finitos da viga")
    nonlinear: bool = True
    redistribution_delta: float = Field(0.90, ge=0.75, le=1.0, description="Fator de redistribuição de momentos")
    include_self_weight: bool = True
    gamma_f: float = Field(1.4, ge=1.0, le=2.0, description="Coeficiente de majoração das ações")

class CoreAnalysisRequest(BaseModel):
    building_Lx: float = Field(24.0, gt=1.0, le=500.0, description="Dimensão X da edificação (m)")
    building_Ly: float = Field(24.0, gt=1.0, le=500.0, description="Dimensão Y da edificação (m)")
    n_floors: int = Field(40, ge=1, le=200, description="Número de pavimentos")
    floor_height: float = Field(3.0, gt=1.0, le=8.0, description="Altura de pavimento (m)")
    floor_weight_kN: float = Field(5000.0, gt=0.0, le=1.0e7, description="Peso por pavimento (kN)")
    fck: float = Field(35.0, ge=10.0, le=120.0, description="Resistência característica do concreto (MPa)")
    elevator_shafts: Optional[List[Dict]] = None   # [{x0, y0, width, depth, wall_thickness, open_side}]
    stair_cores: Optional[List[Dict]] = None       # [{x0, y0, width, depth, wall_thickness}]
    shear_walls: Optional[List[Dict]] = None       # [{x0, y0, length, thickness, direction}]

class ReservoirRequest(BaseModel):
    name: str = 'RES_01'
    type: str = 'elevated'       # elevated, ground, buried, pool
    Lx: float = Field(5.0, gt=0.5, le=100.0, description="Comprimento X do reservatório (m)")
    Ly: float = Field(4.0, gt=0.5, le=100.0, description="Comprimento Y do reservatório (m)")
    H: float = Field(3.0, gt=0.2, le=50.0, description="Altura de água/parede (m)")
    wall_thickness: float = Field(0.20, gt=0.05, le=2.0, description="Espessura da parede (m)")
    slab_thickness: float = Field(0.20, gt=0.05, le=2.0, description="Espessura da laje (m)")
    fck: float = Field(30.0, ge=10.0, le=120.0, description="Resistência característica do concreto (MPa)")
    soil_depth: float = Field(0.0, ge=0.0, le=100.0, description="Altura de solo atuante (m)")
    soil_gamma: float = Field(18.0, gt=1.0, le=30.0, description="Peso específico do solo (kN/m³)")
    soil_ka: float = Field(0.33, ge=0.0, le=1.5, description="Coeficiente de empuxo ativo")

class ColumnRequest(BaseModel):
    b: float = Field(0.60, gt=0.05, le=5.0, description="Dimensão b do pilar (m)")
    h: float = Field(0.60, gt=0.05, le=5.0, description="Dimensão h do pilar (m)")
    fck: float = Field(40.0, ge=10.0, le=120.0, description="Resistência característica do concreto (MPa)")
    caa: int = Field(2, ge=1, le=4, description="Classe de Agressividade Ambiental")
    cover: Optional[float] = Field(None, gt=0.0, le=0.20, description="Cobrimento nominal (m); se ausente, vem da CAA")
    L_free: float = Field(3.0, gt=0.5, le=20.0, description="Comprimento livre do pilar (m)")
    Nd_kN: float = Field(5000.0, ge=0.0, le=1.0e7, description="Esforço normal de cálculo (kN)")
    Mxd_kNm: float = Field(0.0, description="Momento de cálculo em X (kNm)")
    Myd_kNm: float = Field(0.0, description="Momento de cálculo em Y (kNm)")
    n_floors_for_shortening: int = Field(40, ge=1, le=200, description="Número de pavimentos para estimativa de encurtamento")

class OptimizationRequest(BaseModel):
    project_id: str
    target: str = "cost" # cost, weight, carbon
    variables: List[str] = ["h", "fck"]
    constraints: Dict = {"w_max": 30.0, "sigma_adm": 200.0}
    population_size: int = 10
    generations: int = 5

class CopilotRequest(BaseModel):
    project_id: str
    analysis_type: str = "general" # general, cracking, efficiency, vibration
