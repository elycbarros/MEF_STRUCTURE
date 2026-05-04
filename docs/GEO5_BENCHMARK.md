# Benchmark Comercial - Radier e Fundacoes

Fonte informada pelo usuario: arquivos retirados do site do GEO5.

Arquivos locais analisados:

- `/Users/elycbarros/Downloads/em20_pt.pdf`
- `/Users/elycbarros/Downloads/em21_pt.pdf`
- `/Users/elycbarros/Downloads/em22_pt.pdf`
- `/Users/elycbarros/Downloads/em30_pt.pdf`

## Objetivo

Usar os manuais como benchmark tecnico e de produto para evoluir o Radier Lab sem copiar interface, texto ou implementacao proprietaria. A referencia serve para mapear capacidades esperadas em software comercial de geotecnia/fundacoes e transformar isso em backlog proprio.

## EM20 - Metodo dos Elementos Finitos: Introducao

Tema principal: fundamentos do uso do MEF no GEO5 para problemas geotecnicos.

Pontos de referencia:

- separacao por tipo de problema, incluindo problema plano e simetria axial
- organizacao por tipo de analise, como tensao, fluxo, assentamento e consolidacao
- fluxo por etapas de construcao
- importancia de topologia, condicoes de contorno, materiais, malha e resultados
- uso de elementos estruturais como vigas no ambiente MEF
- leitura dos resultados como deformacoes, tensoes, forcas internas e evolucao por etapas

Aplicacao ao Radier Lab:

- explicitar melhor o tipo de modelo adotado em cada caso
- registrar hipoteses de placa/radier sobre solo Winkler no relatorio
- manter trilha de calculo por etapas, mesmo quando a analise for automatizada
- fortalecer a explicacao da malha e das condicoes de contorno no memorial

## EM21 - Analise de Assentamento do Terreno

Tema principal: assentamento sob sobrecarga continua usando MEF.

Pontos de referencia:

- definicao clara do problema antes da modelagem
- parametros geotecnicos do solo, incluindo peso especifico, modulo de elasticidade, modulo de relaxamento, Poisson, coesao e atrito
- comparacao entre modelos materiais
- sequencia de construcao: tensao geostatica, aplicacao de carga, relaxamento
- avaliacao de deformacao vertical/assentamento
- sensibilidade de resultados a modelo material e malha

Aplicacao ao Radier Lab:

- criar bloco de entrada geotecnica mais rico que apenas `kv` e `sigma_adm`
- melhorar o relatorio de recalques com leitura de uso/limite e sensibilidade
- adicionar comparacao orientativa entre Winkler e estimativas de assentamento por parametros geotecnicos
- evoluir o modo estudo/pericia para explicar a origem de cada parametro

## EM22 - Assentamento da Fundacao de um Silo Circular

Tema principal: fundacao circular de silo por MEF com simetria axial.

Pontos de referencia:

- uso de simetria axial para problema circular simetrico
- modelagem da fundacao como elemento estrutural ligado ao solo
- consideracao de etapas de carregamento e descarregamento
- avaliacao de assentamento e forcas internas
- relacao entre geometria, hipotese de simetria e validade do modelo

Aplicacao ao Radier Lab:

- criar no futuro templates especificos para radiers circulares ou tanques/silos
- separar casos de geometria retangular atual de casos axisimetricos ou arbitrarios
- adicionar verificacao de validade da hipotese geometrica
- preparar estrutura para elementos de viga/anel/ribbing acoplados ao radier

## EM30 - Importacao de Geometria por DXF

Tema principal: importacao, limpeza e uso de geometria DXF no GEO5 FEM.

Pontos de referencia:

- DXF pode conter informacao excessiva ou inadequada para analise
- importacao confiavel exige limpeza, simplificacao e organizacao por camadas/entidades
- ha diferenca entre usar DXF como template visual e importar entidades automaticamente
- interfaces de solo e estruturas podem ser extraidas do desenho quando o arquivo esta bem preparado
- manuais comerciais tratam problemas comuns de importacao e boas praticas de preparacao

Aplicacao ao Radier Lab:

- DXF deve entrar primeiro como importacao assistida/template, nao como promessa de automacao total
- criar validador de geometria antes de gerar malha
- exigir poligonos fechados, unidades conhecidas e entidades filtradas
- registrar no relatorio se a geometria veio de entrada manual, CSV ou DXF
- planejar exportacao DXF de malha, pilares, contornos e mapas de resultado

