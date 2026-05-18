# Contrato de Resposta do Modo Mestre

Este documento registra o envelope esperado entre backend, frontend e store do Modo Mestre.

## Envelope

Toda rota usada pelos playgrounds deve convergir para:

```json
{
  "success": true,
  "result": {},
  "summary": {},
  "full_results": {},
  "pedagogical_steps": { "steps": [] },
  "calculation_trace": {
    "requested_type": "beam",
    "solver_module": "NomeDoSolver",
    "blackboard_builder": "build_x_blackboard",
    "classical_check": true,
    "mef_check": true
  }
}
```

## Campos

- `success`: indica se a rota concluiu sem erro.
- `result`: resultado principal consumido pelo módulo.
- `summary`: resumo executivo opcional para cards e KPIs.
- `full_results`: payload completo quando o backend precisa preservar dados brutos.
- `pedagogical_steps`: memorial didático. Pode vir como `{ steps: [...] }`; o frontend usa `extractMestreSteps`.
- `calculation_trace`: rastreabilidade do solver, builder do memorial e tipo de validação executada.

## Frontend

O store expõe `applyMestreResponse(response)`, que centraliza:

- passos pedagógicos;
- trace de cálculo;
- resultado completo.

Playgrounds que chamam API devem preferir `applyMestreResponse` em vez de chamar separadamente:

- `setPedagogicalSteps`;
- `setCalculationTrace`;
- `setFullResults`.

## Estado Por Módulo

O store mantém snapshots por módulo. Ao trocar de módulo, o estado atual é salvo e o estado do destino é restaurado quando existir. Quando não existir, o store aplica presets mínimos do módulo para evitar contaminação entre viga, pilar, treliça, auditoria etc.

## Validação

Antes de commit/push em mudanças do Mestre, rode:

```bash
tools/validate_mestre.sh
```

O script executa:

- auditoria matemática dos solvers;
- regressões do `exam_auditor`, incluindo PDF;
- regressão do contrato de resposta do Mestre para vigas, pilares, lajes, sapatas, estacas, blocos, pórticos, treliças, SPT, estabilidade, vento, protensão, radier avançado e auditoria;
- build de produção do frontend.

## Regressão de Contrato

O arquivo `mef_engine/test_mestre_response_contract.py` chama os handlers do backend diretamente com fixtures mínimas e exige que todos retornem:

- `success: true`;
- `result` preenchido;
- `summary` preenchido;
- `full_results` preenchido;
- `pedagogical_steps` como lista ou `{ steps: [...] }`;
- `calculation_trace` com `requested_type`, `solver_module`, `blackboard_builder`, `classical_check` e `mef_check`.

Novos módulos do Mestre devem entrar nessa matriz antes de serem considerados estáveis para a interface.
