# MT-IAM POC Repeatability Checkpoint v0.1 — executed local evidence

**Date:** 2026-11-13. **Status:** local functionality verified; multi-round full-registry reliability remains **NOT VERIFIED**. R3 / not production IAM approval.

## What changed
- [Repeatability CLI](../../src/mt_iam/poc/repeatability.py) now **atomically writes** JSON to the designated report file before each round and after each completed round. A forcibly terminated CLI leaves `stage=IN_PROGRESS`, `active_round` and `completed_repeats` as an incomplete diagnostic rather than a false success or missing report.
- `stage=COMPLETE` and `repeatability_pass=true` only when every requested round has completed and results are complete/consistent. `stage=FAILED` is emitted on drift, duplicate ID, unexpected external PASS, or incomplete result.
- Report `schema_version=2` adds `stage`, `active_round` and `updated_at_utc`. It retains `full_poc_verification=NOT_CERTIFIED`.
- [New tests](../../tests/test_repeatability.py) exercise atomic success, failed-round report and process interruption. No arbitrary code execution is enabled by TOML.

## Executed local evidence (Linux / Python 3.13.5)
- `PYTHONPATH=src python -m pytest -q tests/test_repeatability.py` -> **10 passed**, exit 0.
- `PYTHONPATH=src python -m pytest -q -ra -m "not full_registry" tests` -> exit **0**, three Windows-only tests skipped (not Windows verification).
- `PYTHONPATH=src python -m pytest -q -ra -m full_registry tests` -> **1 passed**, exit **0** (one test checks 52 local worker outcomes).
- `PYTHONPATH=src python -m mt_iam.poc.repeatability --id POC-G01-03 --repeats 2 --report artifacts/repeatability-checkpoint.json` -> **2/2 LOCAL_CHECK_PASS**, `stage=COMPLETE`, mean 1239.83 ms; exit 0.
- **52 IDs x 2 rounds** at four concurrent workers attempted in this turn: command exceeded 120-second execution window and was terminated; no new clean-exit report produced. Do not claim a new successful full multi-round run. A previous local artifact with two completed rounds is historical only and not valid certification of current revision.

## Remaining limitations / next exit gates
- This is a **checkpoint**, not a hard wall-time supervisor. The cooperative thread cancellation event may be delayed by blocked scheduler/cleanup; a CI/job-level OS timeout remains required. Windows Job Object deadline behavior needs real Windows tests.
- No evidence for long soak, stable process/RSS/handle counts, GitHub Actions success on the final SHA, Ruff, independently verified reviewer identity, OIDC/Supabase/Cloud Run integration.
- Real external POCs remain BLOCKED. **Zero of 52 full POCs** meet independent security acceptance.
- Next: hard outer supervisor that terminates complete process trees on deadline, verified on Windows/Linux; per-round performance/process telemetry, cross-platform CI, then integration tests.

**Tracking:** [GitHub Issue #69](https://github.com/idev006/MT-I-AM/issues/69) remains OPEN/IN PROGRESS. GitHub Project Board workflow is the only status SSOT.
