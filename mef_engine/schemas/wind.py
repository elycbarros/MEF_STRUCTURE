from pydantic import BaseModel, Field
from typing import Optional

class WindRequest(BaseModel):
    v0: float = Field(30.0, ge=1.0, le=80.0, description="Velocidade básica do vento (m/s)")
    altura_total: float = Field(15.0, gt=1.0, le=800.0, description="Altura total da estrutura (m)")
    largura: float = Field(1.0, gt=0.1, le=300.0, description="Largura exposta ao vento (m)")
    profundidade: Optional[float] = Field(None, gt=0.1, le=300.0, description="Profundidade da estrutura (m)")
    step: float = Field(1.0, gt=0.1, le=20.0, description="Incremento vertical para discretização do vento (m)")
    cf: Optional[float] = Field(None, ge=0.0, le=5.0, description="Coeficiente de força aerodinâmico")
    area_por_nivel_m2: Optional[float] = Field(None, gt=0.0, le=10000.0, description="Área tributária por nível (m²)")
    s1: float = Field(1.0, gt=0.0, le=2.0, description="Fator topográfico S1")
    s3: float = Field(1.0, gt=0.0, le=2.0, description="Fator estatístico S3")
    categoria: int = Field(2, ge=1, le=5, description="Categoria de rugosidade NBR 6123")
    classe: str = 'B'
    is_dynamic: bool = False
    f1: float = Field(0.5, gt=0.01, le=10.0, description="Frequência fundamental (Hz)")
    zeta: float = Field(0.01, ge=0.001, le=0.20, description="Razão de amortecimento")
    beta: float = Field(1.0, gt=0.0, le=5.0, description="Fator modal/dinâmico auxiliar")

class WindStabilityRequest(WindRequest):
    total_p_kN: float = Field(10000.0, gt=0.0, le=1.0e7, description="Carga vertical total da estrutura (kN)")
    m1_kNm: Optional[float] = Field(None, description="Momento de primeira ordem informado (kNm)")
