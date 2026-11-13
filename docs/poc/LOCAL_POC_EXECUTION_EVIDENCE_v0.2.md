# Local POC Lab v0.2 — Executed Evidence and Handoff

**Evidence date:** 2026-11-13; **Scope:** local isolated container Python laboratory, NOT the user's Windows PC or Supabase.
**Risk:** R3 platform prerequisites. This is supporting evidence, NOT a PASS of full POC-G01-01, POC-G02-01, POC-G02-04 or POC-G10-01.
**Code:** src/mt_iam, tests, and pyproject.toml synchronized to repository after testing. GitHub contents API individual commits; final test-file commit fcc825315dcbad3a70ece1c886e7f5bca315fb4a.

## Observed execution
- Runtime Linux, Python 3.13.5, pytest 9.0.2, FastAPI 0.128.2, SQLAlchemy 2.0.50; optional psycopg driver not installed.
- Command: `cd /mnt/data/mt-iam-lab && PYTHONPATH=src python -m pytest -v tests`
- Result: **8 passed in 0.89s** (four foundation tests and four local SQLite synthetic DB tests).
- Command: `python -m compileall -q src tests` -> exit 0.
- ASGI TestClient: `GET /health/live` -> HTTP 200 `{"status":"alive"}`; `GET /health/ready` -> HTTP 200 `{"status":"ready"}`.
- Command: `PYTHONPATH=src python -m mt_iam.adapters.probe` without remote DB URL -> `BLOCKED: set MT_IAM_DATABASE_URL from approved secret source`, exit 2. This is an intentional safe-stop, **not** a successful PostgreSQL connection.

## Coverage and limitations
- PASS (local subset only): ASGI health and lifespan, typed Settings production issuer validation, path traversal, scoped scratch cleanup, synthetic SQLite SQLAlchemy connect, transaction commit/rollback, approved driver gate and application-owned engine disposal.
- **NOT RUN:** real Supabase PostgreSQL, psycopg connection, pooler/prepared statement behavior, Alembic migrations, OIDC provider and cross-app SSO, Cloud Run, OCI build, Windows validation, actual Cloud cost, CI pipeline.
- **NOT RUN:** Ruff lint/static security; runner lacked Ruff. Editable package installation/build lock and separate clean venv were also not executed.
- Local SQLite is **not a substitute** for PostgreSQL evidence. No production credentials, staff data, tokens or keys were used.
- Resource tests are scoped behavior only; no claim of long-running memory/FD leak freedom.
- Existing PostgreSQL adapter is a candidate experiment: validate transaction pooling, driver options, TLS, least-privileged role and clock/timeouts against real service before adoption.

## Next actions / owners
1. Run project locally on Windows with Python 3.12 and dependencies `python -m pip install -e ".[test,database]"`.
2. Run pytest and Ruff and record version/exit codes at exact source revision.
3. With approved, secure test connection string (never commit it), run `python -m mt_iam.adapters.probe`; capture sanitized success/failure and database connection type.
4. Record POC-G02-01 and G02-04 only after *actual* Supabase evidence. Continue OIDC server evaluation separately.
5. Commit dependency lock + hashes after resolving on supported Python platforms.

## Reproducibility and review status
**Evidence collection:** local execution observed. **Independent reviewer:** unassigned. **Full POC verification:** NOT RUN. **Production:** BLOCKED.
