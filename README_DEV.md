# Desenvolvimento do Atlas Structural Engine

Este guia contém instruções para configurar e desenvolver o motor de cálculo Atlas, que utiliza uma arquitetura híbrida Python + Rust para alta performance.

## 🛠️ Compilação e Instalação

O core computacional está em `mef_engine/structural_core_rs`. Para compilar e instalar o módulo nativo:

```bash
make build-rust
```

Isso utiliza o `maturin` para gerar o binário otimizado e instalá-lo no seu ambiente Python atual.

## 🧪 Testes e Validação

Para garantir a integridade científica e performance do motor:

```bash
# Executa todos os testes de paridade e escala
make test

# Executa apenas benchmarks de performance
make bench
```

## ⚠️ Armadilhas Conhecidas (Guia de Sobrevivência)

1.  **Matriz Densa vs Esparsa**: Modelos com mais de 2000 DOFs (ex: edifícios > 10 pavimentos) explodem em memória se usados com solvers densos. O sistema agora chaveia automaticamente para o solver esparso nativo do `faer`.
2.  **Visibilidade de Logs**: Logs gerados no Rust (via `eprintln!`) podem não aparecer no console Python em alguns ambientes. Verifique o `stderr` ou utilize o sistema de logging do `frame_engine.py`.
3.  **Ambiente de Execução (CWD)**: Sempre execute comandos da raiz do projeto. Os scripts utilizam `Path(__file__).resolve()` para localizar arquivos de referência, evitando erros de "File Not Found".

## 🏗️ Próximos Passos Recomendados

- **Modal Analysis**: Implementar extração de autovalores para análise dinâmica (vento/sismo).
- **Fiber Model**: Upgrade do solver de colunas para integração numérica de fatias.
