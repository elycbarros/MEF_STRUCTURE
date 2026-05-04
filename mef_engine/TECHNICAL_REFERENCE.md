# Documentação Técnica — MEF STRUCTURAL API V4.0-ELITE

## Referência Técnica e Normativa

Este documento detalha os parâmetros de entrada, saída, hipóteses e limitações de cada motor do ecossistema **MEF STRUCTURAL**. Todas as implementações seguem rigorosamente as normas brasileiras (ABNT NBR).

---

## Escopo e Maturidade (M4-ELITE)

Para garantir o uso correto da ferramenta, o escopo de cada módulo é classificado conforme sua maturidade:

| Módulo | Status | Descrição do Escopo |
| :--- | :--- | :--- |
| **Radier Liso** | **Calculado** | Verificação rigorosa de flexão, punção e geotecnia. |
| **Vigas Contínuas** | **Calculado** | Dimensionamento ELU e ELS (Flechas e Fissuras). |
| **Pórtico 3D** | **Calculado** | Esforços globais e estabilidade P-Delta. |
| **Radier Estaqueado** | **Orientativo** | Estimativa de interação solo-estaca (simplificado). |
| **Encurtamento Colunas**| **Orientativo** | Previsão teórica de encurtamento elástico acumulado. |
| **BIM / IFC** | **Experimental** | Exportação de geometria para compatibilização. |

> [!IMPORTANT]
> Resultados classificados como **Orientativos** devem ser validados por análise complementar detalhada antes da execução.

---

## 1. Motores de Cálculo Principais

### 1.1 Radier e Lajes (`RadierSolverM4`)
**Propósito:** Resolução de placas de concreto sobre fundação elástica (Winkler) ou apoios discretos (Lajes).

| Campo | Unidade | Descrição |
|:---|:---|:---|
| `Lx`, `Ly` | m | Dimensões da placa |
| `h` | m | Espessura da placa |
| `kv` | N/m³ | Coeficiente de reação vertical do solo |
| `piles` | list | Lista de estacas (apoios elásticos pontuais) |

**Hipóteses:**
- Teoria de Placas de Mindlin-Reissner (considera deformação por cortante).
- Solo modelado como molas lineares (Winkler) com opção *tensionless* (não resiste à tração).
- Interação Solo-Estrutura (SSI) avançada via matriz de rigidez da superestrutura.

**Limitações:**
- Não considera não-linearidade física do solo (apenas elasto-plástico simplificado).
- Malha retangular regular (nx × ny).

---

### 1.2 Pórtico 3D Premium (`Frame3DEngine`)
**Propósito:** Análise matricial de estruturas espaciais com efeitos globais de 2ª ordem.

**Entradas:**
- `nodes`: Coordenadas X, Y, Z e condições de contorno (engaste, apoio).
- `members`: Conectividade, seções transversais (E, I, J, A).
- `loads`: Cargas nodais e distribuídas em coordenadas globais ou locais.

**Capacidades V4:**
- **P-Delta Iterativo**: Consideração rigorosa da instabilidade geométrica.
- **Extração de Esforços**: $N, V_y, V_z, T, M_y, M_z$ em qualquer ponto da barra.
- **Equilíbrio Global**: Verificação de resíduo de forças para auditoria (tolerância < 0.001 kN).

**Saída de Auditoria (`FrameResult`):**
- `member_efforts`: Esforços internos por barra (kN, kNm).
- `top_displacement_mm`: Deslocamento horizontal no topo do edifício.
- `gamma_z`: Coeficiente de estabilidade global.
- `equilibrium`: Relatório de resíduos de forças por nó.

---

### 1.3 Dimensionamento de Vigas (`BeamSolverM4`)
**Propósito:** Análise de vigas contínuas com redistribuição plástica e verificação de fissuração.

**Parâmetros de Entrada:**
- `caa`: Classe de Agressividade Ambiental (1 a 4).
- `nonlinear`: Ativa inércia efetiva (Branson) para cálculo de flechas reais.
- `redistribution_delta`: Fator $\delta$ (0.75 a 1.00) conforme NBR 6118.

**Saída de Auditoria (`BeamResult`):**
- `moments_kNm`: Vetor de momentos fletores ao longo da viga.
- `as_required_cm2`: Armadura longitudinal calculada.
- `wk_mm`: Abertura de fissuras estimada.
- `deflection_max_mm`: Flecha máxima considerando inércia fissurada.
- `memorial_markdown`: Documento completo para auditoria.

---

### 1.4 Pilares e Encurtamento (`ColumnSolverM4`)
**Propósito:** Dimensionamento de pilares à flexão composta oblíqua e estimativa de encurtamento elástico em edifícios altos.

**Hipóteses:**
- Consideração de imperfeições geométricas locais e globais.
- Efeito de 2ª ordem local via método do pilar padrão com curvatura aproximada.
- Estimativa de encurtamento acumulado pavimento a pavimento.

---

## 2. Motores Auxiliares e Normas

