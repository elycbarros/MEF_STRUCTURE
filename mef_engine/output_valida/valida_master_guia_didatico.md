# Guia Didatico de Dimensionamento de Radier

## Finalidade

Este texto e um anexo de consulta opcional. Ele explica, em linguagem tecnica e didatica, como o modulo percorre o dimensionamento preliminar de um radier liso sobre base de Winkler. Nao substitui o memorial de calculo nem a revisao do engenheiro responsavel.

## 1. Conceito estrutural adotado

O radier e tratado como uma laje de fundacao que distribui as cargas da superestrutura ao solo. No modelo atual, a laje trabalha sobre molas verticais de Winkler, o que significa que a reacao do solo cresce com o recalque local conforme o parametro `k_v`.

- geometria do caso: `10.00 m x 10.00 m`
- espessura adotada: `0.500 m`
- concreto: `fck = 30.00 MPa`
- aco: `fyk = 500.00 MPa`

## 2. Entradas principais do problema

O fluxo usa quatro grupos de entrada:

1. geometria do radier
2. materiais
3. carregamentos
4. rigidez e limite admissivel do solo

No caso atual:

- carga distribuida de servico: `50000.00 Pa`
- carga total de servico: `11250.000 kN`
- carga de pilares considerada: `5000.000 kN`
- `k_v`: `20000000.0 N/m3`
- `sigma_adm`: `200.00 kPa`

## 3. Analise de servico no solo

Primeiro o solver calcula deslocamentos, pressoes de contato e esforcos fletores para a combinacao de servico. Essa etapa responde perguntas basicas:

- qual e o recalque maximo esperado
- como a pressao se distribui no contato solo-radier
- onde aparecem os maiores momentos

Resultados sinteticos do caso:

- pressao media no solo: `112.500 kPa`
- pressao maxima no modelo: `189.527 kPa`
- recalque maximo: `9.476 mm`
- recalque diferencial: `6.485 mm`

Interpretacao didatica:

- se a pressao maxima se aproxima muito de `sigma_adm`, o radier pode ainda funcionar estruturalmente, mas o solo passa a comandar a viabilidade
- se os recalques sobem demais, a preocupacao deixa de ser apenas resistencia e passa a ser desempenho em servico

## 4. Pre-dimensionamento da espessura

Antes do detalhamento de armadura, o sistema compara a espessura adotada com uma referencia preliminar baseada no nivel de carregamento por area.

- espessura de referencia: `0.200 m`
- espessura adotada: `0.500 m`
- atende referencia preliminar: `True`

Didaticamente, essa comparacao nao encerra o projeto. Ela serve como triagem inicial. Mesmo uma espessura acima da referencia pode ser inadequada se houver punção, recalque ou construtibilidade ruim.

## 5. Combinacoes para verificacoes

O modulo registra combinacoes de servico e ELU para rastreabilidade:

- servico rara: `{'G': 1.0, 'Q': 1.0}`
- ELU: `{'G': 1.4, 'Q': 1.4}`

Em termos de ensino, isso mostra que o radier nao e verificado apenas com uma unica fotografia de carga. A leitura correta separa:

- servico: recalque, fissuracao e comportamento global
- ELU: resistencia a flexao e punção

## 6. Flexao e armadura

Com os momentos obtidos pelo modelo, o sistema estima armaduras nas direcoes X e Y, em faces superior e inferior.

- Asx topo adotada max: `33.531 cm2/m`
- Asy topo adotada max: `33.531 cm2/m`
- Asx inferior adotada max: `6.144 cm2/m`
- Asy inferior adotada max: `6.144 cm2/m`

Ponto didatico importante:

- armadura inferior costuma responder pelas regioes de momento positivo
- armadura superior aparece com mais intensidade sobre pilares, bordas e faixas de momento negativo
- o resultado atual e uma base de dimensionamento, nao um detalhamento executivo final por faixas

## 7. Punção

A punção e uma verificacao critica em radiers com cargas concentradas. O sistema calcula a razao entre solicitacao e resistencia normativa.

- razao maxima de punção: `n/d`
- atende: `True`
- local critico: `None`

Interpretacao didatica:

- `ratio < 1.0` indica atendimento no criterio adotado
- valores altos, mesmo abaixo de 1.0, sugerem estudar reforcos locais, pedestais, cogumelos ou engrossamentos
- quando a punção governa, a solucao deixa de ser um simples radier liso economico

## 8. Verificacoes de servico

O radier nao deve ser lido apenas pela resistencia. O modulo tambem verifica desempenho em uso:

- fissuracao em X atende: `True`
- fissuracao em Y atende: `True`
- criterio global de recalque atende: `True`

Ensino pratico:

- um radier pode atender a flexao e ainda ser ruim em recalque
- um radier pode ter pressao no solo aceitavel e ainda demandar revisao por punção local
- e a combinacao dessas leituras que sustenta a decisao tecnica final

## 9. Diagnostico final da solucao

Ao fim da cadeia, o sistema consolida um diagnostico orientativo para a viabilidade do radier liso.

- classificacao: `sem_diagnostico`
- recomendacao principal: `n/d`
- status profissional do checklist: `nao_apto_requer_revisao_tecnica`

Como ler esse diagnostico:

- `viavel preliminarmente` significa que o caminho do radier liso segue aberto
- `viavel com alertas` indica que ainda e uma opcao, mas com pontos de atencao
- `viavel com restricoes` mostra que a solucao exige comparacao com alternativas
- `nao recomendado` ou `estudar solucao alternativa` indica que o radier liso perdeu protagonismo tecnico no caso

## 10. Quando estudar outra tipologia

Didaticamente, o projetista deve sair do radier liso quando o caso mostrar sinais como:

- espessura muito alta para manter desempenho
- pressao de contato muito proxima ou acima da admissivel
- punção em margem curta ou nao atendente
- recalques ou distorcoes incompatíveis com a estrutura
- riscos de campo ou de solo que inviabilizam fundacao rasa simples

Alternativas tipicas:

- sapatas
- radier com reforcos locais
- radier nervurado
- radier estaqueado
- fundacao profunda

## 11. Limites deste guia

Este texto e propositalmente pedagogico. Ele explica o racional do modulo atual, mas nao substitui:

- verificacoes normativas complementares
- julgamento geotecnico da obra real
- detalhamento executivo de armaduras
- compatibilizacao com a superestrutura e com a execucao

## 12. Fechamento

Em resumo, dimensionar um radier nao e apenas escolher uma espessura e calcular aço. O processo correto passa por:

1. entender cargas e solo
2. modelar a interacao laje-solo
3. verificar pressoes e recalques
4. dimensionar flexao
5. verificar punção
6. consolidar um diagnostico tecnico da viabilidade da solucao

Esse e exatamente o encadeamento que o modulo procura ensinar neste caso.
