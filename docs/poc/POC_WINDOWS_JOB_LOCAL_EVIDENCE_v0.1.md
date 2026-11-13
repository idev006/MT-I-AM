# MT-IAM POC Windows Job Object lifecycle — v0.1 local evidence

**Date:** 2026-11-13. **Risk:** R3. **Scope:** process lifetime for trusted local POC workers; not production authentication release.

## Implementation
- [windows_job.py](../../src/mt_iam/poc/windows_job.py) attaches a worker itself to a Windows Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` **before any handler executes**. Failure to assign (e.g. restrictive parent job) fails closed.
- [isolated_worker.py](../../src/mt_iam/poc/isolated_worker.py) uses the context and flushes JSON status. The Job Object handle stays owned until worker **process exit**; closing it when the context exits would kill the worker itself and cause a false failure.
- [test_windows_job.py](../../tests/test_windows_job.py) contains a Windows-only child-spawning integration test; Linux runs it as SKIPPED. Lifecycle control is NOT a malicious-code sandbox, network isolation, or CPU/memory guarantee.

## Local evidence
- Linux, Python 3.13 sandbox: `PYTHONPATH=src python -m pytest -q -ra` completed and logged **118 passed, 1 skipped**. A wrapper monitoring call separately timed out *after the pytest progress log had reported completion*, so full reliability should be confirmed by CI.
- `python -m compileall -q src tests`: exit 0.
- Ruff locally: **NOT RUN** (not installed).
- Windows test, Windows CI, provider integration, security review: **NOT VERIFIED / BLOCKED**.

## Exit gate
1. Execute Windows 10/11 or GitHub `windows-latest` full matrix and `test_windows_job_kills_child_when_worker_exits` with actual Windows Job Object.
2. Verify fail-closed behavior if host policy disallows nested jobs; no silent fallback to uncontained execution.
3. Load/timeout/cancel soak, OS-level resource budgets, evidence/reviewer authenticity and final commit SHA review.
4. Only then consider advancing [Issue #69](https://github.com/idev006/MT-I-AM/issues/69). **Not a full POC PASS for any of the canonical 52.**

## Primary references
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
