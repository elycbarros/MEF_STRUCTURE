# Referencias Academicas Brasileiras - Radier e Interacao Solo-Estrutura

Arquivos locais analisados:

- `/Users/elycbarros/Downloads/Dissertacao de Mestrado Ruiter da S Souza 2010.pdf`
- `/Users/elycbarros/Downloads/FILIPE ROCHA GUEDES e RENAN GODOY BURGOS - ANÁLISE ESTRUTURAL DE LAJE DE FUNDAÇÃO TIPO RADIER EM CONCRETO ARMADO.pdf`
- `/Users/elycbarros/Downloads/PB_COECI_2016_2_37.pdf`
- `/Users/elycbarros/Downloads/PROJETO_DE_ESTRUTURA_DE_FUNDACAO_EM_CONC.pdf`
- `/Users/elycbarros/Downloads/Revista Concreto IBRACON 109. Estruturas em concreto 2.pdf`
- `/Users/elycbarros/Downloads/salete,+10+ANÁLISE+DE+SENSIBILIDADE+DOS+PARÂMETROS+GEOTÉCNICOS+DE+UM+RADIER+ESTAQUEADO+MODELADO+UTILIZANDO+O+MÉTODO+DOS+ELEMENTOS+F.pdf`
- `/Users/elycbarros/Downloads/FINAL-PALESTRA-IE.pdf`

## Objetivo

Consolidar uma base academica brasileira para orientar o desenvolvimento do Radier Lab, especialmente nos temas de modelagem estrutural, interacao solo-estrutura, analogia de grelha, Winkler, MEF, protensao e radier estaqueado.

## 1. Souza, Ruiter da Silva - 2010

Titulo: `Analise dos fatores de interacao entre estacas em radier estaqueado: comparacao entre duas ferramentas numericas`.

Instituicao: Universidade Federal de Goias, dissertacao de mestrado em Geotecnia.

Foco tecnico:

- radier estaqueado
- interacao entre estacas
- comparacao entre ferramentas numericas
- MEF como referencia mais completa para radier estaqueado
- metodos simplificados e fatores de interacao
- componentes do sistema: solo, estacas e radier
- calibracao de distancia maxima de interacao entre estacas

Uso no Radier Lab:

- reforca que radier estaqueado deve ser modulo proprio, nao variacao simples do radier liso
- orientar futuro comparador de solucoes quando o radier liso nao atende
- base para backlog de interacao estaca-estaca, estaca-solo, solo-estaca e solo-solo
- justificar mensagens de escopo no diagnostico atual

Status sugerido:

- `referencia_para_futuro_modulo`
- nao implementar diretamente no nucleo atual

## 2. Guedes e Burgos - 2014

Titulo: `Analise estrutural de laje de fundacao tipo radier em concreto armado`.

Instituicao: Universidade Federal de Pernambuco, TCC de Engenharia Civil.

Foco tecnico:

- radier em concreto armado
- analise estrutural por diferentes estrategias de modelagem
- interacao solo-estrutura
- analogia de grelha
- metodo dos elementos finitos
- hipotese de Winkler
- coeficiente de reacao vertical do solo
- SAP2000 como ferramenta de estudo
- variacao de `Kv`, espessura, momentos fletores e deslocamentos
- comparacao de apoios elasticos tipo `Area Springs` e `Joint Springs`

Uso no Radier Lab:

- validar a importancia da sensibilidade de `kv`
- inspirar comparacao entre modelos de apoio elastico
- fortalecer relatorio de influencia do solo nos esforcos e deslocamentos
- apoiar modulo futuro de analogia de grelha como metodo comparativo

Status sugerido:

- `referencia_de_validacao_modelagem`
- util para testes comparativos e exemplos didaticos

## 3. Cibulski Junior - 2016

Titulo: `Estudo da modelagem de radier rigido em concreto armado na analise da interacao solo-estrutura`.

Instituicao: Universidade Tecnologica Federal do Parana, TCC de Engenharia Civil.

Foco tecnico:

- radier rigido em concreto armado
- interacao solo-estrutura
- solo como semi-espaco elastico linear
- hipotese de Winkler com cama de molas distribuidas
- obtencao do coeficiente de reacao vertical
- SAP2000
- analogia de grelha
- redistribuicao de esforcos na estrutura
- importancia da previsao de recalques
- mencao a radier estaqueado como alternativa quando o radier isolado nao satisfaz recalques

Uso no Radier Lab:

- apoiar o diagnostico de viabilidade do radier liso
- reforcar que recalque e ISE devem afetar a recomendacao de solucao
- orientar mensagens sobre radier estaqueado como alternativa, sem calcula-lo no modulo atual
- embasar checklist de obtencao e confiabilidade de `kv`

Status sugerido:

- `referencia_para_diagnostico_e_ise`
- util para calibrar alertas de recalque e rigidez do solo

## 4. Doria, Luis Eduardo Santos - 2007

Titulo: `Projeto de estrutura de fundacao em concreto do tipo radier`.

Instituicao: Universidade Federal de Alagoas, dissertacao de mestrado em Engenharia Civil - Estruturas.

