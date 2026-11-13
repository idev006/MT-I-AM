> **SUPERSEDED / HISTORICAL — DO NOT IMPLEMENT.** Replaced by [ADR-006](../adr/ADR-006_PROVIDER_INDEPENDENT_GAS_POSTGRES_ONLY.md), [Target Architecture v0.4](../architecture/TARGET_ARCHITECTURE_v0.4.md), and [POC-03](../poc/POC-03_PROVIDER_INDEPENDENT_SSO.md). Supabase is PostgreSQL storage ONLY; Supabase Auth/OAuth Server is prohibited as a MT-IAM dependency.

# POC-02 — Native Supabase OIDC SSO Feasibility Plan
Status: NOT RUN. Date 2026-11-13.
Technical candidate: Supabase OAuth 2.1 Server public beta as OIDC provider; GAS MT-IAM domain backend; Supabase PostgreSQL personnel SSOT.

## Preflight
- Verify OAuth Server feature actually available and enabled in target Supabase project.
- Validate free plan MAU and operational limits; note public beta risk and issuer/domain conventions.
- Configure asymmetric JWT signing key (RS256/ES256) for ID tokens.
- Register two separate OAuth clients, exact HTTPS callback URIs.
- Construct branded /oauth/consent UI using official SDK getAuthorizationDetails, approveAuthorization, denyAuthorization.
- Synthetic identity only.

## Demonstration
A = GAS-backed Vehicle Contact prototype. B = Python/Node or other independent app on another origin. Each app uses generic OIDC client, not a shared Supabase Auth client SDK requirement. Both have local user admission/access data.

## Mandatory acceptance
- SSO-A1: Browser signs in via A then via B without another password prompt under valid policy.
- SSO-A2: Browser cold reopen produces expected result based on session persistence policy.
- SSO-A3: B rejects unauthorised account without invalidating A or global session.
- SEC-A1: JWT issuer, audience, signature, expiry and nonce validation rejects invalid cases.
- SEC-A2: PKCE/state/code replay and incorrect redirect URI are rejected.
- SEC-A3: No cross-app token reuse or service_role exposed.
- OPS-A1: Central disable blocks fresh authorization; local session termination bounded and measured.
- OPS-A2: Sessions/refresh/logout behavior measured in two browsers.
- PERF-A1: P50/P95 end-to-end SSO measured under representative test load.
- PORT-A1: Document and test portability path for users/issuer/keys; disclose unportable items.

## Output evidence
Sanitized test IDs, browser/environment, exact commands/scripts, result (PASS/FAIL/BLOCKED), timestamp, provider version/feature status, relevant request correlation IDs, logs without secrets, P50/P95/error, and unresolved risk owner. Do NOT claim POC complete from documents alone.

## Supabase official reference
https://supabase.com/docs/guides/auth/oauth-server/getting-started
https://supabase.com/docs/guides/auth/oauth-server/oauth-flows
