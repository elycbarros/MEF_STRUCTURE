# Validação

## Matriz de Validação

8 benchmarks de referência validam a precisão do motor.

| Código | Descrição | Fonte | Status |
|---|---|---|---|
| RAD‑001 | Radier Mindlin Winkler v2 (carga uniforme) | Manual analítico | ✅ |
| RAD‑002 | Radier — convergência de malha (L2) | Análise de refinamento | ✅ |
| RAD‑003 | Placa Timoshenko — validação de rigidez | Timoshenko & Woinowsky-Krieger | ✅ |
| RAD‑004 | Fundação Hetenyi — viga infinita em base elástica | Hetenyi (1946) | ✅ |
| BEAM‑001 | Viga biapoiada — flecha analítica Euler-Bernoulli | Resistência dos Materiais | ✅ |
| BEAM‑002 | Viga contínua — momentos NBR 6118 | NBR 6118:2014 | ✅ |
| FRAME‑001 | Pórtico 2D — verificação de equilíbrio | Estática das Estruturas | ✅ |
| FRAME‑002 | Cantilever Euler-Bernoulli — flecha de ponta | SAP2000 (referência) | ✅ |
| FRAME‑003 | Pórtico 2 pavimentos — análise modal | SAP2000 (referência) | ✅ |
| WIND‑001 | Perfil S2 — comparação com NBR 6123 Tabela 1 | NBR 6123:1988 | ✅ |
| WIND‑002 | Força global de vento — edifício retangular | NBR 6123:1988 | ✅ |

## Benchmarks de Performance

### Rust Assembly (Criterion)

```bash
cd structural_core_rs
cargo bench
```

| Malha | Tempo de Montagem |
|---|---|
| 13×13 | 211 µs |
| 25×25 | 825 µs |
| 50×50 | 3.2 ms |

Relatório HTML: `structural_core_rs/target/criterion/report/index.html`

### Testes de Velocidade (pytest)

```bash
pytest tests/test_radier_rs_benchmark.py -v
```

| Teste | Critério | Status |
|---|---|---|
| Rust assembly matches Python | Erro < 1e-10 | ✅ |
| Rust assembly speed | ≥ 2× Python | ✅ (3.6× real) |