### 2.1 Combinações NBR 8681 (`LoadCombinatorV4`)
O sistema gera envoltórias automáticas para todos os elementos estruturais.

| Tipo | Coeficientes | Descrição |
|:---|:---|:---|
| **ELU Normal** | $\gamma_G=1.4, \gamma_Q=1.4$ | Fundamental para segurança estrutural |
| **ELU Especial** | $\gamma_G=1.3, \gamma_Q=1.2$ | Situações de construção ou transitórias |
| **ELS Quase Perm.** | $\psi_2 \cdot Q_k$ | Verificação de flechas e danos permanentes |
| **ELS Frequente** | $\psi_1 \cdot Q_k$ | Verificação de fissuração e conforto |

### 2.2 Vento NBR 6123 (`WindEngineM4`)
**Modelo:** Estático e Dinâmico (Modelo Discreto).
- Gera perfil de pressões dinâmicas $q(z)$.
- Calcula forças horizontais por pavimento e momento de tombamento total.
- Integração direta com o motor de Estabilidade Global ($\gamma_z$).

---

## 3. Exemplos de Payloads (API ready-to-use)

### 3.1 Viga Contínua Premium
```json
{
  "L": 12.0,
  "b": 0.20,
  "h": 0.60,
  "fck": 30.0,
  "caa": 2,
  "supports": [
    {"x": 0.0, "type": "pinned"},
    {"x": 6.0, "type": "pinned"},
    {"x": 12.0, "type": "pinned"}
  ],
  "distributed_loads": [
    {"val": 25.0, "start": 0.0, "end": 12.0, "type": "permanent"}
  ],
  "nonlinear": true
}
```

### 3.2 Pórtico 3D (Pavimento Tipo)
```json
{
  "nodes": [
    {"id": "N1", "x": 0, "y": 0, "z": 0, "fix": [1,1,1,1,1,1]},
    {"id": "N2", "x": 5, "y": 0, "z": 3, "fix": [0,0,0,0,0,0]}
  ],
  "members": [
    {"id": "B1", "node_i": "N1", "node_j": "N2", "section": "P20x40"}
  ],
  "loads": [
    {"node": "N2", "fz": -150.0, "type": "permanent"}
  ],
  "p_delta": true
}
```

### 3.3 Combinações NBR 8681
```json
{
  "actions": [
    {"name": "G", "kind": "permanent", "value": 100.0},
    {"name": "Q_res", "kind": "variable", "category": "residential", "value": 50.0},
    {"name": "Vento", "kind": "variable", "category": "wind", "value": 30.0}
  ],
  "gamma_g_unfav": 1.4,
  "gamma_q": 1.4
}
```

---

## 4. Limitações Gerais do Sistema

1. **Materiais**: Assume comportamento linear-elástico para análise global de esforços. Não-linearidade física disponível apenas nos módulos de Viga e Radier (Branson/Estádio II).
2. **Geometria**: Elementos de barra (1D) e placa (2D). Não suporta elementos de volume (3D Solid).
3. **Dinâmica**: Análise dinâmica limitada ao vento (NBR 6123). Não realiza análise sísmica ou de vibrações induzidas por pessoas (conforto) além do simplificado.

---

## 5. Tratamento de Erros Profissional

A plataforma MEF STRUCTURAL utiliza um sistema de erro padronizado para garantir auditoria e clareza diagnóstica.

### Formato de Resposta de Erro
```json
{
  "error": {
    "code": "STRING_ID",
    "type": "CLASSIFICAÇÃO",
    "message": "Mensagem clara ao usuário",
    "detail": "Detalhes técnicos (opcional)",
    "module": "módulo_origem"
  }
}
```

### Classificação de Erros
| Tipo | Código Exemplo | Descrição |
| :--- | :--- | :--- |
| **Entrada Inválida** | `VAL-001` | Parâmetros geométricos ou materiais fora dos limites normativos. |
| **Modelo Instável** | `STB-001` | Estrutura hipostática, singularidade de matriz ou instabilidade global. |
| **Falha Numérica** | `NUM-001` | Divergência em processos iterativos (P-Delta, SSI, Tração). |
| **Fora de Escopo** | `SCP-001` | Solicitação de recurso não implementado ou além dos limites do motor. |
| **Erro Interno** | `INT-500` | Falha inesperada no ambiente de execução ou sistema de arquivos. |

---

## Referências Bibliográficas

1. **ABNT NBR 6118:2023** — Projeto de estruturas de concreto — Procedimento.
2. **ABNT NBR 6122:2022** — Projeto e execução de fundações.
3. **ABNT NBR 6123:1988** — Forças devidas ao vento em edificações.
4. **ABNT NBR 8681:2003** — Ações e segurança nas estruturas — Procedimento.
5. **Cook, R. D.** — *Concepts and Applications of Finite Element Analysis*.
6. **Park & Paulay** — *Reinforced Concrete Structures*.
7. **Bowles, J.E.** — *Foundation Analysis and Design*.

---
*Documentação atualizada em 2026-05-03 para MEF STRUCTURAL V4.0.0-ELITE*
