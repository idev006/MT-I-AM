# Project Charter — DRAFT v0.1

## Mission
One identity, independently developed applications, no unnecessary repeated login, common secure integration rules.

## Scope
MT-IAM provides identity and account lifecycle, a shared personnel directory SSOT (or authoritative synchronized view of upstream HR), cross-application SSO, client registration, minimal identity APIs and security audit.

Apps independently own access admission, internal roles/permissions, business logic/data, operational logs, deployment and technology choices.

## Constraints
- GAS business backend + Supabase PostgreSQL initial choice.
- Portable system and protocols, zero-cost-first POC.
- OIDC/OAuth standards, no homemade cryptography.
- Independent applications on different domains and runtimes.

## Governance
Gate-based approvals: Architecture -> SSO feasibility -> Core directory -> Two independent client integrations -> Security and performance -> Controlled pilot.

## Critical open issue
GAS cookie/header constraints may require a standards-capable protocol layer. This must be proved before production.
