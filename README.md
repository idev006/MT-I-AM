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
