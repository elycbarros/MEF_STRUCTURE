from __future__ import annotations

from pathlib import Path

import pandas as pd


def validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f'{name} deve ser positivo.')


def validate_lab_config(config) -> None:
    validate_positive('Lx', config.Lx)
    validate_positive('Ly', config.Ly)
    validate_positive('h', config.h)
    validate_positive('kv', config.kv)
    validate_positive('q', config.q)
    if config.nx < 3 or config.ny < 3:
        raise ValueError('nx e ny devem ser >= 3.')
    if config.nx % 2 == 0 or config.ny % 2 == 0:
        raise ValueError('nx e ny devem ser ímpares para manter um nó central e malha mais estável.')
    if not (0.0 < config.nu < 0.5):
        raise ValueError('nu deve estar entre 0 e 0.5.')
    validate_positive('fck', config.fck)
    validate_positive('fyk', config.fyk)


def _validate_required_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f'{label} sem colunas obrigatórias: {sorted(missing)}')


def validate_columns_dataframe(df: pd.DataFrame) -> None:
    _validate_required_columns(df, {'id', 'x', 'y', 'p', 'bx', 'by'}, 'CSV de pilares')
    if (df[['p', 'bx', 'by']] <= 0).any().any():
        raise ValueError('CSV de pilares deve ter p, bx e by positivos.')


def validate_measurements_dataframe(df: pd.DataFrame) -> None:
    _validate_required_columns(df, {'x', 'y', 'w_mm'}, 'CSV de medições')
    if len(df) == 0:
        raise ValueError('CSV de medições não pode estar vazio.')


def validate_spt_dataframe(df: pd.DataFrame) -> None:
    _validate_required_columns(df, {'x', 'y'}, 'CSV de sondagens')
    if len(df) == 0:
        raise ValueError('CSV de sondagens não pode estar vazio.')
    if ('kv' not in df.columns) and ('nspt' not in df.columns):
        raise ValueError("CSV de sondagens deve conter 'kv' ou 'nspt'.")
    if 'kv' in df.columns:
        kv = pd.to_numeric(df['kv'], errors='coerce')
        if kv.isna().any():
            raise ValueError('CSV de sondagens possui valores não numéricos em kv.')
        if (kv <= 0).any():
            raise ValueError('CSV de sondagens deve ter kv positivo.')
    if 'nspt' in df.columns:
        nspt = pd.to_numeric(df['nspt'], errors='coerce')
        if nspt.isna().any():
            raise ValueError('CSV de sondagens possui valores não numéricos em nspt.')
        if (nspt < 0).any():
            raise ValueError('CSV de sondagens deve ter nspt >= 0.')
    if 'soil_type' in df.columns:
        if df['soil_type'].astype(str).str.strip().eq('').any():
            raise ValueError('CSV de sondagens possui soil_type vazio.')


def validate_columns_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_columns_dataframe(df)
    return df


def validate_measurements_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_measurements_dataframe(df)
    return df


def validate_spt_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_spt_dataframe(df)
    return df
