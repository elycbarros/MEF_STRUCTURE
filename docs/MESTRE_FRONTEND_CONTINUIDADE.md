# Continuidade - Atlas Mestre Frontend e Roteamento de Cálculo

Atualizado em: 2026-05-11

## Escopo Desta Retomada

Esta retomada focou no app novo `mef_frontend`, especialmente na rota Mestre:

- `mef_frontend/src/app/(app)/mestre/page.tsx`
- `mef_frontend/src/app/(app)/mestre/components/*`
- `mef_frontend/src/lib/*`
- `mef_engine/routes/special.py`
- builders pedagógicos em `mef_engine/reporting/pedagogy/*`

O `mef_dashboard` antigo foi analisado, mas não foi usado como base de evolução nesta etapa.

## Decisão Arquitetural

O caminho escolhido foi consolidar `mef_frontend` como app principal do Atlas Mestre e deixar `mef_dashboard` como fonte futura de componentes/ideias.

Motivo: `mef_frontend` tem App Router, estado mais simples com Zustand, UI mais focada no fluxo pedagógico e menor dívida estrutural.

## O Que Foi Feito No Frontend

### 1. Limpeza Técnica Inicial

Foram criados tipos centrais para o Mestre em:

- `mef_frontend/src/lib/mestre-types.ts`

Esse arquivo agora centraliza:

- `MestreElementType`
- `MestreParams`
- `MestreStep`
- payloads de viga, apoio, carga, solo
- `MestreApiResponse`
- helper `extractMestreSteps`

Também foram tipados/ajustados:

- `mef_frontend/src/lib/store-mestre.ts`
- `mef_frontend/src/lib/api-mestre.ts`

Resultado: `npm run lint` e `npm run build` passaram no `mef_frontend`.

### 2. Separação Dos Playgrounds

Antes, viga, pilar e laje usavam o mesmo `BeamPlayground`.

Agora existem componentes separados:

- `BeamPlayground.tsx` - viga
- `ColumnPlayground.tsx` - pilar
- `SlabPlayground.tsx` - laje/radier didático
- `PilePlayground.tsx` - estaca
- `PileCapPlayground.tsx` - bloco sobre estacas
- `FootingPlayground.tsx` - sapata
- `SpecialPlayground.tsx` - escadas e elementos especiais

A seleção acontece em:

- `mef_frontend/src/app/(app)/mestre/page.tsx`

Regra de UX importante:

- Os solvers Mestre não disparam automaticamente ao entrar no módulo.
- O usuário deve ajustar os parâmetros e clicar no botão de cálculo.
- Foram removidos os `useEffect`/`debounce` que calculavam ao montar o componente ou a cada alteração de campo.
- O memorial vazio agora informa: "Ajuste os parâmetros e clique em calcular para gerar o memorial."

### 3. Correção Do Viewport 3D

Arquivo:

- `mef_frontend/src/app/(app)/mestre/components/Beam3DView.tsx`

Correções feitas:

- Estaca deixou de parecer pilar: agora fica enterrada abaixo da cota 0.
- Estaca não usa mais animação `Float`.
- Bloco sobre estacas deixou de puxar viga: agora mostra bloco, pilar e duas estacas.
- Escada e especiais deixaram de cair no modelo de viga.
- Foram adicionados modelos leves para:
  - escada
  - muro de arrimo
  - reservatório
  - consolo curto
  - dente Gerber
  - viga parede
  - fallback genérico para especiais futuros

Importante: o fallback visual agora nunca usa `BeamModel`. Se um especial novo não tiver modelo próprio, ele usa `GenericSpecialModel`.

### 4. Painel Dos Especiais

Arquivo:

- `mef_frontend/src/app/(app)/mestre/components/SpecialPlayground.tsx`

Correções:

- `stair` agora recebe campos de escada corretamente.
- Antes havia divergência: sidebar enviava `stair`, mas o painel esperava `stairs`.
- Adicionados campos mínimos para:
  - escada
  - muro de arrimo
  - reservatório
  - dente Gerber
  - viga parede
  - consolo curto já existia

### 5. Diagramas Técnicos Sem Imagens

Pedido posterior: não usar imagens estáticas nos memoriais; usar diagramas gerados.

Implementado:

