"""
wind_memorial.py - Memorial Markdown Padronizado para ações de vento NBR 6123.
"""
from __future__ import annotations
from typing import Any
from memorial_factory import build_unified_memorial
from platform_core import PLATFORM_VERSION, generate_payload_hash

def _fmt(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/d"

def build_wind_memorial(result: dict[str, Any]) -> str:
    p_hash = generate_payload_hash(result)
    config = result.get("config", {})
    summary = result.get("summary", {})
    geometry = result.get("geometry", {})
    
    hypotheses = [
        "Analise estatica e dinamica conforme NBR 6123:1988",
        "Consideracao de fatores topograficos (S1) e estatisticos (S3)",
        "Rugosidade do terreno via categorias (I a V)",
        "Modelo discreto para analise dinamica (edificios altos)"
    ]

    materials = {
        "Regiao": f"{config.get('v0', 30)} m/s (Velocidade Basica)",
        "S1 (Topografia)": config.get('s1', 1.0),
        "S3 (Estatistico)": config.get('s3', 1.0),
        "Categoria de Rugosidade": config.get('categoria', 2)
    }

    loads = {
        "Forca Total (Fk)": f"{_fmt(summary.get('total_force_kN', 0))} kN",
        "Momento na Base (Mk)": f"{_fmt(summary.get('base_moment_kNm', 0))} kNm",
        "Pressao Dinamica Maxima": f"{_fmt(summary.get('max_q_Pa', 0))} Pa"
    }

    combinations = [
        "Vento como acao variavel principal ou secundaria",
        "Fator psi_0 conforme NBR 8681"
    ]

    model_details = {
        "Altura do Edificio": f"{_fmt(geometry.get('height_m', 0))} m",
        "Largura Exposta": f"{_fmt(geometry.get('width_m', 0))} m",
        "Coeficiente de Arrasto (Cf)": _fmt(geometry.get('cf', 0)),
        "Analise Dinamica": "SIM" if config.get('is_dynamic') else "NAO"
    }

    results_summary = {
        "Forca de Pico por Nivel": f"{_fmt(summary.get('max_force_level_kN', 0))} kN",
        "Fator de Amplificacao Dinamica": _fmt(config.get('zeta', 1.0) if config.get('is_dynamic') else 1.0)
    }

    verifications = [
        {
            "label": "Velocidade Basica V0",
            "pass": config.get('v0', 0) > 0,
            "value": f"{config.get('v0', 0)} m/s",
            "limit": "> 0"
        }
    ]

    governing = {
        "Nivel Critico": "Topo do edificio",
        "Direcao do Vento": "0 ou 90 graus (conforme Cf)",
        "Criterio Governante": "Pressao Dinamica NBR 6123"
    }

    alerts = []
    if config.get('is_dynamic') and config.get('f1', 0.5) < 1.0:
        alerts.append("Estrutura flexivel, sensivel a efeitos dinamicos do vento.")

    limitations = [
        "Nao considera efeitos de vizinhanca (canalizacao)",
        "Nao considera instabilidade aeroelastica (galope/flutter)"
    ]

    return build_unified_memorial(
        module_title="Ações de Vento (NBR 6123)",
        engine_name="WindEngineM4",
        engine_version="1.0.0",
        hypotheses=hypotheses,
        materials=materials,
        loads=loads,
        combinations=combinations,
        model_details=model_details,
        results=results_summary,
        verifications=verifications,
        governing=governing,
        alerts=alerts,
        limitations=limitations
    )
