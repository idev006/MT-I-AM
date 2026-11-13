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
