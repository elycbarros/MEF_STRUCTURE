# Modo UFO

Análise global profissional de edifícios com pórtico 3D, estabilidade,
vento, sísmico, SSI e detalhamento executivo.

**Prefixo:** `/api/ufo/` (legacy) | `/api/v1/ufo/` (versionado)

---

## POST `/calculate/frame`

Análise síncrona de pórtico 3D Premium com P-Delta.

### Request Body — `FrameRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `nodes` | list[FrameNodeInput] | — | `{id, x, y, z}` |
| `members` | list[FrameMemberInput] | — | `{id, node_i, node_j, section: {b, h, E, G}}` |
| `loads` | list[FrameLoadInput] | — | `{node_id, Fx, Fy, Fz, Mx, My, Mz}` |
| `supports` | dict[int, list[int]] | — | `{node_id: [dofs 0-5]}` |
| `use_p_delta` | bool | True | Análise P-Delta |
| `nbr_stiffness_reduction` | bool | True | Redução de rigidez NBR 6118 |
| `wind_v0` | float | 0.0 | Velocidade do vento (m/s) |
| `wind_categoria` | int | 2 | Categoria NBR 6123 |
| `wind_cp` | float | 0.8 | Coeficiente aerodinâmico |
| `wind_width_m` | float | 5.0 | Largura de tributação |
| `n_floors_for_wind` | int | 0 | Pavimentos para vento automático |
| `floor_height_m` | float | 3.0 | Pé-direito (m) |

### Resposta

| Campo | Tipo | Descrição |
|---|---|---|
| `success` | bool | Sucesso |
| `analysis_type` | str | `"PORTICO_3D_PREMIUM_P_DELTA"` ou `"PORTICO_3D_ELASTICO"` |
| `gamma_z` | float | Coeficiente Gama-Z |
| `stability_class` | str | `"NAO_SENSIVEL"`, `"SENSIVEL"`, `"INSTAVEL"` |
| `top_displacement_mm` | float | Deslocamento do topo |
| `nodal_displacements` | dict | Deslocamentos de todos os nós |
| `member_efforts` | dict | Esforços internos (N, Vy, Vz, T, My, Mz) |
| `equilibrium` | dict | Equilíbrio nodal |
| `diagrams` | list[dict] | Diagramas detalhados |

### POST `/calculate/frame/modal`

Análise modal assíncrona (retorna `job_id`).

```json
// Resposta imediata:
{ "job_id": "abc123", "status": "queued" }

// Consulta: GET /calculate/frame/modal/{job_id}
// Resposta com resultados modais
```

### POST `/calculate/frame/async`

Análise assíncrona do mesmo pórtico.

```json
// Resposta:
{ "job_id": "abc123", "status": "queued" }

// Consulta: GET /calculate/jobs/{job_id}
// Retorna status + progresso + resultado
```

---

## POST `/detailing/global-summary`

Detalhamento executivo global do edifício (UFO DetailingOrchestrator).

### Request Body

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `nodes` | list[dict] | — | Definição dos nós |
| `members` | list[dict] | — | Barras com seções |
| `loads` | list[dict] | — | Cargas nodais |
| `supports` | dict | — | Restrições nodais |
| `fck` | float | 30.0 | Resistência do concreto (MPa) |

---

## POST `/ssi/pile-nonlinear`

Análise não-linear de estaca via curvas p-y.

### Request Body — `SSINonLinearRequest`

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `nodes` | list[dict] | — | Nós |
| `members` | list[dict] | — | Barras |
| `loads` | list[dict] | — | Cargas |
| `supports` | dict | — | Restrições |
| `pile_configs` | dict[str, dict] | — | `{node_id: {soil_type, diameter, ...}}` |
| `max_iter` | int | 15 | Máximo de iterações |
| `tol` | float | 0.01 | Tolerância de convergência |

### Resposta

| Campo | Descrição |
|---|---|
| `success` | Convergiu? |
| `iterations` | Iterações realizadas |
| `displacements` | Deslocamentos finais |
| `final_springs_kN_m` | Rigidez final das molas |
