# Briefing de Retomada - Vento + Estabilidade

**Data:** 2026-05-03  
**Escopo da retomada:** consolidar o ponto atual do `WindEngine`, do acoplamento com estabilidade global e das diretrizes para continuidade posterior.

---

## 1. Estado atual

O módulo de vento foi evoluído de um gerador simples de pressões `z/q_Pa` para um motor com perfil rastreável por nível.

Arquivos principais:
- `wind_engine.py`
- `stability_engine.py`
- `api.py`
- `README.md`
- `TECHNICAL_REFERENCE.md`

O backend FastAPI está com dois endpoints de vento:

| Endpoint | Finalidade |
|:---|:---|
| `POST /calculate/wind` | Calcula perfil completo de vento por nível |
| `POST /calculate/wind-stability` | Calcula vento e alimenta automaticamente a estabilidade global |

---

## 2. WindEngine - recursos implementados

O `WindEngine` agora calcula:
- fator `S2` por nível
- velocidade característica `Vk`
- pressão dinâmica `q`
- coeficiente de arrasto `Cf`
- área tributária por nível
- força média de vento
- força total, com amplificação dinâmica quando habilitada
- momento na base por nível
- resumo com força total, momento total na base, pressão máxima e maior força por nível

Métodos novos/importantes:
- `calculate_wind_speed(z, config)`
- `calculate_s2(z, config)`
- `calculate_level(z, area, cf, config, height=None)`
- `generate_force_profile(...)`

Métodos antigos preservados por compatibilidade:
- `calculate_dynamic_pressure(...)`
- `get_drag_force(...)`
- `generate_vertical_profile(...)`

Observação importante:
- `get_s2_dynamic()` agora aplica piso de `z = 5 m`, evitando pressão zero artificial na base em análises dinâmicas.

---

## 3. Contrato atual de `/calculate/wind`

Payload típico:

```json
{
  "v0": 30,
  "altura_total": 30,
  "largura": 12,
  "profundidade": 18,
  "step": 3,
  "categoria": 2,
  "classe": "B",
  "s1": 1,
  "s3": 1,
  "is_dynamic": false,
  "f1": 0.5,
  "zeta": 0.01
}
```

Saída principal:
- `config`
- `geometry`
- `summary`
- `profile`
- `legacy_profile`

`summary` contém:
- `total_force_N`
- `total_force_kN`
- `base_moment_kNm`
- `max_q_Pa`
- `max_force_level_kN`

`legacy_profile` mantém compatibilidade com consumidores antigos que esperam apenas:
- `z`
- `q_Pa`

---

## 4. Acoplamento vento + estabilidade

Endpoint implementado:

```txt
POST /calculate/wind-stability
```

Payload adicional:

```json
{
  "total_p_kN": 12000,
  "m1_kNm": null
}
```

Lógica de acoplamento:
- `wind.summary.total_force_kN` alimenta `total_h_force_kN`
- `wind.summary.base_moment_kNm` alimenta `m1_kNm`
- se `m1_kNm` vier no payload, ele sobrescreve o momento calculado pelo vento

Saída:
- `wind`: resultado completo do vento
- `stability`: resultado do `StabilityEngine`
- `coupling`: rastreabilidade dos valores transferidos entre motores

Campos importantes de `stability`:
- `gamma_z`
- `is_stable`
- `requires_second_order`
- `p_delta_factor`
- `peak_acceleration_ms2`
- `comfort_status`
- `p_delta_iterations`
- `is_divergent`

---

## 5. Validações realizadas

Comandos executados com sucesso:

```bash
python3 -m py_compile api.py wind_engine.py stability_engine.py
```

Chamadas HTTP testadas:

```bash
curl -s -X POST http://127.0.0.1:8000/calculate/wind \
  -H 'Content-Type: application/json' \
  -d '{"v0":30,"altura_total":10,"largura":12,"profundidade":20,"step":3,"categoria":2,"classe":"B"}'
```

