# MT-IAM POC Platform — Local v0.4 Verification Evidence

**Date:** 2026-11-13 (Asia/Bangkok). **Scope:** local Python/Linux sandbox, source staged then synchronized to GitHub. **This is NOT a production IAM or 52-POC certification.**

## Executed tests
- Command: `cd /mnt/data/MT-IAM-POC-Platform/work/project && PYTHONPATH=src python -m pytest -q tests` — observed **95 passed, exit 0**.
- Command: `PYTHONPATH=src python -m compileall -q src tests` — observed exit 0.
- Command: `PYTHONPATH=src python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/local-v04.json` — executed, JSON generated.
- Runner snapshot: **53 total registry items**, 30 `LOCAL_CHECK_PASS`, 22 `BLOCKED`, 1 `SKIPPED` optional synthetic extension; 0 `FAIL`, 0 `TIMEOUT`, 0 `CANCELLED` in full registry *normal run*. **Verification classification: NOT_CERTIFIED.**
- Targeted synthetic tests additionally triggered **TIMEOUT**, **CANCELLED**, and oversized output, and verified expected fail-closed statuses.
- Interpreter observed: Python 3.13.5. Windows Python 3.12 and GitHub Actions CI results: **NOT RUN / not verified** in this environment.
- Ruff CLI availability: **NOT RUN** (Ruff not installed in this local runner), so no lint pass claim.

## Changed paths
- `src/mt_iam/poc/isolated.py`: trusted handler allowlist; bounded temporary-file output to avoid unbounded pipe RAM; timeout/cancel shutdown and reaping; allowlisted environment prevents DB/cloud credentials inheritance. Not a full OS sandbox.
- `src/mt_iam/poc/platform.py`: JSON summary now distinguishes `TIMEOUT` and `CANCELLED`.
- `tests/test_isolated_orchestrator.py`: five new cases including live child timeout/cancel, excessive output, secret environment and report counts.
- `scripts/test-local.ps1` / `scripts/test-local.sh`: reproducible local test commands.
- `docs/poc/POC_PLATFORM_LOCAL_TEST_HANDOFF_v0.4.md`: Windows handoff and risk boundaries.
- Existing matrix CI workflow is versioned in `.github/workflows/poc-tests.yml`, but no new run confirmed.

## Residual risk / next gates
- **BLOCKED:** Supabase PostgreSQL, OpenID Connect authorization server and conformance, Cloud Run, production credential handling, OS-level CPU/RAM ceilings, external portability/recovery tests.
- **NOT RUN:** Windows PowerShell execution, all CI matrix outcomes, Ruff on this runner, resource soak/leak benchmark and independent R3 reviewer sign-off.
- Windows process-tree kill uses `taskkill /T /F`; must be validated with real grandchildren/cancellation on Windows. Unix uses owned process groups.
- Python package version ranges currently not locked for reproducible builds.
- A local-check PASS means only the small reviewed handler logic ran; it never represents a complete POC security verdict. No production release is approved.

## Acceptance / Kanban
The canonical progress work item remains [Issue #69](https://github.com/idev006/MT-I-AM/issues/69) **OPEN — In Progress**, awaiting the above gates and reviewer. The existing GitHub Project/Issues are status SSOT; this document is the technical evidence SSOT for this local checkpoint.
