# MEF STRUCTURAL - Matriz Formal de Validacao

Data: 2026-05-03  
Objetivo: estabelecer a base de validacao necessaria para elevar a plataforma de M3 para M4.

## Criterios de Status

- `APROVADO`: teste automatizado existe e passa dentro da tolerancia.
- `PARCIAL`: existe teste ou evidencia, mas ainda falta benchmark externo, tolerancia formal ou cobertura completa.
- `PENDENTE`: caso necessario ainda nao implementado.
- `ORIENTATIVO`: resultado aceito apenas para apoio preliminar, sem uso profissional direto.

## Contrato Geral de Unidades

| Grandeza | Unidade Padrao | Observacao |
|---|---:|---|
| Comprimento global | m | Geometria, vaos, coordenadas e espessuras |
| Deslocamento de saida | mm | Relatorios, ELS e dashboards |
| Forca concentrada | kN ou N | API de radier usa pilares em kN; frame usa cargas nodais em N |
| Momento | kNm ou N.m | API de elementos usa kNm; frame nodal usa N.m |
| Carga distribuida de area | Pa = N/m² | `q` do radier/laje |
| Pressao do solo | kPa | Relatorios e verificacoes geotecnicas |
| Coeficiente de reacao vertical | N/m³ | `kv` sempre em N/m³ |
| Concreto | MPa | `fck` |
| Aco | MPa | `fyk` |
| Modulo elastico | Pa | `E`, `G` no portico 3D |
| Vento | m/s, Pa, kN | Entrada `v0` em m/s; pressoes em Pa |

## Faixas de Validacao de Entrada

| Campo | Faixa M4 | Unidade | Erro que deve bloquear |
|---|---:|---:|---|
| `fck` | 10 a 120 | MPa | valores como 300 MPa |
| `fyk` | 250 a 700 | MPa | aco fora de faixa usual |
| `h` | 0.05 a 5.0 | m | espessura zero ou negativa |
| `kv` | 1e5 a 1e9 | N/m³ | valor em kN/m³ sem conversao |
| `q` | 0 a 5e6 | Pa | carga negativa ou escala absurda |
| `sigma_adm_kPa` | 1 a 5000 | kPa | tensao nula/negativa |
| `v0` | 1 a 80 | m/s | vento fora de faixa usual NBR |
| `caa` | 1 a 4 | classe | CAA inexistente |
| `gamma_g`, `gamma_q` | 0.8 a 2.0 | adim. | coeficiente parcial incoerente |
| `psi0`, `psi1`, `psi2` | 0 a 1 | adim. | fator de combinacao incoerente |

## Matriz por Modulo

### 1. Radier

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| RAD-001 | Sintetico | Radier retangular 24 x 24 m, Winkler uniforme | Regressao interna `radier_lab_v24` | 5% em `w_max` e `qmax` | Convergencia com `residual_ratio` baixo | PARCIAL |
| RAD-002 | Analitico | Pressao media por carga total / area | Equilibrio estatico | 1% | `pressao_media_kPa` coerente com carga/area | PARCIAL |
| RAD-003 | Normativo | Punção em pilar central | NBR 6118, criterio de punção | 5% | `puncao_ratio_max` rastreavel | PARCIAL |
| RAD-004 | Normativo | Fissuracao ELS-W | NBR 6118, limite `wk` | 0.02 mm | `wk_x_ok` e `wk_y_ok` coerentes | PARCIAL |
| RAD-005 | Comercial | Comparacao com GEO5/SAFE para placa Winkler simples | Benchmark externo a construir | 10% | Recalques e pressoes proximos | PENDENTE |
| RAD-006 | Sintetico | Entrada com `kv=22000` sem conversao | Contrato de unidades | bloqueio | HTTP 422 com mensagem sobre N/m³ | APROVADO |

### 2. Vigas

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| BEAM-001 | Analitico | Viga biapoiada com carga distribuida | Formulas classicas Euler-Bernoulli | 5% em flecha/momento | `max_deflection_mm` e `M_max` coerentes | PARCIAL |
| BEAM-002 | Normativo | Flexao simples com As minima | NBR 6118 | 5% | `As_cm2 >= As_min_cm2` | APROVADO |
| BEAM-003 | Normativo | Cisalhamento com biela comprimida | NBR 6118 | 5% | `biela_status` coerente | PARCIAL |
| BEAM-004 | Normativo | CAA III ajusta cobrimento e `wk_limit` | NBR 6118 durabilidade | exato | `cover_mm=40`, `wk_limit=0.2` | APROVADO |
| BEAM-005 | Sintetico | `fck=300` | Contrato de unidades/faixas | bloqueio | HTTP 422 | APROVADO |
| BEAM-006 | Comercial | Comparacao com Ftool/TQS/Eberick para viga simples | Benchmark externo a construir | 5% | Diagramas e reacoes coerentes | PENDENTE |

