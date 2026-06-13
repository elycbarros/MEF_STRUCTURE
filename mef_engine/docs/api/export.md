# Exportação

## BIM/CSV

### POST `/api/ufo/export/bim-csv`

Exporta resultados de análise em formato CSV dentro de um arquivo ZIP.

**Request Body**: raw dict com resultados da análise.

**Resposta**: `StreamingResponse` (ZIP) — `application/zip`

Conteúdo do ZIP:
- `esforcos_barras.csv` — Esforços internos por barra
- `deslocamentos_nodais.csv` — Deslocamentos dos nós
- `reacoes_apoio.csv` — Reações de apoio
- `metadados.json` — Metadados do projeto

### POST `/api/ufo/export/bim-manifest`

Manifesto BIM com sumário completo dos resultados exportáveis.

**Resposta**: JSON com sumário estruturado.

---

## DXF

### POST `/api/ufo/export/dxf/radier`

Desenho técnico do radier em formato DXF.

**Camadas geradas:**
| Layer | Conteúdo | Cor |
|---|---|---|
| `ARMAÇÃO_INFERIOR_X` | Armadura inferior direção X | Cyan |
| `ARMAÇÃO_INFERIOR_Y` | Armadura inferior direção Y | Blue |
| `ARMAÇÃO_SUPERIOR_X` | Armadura superior direção X | Yellow |
| `ARMAÇÃO_SUPERIOR_Y` | Armadura superior direção Y | Red |

### POST `/api/ufo/export/dxf/slab`

Desenho de laje em DXF.

---

## PDF (Relatórios)

### POST `/api/mestre/export/pdf`

Relatório profissional de radier em PDF.

| Campo | Tipo | Descrição |
|---|---|---|
| `results` | dict | Resultados da análise |
| `project_meta` | dict | Metadados do projeto |
| `wind_results` | dict | Resultados de vento (opcional) |
| `stability_results` | dict | Resultados de estabilidade (opcional) |

### POST `/api/mestre/export/academic/beam`

Memorial acadêmico de análise de viga em PDF.
**Request Body:** `BeamAnalysisRequest`

### POST `/api/mestre/export/academic/column`

Memorial acadêmico de dimensionamento de pilar em PDF.
**Request Body:** `ColumnRequest`

### POST `/api/mestre/export/academic/stability`

Memorial de estabilidade e vento em PDF.

| Campo | Tipo | Padrão |
|---|---|---|
| `v0` | float | 30.0 |
| `height` | float | 30.0 |
| `width_x` | float | 12.0 |
| `s1` | float | 1.0 |
| `s3` | float | 1.0 |
| `categoria` | int | 2 |
| `classe` | str | "B" |

### POST `/api/mestre/export/academic/spt`

Memorial geotécnico de sondagem SPT em PDF.

### POST `/api/mestre/generate/professional-memorial`

Memorial descritivo profissional em PDF.

### POST `/api/mestre/generate/exam-auditor-memorial`

Memorial de auditoria de prova (exame) em PDF.

---

## Formato MsgPack

A API suporta resposta em MsgPack quando o header
`Accept: application/x-msgpack` é enviado.

| Formato | Content-Type | Tamanho |
|---|---|---|
| JSON | `application/json` | 100% (referência) |
| MsgPack | `application/x-msgpack` | ~60% do JSON |

Ativado nos endpoints:
- `POST /calculate/frame`
- `GET /calculate/jobs/{job_id}`
