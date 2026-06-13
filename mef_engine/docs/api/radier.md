# Radier

Solver híbrido Python+Rust para radier sobre base elástica de Winkler
(teoria de Mindlin).

**Prefixo:** `/api/mestre/` | `/api/v1/mestre/`

---

## POST `/calculate` (modo radier)

Configurando `system_type: "radier"` no endpoint principal.

### Parâmetros Geométricos

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `Lx` | float | 32.5 | Comprimento X (m) |
| `Ly` | float | 24.8 | Comprimento Y (m) |
| `h` | float | 1.15 | Espessura (m) |
| `mesh_size_x` | int | (auto) | Divisões em X |
| `mesh_size_y` | int | (auto) | Divisões em Y |

### Parâmetros do Solo

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `kv` | float | 22.1e6 | Coeficiente de reação vertical (N/m³) |
| `sigma_adm_kPa` | float | 200.0 | Tensão admissível (kPa) |

### Parâmetros do Concreto

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `fck` | float | 30.0 | Resistência do concreto (MPa) |
| `fyk` | float | 500.0 | Resistência do aço (MPa) |

### Carregamentos

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `q` | float | 140e3 | Carga distribuída (Pa) |
| `pillars` | list[PillarInput] | null | Cargas concentradas nos pilares |

### Solver Híbrido

O radier usa aceleração Rust quando disponível:

| Operação | Python | Rust (faer + rayon) | Speedup |
|---|---|---|---|
| Montagem 13×13 | 17 ms | 211 µs | ~80× |
| Solve sparse | 1.0 ms (spsolve) | 0.4 ms (faer LU) | ~2.6× |
| Total | 18 ms | 5 ms | **~3.6×** |

### Convergência

O solver retorna `converged: bool` no resultado:

```json
{
    "solver_result": {
        "converged": true,
        "w_max_mm": 12.4,
        "q_max_kPa": 185.0,
        "iterations": 4
    }
}
```

### Fallback

Quando o módulo Rust não está disponível, o sistema usa
automaticamente `scipy.sparse.linalg.spsolve`.

---

## ENDPOINTS ADICIONAIS

### DXF Export

| Endpoint | Descrição |
|---|---|
| `POST /api/ufo/export/dxf/radier` | Desenho do radier em DXF (4 camadas de armadura) |
| `POST /api/ufo/export/dxf/slab` | Desenho de laje em DXF |

### BIM Export

| Endpoint | Descrição |
|---|---|
| `POST /api/ufo/export/bim-csv` | Resultados em CSV (ZIP) |
| `POST /api/ufo/export/bim-manifest` | Manifesto BIM em JSON |

### Relatório Profissional

| Endpoint | Descrição |
|---|---|
| `POST /api/mestre/export/pdf` | Relatório profissional radier em PDF |
