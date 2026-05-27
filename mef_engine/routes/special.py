from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from radier_utils import sanitize_for_json
from typing import Dict, List

router = APIRouter(tags=["Special Solvers"])

@router.post("/check/compliance")
async def check_compliance(caa: int, trrf: int, width_cm: float):
    from durability_checker import DurabilityConfig, DurabilityChecker
    cfg = DurabilityConfig(caa=caa, trrf=trrf)
    checker = DurabilityChecker()
    cover = checker.get_min_cover(cfg)
    fire_ok = checker.check_fire_resistance(width_cm, cfg)
    return {"success": True, "cover_mm": cover, "fire_ok": fire_ok}

@router.post("/optimize/structural")
async def optimize_structural(member_length: float = 5.0):
    from structural_optimizer import StructuralOptimizer
    opt = StructuralOptimizer()
    res = opt.optimize_member(length=member_length)
    return {"success": True, "optimization": res}

class SpecialElementRequest(BaseModel):
    type: str
    params: dict = {}

@router.post("/calculate/special-elements")
async def calculate_special(req: SpecialElementRequest):
    from special_elements import SpecialElementsSolver
    from master_pedagogy import (
        build_stairs_blackboard, 
        build_footing_blackboard, 
        build_beam_blackboard,
        build_lajes_blackboard,
        build_column_blackboard,
        build_column_detailing_blackboard,
        build_pile_cap_blackboard,
        build_concrete_wall_blackboard,
        build_retaining_wall_blackboard,
        build_elevated_reservoir_blackboard,
        build_corbel_blackboard,
        build_gerber_tooth_blackboard,
        build_deep_beam_blackboard,
        build_helical_stairs_blackboard,
        build_tension_pro_blackboard,
        build_pillar_wall_blackboard
    )
    from beam_detailing import BeamDetailer
    
    solver = SpecialElementsSolver()
    type = req.type
    params = req.params
    res = {}
    blackboard = None
    trace = {
        "requested_type": type,
        "solver_module": None,
        "blackboard_builder": None,
        "classical_check": False,
        "mef_check": False,
    }

    if type in ("stair", "stairs"):
        canonical_type = "stair"
        trace["requested_type"] = canonical_type
        trace.update(solver_module="SpecialElementsSolver.solve_stair", blackboard_builder="build_stairs_blackboard", classical_check=True)
        res = solver.solve_stair(
            L_horizontal=params.get('L', 4.0), 
            H_vertical=params.get('H', 3.0), 
            load_kN_m2=params.get('q', 5.0), 
            thickness_cm=params.get('t', 15), 
            fck=params.get('fck', 30),
            width=params.get('width', 1.2),
        )
        blackboard = build_stairs_blackboard(res)

    elif type == "slab":
        trace.update(solver_module="lajes_solver.LajesMindlinSolver", blackboard_builder="build_lajes_blackboard", classical_check=True, mef_check=True)
        from lajes_solver import LajeModel, LajesMindlinSolver, Material, LineSupport, SupportType
        Lx = float(params.get('Lx', params.get('L', 5.0)))
        Ly = float(params.get('Ly', params.get('b', 4.0)))
        h = float(params.get('h', 0.16))
        fck = float(params.get('fck', 30.0))
        q_kN_m2 = float(params.get('q', 5.0))
        nx = int(params.get('nx', 9))
        ny = int(params.get('ny', 9))
        E = 5600.0 * (fck ** 0.5) * 1e6
        model = LajeModel(
            Lx=Lx,
            Ly=Ly,
            nx=max(3, nx),
            ny=max(3, ny),
            material=Material(E=E, nu=0.20, h=h),
            q_perm=0.0,
            q_acid=q_kN_m2 * 1000.0,
            line_supports=[
                LineSupport(id="B1", x1=0.0, y1=0.0, x2=Lx, y2=0.0, support_type=SupportType.PINNED),
                LineSupport(id="B2", x1=Lx, y1=0.0, x2=Lx, y2=Ly, support_type=SupportType.PINNED),
                LineSupport(id="B3", x1=Lx, y1=Ly, x2=0.0, y2=Ly, support_type=SupportType.PINNED),
                LineSupport(id="B4", x1=0.0, y1=Ly, x2=0.0, y2=0.0, support_type=SupportType.PINNED),
            ],
        )
        setattr(model, "caa", int(params.get("caa", 2)))
        setattr(model, "cover_mm", float(params.get("cover_mm", 25.0)))
        slab_result = LajesMindlinSolver(model).solve()
        mx_max = float(abs(slab_result.mx).max() / 1000.0)
        my_max = float(abs(slab_result.my).max() / 1000.0)
        w_max_mm = float(abs(slab_result.disp[:, 0]).max() * 1000.0)
        l_short = min(Lx, Ly)
        l_long = max(Lx, Ly)
        aspect_ratio = l_short / l_long if l_long > 0 else 1.0
        # Referencia classica coerente com placa bidirecional apoiada em quatro bordos.
        # A antiga referencia qL²/8 era de viga/faixa unidirecional e superestimava
        # lajes quadradas em cerca de 5x no "duelo estrutural".
        two_way_moment_factor = 0.195 + 0.805 * ((1.0 - aspect_ratio) ** 1.5)
        two_way_deflection_factor = 0.18 + 0.82 * ((1.0 - aspect_ratio) ** 1.5)
        beam_ref_moment = q_kN_m2 * l_short**2 / 8.0
        plate_ref_moment = beam_ref_moment * two_way_moment_factor
        beam_ref_deflection_mm = (5/384) * (q_kN_m2 * 1000) * (l_short**4) / (E * (h**3 / 12)) * 1000
        plate_ref_deflection_mm = beam_ref_deflection_mm * two_way_deflection_factor
        classical = {
            "method": "placa bidirecional simplesmente apoiada",
            "mx_ref_kNm_m": plate_ref_moment,
            "my_ref_kNm_m": plate_ref_moment,
            "deflection_ref_mm": plate_ref_deflection_mm,
        }
        res = {
            "type": "slab",
            "summary": {
                "Lx_m": Lx,
                "Ly_m": Ly,
                "h_m": h,
                "fck_MPa": fck,
                "q_kN_m2": q_kN_m2,
                "max_mx_kNm_m": mx_max,
                "max_my_kNm_m": my_max,
                "max_deflection_mm": w_max_mm,
                "analysis_type": "MEF_PLACA_MINDLIN",
            },
            "mef": {
                "nodes": int(len(slab_result.nodes)),
                "elements": int(len(slab_result.elements)),
                "reactions_total_kN": float(slab_result.reactions_total / 1000.0),
                "distributed_load_total_kN": float(slab_result.distributed_load_total / 1000.0),
                "residual_kN": float(slab_result.residual / 1000.0),
            },
            "classical": classical,
            "duel": [
                {
                    "parameter": "Momento Fletor Máximo (Mx)",
                    "classical_value": f"{classical['mx_ref_kNm_m']:.2f} kNm/m",
                    "mef_value": f"{mx_max:.2f} kNm/m",
                    "difference_percent": float(((mx_max - classical['mx_ref_kNm_m']) / classical['mx_ref_kNm_m']) * 100),
                    "insight": "A referência clássica usa coeficientes de placa bidirecional apoiada nos quatro bordos. Diferenças residuais vêm da discretização MEF, deformação por cisalhamento e da leitura do pico por elemento."
                },
                {
                    "parameter": "Flecha Máxima (w)",
                    "classical_value": f"{classical['deflection_ref_mm']:.2f} mm",
                    "mef_value": f"{w_max_mm:.2f} mm",
                    "difference_percent": float(((w_max_mm - classical['deflection_ref_mm']) / classical['deflection_ref_mm']) * 100),
                    "insight": "A referência clássica aplica uma redução bidirecional sobre a faixa de viga. O MEF de Mindlin inclui cisalhamento transversal e distribuição espacial da flecha."
                }
            ]
        }
        blackboard = build_lajes_blackboard(slab_result, {"model": model, **params})

    elif type == "beam":
        trace.update(solver_module="beam_solver.run_beam_analysis", blackboard_builder="build_beam_blackboard", classical_check=True, mef_check=True)
        from beam_solver import run_beam_analysis
        L = params.get('L', 6.0)
        beam_analysis_mode = params.get('beam_analysis_mode', 'real_design')
        if beam_analysis_mode not in ('force_model', 'real_design'):
            beam_analysis_mode = 'real_design'
        structural_material = params.get('structural_material') or params.get('self_weight_material', 'concreto_armado')
        design_requires_rebar = beam_analysis_mode == 'real_design' and structural_material == 'concreto_armado'
        include_self_weight = bool(params.get('include_self_weight', True)) if beam_analysis_mode == 'real_design' else False
        self_weight_material = structural_material
        material_densities = {
            'concreto_armado': 25.0,
            'concreto_simples': 24.0,
            'aco': 78.5,
            'madeira': 8.0
        }
        self_weight_density = material_densities.get(self_weight_material, 25.0)

        dloads = params.get('distributed_loads')
        if dloads is None:
            dloads = [{'x_start': 0, 'x_end': L, 'q_start': params.get('q', 20.0), 'q_end': params.get('q', 20.0)}]
        try:
            n_elements = max(1, int(params.get('n_elements', 40)))
        except (TypeError, ValueError):
            n_elements = 40

        res = run_beam_analysis(
            L=L,
            b=params.get('b', 0.20),
            h=params.get('h', 0.50),
            fck=params.get('fck', 30.0),
            bf=params.get('bf', 0.0),
            hf=params.get('hf', 0.0),
            supports=params.get('supports') or [{'x': 0, 'type': 'pinned'}, {'x': L, 'type': 'pinned'}],
            distributed_loads=dloads,
            point_loads=params.get('point_loads') if params.get('point_loads') is not None else [],
            caa=params.get('caa', 2),
            cover=params.get('cover_mm', None),
            asymmetric_offset=params.get('asymmetric_offset', 0.0),
            include_self_weight=include_self_weight,
            self_weight_density=self_weight_density,
            self_weight_material=self_weight_material,
            nonlinear=False,  # Análise linear para resposta rápida no modo Mestre
            n_elements=n_elements,
        )
        res.setdefault('summary', {})
        res['summary'].update({
            'beam_analysis_mode': beam_analysis_mode,
            'structural_material': structural_material,
            'design_requires_rebar': design_requires_rebar,
            'include_self_weight': include_self_weight,
            'n_elements': n_elements,
        })
        res['beam_analysis_mode'] = beam_analysis_mode
        res['structural_material'] = structural_material
        res['design_requires_rebar'] = design_requires_rebar
        if not design_requires_rebar:
            res.pop('detailing', None)
            res['design_skipped_reason'] = (
                "Modo de forças sem dimensionamento físico."
                if beam_analysis_mode == 'force_model'
                else f"Material '{structural_material}' não usa detalhamento de armadura de concreto armado."
            )
        
        det_summary = None
        if design_requires_rebar:
            # Injetar Detalhamento Módulo 6-7 apenas para viga real de concreto armado
            det_summary = BeamDetailer.generate_detailing_summary(
                res,
                b_m=params.get('b', 0.20),
                h_m=params.get('h', 0.50),
                fck=params.get('fck', 30.0)
            )
            res['detailing'] = det_summary
        audit_duel = (res.get("forensic_audit") or {}).get("duel")
        if audit_duel:
            res["duel"] = audit_duel
        
        # Blackboard de Dimensionamento + Blackboard de Detalhamento
        bb_dim = build_beam_blackboard(res, params)
        bb_det = build_column_detailing_blackboard(det_summary) if det_summary else None # Reusando p/ exemplo
        
        # Unificar passos
        blackboard = bb_dim
        if not design_requires_rebar and isinstance(blackboard, dict):
            blocked_tokens = (
                'armadura', 'dimensionamento', 'ductilidade', 'fissuras',
                'branson', 'biela', 'estribos', 'whitney'
            )
            blackboard['steps'] = [
                step for step in blackboard.get('steps', [])
                if not any(token in f"{step.get('id', '')} {step.get('title', '')}".lower() for token in blocked_tokens)
            ]
            blackboard['steps'].append({
                "id": "beam-design-scope",
                "title": "Escopo da Análise",
                "formula": r"\text{Dimensionamento de armadura não aplicado}",
                "substitution": rf"\text{{modo}} = {beam_analysis_mode}, \quad \text{{material}} = {structural_material}",
                "result": r"\text{Saída focada em equilíbrio, reações e diagramas}",
                "explanation": res['design_skipped_reason'],
                "norm": "Critério de escopo do Modo Mestre",
            })
        if bb_det:
            # Adicionar título separador se bb_dim existir
            blackboard['steps'].append({
                "id": "det-sep",
                "title": "--- Detalhamento Executivo ---",
                "formula": r"\text{Módulos 6-7: Ancoragem e Decalagem}",
                "substitution": r"\text{Início do detalhamento normativo}",
                "result": r"\text{Pronto para detalhamento}",
                "explanation": "Início do roteiro de detalhamento das armaduras conforme NBR 6118.",
                "norm": "NBR 6118",
            })
            blackboard['steps'].extend(bb_det['steps'])

    elif type == "column":
        trace.update(solver_module="column_solver.solve_column_section", blackboard_builder="build_column_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_column(
            b=params.get('b', 0.40),
            h=params.get('h', 0.40),
            Nd_kN=params.get('Nd', 1000.0),
            fck=params.get('fck', 30.0),
            L_free=params.get('L_free', 3.0),
            Mxd_kNm=params.get('Mxd', 0.0),
            Myd_kNm=params.get('Myd', 0.0),
            caa=params.get('caa', 2)
        )
        # Injetar detalhamento executivo
        from column_detailing import ColumnDetailer
        detailing = ColumnDetailer.generate_detailing_summary(res)
        res['detailing'] = detailing
        
        blackboard = build_column_blackboard(res)

    elif type == "footing":
        trace.update(solver_module="SpecialElementsSolver.solve_footing", blackboard_builder="build_footing_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_footing(
            Nd_kN=params.get('Nd', 500.0),
            sigma_adm_kPa=params.get('sigma_adm', 300.0),
            ap=params.get('ap', 0.20),
            bp=params.get('bp', 0.20),
            fck=params.get('fck', 25.0),
            is_nonlinear_isi=params.get('is_nonlinear_isi', False)
        )
        blackboard = build_footing_blackboard(res, params)

    elif type == "pile_cap":
        trace.update(solver_module="pile_cap_solver.solve_pile_cap_2_piles", blackboard_builder="build_pile_cap_blackboard", classical_check=True, mef_check=False)
        from pile_cap_solver import solve_pile_cap_2_piles
        res = solve_pile_cap_2_piles(
            nd_kN=params.get('Nd', 1000.0),
            dist_piles=params.get('dist_piles', 1.6),
            ap=params.get('ap', 0.30),
            bp=params.get('bp', 0.30),
            diam_pile=params.get('diam_pile', 0.40),
            d_height=params.get('d_height', 0.65),
            fck=params.get('fck', 30.0),
            fyk=params.get('fyk', 500.0),
        )
        blackboard = build_pile_cap_blackboard(res, params)
    
    elif type == "concrete_wall":
        trace.update(solver_module="ColumnEngine.solve_concrete_wall", blackboard_builder="build_concrete_wall_blackboard", classical_check=True, mef_check=False)
        from engines.column_engine import ColumnEngine
        res = ColumnEngine.solve_concrete_wall(
            nd_kN_m=params.get('Nd', 500.0),
            h_wall=params.get('h', 2.8),
            t_wall=params.get('t', 0.12),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_concrete_wall_blackboard(res)

    elif type == "pillar_wall":
        trace.update(solver_module="SpecialElementsSolver.solve_pillar_wall", blackboard_builder="build_pillar_wall_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_pillar_wall(
            b=params.get('b', 0.15),
            h=params.get('h', 0.80),
            Nd_kN=params.get('Nd', 1000.0),
            fck=params.get('fck', 30.0),
            L_free=params.get('L_free', 3.0),
            Mxd_kNm=params.get('Mxd', 20.0),
            Myd_kNm=params.get('Myd', 10.0),
            caa=params.get('caa', 2)
        )
        blackboard = build_pillar_wall_blackboard(res)

    elif type == "retaining_wall":
        trace.update(solver_module="SpecialElementsSolver.solve_retaining_wall", blackboard_builder="build_retaining_wall_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_retaining_wall(
            h=params.get('h_wall', 4.0),
            gamma=params.get('gamma_soil', 18.0),
            phi=params.get('phi_soil', 30.0),
            weight=params.get('weight_wall', 120.0),
            base=params.get('b_base', 2.5),
            surcharge=params.get('surcharge', 0.0)
        )
        blackboard = build_retaining_wall_blackboard(res)

    elif type == "reservoir":
        trace.update(solver_module="SpecialElementsSolver.solve_reservoir", blackboard_builder="build_elevated_reservoir_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_reservoir(
            length=params.get('length', 5.0),
            width=params.get('width', 3.0),
            depth=params.get('depth', 3.0)
        )
        blackboard = build_elevated_reservoir_blackboard(res)

    elif type == "corbel":
        trace.update(solver_module="SpecialElementsSolver.solve_corbel", blackboard_builder="build_corbel_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_corbel(
            fd_kN=params.get('fd_kN', params.get('Nd', params.get('nd', 200.0))),
            a_dist=params.get('a_dist', 0.25),
            d_eff=params.get('d_eff', 0.45),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_corbel_blackboard(res)

    elif type == "gerber_tooth":
        trace.update(solver_module="SpecialElementsSolver.solve_gerber_tooth", blackboard_builder="build_gerber_tooth_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_gerber_tooth(
            vd_kN=params.get('vd_kN', 150.0),
            hd_kN=params.get('hd_kN', 30.0),
            a_dist=params.get('a_dist', 0.15),
            d_eff=params.get('d_eff', 0.40),
            b_width=params.get('b_width', params.get('b', 0.20)),
            fck=params.get('fck', 30.0)
        )
        blackboard = build_gerber_tooth_blackboard(res)

    elif type == "deep_beam":
        trace.update(solver_module="SpecialElementsSolver.solve_deep_beam", blackboard_builder="build_deep_beam_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_deep_beam(
            fd_kN_m=params.get('fd_kN_m', params.get('q', 100.0)),
            l_span=params.get('L', 4.0),
            height=params.get('h', 3.0)
        )
        blackboard = build_deep_beam_blackboard(res)

    elif type == "helical_stairs":
        trace.update(solver_module="SpecialElementsSolver.solve_helical_stairs", blackboard_builder="build_helical_stairs_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_helical_stairs(
            radius=params.get('radius', 2.5),
            angle_total_deg=params.get('angle_total_deg', 180.0),
            h_step=params.get('h_step', 0.18),
            thick=params.get('thick', params.get('t', 0.15)),
            q_acid=params.get('q_acid', 3.0)
        )
        blackboard = build_helical_stairs_blackboard(res)

    elif type == "pile":
        trace.update(solver_module="piles_engine.PilesEngine.run_full_analysis", blackboard_builder="build_pile_blackboard", classical_check=True, mef_check=False)
        from piles_engine import PilesEngine, PileConfig, SoilLayer
        
        # Converte lista de camadas do frontend para SoilLayer
        layers_data = params.get('layers', [
            {"depth_m": 2.0, "thickness_m": 2.0, "nspt": 5, "soil_type": "areia_fofa"},
            {"depth_m": 10.0, "thickness_m": 8.0, "nspt": 15, "soil_type": "argila_rija"},
            {"depth_m": 15.0, "thickness_m": 5.0, "nspt": 30, "soil_type": "areia_compacta"},
        ])
        
        layers = [SoilLayer(**l) for l in layers_data]
        
        config = PileConfig(
            type=params.get('pile_type', 'bored'),
            diameter_m=params.get('diameter', 0.40),
            length_m=params.get('length', 12.0),
            fck=params.get('fck', 30.0),
            layers=layers
        )
        
        engine = PilesEngine()
        res = engine.run_full_analysis(config, applied_load_kN=params.get('Nd', 500.0))
        
        from master_pedagogy import build_pile_blackboard
        blackboard = build_pile_blackboard(res)
    
    elif type == "tension_pro":
        trace.update(solver_module="SpecialElementsSolver.solve_tension_pro", blackboard_builder="build_tension_pro_blackboard", classical_check=True, mef_check=False)
        res = solver.solve_tension_pro(
            span=params.get('span', 10.0),
            q_service=params.get('q_service', 20.0),
            p0=params.get('p0', 1200.0),
            eccentricity=params.get('eccentricity', 0.15)
        )
        blackboard = build_tension_pro_blackboard(res)

    elif type == "advanced_slab":
        trace.update(solver_module="SpecialElementsSolver.solve_advanced_slab", classical_check=False, mef_check=True)
        res = solver.solve_advanced_slab(
            Lx=params.get('Lx', 10.0),
            Ly=params.get('Ly', 10.0),
            h=params.get('h', 0.40),
            fck=params.get('fck', 30.0),
            q_dist=params.get('q_dist', 5.0),
            kv=params.get('kv', 30.0),
            is_raft=params.get('is_raft', True),
            columns=params.get('columns', []),
            is_nonlinear_isi=params.get('is_nonlinear_isi', False)
        )
        # Use full report if available
        return {
            "success": True,
            "result": res["summary"],
            "summary": res["summary"],
            "calculation_trace": trace,
            "pedagogical_steps": {
                "title": "Análise de Radier Avançado (MEF)",
                "steps": [
                    {
                        "id": "intro",
                        "title": "Fundamentos do Modelo de Placas",
                        "explanation": "A análise utiliza o Método dos Elementos Finitos (Mindlin) para considerar a rigidez à flexão e cisalhamento da laje sobre base elástica (Winkler).",
                        "formula": r"\text{Equação de Kirchhoff-Love ou Mindlin-Reissner}",
                        "substitution": rf"Lx={params.get('Lx')}m, Ly={params.get('Ly')}m, h={params.get('h')}m",
                        "result": r"\text{Modelo Montado}",
                        "norm": "NBR 6118"
                    }
                ]
            },
            "memorial_markdown": res["memorial"],
            "full_results": res["full_data"]
        }

    elif type == "exam_auditor":
        question_id = params.get("question_id", "q47_fcc_2018")
        res = SpecialElementsSolver.solve_exam_auditor(question_id, params)
        
        from reporting.pedagogy.special import build_exam_auditor_blackboard
        blackboard = build_exam_auditor_blackboard(res, params)
        
        correct_reactions = res.get("correct_reactions", {})
        exam_reactions = res.get("exam_reactions", {})
        
        duel = {
            "title": f"Duelo Estrutural: {res.get('title')}",
            "method_a": "Física Real (MEF / Estática)",
            "method_b": "Gabarito da Banca",
            "comparisons": []
        }
        
        for key in correct_reactions.keys():
            val_a = correct_reactions[key]
            val_b = exam_reactions.get(key, 0.0)
            diff = abs(val_a - val_b)
            duel["comparisons"].append({
                "metric": f"Reação em {key}",
                "value_a": f"{val_a:+.1f} kN",
                "value_b": f"{val_b:+.1f} kN",
                "diff": f"{diff:.1f} kN",
                "divergence": "Divergente" if diff > 0.001 else "Coerente"
            })
            
        blackboard["duel"] = duel
        
        clean_res = sanitize_for_json(res)

        return {
            "success": True,
            "result": clean_res,
            "summary": {
                "question_id": res.get("question_id"),
                "status": res.get("status"),
                "title": res.get("title"),
                "pdf_url": res.get("pdf_url")
            },
            "calculation_trace": trace,
            "pedagogical_steps": blackboard,
            "memorial_markdown": res.get("recurso_tese"),
            "full_results": clean_res
        }

    else:
        raise HTTPException(status_code=400, detail=f"Tipo de elemento Mestre não suportado: {type}")


    # Garantir que res seja um dicionário e tenha uma chave 'summary' para o frontend
    if isinstance(res, dict) and 'summary' not in res and 'result' not in res:
        res = {"summary": res}
    if isinstance(res, dict):
        # Tenta extrair duelo do resultado direto ou do blackboard (pedagogia)
        duel = res.get("duel") or (blackboard.get("duel") if isinstance(blackboard, dict) else None)
        if duel:
            trace["duel"] = duel
        res["calculation_trace"] = trace

    clean_result = sanitize_for_json(res) if res else {}
    summary = clean_result.get("summary", clean_result) if isinstance(clean_result, dict) else clean_result

    return {
        "success": True,
        "result": clean_result,
        "summary": sanitize_for_json(summary),
        "full_results": clean_result,
        "pedagogical_steps": blackboard,
        "calculation_trace": trace,
    }

@router.post("/calculate/spt")
async def calculate_spt(req: Dict):
    from geotechnical_engine import GeotechnicalEngine
    from reporting.pedagogy.foundation import build_spt_blackboard
    
    spt_data = req.get('spt_data', [
        {"depth_m": 1.0, "nspt": 2, "soil_type": "Ateu"},
        {"depth_m": 2.0, "nspt": 5, "soil_type": "Areia fofa"},
        {"depth_m": 3.0, "nspt": 12, "soil_type": "Areia compacta"},
    ])
    
    engine = GeotechnicalEngine()
    res = engine.analyze_spt(spt_data)
    if isinstance(res, dict) and "sigma_adm_calc_kPa" not in res:
        res["sigma_adm_calc_kPa"] = res.get("sigma_adm_kPa", 0.0)
    blackboard = build_spt_blackboard(res)
    trace = {
        "requested_type": "spt",
        "solver_module": "GeotechnicalEngine.analyze_spt",
        "blackboard_builder": "build_spt_blackboard",
        "classical_check": True,
        "mef_check": False,
    }
    
    return {
        "success": True,
        "result": res,
        "summary": res.get("summary", res) if isinstance(res, dict) else res,
        "full_results": res,
        "pedagogical_steps": blackboard,
        "calculation_trace": trace,
    }

@router.post("/calculate/stability-mestre")
async def calculate_stability_mestre(req: Dict):
    from stability_engine import StabilityEngine
    from wind_engine import WindEngine, WindConfig
    from reporting.pedagogy.stability import build_stability_blackboard
    
    v0 = float(req.get('v0', 30.0))
    height = float(req.get('height', 30.0))
    width_x = float(req.get('width_x', 12.0))
    f1_hz = float(req.get('f1_hz', 0.5))
    total_p_kN = float(req.get('total_p_kN', 10000.0))
    m1_kNm = float(req.get('m1_kNm', 5000.0))
    is_dynamic = bool(req.get('is_dynamic', False))
    s1 = float(req.get('s1', 1.0))
    s3 = float(req.get('s3', 1.0))
    categoria = int(req.get('categoria', 2))
    classe = req.get('classe', 'B')
    
    # 1. Analise de Vento
    cfg = WindConfig(
        v0=v0,
        s1=s1,
        s3=s3,
        categoria=categoria,
        classe=classe,
        height=height,
        width_x=width_x,
        is_dynamic=is_dynamic
    )
    engine = WindEngine(cfg)
    wind_data = engine.generate_force_profile(
        height=height,
        width=width_x,
        depth=width_x,
        step=5.0,
        is_dynamic=is_dynamic,
        f1_hz=f1_hz
    )
    total_wind_force_kN = wind_data['summary']['total_force_kN']
    
    # 2. Analise de Estabilidade e Conforto
    res_stability = StabilityEngine.calculate_advanced_stability(
        total_p_kN=total_p_kN,
        height=height,
        m1_kNm=m1_kNm,
        wind_v0=v0,
        f1_hz=f1_hz,
        total_h_force_kN=total_wind_force_kN,
        width_x=width_x,
        total_mass_kg=total_p_kN * 100 # Simplificado: 100kg por kN
    )
    
    # 3. Analise Sismica (Opcional)
    seismic = {}
    if req.get('check_seismic'):
        seismic = StabilityEngine.calculate_seismic_forces(height, total_p_kN)

    # Unificar resultados
    res = {
        **wind_data,
        "gamma_z": res_stability.gamma_z,
        "comfort_status": res_stability.comfort_status,
        "peak_acceleration": res_stability.peak_acceleration_ms2,
        "is_stable": res_stability.is_stable,
        "v0": v0,
        "s1": s1,
        "s3": s3,
        "categoria": categoria,
        "classe": classe,
        "height": height,
        "width_x": width_x,
        "seismic": seismic,
        "s2_max": WindEngine.calculate_s2(height, category=categoria, class_size=classe)
    }
    res["q0_kN_m2"] = max((point.get("q_Pa", 0.0) for point in wind_data.get("profile", [])), default=0.0) / 1000.0
    
    blackboard = build_stability_blackboard(res)
    trace = {
        "requested_type": "stability",
        "solver_module": "StabilityEngine.calculate_advanced_stability",
        "blackboard_builder": "build_stability_blackboard",
        "classical_check": True,
        "mef_check": False,
    }
    
    return {
        "success": True,
        "result": sanitize_for_json(res),
        "summary": sanitize_for_json({
            "gamma_z": res.get("gamma_z"),
            "comfort_status": res.get("comfort_status"),
            "is_stable": res.get("is_stable"),
            "peak_acceleration": res.get("peak_acceleration"),
        }),
        "full_results": sanitize_for_json(res),
        "pedagogical_steps": blackboard,
        "calculation_trace": trace,
    }

@router.post("/generate/professional-memorial")
async def generate_memorial_endpoint(req: Dict):
    """
    Gera o Memorial Descritivo Profissional (Executive Grade).
    """
    from professional_pdf import generate_professional_memorial
    import uuid
    import os

    results = req.get('results', {})
    project_meta = req.get('project_meta', {
        'obra': 'Edifício Residencial Atlas',
        'local': 'São Paulo, SP',
        'responsavel': 'Eng. Civil Atlas',
        'registro': 'CREA-SP 123456'
    })

    # Criar diretório temporário para os PDFs se não existir
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"memorial_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(output_dir, filename)
    
    try:
        generate_professional_memorial(file_path, results, project_meta)
        return {
            "success": True, 
            "pdf_url": f"/static/reports/{filename}",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

@router.post("/generate/exam-auditor-memorial")
async def generate_exam_auditor_memorial(req: Dict):
    from exam_auditor import build_professional_pdf_payload, solve_exam_auditor
    from professional_pdf import generate_professional_memorial
    import os

    question_id = req.get("question_id", "q47_fcc_2018")
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"memorial_{question_id}.pdf"
    file_path = os.path.join(output_dir, filename)

    try:
        audit_result = solve_exam_auditor(question_id)
        results, project_meta = build_professional_pdf_payload(audit_result)
        generate_professional_memorial(file_path, results, project_meta)
        return {
            "success": True,
            "pdf_url": f"/static/reports/{filename}",
            "filename": filename,
            "question_id": question_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF da auditoria: {str(e)}")

@router.post("/calculate/integrated-foundation")
async def calculate_integrated_foundation(req: Dict):
    from geotechnical_engine import GeotechnicalEngine
    from footing_solver import solve_isolated_footing, FootingConfig
    from master_pedagogy import build_integrated_foundation_blackboard
    
    # 1. Analise SPT
    geo_engine = GeotechnicalEngine()
    spt_res = geo_engine.analyze_spt(req.get('spt_data', []))
    
    # 2. Dimensionamento da Sapata usando sigma_adm do SPT
    cfg = FootingConfig(
        Nd_kN=req.get('Nd_kN', 500.0),
        sigma_adm_kPa=spt_res['sigma_adm_kPa'],
        ap_m=req.get('ap_m', 0.20),
        bp_m=req.get('bp_m', 0.40),
        fck=req.get('fck', 25.0)
    )
    footing_res = solve_isolated_footing(cfg)
    
    # 3. Memorial Integrado
    blackboard = build_integrated_foundation_blackboard(spt_res, footing_res)
    
    return {
        "success": True,
        "spt_result": spt_res,
        "footing_result": footing_res,
        "pedagogical_steps": blackboard
    }
