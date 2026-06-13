# Modo Mestre

Análise didática e segmentada de elementos estruturais isolados.

**Prefixo:** `/api/mestre/` (legacy) | `/api/v1/mestre/` (versionado)

---

## POST `/calculate`

Motor principal de análise — radier sobre base elástica de Winkler.

### Request Body

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `Lx` | float | 32.5 | Comprimento X (m) |
| `Ly` | float | 24.8 | Comprimento Y (m) |
| `h` | float | 1.15 | Espessura (m) |
| `kv` | float | 22.1e6 | Coeficiente de reação vertical (N/m³) |
| `q` | float | 140e3 | Carga distribuída (Pa) |
| `sigma_adm_kPa` | float | 200.0 | Tensão admissível do solo (kPa) |
| `fck` | float | 30.0 | Resistência do concreto (MPa) |
| `fyk` | float | 500.0 | Resistência do aço (MPa) |
| `system_type` | str | "radier" | `"radier"` ou `"laje"` |
| `slab_type` | str | "solid" | Tipo de laje: `solid`, `ribbed`, `hollow_core`, `prestressed`, `trussed` |
| `pillars` | list[PillarInput] | null | Definição dos pilares |

### PillarInput

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | str | ID do pilar |
| `x`, `y` | float | Coordenadas (m) |
| `p_kN` | float | Carga vertical (kN) |
| `bx`, `by` | float | Dimensões do pilar (m) |

### LineSupportInput

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | str | ID do apoio |
| `x1`, `y1`, `x2`, `y2` | float | Coordenadas inicial/final (m) |
| `support_type` | str | `"pinned"`, `"fixed"`, `"spring"` |
| `k_spring` | float | Rigidez da mola (N/m) |

### Resposta

| Campo | Tipo | Descrição |
|---|---|---|
| `success` | bool | Sucesso da operação |
| `master` | dict | Resultados brutos do motor |
| `deterministic` | dict | Sumário MEF |
| `winkler_consistency` | dict | Consistência do modelo de Winkler |
| `analytical_comparison` | dict | Comparação MEF vs analítico |
| `reinforcement_summary` | dict | Sumário de armadura |
| `field_risk_summary` | dict | Risco de campo |
| `foundation_recommendation` | dict | Recomendação de fundação |
| `executive_decision` | dict | Decisão executiva |

---

## POST `/calculate/special-elements`

Calcula elementos estruturais especiais.

### Tipos Suportados

| `type` | Elemento | Parâmetros Chave |
|---|---|---|
| `"stair"` | Escada | `L`, `H`, `q`, `t`, `fck` |
| `"slab"` | Laje | `Lx`, `Ly`, `h`, `fck`, `q` |
| `"beam"` | Viga | `L`, `b`, `h`, `fck`, `supports`, `distributed_loads` |
| `"column"` | Pilar | `b`, `h`, `Nd`, `fck`, `L_free` |
| `"footing"` | Sapata | `Nd`, `sigma_adm`, `ap`, `bp`, `fck` |
| `"pile_cap"` | Bloco de estaca | `Nd`, `dist_piles`, `diam_pile`, `fck` |
| `"concrete_wall"` | Parede de concreto | `Nd`, `h`, `t`, `fck` |
| `"pillar_wall"` | Parede-pilar | `b`, `h`, `Nd`, `fck` |
| `"retaining_wall"` | Muro de arrimo | `h_wall`, `gamma_soil`, `phi_soil` |
| `"reservoir"` | Reservatório | `length`, `width`, `depth` |
| `"corbel"` | Consolo | `fd_kN`, `a_dist`, `d_eff`, `fck` |
| `"deep_beam"` | Viga-parede | `q`, `L`, `h` |
| `"helical_stairs"` | Escada helicoidal | `radius`, `angle_total_deg`, `h_step` |
| `"pile"` | Estaca | `pile_type`, `diameter`, `length`, `fck`, `Nd` |
| `"tension_pro"` | Protensão | `span`, `q_service`, `p0`, `eccentricity` |
| `"advanced_slab"` | Laje avançada | `Lx`, `Ly`, `h`, `fck`, `columns` |
| `"exam_auditor"` | Auditoria de prova | `question_id` |

---

## POST `/frame/analyze`

Análise pedagógica de pórtico 3D com exibição de matriz de rigidez.

### Request Body

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `nodes` | list[dict] | — | `{id, x, y, z}` |
| `members` | list[dict] | — | `{id, node_i, node_j, section: {b, h, E}}` |
| `loads` | list[dict] | — | `{node_id, fx, fy, fz, mx, my, mz}` |
| `supports` | dict | — | `{node_id: [blocked_dofs 0-5]}` |
| `show_matrix_proof` | bool | True | Exibe matriz de rigidez |
| `is_truss` | bool | False | Modo treliça |

### Resposta

| Campo | Descrição |
|---|---|
| `success` | Sucesso |
| `mode` | `"MESTRE_PEDAGOGICAL"` |
| `displacements` | Deslocamentos nodais |
| `efforts` | Esforços nas barras (N, V, M) |
| `equilibrium_audit` | Auditoria de equilíbrio dos nós |
| `pedagogical_proofs` | Matriz de rigidez passo a passo |
| `pedagogical_steps` | Passos do quadro negro pedagógico |
| `memorial_markdown` | Memorial de cálculo em Markdown |

---

## Outros Endpoints do Modo Mestre

### POST `/load-combinations`

Combinações de carga conforme NBR 8681.

| Campo | Tipo | Padrão |
|---|---|---|
| `actions` | list[LoadActionInput] | — |
| `gamma_g_unfav` | float | 1.4 |
| `gamma_g_fav` | float | 1.0 |
| `gamma_q` | float | 1.4 |

### POST `/check/compliance`

Verificação de durabilidade.

| Parâmetro | Tipo |
|---|---|
| `caa` | int (classe de agressividade) |
| `trrf` | int (TRRF em minutos) |
| `width_cm` | float (largura da peça) |

### POST `/calculate/spt`

Análise de sondagem SPT.

| Campo | Tipo | Padrão |
|---|---|---|
| `spt_data` | list[dict] | Exemplo de camadas |
| Demais parâmetros | — | Comporta `N_spT`, profundidade, nível d'água |

### POST `/calculate/stability-mestre`

Estabilidade + vento em modo pedagógico.

| Campo | Tipo | Padrão |
|---|---|---|
| `v0` | float | 30.0 |
| `height` | float | 30.0 |
| `total_p_kN` | float | 10000.0 |
| `m1_kNm` | float | 5000.0 |
| `s1` | float | 1.0 |
| `s3` | float | 1.0 |
| `classe` | str | "B" |
| `categoria` | int | 2 |
| `f1_hz` | float | 0.5 |

### POST `/optimize_design`

Otimização iterativa de espessura.

| Campo | Tipo | Descrição |
|---|---|---|
| `current_h` | float | Espessura atual (m) |
| `target_sigma` | float | Tensão alvo (kPa) |
| `config` | ConfigInput | Configuração opcional |