- Backend passou a emitir `diagramData` em vez de caminhos `/diagrams/*.png`.
- `MemorialEngine.add_step()` aceita `diagramData`.
- Frontend renderiza `diagramData` com SVG via `TechnicalDiagram`.
- `MemorialAccordion` não renderiza mais `<Image>` para diagramas.
- `MemorialHeader` não exporta mais `<img>` de diagramas estáticos no HTML.

Arquivo novo:

- `mef_frontend/src/app/(app)/mestre/components/TechnicalDiagram.tsx`

Builders ajustados:

- `mef_engine/reporting/pedagogy/slab.py`
- `mef_engine/reporting/pedagogy/foundation.py`
- `mef_engine/reporting/pedagogy/special.py`

Diagramas técnicos atuais:

- sapata isolada em corte com pilar, terreno, base e pressão de contato
- laje/placa Mindlin
- muro de arrimo
- escada
- reservatório
- consolo
- dente Gerber
- viga parede

## O Que Foi Feito No Backend

### 1. Rota Mestre Com Rastreabilidade

Arquivo:

- `mef_engine/routes/special.py`

Foi adicionado `calculation_trace` na resposta da rota:

```json
{
  "requested_type": "slab",
  "solver_module": "lajes_solver.LajesMindlinSolver",
  "blackboard_builder": "build_lajes_blackboard",
  "classical_check": true,
  "mef_check": true
}
```

Isso permite verificar, pelo frontend ou logs, se cada módulo puxou o cálculo correto.

### 2. Correção Crítica: Laje Puxava Viga

Problema encontrado:

- `type == "slab"` chamava `solver.solve_beam()`
- também usava `build_beam_blackboard()`

Correção:

- `type == "slab"` agora chama `lajes_solver.LajesMindlinSolver`
- usa `build_lajes_blackboard`
- retorna resultado MEF de placa Mindlin
- inclui referência clássica simples de faixa equivalente

Arquivos envolvidos:

- `mef_engine/routes/special.py`
- `mef_engine/reporting/pedagogy/slab.py`

### 3. Correção: Sapata Tinha Caminho Duplicado

Problema encontrado:

- havia dois blocos `elif type == "footing"`
- o segundo, com `footing_solver.solve_isolated_footing`, era inalcançável
- a rota acabava usando uma solução simplificada dentro de `SpecialElementsSolver`

Correção:

- sapata agora usa `footing_solver.solve_isolated_footing`
- memorial usa `build_footing_blackboard`

Arquivos:

- `mef_engine/routes/special.py`
- `mef_engine/reporting/pedagogy/foundation.py`

### 4. Bloco Sobre Estacas

Problema:

- `pile_cap` estava no frontend, mas não tinha rota de cálculo conectada.

Correção:

- `pile_cap` agora chama `pile_cap_solver.solve_pile_cap_2_piles`
- memorial usa `build_pile_cap_blackboard`

Arquivo:

- `mef_engine/routes/special.py`

### 5. Ajustes Nos Builders Pedagógicos

Arquivos:

- `mef_engine/reporting/pedagogy/base.py`
- `mef_engine/reporting/pedagogy/slab.py`
- `mef_engine/reporting/pedagogy/foundation.py`
- `mef_engine/reporting/pedagogy/special.py`

Correções:

- `MemorialEngine.add_step()` agora aceita `detailingData`
- `slab.py` importou `math` e corrigiu uso de `result` para `res`
- `foundation.py` importou `math` e passou a reconhecer `as_a_cm2/as_b_cm2`
- `special.py` importou `math`

## Matriz Atual: Módulo -> Solver

Verificado por chamada direta de `calculate_special`.

```text
beam            -> beam_solver.run_beam_analysis              clássico=True  MEF=True
slab            -> lajes_solver.LajesMindlinSolver            clássico=True  MEF=True
column          -> column_solver.solve_column_section         clássico=True  MEF=False
footing         -> footing_solver.solve_isolated_footing      clássico=True  MEF=False
pile_cap        -> pile_cap_solver.solve_pile_cap_2_piles     clássico=True  MEF=False
pile            -> piles_engine.PilesEngine.run_full_analysis clássico=True  MEF=False
stair           -> SpecialElementsSolver.solve_stair          clássico=True  MEF=False
retaining_wall  -> SpecialElementsSolver.solve_retaining_wall clássico=True  MEF=False
reservoir       -> SpecialElementsSolver.solve_reservoir      clássico=True  MEF=False
corbel          -> SpecialElementsSolver.solve_corbel         clássico=True  MEF=False
gerber_tooth    -> SpecialElementsSolver.solve_gerber_tooth   clássico=True  MEF=False
deep_beam       -> SpecialElementsSolver.solve_deep_beam      clássico=True  MEF=False
```

