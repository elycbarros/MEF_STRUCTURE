"""
load_combinator.py - Motor de Combinações de Ações NBR 8681 (M4 Premium).
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Literal, Dict, List, Any


ActionKind = Literal["permanent", "variable"]
UsageCategory = Literal["residential", "commercial", "office", "roof", "wind", "snow"]

# NBR 6118 / NBR 8681 Tabela de Psi
PSI_FACTORS = {
    "residential": {"psi0": 0.5, "psi1": 0.4, "psi2": 0.3},
    "office":      {"psi0": 0.7, "psi1": 0.6, "psi2": 0.4},
    "commercial":  {"psi0": 0.7, "psi1": 0.6, "psi2": 0.4},
    "roof":        {"psi0": 0.5, "psi1": 0.2, "psi2": 0.0},
    "wind":        {"psi0": 0.6, "psi1": 0.3, "psi2": 0.0},
    "snow":        {"psi0": 0.5, "psi1": 0.2, "psi2": 0.0},
}

@dataclass
class LoadAction:
    name: str
    kind: ActionKind
    value: float | np.ndarray # Suporta escalar ou vetor de esforços
    category: UsageCategory = "residential"
    psi0: float = 0.5
    psi1: float = 0.4
    psi2: float = 0.3
    is_favorable: bool = False # Se True, usa gamma_g_min (1.0) em vez de 1.4

def _build_action(item: dict) -> LoadAction:
    cat = item.get("category", "residential")
    psis = PSI_FACTORS.get(cat, PSI_FACTORS["residential"])
    
    val = item.get("value", 0.0)
    if isinstance(val, list): val = np.array(val)
    
    return LoadAction(
        name=str(item.get("name", "acao")),
        kind=item.get("kind", "variable"),
        value=val,
        category=cat,
        psi0=float(item.get("psi0", psis["psi0"])),
        psi1=float(item.get("psi1", psis["psi1"])),
        psi2=float(item.get("psi2", psis["psi2"])),
        is_favorable=bool(item.get("is_favorable", False))
    )

def combine_nbr8681(
    raw_actions: list[dict],
    gamma_g_unfav: float = 1.4,
    gamma_g_fav: float = 1.0,
    gamma_q: float = 1.4,
    special_situation: bool = False
) -> dict:
    """
    Gera as combinações ELU e ELS conforme NBR 8681.
    Se 'special_situation' for True, usa gammas reduzidos (Especial/Construção).
    """
    if special_situation:
        gamma_g_unfav, gamma_q = 1.3, 1.2
        
    actions = [_build_action(a) for a in raw_actions]
    permanent = [a for a in actions if a.kind == "permanent"]
    variable = [a for a in actions if a.kind == "variable"]
    
    # Soma de permanentes (considerando favoráveis/desfavoráveis)
    # G_d = sum(gamma_g_i * G_k_i)
    gk_total_d = 0.0
    for a in permanent:
        gamma = gamma_g_fav if a.is_favorable else gamma_g_unfav
        gk_total_d += gamma * a.value
        
    # ELS: gamma_g = 1.0 sempre
    gk_els = sum(a.value for a in permanent)

    results = {"elu": [], "els_rare": [], "els_freq": [], "els_qp": None}

    # 1. ELU Fundamental (cada variável é principal uma vez)
    if not variable:
        results["elu"].append({"name": "ELU_FUND_G", "value": gk_total_d})
    else:
        for leading in variable:
            accompanying = sum(a.psi0 * a.value for a in variable if a != leading)
            val = gk_total_d + gamma_q * (leading.value + accompanying)
            results["elu"].append({"name": f"ELU_FUND_{leading.name}", "value": val})

    # 2. ELS Raro
    if not variable:
        results["els_rare"].append({"name": "ELS_RARO_G", "value": gk_els})
    else:
        for leading in variable:
            accompanying = sum(a.psi0 * a.value for a in variable if a != leading)
            val = gk_els + leading.value + accompanying
            results["els_rare"].append({"name": f"ELS_RARO_{leading.name}", "value": val})

    # 3. ELS Frequente
    if not variable:
        results["els_freq"].append({"name": "ELS_FREQ_G", "value": gk_els})
    else:
        for leading in variable:
            accompanying = sum(a.psi2 * a.value for a in variable if a != leading)
            val = gk_els + leading.psi1 * leading.value + accompanying
            results["els_freq"].append({"name": f"ELS_FREQ_{leading.name}", "value": val})

    # 4. ELS Quase Permanente
    val_qp = gk_els + sum(a.psi2 * a.value for a in variable)
    results["els_qp"] = {"name": "ELS_QP", "value": val_qp}

    # Envoltórias (se os valores forem arrays, calcula max/min elemento a elemento)
    def _get_envelope(cases):
        values = [c["value"] for c in cases]
        if isinstance(values[0], np.ndarray):
            return {"max": np.max(values, axis=0), "min": np.min(values, axis=0)}
        else:
            return {"max": max(values), "min": min(values)}

    return {
        "success": True,
        "elu": results["elu"],
        "els_rare": results["els_rare"],
        "els_freq": results["els_freq"],
        "els_qp": results["els_qp"],
        "envelopes": {
            "elu": _get_envelope(results["elu"]),
            "els_rare": _get_envelope(results["els_rare"]),
            "els_freq": _get_envelope(results["els_freq"])
        }
    }
