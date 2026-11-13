# MT-IAM — MT Identity & Access Management

Status: Architecture Foundation Draft v0.1 — 13 November 2026.

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
