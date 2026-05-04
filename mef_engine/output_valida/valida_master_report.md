# Relatorio Radier Lab

## Resumo Executivo

- decisao tecnica: `Nao apto para detalhamento ate revisao tecnica dos bloqueios normativos.`
- status profissional: `nao_apto_requer_revisao_tecnica`
- score de maturidade: `4.16/5` (`4 - quase executivo`)
- pressao maxima / admissivel: `0.948` (ATENDE)
- puncao: `ATENDE` | ratio max `n/d`
- servico: recalque max `9.476 mm`, diferencial `6.485 mm`, fissuracao x/y `ATENDE/ATENDE`


### Acoes Tecnicas Recomendadas

- benchmark_minimo_ok: Suite benchmark interna passou nas tolerancias


## Matriz de Confiabilidade

| Controle | Status | Evidencia |
| :--- | :--- | :--- |
| Validacao de entradas | ATENDE | CSVs/configuracao passam pela camada de validacao |
| Equilibrio numerico | ATENDE | residual=8.465e-10 |
| Benchmark interno | NAO_ATENDE | Benchmark fixo do caso de regressao interno. |
| Checklist profissional | NAO_ATENDE | nao_apto_requer_revisao_tecnica |
| Score de maturidade | ATENDE | 4.16/5 |


## Enquadramento Profissional

- modulo: `Modulo de Radier em Concreto Armado`
- modo de uso: `Dimensionamento`
- etapa do projeto: `pesquisa_aplicada`
- perfil do cliente: `construtora_talls`
- objetivo: `dimensionamento, analise e pericia de radier com foco didatico e pesquisa aplicada`
- foco do modo: `dimensionamento preliminar, verificacoes de resistencia e definicao de espessura/armaduras`


## Base Normativa

- perfil principal: `ABNT NBR 6118:2023`
- fundações: `ABNT NBR 6122:2019`
- ações e combinações: `ABNT NBR 8681`
- papel do perfil: `principal`
- observação: `Perfil principal do dimensionador. Aderência normativa deve ser auditada cláusula a cláusula durante a evolução do motor.`

### Referencias Internacionais

- ACI 318-25 (comparativo)
- EN 1992-1-1:2004 Eurocode 2 (comparativo)

### Combinacoes Adotadas

- serviço rara: `{'G': 1.0, 'Q': 1.0}`
- serviço frequente: `{'G': 1.0, 'Q': 0.7}`
- ELU: `{'G': 1.4, 'Q': 1.4}`

### Matriz de Verificacoes

#### Automatizado no Modulo

- pressao media e maxima de contato no solo
- pre-dimensionamento orientativo da espessura
- flexao ELU por faces com Wood-Armer simplificado
- punção ELU completa (NBR 6118) com fator beta (momentos) e Wp
- indicadores de servico por recalque

#### Parcial ou em Evolucao

- combinações normativas completas ELU/ELS
- fissuracao por abertura de fissuras
- detalhamento executivo final por faixas e regiões

#### Exige Validacao de Engenharia

- aceitação final do dimensionamento para projeto executivo
- compatibilização com documentos geotécnicos e critérios específicos da obra
- escolha final das combinações e coeficientes conforme caso real

### Checklist Normativo Detalhado