## Matriz de Lacunas Comerciais

| Capacidade | Radier Lab hoje | Benchmark GEO5 | Prioridade |
| :--- | :--- | :--- | :--- |
| MEF para radier/laje de fundacao | Implementado para nucleo atual | Produto comercial consolidado | Alta |
| Malha automatica flexivel | Malha regular atual | Malha/refinamento por geometria | Alta |
| Geometria arbitraria | Nao consolidada | Recurso esperado | Alta |
| Etapas de construcao | Parcial no pipeline/relatorio | Fluxo central do FEM | Media |
| Modelos materiais geotecnicos | Winkler simplificado | Modelos geotecnicos variados | Media |
| Simetria axial | Nao implementado | Usado em fundacoes circulares | Baixa/media |
| Elementos de viga acoplados | Planejado | Recurso de modelagem | Media |
| DXF import/export | Planejado | Recurso comercial | Alta |
| Relatorio tecnico final | Markdown/JSON | PDF/Word comercial | Alta |
| Casos de carga e combinacoes | Simplificado | Multicaso/multicombinacao | Alta |

## Backlog Derivado

1. Criar camada de geometria:
   - contorno do radier
   - aberturas/recortes
   - pilares/pontos de carga
   - linhas de carga/vigas futuras

2. Criar gerador de malha melhorado:
   - malha regular como fallback
   - refinamento local em pilares e bordas
   - validacao visual e numerica da malha

3. Evoluir entradas geotecnicas:
   - manter `kv` como caminho rapido
   - permitir perfil com `E`, `nu`, `gamma`, `c`, `phi`
   - mapear parametros para correlacoes e faixas de confiabilidade

4. Expandir casos de carga:
   - multiplos casos
   - combinacoes de servico e ELU
   - cargas pontuais, lineares e distribuidas

5. Iniciar DXF de forma controlada:
   - importacao como template
   - validacao de unidades/camadas
   - exportacao de resultados principais

6. Profissionalizar relatorios:
   - manter Markdown/JSON para rastreabilidade
   - adicionar exportacao PDF
   - estudar exportacao DOCX/Word

## Nota de escopo

Os manuais GEO5 sao referencia externa de produto e fluxo de engenharia. O Radier Lab deve manter linguagem, arquitetura, criterios e implementacao proprios, usando o benchmark apenas para orientar lacunas e prioridades.

## AltoQi Eberick - Dimensionamento de Laje de Fundacao Tipo Radier

Referencia: https://suporte.altoqi.com.br/hc/pt-br/articles/360037896274

Data observada na pagina: 11 de novembro de 2025.

Pontos de referencia:

- radier descrito como laje apoiada diretamente no solo para receber cargas da superestrutura
- dimensionamento depende do porte da estrutura e da capacidade de suporte do solo
- coeficientes de recalque vertical e horizontal devem ser definidos com base em estudos geotecnicos
- analise de interacao solo-estrutura e usada para obter deslocamentos e esforcos internos
- pressao de contato e base para obtencao dos esforcos internos
- modelo comercial baseado em placa/malha sobre apoios elasticos equivalentes
- comportamento do solo baseado na hipotese de Winkler
- relacao explicita: `p_s = kv . d`
- valores inadequados de coeficiente de recalque podem gerar dimensionamento inadequado
- exemplo mostra que variar `kv` altera recalques e momentos fletores
- deslocamentos da ordem de 1 a 2 cm sao indicados como faixa usual de atencao; valores maiores exigem analise mais criteriosa de recalques e inclinacoes
- diagrama de pressoes no solo e resultado central de leitura
- verificacao de pressao de contato de tracao na base do radier
- verificacao de pressoes maiores que a admissivel
- verificacao a puncao junto aos pilares conforme NBR 6118, com perimetros criticos variando conforme posicao do pilar

Aplicacao ao Radier Lab:

- reforcar no relatorio a equacao `p = kv . d` como controle de consistencia Winkler
- manter `kv` como parametro de alto impacto no diagnostico e na sensibilidade
- adicionar gatilho explicito para tracao/perda de contato na base do radier
- destacar comparacao `qmax / sigma_adm` como aviso comercialmente esperado
- incluir leitura executiva de recalques acima de 10 a 20 mm como faixa que exige criterio adicional
- evoluir visualmente para diagrama/mapa de pressoes no solo como resultado de primeira classe
- detalhar punção por tipo de pilar: interior, borda e canto
