# Rust Core

Módulo nativo de alto desempenho escrito em Rust via PyO3.

**Prefixo:** `/rust/` (legacy) | `/api/v1/rust/` (versionado)

---

## POST `/solve/beam`

Solver de vigas implementado em Rust.

### Request Body — `SolverRequestRS`

| Campo | Tipo | Descrição |
|---|---|---|
| `spans` | list[SpanInputRS] | Definição dos vãos |
| `point_loads` | list[dict] | `[{node_idx, value}]` |
| `fixed_dofs` | list[int] | Graus de liberdade fixos |

### SpanInputRS

| Campo | Tipo | Descrição |
|---|---|---|
| `length` | float | Comprimento do vão (m) |
| `e_gpa` | float | Módulo de elasticidade (GPa) |
| `inertia_m4` | float | Momento de inércia (m⁴) |

### Resposta

```json
{
    "status": "ok",
    "matrix_size": 12,
    "displacements": [0.0, 0.0023, ...]
}
```

---

## POST `/tension-pro/friction-loss`

Cálculo de perda por atrito em cabos de protensão (Rust).

### Request Body — `TensionProRequest`

| Campo | Tipo | Descrição |
|---|---|---|
| `fck` | float | Resistência do concreto (MPa) |
| `p0` | float | Força inicial de protensão (kN) |
| `mu` | float | Coeficiente de atrito angular |
| `k` | float | Coeficiente de atrito por metro |
| `x` | float | Distância ao longo do cabo (m) |
| `theta` | float | Variação angular total (rad) |

### Resposta

```json
{
    "p_x": 975.4
}
```

(`p_x` = força de protensão após perda por atrito na posição x)

---

## Estrutura do Código Rust

```
structural_core_rs/
├── Cargo.toml
├── src/
│   ├── lib.rs                # PyO3 bindings públicos
│   └── radier_winkler.rs     # FEM Radier + solve sparse
├── benches/
│   └── bench_radier.rs       # Benchmarks Criterion
└── .cargo/
    └── config.toml           # macOS linker flags
```

### Dependências (Cargo.toml)

| Crate | Uso |
|---|---|
| `pyo3` | Bindings Python ↔ Rust |
| `numpy` | Arrays NumPy |
| `ndarray` | Matrizes n-dimensionais |
| `faer` | Solve LU esparso |
| `nalgebra` | Álgebra linear geral |
| `rayon` | Paralelismo de dados |

### Compilação

```bash
cd structural_core_rs
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin build --release
pip install target/wheels/*.whl

# Testes
cargo test

# Benchmarks
cargo bench
```
