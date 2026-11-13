#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3.12}"
if [[ ! -d .venv ]]; then "$PYTHON" -m venv .venv; fi
.venv/bin/python -m pip install -e '.[test,database]'
.venv/bin/python -m pytest -v tests
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/local.json
echo 'Local gates completed; external-provider BLOCKED results are not certification.'
