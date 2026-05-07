"""slab_reporting.py – Gerador de Relatórios Markdown para Lajes Suspensas."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

def _fmt(value, digits: int = 3, suffix: str = '') -> str:
    if value is None: return 'n/d'
    try: return f'{float(value):.{digits}f}{suffix}'
    except: return str(value)

def build_slab_markdown_report(memorial: dict) -> str:
    """Gera o relatório profissional em Markdown específico para lajes."""
    geo = memorial['geometry']
    mat = memorial['materiais']
    stru = memorial['verificacoes_estruturais']
    serv = memorial['verificacoes_de_servico']
    
    report = f"""# Memorial de Calculo: Laje Suspensa
    
## 1. Premissas de Projeto
- **Geometria:** {geo['Lx_m']}x{geo['Ly_m']} m | Espessura: {geo['h_m']*100} cm
- **Materiais:** Concrete fck={mat['fck_MPa']} MPa | CA-50
- **Norma Base:** {memorial['base_normativa']['perfil_principal']}

## 2. Resultados da Analise MEF
- **Momento Fletor Maximo (Mx):** {_fmt(stru['flexao']['Mx_max_kNm_m'], 2)} kNm/m
- **Momento Fletor Maximo (My):** {_fmt(stru['flexao']['My_max_kNm_m'], 2)} kNm/m
- **Flecha Maxima (ELU):** {_fmt(serv['w_max_mm'], 2)} mm
- **Limite de Flecha (L/250):** {_fmt(serv['w_limit_mm'], 2)} mm

## 3. Verificacao de Seguranca
- **Equilibrio Global:** {"OK" if stru['equilibrio_global']['atende'] else "ERRO"}
- **Puncao:** {stru['puncao']['status']} (Ratio: {_fmt(stru['puncao']['ratio_max'], 2)})

---
*Relatorio gerado automaticamente pelo MEF STRUCTURAL - Modulo Lajes.*
"""
    return report

def build_slab_artifact_manifest(config: Any, memorial: dict) -> dict:
    """Cria o manifesto de artefatos para o dashboard."""
    return {
        "title": "Relatorio de Calculo: Laje Suspensa",
        "system": "Lajes PRO",
        "artifacts": [
            {"id": "memorial_json", "path": f"{config.base_name}_memorial.json", "label": "Dados do Memorial (JSON)"},
            {"id": "nodal_results", "path": f"{config.base_name}_nodes.csv", "label": "Resultados Nodais (CSV)"}
        ]
    }
