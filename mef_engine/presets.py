"""
presets.py — Módulo de Presets para Usabilidade e Facilidade de Uso.
Fornece valores típicos para solos e carregamentos em conformidade com as normas brasileiras.
"""
from typing import Dict, Any, Optional

SOIL_PRESETS: Dict[str, Dict[str, Any]] = {
    "argila_mole": {
        "name": "Argila Mole (Geral)",
        "kv": 10.0e6,              # 10 MN/m³
        "sigma_adm_kPa": 80.0,
        "description": "Solo argiloso de consistência mole, alta compressibilidade e baixa capacidade de carga."
    },
    "argila_media": {
        "name": "Argila Média",
        "kv": 25.0e6,              # 25 MN/m³
        "sigma_adm_kPa": 150.0,
        "description": "Solo argiloso de consistência média e compressibilidade moderada."
    },
    "argila_rija": {
        "name": "Argila Rija / Muito Rija",
        "kv": 50.0e6,              # 50 MN/m³
        "sigma_adm_kPa": 250.0,
        "description": "Solo argiloso firme/rijo com boa capacidade de carga e recalques controlados."
    },
    "areia_frouxa": {
        "name": "Areia Frouxa",
        "kv": 20.0e6,              # 20 MN/m³
        "sigma_adm_kPa": 120.0,
        "description": "Solo arenoso mal compactado, susceptível a deformações imediatas."
    },
    "areia_compacta": {
        "name": "Areia Compacta / Muito Compacta",
        "kv": 75.0e6,              # 75 MN/m³
        "sigma_adm_kPa": 350.0,
        "description": "Solo arenoso muito denso/compacto, excelente capacidade de carga e recalques mínimos."
    },
    "solo_misto": {
        "name": "Solo Misto (Silte Arenoso / Argiloso)",
        "kv": 35.0e6,              # 35 MN/m³
        "sigma_adm_kPa": 180.0,
        "description": "Comportamento misto com capacidade de carga intermediária."
    }
}

# Cargas por pavimento típicas (Peso Próprio Estimado + Revestimentos + Acidental NBR 6120)
PURPOSE_PRESETS: Dict[str, Dict[str, Any]] = {
    "residencial": {
        "name": "Edificação Residencial",
        "q_per_floor_Pa": 12.0e3,  # 12 kN/m² por pavimento
        "description": "Uso residencial padrão incluindo sobrecargas, divisórias e peso próprio estrutural estimado."
    },
    "comercial": {
        "name": "Edificação Comercial / Lojas",
        "q_per_floor_Pa": 15.0e3,  # 15 kN/m² por pavimento
        "description": "Áreas comerciais com fluxos moderados de pessoas e estocagem leve."
    },
    "escritorio": {
        "name": "Escritórios / Salas Comerciais",
        "q_per_floor_Pa": 14.0e3,  # 14 kN/m² por pavimento
        "description": "Salas de escritórios comerciais com divisórias e mobiliário padrão."
    },
    "garagem": {
        "name": "Garagens / Estacionamento de Veículos Leves",
        "q_per_floor_Pa": 10.0e3,  # 10 kN/m² por pavimento
        "description": "Garagens residenciais e comerciais destinadas a veículos de passeio."
    },
    "cobertura": {
        "name": "Laje de Cobertura (Sem Acesso Público)",
        "q_per_floor_Pa": 8.0e3,   # 8 kN/m²
        "description": "Lajes de cobertura técnica destinadas a manutenção e impermeabilização."
    }
}

def resolve_presets(
    soil_preset_id: Optional[str],
    purpose_preset_id: Optional[str],
    num_floors: int = 1
) -> Dict[str, Any]:
    """
    Retorna os valores resolvidos a partir dos presets informados.
    Se não informados, retorna dicionário vazio.
    """
    resolved = {}
    
    if soil_preset_id and soil_preset_id in SOIL_PRESETS:
        preset = SOIL_PRESETS[soil_preset_id]
        resolved["kv"] = preset["kv"]
        resolved["sigma_adm_kPa"] = preset["sigma_adm_kPa"]
        resolved["soil_preset_name"] = preset["name"]
        
    if purpose_preset_id and purpose_preset_id in PURPOSE_PRESETS:
        preset = PURPOSE_PRESETS[purpose_preset_id]
        resolved["q"] = preset["q_per_floor_Pa"] * max(1, num_floors)
        resolved["purpose_preset_name"] = preset["name"]
        
    return resolved
