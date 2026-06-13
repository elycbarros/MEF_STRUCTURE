# Atlas Structural Engine

**Motor MEF 3D de Alta Performance com Aceleração Rust**

Bem-vindo à documentação técnica do **Atlas Structural Engine**, o núcleo de inteligência
estrutural da plataforma MEF STRUCTURAL.

## Capacidades Principais

| Módulo | Descrição | Status |
|---|---|---|
| **Pórtico 3D (C1)** | Elementos de barra 12-DOF Euler-Bernoulli | ✅ Produção |
| **Estabilidade Global (C2)** | Gama-Z e Alfa (NBR 6118:2014) | ✅ Produção |
| **Não-Linearidade Geométrica** | P-Delta iterativo com aceleração de Aitken | ✅ Produção |
| **Motor Híbrido Rust** | Montagem de matrizes em paralelo (Rayon) | ✅ Produção |
| **Auditoria de Equilíbrio (C3)** | Verificação de resíduos numéricos | ✅ Produção |
| **Análise Sísmica** | Espectro NBR 15421, análise modal | ✅ Produção |
| **Vento (NBR 6123)** | Perfis S1/S2/S3, coeficientes Cp/Ce | ✅ Produção |
| **Radier (Mindlin-Winkler)** | Solver híbrido Python + Rust | ✅ Produção |
| **Integração Solo-Estrutura (SSI)** | Molas de Winkler, grupo de estacas | ✅ Produção |
| **Exportação BIM** | CSV, DXF, MsgPack | ✅ Produção |

## Stack Tecnológica

| Componente | Tecnologia | Versão |
|---|---|---|
| Runtime | Python | 3.14 |
| Framework Web | FastAPI + Uvicorn | — |
| Validação | Pydantic v2 | — |
| Álgebra Linear | NumPy + SciPy | — |
| Aceleração Nativa | Rust via PyO3 | 0.21.2 |
| Matrizes (Rust) | faer (sparse LU) | — |
| Paralelismo (Rust) | Rayon | — |
| Build Nativo | maturin | — |
| CI/CD | GitHub Actions | — |
| Deploy | Docker multi-stage | — |
| Documentação | MkDocs + Material | — |

## Início Rápido

```bash
# Desenvolvimento local
pip install -r requirements.txt
python api.py
# Acessar http://localhost:8000/docs

# Com Docker
docker compose build
docker compose up -d
# Acessar http://localhost:8000
```

## Convenções da Documentação

- **Endpoints**: `MÉTODO /path` — exemplos em JSON
- **Prefixos**: `/api/mestre/` (legacy) e `/api/v1/mestre/` (versionado)
- **Erros**: formato padronizado com `code`, `type`, `message`, `detail`, `module`
