from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any, Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from errors import StructuralError, StandardErrorResponse, ErrorCode, ErrorResponse

# Import modular routers
from routes import core, wind, stability, reports, elite, special, frame as frame_router, loads, phd, forensic, structural_rs, mestre_frame, seismic, ssi, ufo_detailing
from persistence import persistence

app = FastAPI(
    title="ATLAS STRUCTURAL ENGINE — Pro Edition",
    description="""
### Motor MEF 3D de Alta Performance com Aceleração Rust

Bem-vindo à API do **Atlas Structural Engine**, o núcleo de inteligência estrutural da plataforma MEF STRUCTURAL.

#### Capacidades Principais:
*   **Análise de Pórtico 3D (C1)**: Elementos de barra 12-DOF com formulação Euler-Bernoulli refinada.
*   **Estabilidade Global (C2)**: Cálculo automático de Gama-Z e Alfa seguindo NBR 6118:2014.
*   **Não-Linearidade Geométrica**: Solver P-Delta iterativo com aceleração de Aitken para convergência rápida em grandes edifícios.
*   **Motor Híbrido Rust**: Montagem de matrizes em paralelo (Rayon) para modelos de alta complexidade (>10.000 DOFs).
*   **Auditoria de Equilíbrio (C3)**: Verificação de resíduos numéricos e equilíbrio global para garantia de segurança.

#### Modos de Operação:
1.  **Modo Mestre**: Didático e segmentado, focado em vigas, pilares e treliças isoladas.
2.  **Modo UFO**: Análise global de edifícios, integração solo-estrutura e efeitos de vento.

---
*Contato Técnico: Suporte de Engenharia — PhD Structural Lab*
""",
    version="6.2.0-ELITE"
)

# --- Endpoints de Gestão de Projetos (M5-Pleno) ---

@app.get("/projects")
async def list_projects():
    return {"projects": persistence.list_projects()}

@app.post("/projects")
async def create_project(data: dict):
    # data: {name, client, description}
    pid = persistence.create_project(
        name=data.get('name', 'Novo Projeto'),
        client=data.get('client', ''),
        description=data.get('description', '')
    )
    return {"project_id": pid, "status": "created"}

@app.get("/projects/{project_id}/history")
async def get_project_history(project_id: str):
    return {"history": persistence.get_project_history(project_id)}

# --- Middleware & Handlers ---

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StructuralError)
async def structural_exception_handler(request, exc: StructuralError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "type": exc.error_type,
                "message": exc.message,
                "detail": exc.detail,
                "module": exc.module
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VAL-002",
                "type": ErrorCode.INVALID_INPUT,
                "message": "Dados de entrada inválidos ou fora dos limites normativos.",
                "detail": str(exc.errors()),
                "module": "api_gateway"
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INT-500",
                "type": ErrorCode.INTERNAL_ERROR,
                "message": "Ocorreu um erro interno inesperado no servidor.",
                "detail": str(exc),
                "module": "system"
            }
        }
    )

# Include Modular Routers
# Note: tags and prefixes are defined within the routers for better organization
# --- MODO MESTRE (Análise Pedagógica e Segmentada) ---
mestre_prefix = "/api/mestre"
from routes import mestre_frame # New module
app.include_router(core.router, prefix=mestre_prefix)
app.include_router(mestre_frame.router, prefix=mestre_prefix)
app.include_router(phd.router, prefix=mestre_prefix)
app.include_router(reports.router, prefix=mestre_prefix)
app.include_router(loads.router, prefix=mestre_prefix)
app.include_router(special.router, prefix=mestre_prefix)

# --- MODO UFO (Análise Global e Auditoria Profissional) ---
ufo_prefix = "/api/ufo"
from routes import seismic, ssi, ufo_detailing # Import late to ensure file exists
app.include_router(frame_router.router, prefix=ufo_prefix) # C1: Frame 3D Premium
app.include_router(stability.router, prefix=ufo_prefix)
app.include_router(seismic.router, prefix=ufo_prefix)
app.include_router(ssi.router, prefix=ufo_prefix)
app.include_router(ufo_detailing.router, prefix=ufo_prefix)
app.include_router(elite.router, prefix=ufo_prefix)
app.include_router(forensic.router, prefix=ufo_prefix)
app.include_router(wind.router, prefix=ufo_prefix)
app.include_router(structural_rs.router, prefix="/rust")

# --- Custom Responses ---
try:
    import msgpack
    class MsgPackResponse(JSONResponse):
        media_type = "application/x-msgpack"
        def render(self, content: Any) -> bytes:
            # Recursively ensure content is msgpack compatible
            return msgpack.packb(content, use_bin_type=True)
except ImportError:
    msgpack = None

# --- Health & Info ---
@app.get("/api/health")
@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "ATLAS-6.2-ELITE", "version": "6.2.0-ELITE"}

@app.get("/api/info")
async def info():
    return {
        "app": "ATLAS STRUCTURAL ENGINE",
        "version": "6.2.0-ELITE",
        "capabilities": ["P-Delta", "Modal", "NBR6118-Serviceability", "Rust-Assembly", "MsgPack"]
    }

@app.get("/")
async def root():
    return {
        "app": "ATLAS STRUCTURAL ENGINE — Pro Edition",
        "version": "6.2.0-ELITE",
        "status": "online",
        "modules": ["Core", "Wind", "Stability", "Elite", "Reports", "Special", "Frame3D", "PhD-Autonomous", "RustCore", "TensionPro"]
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
