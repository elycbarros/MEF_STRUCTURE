# Histórico de Atualizações - MEF Structural

## [1.0.0] - 2026-05-04
### Adicionado
- **Fase 5: Inteligência Pura & Interoperabilidade** concluída.
- **M5-PhD Optimization Engine**: Motor de design gerativo para otimização de seções e materiais.
- **BIM Interoperability**: Exportação nativa de arquivos IFC 2x3 para integração com Revit/TQS/Tekla.
- **Física Avançada (TensionPro)**: Simulação de fluência, retração e perdas diferidas conforme NBR 6118.
- **Elite Cohesion Design System**: Unificação visual completa entre os motores MESTRE e UFO.
- **Navegação Horizontal**: Migração da Sidebar vertical para uma Tab-bar horizontal superior, liberando 100% da largura da tela para o conteúdo técnico.
- **Memorial HTML Premium**: Substituição da geração de PDF no backend por um relatório HTML de alta fidelidade com função nativa de impressão/salvamento.
- **Layout de Diagramas**: Otimização da visualização dos gráficos DMF/DEC/Flecha para disposição vertical com altura expandida (350px).
- **Structural Audit Agent**: Presença nativa de IA Ph.D. em todos os módulos para auditoria forense.

### Corrigido
- Erro de referência (`ReferenceError: Activity is not defined`) no hook `useProjectState`.
- Erros de aninhagem HTML no componente `VigaCrossView`.
- Redundância de imports em componentes de visualização.

### Alterado
- Refatoração profunda da `page.tsx` para extrair lógica de negócio para `lib/formatters.ts`.
- Migração de todos os módulos para o contêiner unificado `ModuleContainer`.
- Atualização da WelcomeScreen para experiência premium de primeiro acesso.

## [2.0.0] - 2026-05-07
### Adicionado
- **UFO Universal Engine**: Expansão do motor 3D para suporte a sobrados, casas, galpões comerciais e edificações não usuais.
- **Geotecnia Avançada (SSI)**: Implementação de curvas p-y (Reese/Matlock) para interação solo-estrutura não-linear em estacas.
- **Detalhamento Global Automático**: Orquestrador de consumo de aço para todo o edifício, integrando esforços 3D com resumos executivos.
- **Análise Sísmica (RSA)**: Implementação de Resposta Espectral (NBR 15421) com superposição SRSS.
- **Auditoria de Conforto**: Verificação automática de aceleração de pico (NBR 6123) para conforto de usuários.
- **Modo Mestre vs Modo UFO**: Diferenciação arquitetônica formal entre ensino pedagógico e auditoria profissional global.

### Alterado
- **WelcomeScreen V2.0**: Rebrand total com foco na separação MESTRE/UFO e novos escopos de edificação.
- **Dashboard Profissional**: Inclusão de KPIs de consumo de aço e status sísmico auditado.
- **UfoStabilityView**: Integração de análise modal (períodos e frequências) e auditoria de vibrações.

---
*Regra de Versionamento VibeDoCode: V[MAJOR].[MINOR].[PATCH]*
