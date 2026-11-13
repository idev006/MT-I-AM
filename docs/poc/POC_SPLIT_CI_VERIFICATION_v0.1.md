# MT-IAM POC CI Repeatability — Fast and Full Registry Gates

**Date:** 2026-11-13 (Asia/Bangkok). **Risk class:** R3 local test delivery. **Not production SSO certification.**

## Why this milestone
The 52-item isolated-worker integration test uses real subprocesses and takes materially longer than unit tests. A combined pytest command makes failures hard to distinguish and can exceed short interactive execution windows. **No tests are deleted or skipped silently:** one test is tagged `full_registry`, and both groups are mandatory gates in GitHub CI and the Windows/Linux local scripts.

## Changes
- [`tests/test_isolated_orchestrator.py`](../../tests/test_isolated_orchestrator.py): mark the test that executes all 52 registry items with `@pytest.mark.full_registry`.
- [`pyproject.toml`](../../pyproject.toml): register `full_registry` marker so `--strict-markers` can be adopted later.
- [`poc-tests.yml`](../../.github/workflows/poc-tests.yml): execute two separate hard-failing CI steps: `-m "not full_registry"` and `-m full_registry`. Matrix: Ubuntu/Windows × Python 3.12/3.13. CI outcome on final SHA is not yet confirmed.
- [`test-local.ps1`](../../scripts/test-local.ps1) and [`test-local.sh`](../../scripts/test-local.sh): invoke the same two gates before invoking the POC runner.

## Executed local evidence
Environment: isolated Linux Python 3.13.5; source tree derived from the previously synchronized POC Platform v0.8 local working copy, then patched for split gates. **This is not Windows CI evidence.**

```bash
PYTHONPATH=src python -m pytest -q -ra -m "not full_registry" tests
# EXIT 0; 3 Windows-only tests skipped, all other selected tests passed

PYTHONPATH=src python -m pytest -q -ra -m full_registry tests
# EXIT 0; 1 integration test passed; runs actual 52 worker cases

python -m compileall -q src tests
# EXIT 0
```

The heavy integration test checks 52 results: **30 LOCAL_CHECK_PASS, 22 BLOCKED, zero independently verified full POC PASS**. This is expected and MUST NOT be interpreted as 30 production-ready IAM components.

## Outstanding gates
- **Windows/Linux × Python 3.12/3.13 GitHub Actions logs on final SHA:** NOT VERIFIED.
- **Ruff:** NOT RUN in this local environment (module unavailable).
- **Windows Job Object memory/CPU/process ownership:** NOT VERIFIED on Windows.
- **Reproducible pinned dependency resolution/lock, artifact chain of custody, reviewer authentication:** BLOCKED/NOT RUN.
- **Real Supabase PostgreSQL, OIDC conformance, Cloud Run:** BLOCKED.

## Next action
Inspect GitHub Actions matrix run and fix any failing OS/Python job. Introduce CI test-result artifacts and dependency lock, run bounded stress soak with leak metrics, and move to external integrations only with approved test access. Maintain [#69](https://github.com/idev006/MT-I-AM/issues/69) as OPEN/IN PROGRESS.
