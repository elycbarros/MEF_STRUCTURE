from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from schemas.common import PillarInput, HoleInput, BeamInput, LineSupportInput, AreaLoadInput

class ConfigInput(BaseModel):
    Lx: float = Field(32.5, gt=0.5, le=500.0, description="Comprimento X do radier/laje (m)")
    Ly: float = Field(24.8, gt=0.5, le=500.0, description="Comprimento Y do radier/laje (m)")
    h: float = Field(1.15, gt=0.05, le=5.0, description="Espessura do radier/laje (m)")
    kv: float = Field(22.1e6, ge=1.0e5, le=1.0e9, description="Coeficiente de reação vertical do solo (N/m³)")
    q: float = Field(140e3, ge=0.0, le=5.0e6, description="Carga distribuída vertical (Pa = N/m²)")
    sigma_adm_kPa: float = Field(200.0, gt=1.0, le=5000.0, description="Tensão admissível do solo (kPa)")
    fck: float = Field(30.0, ge=10.0, le=120.0, description="Resistência característica do concreto (MPa)")
    fyk: float = Field(500.0, ge=250.0, le=700.0, description="Resistência característica do aço (MPa)")
    pillars: Optional[list[PillarInput]] = None
    columns_csv: Optional[str] = None
    measurements_csv: Optional[str] = None
    analysis_mode: str = "manual"
    foundation_type: str = "smooth"
    purpose_preset_id: Optional[str] = None
    soil_preset_id: Optional[str] = None
    field_risk_ids: list[str] = []
    guided_context: Optional[dict[str, Any]] = None
    diagnostic_conservatism: str = "balanced"
    ignore_pillars: bool = False
    soil_parameter_context: Optional[dict[str, Any]] = None
    system_type: str = "radier" # "radier" ou "laje"
    slab_type: str = "solid" # "solid", "ribbed", "hollow_core", "prestressed", "trussed"
    filler_type: str = "ceramic" # "ceramic", "eps"
    
    # Parâmetros Especiais de Lajes
    b_nerv: float = Field(0.10, ge=0.05, le=0.30, description="Largura da nervura (m)")
    dist_nerv: float = Field(0.50, ge=0.30, le=1.50, description="Distância entre eixos das nervuras (m)")
    h_mesa: float = Field(0.05, ge=0.03, le=0.15, description="Espessura da mesa da nervurada (m)")
    area_voids: float = Field(0.04, ge=0.01, le=0.20, description="Área de vazios da laje alveolar (m²)")
    p_force: float = Field(200.0, ge=10.0, le=5000.0, description="Força de protensão (kN)")
    ecc: float = Field(0.05, ge=0.01, le=0.50, description="Excentricidade do cabo (m)")
    
    # Novas opções para o solver de lajes
    supports: Optional[list[PillarInput]] = None
    line_supports: Optional[list[LineSupportInput]] = None
    holes: Optional[list[HoleInput]] = None
    beams: Optional[list[BeamInput]] = None
    area_loads: Optional[list[AreaLoadInput]] = None
    slab_mesh_size: float = Field(0.5, gt=0.05, le=5.0, description="Tamanho alvo da malha de laje (m)")
    # Wind & Stability
    wind_v0: Optional[float] = Field(30.0, ge=0.0, le=80.0, description="Velocidade básica do vento (m/s)")
    wind_categoria: Optional[int] = Field(2, ge=1, le=5, description="Categoria de rugosidade NBR 6123")
    wind_f1_hz: Optional[float] = Field(0.5, gt=0.01, le=10.0, description="Frequência fundamental da estrutura (Hz)")
    wind_zeta: Optional[float] = Field(0.01, ge=0.001, le=0.20, description="Razão de amortecimento estrutural")
    wind_is_dynamic: bool = False
    num_floors: int = Field(10, ge=1, le=200, description="Número de pavimentos")
    pillar_height: float = Field(3.0, gt=1.0, le=8.0, description="Altura típica de pilar/pavimento (m)")
    enable_analytical_comparison: bool = True

    @field_validator("kv")
    @classmethod
    def validate_kv_units(cls, value: float) -> float:
        if value < 1.0e5:
            raise ValueError("kv deve ser informado em N/m³; valores em kN/m³ ou MN/m³ sem conversão parecem incorretos")
        return value
    
class EstimateLoadsRequest(BaseModel):
    n_floors: int = 1
    area_per_floor: float = 100.0
    use_type: str = "residential" # "residential", "commercial", "industrial"
    config: Optional[ConfigInput] = None

class CoreAnalysisRequest(BaseModel):
    core_type: str = "elevator" # "elevator", "staircase", "shear_wall"
    config: dict
    loads: Optional[dict] = None

class DesignOptimizationInput(BaseModel):
    current_h: float
    target_sigma: float
    config: Optional[ConfigInput] = None

class AnalyticalComparisonResult(BaseModel):
    success: bool
    q_max_mef: float
    q_max_analytical: float
    ratio: float
    details: Optional[dict] = None
