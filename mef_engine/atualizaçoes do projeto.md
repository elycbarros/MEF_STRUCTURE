## V3.5.0 (2026-05-03) — Vento + Estabilidade Global

### Motor de Vento (`wind_engine.py`)
- **NBR 6123**: Cálculo de Vk, S2 (estático e dinâmico) e pressões dinâmicas q.
- **Modelo Discreto**: Implementação do Capítulo 9 para edifícios altos, com fator de pico e resposta ressonante.
- **Perfil por Nível**: Geração de força horizontal (kN) e momento de tombamento (kNm) rastreáveis nível a nível.

### Acoplamento de Estabilidade (`stability_engine.py`)
- **Integração Automática**: Vento alimenta diretamente o cálculo do Gamma-Z e P-Delta.
- **Critério de Conforto**: Verificação de aceleração de pico para conforto humano em edifícios altos.
- **API REST**: Endpoint `POST /calculate/wind-stability` para análise acoplada.

### Dashboard High-Fidelity (Frontend)
- **Painel dedicado**: Nova aba "Vento" com controle de parâmetros normativos.
- **Visualização**: Tabela de perfil de vento com barras de intensidade por nível.
- **Cards de Estabilidade**: Feedback visual imediato sobre a estabilidade global da estrutura.

## V3.4.0 (2026-05-03) — Reservatórios e Piscinas


### Módulo Completo (`reservoir_pool_solver.py`)
- **Tipos**: Elevado, apoiado, enterrado, piscina.
- **Paredes**: Empuxo hidrostático (triangular) e empuxo de solo, 4 condições de apoio (engastado-livre, bi-apoiado, etc).
- **Casos de Carga**: CHEIO, VAZIO+EMPUXO, CHEIO+EMPUXO — envoltória automática.
- **Fissuração**: Controle rigoroso wk ≤ 0.1mm na face molhada (NBR 6118 §17.3.3), com iteração automática de As.
- **Laje de Fundo**: Dimensionamento via coeficientes de Bares, verificação de flecha.
- **Subpressão/Flutuação**: Fator de segurança contra flutuação (≥ 1.2) para reservatórios enterrados.
- **Resumo Hidráulico**: Volume, peso da água, volume de concreto, pressão no fundo.
- **API REST**: `POST /calculate/reservoir`.
- **Validação**: Reservatório 5×4×3m → 60m³, As=22.2cm²/m (governado por fissuração), wk=0.099mm ✅.

## V3.3.0 (2026-05-03) — Núcleo Rígido (Building Core)

### Módulo de Contraventamento (`building_core.py`)
- **Fosso de Elevador**: Seção em "U" (3 paredes + abertura para porta), posicionável e parametrizável.
- **Caixa de Escada**: Seção retangular com parede central opcional (divisória de lances).
- **Parede de Cisalhamento**: Paredes isoladas em X ou Y.
- **Propriedades Reais**: Ix, Iy, J (torção Saint-Venant), centróide, área — por seção composta de paredes finas.
- **NLF (§15.7.3)**: Fator 0.80 aplicado automaticamente a paredes e núcleos.
- **Análise de Torção**: Verificação de excentricidade entre centro de rigidez (CR) e centro de massa (CM).
- **Integração Direta**: Exporta EI e K_rot formatados para `stability_engine.py` (γz/P-Delta) e `ssi_advanced.py` (locking).
- **API REST**: Novo endpoint `POST /calculate/building-core`.
- **Validação**: Edifício 40 pav. com layout simétrico → excentricidade 0.0%, f1 = 0.36 Hz.

## V3.2.0 (2026-05-03) — Módulo de Vigas

### Módulo Completo de Vigas (`beam_solver.py`)
- **Solver FEM Euler-Bernoulli**: Elementos de viga com 2 nós e 4 DOFs (w, θ), suporte a vigas contínuas de N vãos.
- **Carregamentos**: Cargas distribuídas (uniformes e trapezoidais), cargas concentradas (P, M), peso próprio automático.
- **Apoios**: Articulado (pinned), engastado (fixed), rolete (roller), mola elástica (spring).
- **Dimensionamento NBR 6118:2023**:
  - Flexão simples (domínios 2/3, armadura mínima Tabela 17.3)
  - Cisalhamento Modelo I (§17.4.2.2, verificação de biela Vrd2)
  - Flecha (limites L/250 e L/500, Tabela 13.3)
  - Especificação comercial de estribos (φ e espaçamento)
- **API REST**: Novo endpoint `POST /calculate/beam` com diagramas V, M e w para frontend.
- **Validação**: Viga contínua 2 vãos (6m + 4m), 20 kN/m → Domínio 2, flecha 1.9mm (OK).

## V3.1.0 (2026-05-03) — Elite Engineering Tier

