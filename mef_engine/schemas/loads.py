from pydantic import BaseModel, Field
from typing import Literal, Union, List


class LoadActionInput(BaseModel):
    name: str
    kind: Literal["permanent", "variable"] = "variable"
    value: Union[float, List[float]] = Field(..., description="Valor caracteristico (escalar ou vetor de esforcos)")
    category: Literal["residential", "commercial", "office", "roof", "wind", "snow"] = "residential"
    psi0: float = Field(0.5, ge=0.0, le=1.0)
    psi1: float = Field(0.4, ge=0.0, le=1.0)
    psi2: float = Field(0.3, ge=0.0, le=1.0)
    is_favorable: bool = Field(False, description="Se True, aplica gamma_g favoravel (1.0)")


class LoadCombinationRequest(BaseModel):
    actions: list[LoadActionInput]
    gamma_g_unfav: float = Field(1.4, ge=1.0, le=2.0)
    gamma_g_fav: float = Field(1.0, ge=0.8, le=1.2)
    gamma_q: float = Field(1.4, ge=1.0, le=2.0)
    special_situation: bool = Field(False, description="Se True, usa gammas para ELU Especial/Construcao")
