# Módulos Elite

Análise avançada de elementos estruturais individuais.

**Prefixo:** `/api/ufo/` (compartilha prefixo UFO)

---

## POST `/calculate/beam`

Análise completa de viga: MEF + dimensionamento + detalhamento.

### Request Body — `BeamAnalysisRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `L` | float | 6.0 | Vão total (m) |
| `b` | float | 0.20 | Largura da viga (m) |
| `h` | float | 0.50 | Altura da viga (m) |
| `fck` | float | 30.0 | Resistência do concreto (MPa) |
| `caa` | int | 2 | Classe de agressividade |
| `cover` | float | null | Cobrimento (m) |
| `supports` | list[dict] | — | Apoios `{x, type}` |
| `distributed_loads` | list[dict] | null | Cargas distribuídas |
| `point_loads` | list[dict] | null | Cargas concentradas |
| `n_elements` | int | 40 | Número de elementos finitos |
| `nonlinear` | bool | True | Análise não-linear |
| `include_self_weight` | bool | True | Incluir peso próprio |
| `gamma_f` | float | 1.4 | Coeficiente de majoração |

### Resposta

| Campo | Descrição |
|---|---|
| `success` | Sucesso |
| Deslocamentos | Flechas (mm) |
| Esforços | Diagramas (N, V, M) |
| Dimensionamento | Armadura longitudinal e transversal |
| `memorial_markdown` | Memorial de cálculo |
| `pedagogical_steps` | Passos pedagógicos |
| Deformações | Flecha imediata e diferida |

---

## POST `/calculate/column`

Dimensionamento completo de pilar com flexão composta.

### Request Body — `ColumnRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `b` | float | 0.60 | Largura da seção (m) |
| `h` | float | 0.60 | Altura da seção (m) |
| `fck` | float | 40.0 | Resistência do concreto (MPa) |
| `caa` | int | 2 | Classe de agressividade |
| `cover` | float | null | Cobrimento (m) |
| `L_free` | float | 3.0 | Comprimento de flambagem (m) |
| `Nd_kN` | float | 5000.0 | Força normal de cálculo (kN) |
| `Mxd_kNm` | float | 0.0 | Momento em X (kNm) |
| `Myd_kNm` | float | 0.0 | Momento em Y (kNm) |
| `n_floors_for_shortening` | int | 40 | Pavimentos para cálculo de encurtamento |

### Resposta

| Campo | Descrição |
|---|---|
| `design` | Dimensionamento (armadura, taxa) |
| `shortening` | Encurtamento elástico |
| `pedagogical_steps` | Passos pedagógicos |
| `summary` | Resumo executivo |

---

## POST `/calculate/building-core`

Análise de núcleo rígido (poço de elevador, caixa de escada, shear walls).

### Request Body — `CoreAnalysisRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `building_Lx` | float | 24.0 | Dimensão X do edifício (m) |
| `building_Ly` | float | 24.0 | Dimensão Y (m) |
| `n_floors` | int | 40 | Número de pavimentos |
| `floor_height` | float | 3.0 | Pé-direito (m) |
| `floor_weight_kN` | float | 5000.0 | Peso por pavimento (kN) |
| `fck` | float | 35.0 | Concreto (MPa) |
| `elevator_shafts` | list[dict] | null | Poços de elevador |
| `stair_cores` | list[dict] | null | Caixas de escada |
| `shear_walls` | list[dict] | null | Paredes estruturais |

---

## POST `/optimize`

Otimização genética de parâmetros estruturais.

### Request Body — `OptimizationRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `project_id` | str | — | ID do projeto |
| `target` | str | "cost" | Objetivo (`cost`, `weight`, `displacement`) |
| `variables` | list[str] | `["h", "fck"]` | Variáveis de otimização |
| `constraints` | dict | `{w_max: 30.0}` | Restrições |
| `population_size` | int | 10 | Tamanho da população |
| `generations` | int | 5 | Número de gerações |

---

## POST `/copilot/diagnose`

Diagnóstico por IA Copilot.

| Campo | Tipo | Padrão |
|---|---|---|
| `project_id` | str | — |
| `analysis_type` | str | "general" |

---

## POST `/calculate_v2_unified`

Pipeline integrado: Pórtico 3D → Radier (análise completa do edifício).

**Request Body:** `ConfigInput` (mesmo do endpoint `/calculate` do core)

**Resposta:** Resultados combinados de pórtico, radier, vento,
diagnósticos de campo, consistência Winkler e recomendação de fundação.
