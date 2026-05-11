# Revisao Numerica Da Viga Cross

Data: 2026-05-11

## Objetivo

Verificar o motor didatico Hardy Cross contra casos conhecidos e contra o solver MEF de vigas (`beam_solver.run_beam_analysis`).

## Escopo

Arquivos revisados:

```text
mef_frontend/src/lib/vigacross/engine.ts
mef_engine/beam_solver.py
```

O comparativo foi feito sem peso proprio no MEF para manter equivalencia com a Viga Cross, que hoje considera apenas as cargas informadas.

## Correcoes Aplicadas

1. Liberacao de extremidades articuladas.

Antes, a Viga Cross apenas zerava o momento em uma extremidade articulada. Isso estava incompleto para o metodo de distribuicao de momentos, pois a liberacao deve transmitir metade da correcao para a extremidade oposta quando ela nao estiver liberada.

Efeito:

- viga continua de dois vaos iguais com carga uniforme agora gera momento interno `qL2/8`, como esperado;
- casos com apoio extremo articulado nao ficam artificialmente sub-rigidos.

2. Convencao de sinais para reacoes e diagramas.

Os momentos finais do Hardy Cross estavam corretos na convencao local do metodo, mas a conversao para diagrama fisico e reacoes estava usando o sinal da extremidade direita de modo inconsistente.

Efeito:

- apoio hiperestatico aparece com momento negativo no diagrama;
- reacoes de vigas continuas passam a bater com valores conhecidos;
- cortante, momento e flecha ficam coerentes com o MEF.

## Casos Validados

### Caso 1 - Viga Biapoiada

Entrada:

```text
L = 4 m
q = 20 kN/m
apoios = pin, pin
```

Resultado Viga Cross:

```text
R1 = 40 kN
R2 = 40 kN
Mmax = 40 kNm
Vmax = 40 kN
```

Resultado MEF:

```text
R1 ~= 40 kN
R2 ~= 40 kN
Mmax ~= 40 kNm
Vmax ~= 40 kN
```

Status: OK.

### Caso 2 - Viga Biengastada

Entrada:

```text
L = 4 m
q = 20 kN/m
apoios = fixed, fixed
```

Resultado Viga Cross:

```text
R1 = 40 kN
R2 = 40 kN
Mapoio = -26.67 kNm
Msagente = 13.33 kNm
```

Resultado MEF:

```text
R1 ~= 40 kN
R2 ~= 40 kN
Mabs ~= 26.63 kNm
Msagente ~= 13.37 kNm
```

Status: OK.

### Caso 3 - Viga Continua Com Dois Vaos Iguais

Entrada:

```text
Ltotal = 8 m
vaos = 4 m + 4 m
q = 20 kN/m em ambos os vaos
apoios = pin, pin, pin
```

Resultado Viga Cross:

```text
R1 = 30 kN
R2 = 100 kN
R3 = 30 kN
Mapoio interno = -40 kNm
Msagente ~= 22.4 kNm
Vmax = 50 kN
```

Resultado MEF:

```text
R1 ~= 30.05 kN
R2 ~= 99.90 kN
R3 ~= 30.05 kN
Mapoio interno ~= -39.80 kNm
Msagente ~= 22.48 kNm
Vmax ~= 49.95 kN
```

Status: OK.

## Observacoes Importantes

- A Viga Cross ainda e um modulo didatico local no frontend.
- Ela nao substitui o solver executivo MEF de vigas.
- Ela ainda nao considera peso proprio automaticamente.
- Ela ainda nao dimensiona armaduras conforme NBR 6118; apenas calcula redistribuicao de momentos, reacoes e diagramas elasticos.
- Para comparacao justa com o MEF, usar `include_self_weight=False` no `beam_solver`.

## Proximo Passo Recomendado

Criar uma camada de auditoria automatica para Viga Cross:

```text
Viga Cross -> resultado didatico Hardy Cross
Beam Solver -> resultado MEF elastico equivalente
Duelo Estrutural -> diferenca percentual por reacao, momento e cortante
```

Isso permitiria mostrar ao usuario quando a Viga Cross esta sendo usada como verificacao manual didatica e quando deve migrar para o calculo executivo por MEF.
