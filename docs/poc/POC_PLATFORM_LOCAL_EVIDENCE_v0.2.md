# MT-IAM POC Platform v0.2 — Executed Local Evidence
**Date:** 2026-11-13 (Asia/Bangkok). **Environment:** isolated Linux Python 3.13.5 runner in ChatGPT sandbox. **Evidence classification:** local deterministic test only; no provider credential or real staff records.

## Commands and observed results
- `PYTHONPATH=src python -m pytest -q` -> **79 passed**, exit **0**.
- `python -m compileall -q src tests` -> exit **0**.
- `PYTHONPATH=src python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/full-v0.2.json` -> exit **0**, 53 registered cases: **30 LOCAL_CHECK_PASS / 22 BLOCKED / 1 SKIPPED**.
- `PYTHONPATH=src python -m mt_iam.poc.platform_cli --config configs/platform.toml --strict` -> exit **2**, designed fail-closed policy because 22 cases are blocked and one new example POC is disabled.
- `--dry-run --id POC-G05-04` -> verifies dependency expansion and no handler execution; records blocked dependent. Prerequisite outcomes do not become fabricated PASS.

## Coverage
- 52 canonical POC identifiers remain unchanged. 53rd is the synthetic `POC-G99-01`, metadata-only, disabled and excluded from denominator.
- TOML tests cover new-item registration, duplicate rejection, invalid fields, dependency cycles, unknown prerequisites, illegal dynamic handler promotion, setting types, prohibited parallel/remote execution, exception-to-FAIL, disabled items, dry-run, atomic JSON result and topological dependency order.
- Existing checks cover local POC subsets. **No full POC has been certified PASS** merely from this run.
- The local engine is intentionally sequential (safe) and **does not implement process isolation, hard timeout, parallel execution, full cancellation guarantees, or remote providers**. No claim of stability at load or long-running leak freedom.

## Missing verification / release blocks
- Python 3.12 and Windows test evidence: **NOT RUN**.
- GitHub Actions execution of the updated workflow: **NOT VERIFIED**.
- Ruff and type checker, dependency lock/SBOM, security scan: **NOT RUN**.
- Supabase PostgreSQL live connectivity/pooler, OIDC conformance, Cloud Run/portability: **BLOCKED** pending explicit authorized test infrastructure.
- Independent reviewer and full risk R3 acceptance: **BLOCKED**.
- Additional v0.3 subprocess scheduler and stronger execution isolation: **NOT IMPLEMENTED**; tracked by [Issue #69](https://github.com/idev006/MT-I-AM/issues/69).

## Source and SSOT
- [POC Platform Design](POC_PLATFORM_DESIGN_v0.2.md).
- [TOML registry](../../configs/poc_registry.toml), [settings](../../configs/platform.toml).
- [Platform implementation](../../src/mt_iam/poc/platform.py), [tests](../../tests/test_poc_platform.py).
- GitHub Issues is authoritative for live work-state; this file is a dated *test evidence snapshot*, not a substitute for issue review.
