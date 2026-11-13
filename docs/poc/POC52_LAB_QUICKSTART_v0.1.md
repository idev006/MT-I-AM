# MT-IAM POC52 Python Lab v0.1

**This is a POC harness, NOT a production IAM or an OIDC provider.**

Maintains **52 unique POC IDs** from the master plan. Local deterministic checks are distinct from real-provider verification. On this baseline, 30 local checks have actual executable assertions; 22 cases report `BLOCKED` with a specific external requirement. No complete POC has been certified PASS.

## Quickstart (Windows PC / Linux)

Requires Python 3.12 or 3.13. The entire source tree is safe to test with synthetic data.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,database]"
python -m pytest -q
python -m mt_iam.poc.runner --output poc52-local-results.json
python -m mt_iam.poc.runner --require-all-pass  # exits 1 while any POC blocked
```

Alternative without installing package if dependencies already exist: `PYTHONPATH=src python -m pytest -q` on Linux. Test result ≠ Cloud/production conformance.

## Opt-in live checks (only after authorized setup)

```powershell
# Set environment variables securely, never commit URLs containing secrets:
python -m mt_iam.poc.live_probes oidc
python -m mt_iam.poc.live_probes cloudrun
python -m mt_iam.poc.live_probes postgresql
```

`MT_IAM_OIDC_ISSUER` and `MT_IAM_CLOUD_RUN_URL` must be HTTPS URLs. `MT_IAM_DATABASE_URL` must use PostgreSQL/psycopg. All external probes are **read-only** and return `LIVE_PARTIAL` only, not full POC PASS. No provider connection is attempted during local pytest.

## Directory layout

```text
src/mt_iam/{api,core,adapters,poc}/
  poc/registry.py       52 canonical identifiers
  poc/domain.py         synthetic state, scope and concurrency models
  poc/checks.py         30 deterministic checks + 22 explicit blockers
  poc/runner.py         CLI and JSON evidence output
  poc/live_probes.py    opt-in HTTPS discovery/health and PostgreSQL SELECT 1

tests/{test_database,test_poc_foundation,test_poc52,test_live_probes}.py
.github/workflows/poc-tests.yml   workflow submitted; CI execution unverified
```

Each POC official evidence and status remains in the existing GitHub Master POC Plan, evidence files, and linked Issues. **One SSOT for work status = GitHub Issues/Project board when activated.** Cloud bill, real-key custody, OAuth conformance, provider restore, and live identity security are outside this mock environment.
