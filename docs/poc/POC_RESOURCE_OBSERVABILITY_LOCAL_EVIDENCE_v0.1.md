# MT-IAM POC Resource Observability — Local Evidence v0.1

**Date:** 2026-11-14 (Asia/Bangkok). **Scope:** Linux Python 3.13.5, synthetic/trusted POC subprocesses. **Risk:** R3. **Not a security-certified identity provider or evidence of production readiness.**

## Delivered
- [resource_telemetry.py](../../src/mt_iam/poc/resource_telemetry.py): bounded read-only process-tree sampling using `psutil` (parent + currently visible descendants) with sample count, sampling errors, peak sampled tree RSS, peak process count, and last observed count.
- [repeatability_supervisor.py](../../src/mt_iam/poc/repeatability_supervisor.py): telemetry sampled no more often than approximately 4 times per second, included in JSON evidence for successful, failed, interrupted, and hard-timeout outcomes.
- [test_resource_telemetry.py](../../tests/test_resource_telemetry.py): positive live worker memory observation, hard timeout evidence, and incomplete/failed report persistence.
- [pyproject.toml](../../pyproject.toml) adds `psutil>=5.9,<8` as a runtime dependency for Windows/Linux.
- The telemetry report intentionally includes `complete_census=false`: asynchronous sampling can miss brief peaks or detached children; it is NOT a guarantee of no memory leak, CPU limit enforcement, or process-tree containment.

## Executed local checks
- `PYTHONPATH=src python -m pytest -q tests/test_resource_telemetry.py tests/test_repeatability_supervisor.py` → **8 passed**, exit 0. Re-run after adjusting Windows-sensitive startup timing: **8 passed**, exit 0.
- `PYTHONPATH=src python -m pytest -q -m "not full_registry" tests` → **exit 0**, three Windows-only tests skipped.
- `python -m compileall -q src tests` → **exit 0**.
- `PYTHONPATH=src python -m mt_iam.poc.repeatability_supervisor --repeats 2 --workers 4 --round-timeout 50 --hard-timeout 120 --report /mnt/data/mt-iam-telemetry-52x2.json`: Supervisor printed **exit=0**. Verified JSON: `stage=COMPLETE`, `completed_repeats=2`, `repeatability_pass=true`; both rounds **30 LOCAL_CHECK_PASS + 22 BLOCKED**; durations **16653.38 ms** and **15981.76 ms**.
- Sampled process-tree maximum: **667,709,440 bytes (~636.8 MiB)**, **5 processes**, **122 samples**, **0 sample errors**. These are observed values in this sandbox, not universal thresholds.
- **Caveat:** the outer command wrapper timed out after displaying the Supervisor's exit=0 line; JSON was subsequently read and verified independently. Treat supervisor checkpoint as locally complete, but **outer wrapper clean termination/CI repeatability remains unresolved**.

## Acceptance and remaining risks
- `LOCAL_CHECK_PASS` remains only a trusted synthetic local check; **zero out of 52** POCs are independently accepted as full integration/security POCs.
- GitHub Actions Windows/Linux x Python 3.12/3.13 results on final revision: **NOT VERIFIED** (commit status lookup returned no usable status checks).
- Windows Job Object limits and process-tree handling: **NOT VERIFIED** on actual Windows runner.
- Need repeated multi-run RSS/FD/handle growth trends with thresholds, child process retention checks, safe telemetry failure policy, Ruff and dependency lock validation.
- Supabase PostgreSQL, OIDC conformance, Cloud Run and independent R3 reviewer: **BLOCKED/NOT RUN**.

**Tracking:** [GitHub Issue #69](https://github.com/idev006/MT-I-AM/issues/69) remains OPEN / IN PROGRESS; board workflow status is not directly editable with the connected tools.
