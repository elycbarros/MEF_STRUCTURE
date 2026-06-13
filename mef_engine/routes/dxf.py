from dxf_engine import export_radier_dxf, export_slab_dxf
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix='/dxf', tags=['UFO - DXF Export'])


class SlabDXFRequest(BaseModel):
    Lx: float = Field(..., gt=0)
    Ly: float = Field(..., gt=0)
    x_bottom_cm: float = 12.5
    y_bottom_cm: float = 15.0
    x_top_cm: float = 20.0
    y_top_cm: float = 20.0
    x_bottom_phi: float = 10.0
    y_bottom_phi: float = 8.0
    x_top_phi: float = 10.0
    y_top_phi: float = 8.0
    x_bottom_as: float = 6.4
    y_bottom_as: float = 3.35
    x_top_as: float = 4.0
    y_top_as: float = 2.5


class RadierDXFRequest(BaseModel):
    Lx: float = Field(..., gt=0)
    Ly: float = Field(..., gt=0)
    h_m: float = 0.50
    cover_m: float = 0.04
    bottom_x_spacing: float = 15.0
    bottom_y_spacing: float = 15.0
    top_x_spacing: float = 20.0
    top_y_spacing: float = 20.0
    bottom_x_diameter: float = 12.5
    bottom_y_diameter: float = 12.5
    top_x_diameter: float = 10.0
    top_y_diameter: float = 10.0
    project: str = 'Radier'
    client: str = 'N/D'
    author: str = 'MEF STRUCTURAL'


@router.post('/slab')
async def generate_slab_dxf(req: SlabDXFRequest):
    import os
    import tempfile

    tmp = tempfile.NamedTemporaryFile(suffix='.dxf', delete=False)
    design_data = {
        'detailing': {
            'x_bottom': {
                'diameter_mm': req.x_bottom_phi,
                'spacing_cm': req.x_bottom_cm,
                'as_real_cm2': req.x_bottom_as,
            },
            'y_bottom': {
                'diameter_mm': req.y_bottom_phi,
                'spacing_cm': req.y_bottom_cm,
                'as_real_cm2': req.y_bottom_as,
            },
            'x_top': {'diameter_mm': req.x_top_phi, 'spacing_cm': req.x_top_cm, 'as_real_cm2': req.x_top_as},
            'y_top': {'diameter_mm': req.y_top_phi, 'spacing_cm': req.y_top_cm, 'as_real_cm2': req.y_top_as},
        }
    }
    path = export_slab_dxf(tmp.name, req.Lx, req.Ly, design_data)
    with open(path, 'rb') as f:
        content = f.read()
    os.unlink(path)
    from fastapi.responses import Response

    return Response(
        content=content, media_type='application/dxf', headers={'Content-Disposition': 'attachment; filename=slab.dxf'}
    )


@router.post('/radier')
async def generate_radier_dxf(req: RadierDXFRequest):
    import os
    import tempfile

    tmp = tempfile.NamedTemporaryFile(suffix='.dxf', delete=False)
    design_data = {
        'steel_details': {
            'bottom_x': {'spacing': req.bottom_x_spacing, 'diameter': req.bottom_x_diameter},
            'bottom_y': {'spacing': req.bottom_y_spacing, 'diameter': req.bottom_y_diameter},
            'top_x': {'spacing': req.top_x_spacing, 'diameter': req.top_x_diameter},
            'top_y': {'spacing': req.top_y_spacing, 'diameter': req.top_y_diameter},
        },
        'columns': [],
        'punching': [],
        'steel_list': [],
        'h_m': req.h_m,
        'cover_m': req.cover_m,
        'project': req.project,
        'client': req.client,
        'author': req.author,
    }
    path = export_radier_dxf(tmp.name, req.Lx, req.Ly, design_data)
    with open(path, 'rb') as f:
        content = f.read()
    os.unlink(path)
    from fastapi.responses import Response

    return Response(
        content=content,
        media_type='application/dxf',
        headers={'Content-Disposition': 'attachment; filename=radier.dxf'},
    )
