# MEF STRUCTURAL (ATLAS) — Planejamento Estratégico e de Produto (M4+)

> **"Não somos o software onde você desenha a estrutura. Somos a inteligência na nuvem que audita, otimiza o custo e valida a segurança do seu projeto estrutural."**

---

## 1. Visão de Produto e Posicionamento

O mercado de software de engenharia civil é dominado por plataformas desktop legadas (TQS, Eberick, Cypecad) e generalistas de análise numérica pesada (SAP2000, Robot, ANSYS). O **MEF STRUCTURAL (ATLAS)** não busca concorrer no desenvolvimento de geometrias do zero ou detalhamento de pranchas finais (CAD). 

Nossa tese é que a engenharia moderna precisa de **Inteligência, Agilidade na Nuvem e Transparência**. O ATLAS posiciona-se como um **Hub Headless de Auditoria e Otimização Paramétrica**, projetado para ser consumido por humanos (via web dashboards ricos) e por IAs (via APIs estruturadas).

---

## 2. Os 4 Pilares de Diferenciação de Produto

### Pilar A: Otimização de Consumo Financeiro (Cost-Driven Optimization)
Ao contrário das ferramentas tradicionais, que apenas verificam se uma seção passa ou falha, o ATLAS executa varreduras de otimização em tempo recorde utilizando seu solver em Rust (`faer`):
* **Otimização Multicritério:** Variação automática de espessura de radier ($h$), rigidez do solo ($k_v$), bitolas de armadura e $f_{ck}$ do concreto para encontrar o **menor custo de material** garantindo 100% de segurança normativa.
* **Simulação de Sensibilidade Geotécnica:** Análise de variação de recalques e pressões de contato para evitar superdimensionamento por incerteza geológica.

### Pilar B: Auditoria Independente de Riscos (Compliance & Risk Assessment)
Atua como uma **"Segunda Opinião de Engenharia"**:
* **Engenheiro Executa no TQS/Eberick** ➔ **Exporta para o ATLAS** ➔ **ATLAS aponta desconformidades.**
* Foco em pontos críticos negligenciados ou simplificados pelas ferramentas comerciais:
  * Análise não-linear real de contato solo-radier (Tensionless / perda de contato).
  * Verificação rigorosa de punção complexa com furos e contornos irregulares.
  * Efeitos globais de 2ª ordem reais (P-Delta iterativo barra por barra) comparados ao aproximado Gama-Z.

### Pilar C: Blackboard Pedagógico (Edu-Tech de Engenharia)
Transformar relatórios incompreensíveis em conhecimento prático:
* Em vez de um rótulo estático "FAIL", o software monta um **Memorial Explicativo Passo a Passo** (Blackboard) com diagramas de esforços, equações normativas (NBR 6118/6123) com os valores reais substituídos e caminhos de correção recomendados.

### Pilar D: API-First & AI-Ready (Infraestrutura do Futuro)
Nenhum software do mercado permite integração nativa com Inteligência Artificial:
* Arquitetura desacoplada e conteinerizada (Docker).
* Endpoints limpos para entrada e saída em JSON.
* Pronto para ser o motor de cálculo de **Agentes de IA autônomos** que gerenciam projetos de engenharia.

---

## 3. Arquitetura Tecnológica Recomendada

```
                               ┌────────────────────────┐
                               │   Clientes / Usuários  │
                               └───────────┬────────────┘
                                           │
                     ┌─────────────────────┼─────────────────────┐
                     ▼                     ▼                     ▼
             ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
             │ Dashboard Web │     │ Agentes de IA │     │ Scripts/BIM   │
             │ (React/Next)  │     │ (LLM / Python)│     │ Integrations  │
             └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
                     │                     │                     │
                     └─────────────────────┼─────────────────────┘
                                           │ (API Gateway JSON)
                                           ▼
                               ┌────────────────────────┐
                               │  FastAPI Router (py)   │
                               └───────────┬────────────┘
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
         ┌───────────────────────┐                   ┌───────────────────────┐
         │  Módulos de Auditoria │                   │  Rust Solver (Core)   │
         │  & Pedagogia (Python) │                   │  (faer / PyO3)        │
         ├───────────────────────┤                   ├───────────────────────┤
         │ • NBR 6118 Rules      │                   │ • 3D Frame solver     │
         │ • Memorial Generator  │                   │ • Shell-Q4 solver     │
         │ • Cost Calculations   │                   │ • P-Delta Iterations  │
         └───────────────────────┘                   └───────────────────────┘
```

