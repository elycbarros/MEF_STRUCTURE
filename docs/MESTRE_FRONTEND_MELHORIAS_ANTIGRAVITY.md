# Plano De Melhorias Do Frontend Mestre

Este documento foi escrito para continuidade independente por qualquer agente ou modelo de IA. Ele resume o estado atual do frontend Mestre, os problemas encontrados e a ordem recomendada de melhoria.

## Contexto Atual

Projeto principal:

```text
/Users/elycbarros/DEV2/MEF STRUCTURAL
```

Frontend novo:

```text
mef_frontend/
```

Backend:

```text
mef_engine/
```

Documento de continuidade operacional:

```text
docs/MESTRE_FRONTEND_CONTINUIDADE.md
```

O frontend novo do Mestre já possui módulos para elementos isolados e especiais:

- Viga Isolada
- Viga Cross
- Pilar
- Laje/Radier simplificado
- Sapata
- Estaca
- Bloco sobre Estacas
- Escada
- Escada Helicoidal
- Muro de Arrimo
- Parede de Concreto
- Reservatório
- Consolo Curto
- Dente Gerber
- Viga Parede

Também já existe verificação automatizada básica:

```bash
python3 -m pytest tests/test_mestre_routing.py -q
cd mef_frontend && npm run lint
cd mef_frontend && npm run build
```

## Problema Principal

O frontend Mestre foi reconstruído em etapas. Algumas funcionalidades da versão anterior (`mef_dashboard`) foram migradas, outras ficaram ausentes ou parcialmente substituídas.

O objetivo agora não é apenas adicionar telas, mas organizar o sistema para que:

- cada módulo tenha cálculo próprio;
- cada módulo tenha memorial próprio;
- o usuário saiba se está usando cálculo clássico, MEF ou módulo didático;
- recursos antigos sejam recuperados sem misturar responsabilidades;
- novos módulos não transformem `page.tsx` e `MestreSidebar.tsx` em cadeias difíceis de manter.

## Melhorias Recomendadas

## Status E Ordem Atual De Execução

### Feito

1. Separação visual da sidebar por famílias.

Executado em:

```text
mef_frontend/src/app/(app)/mestre/components/MestreSidebar.tsx
```

Estado atual:

- A sidebar foi separada em `Elementos NBR 6118`, `Fundações`, `Sistemas` e `Módulos Especiais`.
- Os módulos existentes foram redistribuídos sem alterar seus tipos internos.
- Módulos ainda não migrados aparecem como placeholders desabilitados com selo `breve`.
- Esta etapa atende a sugestão 1 como organização visual inicial.

2. Viga Cross recuperada.

Executado em:

```text
mef_frontend/src/lib/vigacross/
mef_frontend/src/app/(app)/mestre/components/BeamCrossPlayground.tsx
```

Estado atual:

- `Viga Cross` voltou à sidebar.
- O motor Hardy Cross antigo foi portado.
- O módulo gera memorial local e `calculation_trace` local.
- Foram adicionados diagramas de cortante, momento e flecha.

3. Vigas com balanços.

Estado atual:

- A rota `beam` usa `run_beam_analysis` diretamente.
- Apoios e cargas customizadas do frontend chegam ao solver.
- O playground de vigas possui presets de balanço.

### Ordem Atual Do Que Falta Fazer

Esta é a ordem recomendada a partir do estado atual, já considerando que a sugestão 1 foi executada visualmente.

1. Criar registro único de módulos no frontend.

Objetivo:

- retirar a definição manual duplicada entre `MestreSidebar.tsx` e `page.tsx`;
- preparar a entrada segura de SPT, γz, vento, Tension Pro, pórticos, treliças e radier avançado;
- transformar os placeholders `breve` em itens declarados no mesmo registro.

Arquivos prováveis:

