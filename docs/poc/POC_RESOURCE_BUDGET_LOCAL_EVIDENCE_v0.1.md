# MT-IAM POC Resource Budget — Local milestone evidence v0.1

**Date:** 2026-11-13. **Risk class:** R3. **Scope:** trusted local synthetic POC workers; **not** a security sandbox, production IAM acceptance, or certified cloud run.

## Implementation
- [resource_budget.py](../../src/mt_iam/poc/resource_budget.py) validates `memory_mb=128..4096`, `cpu_seconds=1..300` (reject bool and wrong types).
- POSIX child installs `RLIMIT_AS` and `RLIMIT_CPU` **inside the worker before trusted POC handler**, avoiding unsafe `preexec_fn` in multithreaded Python. Parent still enforces elapsed timeout/termination separately.
- [platform.toml](../../configs/platform.toml) adds `[poc.resources]` (defaults: memory 768 MiB, CPU 30 seconds per worker); [settings.py](../../src/mt_iam/poc/settings.py) validates these values and rejects unknown/unsafe keys.
- CLI → scheduler → isolated worker propagates nonsecret validated budget values. Worker rejects external/unknown handlers as before.
- [windows_job.py](../../src/mt_iam/poc/windows_job.py) now also requests Windows Job Object **job-wide committed memory limit** and **per-process user CPU time limit** from the validated budget, in addition to KILL_ON_JOB_CLOSE. Windows enforcement has **not been executed or verified on real Windows**; the Windows-only regression tests in [test_resource_budget.py](../../tests/test_resource_budget.py) must pass in CI before acceptance.

## Executed evidence (isolated Linux Python 3.13.5)
- `PYTHONPATH=src python -m pytest -q tests/test_resource_budget.py tests/test_windows_job.py` → **12 passed / 3 skipped** in the Linux sandbox (Windows-only tests skipped), exit 0.\n- `PYTHONPATH=src python -m mt_iam.poc.platform_cli --config configs/platform.toml --id POC-G01-03` → **1 LOCAL_CHECK_PASS**, exit 0; not a full POC PASS.\n- `PYTHONPATH=src python scripts/poc_soak.py --repeats 5` → **5/5 LOCAL_CHECK_PASS**, mean 1304.06 ms in this run; short repeat smoke only, not proof of leak freedom.
- `PYTHONPATH=src python -m pytest -q tests/test_isolated_orchestrator.py tests/test_poc_platform.py` → **31 passed**, exit 0.
- `PYTHONPATH=src python -m compileall -q src tests` → exit 0.
- Full suite attempt printed progress to 100% with one Windows-only SKIP, but execution wrapper timed out before reporting completion; **full-suite clean exit NOT VERIFIED** at this revision.
- Windows CI, independent security reviewer, Ruff, actual Windows budget enforcement, and real OIDC/Supabase/Cloud Run evidence remain **NOT VERIFIED**.

## Known constraints and acceptance implications
- `RLIMIT_AS` bounds virtual memory, not process-group aggregate RSS nor cgroup memory; forked children and host-specific behavior require further review.
- `RLIMIT_CPU` measures CPU time, distinct from parent wall timeout.
- TOML budget values and wrapper tests prove local configuration/wiring only. Cross-platform resource acceptance must remain OPEN.
- Strict 52-POC certification remains unverified. Thirty local synthetic diagnostics must not become 30 full POC PASS.

## Next gates
1. Verify new Windows job-level memory/CPU constraints on real Windows 10/11 or GitHub Actions Windows matrix; check nested job restrictions and committed-memory behavior.
2. Repeat full suite with captured exit code and CI artifact; inspect long-running test teardown.
3. Add bounded load/soak tests, process leak metrics and resource cleanup evidence with reviewed thresholds.
4. Real provider POC gates, evidence provenance and independent R3 review.

**Tracking:** [GitHub Issue #69](https://github.com/idev006/MT-I-AM/issues/69) remains OPEN / IN PROGRESS. Project Board status, where available, remains workflow SSOT.
