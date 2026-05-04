from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from schemas.reports import ExportPDFRequest
from schemas.elite import BeamAnalysisRequest, ColumnRequest
from radier_pdf import generate_radier_report_pdf
from radier_utils import ensure_directory
import os

router = APIRouter(tags=["Reports"])

@router.post("/export/pdf")
async def export_pdf(request: ExportPDFRequest):
    try:
        output_dir = "output_api"
        ensure_directory(output_dir)
        pdf_path = os.path.join(output_dir, "radier_report_professional.pdf")
        
        results = request.results
        if request.wind_results:
            results['wind_data'] = request.wind_results
        if request.stability_results:
            results['stability_data'] = request.stability_results
            
        generate_radier_report_pdf(pdf_path, results, request.project_meta)
        
        return FileResponse(
            path=pdf_path,
            filename="relatorio_radier_profissional.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/academic/beam")
async def export_academic_beam_pdf(request: BeamAnalysisRequest):
    try:
        from beam_solver import run_beam_analysis
        from master_pedagogy import build_beam_blackboard
        from academic_pdf import generate_academic_blackboard_pdf

        output_dir = "output_api"
        ensure_directory(output_dir)
        payload = request.model_dump()
        result = run_beam_analysis(**payload)
        blackboard = build_beam_blackboard(result, payload)
        pdf_path = os.path.join(output_dir, "engine_mestre_viga_memorial_pedagogico.pdf")
        generate_academic_blackboard_pdf(pdf_path, blackboard, {
            "disciplina": "Concreto Armado",
            "professor": "Engine MESTRE",
        }, diagrams=result.get('diagrams'), classical_diagrams=result.get('classical_diagrams'))
        return FileResponse(
            path=pdf_path,
            filename="engine_mestre_viga_memorial_pedagogico.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/academic/column")
async def export_academic_column_pdf(request: ColumnRequest):
    try:
        from column_solver import ColumnSection, ColumnLoads, solve_column_section
        from durability_checker import DurabilityChecker, DurabilityConfig
        from master_pedagogy import build_column_blackboard
        from academic_pdf import generate_academic_blackboard_pdf

        output_dir = "output_api"
        ensure_directory(output_dir)
        cover_m = request.cover if request.cover is not None else DurabilityChecker.get_min_cover(DurabilityConfig(caa=request.caa), "column") / 1000.0
        sec = ColumnSection(b=request.b, h=request.h, fck=request.fck, cover=cover_m, caa=request.caa, L_free=request.L_free)
        loads = ColumnLoads(Nd_kN=request.Nd_kN, Mxd_kNm=request.Mxd_kNm, Myd_kNm=request.Myd_kNm)
        design = solve_column_section(sec, loads)
        blackboard = build_column_blackboard(sec, loads, design)
        pdf_path = os.path.join(output_dir, "engine_mestre_pilar_memorial_pedagogico.pdf")
        generate_academic_blackboard_pdf(pdf_path, blackboard, {
            "disciplina": "Concreto Armado",
            "professor": "Engine MESTRE",
        })
        return FileResponse(
            path=pdf_path,
            filename="engine_mestre_pilar_memorial_pedagogico.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
