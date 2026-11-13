# MT-IAM POC Artifact Integrity — Local milestone evidence

**Date:** 2026-11-13. **Scope:** isolated Python 3.13 Linux sandbox, synthetic evidence. Risk tier R3. **Not independent POC certification or production release.**

## Delivery
- [`artifact_integrity.py`](../../src/mt_iam/poc/artifact_integrity.py) computes actual SHA-256 of local evidence file bytes.
- Rejects missing/malformed SHA-256, traversal/absolute/Windows-drive paths, symlinks, duplicate names, oversized/nonregular evidence and missing root.
- Files limited to 16 MiB each, 32 items per report; streamed hashing avoids loading the whole artifact in memory.
- [`quality_gate.py`](../../src/mt_iam/poc/quality_gate.py) CLI now requires `--artifact-root` when syntactic verification would return PASS. JSON field checks alone can no longer return successful CLI exit code.
- [`test_artifact_integrity.py`](../../tests/test_artifact_integrity.py) covers positive, tampering and invalid/path/size cases.

## Executed tests
Local working copy `/mnt/data/mt_iam_next` derived from existing POC Platform.
- `PYTHONPATH=src python -m pytest -q tests/test_quality_gate.py tests/test_artifact_integrity.py` → **21 tests passed**, exit 0.
- `PYTHONPATH=src python -m pytest -q` → **116 tests passed**, exit 0.
- `python -m compileall -q src tests` → exit 0.
- `python -m ruff check ...` → **NOT RUN**, Ruff unavailable (`No module named ruff`).
- Windows and GitHub CI rerun after GitHub sync → **NOT VERIFIED**.
- No OIDC/Supabase/Cloud Run credentials used; corresponding live POC outcomes remain BLOCKED.

## Caveats
- Validating a digest against a self-supplied expected hash cannot authenticate the origin of the artifact or the reviewer. Git commit provenance, artifact custody, verified reviewer permissions and independent sign-off remain required.
- Concurrent mutation of evidence files and hardlinks are not fully defended. Use isolated, immutable evidence directories and restrictive permissions; do not process hostile user-uploaded roots.
- The reference implementation and tests were synchronized as separate GitHub commits; rerun full suite in CI at the final revision before accepting the gate.

## Local CLI
```powershell
python -m mt_iam.poc.quality_gate artifacts/evidence/POC-G10-01.json --artifact-root artifacts/evidence
```
The manifest must name relative paths inside the approved artifact directory, each with a SHA-256. CLI exit 0 means **structural and file-digest checks passed**, not complete POC acceptance.
