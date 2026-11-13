# MT-IAM POC Repeatability Gate — Local milestone v0.1

**Observed date:** 2026-11-13, isolated Linux Python 3.13.5. **Risk R3; full POC certification remains NOT VERIFIED.**

## Implemented and committed
- [repeatability.py](../../src/mt_iam/poc/repeatability.py): bounded 1..10 runs, <=600s per-round cooperative cancellation deadline, max_workers enforced by existing orchestrator, JSON status/duration per round, stop on drift/timeout/duplicate/missing result, explicit external POC fail-closed.
- [test_repeatability.py](../../tests/test_repeatability.py): 7 tests including real child workers, external BLOCKED, drift, duplicate, forged remote PASS, invalid limits.
- [GitHub Actions workflow](../../.github/workflows/poc-tests.yml): separate fast and full registry pytest gates, plus three-round bounded repeatability smoke with `poc-repeatability.json` artifact.
- This gate proves *local process diagnostics repeatability*, not real OIDC, Supabase, Cloud Run or security certification.

## Executed results in local sandbox
- `PYTHONPATH=src python -m pytest -q tests/test_repeatability.py` → **7 passed**, exit code 0.
- `PYTHONPATH=src python -m pytest -q -ra -m "not full_registry" tests` → **exit 0, 3 Windows-only skips** (all remaining selected tests passed).
- `PYTHONPATH=src python -m pytest -q -ra -m full_registry tests` → **exit 0**, one 52-item isolated registry test, separate run.
- `PYTHONPATH=src python -m mt_iam.poc.repeatability --repeats 3 --id POC-G01-03 --round-timeout 10 --report artifacts/repeatability-3x1.json` → **3/3 LOCAL_CHECK_PASS**, average **1274.50ms/round**, exit 0.
- Full 52-item registry *twice continuously* was attempted; outer interactive tool execution timed out while the second round was in progress. **Do not classify multi-round full-registry evidence as PASS**. Further deadline-specific evidence and CI logs are needed.
- Production/final POC verified count remains **0 / 52** at current independent certification gate.

## Technical limits
- Per-round wall deadline uses a cooperative `Event` consumed by `run_isolated`; a hung scheduler or deadlocked user-supplied handler could delay returning. Shell/CI outer timeouts remain mandatory.
- No file/console output of secrets; JSON is diagnostic only. `repeatability_pass=true` must never be converted to full POC PASS.
- Windows Job Objects and CPU/RAM enforcement still require actual Windows evidence.
- GitHub Actions run at final SHA, Ruff, pinned lockfile and independent reviewer are **NOT VERIFIED**.

## Next milestone
1. Investigate multi-round full-registry end-to-end timings / teardown resource growth under host-budget instrumentation.
2. Run Windows/Linux Python matrix and read JUnit/artifacts before accepting CI.
3. Stress/soak with bounded total duration and process/RSS/handle telemetry on approved local environments.
4. Move to live provider POCs with approved test infrastructure and reviewed secrets after critical process gates.
5. Track all milestones in [Issue #69](https://github.com/idev006/MT-I-AM/issues/69), OPEN / IN PROGRESS.
