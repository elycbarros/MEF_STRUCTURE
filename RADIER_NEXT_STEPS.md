# Próximos Passos do Sistema de Radier

## Objetivo

Registrar o que ficou planejado para a próxima fase do sistema, mantendo o foco atual em `radier / laje de fundação`, sem ainda implementar cálculo de `radier estaqueado`.

## O que já está encaminhado

- modo guiado com presets de finalidade
- presets de solo
- triagem de riscos de campo
- memorial com atualização dos dados do documento
- módulo de armadura do radier
- diagnóstico de viabilidade da solução de fundação
- recomendação de alternativas quando o radier liso se mostra pouco realista

## Benchmark comercial observado

### GEO5 - Laje e Radier

Referencia: https://geo5.com.br/laje-e-radier/
Benchmark tecnico complementar: `docs/GEO5_BENCHMARK.md`, com leitura dos manuais `em20_pt.pdf`, `em21_pt.pdf`, `em22_pt.pdf` e `em30_pt.pdf` retirados do site do GEO5.

### AltoQi Eberick - Radier

Referencia: https://suporte.altoqi.com.br/hc/pt-br/articles/360037896274

Pontos incorporados ao benchmark comercial:

- modelo de placa/malha sobre apoios elasticos equivalentes
- hipotese de Winkler com `p = kv . d`
- importancia dos coeficientes de recalque vertical e horizontal obtidos por estudo geotecnico
- variacao de `kv` altera deslocamentos e momentos fletores
- pressao de contato e diagrama de pressoes no solo como leitura central
- avisos comerciais esperados:
  - tracao na base do radier/perda de contato
  - pressoes de contato acima da admissivel
  - necessidade de analise mais rigorosa quando deslocamentos passam da ordem de 1 a 2 cm
- puncao junto aos pilares com perimetros criticos conforme posicao do pilar

## Referencias academicas brasileiras

Matriz consolidada em `docs/ACADEMIC_RADIER_REFERENCES.md`, a partir de dissertacoes e TCCs sobre radier, interacao solo-estrutura, analogia de grelha, Winkler, SAP2000/TQS/DIANA e radier estaqueado.

Referencias analisadas:

- Souza, Ruiter da Silva (2010): fatores de interacao entre estacas em radier estaqueado
- Guedes e Burgos (2014): analise estrutural de laje de fundacao tipo radier em concreto armado
- Cibulski Junior (2016): modelagem de radier rigido e interacao solo-estrutura
- Doria, Luis Eduardo Santos (2007): projeto de estrutura de fundacao em concreto do tipo radier
- Fortes, Caria, Funahashi Jr. e Kuperman (IBRACON 109, 2023): radier de grandes dimensoes, projeto estrutural e estudo termico
- Miloch e Faria (2021): sensibilidade de parametros geotecnicos em radier estaqueado por MEF/Monte Carlo
- Fabio Albino de Souza, palestra IE: radier simples, armado, protendido, tipologias, F-CBR, execucao e fator de forma

Leitura para o Radier Lab:

- o nucleo atual de radier liso Winkler esta alinhado com uma linha recorrente da literatura brasileira
- `kv` agora e tratado como dado de confiabilidade variavel, com origem documentada na interface, API, JSON e memorial
- analogia de grelha deve entrar como metodo comparativo futuro, nao como substituto imediato do MEF
- radier estaqueado deve permanecer como modulo futuro separado, pela interacao solo-radier-estacas
- comparador tecnico-economico deve considerar consumo/custo, nao apenas verificacao mecanica
- radiers muito espessos/grandes volumes exigem checklist tecnologico de concreto massa, temperatura, maturidade e fissuracao termica
- modulo futuro de radier estaqueado deve considerar incertezas e sensibilidade; comprimento de estacas e rigidez/modulo do solo aparecem como variaveis dominantes em fonte academica
- a interface guiada deve evoluir para selecionar tipologia de radier com condicionantes de solo/superestrutura/execucao
- o diagnostico deve incluir fator de forma `SF = perimetro^2 / area` para alertar formas alongadas e possiveis efeitos de torcao

O software comercial GEO5 posiciona o modulo `Laje e Radier` como uma ferramenta de dimensionamento de radiers e analise de lajes de fundacao por MEF sobre subsolo elastico.

Pontos fortes usados como referencia de produto:

- formas arbitrarias de laje/radier
- gerador automatico de malha de elementos finitos
- refinamento de malha em torno de pontos e linhas
- dimensionamento de lajes e radiers
- possibilidade de fundacao por estacas sob a placa
- apoios concentrados e distribuidos, fixos ou elasticos
- modelo de subsolo Winkler-Pasternak com parametros `C1` e `C2`
- introducao de vigas por parametros de secao transversal
- cargas de forca e deformacao
- multiplos casos de carga e combinacoes
- gerador automatico de combinacoes segundo EN 1990
- armadura necessaria para flexao e cisalhamento
- importacao/exportacao DXF
- relatorios finais em PDF ou Word

Leitura para o Radier Lab:

- manter foco atual em radier liso Winkler como nucleo confiavel
- evoluir para malha/geometria mais flexivel antes de prometer formas arbitrarias
- tratar Winkler-Pasternak como futura melhoria real do modelo de solo, nao apenas parametro de interface
- separar claramente `radier sobre solo` de `radier estaqueado`, pois a solucao com estacas muda o modelo fisico
- priorizar exportacao profissional e rastreabilidade antes de ampliar tipologias estruturais

## Próximas entregas