```text
mef_frontend/src/lib/mestre-modules.ts
mef_frontend/src/lib/mestre-types.ts
mef_frontend/src/app/(app)/mestre/page.tsx
mef_frontend/src/app/(app)/mestre/components/MestreSidebar.tsx
```

2. Recuperar módulos pequenos com backend pronto: SPT e Estabilidade γz.

Objetivo:

- criar `SptPlayground.tsx`;
- criar `StabilityPlayground.tsx`;
- ativar os itens atualmente desabilitados na sidebar;
- preencher memorial à direita e `calculation_trace`.

Rotas prováveis:

```text
/api/mestre/calculate/spt
/api/mestre/calculate/stability-mestre
```

3. Padronizar diagramas em módulos estruturais.

Objetivo:

- usar o padrão recém-aplicado no `Viga Cross` como referência;
- garantir linha zero, nós/vãos, unidades, valores extremos e área/curva legíveis.

Prioridade:

```text
Viga Isolada
Pilar
Laje/Radier simplificado
Pórticos, quando migrados
Treliças, quando migradas
```

4. Melhorar o módulo Pilar com ideias do P-Calc.

Objetivo:

- adicionar diagrama de interação `N-M`;
- destacar ponto solicitante;
- mostrar se está dentro/fora da envoltória resistente;
- reforçar esbeltez, segunda ordem e momentos mínimos.

5. Recuperar Vento / NBR 6123.

Objetivo:

- criar tela de vento;
- ligar com `routes/wind.py`;
- exibir perfil de pressão/força e, se aplicável, resultado de estabilidade.

6. Criar infraestrutura de casos de carga, combinações e envoltórias.

Objetivo:

- aproximar a experiência de ferramentas como FTool;
- permitir ELU, ELS e envelopes sem duplicar lógica em cada módulo.

7. Criar biblioteca de apoios avançados.

Objetivo:

- apoio inclinado;
- mola vertical/horizontal/rotacional;
- recalque imposto;
- rotação imposta.

8. Recuperar Tension Pro / Protensão.

Objetivo:

- confirmar rota Rust ativa;
- criar `TensionProPlayground.tsx`;
- ligar memorial e `calculation_trace`.

9. Recuperar Pórticos e Treliças.

Objetivo:

- criar módulos em `Sistemas`;
- usar visual 2D/3D próprio;
- evitar misturar com Viga Isolada.

10. Reabrir Radier/Lajes avançado.

Objetivo:

- criar módulo próprio;
- não misturar com `SlabPlayground` atual;
- recuperar editor visual, pilares, furos, apoios, mapa de solo, detalhamento e relatório.

### 1. Separar O Mestre Em Categorias Claras

Hoje a sidebar mistura fundações, superestrutura, módulos didáticos e especiais. Com o retorno de SPT, estabilidade, pórticos, treliças, Tension Pro e radier avançado, a navegação ficará confusa.

Sugestão de categorias:

```text
Elementos NBR 6118
- Viga Isolada
- Pilar
- Laje
- Escada
- Escada Helicoidal
- Consolo Curto
- Dente Gerber
- Viga Parede
- Parede de Concreto

Fundações E Geotecnia
- Sapata Isolada
- Estaca
- Bloco sobre Estacas
- Muro de Arrimo
- Sondagem SPT
- Radier Avançado

Sistemas Estruturais
- Pórticos
- Treliças
- Estabilidade γz
- Vento / NBR 6123

Módulos Especiais
- Viga Cross
- Tension Pro / Protensão
- Biblioteca Técnica
- Backlog Acadêmico
```

Critério de aceite:

- A sidebar deve continuar compactável.
- Os módulos existentes não devem desaparecer.
- O usuário deve entender visualmente a diferença entre elemento isolado, fundação, sistema estrutural e módulo didático.

Status atual:

- Executado visualmente em `MestreSidebar.tsx`.
- A sidebar foi separada em `Elementos NBR 6118`, `Fundações`, `Sistemas` e `Módulos Especiais`.
- Módulos ainda não migrados foram adicionados como placeholders desabilitados com selo `breve`.
- Ainda falta consolidar a configuração em um registro único de módulos, que é a próxima etapa recomendada.

