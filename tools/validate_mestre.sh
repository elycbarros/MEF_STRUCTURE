#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Backend solver audit =="
cd "$ROOT/mef_engine"
.venv/bin/python tests/test_solver_audit.py

echo "== Exam auditor regression =="
.venv/bin/python test_exam_auditor.py

echo "== Mestre response contract =="
.venv/bin/python test_mestre_response_contract.py

echo "== Frontend production build =="
cd "$ROOT/mef_frontend"
npm run build
