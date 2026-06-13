# Deployment

## Docker (Recomendado)

### Build

```bash
# Na raiz do projeto (onde está docker-compose.yml)
docker compose build
```

### Run

```bash
docker compose up -d
# Acessar: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Variáveis de Ambiente

```yaml
environment:
  - MEF_AUTH_ENABLED=0          # Habilitar em produção
  - MEF_API_KEY=change-me       # Chave de API
  - MEF_RATE_LIMIT_ENABLED=1    # Rate limiting on
  - MEF_RATE_LIMIT_DEFAULT=100/minute
```

### Health Check

```yaml
healthcheck:
  test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

### Volumes

```yaml
volumes:
  - ./logs:/app/logs         # Logs persistentes
  - ./output_api:/app/output_api  # PDFs e exportações
```

## Manual

```bash
# 1. Criar ambiente virtual
python3 -m venv .venv && source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Build módulo Rust (opcional)
cd structural_core_rs
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 maturin build --release
pip install target/wheels/*.whl
cd ..

# 4. Executar
python api.py
# Servidor em http://localhost:8000
```

## CI/CD

O projeto usa GitHub Actions com três jobs paralelos:

| Job | O que executa | Gatilho |
|---|---|---|
| `lint` | ruff check + format | PR e push |
| `test-python` | build Rust wheel + pytest + cobertura | PR e push |
| `test-rust` | cargo test + cargo check | PR e push |

## Monitoramento

- **Logs**: Arquivos em `logs/engine.log` com rotação
- **Cache**: `GET /api/cache/stats` para hit rate
- **Health**: `GET /api/health` com status do módulo Rust
- **Rust Benchmarks**: `cargo bench` (relatório HTML em `target/criterion/`)