### 2. Criar Um Registro Único De Módulos No Frontend

Atualmente `mef_frontend/src/app/(app)/mestre/page.tsx` escolhe o componente com uma cadeia de condicionais:

```tsx
selectedElementType === 'pile' ? ...
```

Isso deve ser substituído por um registro central, por exemplo:

```text
mef_frontend/src/lib/mestre-modules.ts
```

Exemplo conceitual:

```ts
export const MESTRE_MODULES = {
  beam: {
    label: 'Viga Isolada',
    category: 'Elementos NBR 6118',
    component: BeamPlayground,
    solverKind: 'backend',
    classical: true,
    mef: true,
  },
  beam_cross: {
    label: 'Viga Cross',
    category: 'Módulos Especiais',
    component: BeamCrossPlayground,
    solverKind: 'local',
    classical: true,
    mef: false,
  },
};
```

Critério de aceite:

- `MestreSidebar.tsx` deve montar a navegação a partir desse registro.
- `page.tsx` deve renderizar o componente a partir desse registro.
- Adicionar um novo módulo deve exigir alteração em um lugar principal, não em vários arquivos.

Arquivos prováveis:

- `mef_frontend/src/lib/mestre-types.ts`
- `mef_frontend/src/lib/mestre-modules.ts`
- `mef_frontend/src/app/(app)/mestre/page.tsx`
- `mef_frontend/src/app/(app)/mestre/components/MestreSidebar.tsx`

### 3. Recuperar Primeiro Os Módulos Com Backend Pronto

Prioridade recomendada:

1. Sondagem SPT
2. Estabilidade γz
3. Vento / NBR 6123
4. Tension Pro / Protensão
5. Pórticos
6. Treliças
7. Radier/Lajes avançado

Justificativa:

- SPT e γz já existiam no `SpecialElementsView` antigo e possuem rotas Mestre no backend.
- Vento possui rota específica em `mef_engine/routes/wind.py`.
- Tension Pro existia no frontend antigo, mas deve confirmar se a rota Rust ainda está ativa antes de migrar.
- Pórticos, treliças e radier avançado têm maior escopo e precisam de telas próprias.

Rotas/backend relevantes:

```text
mef_engine/routes/special.py
- /api/mestre/calculate/spt
- /api/mestre/calculate/stability-mestre

mef_engine/routes/wind.py
- /api/ufo/wind
- /api/ufo/wind-stability

mef_engine/routes/core.py
- /api/radier/calculate ou rota equivalente incluída em api.py

mef_engine/routes/elite.py
- /calculate_v2_unified
- /calculate/frame-legacy
```

Critério de aceite:

- Cada módulo recuperado deve aparecer na sidebar.
- Cada módulo deve ter formulário mínimo funcional.
- Cada módulo deve preencher memorial à direita.
- Quando usar backend, deve exibir `calculation_trace`.
- Quando for local, deve criar `calculation_trace` equivalente.

### 4. Padronizar `calculation_trace` Para Todos Os Módulos

Atualmente o backend já retorna `calculation_trace` para módulos Mestre. O módulo local `Viga Cross` também cria um trace local.

Todos os módulos devem expor:

```ts
{
  requested_type: string;
  solver_module: string;
  blackboard_builder: string;
  classical_check: boolean;
  mef_check: boolean;
}
```

Campos adicionais recomendados:

```ts
{
  warnings?: string[];
  assumptions?: string[];
  input_summary?: Record<string, unknown>;
}
```

Critério de aceite:

- `MemorialHeader` deve mostrar claramente solver, clássico e MEF.
- Módulos locais e backend devem ter padrão visual igual.
- Testes devem falhar se um tipo usar solver ou memorial errado.

Arquivos prováveis:

