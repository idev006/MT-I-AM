> **SUPERSEDED / HISTORICAL — DO NOT IMPLEMENT.** Replaced by [ADR-006](../adr/ADR-006_PROVIDER_INDEPENDENT_GAS_POSTGRES_ONLY.md), [Target Architecture v0.4](../architecture/TARGET_ARCHITECTURE_v0.4.md), and [POC-03](../poc/POC-03_PROVIDER_INDEPENDENT_SSO.md). Supabase is PostgreSQL storage ONLY; Supabase Auth/OAuth Server is prohibited as a MT-IAM dependency.

# ADR-005 — Use Supabase Auth Native OAuth 2.1 / OIDC Server
Date: 2026-11-13
Status: PROPOSED — supersedes the *proposed implementation option* in ADR-003, not approved for production.
Risk: R3

## Decision
Adopt Supabase Auth OAuth 2.1 Server / OpenID Connect provider as the **preferred protocol engine for POC-01**. Continue to use Google Apps Script as MT-IAM's primary personnel/account/directory/governance business backend and Supabase PostgreSQL as the primary database. Vue/static authorization UI integrates with Supabase Auth; OAuth clients are independently hosted in any supported stack.

## Newly verified capability (as of 2026-11-13)
Supabase documentation says OAuth 2.1 Server supports OIDC discovery, ID tokens, authorization code+PKCE, refresh token, JWKS, userinfo, OAuth app registration and custom login/consent UI. Public beta, available on all plans, MAU usage counts against plan limits. References:
- https://supabase.com/docs/guides/auth/oauth-server
- https://supabase.com/docs/guides/auth/oauth-server/getting-started
- https://supabase.com/docs/guides/auth/oauth-server/oauth-flows
- https://supabase.com/features/oauth2-1-server

## Architecture boundary
- Supabase Auth: authentication credentials, OAuth authorization, JWT signatures, identity protocol session, PKCE, revocation semantics as provided/tested.
- MT-IAM GAS: shared personnel directory SSOT, organization assignments, account-governance workflows, restricted administration, identity audit aggregation and client governance orchestration.
- Supabase PostgreSQL: user-person mapping, personnel data, organization directory and application registration metadata. auth.users is the *authentication account record*, while domain person_id/user_id mapping and source provenance are separately modeled. Never copy passwords into custom GAS tables.
- Each app: app access admission, local roles, permissions, business rules, business data and logs. OAuth client registration grants only an identity trust relationship, NOT app access.

## Consequences
This is a change from the previously preferred *self-owned authentication protocol engine* to a self-managed **MT-IAM product using Supabase Auth's protocol engine**. Source/portability goal remains: GoTrue/Supabase components are self-hostable where supported, but a seamless migration of password hashes, MFA state, issuer, tokens, keys and active sessions is NOT guaranteed. Portable SQL alone does not solve this. Explicit exit strategy and tests required.

## Mandatory implementation policy
1. Enable Authentication > OAuth Server; create separate OAuth clients for test App A and App B.
2. Use Authorization Code + PKCE S256 and openid scope; configure exact callback URIs. Keep dynamic client registration disabled by default.
3. Set asymmetric JWT signing keys (RS256/ES256): Supabase docs require asymmetric signing for OIDC ID tokens. Verify JWKS/issuer/audience and expiration.
4. Implement a secure authorization UI, consent policy, session reuse and account-disabled behavior. No self-coded custom JWT signing.
5. GAS must not expose service_role credentials to browsers; protect admin-to-Supabase calls, add RLS and access scoping.
6. Test cross-origin SSO on at least 2 independent runtime/hosting stacks, including denied admission. Confirm cookies, reauthentication UX, refresh and logout on real browsers.
7. Do not claim automatic global app logout or instantaneous revocation. Define bounded local-session invalidation.
8. No public-repo credentials or real personnel records.

## Rejected alternatives for baseline POC
- GAS-only hand-made OIDC server: excessive HTTP/cookie/protocol risk.
- Additional Worker by default: unnecessary before testing native Supabase OIDC support.
- JWT-only shared login: does not deliver correct multi-app SSO.

## Evidence / acceptance
Status: NOT RUN. G1 requires architecture review, G3 requires two-app OIDC and SSO integration evidence, G6 requires security tests, G7 requires migration/restore and operational proof. Public beta maturity and free tier limits require explicit risk acceptance before pilot.
