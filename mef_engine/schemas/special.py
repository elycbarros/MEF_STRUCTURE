from pydantic import BaseModel
from typing import Optional

class SpecialElementRequest(BaseModel):
    type: str
    params: dict = {}

class BeamAnalysisRequest(BaseModel):
    spans: list[dict]
    loads: list[dict]
    material: dict

class ReservoirRequest(BaseModel):
    reservoir_type: str = "supported" # "supported", "elevated", "buried", "pool"
    dimensions: dict # { Lx, Ly, H }
    soil_params: Optional[dict] = None
    water_level: Optional[float] = None

class ColumnRequest(BaseModel):
    section_type: str = "rectangular"
    dimensions: dict # { b, h }
    length: float
    loads: dict # { Nd, Mdx, Mdy }
    material: dict # { fck, fyk }
