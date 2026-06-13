from __future__ import annotations

from pydantic import BaseModel, Field


class StabilityRequest(BaseModel):
    total_p_kN: float = Field(..., gt=0, description='Carga vertical total (kN)')
    height: float = Field(..., gt=0, description='Altura total (m)')
    m1_kNm: float = Field(..., ge=0, description='Momento de 1ª ordem (kNm)')
    wind_v0: float = Field(default=30.0, ge=5, le=60, description='Velocidade básica do vento (m/s)')
    f1_hz: float = Field(default=0.5, gt=0, le=10, description='Frequência fundamental (Hz)')
    total_h_force_kN: float = Field(default=0.0, ge=0, description='Força horizontal total (kN)')
    width_x: float = Field(default=20.0, gt=0, description='Largura exposta ao vento (m)')
    total_mass_kg: float = Field(default=0.0, ge=0, description='Massa total (kg) — 0 = estimativa automática')