```bash
curl -s -X POST http://127.0.0.1:8000/calculate/wind-stability \
  -H 'Content-Type: application/json' \
  -d '{"v0":30,"altura_total":30,"largura":12,"profundidade":18,"step":3,"categoria":2,"classe":"B","total_p_kN":12000,"f1":0.6}'
```

OpenAPI confirmou a rota:

```txt
/calculate/wind-stability
```

---

## 6. Servidores ao final da sessão

Durante a sessão, os servidores estavam assim:

| Serviço | URL |
|:---|:---|
| Frontend Next.js | `http://localhost:3000` |
| Backend FastAPI | `http://127.0.0.1:8000` |

Se retomar em outra sessão, confirmar processos com:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

E reiniciar, se necessário:

```bash
cd "/Users/elycbarros/DEV2/MEF STRUCTURAL/radier_lab"
python3 api.py
```

```bash
cd "/Users/elycbarros/DEV2/MEF STRUCTURAL/radier_lab_next"
npm run dev
```

---

## 7. Diretrizes para continuar

### Prioridade 1 - Frontend de vento

Criar painel dedicado para vento e estabilidade com:
- inputs de `v0`, altura, largura, profundidade, categoria, classe e passo vertical
- toggle para análise dinâmica
- inputs de `f1`, `zeta` e `total_p_kN`
- cards de força total, momento na base, `qmax`, `Cf`, `gamma_z`, P-Delta e conforto
- tabela resumida por nível
- gráfico simples do perfil `q(z)` e `F(z)`

Recomendação:
- usar `/calculate/wind-stability` como endpoint principal do painel
- manter `/calculate/wind` para análises isoladas ou debug técnico

### Prioridade 2 - Relatório técnico

Integrar os resultados de vento ao `ReportView` e, depois, ao PDF:
- seção "Ações de Vento - NBR 6123"
- premissas de entrada
- resumo de forças
- perfil por nível resumido
- estabilidade global e conforto
- bloco de rastreabilidade `coupling`

### Prioridade 3 - Modularização da API

O arquivo `api.py` está grande. Próxima evolução recomendada:

```txt
radier_lab/
  api.py
  routes/
    wind.py
    stability.py
    frame.py
    special_elements.py
    reports.py
  schemas/
    wind.py
    common.py
```

Diretriz:
- mover rotas sem alterar contratos HTTP
- primeiro extrair vento/estabilidade, porque já estão bem delimitados
- manter `api.py` como ponto de composição do FastAPI

### Prioridade 4 - Revisão técnica do modelo dinâmico

O modelo dinâmico atual é uma aproximação operacional. Antes de usar como entrega normativa forte:
- revisar parâmetros do modelo discreto da NBR 6123
- calibrar `dynamic_factor`
- limitar amplificações exageradas por faixa de validade
- documentar claramente como "modelo aproximado" quando aplicável

---

## 8. Cuidados importantes

- Não quebrar `legacy_profile`, pois demos antigas podem depender de `z/q_Pa`.
- Manter `m1_kNm` sobrescrevível no endpoint integrado.
- Evitar lógica duplicada de vento no frontend; o backend já entrega `summary`, `geometry` e `profile`.
- Ao criar UI, não renderizar tabelas longas sem paginação ou resumo.
- Em relatórios, separar:
  - pressão dinâmica
  - força horizontal
  - momento de tombamento
  - estabilidade global
  - conforto/aceleração

---

## 9. Próximo comando sugerido

Na próxima sessão, começar por:

```bash
python3 -m py_compile api.py wind_engine.py stability_engine.py
```

Depois testar:

```bash
curl -s -X POST http://127.0.0.1:8000/calculate/wind-stability \
  -H 'Content-Type: application/json' \
  -d '{"v0":30,"altura_total":30,"largura":12,"profundidade":18,"step":3,"categoria":2,"classe":"B","total_p_kN":12000,"f1":0.6}'
```

Se estiver tudo OK, seguir para o painel frontend de vento.
