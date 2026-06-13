# Arquitetura

## Visão Geral em Camadas

O Atlas Structural Engine segue arquitetura hexagonal com aceleração
seletiva via Rust, injeção de dependência e fallback transparente.

```
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  /api/mestre/*  /api/v1/mestre/*  /api/ufo/*  /api/v1/ufo/* │
├──────────────────────────────────────────────────────────────┤
│                     Camada de Rotas (routes/)                │
│  core.py  frame.py  stability.py  wind.py  seismic.py  ssi   │
│  elite.py  forensic.py  phd.py  reports.py  loads.py         │
│  mestre_frame.py  special.py  ufo_detailing.py  wind.py      │
│  structural_rs.py                                             │
├──────────────────────────────────────────────────────────────┤
│                   Camada de Engenharia (Motores)              │
│  frame_engine.py     wind_engine.py       seismic_engine.py   │
│  stability_engine.py  ssi_engine.py         radier_solver_v2  │
│  beam_solver.py      column_solver.py     footing_solver.py   │
│  dxf_engine.py        bim_engine.py        ml_surrogate.py    │
│  pile_cap_solver.py  retaining_wall_solver.py  pile_engine    │
├──────────────────────────────────────────────────────────────┤
│                   Camada de Aceleração Nativa                 │
│  radier_rs_adapter.py  ←→  structural_core_rs/               │
│   (PyO3 bridge, fallback)       (Rust: faer + rayon)          │
├──────────────────────────────────────────────────────────────┤
│                Infraestrutura Compartilhada                   │
│  cache_utils.py  log_config.py  errors.py  persistence.py     │
│  load_combinator.py  platform_core.py  platform_reporting.py  │
└──────────────────────────────────────────────────────────────┘
```

## Fluxo de Requisição

```
Cliente → FastAPI → AuthMiddleware → RateLimitMiddleware
    → Rota (valida Pydantic) → Engine (Python/Rust) → Resposta JSON
```

### Cache LRU

O `AnalysisCache` (em `cache_utils.py`) usa LRU com chave SHA256:

```python
cache = AnalysisCache(maxsize=128, ttl=300)  # 128 itens, 5 min TTL
```

| Métrica | Descrição |
|---|---|
| `size` | Itens atualmente em cache |
| `hits` | Cache hits |
| `misses` | Cache misses |
| `hit_rate_pct` | Taxa de acerto (%) |

Endpoints: `GET /api/cache/stats`, `POST /api/cache/clear`

### Logging Estruturado

`log_config.py` configura logging no formato:

```
2026-06-13 09:50:07 | INFO     | frame_engine | Análise concluída em 0.34s
```

Saída simultânea:
- **Console** (stdout, nível INFO)
- **Arquivo** (`logs/engine.log`, nível DEBUG, rotação)

Todas as rotas usam `logger = logging.getLogger(__name__)` em vez de `print()`.

## Aceleração Rust

### Módulo: `structural_core_rs`

Compilado como wheel nativo via PyO3/maturin.

| Operação | Python | Rust | Speedup |
|---|---|---|---|
| Montagem FEM (13×13) | 17 ms | 211 µs | ~80× |
| Solve sparse LU | spsolve | faer | ~2.6× |
| Total (13×13) | 18 ms | 5 ms | ~3.6× |

### Fallback Automático

Quando `structural_core_rs` não está instalado:

```python
try:
    import structural_core_rs
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False  # fallback para scipy
```

### Benchmarks

```bash
cd structural_core_rs
cargo bench  # Relatório HTML em target/criterion/
```

## Versionamento de API

| Prefixo | Status |
|---|---|
| `/api/mestre/...` | Legacy (mantido) |
| `/api/v1/mestre/...` | Atual |
| `/api/ufo/...` | Legacy (mantido) |
| `/api/v1/ufo/...` | Atual |
| `/rust/...` | Legacy |
| `/api/v1/rust/...` | Atual |

**Discovery**: `GET /api/versions` retorna `current`, `available`, `legacy_paths`, `versioned_paths`.

## Tratamento de Erros

A API usa três handlers globais:

| Handler | Código | Quando |
|---|---|---|
| `StructuralError` | 400 | Erros de engenharia (validação NBR, divergência, etc.) |
| `RequestValidationError` | 422 | Schema inválido (Pydantic) |
| `Exception` | 500 | Erro interno não tratado |

Todos retornam formato padronizado:

```json
{
    "error": {
        "code": "EST-001",
        "type": "estabilidade",
        "message": "Descrição em português",
        "detail": "Detalhe técnico",
        "module": "module_name"
    }
}
```
