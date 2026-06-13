# Testes

## Suíte de Testes

**70 testes** distribuídos em 6 arquivos:

| Arquivo | Testes | O que cobre |
|---|---|---|
| `tests/test_structural_suite.py` | 52 | Rotas, solvers, building core, radier |
| `tests/test_solver_audit.py` | 7 | Solver de pilar, estabilidade |
| `tests/test_regression_snapshots.py` | 2 | Regressão de viga e pórtico |
| `tests/test_radier_rs_benchmark.py` | 2 | Benchmark Rust (precisão + velocidade) |
| `tests/test_property_based.py` | 7 | Testes baseados em propriedades (Hypothesis) |

## Executando

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=. --cov-report=term

# Testes específicos
pytest tests/test_property_based.py -v
pytest tests/test_radier_rs_benchmark.py -v
pytest tests/test_structural_suite.py::TestAPIRoutes -v
```

## Testes por Propriedade (Hypothesis)

7 testes baseados em propriedades usando a biblioteca Hypothesis:

| Teste | Propriedade |
|---|---|
| `test_radier_global_equilibrium` | Soma reações de apoio = carga aplicada |
| `test_beam_global_equilibrium` | Equilíbrio de viga biapoiada |
| `test_radier_monotonic_stiffness` | Aumentar rigidez → reduzir deslocamento |
| `test_radier_linear_superposition` | Carga dobra → deslocamento dobra |
| `test_gamma_z_monotonic` | Mais carga → maior γz |
| `test_wind_pressure_positive` | Pressão dinâmica sempre > 0 |
| `test_radier_symmetry_uniform_load` | Malha simétrica → deslocamentos simétricos |

## CI/CD (GitHub Actions)

O workflow de CI (`ci.yml`) tem 3 jobs paralelos:

### Job `lint`
- Ruff check
- Ruff format (dry-run)

### Job `test-python`
- Build wheel Rust com maturin
- pytest com cobertura
- Validação de startup da API

### Job `test-rust`
- cargo test (unit + integração)
- cargo check (compilação)
