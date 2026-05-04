from pydantic import BaseModel
from typing import Optional

class ExportPDFRequest(BaseModel):
    results: dict
    project_meta: dict
    wind_results: Optional[dict] = None
    stability_results: Optional[dict] = None
