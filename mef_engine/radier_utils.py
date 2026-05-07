from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

import pandas as pd


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_json(path: str | Path, payload: dict) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return str(file_path)


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_csv_preview(path: str | Path, rows: int = 10) -> pd.DataFrame:
    return pd.read_csv(path).head(rows)


def dataclass_to_dict(instance) -> dict:
    return asdict(instance)


def sanitize_for_json(value):
    """Converte NaN/Inf para None para evitar falha de serialização JSON."""
    import math
    try:
        import numpy as np
    except Exception:
        np = None

    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(v) for v in value]
    if np is not None and isinstance(value, np.ndarray):
        return sanitize_for_json(value.tolist())
    if np is not None and isinstance(value, np.generic):
        return sanitize_for_json(value.item())
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if hasattr(value, 'model_dump'):
        return sanitize_for_json(value.model_dump())
    if hasattr(value, '__dict__'):
        return sanitize_for_json(value.__dict__)
    return str(value) if hasattr(value, '__class__') and value.__class__.__name__ == 'PillarSupport' else value


def _as_float(value: any, default: float = 0.0) -> float:
    import math
    try:
        f = float(value)
        return f if math.isfinite(f) else default
    except (ValueError, TypeError):
        return default
