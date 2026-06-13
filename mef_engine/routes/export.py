import json
import os
import tempfile
import zipfile
from pathlib import Path

from bim_engine import BIMCoordinator, export_results_csv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix='/export', tags=['UFO - Export BIM'])


class ExportRequest(BaseModel):
    memorial: dict = {}
    results: dict = {}
    project_name: str = 'projeto'


@router.post('/bim-csv')
async def export_bim_csv(req: ExportRequest):
    try:
        tmpdir = tempfile.mkdtemp()
        csv_dir = export_results_csv(tmpdir, req.memorial, req.results)
        zip_path = os.path.join(tmpdir, f'{req.project_name}_bim.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for f in Path(csv_dir).glob('*.csv'):
                zf.write(str(f), f.name)
        with open(zip_path, 'rb') as f:
            content = f.read()
        import shutil

        shutil.rmtree(tmpdir)
        from fastapi.responses import Response

        return Response(
            content=content,
            media_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename={req.project_name}_bim.zip'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/bim-manifest')
async def export_bim_manifest(req: ExportRequest):
    try:
        tmpdir = tempfile.mkdtemp()

        # Cria um objeto config-like mínimo
        class ConfigLike:
            base_name = req.project_name
            module_name = req.memorial.get('system_type', 'radier')
            code_profile = 'NBR'
            Lx = req.memorial.get('Lx', 0)
            Ly = req.memorial.get('Ly', 0)
            h = req.memorial.get('h', 0)
            fck = req.memorial.get('fck', 30)

        coord = BIMCoordinator(tmpdir)
        path = coord.export_structural_manifest(ConfigLike(), req.results)
        with open(path) as f:
            manifest = json.load(f)
        import shutil

        from fastapi.responses import JSONResponse

        shutil.rmtree(tmpdir)
        return JSONResponse(manifest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