### Frente A — Não-Linearidade Física (Estádio III)
- **Redistribuição Plástica de Momentos**: Motor automático que identifica picos sob pilares (percentil 90), aplica redução δ (até 25%, NBR 6118 §14.6.4.3), e distribui o excedente para o campo.
- **Classificação por Estado**: Cada elemento é classificado como Estádio I (íntegro), II (fissurado) ou III (plastificado).
- **Resultado**: 16 elementos fissurados, 7.4% de redução nos picos de momento.

### Frente B — Efeito de Grupo de Estacas
- **Fatores de Interação (Poulos & Davis / Randolph & Wroth)**: Matriz α_ij calculada automaticamente com base em espaçamento, diâmetro e comprimento.
- **Eficiência do Grupo**: Redução automática da rigidez efetiva (k_eff = k_isolada × η) antes do solve.
- **Classificação**: EFICIENTE (η ≥ 0.85), MODERADO (η ≥ 0.60), INEFICIENTE (η < 0.60).

### Frente C — Adensamento e Fluência (Terzaghi + Creep)
- **Curva Recalque × Tempo**: Geração automática para t = 0.5, 1, 2, 5, 10, 25, 50 anos.
- **Teoria de Adensamento**: Primário (Cc, Cs, OCR) via série de Fourier + Secundário (C_alpha).
- **Classificação Temporal**: ADEQUADO, ATENÇÃO_CREEP, ATENÇÃO_TEMPORAL, RISCO_ALTO, RISCO_CRÍTICO.

### Frente D — Punção em Bordas Complexas (Shafts e Furos)
- **Detecção Automática**: Aberturas dentro da zona 2d do pilar são identificadas e quantificadas.
- **Dedução Geométrica**: Perímetro C' (u1) reduzido conforme NBR 6118 / Eurocode 2.
- **Flag de Segurança**: Pilares que mudam de ATENDE para NÃO_ATENDE são sinalizados automaticamente.


### Frente A — Interação Solo-Estrutura (SSI) Avançada
- **Locking Effect**: Implementação de rigidez axial e rotacional ($K_{\theta}$) nos nós dos pilares para simular o efeito viga-parede da superestrutura de 40 andares.
- **Solver Pro**: Integração da rigidez da superestrutura diretamente na matriz de rigidez global do radier, reduzindo momentos de pico em ~12%.

### Frente B — Detalhamento e CAD Autônomo
- **DXF Engine 2.0**: Geração automática de pranchas técnicas em DXF com camadas normativas (`ARM_INF`, `ARM_SUP`, `ARM_PUNCAO`).
- **Reforço de Punção Visual**: Desenho automático de perímetros de reforço (estribos/studs) no CAD onde a capacidade do concreto é excedida.
- **Malha Comercial**: Tradução de $cm^2/m$ para especificações comerciais (ex: $\phi 12.5$ c/ 15cm).

### Frente C — Auditoria Técnica e Memorial
- **Memorial Rastreável**: Inclusão de status de geração CAD e métricas de SSI no memorial JSON e relatório Markdown.
- **Maturity Score**: Elevação da maturidade do módulo para **3.6 (Técnico Robusto)**.

## V2.6.0 (2026-04-24) — Fechamento do Módulo Radier

### Frente A — Diagnóstico de Tração/Contato + Recalque Crítico
- Gatilho `tension_contact_loss`: detecta perda de contato solo-radier por fração de nós tracionados. Níveis: bloqueio (>5%), restrição (>1%), alerta (>0%).
- Gatilho `high_settlement_warning`: alerta para recalque máximo >10 mm e restrição para >20 mm.
- Estimativa de `contact_loss_fraction` a partir de `w_min_mm` negativo quando não fornecida pelo solver.

### Frente B — Armadura por Faixas Regionais
- `build_regional_reinforcement_map()`: divide o radier em 3 faixas (borda / pano central / sobre pilares) com fatores regionais típicos de distribuição Winkler.
- Flag `requer_reforco_local` quando pico da faixa de pilar > 1,5× pano central.
- Retornado como `regional_reinforcement` no endpoint `/calculate`.

### Frente C — Mapa Visual de Pressões (Frontend)
- Novo componente `SoilPressureMap.tsx`: SVG inline 10×10 com gradiente verde→amarelo→vermelho, marcação dos pilares, dimensões e legenda de escala.
- Novo componente `SolutionComparator.tsx`: tabela responsiva (desktop) / cards (mobile) com badges de maturidade e código de cores por viabilidade.
- `ReportView.tsx`: adicionadas seções 10 (mapa + armadura por faixas), 11 (comparador de soluções), 12 (checklist de concreto massa).

### Frente D — Checklist de Concreto Massa
- `build_thermal_checklist()`: retorna 7 itens de checklist executivo quando h ≥ 0,80 m, com prioridade alta/média.
- Retornado como `thermal_checklist` no endpoint `/calculate`.

