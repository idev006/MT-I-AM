# MT-ISP-001 — Independent Application Integration (DRAFT)

## Boundaries
MT-IAM authenticates, manages common identity/personnel directory and registers trusted application clients. Every application decides its own user admission, roles, permissions, business actions and storage.

## Standards
- HTTPS/TLS
- OpenID Connect Authorization Code + PKCE for interactive sign-in, conditional on provider conformance POC
- OAuth/OIDC discovery, authorization, token and JWKS behavior as specified by standards
- Validate signature, issuer, audience, expiry, nonce/state where applicable
- Immutable issuer+subject identity key, not email as primary key
- JSON UTF-8 and OpenAPI for proprietary directory and administration APIs

## App onboarding
App ID, client ID/type, owner contact, redirect URI allowlist, permitted scopes, security evidence, supported contract version and incident response contact.

## Directory APIs — logical proposed interfaces, not deployed GAS paths
- GET /v1/identity/me
- GET /v1/directory/changes
- GET /v1/organizations
- Restricted admin APIs for app client registration

## Error semantics
Stable code, message, request_id and optional retry_after. Distinguish unauthenticated, forbidden, rate limited and unavailable; no account enumeration leaks.

## Restrictions
Never pass tokens in query strings, trust browser-provided user IDs, or use token issued for App A at App B. Never let clients query IAM storage tables directly.

## Known risk
GAS lacks arbitrary HTTP response header and cookie control. OIDC/SSO with GAS alone is unproven; the protocol surface may need a portable edge component. No custom auth/verify endpoint can substitute for OIDC conformance.
