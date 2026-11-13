# MT-IAM POC Acceptance Gate — Milestone evidence, 2026-11-13

**Risk R3. Status: Local gate unit tests PASS; independent security review, remote provider integration, Windows CI: NOT RUN.**

## Purpose
Prevent the 30 local diagnostics from being misreported as fully proven identity/SSO POCs. The gated schema is separate from `LOCAL_CHECK_PASS` and does not mutate GitHub Project status automatically.

## Implemented
- Module `src/mt_iam/poc/quality_gate.py`: `check_evidence(document, registry)` and CLI.
- Reject unknown IDs, unrecognized schemas/status, missing source SHA/environment/command, inadequate test cases, missing evidence digests, missing independent reviewer/decision, resource cleanup, and missing external proof for external POCs.
- The `artifacts` hashes and reviewer fields are checked for **presence/shape**, NOT cryptographic verification against fetched files nor real reviewer authentication. Cannot alone certify a POC or authorize release.
- Explicitly forbid assuming `LOCAL_CHECK_PASS` equals independent full `PASS` by requiring additional scoped evidence.

## Observed local commands
- `PYTHONPATH=src python -m pytest -q tests/test_quality_gate.py` → **8 passed**.
- `PYTHONPATH=src python -m pytest -q` → **103 passed**, exit 0, in isolated Python 3.13.5 Linux execution environment.
- `python -m ruff check ...` → **NOT RUN** (Ruff not installed in local runner).
- **NOT RUN** Windows, Cloud Run, OIDC, Supabase, PostgreSQL live, process-tree soak, independently authenticated evidence review.

## CLI usage
```powershell
python -m mt_iam.poc.quality_gate artifacts/evidence/POC-G10-01.json
```
Exit 0: structurally sufficient PASS evidence; exit 2: BLOCKED or malformed. Do not close POC issue on an exit-0 alone without verifying artifacts and reviewer authority.

## Next
Introduce cryptographically checked artifact hashes, reviewers/permissions, CI on Windows/Linux, dependency lock; continue POC Platform #69 as IN PROGRESS. Production readiness remains BLOCKED. GitHub Issues/Projects is the work-status SSOT; this file is historical evidence, not a competing Kanban status table.
