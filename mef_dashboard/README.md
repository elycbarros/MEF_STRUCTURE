# Radier Lab Next (React + TypeScript)

Frontend React/TypeScript para o motor de calculo do `radier_lab` (API FastAPI).

## Execucao local

1. Suba a API Python:

```bash
cd ../radier_lab
python3 api.py
```

2. Suba o frontend:

```bash
cd ../radier_lab_next
npm run dev -- --hostname 127.0.0.1 --port 3001
```

3. Abra:

- `http://127.0.0.1:3001`

## Variaveis de ambiente

Opcionalmente, configure a URL da API:

```bash
NEXT_PUBLIC_RADIER_API_URL=http://127.0.0.1:8000
```

Se nao for definida, o frontend usa `http://127.0.0.1:8000` por padrao.

## Scripts

- `npm run dev`: ambiente de desenvolvimento
- `npm run build`: build de producao
- `npm run start`: serve build de producao

## Estrutura

- `src/app/page.tsx`: dashboard principal
- `src/components`: componentes de UI
- `src/app/globals.css`: tema visual

## Dependencias externas

O projeto nao depende de fontes remotas para funcionar localmente.