### 1. Calibrar o módulo de diagnóstico

- status: iniciado em 2026-04-24
- ajuste do nível de conservadorismo implementado no backend e já usado pela interface
- limites graduais de alerta/restrição/bloqueio agora consideram:
  - espessura elevada
  - relação `qmax / sigma_adm`
  - punção próxima do limite
  - recalque e distorção
  - fissuração em serviço
  - consistência simplificada de Winkler
- próximos gatilhos comerciais a implementar:
  - tracao/perda de contato na base do radier
  - destaque para recalque acima de 10 a 20 mm como faixa de maior rigor
  - mapa/diagrama de pressoes no solo como saida principal
- separar melhor:
  - alerta
  - restrição
  - bloqueio técnico
- próximo ajuste: validar os valores dos limites com casos reais e calibrar mensagens por tipo de obra

### 2. Destacar a recomendação principal no relatório

- status: iniciado em 2026-04-24
- API agora exporta `executive_decision` como resumo normalizado de decisão
- relatório final e interface passam a mostrar com mais força a decisão:
  - `radier liso viável`
  - `radier liso com restrições`
  - `estudar solução alternativa`
- classificação levada para:
  - memorial
  - resumo executivo
  - exportação JSON
- próximo ajuste: criar visual PDF/Word e uma página de capa executiva para entrega ao cliente

### 3. Melhorar o módulo de armadura

- detalhar melhor faixas de armadura por regiões
- indicar reforços locais em torno de pilares e bordas
- adicionar alerta executivo para radiers espessos:
  - estudo termico
  - plano de concretagem
  - controle de temperatura de lancamento
  - maturidade/monitoramento
  - risco de fissuracao termica e etringita tardia
- estudar lógica futura para:
  - pedestais
  - cogumelos
  - engrossamentos locais
  - radier nervurado
- preparar informacoes para tipologias:
  - radier com capiteis
  - radier com pedestais
  - radier nervurado
  - radier flutuante
  - radier protendido

### 4. Criar comparador de soluções

- comparação orientativa entre:
  - radier liso
  - sapatas
  - radier com reforços locais
  - radier estaqueado
  - fundação profunda
- sem calcular piled raft por enquanto
- foco inicial: apoio à decisão técnica e econômica preliminar
- incluir coluna de maturidade do modelo:
  - implementado
  - aproximado/orientativo
  - fora do escopo atual
- usar o benchmark GEO5 para mapear recursos comerciais esperados sem misturar com promessas ainda nao implementadas

### 5. Preparar a futura expansão para outros tipos de radier

- manter `radier liso` como solução atualmente calculada
- preparar estrutura de dados para:
  - radier com pedestais
  - radier com cogumelos
  - radier nervurado
  - radier em caixão
- deixar claro na interface o que está:
  - implementado
  - apenas recomendado
  - planejado para fase futura
- backlog tecnico inspirado no benchmark comercial:
  - geometrias arbitrarias
  - refinamento local de malha em pilares, linhas de carga e bordas
  - apoios elasticos/concentrados adicionais
  - vigas de fundacao acopladas ao radier
  - modelo Winkler-Pasternak
  - importacao/exportacao DXF
  - relatorio PDF/Word
- backlog academico para radier estaqueado:
  - modelo solo-radier-estacas separado
  - contato solo-fundacao
  - sensibilidade probabilistica/Monte Carlo
  - variaveis dominantes: comprimento das estacas e modulo/rigidez do solo
  - saida principal preliminar: deslocamento/recalque maximo
- backlog pratico de execucao/tipologia:
  - origem do `kv` por F-CBR como metodo futuro
  - solos expansivos e colapsiveis
  - aterros e nivel d'agua/subpressao
  - manta retardadora de vapor
  - fator de forma do radier
  - limites geometricos orientativos para nervuras

### 6. Futuro módulo separado de lajes

- manter separado do módulo de fundações
- estudar depois:
  - lajes de passagem de veículos
  - lajes sobre solo
  - pisos industriais / pátios
- usar normas e critérios específicos desse domínio, sem misturar com o fluxo atual de fundação

## Observações técnicas importantes

- `radier estaqueado / piled raft` muda o modelo físico e numérico
- não tratar essa solução como simples variação do radier liso
- quando for implementar no futuro, considerar interação:
  - solo
  - radier
  - estacas
  - redistribuição de carga

## Estratégia de Performance e Escalabilidade

### Otimização Atual (Fase 1: Sparse Engine)
- Migração completa de todos os motores FEM (`radier`, `lajes`, `frame_engine`, `beam_solver`) para arquitetura de **Matrizes Esparsas (CSR format)** usando `SciPy Sparse`.
- Ganhos esperados: Redução exponencial de memória e tempo de processamento para modelos de edifícios altos e malhas refinadas.
- Manutenibilidade: Mantido em Python para agilidade, utilizando solvers compilados em C/Fortran (SciPy).

### Próximo Passo Lógico (Fase 2: Rust Integration)
- Para modelos ultra-complexos com **milhões de nós**, a migração dos kernels de assemblagem e resolução para **Rust** é o próximo passo planejado.
- O uso de Rust permitirá paralelismo massivo e gerenciamento de memória "zero-cost", essencial para análises de grandes núcleos estruturais e cidades digitais.

## Prioridade sugerida

1. calibrar diagnóstico
2. reforçar a recomendação no relatório
3. evoluir armadura/faixas locais
4. criar comparador de soluções
5. preparar outros tipos de radier
6. abrir módulo separado de lajes