Interpretação:

- Viga e laje fazem clássico + MEF.
- Demais módulos estão roteados para seus cálculos corretos, mas são analíticos/clássicos por enquanto.

## Validações Executadas

Frontend:

```bash
cd mef_frontend
npm run lint
npm run build
```

Ambos passaram.

Backend:

```bash
cd mef_engine
python3 -m py_compile routes/special.py reporting/pedagogy/base.py reporting/pedagogy/slab.py reporting/pedagogy/foundation.py reporting/pedagogy/special.py
```

Passou.

Também foi executada uma chamada direta em Python para os módulos Mestre principais e especiais, confirmando `calculation_trace` e retorno dos passos pedagógicos.

## Pontos De Atenção Para Próxima Continuidade

## Atualização: Tipo De Estaca Hélice Contínua

- A opção `Hélice contínua` foi adicionada ao seletor de estacas no frontend com valor interno `cfa`.
- O solver `mef_engine/piles_engine.py` agora reconhece `cfa` em Aoki-Velloso e Decourt-Quaresma.
- Critério adotado nesta etapa: usar os mesmos fatores conservadores da estaca escavada (`F1=3.0`, `F2=6.0`, `alpha_dq=0.85`, `beta_dq=0.80`) por ser moldada in loco. Se houver tabela normativa/escritório específica para hélice contínua, calibrar esses fatores depois.
- A suíte `tests/test_mestre_routing.py` inclui caso de rota para `pile_type="cfa"`.

## Atualização: Conferência Solver E Memorial Por Tipo

- A rota Mestre agora aceita `stair` como tipo canônico de escada e mantém `stairs` apenas como alias de compatibilidade.
- O memorial de escada foi corrigido para registrar `element_type="stair"`, alinhado ao frontend e ao `calculation_trace`.
- Foram expostos no frontend os tipos que já existiam no backend: `concrete_wall` (Parede de Concreto) e `helical_stairs` (Escada Helicoidal).
- O formulário de consolo agora envia `fd_kN` para o solver correto, e as dimensões `a_dist`/`d_eff` ficam em metros, como o backend espera.
- O formulário de dente Gerber passou a expor `a_dist`, `d_eff` e `b`, e a rota aceita `b` como largura.
- Viga parede deixou de usar o vão `L` como carga; agora usa `fd_kN_m` ou `q` para carga distribuída e `L` apenas para vão.
- `tests/test_mestre_routing.py` agora valida também o memorial: cada tipo conhecido precisa retornar `metadata.element_type` igual ao tipo calculado e não pode cair no fallback de warning.

## Atualização: Vigas Com Balanços

- A rota `beam` deixou de usar o wrapper simplificado de viga biapoiada e agora chama `beam_solver.run_beam_analysis` diretamente com `supports`, `distributed_loads` e `point_loads` enviados pelo frontend.
- O playground de vigas ganhou presets de vínculo: `Biapoiada`, `Engastada livre`, `Balanço esquerdo`, `Balanço direito` e `Balanço duplo`.
- O balanço é representado por apoios internos ao comprimento total da viga. Exemplo: `L=6m`, apoio em `x=1,2m` e apoio em `x=6,0m` gera balanço à esquerda de `1,2m`.
- A suíte `tests/test_mestre_routing.py` tem teste específico garantindo que apoios personalizados de balanço chegam ao solver e não são substituídos por apoios padrão em `0` e `L`.

## Atualização: Retorno Do Módulo Viga Cross

- O módulo `Viga Cross` da versão anterior foi portado de `mef_dashboard/src/modules/vigacross` para `mef_frontend/src/lib/vigacross`.
- A sidebar do Mestre voltou a exibir `Viga Cross` em Superestrutura, com tipo interno `beam_cross`.
- Foi criado `mef_frontend/src/app/(app)/mestre/components/BeamCrossPlayground.tsx` com cálculo local pelo método de Hardy Cross, edição de vãos, apoios, cargas distribuídas e cargas pontuais.
- O módulo gera passos de memorial no painel direito, incluindo propriedades da seção, momentos de engastamento perfeito, convergência, equilíbrio e envoltória didática.
- Este módulo é pedagógico/clássico (`mef_check=False`) e não chama a API do backend; para dimensionamento MEF executivo usar `Viga Isolada`.

