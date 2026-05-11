# Instrucoes Para Antigravity - Proxima Rodada

Atualizado em: 2026-05-11

## Objetivo

Este arquivo orienta a continuidade do trabalho no Atlas Mestre independentemente do modelo de IA usado. O foco da proxima rodada deve ser validar runtime dos modulos novos e corrigir conexoes frontend/backend que ainda podem falhar mesmo com build aprovado.

## Contexto Do Projeto

Raiz do projeto:

```text
/Users/elycbarros/DEV2/MEF STRUCTURAL
```

Frontend:

```text
mef_frontend/
```

Backend:

```text
mef_engine/
```

Documentos relacionados:

```text
docs/MESTRE_FRONTEND_CONTINUIDADE.md
docs/MESTRE_FRONTEND_MELHORIAS_ANTIGRAVITY.md
```

## Estado Validado Nesta Rodada

Comandos executados com sucesso:

```bash
cd mef_frontend && npm run lint
cd mef_frontend && npm run build
python3 -m pytest tests/test_mestre_routing.py -q
python3 -m pytest mef_engine/tests/test_structural_suite.py tests/test_mestre_routing.py -q
```

Resultado atual:

- Frontend compila.
- Lint do frontend passa.
- Teste de roteamento Mestre passa com 5 testes.
- Suite estrutural backend passa com 31 testes.
- Validacao combinada passa com 36 testes.
- O erro de React `Received NaN for the children attribute` no `CrossDiagram`/visualizacao 3D foi mitigado com normalizacao de dados no `Beam3DView`.

## Alteracoes Feitas Na Ultima Rodada

Arquivos ajustados:

```text
mef_frontend/src/lib/mestre-types.ts
mef_frontend/src/lib/api-mestre.ts
mef_frontend/src/lib/store-mestre.ts
mef_frontend/src/app/(app)/mestre/components/Beam3DView.tsx
mef_frontend/src/app/(app)/mestre/components/AdvancedSlabPlayground.tsx
mef_frontend/src/app/(app)/mestre/components/EngineeringSettings.tsx
mef_frontend/src/app/(app)/mestre/components/FramePlayground.tsx
mef_frontend/src/app/(app)/mestre/components/TensionProPlayground.tsx
mef_frontend/src/app/(app)/mestre/components/TrussPlayground.tsx
```

Resumo:

- `MestreElementType` foi alinhado aos modulos exibidos na sidebar:
  - `wind`
  - `advanced_slab`
  - `tension_pro`
  - `tech_library`
- `Beam3DView` recebeu guardas contra nos/membros incompletos e barras de comprimento zero.
- `AdvancedSlabPlayground`, `TensionProPlayground`, `FramePlayground` e `TrussPlayground` tiveram estados locais tipados e parametros numericos normalizados.
- `EngineeringSettings` teve tipos fechados para unidades e casos de carga.
- `analyzeMestreFrame` passou a aceitar cargas genericas de sistema, pois pórticos/trelicas enviam cargas nodais e nao `PointLoad` de viga.
- Duplicidade de `unitConfig` foi removida de `store-mestre.ts`.
- Endpoint de vento no frontend foi corrigido de `/api/ufo/calculate/wind` para `/api/ufo/wind`, alinhando com `mef_engine/routes/wind.py`.

## Pontos De Atencao Importantes

### 1. Nao Confundir Build Verde Com Runtime Verde

O build passa, mas alguns modulos ainda precisam ser testados com backend rodando.

Prioridade de validacao manual/API:

```text
Vento
Radier Avancado
Tension Pro
Porticos
Trelicas
SPT
Estabilidade gamma-z
```

### 2. Endpoint De Vento Corrigido, Falta Validacao Visual

No frontend:

```text
mef_frontend/src/lib/api-mestre.ts
```

Funcao:

```ts
calculateWind()
```

Estado atual:

```text
/api/ufo/wind
```

Essa rota esta alinhada com:

```text
mef_engine/routes/wind.py
```

Acao recomendada:

1. Rodar backend e frontend.
2. Abrir `Vento / NBR 6123`.
3. Executar um caso simples.
4. Confirmar memorial, perfil de vento e ausencia de erro no console.

### 3. Radier Avancado E Tension Pro Existem No Backend Especial

Foram encontrados handlers em:

```text
mef_engine/routes/special.py
```

Tipos:

```text
advanced_slab
tension_pro
```

E solvers em:

```text
mef_engine/special_elements.py
```

Acao recomendada:

1. Rodar o backend.
2. Abrir `Radier Avancado` e executar um caso simples.
3. Abrir `Tension Pro` e executar um caso simples.
4. Verificar se o memorial aparece e se `calculation_trace` esta coerente.
5. Se o resultado vier sem `pedagogical_steps`, ajustar builder/memorial.

### 4. Porticos E Trelicas Usam A Mesma Rota De Frame Mestre

Frontend:

```text
FramePlayground.tsx
TrussPlayground.tsx
api-mestre.ts -> analyzeMestreFrame()
```

Backend:

```text
mef_engine/routes/mestre_frame.py
```

Acao recomendada:

1. Testar pórtico simples 1 vao x 1 pavimento.
2. Testar trelica Warren com 6 paineis.
3. Conferir se o diagrama 2D/3D mostra o sistema real e nao fallback.
4. Conferir se o memorial usa builder de sistema adequado.

### 5. Worktree Esta Sujo

Ha muitas alteracoes no repositorio, inclusive em arquivos do backend que nao foram alterados nesta rodada. Nao reverter nada automaticamente.

Antes de qualquer refatoracao grande, rode:

```bash
git status --short
```

E trate apenas arquivos relacionados a tarefa em andamento.

## Checklist Recomendado Para A Proxima Rodada

1. Subir backend.

Comando provavel, a confirmar conforme ambiente:

```bash
cd mef_engine
python3 api.py
```

2. Subir frontend.

```bash
cd mef_frontend
npm run dev
```

3. Validar os modulos, nesta ordem:

```text
Vento
Radier Avancado
Tension Pro
Porticos
Trelicas
SPT
Estabilidade gamma-z
```

4. Corrigir endpoint de vento se falhar.

5. Confirmar que nenhum solver dispara automaticamente ao entrar no modulo. O usuario deve clicar no botao de calcular.

6. Confirmar que cada modulo preenche:

```text
pedagogical_steps
calculation_trace
fullResults
```

7. Rodar validacoes finais:

```bash
cd mef_frontend && npm run lint
cd mef_frontend && npm run build
python3 -m pytest tests/test_mestre_routing.py -q
```

## Criterios De Aceite

Uma etapa pode ser considerada concluida quando:

- o modulo abre sem erro no console;
- nao calcula automaticamente ao trocar de modulo;
- calcula apos clique explicito;
- retorna memorial didatico;
- mostra `calculation_trace` coerente com o solver;
- nao puxa visualizacao errada no `Beam3DView`;
- `npm run lint`, `npm run build` e `tests/test_mestre_routing.py` passam.

## Proximo Item Mais Urgente

Validar visualmente os modulos no navegador com backend rodando.

Prioridade:

```text
Vento / NBR 6123
Radier Avancado
Tension Pro
Porticos
Trelicas
```

Motivo:

- lint, build e testes automatizados estao verdes;
- a proxima classe de risco e runtime/UX: console, preenchimento de memorial, diagramas e estado global;
- o endpoint de vento ja foi corrigido, mas ainda precisa de verificacao manual com servidor ativo.
