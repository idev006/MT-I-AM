# MT-IAM POC Resource Budget — Local milestone evidence v0.1

**Date:** 2026-11-13. **Risk class:** R3. **Scope:** trusted local synthetic POC workers; **not** a security sandbox, production IAM acceptance, or certified cloud run.

## Implementation
- [resource_budget.py](../../src/mt_iam/poc/resource_budget.py) validates `memory_mb=128..4096`, `cpu_seconds=1..300` (reject bool and wrong types).
- POSIX child installs `RLIMIT_AS` and `RLIMIT_CPU` **inside the worker before trusted POC handler**, avoiding unsafe `preexec_fn` in multithreaded Python. Parent still enforces elapsed timeout/termination separately.
- [platform.toml](../../configs/platform.toml) adds `[poc.resources]` (defaults: memory 768 MiB, CPU 30 seconds per worker); [settings.py](../../src/mt_iam/poc/settings.py) validates these values and rejects unknown/unsafe keys.
- CLI → scheduler → isolated worker propagates nonsecret validated budget values. Worker rejects external/unknown handlers as before.
- Windows Job Object remains a child-lifetime safeguard; **Windows CPU/RAM budget enforcement is NOT implemented** by this milestone. Do not claim `[poc.resources]` limits are enforced on Windows yet. This is an explicit cross-platform blocker.

## Executed evidence (isolated Linux Python 3.13.5)
- `PYTHONPATH=src python -m pytest -q tests/test_resource_budget.py` → **11 passed**, exit 0.
- `PYTHONPATH=src python -m pytest -q tests/test_isolated_orchestrator.py tests/test_poc_platform.py` → **31 passed**, exit 0.
- `PYTHONPATH=src python -m compileall -q src tests` → exit 0.
- Full suite attempt printed progress to 100% with one Windows-only SKIP, but execution wrapper timed out before reporting completion; **full-suite clean exit NOT VERIFIED** at this revision.
- Windows CI, independent security reviewer, Ruff, cross-platform resource limits, and real OIDC/Supabase/Cloud Run evidence remain **NOT VERIFIED**.

## Known constraints and acceptance implications
- `RLIMIT_AS` bounds virtual memory, not process-group aggregate RSS nor cgroup memory; forked children and host-specific behavior require further review.
- `RLIMIT_CPU` measures CPU time, distinct from parent wall timeout.
- TOML budget values and wrapper tests prove local configuration/wiring only. Cross-platform resource acceptance must remain OPEN.
- Strict 52-POC certification remains unverified. Thirty local synthetic diagnostics must not become 30 full POC PASS.

## Next gates
1. Enforce Windows job-level memory/CPU constraints and confirm on real Windows 10/11 or GitHub Actions Windows matrix.
2. Repeat full suite with captured exit code and CI artifact; inspect long-running test teardown.
3. Add bounded load/soak tests, process leak metrics and resource cleanup evidence with reviewed thresholds.
4. Real provider POC gates, evidence provenance and independent R3 review.

**Tracking:** [GitHub Issue #69](https://github.com/idev006/MT-I-AM/issues/69) remains OPEN / IN PROGRESS. Project Board status, where available, remains workflow SSOT.
