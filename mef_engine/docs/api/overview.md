# Visão Geral da API

## Todos os Endpoints

Total: **47 endpoints** em 15 arquivos de rota.

### Health, Cache e Metadados

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/` | Raiz — versão, status, módulos |
| `GET` | `/api/health` | Status do servidor + Rust + cache |
| `GET` | `/api/v1/health` | (versionado) |
| `GET` | `/api/info` | Metadados da aplicação |
| `GET` | `/api/v1/info` | (versionado) |
| `GET` | `/api/versions` | Versões disponíveis da API |
| `GET` | `/api/cache/stats` | Estatísticas do cache LRU |
| `GET` | `/api/v1/cache/stats` | (versionado) |
| `POST` | `/api/cache/clear` | Limpa o cache |
| `POST` | `/api/v1/cache/clear` | (versionado) |

### Projetos

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/projects` | Lista projetos salvos |
| `POST` | `/projects` | Cria novo projeto |
| `GET` | `/projects/{id}/history` | Histórico do projeto |

### Modo Mestre (prefixo: `/api/mestre/` ou `/api/v1/mestre/`)

| Método | Path | Arquivo | Descrição |
|---|---|---|---|
| `POST` | `/calculate` | core.py | Motor principal — análise de radier/laje |
| `POST` | `/estimate_loads` | core.py | Estimativa preliminar de cargas (NBR 6120) |
| `POST` | `/optimize_design` | core.py | Otimização iterativa de espessura |
| `POST` | `/frame/analyze` | mestre_frame.py | Análise pedagógica de pórtico 3D |
| `POST` | `/check/compliance` | special.py | Verificação de durabilidade (cobrimento, fogo) |
| `POST` | `/optimize/structural` | special.py | Otimização de elemento estrutural |
| `POST` | `/calculate/special-elements` | special.py | Elementos especiais (escada, laje, viga, pilar, etc.) |
| `POST` | `/calculate/spt` | special.py | Análise de sondagem SPT |
| `POST` | `/calculate/stability-mestre` | special.py | Estabilidade + vento (pedagógico) |
| `POST` | `/generate/professional-memorial` | special.py | Memorial descritivo profissional PDF |
| `POST` | `/generate/exam-auditor-memorial` | special.py | Memorial de auditoria de prova PDF |
| `POST` | `/calculate/integrated-foundation` | special.py | Solução integrada SPT + fundação |
| `POST` | `/export/pdf` | reports.py | Relatório profissional radier PDF |
| `POST` | `/export/academic/beam` | reports.py | Memorial acadêmico de viga PDF |
| `POST` | `/export/academic/column` | reports.py | Memorial acadêmico de pilar PDF |
| `POST` | `/export/vigacross/pdf` | reports.py | Memorial técnico VigaCross PDF |
| `POST` | `/export/academic/spt` | reports.py | Memorial geotécnico SPT PDF |
| `POST` | `/export/academic/stability` | reports.py | Memorial estabilidade/vento PDF |
| `POST` | `/calculate/load-combinations` | loads.py | Combinações de carga (NBR 8681) |

### Modo UFO (prefixo: `/api/ufo/` ou `/api/v1/ufo/`)

| Método | Path | Arquivo | Descrição |
|---|---|---|---|
| `POST` | `/calculate/frame/modal` | frame.py | Análise modal assíncrona |
| `GET` | `/calculate/frame/modal/{job_id}` | frame.py | Resultado da análise modal |
| `POST` | `/calculate/frame` | frame.py | Análise síncrona de pórtico 3D Premium |
| `POST` | `/calculate/frame/async` | frame.py | Análise assíncrona de pórtico 3D |
| `GET` | `/calculate/jobs/{job_id}` | frame.py | Status de job assíncrono |
| `POST` | `/calculate/stability` | stability.py | Estabilidade avançada (Gama-Z, conforto, vórtice) |
| `POST` | `/calculate/stability-dashboard` | stability.py | Dashboard unificado (vento + estabilidade + sísmico) |
| `POST` | `/calculate/wind` | wind.py | Perfil de vento (NBR 6123) |
| `POST` | `/calculate/wind-stability` | wind.py | Vento + estabilidade acoplados |
| `POST` | `/seismic/analyze` | seismic.py | Análise sísmica (espectro de resposta) |
| `POST` | `/ssi/pile-nonlinear` | ssi.py | Análise não-linear de estaca (curvas p-y) |
| `POST` | `/detailing/global-summary` | ufo_detailing.py | Detalhamento executivo global |

### Módulos Elite (prefixo: `/api/ufo/`)

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/calculate/beam` | Análise completa de viga (MEF + dimensionamento) |
| `POST` | `/calculate/column` | Dimensionamento completo de pilar |
| `POST` | `/calculate/building-core` | Análise de núcleo rígido (elevador, escada) |
| `POST` | `/calculate/concrete_wall` | Dimensionamento de parede de concreto |
| `POST` | `/calculate/frame-legacy` | Pórtico 3D via StrucPy (legado) |
| `POST` | `/calculate_v2_unified` | Pipeline unificado Pórtico → Radier |
| `POST` | `/optimize` | Otimização genética |
| `POST` | `/copilot/diagnose` | Diagnóstico AI Copilot |
| `POST` | `/estimate_loads` | Estimativa de cargas NBR 6120 |

### Forense e Incerteza

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/forensic/monte-carlo` | Simulação Monte Carlo |
| `POST` | `/forensic/calibrate` | Calibração de kv com medições reais |

### PhD (Autonomous Engine)

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/phd/predict_fast` | Predição ultrarrápida via ML surrogate |
| `POST` | `/phd/auto_design` | Agente autônomo de otimização |
| `GET` | `/phd/distributed_status` | Status do cluster distribuído |

### Rust Core (prefixo: `/rust/` ou `/api/v1/rust/`)

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/solve/beam` | Solver de viga nativo Rust |
| `POST` | `/tension-pro/friction-loss` | Perda por atrito em protensão (Rust) |

## Segurança

### Autenticação

| Variável | Padrão | Descrição |
|---|---|---|
| `MEF_AUTH_ENABLED` | `0` | Habilita verificação de API Key |
| `MEF_API_KEY` | `dev-key-2024` | Chave esperada no header |

Header: `X-API-Key: <chave>`

Endpoints isentos: health, info, versions, root.

### Rate Limiting

| Variável | Padrão | Descrição |
|---|---|---|
| `MEF_RATE_LIMIT_ENABLED` | `0` | Habilita rate limiting |
| `MEF_RATE_LIMIT_DEFAULT` | `100/minute` | Limite global |
| `MEF_RATE_LIMIT_BURST` | `200/minute` | Burst máximo |

## Formato de Resposta

### Sucesso

```json
{
    "success": true,
    "result": { ... },
    "summary": { ... }
}
```

### Erro

```json
{
    "error": {
        "code": "EST-001",
        "type": "estabilidade",
        "message": "Estrutura instável — Gama-Z > 1.30",
        "detail": "γz calculado = 1.45, reduzir carga ou aumentar rigidez",
        "module": "stability_engine"
    }
}
```

### Resposta Customizada: MsgPack

Quando `Accept: application/x-msgpack` é enviado, a API retorna
MsgPack em vez de JSON (~40% menor).
