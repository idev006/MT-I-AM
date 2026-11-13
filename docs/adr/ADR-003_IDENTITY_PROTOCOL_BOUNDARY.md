# ADR-003 — Standards-Compliant Identity Protocol Boundary
Status: PROPOSED (v0.2, 2026-11-13). Owner: MT-IAM architecture. Risk: R3.

## Context
MT-IAM must provide portable, cross-origin, long-lived-but-controlled SSO to arbitrary independent application stacks. GAS is primary business backend and Supabase PostgreSQL is the database. Conventional GAS Web Apps lack arbitrary Set-Cookie, headers and fine-grained HTTP response control; this threatens OIDC compliance.

## Decision proposed
Use an explicit **OIDC Protocol Boundary** whose implementation MUST pass browser and protocol conformance tests. Keep domain/account/directory and personnel SSOT services on GAS + Supabase. Identity protocols must not be improvised as application-specific login/verify API endpoints.

## Alternatives
A: GAS-only OIDC provider, test early. Risk: HTTP/cookie capability gap; cannot assert feasibility.
B: Small portable standards-capable protocol/session layer, business domain GAS. Additional runtime but minimal scope.
C: Mature self-hostable OSS OIDC engine integrating the MT-IAM domain; less custom protocol risk but another component.
D: Managed IdP: easiest operation but conflicts with portability/ownership preference.

## Selection criteria
OIDC conformance, PKCE, CSRF, secure cookie control, signature/key rotation, session logout and revocation, zero-fee POC, deployability, recovery and operation cost.

## Gate
No option approved for production until POC-01 publishes test commands, outcomes, latency, browser scenarios and threat mitigations. Any new runtime requires explicit architecture approval and updated ownership/portability documentation.
