# Estabilidade Global

Endpoints para análise de estabilidade de edifícios conforme NBR 6118:2014.

**Prefixo:** `/api/ufo/` | `/api/v1/ufo/`

---

## POST `/calculate/stability`

Cálculo do coeficiente Gama-Z, análise de conforto e vórtice.

### Request Body — `StabilityRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `total_p_kN` | float | — | Carga vertical total (kN) |
| `height` | float | — | Altura total do edifício (m) |
| `m1_kNm` | float | — | Momento de 1ª ordem (kNm) |
| `wind_v0` | float | 30.0 | Velocidade básica do vento (m/s) |
| `f1_hz` | float | 0.5 | Frequência fundamental (Hz) |
| `total_h_force_kN` | float | 0.0 | Força horizontal total (kN) |
| `width_x` | float | 20.0 | Largura exposta ao vento (m) |
| `total_mass_kg` | float | 0.0 | Massa total (kg) |

### Resposta

```json
{
    "success": true,
    "stability": {
        "gamma_z": 1.12,
        "is_stable": true,
        "requires_second_order": true,
        "p_delta_factor": 0.87,
        "p_delta_iterations": 4,
        "is_divergent": false,
        "peak_acceleration_ms2": 0.015,
        "comfort_status": "baixo",
        "comfort_frequency_hz": 0.50,
        "vortex_shedding": {
            "v_crit_ms": 42.0,
            "v_service_ms": 38.0,
            "risk_ratio": 0.90,
            "lock_in_risk": "moderado"
        }
    }
}
```

### Critérios Gama-Z (NBR 6118:2014, item 15.5)

| γz | Classificação | Ação |
|---|---|---|
| ≤ 1.10 | Nós fixos | Dispensa P-Delta |
| 1.10 < γz ≤ 1.30 | Nós móveis | P-Delta obrigatório |
| > 1.30 | Instável | Redimensionar |

---

## POST `/calculate/stability-dashboard`

Dashboard unificado com vento + estabilidade + sísmico + vórtice.

### Request Body — `UnifiedStabilityRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `total_p_kN` | float | — | Carga vertical total (kN) |
| `height` | float | — | Altura (m) |
| `width_x` | float | 20.0 | Largura em vento (m) |
| `depth` | float | null | Profundidade (m) |
| `wind_v0` | float | 30.0 | Velocidade do vento (m/s) |
| `wind_categoria` | int | 2 | Categoria de rugosidade |
| `wind_classe` | str | "B" | Classe da edificação |
| `m1_kNm` | float | null | Momento de 1ª ordem |
| `f1_hz` | float | 0.5 | Frequência fundamental |
| `zeta` | float | 0.01 | Amortecimento crítico |
| `total_mass_kg` | float | null | Massa total |
| `seismic_zone` | int | null | Zona sísmica NBR 15421 |
| `seismic_soil` | str | "D" | Classe de solo sísmico |

### Resposta

| Seção | Conteúdo |
|---|---|
| `wind` | Perfil de vento completo (NBR 6123) |
| `stability` | γz, classificação, P-Delta |
| `comfort` | Aceleração de topo, frequência |
| `vortex` | Velocidade crítica, risco de lock-in |
| `seismic` | Zona, espectro de resposta |
| `coupling` | Acoplamento vento-estabilidade |
