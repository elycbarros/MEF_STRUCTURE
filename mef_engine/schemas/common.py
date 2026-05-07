from pydantic import BaseModel, Field
from typing import Optional

class PillarInput(BaseModel):
    id: str
    x: float = Field(..., description="Coordenada X do pilar (m)")
    y: float = Field(..., description="Coordenada Y do pilar (m)")
    p_kN: float = Field(..., ge=0.0, le=200000.0, description="Carga vertical característica/serviço no pilar (kN)")
    bx: float = Field(0.5, gt=0.05, le=5.0, description="Dimensão do pilar na direção X (m)")
    by: float = Field(0.5, gt=0.05, le=5.0, description="Dimensão do pilar na direção Y (m)")
    support_type: str = "pinned" # "pinned", "fixed", "spring"
    k_spring: float = Field(0.0, ge=0.0, description="Rigidez de mola quando support_type='spring' (N/m)")

class LineSupportInput(BaseModel):
    id: str
    x1: float = Field(..., description="Coordenada X inicial do apoio linear (m)")
    y1: float = Field(..., description="Coordenada Y inicial do apoio linear (m)")
    x2: float = Field(..., description="Coordenada X final do apoio linear (m)")
    y2: float = Field(..., description="Coordenada Y final do apoio linear (m)")
    support_type: str = "pinned"
    k_spring: float = Field(0.0, ge=0.0, description="Rigidez de mola do apoio linear (N/m)")

class BeamInput(BaseModel):
    id: str
    node1_id: int
    node2_id: int
    b: float = Field(0.30, gt=0.05, le=5.0, description="Largura da viga (m)")
    d: float = Field(0.50, gt=0.05, le=5.0, description="Altura da viga (m)")
    xUDL: float = Field(0.0, description="Carga distribuída local X (N/m)")
    yUDL: float = Field(0.0, description="Carga distribuída local Y (N/m)")
    zUDL: float = Field(0.0, description="Carga distribuída local Z (N/m)")

class HoleInput(BaseModel):
    x_min: float = Field(..., description="Coordenada X mínima da abertura (m)")
    y_min: float = Field(..., description="Coordenada Y mínima da abertura (m)")
    x_max: float = Field(..., description="Coordenada X máxima da abertura (m)")
    y_max: float = Field(..., description="Coordenada Y máxima da abertura (m)")

class AreaLoadInput(BaseModel):
    x_min: float = Field(..., description="Coordenada X mínima da carga (m)")
    y_min: float = Field(..., description="Coordenada Y mínima da carga (m)")
    x_max: float = Field(..., description="Coordenada X máxima da carga (m)")
    y_max: float = Field(..., description="Coordenada Y máxima da carga (m)")
    q_kN: float = Field(..., description="Valor da carga distribuída (kN/m²)")
