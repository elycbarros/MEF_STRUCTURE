# MEF STRUCTURAL V4.0-ELITE — API Payload Samples

Esta guia fornece exemplos práticos de payloads JSON para os principais endpoints da API, prontos para uso em testes via Postman, Insomnia ou cURL.

---

## 1. Viga Premium (`/calculate/beam`)
Analisa vigas contínuas com não-linearidade física e redistribuição.

```json
{
  "L": 10.0,
  "b": 0.20,
  "h": 0.50,
  "fck": 30.0,
  "caa": 2,
  "supports": [
    {"x": 0.0, "type": "pinned"},
    {"x": 5.0, "type": "pinned"},
    {"x": 10.0, "type": "pinned"}
  ],
  "distributed_loads": [
    {"val": 20.0, "start": 0.0, "end": 10.0, "type": "permanent"},
    {"val": 10.0, "start": 0.0, "end": 10.0, "type": "variable"}
  ],
  "nonlinear": true,
  "redistribution_delta": 0.90
}
```

---

## 2. Pórtico 3D Elite (`/calculate/frame`)
Análise de estabilidade global P-Delta e esforços internos.

```json
{
  "nodes": [
    {"id": "BASE", "x": 0, "y": 0, "z": 0, "fix": [1,1,1,1,1,1]},
    {"id": "TOP", "x": 0, "y": 0, "z": 3.0, "fix": [0,0,0,0,0,0]}
  ],
  "members": [
    {"id": "P1", "node_i": "BASE", "node_j": "TOP", "section": "P30x30"}
  ],
  "loads": [
    {"node": "TOP", "fz": -1000.0, "type": "permanent"},
    {"node": "TOP", "fx": 50.0, "type": "wind"}
  ],
  "p_delta": true
}
```

---

## 3. Pilar e Encurtamento (`/calculate/column`)
Dimensionamento e verificação de deformações elásticas acumuladas.

```json
{
  "b": 0.40,
  "h": 0.40,
  "fck": 40.0,
  "caa": 2,
  "L_free": 3.20,
  "Nd_kN": 2500.0,
  "Mxd_kNm": 45.0,
  "Myd_kNm": 20.0,
  "n_floors_for_shortening": 25
}
```

---

## 4. Combinações NBR 8681 (`/calculate/load-combinations`)
Geração de envoltórias para múltiplas ações.

```json
{
  "actions": [
    {"name": "Peso Proprio", "kind": "permanent", "value": 150.0},
    {"name": "Utilizacao", "kind": "variable", "category": "residential", "value": 80.0},
    {"name": "Vento 0", "kind": "variable", "category": "wind", "value": 40.0},
    {"name": "Vento 90", "kind": "variable", "category": "wind", "value": 35.0}
  ],
  "gamma_g_unfav": 1.4,
  "gamma_q": 1.4,
  "special_situation": false
}
```

---

## 5. Vento e Estabilidade (`/calculate/wind`)
Perfil de vento NBR 6123 integrado com estabilidade global.

```json
{
  "v0": 35.0,
  "altura_total": 60.0,
  "largura": 24.0,
  "profundidade": 18.0,
  "categoria": 3,
  "classe": "C",
  "is_dynamic": true,
  "f1": 0.45
}
```

---

## 6. Radier/Lajes (`/calculate`)
O motor principal de fundação e lajes.

```json
{
  "Lx": 20.0,
  "Ly": 20.0,
  "h": 0.60,
  "fck": 30.0,
  "kv": 25e6,
  "q": 10.0,
  "nx": 21,
  "ny": 21,
  "piles": [
    {"id": "E1", "x": 2.0, "y": 2.0, "k": 500e6},
    {"id": "E2", "x": 18.0, "y": 18.0, "k": 500e6}
  ],
  "columns": [
    {"id": "P1", "x": 10.0, "y": 10.0, "load": 2000.0, "bx": 0.50, "by": 0.50}
  ]
}
```

---

## Dicas Pro
- Use `gamma_g_fav: 1.0` em combinações para verificar efeitos de alívio (ex: vento em reservatórios vazios).
- O parâmetro `caa` (Classe de Agressividade Ambiental) afeta automaticamente o cobrimento e os limites de abertura de fissuras ($w_k$).
- No motor de vento, `is_dynamic: true` ativa o Modelo Discreto da NBR 6123, essencial para edifícios com $H > 40m$ ou esbeltos.
