from __future__ import annotations

import os
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from log_config import get_logger

logger = get_logger(__name__)

from radier_utils import read_json, sanitize_for_json
from schemas.core import ConfigInput, DesignOptimizationInput
from slab_lab import Hole, LineSupport, PillarSupport, SlabConfig, SlabLab

from routes.core_helpers import (
    build_executive_decision_summary,
    build_field_risk_summary,
    build_foundation_recommendation,
    build_regional_reinforcement_map,
    build_reinforcement_summary,
    build_solution_comparison,
    build_thermal_checklist,
    build_winkler_consistency,
)


class SlabEngineWrapper:
    config: SlabConfig

    def __init__(self, input_data: ConfigInput) -> None:
        # Mapeia ConfigInput para SlabConfig
        data = input_data.model_dump()

        # Converte dicionários para objetos PillarSupport, LineSupport e Hole
        pillars = []
        for p in data.get('pillars', []) or []:
            pillars.append(
                PillarSupport(
                    id=str(p.get('id')),
                    x=float(p.get('x')),
                    y=float(p.get('y')),
                    bx=float(p.get('bx', 0.5)),
                    by=float(p.get('by', 0.5)),
                )
            )

        line_supports = []
        for ls in data.get('line_supports', []) or []:
            line_supports.append(
                LineSupport(
                    id=str(ls.get('id', 'LS')),
                    x1=float(ls.get('x1')),
                    y1=float(ls.get('y1')),
                    x2=float(ls.get('x2')),
                    y2=float(ls.get('y2')),
                )
            )

        holes = []
        for h in data.get('holes', []) or []:
            holes.append(
                Hole(
                    x_min=float(h.get('x_min')),
                    y_min=float(h.get('y_min')),
                    x_max=float(h.get('x_max')),
                    y_max=float(h.get('y_max')),
                )
            )

        self.config = SlabConfig(
            base_name=data.get('base_name', 'slab_project'),
            Lx=data.get('Lx', 6.0),
            Ly=data.get('Ly', 6.0),
            nx=data.get('nx', 21),
            ny=data.get('ny', 21),
            h=data.get('h', 0.15),
            fck=data.get('fck', 30.0),
            fyk=data.get('fyk', 500.0),
            cover=data.get('cover', 0.02),
            q_perm=data.get('q_perm', 1.5),
            q_acid=data.get('q_acid', 2.0),
            slab_type=data.get('slab_type', 'solid'),
            b_nerv=data.get('b_nerv', 0.10),
            dist_nerv=data.get('dist_nerv', 0.50),
            h_mesa=data.get('h_mesa', 0.05),
            area_voids=data.get('area_voids', 0.04),
            p_force=data.get('p_force', 200.0),
            ecc=data.get('ecc', 0.05),
            filler_type=data.get('filler_type', 'ceramic'),
            pillars=pillars,
            line_supports=line_supports,
            holes=holes,
        )

    def run_analysis(self) -> Any:
        lab = SlabLab(self.config)
        return lab.run_full_pipeline()


class RadierEngine:
    config: Any

    def __init__(self, input_data: ConfigInput) -> None:
        # Mapeia ConfigInput para RadierConfig
        import inspect

        from radier_lab_v24 import LabConfig as RadierConfig

        full_data = input_data.model_dump()

        if 'system_type' in full_data:
            full_data['module_name'] = full_data['system_type']

        valid_keys = set(inspect.signature(RadierConfig).parameters.keys())
        filtered_data = {k: v for k, v in full_data.items() if k in valid_keys}

        if 'Lx' in full_data:
            filtered_data['Lx'] = full_data['Lx']
        if 'Ly' in full_data:
            filtered_data['Ly'] = full_data['Ly']

        self.config = RadierConfig(**filtered_data)

    def run_analysis(self) -> dict:
        from radier_lab_v24 import run_full_pipeline_demo as run_radier_pipeline

        master_summary = run_radier_pipeline(self.config)

        out_dir = self.config.output_dir
        det_file = os.path.join(out_dir, f'{self.config.base_name}_deterministic_summary.json')
        memorial_file = os.path.join(out_dir, f'{self.config.base_name}_memorial_summary.json')

        results = {
            'master': master_summary,
            'deterministic_results': read_json(det_file) if os.path.exists(det_file) else {},
            'memorial': read_json(memorial_file) if os.path.exists(memorial_file) else {},
        }
        return results


class RadierAnalytical:
    input_data: ConfigInput

    def __init__(self, input_data: ConfigInput) -> None:
        self.input_data = input_data

    def run_comparison(self, mef_results: dict) -> dict:
        # Esta função agora é legada, os resultados vêm do memorial
        return mef_results.get('memorial', {}).get('comparativo_metodologias', {})


router = APIRouter(tags=['Mestre - Core'])


