# Relatório de Validação — Atlas Structural Engine

**Data:** 13/06/2026 10:38
**Versão da Matriz:** 6.4.0
**Python:** 3.14.2
**Benchmarks:** 13
**Aprovados:** 13
**Taxa de Sucesso:** 100.0%
**Tempo Total:** 902.05ms

## Resumo

| Módulo | ID | Nome | Status | Erro |
|--------|----|------|--------|------|
| slab | SLAB-001 | Laje Suspensa com 4 Pilares (Carga Uniforme) | ✅ Pass | reaction_total_kN=500.0, equilibrium_error_pct=0.0 |
| column | COLUMN-001 | Pilar Curto sob Compressão Centrada (NBR 6118) | ✅ Pass | n_rd_kN=1987.1, atende=True |
| column | COLUMN-002 | Esbeltez e Limite de Dispensa (NBR 6118) | ✅ Pass | lambda=34.6, lambda_limite=41.7, dispensa_2a_ordem=True |
| rad | RAD-001 | Placa Rígida sobre Solo Elástico (Carga Uniforme) | ✅ Pass | pressao_media_kPa=10.0, recalque_medio_mm=1.0 |
| rad | RAD-002 | Punção em Laje Espessa (Caso Central) | ✅ Pass | tau_rd1_min=0.65, atende=True |
| rad | RAD-003 | Placa Mindlin Apoiada em Quatro Bordos (Carga Unif | ✅ Pass | w_centro_mm=5.78, Mx_centro_kNm_m=44.21 |
| rad | RAD-004 | Radier sobre Winkler com Carga Concentrada | ✅ Pass | w_max_mm=1.456 |
| beam | BEAM-001 | Viga Bi-apoiada Carga Uniforme | ✅ Pass | moment_max_kNm=62.5, shear_max_kN=50.0 |
| beam | BEAM-002 | Viga Contínua de 3 Vãos (Carga Distribuída) | ✅ Pass | M_apoio_B_kNm=89.89, M_vao_central_kNm=75.5 |
| frame | FRAME-001 | Pórtico Simples P-Delta (Benchmark de Estabilidade | ✅ Pass | gamma_z=1.0, is_stable=True |
| frame | FRAME-002 | Cantilever Euler-Bernoulli (Carga na Ponta) | ✅ Pass | w_ponta_mm=10.667, M_base_kNm=40.0 |
| frame | FRAME-003 | Pórtico de 2 andares (Análise Modal) | ✅ Pass |  |
| wind | WIND-001 | Perfil de Pressão NBR 6123 (Edifício 30m, Categori | ✅ Pass | s2_topo=1.094, q_top_Pa=660.1 |

## Detalhamento por Benchmark

### SLAB-001: Laje Suspensa com 4 Pilares (Carga Uniforme)
- **Execução:** 108.16ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| reaction_total_kN | 500.0 | 500.0 | 0.0 | ✅ |
| equilibrium_error_pct | 0.0 | 0.1 | 0.0 | ✅ |

---

### COLUMN-001: Pilar Curto sob Compressão Centrada (NBR 6118)
- **Execução:** 0.3ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| n_rd_kN | 1987.1 | 1987.1 | 0.0 | ✅ |
| atende | True | True | 0 | ✅ |

---

### COLUMN-002: Esbeltez e Limite de Dispensa (NBR 6118)
- **Execução:** 0.3ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| lambda | 34.6 | 34.6 | 0.0 | ✅ |
| lambda_limite | 41.7 | 41.7 | 0.0 | ✅ |
| dispensa_2a_ordem | True | True | 0 | ✅ |

---

### RAD-001: Placa Rígida sobre Solo Elástico (Carga Uniforme)
- **Execução:** 90.22ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| pressao_media_kPa | 10.0 | 10.0 | 0.0 | ✅ |
| recalque_medio_mm | 1.0 | 1.0 | 0.0 | ✅ |

---

### RAD-002: Punção em Laje Espessa (Caso Central)
- **Execução:** 0.5ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| tau_rd1_min | 0.65 | 0.65 | 0.0 | ✅ |
| atende | True | True | 0 | ✅ |

---

### RAD-003: Placa Mindlin Apoiada em Quatro Bordos (Carga Uniforme)
- **Execução:** 1.0ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| w_centro_mm | 5.78 | 5.78 | 0.0 | ✅ |
| Mx_centro_kNm_m | 44.21 | 44.2 | 0.023 | ✅ |

---

### RAD-004: Radier sobre Winkler com Carga Concentrada
- **Execução:** 684.45ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| w_max_mm | 1.456 | 1.55 | 6.065 | ✅ |

---

### BEAM-001: Viga Bi-apoiada Carga Uniforme
- **Execução:** 4.06ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| moment_max_kNm | 62.5 | 62.5 | 0.0 | ✅ |
| shear_max_kN | 50.0 | 50.0 | 0.0 | ✅ |

---

### BEAM-002: Viga Contínua de 3 Vãos (Carga Distribuída)
- **Execução:** 3.36ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| M_apoio_B_kNm | 89.89 | 90.0 | 0.125 | ✅ |
| M_vao_central_kNm | 75.5 | 75.0 | 0.667 | ✅ |

---

### FRAME-001: Pórtico Simples P-Delta (Benchmark de Estabilidade)
- **Execução:** 2.38ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| gamma_z | 1.0 | 1.05 | 4.762 | ✅ |
| is_stable | True | True | 0 | ✅ |

---

### FRAME-002: Cantilever Euler-Bernoulli (Carga na Ponta)
- **Execução:** 1.34ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| w_ponta_mm | 10.667 | 10.67 | 0.031 | ✅ |
| M_base_kNm | 40.0 | 40.0 | 0.0 | ✅ |

---

### FRAME-003: Pórtico de 2 andares (Análise Modal)
- **Execução:** 5.89ms
- **Status:** ✅ Aprovado

---

### WIND-001: Perfil de Pressão NBR 6123 (Edifício 30m, Categoria II, Classe B)
- **Execução:** 0.09ms
- **Status:** ✅ Aprovado

| Verificação | Obtido | Esperado | Erro (%) | Resultado |
|-------------|--------|----------|----------|-----------|
| s2_topo | 1.094 | 1.094 | 0.018 | ✅ |
| q_top_Pa | 660.1 | 660 | 0.015 | ✅ |

---
