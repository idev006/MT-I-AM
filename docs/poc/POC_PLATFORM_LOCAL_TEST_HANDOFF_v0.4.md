# MT-IAM POC Platform — Windows Local Test Handoff v0.4

**Purpose:** Run repeatable local tests using Python 3.12, without claiming OIDC/Supabase/Cloud Run verification.

## Instructions
1. Install Python 3.12 x64 with Windows Python Launcher and Git.
2. Clone `https://github.com/idev006/MT-I-AM.git` into a new directory.
3. Open PowerShell in the project root and run `powershell -ExecutionPolicy Bypass -File scripts/test-local.ps1`.
4. Check `artifacts/poc-results/local.json`. The results `LOCAL_CHECK_PASS` and `BLOCKED` are **not** full POC acceptance.

### Manual commands
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,database]"
.\.venv\Scripts\python.exe -m pytest -v tests
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/local.json
```

## Safety and boundaries
- Worker commands are fixed in Python; TOML must never contain arbitrary import paths or shell commands.
- Owned worker output is redirected to temporary files and checked against a 64 KiB limit; deadlines/cancellation call process-tree termination and wait for exit. This does **not** constitute CPU/RAM sandboxing.
- Child worker environment is allowlisted so database URLs/cloud secrets are not propagated.
- POC Platform config defaults to 2 workers and 15-second worker deadlines. On 8 GB developer PCs use 1–2 workers until measured.
- No real personnel data, operational credentials or cloud expense is necessary for the local suite.
- If a test fails, share a **redacted** pytest log and `git rev-parse HEAD` in the existing GitHub Issue. Never paste live secrets into an Issue.

## Evidence and remaining gates
Local evidence from 2026-11-13: 95 pytest tests passed on Linux/Python 3.13.5 in the ChatGPT container. The complete registry runner still has 30 `LOCAL_CHECK_PASS`, 22 external `BLOCKED` plus one synthetic disabled registry extension. Windows and Python 3.12 CI execution are **NOT VERIFIED** by this run.

Supabase/PostgreSQL integration, OIDC conformance, Cloud Run, independent security review, actual resource quotas, supply-chain lock and external network tests remain **BLOCKED or NOT RUN**. Do not close Phase 1 or claim production-ready identity services solely on the basis of local checks.

**SSOT:** GitHub Issues are the workflow/Kanban source; POC evidence and verified results have separate versioned records.