---

## 4. Cronograma de Desenvolvimento (Roadmap de Marcos)

### 🔹 Fase 1: API de Otimização & Auditoria (Curto Prazo)
* **Objetivos:**
  * Estabilizar os solvers de vigas, colunas, sismo, vento, estabilidade e radier em Rust.
  * Consolidar a suíte de benchmarks analíticos exatos.
  * Criar endpoints dedicados a otimização de custo (ex: `/optimize/radier`, `/optimize/beam`).
  * **Integração de Interação Solo-Estrutura (SSI) (Meta 10/10):** Expor parâmetros de efeito de grupo de estacas e adensamento temporal multicamadas diretamente nas APIs públicas.
  * **Integração de Surrogate Model / Redes Neurais (Meta 10/10):** Habilitar aceleração via modelo substituto de aprendizado de máquina (`StructuralSurrogate`) no endpoint de otimização para ciclos de busca sub-milissegundo.
* **Métricas de Sucesso:**
  * Tempo de processamento de um lote de 100 variações de radier < 2 segundos.
  * Redução do tempo de otimização em até 90% com Surrogate habilitado.
  * 100% de cobertura nos testes de integridade das fórmulas.

### 🔹 Fase 2: O Hub de Segunda Opinião & BIM (Médio Prazo)
* **Objetivos:**
  * Implementar o parser para arquivos IFC (BIM) e DXF (TQS/Eberick/Revit) para importação sem fricção.
  * **Detalhamento Automático Otimizado (Meta 10/10):** Motor de geração paramétrica baseada em templates DXF e injeção de blocos dinâmicos CAD (*Headless CAD Block injection*) para geração de armaduras e tabela de ferros de baixa manutenção.
  * **Módulo de Ancoragem Analítica (NBR 6118):** Cálculo automatizado de comprimento de ancoragem necessário ($l_{b,nec}$) e requisitos de ganchos em nós de pórtico no payload JSON.
  * Desenvolver a ferramenta de visualização interativa do mapa de tensões no solo e armaduras executivas 3D na web.
  * Disponibilizar o "Blackboard Explainer" como serviço interativo na UI.
* **Métricas de Sucesso:**
  * Processamento direto de um arquivo IFC gerado no Revit/TQS com diagnóstico de compliance estrutural impresso em tela.
  * Exportação de pranchas estruturais em DXF geradas a partir de templates visuais sem sobreposição gráfica de textos.

### 🔹 Fase 3: O Agente de IA Estrutural (Longo Prazo)
* **Objetivos:**
  * Lançar SDKs específicos para integrar modelos de linguagem (LLMs) com os solvers do ATLAS.
  * Desenvolver o loop fechado de tomada de decisão (o agente lê os resultados estruturais, executa o redesenho, recalcula o custo e entrega o projeto final otimizado).
* **Métricas de Sucesso:**
  * Um agente autônomo de IA resolvendo problemas de dimensionamento de radier/vigas com feedback normativo do ATLAS sem intervenção humana.

---

## 5. Manutenção e Evolução deste Documento

Este documento serve como a **Constituição de Produto do MEF STRUCTURAL**. Qualquer alteração nas prioridades técnicas ou mudanças arquiteturais globais deve ser registrada e atualizada diretamente nesta página para manter a consistência do roadmap de engenharia.