## Inventário: Recursos Da Versão Anterior Ainda Não Migrados

Base comparada: `mef_dashboard/src/hooks/useProjectState.ts`, `mef_dashboard/src/app/page.tsx`, `mef_dashboard/src/components/*` e `mef_frontend/src/app/(app)/mestre`.

### Migrados Ou Equivalentes No Novo Mestre

- `DIMENSIONAR VIGA` -> `Viga Isolada`, com MEF, apoios customizados, cargas distribuídas, cargas pontuais e balanços.
- `VIGA CROSS` -> `Viga Cross`, portado para `beam_cross`.
- `DIMENSIONAR PILAR` -> `Pilar (Flexo)`.
- `Escadas de Lance` -> `Escada`.
- `Escada Helicoidal` -> `Escada Helicoidal`.
- `Sapatas Isoladas` -> `Sapata Isolada`.
- `Reservatório / Tanques` -> `Reservatório`.
- `Consolos Curtos` -> `Consolo Curto`.
- `Dentes Gerber` -> `Dente Gerber`.
- `Vigas Parede` -> `Viga Parede`.
- `Parede de Concreto` -> `Parede de Concreto`.
- `Muro de Arrimo` -> `Muro Arrimo`.

### Esquecidos Com Backend Já Existente

- `Sondagem SPT`: existia em `SpecialElementsView` e há rota backend `/api/mestre/calculate/spt`; falta tela no `mef_frontend`.
- `Estabilidade γz`: existia em `SpecialElementsView` e há rota backend `/api/mestre/calculate/stability-mestre`; falta tela no `mef_frontend`.
- `Lajes/Radier avançado`: existia via `GuidedGeometryView`, `SupportLocationSection`, `PillarEditor`, `HoleEditor`, `SoilPressureMap`, `ReinforcementView`, `ReportView`; há backend em `routes/core.py`, `routes/elite.py`, `radier_lab_v24.py`, `laje_lab_v2.py`; no Mestre novo existe apenas laje/radier simplificado.
- `Vento / NBR 6123`: existia em `WindStabilityView` e há rotas `routes/wind.py`; não há tela no `mef_frontend`.
- `Pórticos`: existia em `AcademicPorticoView` e há backend de frame/mestre frame; não há módulo no `mef_frontend`.
- `Treliças`: existia em `AcademicTrussView`; não há módulo no `mef_frontend`.
- `Tension Pro / Protensão`: existia em `TensionProView` e chama `/rust/tension-pro/friction-loss`; não há módulo no `mef_frontend`.
- `Biblioteca técnica`: existia em `LibraryView`; não há equivalente no `mef_frontend`.
- `Backlog acadêmico`: existia em `AcademicBacklogView`; não há equivalente no `mef_frontend`.

### Recursos Parciais Ou Substituídos

- `MemorialHtmlView`: substituído por `MemorialHeader` + export HTML, mas ainda não tem modal HTML igual ao anterior.
- `PedagogicalStepsView`: substituído por `MemorialAccordion`.
- `Structural3DView`/`Frame3DView`: substituídos parcialmente por `Beam3DView`; o novo 3D cobre elementos isolados, mas não pórticos/radier completo.
- `AICopilotAlerts`, `OptimizationEngine`, `BimExporter`, `StructuralAuditAgent`: não foram migrados para o Mestre novo.

### Próxima Prioridade Recomendada

1. Migrar `SPT` e `Estabilidade γz`, porque as rotas já existem e são pequenas.
2. Migrar `Tension Pro`, se a rota Rust estiver ativa no backend atual.
3. Criar módulos separados para `Pórticos` e `Treliças`.
4. Reabrir o módulo `Lajes/Radier avançado` como seção própria, sem misturar com a laje simplificada do Mestre.

## Atualização: Separação Da Sidebar Por Famílias

- `MestreSidebar.tsx` foi reorganizada em quatro famílias:
  - `Elementos NBR 6118`
  - `Fundações`
  - `Sistemas`
  - `Módulos Especiais`
- Os módulos existentes foram redistribuídos sem alterar seus tipos internos.
- Os recursos ainda não migrados foram adicionados como placeholders desabilitados com selo `breve`: `Sondagem SPT`, `Radier Avançado`, `Pórticos`, `Treliças`, `Estabilidade γz`, `Vento / NBR 6123`, `Tension Pro` e `Biblioteca Técnica`.
- Os placeholders não chamam `setSelectedElementType`, portanto não quebram o roteamento atual.
- Validação executada:

