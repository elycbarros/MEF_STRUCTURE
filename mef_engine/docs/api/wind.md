# Vento (NBR 6123)

Perfil de vento, forças globais e coeficientes aerodinâmicos.

**Prefixo:** `/api/ufo/` | `/api/v1/ufo/`

---

## POST `/calculate/wind`

Perfil completo de pressão dinâmica conforme NBR 6123.

### Request Body — `WindRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `v0` | float | 30.0 | Velocidade básica do vento (m/s) |
| `altura_total` | float | 15.0 | Altura total da edificação (m) |
| `largura` | float | 1.0 | Largura exposta (m) |
| `profundidade` | float | null | Profundidade (m) |
| `step` | float | 1.0 | Discretização vertical (m) |
| `cf` | float | null | Coeficiente de força aerodinâmico |
| `area_por_nivel_m2` | float | null | Área de tributação por nível |
| `s1` | float | 1.0 | Fator topográfico |
| `s3` | float | 1.0 | Fator estatístico |
| `categoria` | int | 2 | Categoria de rugosidade (I a V) |
| `classe` | str | "B" | Classe (A, B, C) |
| `is_dynamic` | bool | False | Análise dinâmica |
| `f1` | float | 0.5 | Frequência fundamental (Hz) |
| `zeta` | float | 0.01 | Taxa de amortecimento |
| `beta` | float | 1.0 | Fator modal auxiliar |

### Fatores S2 (NBR 6123 Tabela 1)

| Classe | Descrição |
|---|---|
| A | Maior dimensão ≤ 20 m |
| B | Maior dimensão 20–50 m |
| C | Maior dimensão > 50 m |

| Categoria | Rugosidade |
|---|---|
| I | Superfícies lisas (mar, lago) |
| II | Terreno aberto (campo) |
| III | Terreno com obstáculos baixos |
| IV | Terreno com obstáculos numerosos |
| V | Terreno com obstáculos grandes |

### Resposta

```json
{
    "success": true,
    "result": {
        "perfil": [
            {"z_m": 5.0, "S2": 0.89, "q_Pa": 392.0},
            {"z_m": 10.0, "S2": 0.96, "q_Pa": 455.0},
            {"z_m": 15.0, "S2": 1.02, "q_Pa": 514.0}
        ],
        "v0": 30.0,
        "vk": 28.5,
        "q_din": 508.0
    },
    "summary": {
        "max_q_Pa": 514.0,
        "total_force_kN": 145.2,
        "base_moment_kNm": 872.0
    },
    "pedagogical_steps": { ... }
}
```

---

## POST `/calculate/wind-stability`

Análise acoplada vento + estabilidade.

### Request Body — `WindStabilityRequest` (estende `WindRequest`)

| Campo Adicional | Tipo | Padrão | Descrição |
|---|---|---|---|
| `total_p_kN` | float | 10000.0 | Carga vertical total (kN) |
| `m1_kNm` | float | null | Momento de 1ª ordem (kNm) |

### Resposta

| Seção | Conteúdo |
|---|---|
| `wind` | Perfil de vento completo |
| `stability` | γz, classificação, P-Delta |
| `coupling` | Momento e força horizontal utilizados |