### 3. Pilares

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| COL-001 | Sintetico | Pilar curto com N + Mx + My | Regressao interna | 5% | Retorno de As e esbeltez | APROVADO |
| COL-002 | Normativo | Esbeltez local | NBR 6118 | classificacao | `needs_2nd_order_x/y` coerente | PARCIAL |
| COL-003 | Normativo | CAA IV define cobrimento minimo | NBR 6118 durabilidade | exato | `cover_required_mm=50` | APROVADO |
| COL-004 | Analitico | Encurtamento elastico simples | Lei de Hooke | 5% | `elastic_mm` coerente | PARCIAL |
| COL-005 | Comercial | Comparacao com software de pilar para diagrama N-M-M | Benchmark externo a construir | 10% | As proxima para caso padrao | PENDENTE |

### 4. Portico 3D

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| FRM-001 | Analitico | Cantilever 3D com carga lateral no topo | `delta = F H³ / 3EI` | 1% | deslocamento FEM coerente | APROVADO |
| FRM-002 | Sintetico | P-Delta aumenta ou mantem deslocamento lateral | Regressao interna | monotonicidade | `d2 >= 0.9 d1` | APROVADO |
| FRM-003 | Normativo | Gamma-z por deslocamento nodal | NBR 6118 conceitual | classificacao | classe `NAO_SENSIVEL/SENSIVEL/INSTAVEL` | APROVADO |
| FRM-004 | Sintetico | Endpoint `/calculate/frame` usa motor premium | Contrato API V4 | exato | `PORTICO_3D_PREMIUM_P_DELTA` | APROVADO |
| FRM-005 | Analitico | Esforcos internos N, V, M por barra | Formulas classicas | 5% | diagramas locais completos | PENDENTE |
| FRM-006 | Comercial | Comparacao SAP2000/Robot para portico plano | Benchmark externo a construir | 5% | deslocamentos e esforcos proximos | PENDENTE |

### 5. Vento

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| WIND-001 | Normativo | Pressao dinamica `q = 0.613 Vk²` | NBR 6123 | 1% | `q_Pa` coerente | PARCIAL |
| WIND-002 | Normativo | Categoria de rugosidade altera S2 | NBR 6123 | 5% | S2 cresce/reduz conforme categoria | PARCIAL |
| WIND-003 | Sintetico | `v0=120` | Contrato de entrada | bloqueio | HTTP 422 | APROVADO |
| WIND-004 | Comercial | Comparacao com exemplo normativo completo | Exemplo NBR/literatura | 5% | perfil por nivel coerente | PENDENTE |

### 6. Estabilidade

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| STAB-001 | Sintetico | Edificio rigido nao sensivel | Regressao interna | classificacao | `gamma_z < 1.30` | APROVADO |
| STAB-002 | Sintetico | Edificio esbelto sensivel | Regressao interna | classificacao | `requires_second_order=True` ou `gamma_z>1` | APROVADO |
| STAB-003 | Conceitual | Cantilever equivalente vs portico real | Comparacao interna | 10% | diferenca documentada | PENDENTE |
| STAB-004 | Comercial | Benchmark ETABS/SAP2000 para 2a ordem | Benchmark externo a construir | 5% | gamma-z/P-Delta proximos | PENDENTE |

### 7. Combinações

| ID | Tipo | Caso de Teste | Referencia | Tolerancia Aceita | Resultado Esperado | Status |
|---|---|---|---|---:|---|---|
| COMB-001 | Normativo | `G=100`, `Q=30`, gamma=1.4 | NBR 8681 simplificada | exato | ELU = 182 | APROVADO |
| COMB-002 | Normativo | ELS frequente com `psi1=0.4` | NBR 8681 | exato | ELS freq = 112 | APROVADO |
| COMB-003 | Normativo | ELS quase permanente com `psi2=0.3` | NBR 8681 | exato | ELS QP = 109 | APROVADO |
| COMB-004 | Sintetico | `psi0=1.5` | Contrato de entrada | bloqueio | HTTP 422 | APROVADO |
| COMB-005 | Normativo | Multiplas variaveis alternando principal | NBR 8681 | exato | caso governante identificado | PARCIAL |
| COMB-006 | Produto | Envoltoria por elemento | Fluxo profissional | 5% | esforco governante por elemento | PENDENTE |

## Pendencias Para M4 Pleno

1. Adicionar benchmarks externos para radier, viga, portico e estabilidade.
2. Formalizar exemplos normativos de vento com referencias de calculo.
3. Implementar esforcos internos completos no portico 3D.
4. Criar snapshots de resultados esperados por modulo.
5. Publicar exemplos oficiais de payload e resposta por endpoint.
6. Consolidar tratamento de erro padronizado alem do 422 automatico.
7. Adicionar validacao de consistencia geometrica, como pilar fora do radier e barras com nos inexistentes.
