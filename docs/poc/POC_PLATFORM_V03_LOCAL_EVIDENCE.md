# POC Platform v0.3 — Local verification report

**Date:** 2026-11-13. **Risk R3.** This is a development-lab checkpoint, **not production approval**.

## Implemented
- `IsolatedPOCOrchestrator` in `src/mt_iam/poc/platform.py` with dependency gates, `max_workers=1..4`, `timeout_seconds=0.1..300`, fail-fast cancellation, deterministic result ordering, sequential-mode preservation.
- `isolated.py` launches only the trusted hard-coded CHECKS allowlist; config cannot supply shell commands or import paths. Worker environments are allowlisted to omit cloud/database credentials.
- Timeout and cancellation attempt termination of an owned process group on POSIX, and `taskkill /T /F` on Windows; parent reaps the child. Real Windows behavior is **NOT RUN**.
- `isolated_worker.py` has strict ID validation and JSON result protocol; unknown and external handlers fail closed.
- Config section `[poc.orchestrator]` now supports `execution_mode="isolated"`, `max_parallel=2`, `timeout_seconds=15`.
- The CLI reads validated TOML and selects the isolated orchestrator. JSON evidence still reports `full_poc_verification=NOT_CERTIFIED`.

## Observed commands and results

Environment: isolated Linux Python 3.13.5 in the ChatGPT runtime. Exact source at the v0.3 snapshot committed to GitHub (review attached commit).

```sh
PYTHONPATH=src python -m pytest -q
# 90 passed, exit 0
PYTHONPATH=src python -m compileall -q src tests
# exit 0
PYTHONPATH=src python -m mt_iam.poc.platform_cli --config configs/platform.toml --report /mnt/data/poc-v03-full.json
# exit 0; 30 LOCAL_CHECK_PASS, 22 BLOCKED, 1 disabled extension SKIPPED, 0 FAIL
```

Observed tests include a subprocess handler smoke, owned process termination/reaping, worker limit checks, dependency failure propagation, config bounds, and a 52-ID real subprocess run. 53rd ID is a disabled extension example.

## Remaining evidence gates

- **NOT RUN:** GitHub Actions result, Windows/Python 3.12 CI, dependency lock and supply chain review.
- **NOT RUN:** repeated long soak, deterministic forced descendant process-tree failure on Windows, end-to-end cancellation under simultaneous load; memory/FD monitoring and OS-level CPU/RAM resource quotas.
- **NOT RUN/BLOCKED:** actual Supabase PostgreSQL, Google Cloud Run, OIDC conformance, issuer/key continuity, backup/restore, billing.
- **Security limitation:** isolation is process isolation with bounded worker admission, **not** an OS-level security sandbox. Trusted handlers can access local filesystem/network subject to OS user permissions. Future v0.4 must add explicit OS resource ceilings and policy enforcement before calling it a hardened platform.
- **Do not close Issue #69 yet.** Independent reviewer and full R3 gates not passed.

## Decision
Keep v0.3 as a **local development baseline**. Only mark component-level verified local tests PASS; 52 full POC acceptance remains unverified. Issue/Project board owns live work status, evidence file owns test fact.
