# MT-IAM Hard Timeout Supervisor — Local Evidence v0.1

**Date:** 2026-11-14 (Asia/Bangkok) · **Scope:** Python 3.13 Linux local synthetic POC runner · **Risk:** R3. This is **not** a full POC certification or production identity release.

## Change
- [repeatability_supervisor.py](../../src/mt_iam/poc/repeatability_supervisor.py) launches only the fixed, trusted `mt_iam.poc.repeatability` module. It has a hard parent wall-clock limit and uses dedicated POSIX process groups or a Windows live-tree termination attempt.
- On deadline it forcibly ends the owned process group/tree; checkpoint state becomes `TIMEOUT` with `repeatability_pass=false`, while preserving completed rounds.
- Existing report paths are refused rather than overwritten. Completion requires child exit 0, `stage=COMPLETE`, `repeatability_pass=true`, complete round count and `NOT_CERTIFIED` outcome.
- [test_repeatability_supervisor.py](../../tests/test_repeatability_supervisor.py) covers live 2-round trusted check, forced timeout with a persisted completed round, no-overwrite, exit-0-without-evidence failure, and actual POSIX descendant termination.
- [CI](../../.github/workflows/poc-tests.yml) now asks for the **entire 52-item registry × 2 rounds** behind the supervisor, distinct from the standard fast and single full-registry pytest gates; it uploads `poc-repeatability.json`.

## Executed local evidence
Executed in the extracted previous v1.0 project workspace updated with the new module and tests (Linux Python 3.13 environment):
1. `PYTHONPATH=src python -m pytest -q tests/test_repeatability_supervisor.py` → **5 passed**, exit 0.
2. `PYTHONPATH=src python -m pytest -q -ra -m "not full_registry" tests` → **exit 0**, **3 expected Windows-only skips**.
3. `PYTHONPATH=src python -m mt_iam.poc.repeatability_supervisor --repeats 2 --workers 4 --round-timeout 35 --hard-timeout 85 --report supervisor-multiround.json` → exit **0**. JSON: `stage=COMPLETE`, `completed_repeats=2`, `repeatability_pass=true`. Both rounds: **30 LOCAL_CHECK_PASS / 22 BLOCKED**, mean round duration **15938.51ms** (15.94 sec).
4. Tests and runner were verified with **no remote/cloud credentials**. No real OIDC, Supabase, Cloud Run, end-user data or staff records were used.

The `repeatability_pass` above means that **local diagnostics repeated consistently**, not that any of the 52 business/architecture POCs passed independent acceptance. Certified full POC count remains **0/52**.

## Open risks and acceptance gates
- **Windows hard process-tree supervision** has not been exercised on a Windows runner; `taskkill /T` only applies while the top-level process remains live, and descendants detached by other mechanisms are not reliably contained by this supervisor alone. Windows Job Object inner worker tests and CI remain essential.
- **GitHub Actions** runs at final pushed SHA: NOT VERIFIED. No CI badge or exit status can be inferred from editing YAML alone.
- Parent process may be forcibly killed externally before it can finalize the JSON checkpoint. Existing `IN_PROGRESS` state remains fail-closed and must not be treated as completed.
- Full repeated soak under resource-pressure with RSS/FD/process telemetry, pinned dependency lock, Ruff and independent R3 security review: NOT RUN/BLOCKED.

**Workstream:** [Issue #69](https://github.com/idev006/MT-I-AM/issues/69) OPEN / IN PROGRESS. Next: validate GitHub Actions matrix on Windows/Linux and implement resource observability with bounded soaking and cancellation probes.
