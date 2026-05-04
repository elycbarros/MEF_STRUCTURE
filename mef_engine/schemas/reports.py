from pydantic import BaseModel
from typing import Optional

class ExportPDFRequest(BaseModel):
    results: dict
    project_meta: dict
    wind_results: Optional[dict] = None
    stability_results: Optional[dict] = None

class VigaCrossPDFRequest(BaseModel):
    results: dict # CrossSolveResult
    input_data: dict # BeamInput
    project_meta: Optional[dict] = None
