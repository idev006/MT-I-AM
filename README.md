> **DELIVERY ROADMAP SSOT (2026-11-13):** [MT-IAM Delivery Roadmap v1.0](docs/delivery/MT_IAM_DELIVERY_ROADMAP_v1.0.md) governs phases, dependency gates and acceptance; [GitHub Issues / existing Kanban](https://github.com/idev006/MT-I-AM/issues) alone governs the *live* ownership and workflow status, and test evidence governs PASS/FAIL. The next critical milestone is POC Platform v0.3 [Issue #69](https://github.com/idev006/MT-I-AM/issues/69). This is not a production-readiness claim.

> **POC52 EXECUTABLE HARNESS (2026-11-13):** [Code](src/mt_iam/poc/) · [52-case Registry](src/mt_iam/poc/registry.py) · [Local Runner](src/mt_iam/poc/runner.py) · [Local pytest results and limitations](docs/poc/POC52_EXECUTION_REPORT_v0.1.md) · [Machine-readable evidence](docs/poc/evidence/POC52_LOCAL_REPORT.json) · [Windows quickstart](docs/poc/POC52_LAB_QUICKSTART_v0.1.md). **65 local tests passed**, **30 local checks PASS, 22 blocked by external verification**. **ZERO 52 POCs certified full PASS**. `--require-all-pass` fails closed. Separate real-provider OIDC, Cloud Run, Supabase, security/conformance and billing evidence is still required.
>
> **KANBAN SSOT:** [GitHub Issues](https://github.com/idev006/MT-I-AM/issues) now has **52 unique OPEN POC Issues**, 12 Epic Issues and [board setup blocker #18](https://github.com/idev006/MT-I-AM/issues/18). Three duplicate Issues #38–#40 were CLOSED as duplicates. **GitHub Projects graphical board has not been created/configured**, so do not claim a live board URL or automatic Project status. All full POC results remain unapproved.

> **AGILE KANBAN / PROGRESS SSOT (2026-11-13):** [Kanban & Single Source of Truth Governance](docs/delivery/AGILE_KANBAN_SSOT_GOVERNANCE_v1.0.md). Live work status belongs to one GitHub Issue/Project view per work item; POC docs are planned registry and evidence artifacts, **not** an independently editable live progress sheet. GitHub Project board setup has NOT been verified/created.

> **POC-FIRST EXECUTION BASELINE (2026-11-13):** Start with [MT-IAM Master POC Plan v1.0](docs/poc/MASTER_POC_PLAN_v1.0.md) (12 domains, 52 experiments; every verification NOT RUN), then [Team Execution & Handoff Playbook](docs/poc/POC_EXECUTION_AND_HANDOFF_v1.0.md) and [POC Spec/Result Template](docs/poc/POC_SPEC_TEMPLATE_v1.0.md). Prioritize OIDC provider evaluation before complex identity implementation. **Production remains BLOCKED** pending protocol, security, resource, privacy and recovery evidence.

> **CANONICAL ARCHITECTURE (2026-11-13): MT-IAM Python-first / cloud-agnostic.** [ADR-007](docs/adr/ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md) supersedes the GAS-primary runtime decision in ADR-006. Initial deployment is Google Cloud Run using standard OCI containers; domain code must run elsewhere. Supabase remains **PostgreSQL database hosting only** (NO Supabase Auth). The OIDC authorization-server implementation is **not yet selected**; protocol, security, load and portability tests are NOT RUN; production release BLOCKED.
>
> **Current SSOT documents:** [Target Architecture v0.5](docs/architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md) · [Actors / Use Cases / APIs / States / Sequences v0.5](docs/architecture/SYSTEM_MODEL_v0.5.md) · [Engineering & Verification Standard v0.5](docs/delivery/ENGINEERING_VERIFICATION_STANDARD_v0.5.md) · [ADR-007](docs/adr/ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md).
>
> **History:** v0.4 GAS-first and POC-03 GAS-assumptions are retained for traceability and superseded by the Python-first target. No deployed Python implementation or passed test evidence is claimed.


## Current architecture v0.4
- [Target Architecture v0.4](docs/architecture/TARGET_ARCHITECTURE_v0.4.md)
- [ADR-006 — Approved Provider Independence and Supabase DB Only](docs/adr/ADR-006_PROVIDER_INDEPENDENT_GAS_POSTGRES_ONLY.md)
- [POC-03 — Provider-Independent SSO](docs/poc/POC-03_PROVIDER_INDEPENDENT_SSO.md)

# MT-IAM — MT Identity & Access Management

Status: v0.4 direction approved; detailed protocol implementation POC pending — 13 November 2026.

MT-IAM is the central Identity and Single Sign-On platform for MT Agency Super App Framework. Independent applications can use any team, language, database, framework or host. They must conform to a published integration and security protocol.

## Responsibilities
- MT-IAM: central identities, minimum personnel directory, account lifecycle, authentication, SSO, application client registry and identity audit logs.
- Each application: admission decisions, internal roles and permissions, business data, business operations and application logs.
- Governance: versioned integration contract, conformance tests and security requirements.

## Proposed starting technology
Google Apps Script backend, Supabase PostgreSQL, optional Vue static administration UI. Zero-cost-first; no claim of free production operations.

## Critical technical risk
GAS Web Apps cannot freely set response headers and secure session cookies like a general-purpose web server. GAS-only production-grade OIDC/SSO has NOT been proved. The first POC must demonstrate standards conformance or justify a small portable protocol component. Do not write your own cryptography.

## Documentation
- [Charter](docs/architecture/PROJECT_CHARTER.md)
- [Architecture principles](docs/architecture/ARCHITECTURE_PRINCIPLES.md)
- [Roadmap](docs/roadmap/ROADMAP.md)
- [Integration contract](docs/protocol/MT-ISP-001.md)
- [POC acceptance](docs/poc/POC-01_ACCEPTANCE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Architecture decisions](docs/adr/ADR-001_SYSTEM_BOUNDARIES.md)

This public repository contains specifications only; never commit passwords, personal records, tokens or keys.


## Architecture v0.2 — approved brief, detailed designs pending technical review
- [Detailed Architecture](docs/architecture/DETAILED_ARCHITECTURE_v0.2.md)
- [Data Model / ERD](docs/data/DATA_MODEL_v0.2.md)
- [OIDC / SSO Protocol Profile](docs/protocol/MT-ISP-002_OIDC_PROFILE_v0.2.md)
- [Directory API Contract](docs/protocol/MT-ISP-003_DIRECTORY_API_v0.2.md)
- [ADR-003 Protocol Boundary](docs/adr/ADR-003_IDENTITY_PROTOCOL_BOUNDARY.md)
- [ADR-004 Directory SSOT and Application Autonomy](docs/adr/ADR-004_DATA_SSOT_AND_APP_AUTONOMY.md)
- [Threat Model v0.2](docs/security/THREAT_MODEL_v0.2.md)
- [Project Delivery Plan](docs/delivery/DELIVERY_PLAN_v0.2.md)
- [Acceptance Matrix / KPI Contracts](docs/delivery/ACCEPTANCE_MATRIX_v0.2.md)
- [Operations and Portability](docs/operations/OPERATIONS_AND_PORTABILITY_v0.2.md)

### Evidence status
Architecture documents: written. Runtime SSO feasibility, protocol conformance, integration, security and load tests: **NOT RUN**. Production release: **BLOCKED**. Public code repository must not contain secrets or real personnel data.

### Review gates
Detailed design files are proposed specifications. The earlier Architecture Brief v0.2 was approved as the basis for writing them; no claim that a working solution or all detailed ADRs have separately passed security review.


## Updated target architecture v0.3 (2026-11-13)
**Latest preferred POC direction:** Use Supabase Auth's native OAuth 2.1 / OIDC server as identity protocol engine, Google Apps Script for MT-IAM business/domain services, and Supabase PostgreSQL for personnel/identity data. This **replaces the earlier GAS-only OIDC feasibility preference**, without changing the independence of apps and their local permissions. Provider remains public beta; no POC executed. Prior v0.2 documents remain as historical designs and must not be read as the current preferred implementation.

- [Target Architecture v0.3](docs/architecture/TARGET_ARCHITECTURE_v0.3.md)
- [ADR-005 — Supabase Native OIDC](docs/adr/ADR-005_SUPABASE_NATIVE_OIDC_PROVIDER.md)
- [POC-02 — Supabase Native SSO Plan](docs/poc/POC-02_SUPABASE_NATIVE_SSO_PLAN.md)

**Critical trade-off:** MT-IAM owns domain and data governance but delegates OAuth/OIDC protocol execution to Supabase Auth (self-hostable components exist; portability/credential migration must be tested). Production status remains BLOCKED.

## GitHub Issues execution tracker — active SSOT (2026-11-13)
**[Open live MT-IAM Issues](https://github.com/idev006/MT-I-AM/issues)** — 12 domain Epic Issues [#1–#12](https://github.com/idev006/MT-I-AM/issues/1), five first-wave experiment Issues ([OIDC #13](https://github.com/idev006/MT-I-AM/issues/13), [Testing #14](https://github.com/idev006/MT-I-AM/issues/14), [Runtime #15](https://github.com/idev006/MT-I-AM/issues/15), [Database #16](https://github.com/idev006/MT-I-AM/issues/16), [Pooling #17](https://github.com/idev006/MT-I-AM/issues/17)). The graphical GitHub Projects board is **NOT YET CREATED/VERIFIED**: [activation task #18](https://github.com/idev006/MT-I-AM/issues/18) gives exact one-board setup and acceptance checks. The other 47 POCs remain in the Master Registry, not duplicate open issues. Work items start in Backlog; no POC PASS or live delivery percentage claimed.

## Executable Python POC foundation (initial, 2026-11-13)
The first **source-code scaffold** is now in this repository: [`pyproject.toml`](pyproject.toml), [FastAPI health application](src/mt_iam/api/app.py), [typed config](src/mt_iam/core/config.py), [Path Manager](src/mt_iam/core/paths.py), [foundation pytest tests](tests/test_poc_foundation.py), and [Dockerfile](Dockerfile).

**Start here on a Windows PC:** [Local POC Lab Quickstart](docs/poc/LOCAL_POC_LAB_QUICKSTART_v0.1.md). It gives repeatable local environment, test and Docker commands. **Important:** the code has been saved, but local execution/CI, Cloud Run, PostgreSQL, OIDC and security verification remain **NOT RUN**. The 52 POC registry contains planned experiments, not 52 completed software modules. Do not deploy the scaffold as an identity provider.

## Local-first POC Lab v0.2 — executed and synchronized (2026-11-13)
Code was first assembled and tested in an isolated Python environment, then the verified foundation files were synchronized to this repository. **Local evidence:** [8 passing synthetic tests and blocked Supabase probe](docs/poc/LOCAL_POC_EXECUTION_EVIDENCE_v0.2.md). [Python project metadata](pyproject.toml) · [DB-only SQLAlchemy adapter](src/mt_iam/adapters/database.py) · [one-shot PostgreSQL probe](src/mt_iam/adapters/probe.py) · [SQLite scoped tests](tests/test_database.py) · [sanitized environment example](.env.example).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,database]"
python -m pytest -q
python -m ruff check .
# With an approved secret set in your environment, not in GitHub:
python -m mt_iam.adapters.probe
```
**Do not count local SQLite test PASS as PostgreSQL/Supabase PASS.** A live Supabase connection, Windows execution and Ruff validation have not yet been executed by this workflow. This is a POC-only HTTP/DB scaffold, not an identity provider.

## Extensible POC Control Plane v0.3 — local prototype / GitHub promotion pending (2026-11-13)
A **dynamic TOML-based POC Registry and bounded POC Orchestrator** has been prototyped and tested in the local analysis environment. **Promotion of its v0.3 source files to this repository is not yet complete**: follow [tracking Issue #69](https://github.com/idev006/MT-I-AM/issues/69). The current GitHub `src/mt_iam/poc` v0.1 runner remains the published implementation until the reviewed v0.3 code is committed.

Local evidence (not CI): Python 3.13.5, 74 pytest tests passed; 52-ID TOML registry validated; optional 53rd ID registered in test without Python registry changes; targeted isolated orchestrator run showed 1 LOCAL_CHECK_PASS / 1 BLOCKED. A full 52 subprocess orchestrator run was **not completed within the local execution window**. No OIDC conformance, Supabase integration or Cloud Run runtime has passed. **Do not confuse local control-plane tests with complete POC PASS**.

## POC Platform v0.2 — extensible Registry + Orchestrator + TOML (2026-11-13)
**Source now committed:** [Platform Registry / Orchestrator](src/mt_iam/poc/platform.py), [CLI](src/mt_iam/poc/platform_cli.py), [typed TOML validator](src/mt_iam/poc/settings.py), [project TOML settings](configs/platform.toml), [POC registry TOML](configs/poc_registry.toml), [new tests](tests/test_poc_platform.py), [architecture & handoff design](docs/poc/POC_PLATFORM_DESIGN_v0.2.md).

```powershell
python -m pip install -e ".[test,database]"
python -m pytest -q
python -m mt_iam.poc.platform_cli --config configs/platform.toml --dry-run
python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/local.json
python -m mt_iam.poc.platform_cli --config configs/platform.toml --strict
```

**Local proof:** 79 pytest tests PASS (Python 3.13.5, isolated test environment), POC runner 30 `LOCAL_CHECK_PASS` + 22 `BLOCKED` + 1 disabled new POC `SKIPPED`; strict run returns exit 2 as designed. Source synchronization verified through GitHub contents. **No full POC is independently certified PASS; no actual Supabase/OIDC/Cloud Run validation.**

**Coexisting roadmap:** [Issue #69](https://github.com/idev006/MT-I-AM/issues/69) tracks the more advanced v0.3 design (subprocess deadlines/bounded scheduling, reviewer approvals, clean cross-platform CI). v0.2 is the committed, sequential fail-closed baseline and **does not claim to fulfill those v0.3 requirements**. An earlier note above about v0.3 promotion pending is historical and should not be interpreted as a denial of this newly committed v0.2 subset.

**SSOT:** GitHub Issues/Project remains the *only live work-status authority*. Execution JSON reports are immutable evidence snapshots, not independent Kanban tracking files.