```bash
cd mef_frontend
npm run lint
npm run build
```

Ambos passaram.

## Atualização: Diagramas Do Módulo Viga Cross

- `BeamCrossPlayground.tsx` agora renderiza três diagramas após o cálculo Hardy Cross:
  - Diagrama de Esforço Cortante (`V`, kN)
  - Diagrama de Momentos Fletores (`M`, kNm)
  - Linha Elástica / Flecha (`f`, mm)
- Os diagramas usam os pontos já produzidos por `mef_frontend/src/lib/vigacross/engine.ts` em `results.diagrams`.
- Cada gráfico mostra linha zero, área sombreada, nós, vãos e valores mínimo/máximo.
- O memorial do Viga Cross também passou a mencionar `Vmax`, `Mmax` e `fmax` na etapa de envoltória didática.
- Validação executada:

```bash
cd mef_frontend
npm run lint
npm run build
```

Ambos passaram.

## Correção: NaN Nos Diagramas Do Viga Cross

- Corrigido aviso React: `Received NaN for the children attribute`.
- Causa principal: o SVG usava `{-fmt(maxAbs, 1)}`; como `fmt()` retorna string com vírgula decimal, o operador unário `-` gerava `NaN`.
- `BeamCrossPlayground.tsx` agora usa `fmt(-maxAbs, 1)` e possui helper `asFiniteNumber()` para blindar escala, coordenadas, labels e métricas contra `NaN`.
- Também foi adicionada validação antes do cálculo para impedir vãos com comprimento menor ou igual a zero.
- Validação executada:

```bash
cd mef_frontend
npm run lint
npm run build
```

Ambos passaram.

1. `mef_frontend/` aparece como diretório não rastreado no git principal. Antes de commit/push, confirmar se deve ser adicionado integralmente.

2. `mef_engine/routes/special.py` ainda concentra muita lógica. Próximo passo recomendado: criar um dispatcher de cálculo Mestre, por exemplo:

```text
mef_engine/mestre_dispatcher.py
```

com uma tabela tipo:

```python
MESTRE_SOLVERS = {
    "beam": BeamMestreSolver,
    "slab": SlabMestreSolver,
    ...
}
```

3. O MEF de laje no Mestre está funcional, mas é uma placa apoiada no contorno com malha simples. Não confundir com o Atlas Pro de radier/lajes complexas.

4. Os modelos 3D dos especiais são representações didáticas simples, não geometria BIM/execução.

5. `calculation_trace` já é exibido no `MemorialHeader` após o cálculo, mostrando solver, clássico e MEF. Se não aparecer, a chamada provavelmente não retornou ou o backend não está rodando.

6. Foi criada uma suíte automatizada dedicada ao roteamento Mestre:

```text
tests/test_mestre_routing.py
```

Ela valida:

- `beam` nunca chama laje
- `slab` nunca chama viga
- `pile_cap` chama `pile_cap_solver`
- todo tipo conhecido retorna `calculation_trace`

Comando:

```bash
python3 -m pytest tests/test_mestre_routing.py -q
```

Resultado atual: `4 passed`.

## Arquivos Mais Importantes Para Retomar

Frontend:

- `mef_frontend/src/app/(app)/mestre/page.tsx`
- `mef_frontend/src/app/(app)/mestre/components/Beam3DView.tsx`
- `mef_frontend/src/app/(app)/mestre/components/SpecialPlayground.tsx`
- `mef_frontend/src/app/(app)/mestre/components/SlabPlayground.tsx`
- `mef_frontend/src/app/(app)/mestre/components/PileCapPlayground.tsx`
- `mef_frontend/src/lib/mestre-types.ts`
- `mef_frontend/src/lib/store-mestre.ts`
- `mef_frontend/src/lib/api-mestre.ts`

Backend:

- `mef_engine/routes/special.py`
- `mef_engine/reporting/pedagogy/base.py`
- `mef_engine/reporting/pedagogy/slab.py`
- `mef_engine/reporting/pedagogy/foundation.py`
- `mef_engine/reporting/pedagogy/special.py`
- `mef_engine/lajes_solver.py`
- `mef_engine/beam_solver.py`
- `mef_engine/footing_solver.py`
- `mef_engine/pile_cap_solver.py`
