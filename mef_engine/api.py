from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from errors import StructuralError, StandardErrorResponse, ErrorCode, ErrorResponse

# Import modular routers
from routes import core, wind, stability, reports, elite, special, frame as frame_router, loads, phd, forensic, structural_rs
from persistence import persistence

app = FastAPI(
    title="MEF STRUCTURAL PH.D. ENGINE",
    description="Motores de Cálculo Autônomos e Inteligência Generativa (V6.0.0-PHD)",
    version="6.0.0"
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
app.include_router(core.router)
app.include_router(wind.router)
app.include_router(stability.router)
app.include_router(reports.router)
app.include_router(elite.router)
app.include_router(special.router)
app.include_router(frame_router.router)   # C1: Frame 3D Premium (substitui StrucPy)
app.include_router(loads.router)
app.include_router(phd.router) # M5-PhD
app.include_router(forensic.router) # M5-Forensic
app.include_router(structural_rs.router, prefix="/rust")

@app.get("/")
async def root():
    return {
        "app": "MEF STRUCTURAL PH.D. ENGINE",
        "version": "6.0.0-PHD",
        "status": "online",
        "modules": ["Core", "Wind", "Stability", "Elite", "Reports", "Special", "Frame3D", "PhD-Autonomous", "RustCore", "TensionPro"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