@router.post('/calculate')
async def calculate_radier(input_data: ConfigInput):
    """Main structural analysis engine for Radier foundations."""
    try:
        is_laje = input_data.system_type == 'laje'
        if is_laje:
            engine = SlabEngineWrapper(input_data)
        else:
            engine = RadierEngine(input_data)
        results = engine.run_analysis()

        # Step 2: Extract summaries and diagnostics
        field_risk = build_field_risk_summary(input_data)
        winkler = build_winkler_consistency(input_data, results.get('deterministic_results', {}))

        # Step 3: Analytical Comparison
        analytical_results = results.get('memorial', {}).get('comparativo_metodologias')

        # Se por algum motivo não estiver no memorial, tenta o fallback (mas agora deve estar sempre lá)
        if not analytical_results:
            try:
                analytical_engine = RadierAnalytical(input_data)
                analytical_results = analytical_engine.run_comparison(results)
            except Exception as e:
                logger.warning('Analytical comparison fallback failed: %s', e)

        # Step 4: Build Recommendations
        recommendation = build_foundation_recommendation(
            input_data, results.get('memorial', {}), results.get('deterministic_results', {}), field_risk, winkler
        )

        executive_decision = build_executive_decision_summary(recommendation)
        reinforcement = build_reinforcement_summary(results.get('memorial', {}), input_data)
        reinforcement_map = build_regional_reinforcement_map(results.get('memorial', {}), input_data)
        thermal = build_thermal_checklist(input_data)
        comparison = build_solution_comparison(input_data, recommendation)

        # Step 5: Consolidate Output
        final_output = {
            'success': True,
            'is_laje': is_laje,
            'master': results.get('master') if is_laje else results.get('master'),
            'deterministic': results.get('master', {}).get('mef_summary')
            if is_laje
            else results.get('deterministic_results'),
            'specialized': results.get('master', {}).get('specialized') if is_laje else None,
            'memorial': results.get('master', {}).get('memorial') if is_laje else results.get('memorial'),
            'field_risk_summary': field_risk,
            'winkler_consistency': winkler,
            'analytical_comparison': analytical_results,
            'foundation_recommendation': recommendation,
            'executive_decision': executive_decision,
            'reinforcement_summary': reinforcement,
            'reinforcement_map': reinforcement_map,
            'thermal_checklist': thermal,
            'solution_comparison': comparison,
            'timestamp': time.time(),
            'status': 'success',
        }

        return sanitize_for_json(final_output)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Radier analysis failed')
        raise HTTPException(status_code=500, detail=f'Analysis failed: {str(e)}')


@router.post('/estimate_loads')
async def estimate_loads_core(data: dict):
    """Preliminary load estimation based on NBR 6120 typical usage."""
    tipo_uso = data.get('tipo_uso', 'residencial')
    num_pavimentos = data.get('num_pavimentos', 1)

    # Valores típicos (kN/m2) incluindo peso próprio estimado
    loads = {'residencial': 12.0, 'comercial': 15.0, 'escritorio': 14.0, 'garagem': 10.0, 'laje_cobertura': 8.0}

    base_q = loads.get(tipo_uso, 12.0)
    total_q_kPa = base_q * num_pavimentos

    return {'success': True, 'estimated_q_kPa': total_q_kPa, 'num_pavimentos': num_pavimentos, 'tipo_uso': tipo_uso}