- `mef_frontend/src/lib/mestre-types.ts`
- `mef_frontend/src/app/(app)/mestre/components/MemorialHeader.tsx`
- `tests/test_mestre_routing.py`

### 5. Melhorar Entrada De Dados Antes Do Cálculo

Depois da remoção do cálculo automático, o usuário precisa clicar para calcular. Isso é correto. Agora faltam recursos para reduzir erro de entrada.

Adicionar nos módulos principais:

- botão `Restaurar padrão`;
- botão `Exemplo didático`;
- validação visual antes de chamar solver;
- aviso de unidades;
- resumo do modelo antes de calcular;
- mensagens claras quando faltam apoios, cargas ou dimensões.

Prioridade para aplicar:

1. Viga Isolada
2. Estaca
3. Bloco sobre Estacas
4. Sapata
5. Laje/Radier
6. Viga Cross

Critério de aceite:

- O usuário não deve conseguir chamar solver com geometria obviamente inválida.
- A tela deve indicar qual unidade cada campo espera.
- Erros técnicos devem ser traduzidos para uma orientação de engenharia quando possível.

### 6. Recuperar Recursos Auxiliares Com Cuidado

Recursos antigos ainda não migrados:

- `AICopilotAlerts`
- `OptimizationEngine`
- `BimExporter`
- `StructuralAuditAgent`
- `MemorialHtmlView`
- `LibraryView`
- `AcademicBacklogView`

Sugestão:

- Não migrar tudo de uma vez.
- Primeiro estabilizar módulos de cálculo.
- Depois adicionar recursos auxiliares como camadas opcionais.

Critério de aceite:

- Nenhum recurso auxiliar deve bloquear cálculo.
- Se um serviço externo ou rota estiver indisponível, a tela deve continuar funcionando.

## Referências Externas Para Upgrade

Esta seção registra soluções observadas em ferramentas externas e como elas podem orientar o upgrade do Mestre. Não copiar interface, marca, código ou material proprietário. Usar apenas como referência funcional e de experiência de uso.

### Referência: FTool

Fonte:

```text
https://portal.ftool.com.br/
https://portal.ftool.com.br/recursos/
https://portal.ftool.com.br/atualizacoes/
```

Recursos observados:

- modelagem gráfica intuitiva;
- análise estática linear;
- diagramas de esforços;
- reações de apoio;
- deslocamentos;
- deformada da estrutura;
- valores indicados nos diagramas;
- linhas de influência;
- cargas móveis e trem-tipo;
- envoltórias de carga móvel;
- múltiplos casos de carga;
- combinações ponderadas;
- envoltórias de casos e combinações;
- apoios inclinados;
- molas em apoios;
- deslocamentos e rotações prescritos;
- seções genéricas prismáticas;
- tabelas de perfis metálicos;
- configuração de unidades e formato numérico;
- exportação DXF;
- relatórios.

#### Aplicações Recomendadas No Mestre

1. Padronizar diagramas em todos os módulos estruturais:

```text
Viga Isolada:
- normal, cortante, momento, torção quando aplicável, flecha/deformada

Viga Cross:
- cortante, momento, flecha/deformada

Pórticos:
- normal, cortante, momento, deslocamentos, deformada

Treliças:
- esforço axial, deslocamentos, deformada
```

2. Criar infraestrutura de casos de carga:

```text
Caso PP
Caso Permanente
Caso Sobrecarga
Caso Vento
Caso Acidental
Combinação ELU
Combinação ELS
Envelope
```

3. Criar biblioteca de apoios e vínculos:

```text
Livre
Apoio simples
Engaste
Mola vertical
Mola horizontal
Mola rotacional
Apoio inclinado
Recalque imposto
Rotação imposta
```

4. Criar módulo futuro de linhas de influência:

```text
beam_influence
```

Uso:

- vigas contínuas;
- pontes;
- trem-tipo;
- carga móvel;
- máximos e mínimos de V/M/N.

5. Criar biblioteca de seções:

```text
Retangular
T
I
U
L
Circular
Tubular
Genérica por pontos/polígono
Perfis comerciais
```

6. Criar configuração global de unidades:

```text
Comprimento: mm, cm, m
Força: kN, tf
Momento: kNm, tfm
Tensão: kPa, MPa
Formato numérico: casas decimais, vírgula/ponto
```

7. Evoluir exportações:

```text
HTML
PDF
DXF
JSON do modelo
CSV de resultados por barra/nó
```

Critério de aceite para upgrades inspirados no FTool:

- O usuário deve conseguir interpretar o comportamento estrutural sem depender apenas do memorial textual.
- Diagramas devem ter escala, linha zero, valores extremos, identificação de nós/vãos e unidades.
- O modelo visual deve refletir as mesmas cargas e apoios enviados ao solver.

### Referência: TQS P-Calc

Fonte:

```text
https://www.tqs.com.br/apps/p-calc/ejm1se496l
```

Recursos observados:

- análise de pilares de concreto armado;
- flexão composta normal;
- flexão composta oblíqua;
- verificação de ELU de ruptura;
- verificação de instabilidade;
- concretos de alta resistência, `fck > 50 MPa`;
- diagrama de interação `N x M`;
- resultados gráficos de deformações e tensões na seção;
- efeitos locais de segunda ordem;
- não linearidade física e geométrica;
- métodos da ABNT NBR 6118;
- envoltória de momentos mínimos;
- memória de cálculo em PDF.

#### Aplicações Recomendadas No Módulo Pilar

1. Adicionar diagrama de interação `N-M`:

```text
N x Mx
N x My
ponto solicitante Nd/Mxd/Myd
status dentro/fora da envoltória resistente
```

2. Tratar flexão composta oblíqua como modo explícito:

```text
Compressão centrada
Flexão composta normal em X
Flexão composta normal em Y
Flexão composta oblíqua
```

3. Criar visualização da seção:

```text
seção b x h
barras longitudinais
estribos
linha neutra
região comprimida
região tracionada
```

4. Criar mapas/diagramas de deformação e tensão:

```text
deformação no concreto
deformação nas barras
tensão no concreto
tensão no aço
domínio de deformação
```

5. Reforçar efeitos locais de segunda ordem:

```text
lambda
lambda_1
classificação de esbeltez
momento mínimo
momento de primeira ordem
momento de segunda ordem
método normativo adotado
```

6. Implementar envoltória de momentos mínimos:

```text
e_min
M1d_min_x
M1d_min_y
comparação com Mxd/Myd informados
envoltória mínima no gráfico
```

7. Garantir tratamento de `fck > 50 MPa`:

```text
parâmetros do diagrama tensão-deformação
módulo de elasticidade
limites de ductilidade
coeficientes normativos aplicáveis
alertas no memorial
```

8. Melhorar memorial do pilar:

Sequência recomendada:

```text
1. Dados da seção e materiais
2. Esforços solicitantes
3. Excentricidades mínimas
4. Esbeltez e classificação
5. Segunda ordem local
6. Diagrama de interação
7. Armadura adotada
8. Tensões/deformações na seção
9. Verificação final
```

Critério de aceite para upgrades inspirados no P-Calc:

- O módulo Pilar deve mostrar graficamente se o ponto solicitante está dentro da capacidade resistente.
- O memorial deve indicar claramente se governa ruptura, instabilidade, momento mínimo ou segunda ordem.
- Para flexão oblíqua, a interface não deve esconder `Mxd` e `Myd` em campos genéricos; deve deixar claro que a verificação é biaxial.

## Priorização Atualizada Com FTool E P-Calc

### Prioridade Alta

1. Criar registro único de módulos no frontend.
2. Recuperar `SPT` e `Estabilidade γz`.
3. Padronizar diagramas em `Viga Isolada`, `Pilar`, `Laje/Radier simplificado` e futuros `Pórticos`.
4. Melhorar `Pilar` com diagrama `N-M` e ponto solicitante.