### Frente E — Comparador de Soluções
- `build_solution_comparison()`: avaliação qualitativa de 6 soluções (radier liso, sapatas, radier c/ reforços, nervurado, estaqueado, fundação profunda).
- Viabilidade do radier liso derivada do `executive_decision`; demais soluções orientativas baseadas nos gatilhos de bloqueio/restrição.

### Frente F — PDF com Capa Executiva
- `_add_executive_cover()` em `radier_pdf.py`: página de capa com banner escuro, bloco go/no-go colorido, tabela de 12 KPIs, recomendação principal e dados do responsável técnico.
- Ativada automaticamente em `generate_radier_report_pdf()`.

### Correções de Build
- `ExecutiveDecisionCard.tsx`: expandida interface com `pressure_ratio`, `punching_ratio`, `settlement_ratio`, `kv_confidence`.
- `page.tsx`: adicionados helpers `escapeHtml()`, `numberOr()`, componente inline `RebarCard` — corrigidos 3 erros TypeScript pré-existentes.
- Build Next.js: `✓ Compiled successfully` sem erros TypeScript.

## V2.5.3 (2026-04-24) - Decisão Executiva
- **Resumo executivo normalizado:** A API agora retorna `executive_decision` com status, go/no-go, classificação, recomendação principal, próximo passo e primeira ação.
- **Relatório reforçado:** O relatório Markdown destaca o quadro de decisão executiva no resumo e no diagnóstico da solução de fundação.
- **Interface:** A aba de relatório ganhou um card de decisão executiva antes dos detalhes técnicos.
- **Regressão:** Teste de diagnóstico valida coerência entre perfil conservador/permissivo e resultado go/no-go.

## V2.5.2 (2026-04-24) - Confiabilidade do kv
- **Origem do coeficiente `kv`:** Interface agora registra prova de carga, retroanálise, correlação SPT, tabela/literatura ou estimativa inicial.
- **Confiança geotécnica:** O backend recebe `soil_parameter_context` e transforma baixa/média confiabilidade de `kv` em gatilhos técnicos do diagnóstico.
- **Memorial e JSON:** Origem e confiança do `kv` aparecem no diagnóstico, exportação JSON e memorial gerado pela interface.
- **Validação:** Build Next e regressão Python executados com sucesso.

## V2.5.1 (2026-04-24) - Calibração do Diagnóstico
- **Conservadorismo do diagnóstico:** Perfis permissivo, equilibrado e conservador agora calibram pressão, punção, recalque, distorção angular, fissuração, espessura e consistência Winkler.
- **Gatilhos técnicos graduais:** Separação mais clara entre alerta, restrição e bloqueio técnico para viabilidade do radier liso.
- **Rastreabilidade JSON:** Métricas de uso/limite passaram a ser exportadas no diagnóstico da fundação.
- **Regressão:** Inclusão de teste específico para garantir que o perfil conservador seja mais restritivo que o permissivo em caso próximo dos limites.

## V2.5.0 (2026-04-22) - Normativa e Visualização Avançada
- **Punção NBR 6118:2023:** Implementação rigorosa com momentos ($M_x, M_y$), fator $\beta$ e módulo plástico $W_p$.
- **Distorção Angular NBR 6122:2022:** Verificação de recalques diferenciais via triangulação de Delaunay.
- **Visualização Avançada:** Heatmaps interativos para armaduras ($As_x, As_y$), pressões e recalques.
- **UI & Solver:** Suporte total a momentos aplicados em pilares e nova arquitetura de abas de resultados.

## V2.4.1 (2026-04-22) - Melhorias de Validação e UI
- Integração visual do comparativo analítico no Streamlit.
- Ajustes finos no memorial descritivo e checklist profissional.

## V2.4.0 (2026-04-22) - Módulo Analítico
- Inclusão do módulo `radier_analytical.py` para comparação MEF vs. Analítico Rígido.
- Integração das métricas de pressão de solo e punção analítica no pipeline principal.
- Atualização do memorial descritivo para incluir tabelas comparativas.

## V2.3.0 (2026-04-15) - Calibração Bayesiana
- Implementação da calibração de parâmetros de solo via inferência Bayesiana.
- Exportação de distribuições marginais de probabilidade para `kv`.

## V2.2.0 (2026-04-10) - Calibração Inversa e UQ
- Implementação de algoritmos para calibração inversa de `kv`.
- Análise de incerteza (UQ) via Monte Carlo para recalques máximos.

## V2.1.0 (2026-04-05) - Batch Research
- Capacidade de rodar lotes de cenários para sensibilidade paramétrica.
- Post-processor para extração de KPIs de múltiplos arquivos.

## V2.0.0 (2026-03-30) - Mindlin-Winkler V2
- Nova arquitetura do solver baseada em Mindlin-Reissner (lajes grossas).
- Suporte a pilares com dimensões reais e efeito de alívio de solo em punção.
