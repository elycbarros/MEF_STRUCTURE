import logging
import time
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Validation'])


class ValidationResponse(BaseModel):
    total_benchmarks: int
    passed: int
    failed: int
    pass_rate_pct: float
    total_time_ms: float
    results: list[dict[str, Any]]
    metadata: dict[str, Any]


@router.get('', response_model=ValidationResponse)
@router.get('/run', response_model=ValidationResponse)
async def run_validation():
    from validation.validation_runner import run_all_benchmarks

    t0 = time.perf_counter()
    res = run_all_benchmarks()
    elapsed = (time.perf_counter() - t0) * 1000

    summary = res['summary']
    summary['total_time_ms'] = round(elapsed, 2)

    return ValidationResponse(
        total_benchmarks=summary['total_benchmarks'],
        passed=summary['passed'],
        failed=summary['failed'],
        pass_rate_pct=summary['pass_rate_pct'],
        total_time_ms=summary['total_time_ms'],
        results=res['results'],
        metadata={
            **_get_metadata(),
            'api_elapsed_ms': round(elapsed, 2),
        },
    )


@router.get('/dashboard')
async def validation_dashboard():
    from validation.validation_runner import run_all_benchmarks

    res = run_all_benchmarks()
    return _build_dashboard_html(res)


@router.get('/dashboard/embed')
async def validation_dashboard_embed():
    from validation.validation_runner import run_all_benchmarks

    res = run_all_benchmarks()
    return _build_embed_html(res)


def _get_metadata() -> dict:
    import sys
    from datetime import datetime

    return {
        'validation_date': datetime.now().isoformat(),
        'python_version': sys.version.split()[0],
        'validation_matrix_version': '6.4.0',
    }


def _build_dashboard_html(res: dict) -> dict:
    s = res['summary']
    return {
        'html': f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Validação — Atlas Structural Engine</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f5f5f5; color:#333; padding:2rem; }}
  h1 {{ font-size:1.6rem; margin-bottom:0.5rem; }}
  .summary {{ display:flex; gap:1rem; flex-wrap:wrap; margin:1rem 0; }}
  .card {{ background:#fff; border-radius:8px; padding:1.2rem 1.5rem; box-shadow:0 1px 3px rgba(0,0,0,.12); min-width:100px; text-align:center; }}
  .card .number {{ font-size:1.8rem; font-weight:700; }}
  .card .label {{ font-size:.8rem; color:#666; }}
  .pass {{ color:#2e7d32; }}
  .fail {{ color:#c62828; }}
  .rate {{ color:#1565c0; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.12); }}
  th, td {{ padding:.6rem .8rem; text-align:left; border-bottom:1px solid #eee; font-size:.85rem; }}
  th {{ background:#1565c0; color:#fff; font-weight:600; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:12px; font-size:.75rem; font-weight:600; }}
  .badge-pass {{ background:#e8f5e9; color:#2e7d32; }}
  .badge-fail {{ background:#ffebee; color:#c62828; }}
  .meta {{ margin-top:1rem; font-size:.8rem; color:#999; }}
</style>
</head>
<body>
<h1>🔬 Validação — Atlas Structural Engine</h1>
<p style="color:#666;margin-bottom:1rem;">Matriz de validação com {s['total_benchmarks']} benchmarks numéricos e analíticos</p>
<div class="summary">
  <div class="card"><div class="number">{s['total_benchmarks']}</div><div class="label">Total</div></div>
  <div class="card"><div class="number pass">{s['passed']}</div><div class="label">Aprovados</div></div>
  <div class="card"><div class="number fail">{s['failed']}</div><div class="label">Falhas</div></div>
  <div class="card"><div class="number rate">{s['pass_rate_pct']}%</div><div class="label">Taxa de Sucesso</div></div>
  <div class="card"><div class="number">{round(s['total_time_ms'])}</div><div class="label">ms (total)</div></div>
</div>
<table>
<thead><tr><th>ID</th><th>Nome</th><th>Status</th><th>Verificações</th><th>Tempo</th></tr></thead>
<tbody>
{''.join(_row(r) for r in res['results'])}
</tbody>
</table>
<div class="meta">Matriz v{res.get('metadata', {}).get('validation_matrix_version', '?')} &middot; {res.get('metadata', {}).get('validation_date', '')[:19].replace('T', ' ')}</div>
</body>
</html>"""
    }


def _build_embed_html(res: dict) -> dict:
    s = res['summary']
    rows = ''.join(
        f'<tr><td>{r["id"]}</td><td>{"🟢" if r.get("overall_pass") else "🔴"}</td></tr>' for r in res['results']
    )
    return {
        'html': f"""<div style="font-family:monospace;font-size:12px;background:#fff;padding:8px;border-radius:4px;">
<div style="display:flex;gap:12px;margin-bottom:8px;">
<span>✅ {s['passed']}/{s['total_benchmarks']}</span>
<span>⏱️ {round(s['total_time_ms'])}ms</span>
</div>
<table style="width:100%;border-collapse:collapse;">
{rows}
</table>
</div>"""
    }


def _row(r: dict) -> str:
    status = '✅' if r.get('overall_pass') else '❌'
    badge = 'badge-pass' if r.get('overall_pass') else 'badge-fail'
    checks = ', '.join(f'{k}={v.get("got", "?")}' for k, v in r.get('checks', {}).items())
    return f"""<tr>
  <td><strong>{r['id']}</strong></td>
  <td>{r.get('name', '')[:55]}</td>
  <td><span class="badge {badge}">{status} {'Pass' if r.get('overall_pass') else 'Fail'}</span></td>
  <td style="font-size:.75rem;color:#666;">{checks}</td>
  <td>{r.get('exec_time_ms', 0)}ms</td>
</tr>"""
