> **HISTORICAL ADR — PARTIALLY SUPERSEDED by [ADR-007](ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md) on 2026-11-13.** GAS-first implementation decision no longer current. Provider-independence, PostgreSQL-only policy and application autonomy remain binding. Read [Target v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md).

# ADR-006 — Provider-Independent MT-IAM; Supabase Database Only

**Status: ACCEPTED — user approved, 2026-11-13.** Risk tier R3. **Supersedes ADR-005** and the implementation assumptions of Target Architecture v0.3 / POC-02.

## Decision
1. MT-IAM is the organizational identity core and a vendor-neutral OIDC-facing system.
2. **Google Apps Script** is the initial primary application/domain backend and orchestration language.
3. **Supabase PostgreSQL is used ONLY as a PostgreSQL database hosting service.** Do NOT use Supabase Auth, OAuth Server, Auth user store, Auth JWT issuer, Edge Functions, Storage, Realtime or proprietary product services as dependencies of MT-IAM.
4. All independent applications integrate only through **MT-IAM's versioned MT-ISP** (OIDC/OAuth identity contract, HTTPS directory API), not via Supabase URLs or SDKs.
5. Every application owns user admission, local roles, permissions, business rules, data, logs and deployment; registration at IAM does NOT grant end-user app access.
6. The system must permit migration of GAS domain backend to another language (e.g., Python) and database hosting to another PostgreSQL provider with no app business-code change, subject to stable public identity contract.

## Critical feasibility condition
Do not claim GAS alone implements production-grade OIDC, cookie handling, token issuance or signing. GAS web app response header/cookie/status/redirect controls are limited. The logical OIDC protocol boundary **requires a standards-capable, replaceable implementation**, selected after a proof-of-concept. This component may be separately hosted, but its API remains MT-IAM-owned and provider-independent. No Supabase Auth fallback.

## Portability architecture
- Stable, MT-IAM-owned HTTPS issuer URL and discovery endpoint. Caution: preserving URL is necessary but insufficient; key rollover, token issuer, subjects, clients and user sessions all need a tested migration.
- Core domain ports: PersonRepository, IdentityRepository, OrganizationRepository, SessionRepository, ClientRegistryRepository, AuditRepository.
- PostgreSQL adapter via restricted, authenticated server-to-server data access; if using an HTTP façade, it must be provider-independent and security-reviewed; do not expose database service credentials to browsers.
- Identity protocol runtime: conforms to OIDC/OAuth standards and uses portable, reviewed cryptographic/session libraries; password/MFA and key custody need separate decisions.
- No assumption of Supabase auth.users or Supabase auth SDK compatibility.

## Acceptance
A user logs in once at App A, opens App B on another domain without re-entering credentials while central session is eligible; App B can still deny app access. Wrong audience/issuer, expired or forged tokens rejected. A PostgreSQL provider migration and GAS-to-Python domain adapter exercise preserve external contracts. Evidence must be executed and recorded; none is claimed here.

## Documentation lineage
ADR-005 Supabase Native OIDC is rejected/superseded. Target Architecture v0.3 and POC-02 are historical and must not be followed. Superseding design is v0.4 and POC-03.
