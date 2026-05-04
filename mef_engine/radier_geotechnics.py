"""radier_geotechnics.py – Módulo de geotecnia para solo heterogêneo e correlações SPT."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.interpolate import griddata

SOIL_KV_FACTORS_MPA_PER_M: dict[str, dict[str, float]] = {
    # Fatores orientativos para k_v = fator * N_spt.
    # Faixas para estudos preliminares com calibração posterior.
    'argila_mole': {'conservador': 8.0, 'medio': 12.0, 'agressivo': 16.0},
    'argila_rija': {'conservador': 14.0, 'medio': 20.0, 'agressivo': 28.0},
    'silte': {'conservador': 12.0, 'medio': 18.0, 'agressivo': 25.0},
    'areia_fofa': {'conservador': 18.0, 'medio': 28.0, 'agressivo': 40.0},
    'areia_media': {'conservador': 25.0, 'medio': 40.0, 'agressivo': 55.0},
    'areia_compacta': {'conservador': 35.0, 'medio': 55.0, 'agressivo': 80.0},
    'misto': {'conservador': 20.0, 'medio': 30.0, 'agressivo': 45.0},
}

VALID_CORRELATION_LEVELS = {'conservador', 'medio', 'agressivo'}


def _normalize_soil_type(soil_type: object, default_soil_type: str) -> str:
    if soil_type is None:
        return default_soil_type
    key = str(soil_type).strip().lower()
    return key if key in SOIL_KV_FACTORS_MPA_PER_M else default_soil_type


def _resolve_correlation_level(level: str) -> str:
    key = str(level).strip().lower()
    if key not in VALID_CORRELATION_LEVELS:
        raise ValueError(
            f'Nivel de correlacao invalido: {level}. Use um de {sorted(VALID_CORRELATION_LEVELS)}.'
        )
    return key


def nspt_to_kv(
    nspt: float,
    soil_type: str = 'misto',
    correlation_level: str = 'medio',
) -> float:
    nspt_value = max(float(nspt), 0.0)
    soil_key = _normalize_soil_type(soil_type, 'misto')
    level_key = _resolve_correlation_level(correlation_level)
    factor = SOIL_KV_FACTORS_MPA_PER_M[soil_key][level_key]
    return nspt_value * factor * 1e6


def _ensure_kv_column(
    spt_points: pd.DataFrame,
    correlation_level: str,
    default_soil_type: str,
) -> pd.DataFrame:
    df = spt_points.copy()
    required_xy = {'x', 'y'}
    missing_xy = required_xy.difference(df.columns)
    if missing_xy:
        raise ValueError(f"CSV de sondagens sem colunas obrigatorias: {sorted(missing_xy)}")

    df['x'] = pd.to_numeric(df['x'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    if df[['x', 'y']].isna().any().any():
        raise ValueError('CSV de sondagens possui valores nao numericos em x/y.')

    if 'kv' in df.columns:
        df['kv'] = pd.to_numeric(df['kv'], errors='coerce')
        if df['kv'].isna().any():
            raise ValueError('CSV de sondagens possui valores nao numericos em kv.')
        return df

    if 'nspt' not in df.columns:
        raise ValueError("CSV de sondagens deve conter 'kv' ou 'nspt'.")

    df['nspt'] = pd.to_numeric(df['nspt'], errors='coerce')
    if df['nspt'].isna().any():
        raise ValueError('CSV de sondagens possui valores nao numericos em nspt.')

    if 'soil_type' not in df.columns:
        df['soil_type'] = default_soil_type
    df['soil_type'] = df['soil_type'].map(lambda item: _normalize_soil_type(item, default_soil_type))

    df['kv'] = [
        nspt_to_kv(nspt, soil_type=soil_type, correlation_level=correlation_level)
        for nspt, soil_type in zip(df['nspt'].to_numpy(), df['soil_type'].to_numpy())
    ]
    return df


def build_kv_map_and_metadata(
    nodes: np.ndarray,
    spt_points: pd.DataFrame | None,
    default_kv: float,
    correlation_level: str = 'medio',
    default_soil_type: str = 'misto',
    apply_scale_effect: bool = True,
) -> tuple[np.ndarray, dict]:
    """
    Interpola o coeficiente de recalque (kv) nos nós do radier a partir de furos de sondagem.
    spt_points: DataFrame com colunas ['x', 'y', 'kv'] ou ['x', 'y', 'nspt', 'soil_type(opcional)']
    """
    level_key = _resolve_correlation_level(correlation_level)
    soil_default = _normalize_soil_type(default_soil_type, 'misto')

    metadata = {
        'source': 'default_uniform',
        'default_kv_N_m3': float(default_kv),
        'correlation_level': level_key,
        'default_soil_type': soil_default,
        'soil_type_factors_MPa_m': SOIL_KV_FACTORS_MPA_PER_M,
        'notes': [
            'Correlacoes N_spt -> k_v sao orientativas para estudo preliminar.',
            'Recomenda-se calibracao com monitoramento de recalques e investigacao geotecnica local.',
        ],
    }

    if spt_points is None or spt_points.empty:
        return np.full(len(nodes), default_kv), metadata

    df = _ensure_kv_column(spt_points, correlation_level=level_key, default_soil_type=soil_default)
    points = df[['x', 'y']].to_numpy(dtype=float)
    values = df['kv'].to_numpy(dtype=float)

    kv_map = griddata(points, values, (nodes[:, 0], nodes[:, 1]), method='linear')
    nan_mask = np.isnan(kv_map)
    if nan_mask.any():
        kv_nearest = griddata(points, values, (nodes[nan_mask, 0], nodes[nan_mask, 1]), method='nearest')
        kv_map[nan_mask] = kv_nearest

    metadata.update(
        {
            'source': 'spt_interpolated',
            'n_soundings': int(len(df)),
            'kv_source': 'direct_kv' if 'kv' in spt_points.columns else 'nspt_correlation',
            'n_from_direct_kv_points': int(len(df)) if 'kv' in spt_points.columns else 0,
            'kv_min_input_N_m3': float(values.min()),
            'kv_mean_input_N_m3': float(values.mean()),
            'kv_max_input_N_m3': float(values.max()),
            'kv_min_map_N_m3': float(np.min(kv_map)),
            'kv_mean_map_N_m3': float(np.mean(kv_map)),
            'kv_max_map_N_m3': float(np.max(kv_map)),
            'soil_types_used': sorted(set(df.get('soil_type', pd.Series([soil_default])).astype(str).tolist())),
            'interpolation': {
                'inside_hull': 'linear',
                'outside_hull': 'nearest',
            },
        }
    )

    # Aplicação do Efeito de Escala (Terzaghi)
    if apply_scale_effect and len(nodes) > 0:
        lx = nodes[:, 0].max() - nodes[:, 0].min()
        ly = nodes[:, 1].max() - nodes[:, 1].min()
        area = lx * ly
        perimeter = 2.0 * (lx + ly)
        # Raio hidráulico equivalente: 4 * Area / Perimetro (Para quadrado, dá L. Para retângulo longo, aproxima L menor)
        min_dim = (4.0 * area / perimeter) if perimeter > 0 else min(lx, ly)
        
        # Apenas reduz se o radier for considerável (> 0.5m)
        if min_dim > 0.5:
            # Fator (B + 0.3) / (2B)
            scale_factor = (min_dim + 0.30) / (2.0 * min_dim)
            kv_map = kv_map * scale_factor
            
            metadata['scale_effect'] = {
                'applied': True,
                'min_dimension_m': float(min_dim),
                'scale_factor': float(scale_factor),
                'original_kv_mean_N_m3': metadata['kv_mean_map_N_m3'],
                'scaled_kv_mean_N_m3': float(np.mean(kv_map)),
            }
            # Update map stats with scaled values
            metadata['kv_min_map_N_m3'] = float(np.min(kv_map))
            metadata['kv_mean_map_N_m3'] = float(np.mean(kv_map))
            metadata['kv_max_map_N_m3'] = float(np.max(kv_map))
        else:
            metadata['scale_effect'] = {'applied': False, 'reason': 'min_dimension_too_small'}

    return kv_map, metadata


def interpolate_kv_map(
    nodes: np.ndarray,
    spt_points: pd.DataFrame,
    default_kv: float,
    correlation_level: str = 'medio',
    default_soil_type: str = 'misto',
) -> np.ndarray:
    kv_map, _ = build_kv_map_and_metadata(
        nodes,
        spt_points,
        default_kv=default_kv,
        correlation_level=correlation_level,
        default_soil_type=default_soil_type,
    )
    return kv_map


def get_spt_template() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {'id': 'SP01', 'x': 0.0, 'y': 0.0, 'nspt': 15, 'soil_type': 'argila_rija'},
            {'id': 'SP02', 'x': 24.0, 'y': 0.0, 'nspt': 25, 'soil_type': 'areia_media'},
            {'id': 'SP03', 'x': 12.0, 'y': 24.0, 'nspt': 20, 'soil_type': 'misto'},
        ]
    )
