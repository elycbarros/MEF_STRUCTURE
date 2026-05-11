from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from schemas.reports import ExportPDFRequest, VigaCrossPDFRequest
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/academic/beam")
async def export_academic_beam_pdf(request: BeamAnalysisRequest):
    try:
        from beam_solver import run_beam_analysis
        from master_pedagogy import build_beam_blackboard, build_detailing_blackboard
        from beam_detailing import BeamDetailer
        from academic_pdf import generate_academic_blackboard_pdf

        output_dir = "output_api"
        ensure_directory(output_dir)
        payload = request.model_dump()
        result = run_beam_analysis(**payload)
        blackboard = build_beam_blackboard(result, payload)
        
        # Integrar Detalhamento Módulo 6-7 no PDF
        det_summary = BeamDetailer.generate_detailing_summary(
            result.get("design", {}), 
            b_m=payload.get('b', 0.20), 
            h_m=payload.get('h', 0.50), 
            fck=payload.get('fck', 30.0)
        )
        det_steps = build_detailing_blackboard(det_summary).get("steps", [])
        
        # Adicionar separador e passos de detalhamento
        blackboard['steps'].append({
            "title": "--- Detalhamento Executivo ---",
            "latex": r"\text{NBR 6118: Ancoragem e Decalagem}",
            "description": "Início do roteiro de detalhamento das armaduras longitudinais."
        })
        blackboard['steps'].extend(det_steps)

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
        blackboard = build_column_blackboard({**design, "b": request.b, "h": request.h, "fck": request.fck}, request.model_dump())
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/vigacross/pdf")
async def export_vigacross_pdf(request: VigaCrossPDFRequest):
    try:
        from master_pedagogy import build_vigacross_blackboard
        from academic_pdf import generate_academic_blackboard_pdf

        output_dir = "output_api"
        ensure_directory(output_dir)
        
        # O blackboard da Viga Cross
        blackboard = build_vigacross_blackboard(request.results, request.input_data)
        
        # Preparar diagramas para o PDF
        raw_diagrams = request.results.get('diagrams', [])
        mef_diagrams = {
            'x_m': [p.get('x', 0) for p in raw_diagrams],
            'V_kN': [p.get('shear', 0) for p in raw_diagrams],
            'M_kNm': [p.get('moment', 0) for p in raw_diagrams],
            'delta_mm': [p.get('deflection', 0) for p in raw_diagrams]
        }

        pdf_path = os.path.join(output_dir, "viga_cross_memorial_tecnico.pdf")
        generate_academic_blackboard_pdf(
            pdf_path, 
            blackboard, 
            request.project_meta or {
                "disciplina": "Teoria das Estruturas",
                "professor": "Engine VIGA CROSS",
            }, 
            diagrams=mef_diagrams
        )
        
        return FileResponse(
            path=pdf_path,
            filename="viga_cross_memorial_tecnico.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/academic/spt")
async def export_academic_spt_pdf(req: dict):
    try:
        from geotechnical_engine import GeotechnicalEngine
        from master_pedagogy import build_spt_blackboard
        from academic_pdf import generate_academic_blackboard_pdf
        
        output_dir = "output_api"
        ensure_directory(output_dir)
        
        spt_data = req.get('spt_data', [])
        engine = GeotechnicalEngine()
        res = engine.analyze_spt(spt_data)
        blackboard = build_spt_blackboard(res)
        
        pdf_path = os.path.join(output_dir, "mestre_geotecnia_sondagem.pdf")
        generate_academic_blackboard_pdf(pdf_path, blackboard, {
            "disciplina": "Fundacoes e Geotecnia",
            "professor": "Engine MESTRE",
        })
        
        return FileResponse(path=pdf_path, filename="mestre_geotecnia_sondagem.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/academic/stability")
async def export_academic_stability_pdf(req: dict):
    try:
        from wind_engine import WindEngine, WindConfig
        from master_pedagogy import build_stability_blackboard
        from academic_pdf import generate_academic_blackboard_pdf
        
        output_dir = "output_api"
        ensure_directory(output_dir)
        
        cfg = WindConfig(v0=req.get('v0', 30.0), height=req.get('height', 30.0), width_x=req.get('width_x', 12.0))
        engine = WindEngine()
        wind_data = engine.calculate_dynamic_pressure(cfg)
        gamma_z = engine.estimate_gamma_z(cfg.height, 10000, 50)
        res = {**wind_data, "gamma_z": gamma_z}
        blackboard = build_stability_blackboard(res)
        
        pdf_path = os.path.join(output_dir, "mestre_estabilidade_vento.pdf")
        generate_academic_blackboard_pdf(pdf_path, blackboard, {
            "disciplina": "Sistemas Estruturais",
            "professor": "Engine MESTRE",
        })
        
        return FileResponse(path=pdf_path, filename="mestre_estabilidade_vento.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
