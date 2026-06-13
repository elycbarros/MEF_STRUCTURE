# Pontos de Continuidade - MEF STRUCTURAL
**Última Atualização:** 13/06/2026

Este documento resume exatamente o estado atual do projeto, os serviços e frentes de desenvolvimento disponíveis.

---

## 🛠️ Estado Atual dos Serviços
Todos os serviços estão ativos e rodando em segundo plano sob o controle do daemon `mef_guardian.py`:
- **Backend (Porta 8000):** ONLINE
- **Frontend (Porta 3000):** ONLINE
- **Guardian (mef_guardian.py):** ATIVO

### 📌 Comandos de Controle Rápido (Makefile)
* `make status` - Verifica a integridade e PIDs de todos os serviços.
* `make stop` - Encerra com segurança todos os servidores e o guardian.
* `make start` - Inicia novamente o guardian e todos os servidores em segundo plano.

---

## 📝 O Que Foi Concluído
1. **Migração do Frontend Completa:** Todos os módulos de cálculo e playgrounds foram migrados, ativados e integrados na interface (`mef_frontend`). Isso inclui:
   * **NBR 6118:** Viga Isolada, Pilar, Laje, Escadas, Consolo, Dente Gerber, Viga Parede, Parede de Concreto.
   * **Fundações:** Sapata Isolada, Estaca, Bloco sobre Estacas, Muro de Arrimo, Sondagem SPT e Radier Avançado.
   * **Sistemas:** Pórticos, Treliças, Estabilidade $\gamma_z$ e Vento / NBR 6123.
   * **Módulos Especiais:** Viga Cross e Tension Pro.
2. **Biblioteca Técnica:** O único módulo atualmente inativo/desativado por placeholder na barra lateral é a Biblioteca Técnica (`tech_library`).
3. **Estabilização de Solvers e Diagramas:** Todos os solvers foram conectados a seus respectivos endpoints backend ou locais (no caso do Hardy Cross) e a suíte com 36 testes automatizados passou com sucesso.

---

## 🚀 Opções Disponíveis para Continuar (Foco em Refinamento)

### Opção 1: Refinamento de Lajes e Radier (Winkler / Branson / Punção)
* **Objetivos:**
  * Implementação física de perda de contato solo-radier (*tensionless*) e renderização do mapa de pressões do solo na interface.
  * Cálculo de flecha diferida fissurada pelo modelo de Branson.
  * Verificação avançada de armadura de punção e perímetros de cisalhamento.

### Opção 2: Estabilidade Global e Análise Sísmica
* **Objetivos:**
  * Ampliar a verificação sísmica baseada no espectro de resposta da NBR 15421.
  * Implementar cálculo de conforto dinâmico (acelerações sob vento rajada e *Vortex Shedding*).

### Opção 3: Gráficos de Interação N-M no Pilar (Flexo-Compressão)
* **Objetivo:** Adicionar visualização do diagrama de interação de flexão composta oblíqua/normal, sinalizando o ponto solicitante ($N_d, M_d$) para verificação visual da segurança do pilar.
