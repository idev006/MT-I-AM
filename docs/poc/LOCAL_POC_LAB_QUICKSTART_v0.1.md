# MT-IAM Python POC Lab — Local Quickstart v0.1

**Status:** Source-code foundation added on 2026-11-13. **No automated tests have been executed or marked PASS by this GitHub-only creation step.** This is NOT an authentication provider and does not issue tokens.

## Scope and relationship to the 52 POCs
- `POC-G10-01`: pytest foundation, includes four synthetic unit/ASGI tests.
- `POC-G01-01`: local FastAPI and OCI scaffold only; Cloud Run deploy **NOT RUN**.
- `POC-G03-02`: injectable `Settings` example; full domain engine ports/DI **NOT RUN**.
- `POC-G03-05`: minimal typed config and PathManager; engine lifecycle **NOT RUN**.
- **Other POCs:** Master Registry only; not implemented. Do not infer PASS from presence of code.

## Folder structure created
```text
pyproject.toml
Dockerfile
src/mt_iam/
  __init__.py
  api/{__init__.py,app.py}
  core/{__init__.py,config.py,paths.py}
tests/test_poc_foundation.py
docs/poc/{MASTER_POC_PLAN_v1.0.md,POC_EXECUTION_AND_HANDOFF_v1.0.md,POC_SPEC_TEMPLATE_v1.0.md}
```

## Windows PowerShell local setup
Requires Python 3.12 or 3.13. The commands below are instructions for the operator, **not commands already executed on their PC**.

```powershell
git clone https://github.com/idev006/MT-I-AM.git
cd MT-I-AM
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest
python -m ruff check .
python -m uvicorn mt_iam.api.app:app --host 127.0.0.1 --port 8000
```
If the `py -3.12` launcher is absent, use a configured Python 3.12 executable explicitly.

Open `http://127.0.0.1:8000/health/live` and `/health/ready`. API docs available locally at `/docs`. Do not expose this POC publicly as an IAM service.

## Optional local Docker
```powershell
docker build -t mt-iam-poc:local .
docker run --rm --name mt-iam-poc -p 127.0.0.1:8080:8080 mt-iam-poc:local
```
Inspect `http://127.0.0.1:8080/health/live`. On Windows RAM 8 GB, keep container workloads limited.

## Local test evidence to capture
- `git rev-parse HEAD` and Python/pip versions
- `python -m pytest -v` exact output and exit code
- `python -m ruff check .` exact output and exit code
- `curl`/PowerShell `Invoke-RestMethod` on both health routes
- Optional Docker image digest, build log, SIGTERM/stop behavior and memory usage
- Store sanitized observations in `docs/poc/evidence/<POC-ID>/RESULT.md` from the canonical [template](POC_SPEC_TEMPLATE_v1.0.md); obtain reviewer sign-off before any PASS claim.

## Limitations and next actions
- Dependencies are bounded version ranges **not yet frozen into a lockfile**. Pin and lock after local compatibility testing; review dependency vulnerabilities/licenses.
- Container image is minimal and not a hardened production release. No HTTPS, real client/session/token routes, audit trail, operational metrics or database integration.
- No actual Cloud Run deployment, Supabase integration, OIDC conformance, portability or resource benchmark has been conducted.
- Next: execute local tests (G10-01); test OCI startup/shutdown (G01-01/02), then evaluate OIDC provider (G05-01) and PostgreSQL adapter/pooling (G02-01/04). Record results in GitHub Issues #13–#17.

## Authoritative architecture
[Architecture v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md) · [Master POC Plan](MASTER_POC_PLAN_v1.0.md) · [Kanban Governance](../delivery/AGILE_KANBAN_SSOT_GOVERNANCE_v1.0.md).