Foco tecnico:

- radier em concreto armado e concreto protendido
- classificacao quanto a geometria e rigidez
- interacao solo-estrutura
- pressoes de contato
- constantes elasticas do solo
- ensaio de placa, tabelas e calculo de recalque para determinacao de parametros
- placa sobre solo de Winkler
- sistema de vigas sobre base elastica
- diferencas finitas
- elementos finitos
- analogia de grelha sobre base elastica
- CAD/TQS
- comparacao de consumo e custo entre radier armado e protendido

Uso no Radier Lab:

- orientar classificacao de tipos de radier no front e no relatorio
- embasar modulo futuro de protensao como alternativa, nao como item imediato
- apoiar estimativas de custo/consumo no comparador de solucoes
- fortalecer entrada de parametros geotecnicos por ensaio de placa, tabelas e recalques

Status sugerido:

- `referencia_estrutural_principal`
- util para roadmap de grelha, protensao e comparador economico

## 5. Fortes, Caria, Funahashi Jr. e Kuperman - IBRACON 109, 2023

Titulo: `Fundacao em radier de grandes dimensoes: projeto estrutural e estudo termico`.

Fonte: Revista Concreto & Construcoes, IBRACON, ed. 109, jan-mar 2023.

Foco tecnico:

- radier de grandes dimensoes em concreto armado
- edifício residencial no Morumbi, Sao Paulo
- dimensoes da ordem de dezenas de metros e espessura elevada
- interacao entre equipes de estrutura, fundacao e tecnologia do concreto
- verificacoes de flexao, cisalhamento e puncao
- uso de ABNT NBR 6118:2014 e ACI 318:2005 para puncao no caso estudado
- estudo termico de concreto massa
- metodo da maturidade, ASTM C1074-11
- controle de temperatura de lancamento com concreto pre-refrigerado
- risco de fissuracao termica e formacao de etringita tardia
- validacao/iteracao com deslocamentos maximos e distorcao maxima

Uso no Radier Lab:

- criar alerta de `radier espesso / concreto massa` quando h ou volume forem altos
- incluir no diagnostico uma recomendacao de estudo termico para grandes volumes
- separar verificacoes estruturais de verificacoes tecnologicas do concreto
- preparar futuro checklist executivo para concretagem, temperatura, juntas, etapas e monitoramento
- reforcar que radiers muito espessos exigem compatibilizacao com geotecnia e tecnologia do concreto

Status sugerido:

- `referencia_para_checklist_executivo`
- util para proxima camada de risco tecnologico/construtivo

## 6. Miloch e Faria - 2021

Titulo: `Analise de sensibilidade dos parametros geotecnicos de um radier estaqueado modelado utilizando o metodo dos elementos finitos`.

Fonte: Revista de Engenharia e Tecnologia, v. 13, n. 4, dez. 2021.

Foco tecnico:

- radier estaqueado quadrado com 16 estacas
- MEF com modelo 2D usando estado plano de deformacao e simetria
- validacao frente a modelo 3D da literatura
- ANSYS com elementos PLANE82, CONTA172 e TARGET169
- contato solo-fundacao
- modelo constitutivo Drucker-Prager
- parametros aleatorios via Monte Carlo
- variaveis de entrada: geometria da fundacao, propriedades do concreto, indices fisicos e resistencia ao cisalhamento do solo em condicao nao drenada
- saida principal: deslocamento maximo resultante
- comprimento das estacas e modulo de elasticidade do solo como variaveis mais influentes

Uso no Radier Lab:

- reforca que radier estaqueado exige modulo proprio probabilistico/sensibilidade
- orientar futuro estudo de variaveis dominantes para piled raft
- para o comparador atual, indicar que comprimento de estacas e rigidez do solo sao parametros criticos quando a alternativa for radier estaqueado
- ampliar a matriz de sensibilidade futura para alem de `kv`, incluindo `E_solo`, geometria de estacas e propriedades do contato

Status sugerido:

- `referencia_para_futuro_modulo_probabilistico`
- nao entra no nucleo atual de radier liso

## 7. Souza, Fabio Albino - Palestra Instituto de Engenharia

Titulo: `Radier Simples, Armado e Protendido`.

Arquivo: `FINAL-PALESTRA-IE.pdf`.

Foco tecnico:

- definicao de radier/laje sobre solo com referencia a ACI 360R-10
- tipologias de radier:
  - com capiteis
  - com pedestais
  - nervurado
  - estaqueado
  - flutuante
  - simples, armado e protendido
- modelo de Winkler e coeficiente de reacao vertical do solo
- metodos para obter `kv`:
  - ensaio de placa
  - correlacoes com SPT
  - correlacoes com tensoes admissiveis
  - correlacoes com CBR
  - normas internacionais
  - outros metodos de pesquisadores
