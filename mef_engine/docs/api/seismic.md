# Sismo (NBR 15421)

Análise sísmica por espectro de resposta.

**Prefixo:** `/api/ufo/` | `/api/v1/ufo/`

---

## POST `/seismic/analyze`

Análise sísmica usando Response Spectrum Analysis (RSA).

### Request Body — `SeismicAnalysisRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `nodes` | list[dict] | — | `{id, x, y, z}` |
| `members` | list[dict] | — | `{id, node_i, node_j, section: {b, h, E}}` |
| `supports` | dict | — | `{node_id: [blocked_dofs 0-5]}` |
| `soil_class` | str | "D" | Classe de solo (A–E) — NBR 15421 |
| `seismic_zone` | int | 1 | Zona sísmica (0–4) — mapa brasileiro |
| `num_modes` | int | 10 | Número de modos de vibração |
| `R` | float | 1.0 | Fator de ductilidade |
| `I` | float | 1.0 | Fator de importância |

### Classes de Solo (NBR 15421)

| Classe | Descrição | Vs30 (m/s) |
|---|---|---|
| A | Rocha sã | > 1500 |
| B | Rocha alterada / solo muito rígido | 760–1500 |
| C | Solo denso | 360–760 |
| D | Solo médio | 180–360 |
| E | Solo mole | < 180 |

### Zonas Sísmicas Brasileiras (NBR 15421)

| Zona | Região | ag (g) |
|---|---|---|
| 0 | Nordeste (interior) | 0.025 |
| 1 | Centro-oeste, Sudeste | 0.05–0.10 |
| 2 | Sul, parte do Sudeste | 0.15 |
| 3 | Região de Sobral-CE | 0.25 |
| 4 | (não aplicável no Brasil) | 0.35 |

### Resposta

| Campo | Descrição |
|---|---|
| `spectral_accelerations` | Acelerações espectrais por modo |
| `base_shear_kN` | Cortante basal |
| `modal_combination` | Método de combinação (SRSS/CQC) |
| `top_displacement_mm` | Deslocamento de topo |
| `modal_participation` | Participação de massa modal |
| `response_spectrum` | Espectro de resposta elástico |

### Dashboard Sísmico

O endpoint `/calculate/stability-dashboard` também inclui
análise sísmica quando `seismic_zone` é fornecido:

```json
{
    "seismic": {
        "zone": 2,
        "soil_class": "D",
        "ag_g": 0.15,
        "S": 1.5,
        "TB_s": 0.1,
        "TC_s": 0.6,
        "Sa_plateau_ms2": 2.21,
        "design_spectrum": [ ... ]
    }
}
```
