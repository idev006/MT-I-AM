# MT-IAM POC Resource Safety — Worker-descendant cleanup evidence

**Date:** 2026-11-13; Linux / Python 3.13 sandbox. **Scope:** isolated, synthetic worker tests only. **Release gate:** NOT CERTIFIED.

## Defect and fix
A successful Python POC worker could spawn a child process, exit normally, and leave the descendant running because the old `run_isolated` finally cleanup guarded `_terminate_tree` behind `process.poll() is None`. A child may share the worker's POSIX process group even after the worker leader exits.

- `src/mt_iam/poc/isolated.py` now unconditionally calls `_terminate_tree` upon exit.
- On POSIX, `_terminate_tree` signals the worker's dedicated process group even when its leader has exited, and reaps the owned parent process.
- Windows behavior is **not yet equivalent when the leader already exited**; Windows Job Objects / controlled child lifetime must be designed and verified before treating Windows process-tree control as complete.
- This is lifecycle cleanup for trusted handlers, **not a hardened sandbox against malicious processes**.

## Reproduced and checked
- Regression test `test_successful_worker_still_cleans_descendants` starts a synthetic worker that launches a 30-second Python child, returns a valid LOCAL_CHECK_PASS JSON and exits. It asserts the child is no longer running at the end of the parent call; the regression test initially FAILED before the cleanup timing fix and PASSED afterward.
- Local `PYTHONPATH=src python -m pytest -q tests/test_isolated_orchestrator.py` → **17 passed**.
- Local full `PYTHONPATH=src python -m pytest -q` → **117 passed** (prior 116 plus the regression test).
- Local `python -m ruff --version` → **NOT RUN / unavailable**, module ruff not installed.
- Post-push CI on Windows/Linux → **NOT VERIFIED**.
- 52 canonical POC full PASS count remains 0 independently verified; remote/cloud POCs remain blocked.

## Next gate
1. Windows Job Objects or alternative cross-platform reliable child-tree ownership/termination; implement behavioral test.
2. Repeated timeout/cancellation/exit soak, bounded CPU/memory budgets and cleanup leak observation.
3. Review source at merged GitHub SHA, run Windows/Linux CI, and record verified reviewers. Keep [#69](https://github.com/idev006/MT-I-AM/issues/69) OPEN / IN PROGRESS.