- metodo F-CBR para estimativa de coeficiente de reacao vertical
- observacao sobre distribuicao de pressao real em solos coesivos e nao coesivos
- solos expansivos, colapsiveis, aterros e nivel d'agua como condicionantes
- radier estaqueado para casos em que radier apoiado no solo nao suporta carregamentos ou apresenta recalques inaceitaveis
- manta retardadora de vapor, distinta de lona plastica comum
- fator de forma do radier: `SF = perimetro^2 / area`
- recomendacao de investigar efeitos de torcao quando o fator de forma ultrapassa valor limite indicado na palestra
- recomendacoes geometricas para nervuras
- necessidade de norma especifica para radier no contexto brasileiro

Uso no Radier Lab:

- ampliar `foundationTypes` com descricoes tecnicas melhores para capiteis, pedestais, nervurado, flutuante, estaqueado e protendido
- criar campo de origem do `kv` com opcao futura `F-CBR`
- adicionar checklist executivo:
  - solo expansivo
  - solo colapsivel
  - aterro
  - nivel d'agua/subpressao
  - manta retardadora de vapor
- adicionar metrica `shape_factor = perimetro^2 / area`
- gerar alerta de forma alongada/torcao quando o fator de forma for elevado
- preparar backlog para radier nervurado com limites geometricos preliminares
- manter radier protendido como comparador futuro, nao como modulo atual

Status sugerido:

- `referencia_pratica_de_tipologias_e_execucao`
- util para UI guiada, checklist de campo e comparador de solucoes

## Matriz de Temas

| Tema | Referencias fortes | Aplicacao no Radier Lab |
| :--- | :--- | :--- |
| Winkler / cama de molas | Guedes e Burgos, Cibulski, Doria | Nucleo atual e validacao de `kv` |
| Interacao solo-estrutura | Todos | Diagnostico, relatorio e calibracao de sensibilidade |
| Analogia de grelha | Guedes e Burgos, Cibulski, Doria | Futuro metodo comparativo ou fallback |
| MEF | Souza, Guedes e Burgos, Doria | Nucleo numerico e benchmark |
| Radier estaqueado | Souza, Cibulski | Futuro modulo separado e recomendacao de alternativa |
| SAP2000/TQS/DIANA | Souza, Guedes e Burgos, Cibulski, Doria | Benchmark de resultados e fluxo profissional |
| Coeficiente de reacao vertical | Guedes e Burgos, Cibulski, Doria | Entrada geotecnica, confiabilidade e sensibilidade |
| Radier protendido | Doria | Futuro comparador tecnico-economico |
| Custo/consumo | Guedes e Burgos, Doria | Comparador de solucoes |
| Concreto massa / estudo termico | Fortes et al. | Checklist executivo para radiers espessos |
| Sensibilidade probabilistica | Miloch e Faria, Souza | Futuro modulo de incerteza para piled raft e parametros geotecnicos |
| Tipologias e execucao | Fabio Albino de Souza | UI guiada, checklist executivo e comparador |
| Fator de forma / torcao | Fabio Albino de Souza | Novo gatilho geometrico no diagnostico |
| F-CBR / origem de kv | Fabio Albino de Souza | Futuro metodo de entrada/calibracao de `kv` |

## Backlog Academico Derivado

1. Criar `reference_matrix` brasileira:
   - Doria 2007
   - Souza 2010
   - Guedes e Burgos 2014
   - Cibulski 2016

2. Melhorar entrada de `kv`:
   - origem do parametro
   - prova de carga
   - tabela/correlacao
   - calculo por recalque
   - fator de confiabilidade

3. Criar comparador de modelagem:
   - placa MEF atual
   - analogia de grelha
   - modelo rigido simplificado
   - leitura de diferencas nos momentos, pressoes e recalques

4. Ampliar diagnostico:
   - quando radier liso e coerente
   - quando radier liso exige reforco local
   - quando estudar radier estaqueado
   - quando fundacao profunda independente faz mais sentido

5. Criar comparador tecnico-economico:
   - concreto armado
   - radier com engrossamentos
   - radier protendido
   - sapatas
   - radier estaqueado/fundacao profunda como alternativas orientativas

6. Preparar validacoes cruzadas:
   - exemplos academicos simplificados
   - variacao de `kv`
   - variacao de espessura
   - comparacao de deslocamentos e momentos maximos

7. Criar checklist tecnologico para radiers espessos:
   - volume de concreto
   - espessura elevada
   - temperatura de lancamento
   - plano de concretagem em etapas
   - risco de fissuracao termica
   - necessidade de estudo de maturidade/monitoramento

8. Preparar matriz de incerteza para radier estaqueado futuro:
   - comprimento de estacas
   - modulo de elasticidade do solo
   - resistencia nao drenada
   - contato solo-fundacao
   - deslocamento maximo como variavel de saida

9. Ampliar checklist de tipologia e execucao:
   - tipo de radier escolhido
   - solo expansivo/colapsivel
   - aterro e atrito negativo quando houver estacas
   - nivel d'agua/subpressao
   - manta retardadora de vapor
   - fator de forma e torcao
   - nervuras e limites geometricos preliminares

## Nota de Escopo

As referencias academicas devem embasar criterios, mensagens, validacoes e prioridades. Elas nao substituem verificacao normativa, responsabilidade tecnica ou validacao independente dos resultados do software.
