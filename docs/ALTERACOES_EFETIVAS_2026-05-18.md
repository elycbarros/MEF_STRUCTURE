# Alteracoes efetivas - 2026-05-18

## Objetivo

Registrar as correcoes efetivas realizadas hoje no MEF Structural apos a auditoria visual e numerica do modulo Mestre. O foco foi reduzir erros de logica, divergencias matematicas entre solvers e falhas de interface que impediam a validacao.

## Backend / solvers

- Vigas: a rota Python voltou a ser a fonte autoritativa para o solver 1D de vigas enquanto o caminho Rust apresentar inconsistencia nas forcas de extremidade. No caso auditado de 6 m com 20 kN/m mais peso proprio, o caminho Rust retornava equilibrio global incorreto.
- Vigas: normalizacao de cobrimento quando informado em milimetros, evitando que `cover=30` seja interpretado como 30 m.
- Porticos: classificacao de barras corrigida para retornar nomes semanticos (`column` e `beam`) no motor Python, mantendo codigos numericos apenas na adaptacao para o core Rust.
- Porticos: deslocamentos sincronizados apos aceleracao de Aitken no P-Delta, evitando que `U_raw` e `displacements` fiquem inconsistentes.
- Estabilidade global: `gamma_z` deixa de assumir valor negativo em caso divergente; quando `DeltaM/M1 >= 1`, o caso passa a ser marcado como instavel/divergente com `gamma_z = inf`.
- Pilares: correcao do `NameError` em `fyd` no dimensionamento minimo de armadura, usando `fyk/1.15`.
- Lajes: correcao do `NameError` de `fck` na geracao do quadro pedagogico.

## Frontend Mestre

- Vigas: os apoios do diagrama voltaram a ser desenhados com fallback robusto. A visualizacao agora usa apoios explicitos quando existirem, reacoes calculadas quando disponiveis, ou pino/rolete padrao antes do calculo.
- Vigas: a regiao vertical dos apoios passou a ser reservada mesmo antes de haver resultados, evitando que os simbolos desaparecam ou fiquem fora do SVG.
- Vigas: cores dos apoios no SVG usam valor direto em vez de variavel CSS, reduzindo falhas de renderizacao.
- Pilares: `FiberMeshView` aceita fibras tanto em formato de array quanto em formato de objeto, eliminando o erro runtime `f is not iterable`.
- Porticos: adicionado modo didatico opcional de portico especial apoiado em viga isostatica, com pino/rolete na base e controle persistido no estado Mestre.
- Sapatas: coerção booleana no `Switch` de ISE nao linear para destravar o typecheck do Next.
- Estabilidade: leitura numerica segura dos parametros de altura, frequencia e vento, alem de coerção booleana nos checkboxes dinamico/sismico.

## Testes e verificacoes

- Adicionada suite `mef_engine/tests/test_solver_audit.py` com invariantes criticos:
  - equilibrio e momento maximo de viga biapoiada com carga uniforme;
  - deslocamento e equilibrio de console em portico;
  - classificacao de barras como pilar/viga;
  - equilibrio global de laje apoiada nas bordas;
  - pressao admissivel em sapata isolada;
  - execucao do solver de pilares sem `NameError`;
  - estabilidade global sem `gamma_z` negativo.
- Ajustadas unidades em testes antigos de vigas para kN/m, alinhadas ao contrato atual do solver.
- Ajustado `verify_reactions.py` para usar as chaves reais de reacao retornadas pelo solver.

## Observacoes de risco

- O caminho Rust de viga 1D deve permanecer desabilitado para vigas ate haver uma suite dedicada de paridade Python vs Rust cobrindo convencoes de carga, reacoes e forcas internas.
- O arquivo `mef_engine/scratch_list_routes.py` permanece fora do commit por parecer rascunho auxiliar nao integrado ao pacote de correcao.