@router.post('/optimize_design')
async def optimize_design_core(input_data: DesignOptimizationInput):
    """Iterative genetic optimization to find minimum cost configuration (h, fck) that passes checks (deterministic or probabilistic)."""
    try:
        from structural_optimizer import GeneticOptimizer

        config = input_data.config or ConfigInput(Lx=6.0, Ly=6.0, h=input_data.current_h)
        is_laje = config.system_type == 'laje'
        area_m2 = config.Lx * config.Ly

        # Reduzir temporariamente a malha para acelerar iterações do otimizador genético
        orig_nx, orig_ny = config.nx, config.ny
        config.nx = min(config.nx, 9)
        config.ny = min(config.ny, 9)

        def validation_fn(h: float, fck: float) -> dict:
            if not input_data.enable_reliability_mode:
                cfg = config.model_copy(update={'h': h, 'fck': fck})
                try:
                    if is_laje:
                        engine = SlabEngineWrapper(cfg)
                        res = engine.run_analysis()
                        checks = res.get('sanity_checks', {})
                        valid = checks.get('flecha_ok', True) and checks.get('puncao_ok', True) and checks.get('geometria_ok', True)
                        steel_kg = res.get('master', {}).get('consumption', {}).get('steel_kg', 0.0)
                        max_w = res.get('master', {}).get('mef_summary', {}).get('w_max_mm', 0.0)
                    else:
                        from radier_lab_v24 import run_deterministic_fem, run_design_checks
                        radier_cfg = RadierEngine(cfg).config
                        det_file = run_deterministic_fem(radier_cfg)
                        det = read_json(det_file)
                        design_res = run_design_checks(radier_cfg)
                        
                        q_max = det.get('qsoil_max_kPa', 0.0)
                        valid_pressao = q_max <= (input_data.target_sigma or cfg.sigma_adm_kPa)
                        puncao_ok = True
                        if 'punching_check_file' in design_res:
                            import pandas as pd
                            df_punch = pd.read_csv(design_res['punching_check_file'])
                            if not df_punch.empty and 'atende' in df_punch.columns:
                                puncao_ok = bool(df_punch['atende'].all())
                        
                        recalque_max = det.get('w_max_mm', 0.0)
                        flecha_ok = recalque_max <= 50.0
                        valid = valid_pressao and puncao_ok and flecha_ok
                        steel_kg = design_res.get('reinforcement_metrics', {}).get('peso_total_aco_kg', 0.0)
                        max_w = recalque_max
                    
                    return {
                        'valid': valid,
                        'steel_kg': steel_kg,
                        'max_displacement_mm': max_w,
                        'reliability_beta': 4.0 if valid else 0.0,
                        'failure_probability': 0.0 if valid else 1.0
                    }
                except Exception:
                    return {'valid': False, 'steel_kg': 99999.0}
            else:
                import numpy as np
                from scipy.stats import norm
                
                n_samples = 15
                failures = 0
                displacement_list = []
                steel_list = []
                
                rng = np.random.default_rng(12345)
                
                for _ in range(n_samples):
                    sim_kv = max(1e5, float(rng.normal(config.kv, config.kv * input_data.kv_cov)))
                    sim_q = max(0.0, float(rng.normal(config.q, config.q * input_data.q_cov)))
                    
                    cfg = config.model_copy(update={'h': h, 'fck': fck, 'kv': sim_kv, 'q': sim_q})
                    try:
                        if is_laje:
                            engine = SlabEngineWrapper(cfg)
                            res = engine.run_analysis()
                            checks = res.get('sanity_checks', {})
                            is_valid = checks.get('flecha_ok', True) and checks.get('puncao_ok', True) and checks.get('geometria_ok', True)
                            steel_kg = res.get('master', {}).get('consumption', {}).get('steel_kg', 0.0)
                            max_w = res.get('master', {}).get('mef_summary', {}).get('w_max_mm', 0.0)
                        else:
                            from radier_lab_v24 import run_deterministic_fem, run_design_checks
                            radier_cfg = RadierEngine(cfg).config
                            det_file = run_deterministic_fem(radier_cfg)
                            det = read_json(det_file)
                            design_res = run_design_checks(radier_cfg)
                            
                            q_max = det.get('qsoil_max_kPa', 0.0)
                            valid_pressao = q_max <= (input_data.target_sigma or cfg.sigma_adm_kPa)
                            puncao_ok = True
                            if 'punching_check_file' in design_res:
                                import pandas as pd
                                df_punch = pd.read_csv(design_res['punching_check_file'])
                                if not df_punch.empty and 'atende' in df_punch.columns:
                                    puncao_ok = bool(df_punch['atende'].all())
                            
                            recalque_max = det.get('w_max_mm', 0.0)
                            flecha_ok = recalque_max <= 50.0
                            is_valid = valid_pressao and puncao_ok and flecha_ok
                            steel_kg = design_res.get('reinforcement_metrics', {}).get('peso_total_aco_kg', 0.0)
                            max_w = recalque_max
                            
                        if not is_valid:
                            failures += 1
                        displacement_list.append(max_w)
                        steel_list.append(steel_kg)
                    except Exception:
                        failures += 1
                
                p_failure = failures / n_samples
                p_adj = max(1e-5, min(1.0 - 1e-5, p_failure))
                try:
                    beta = float(-norm.ppf(p_adj))
                except Exception:
                    beta = 0.0
                
                is_valid_reliability = beta >= input_data.target_reliability_beta
                
                mean_steel = float(np.mean(steel_list)) if steel_list else 0.0
                mean_w = float(np.mean(displacement_list)) if displacement_list else 0.0
                
                return {
                    'valid': is_valid_reliability,
                    'steel_kg': mean_steel,
                    'max_displacement_mm': mean_w,
                    'reliability_beta': round(beta, 3),
                    'failure_probability': round(p_failure, 4)
                }

        # Instancia e roda o otimizador genético (pop_size=8, generations=5 para manter rápido via API)
        opt = GeneticOptimizer(pop_size=8, generations=5)
        best = opt.optimize_radier(area_m2=area_m2, validation_fn=validation_fn)

        # Restaurar a malha original na resposta para exibição
        config.nx = orig_nx
        config.ny = orig_ny

        return {
            'success': True,
            'suggested_h': best.h,
            'suggested_fck': best.fck,
            'estimated_cost_brl': round(best.cost, 2),
            'valid': best.valid,
            'steel_kg': best.metadata.get('steel_kg', 0.0) if best.metadata else 0.0,
            'max_displacement_mm': round(best.metadata.get('max_displacement_mm', 0.0), 3) if best.metadata else 0.0,
            'reliability_index_beta': best.metadata.get('reliability_beta', 0.0) if best.metadata else 0.0,
            'failure_probability': best.metadata.get('failure_probability', 0.0) if best.metadata else 0.0,
            'status': 'optimized' if best.valid else 'no_valid_configuration_found'
        }

    except Exception as e:
        logger.exception('Design optimization failed')
        raise HTTPException(status_code=500, detail=f'Analysis failed: {str(e)}')