- [ATENDE] NBR6118_NBR6122_PRESSAO_SOLO: Geotecnia de contato | ref: ABNT NBR 6122:2019 + ABNT NBR 6118:2023 (compatibilizacao fundacao-estrutura) | metodo: Pressao media e maxima do modelo versus tensao admissivel informada
- [ATENDE] NBR6118_ELU_FLEXAO: Dimensionamento a flexao | ref: ABNT NBR 6118:2023 (ELU em secoes de concreto armado) | metodo: Flexao ELU por faces com Wood-Armer simplificado e armadura minima
- [NAO_APLICAVEL] NBR6118_ELU_PUNCAO: Punção em laje de fundacao | ref: ABNT NBR 6118:2023 (punção, contornos C e C') | metodo: Formulação completa com fator beta (efeito de momentos) e Wp para pilar interior/borda/canto; não aplicável quando não há pilares/cargas concentradas.
- [ATENDE] NBR6118_ELS_FISSURACAO: Estado limite de servico - fissuracao | ref: ABNT NBR 6118:2023 (controle de abertura de fissuras) | metodo: Estimativa de wk por tensao no aco, diametro e taxa efetiva
- [ATENDE] NBR6122_ELS_DISTORCAO: Estado limite de servico - distorcao angular | ref: ABNT NBR 6122:2022 (anexo J / literatura tecnica) | metodo: Calculo de delta_w / L entre todos os pilares vizinhos via Delaunay
- [ATENDE] NBR6122_ELS_RECALQUES: Estado limite de servico - recalques | ref: ABNT NBR 6122:2019/2022 (criterios de deformabilidade) | metodo: Comparacao de recalque total e diferencial com limites orientativos de servico
- [ATENDE] NBR6118_RASTREABILIDADE: Rastreabilidade tecnica | ref: Boas praticas de auditoria tecnica | metodo: Memorial + relatorio + manifesto de artefatos


## Sequencia de Calculo

- ordem da esteira: `deterministic_service_analysis, design_checks_elu_els, sensitivity_envelope, research_batch, inverse_and_uq, bayesian_calibration`

## Dados da Obra

- Base name: `valida_master`
- Geometria: `10.0 m x 10.0 m`
- Malha: `11 x 11`
- Espessura: `0.50 m`

## Materiais

- `fck`: `30.00 MPa`
- `fyk`: `500.00 MPa`
- cobrimento: `0.050 m`

## Dados do Solo

- `kv`: `20000000.00 N/m³`
- `sigma_adm`: `200.00 kPa`
- modelo: `Winkler vertical`

## Metodologia Geotecnica

- modelo de solo: `Winkler vertical`
- molas sem tracao: `True`
- origem do kv: `uniform_default`


## Acoes e Combinacoes

- `q`: `50000.00 Pa`
- carga total de servico: `11250.000 kN`

## Caso Deterministico

- `w_max_mm`: `9.476`
- `qsoil_max_kPa`: `189.527`
- `mx_abs_max_kNm_m`: `367.044`
- `my_abs_max_kNm_m`: `367.044`
- `residual_ratio`: `8.465e-10`

## Verificacoes Geotecnicas

- `pressao_media_kPa`: `112.500`
- `pressao_max_modelo_kPa`: `189.527`
- atende pressao media: `True`
- atende pressao maxima: `True`

## Comparativo de Metodologias

Nao disponivel para este processamento.


## Matriz de Calibracao por Livros/Autores

- versao: `geotech_ref_matrix_v2`
- modelo: `k_v = fator * N_spt (MPa/m)`
- tipo de projeto: `edificios_altos`
- perfil de pesos: `{'academico': 1.12, 'hibrido': 1.08, 'mercado': 0.95, 'estrutural': 1.08, 'execucao': 0.9, 'pericia': 0.92, 'analise': 1.15}`

### Envelope N-SPT -> k_v (MPa/m)

- `argila_mole`: min=8.0 | alvo=12.0 | max=16.0 MPa/m
- `argila_rija`: min=14.0 | alvo=20.0 | max=28.0 MPa/m
- `silte`: min=12.0 | alvo=18.0 | max=25.0 MPa/m
- `areia_fofa`: min=18.0 | alvo=28.0 | max=40.0 MPa/m
- `areia_media`: min=25.0 | alvo=40.0 | max=55.0 MPa/m
- `areia_compacta`: min=35.0 | alvo=55.0 | max=80.0 MPa/m
- `misto`: min=20.0 | alvo=30.0 | max=45.0 MPa/m

### Referencias Consolidadas

- `Cintra, Aoki e Albiero` | Fundacoes Diretas - Projeto Geotecnico | base=0.920 | fator=1.120 | calibrado=1.030
- `Velloso e Lopes` | Fundacoes - Vol. I | base=0.950 | fator=1.120 | calibrado=1.064
- `Falconi et al.` | Fundacoes Teoria e Pratica | base=0.900 | fator=1.080 | calibrado=0.972
- `Dickran Berberian` | Engenharia de Fundacoes - Passo a Passo | base=0.850 | fator=0.950 | calibrado=0.807
- `Joao Carlos de Campos` | Elementos de Fundacoes em Concreto | base=0.820 | fator=1.080 | calibrado=0.886
- `Vinicius Lorenzi` | Fundacoes na Pratica | base=0.780 | fator=0.900 | calibrado=0.702
- `Referencia tecnica de patologia` | Patologia das Fundacoes | base=0.840 | fator=0.920 | calibrado=0.773
- `Referencia de ISE em edificios` | Interacao Solo-Estrutura e sua Aplicacao na Analise de Estruturas de Edificios | base=0.880 | fator=1.150 | calibrado=1.012

- governanca: `Matriz interna consolidada para calibracao preliminar; nao substitui investigacao geotecnica local, parecer tecnico e validacao de engenharia.`




## Pre-dimensionamento

- `espessura_referencia_m`: `0.200`
- `espessura_adotada_m`: `0.500`
- atende referencia preliminar: `True`

## Modelo Estrutural

- tipo: `placa Mindlin-Reissner sobre base elastica de Winkler`
- elementos: `100`

## Lote Parametrico

- Cenarios avaliados: `4`
- Maior recalque do lote: `kv_low` com `8.565 mm`

## Calibracao Inversa e UQ

- `best_kv`: `15000000.000`
- `best_rmse_mm`: `8.806`
- `best_mae_mm`: `8.233`
- `mc_wmax_p95_mm`: `9.799`
- `mc_qmax_p95_kPa`: `192.976`

## Calibracao Bayesiana

- `kv_map`: `15000000.000`
- `kv_mean`: `17052618.629`
- `kv_p10`: `15000000.000`
- `kv_p50`: `15000000.000`
- `kv_p90`: `20964813.563`
- `sigma_map`: `6.000`
- `sigma_mean`: `5.547`

## Verificacoes Estruturais

- `puncao_ratio_max`: `None`
- `puncao_atende`: `True`
- `Asx_top_adot_max_cm2_m`: `33.53050345738671`
- `Asy_top_adot_max_cm2_m`: `33.530503457386985`

## Detalhamento Estrutural Sintetico

| Item | Valor |
| :--- | :--- |
| Asx topo adotada max | `33.531 cm2/m` |
| Asy topo adotada max | `33.531 cm2/m` |
| Asx inferior adotada max | `6.144 cm2/m` |
| Asy inferior adotada max | `6.144 cm2/m` |
| Sugestao x topo | `phi 20.0 c/ 7.5 cm` |
| Sugestao y topo | `phi 20.0 c/ 7.5 cm` |
| Puncao ratio max | `n/d` |
| Puncao local critico | `None` |
| Distorcao angular max | `n/d` |
| Par critico distorcao | `None` |


## Verificacoes de Servico

- `w_max_mm`: `9.4763400742804`
- `w_med_mm`: `5.305255145791335`
- `w_diff_mm`: `6.484608979367399`
- `wk_x_max_mm`: `0.2114165300899747`
- `wk_y_max_mm`: `0.2114165300899894`
- `wk_x_ok`: `True`
- `wk_y_ok`: `True`

## Criterios de Servico

| Verificacao | Valor | Limite | Unidade | Status |
| :--- | ---: | ---: | :--- | :--- |
| Recalque total maximo em servico | 9.476 | 50.000 | mm | ATENDE |
| Recalque diferencial maximo em servico | 6.485 | 25.000 | mm | ATENDE |
| Distorcao angular maxima entre apoios | n/d | 0.002 | adim | ATENDE |

- abertura de fissuras x/y: `0.211 mm` / `0.211 mm` (limite `0.300 mm`)
- observacao: `Limites orientativos para estudo preliminar, sujeitos a ajuste por tipologia e desempenho alvo.`


## Leitura Orientada pelo Modo

- modo: `Dimensionamento`
- foco: `dimensionamento preliminar, verificacoes de resistencia e definicao de espessura/armaduras`
- secoes prioritarias: `pre_dimensionamento, verificacoes_estruturais, detalhamento_final`
- vetores de decisao: `espessura preliminar, armadura adotada, punção, equilibrio global`

### Checagens Criticas

- Espessura adotada atende referência preliminar: True
- Punção atende: True
- Asx topo adotada máxima (cm²/m): 33.53050345738671
- Asy topo adotada máxima (cm²/m): 33.530503457386985

### Acoes Recomendadas

- Consolidar faixas de armadura inferior e superior.
- Avaliar engrossamentos locais se punção ou momentos forem críticos.


## Avaliacao Tecnica do Modo

### Base de Combinacoes

- serviço: `{'G': 1.0, 'Q': 1.0}`
- ELU simplificado: `{'G': 1.4, 'Q': 1.4}`

### Checagens de Projeto

- pre-dimensionamento atende: `True`
- Asx topo governante (cm²/m): `33.53050345738671`
- Asx base governante (cm²/m): `6.143674666923542`
- Asy topo governante (cm²/m): `33.530503457386985`
- Asy base governante (cm²/m): `6.143674666923542`
- punção atende: `True`
- posição crítica de punção: `None`

### Diretrizes Executivas

- Definir faixas de armadura superior sobre pilares e bordas.
- Confirmar espessura final com base em punção, flexão e construtibilidade.
- Registrar detalhamento preliminar de reforços locais e malhas mínima/inferior/superior.


## Leitura de Pesquisa

### O que esta sendo feito

- O modulo atual modela o radier como placa sobre base elastica de Winkler, adequado para estudos comparativos e rastreio inicial de comportamento.
- O fluxo principal ja contempla pressao de contato, flexao, puncao e indicadores de servico, preservando a logica central do memorial de calculo.

### Oportunidades de Melhoria

- O recalque diferencial estimado merece aprofundamento; comparar malhas, cenarios de kv e estrategias de rigidez local.
- Investigar tabelas de pre-dimensionamento por tipologia de torre, vao entre pilares e rigidez de solo.
- Evoluir a recomendacao de armadura de faixas e reforcos locais de forma mais executiva.

### Questoes para Novas Solucoes

- Como calibrar o coeficiente de recalque com dados de instrumentacao de obras altas para reduzir incerteza de modelo?
- Em quais faixas de rigidez de solo o modelo de Winkler deixa de ser suficiente e passa a exigir formulacoes mais refinadas?
- Quais tipologias de engrossamento sob pilares centrais e de borda trazem melhor ganho de desempenho para torres altas?
- Como transformar os resultados do modulo em base comparativa para futuros modulos de vigas, pilares e interacao solo-estrutura global?


## Evidencias de Benchmark

- suite: `radier_internal_quick_benchmark_v1`
- status global: `False`
- aplicabilidade: `reference_regression`
- bloqueia uso profissional: `True`
- observacao: `Benchmark fixo do caso de regressao interno.`

### Checagens

- [FAIL] benchmark_deterministic_wmax: Faixa de regressao do recalque maximo do caso base | atual=9.476340074280413 | alvo={'min': 4.5, 'max': 5.5, 'unit': 'mm'}
- [FAIL] benchmark_deterministic_qmax: Faixa de regressao da pressao maxima de contato do caso base | atual=189.52680148560827 | alvo={'min': 190.0, 'max': 220.0, 'unit': 'kPa'}
- [PASS] benchmark_equilibrium_residual: Equilibrio global da solucao | atual=8.464720514085557e-10 | alvo={'max': 1e-06, 'unit': 'ratio'}


## Checklist Profissional

- status: `nao_apto_requer_revisao_tecnica`
- observacao: `Uso executivo final exige revisao do engenheiro responsavel e verificacoes normativas complementares.`

### Itens

- [OK] entrada_validada: Configuracoes e CSVs passam pela camada de validacao
- [OK] base_normativa_explicita: Perfil normativo principal e combinacoes estao declarados
- [OK] geotecnia_ok: Pressao media e maxima modelada atendem ao criterio de admissibilidade
- [OK] equilibrio_global_ok: Residual ratio em faixa de equilibrio numerico
- [OK] puncao_ok: Razao de puncao <= 1.0 quando ha cargas concentradas/pilares
- [OK] fissuracao_servico_ok: Checagens de abertura de fissuras em servico atendem ao limite adotado
- [OK] recalque_servico_ok: Checagens de recalque e distorcao angular atendem aos limites orientativos
- [PENDENTE] benchmark_minimo_ok: Suite benchmark interna passou nas tolerancias


## Score de Maturidade

- versao monitorada: `valida_master`
- data UTC: `2026-05-03T01:00:39.888698+00:00`
- score global 0-5: `4.16`
- score global 0-100: `83.1`
- nivel: `4 - quase executivo`

### Subscores

- prontidao profissional: `0.875`
- rastreabilidade normativa: `1.0`
- evidencia benchmark: `0.333`

### Nota de Monitoramento

- `Compare o score_0_5 entre versoes (version_id) para acompanhar maturidade do modulo.`


## Premissas e Limitacoes

### Parcial ou em Evolucao

- combinações normativas completas ELU/ELS
- fissuracao por abertura de fissuras
- detalhamento executivo final por faixas e regiões

### Exige Validacao de Engenharia

- aceitação final do dimensionamento para projeto executivo
- compatibilização com documentos geotécnicos e critérios específicos da obra
- escolha final das combinações e coeficientes conforme caso real


## Rastreabilidade dos Artefatos

| Artefato | Caminho |
| :--- | :--- |
| Memorial JSON | `output_valida/valida_master_memorial_summary.json` |
| Relatorio Markdown | `output_valida/valida_master_report.md` |
| Resumo deterministico | `output_valida/valida_master_deterministic_summary.json` |
| Sensibilidade | `output_valida/valida_master_sensitivity_envelope.csv` |
| Flexao | `output_valida/radier_design_flexure_v2.csv` |
| Puncao | `output_valida/radier_punching_check_v2.csv` |
| Servico | `output_valida/radier_serviceability_check_v2.csv` |
| Manifesto | `output_valida/valida_master_artifacts.json` |