### Prioridade Média

5. Recuperar `Vento / NBR 6123`.
6. Criar infraestrutura de casos de carga, combinações e envoltórias.
7. Criar biblioteca de apoios avançados.
8. Melhorar pilar com deformações/tensões na seção e momentos mínimos.

### Prioridade Baixa Ou Projeto Próprio

9. Recuperar `Tension Pro / Protensão`.
10. Recuperar `Pórticos` e `Treliças`.
11. Linhas de influência e trem-tipo.
12. Biblioteca de seções genéricas.
13. Exportação DXF/PDF completa.
14. Radier/Lajes avançado com editor visual completo.

## Checklist De Implementação Recomendada

### Fase 1: Organização Do Frontend

- [feito] Separar visualmente a sidebar por famílias em `MestreSidebar.tsx`.
- [pendente] Criar `mef_frontend/src/lib/mestre-modules.ts`.
- [pendente] Mover configuração da sidebar para esse registro.
- [pendente] Atualizar `MestreSidebar.tsx` para ler do registro.
- [pendente] Atualizar `page.tsx` para renderizar o componente pelo registro.
- Rodar:

```bash
cd mef_frontend && npm run lint
cd mef_frontend && npm run build
```

### Fase 2: Módulos Pequenos Com Backend Pronto

- Criar `SptPlayground.tsx`.
- Criar `StabilityPlayground.tsx`.
- Adicionar tipos `spt` e `stability` ou nomes equivalentes em `MestreElementType`.
- Garantir memorial e `calculation_trace`.
- Adicionar testes de rota se ainda não existirem.

### Fase 3: Vento E Protensão

- Criar `WindPlayground.tsx`.
- Verificar rota real de vento e prefixo em `mef_engine/api.py`.
- Verificar se `/rust/tension-pro/friction-loss` está ativo.
- Se ativo, criar `TensionProPlayground.tsx`.

### Fase 4: Sistemas Estruturais

- Portar ou recriar `AcademicPorticoView`.
- Portar ou recriar `AcademicTrussView`.
- Decidir se esses módulos entram no Mestre ou em uma seção separada de Sistemas.

### Fase 5: Radier/Lajes Avançado

- Não misturar com `SlabPlayground` atual.
- Criar módulo próprio, por exemplo `AdvancedSlabRadierPlayground.tsx`.
- Recuperar conceitos de:

```text
GuidedGeometryView
SupportLocationSection
PillarEditor
HoleEditor
SoilPressureMap
ReinforcementView
ReportView
```

## Comandos De Verificação

Backend:

```bash
python3 -m pytest tests/test_mestre_routing.py -q
```

Frontend:

```bash
cd mef_frontend
npm run lint
npm run build
```

Compilação Python pontual, quando alterar backend:

```bash
python3 -m py_compile mef_engine/routes/special.py mef_engine/master_pedagogy.py
```

## Cuidados Importantes

- Não reativar cálculo automático ao entrar no módulo.
- Não usar imagens estáticas nos memoriais; usar diagramas/SVG/componentes.
- Não fazer um módulo puxar cálculo de outro sem `calculation_trace` explícito.
- Não misturar radier avançado com laje simplificada.
- Não remover mudanças existentes no backend sem revisar, pois há worktree sujo com alterações anteriores.
- Preservar a documentação em `docs/MESTRE_FRONTEND_CONTINUIDADE.md`.

## Próximo Passo Mais Seguro

Executar o restante da Fase 1: criar o registro único de módulos.

A separação visual da sidebar já foi feita. O próximo passo é tirar a configuração duplicada de `MestreSidebar.tsx` e `page.tsx`, colocando tudo em `mef_frontend/src/lib/mestre-modules.ts`. Isso reduz risco antes de recuperar mais telas e evita que a navegação volte a crescer de forma difícil de manter.
