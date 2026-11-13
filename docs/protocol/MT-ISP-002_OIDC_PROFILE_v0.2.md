# MT-ISP-002 — OIDC/SSO Protocol Profile v0.2 (DRAFT)
**Not a claim of implemented protocol compliance.** Baseline: OpenID Connect Core, Discovery, OAuth 2.0 Security BCP (RFC 9700), PKCE (RFC 7636).

## Purpose and boundary
MT-IAM authenticates a person; each application independently controls admission and its internal permissions. The shared trust contract MUST NOT require application code in GAS or use of Supabase.

## Client registration requirements
- Each app has unique client_id and owner, approved exact redirect_uri(s), public vs confidential client type, scopes, and contact.
- Browser-based clients use authorization code + PKCE S256, state; nonce for ID token binding where applicable.
- Avoid implicit and resource-owner-password flows. Never put access or refresh tokens in redirect URL.
- Server-based apps must protect client credentials and callbacks; secrets never embedded in static JavaScript/GAS browser code.

## Required standards-capable endpoints
- /.well-known/openid-configuration
- authorization_endpoint
- token_endpoint
- jwks_uri
- userinfo_endpoint (if part of supported conformance profile)
- logout and revocation behavior must be explicitly specified and tested.
These are protocol requirements, not known deployable GAS routes. Endpoints/HTTP status codes, Set-Cookie, CORS and Cache-Control require actual implementation evidence.

## Authorization code sign-in
1. Application generates random state, PKCE verifier/challenge; nonce where required; stores one-time correlation bound to browser.
2. Browser top-level redirects to issuer authorization endpoint for the app's client_id.
3. IAM authenticates or reuses valid first-party SSO session; reauthentication policy may require interaction.
4. Issuer returns single-use short-lived code only to exact registered callback.
5. Client exchanges code + verifier; issuer validates client and code, expiration, URI and PKCE.
6. Client validates ID token signature using issuer JWKS, iss, aud, exp, iat, nonce and other applicable claims; establishes an independent app session.
7. App checks its own user membership and roles. Successful authentication by IAM is NEVER sufficient for app admission.

## Token validation
- No token for App A can authenticate App B; enforce aud/client policy.
- Public JWKS supports key rotation with overlap; fail securely on unknown keys with bounded retry.
- Access tokens for APIs and ID tokens for client authentication are distinct. Clients MUST NOT treat one as the other.
- Stable identity is (issuer, subject), not mutable email/display name.

## Session model
- Central server-managed SSO session, first-party cookie when protocol runtime supports Secure, HttpOnly and correct SameSite; CSRF protection.
- Separate local app sessions with independently defined inactivity and absolute lifetimes.
- Closing tab is not automatically logout; expiration, account disable, reauth and global sign-out require documented policy.
- Browser cookie restrictions make third-party iframe silent login unreliable. Favor top-level navigation rather than undocumented third-party cookies.

## Revocation / suspension
- Central disabled users cannot initiate new authorization.
- Existing local app sessions end by declared max revalidation age or tested back-channel mechanism; no blanket instant revocation promise.
- Every application must honor risk-tiered reauthentication and session policies.

## Nonfunctional and portability
- Issuer is canonical HTTPS URL; changing it is a breaking identity migration unless planned; document recovery and rollover.
- Rate limits, error semantics, logging, client secrets and key custody are part of provider security surface.
- GAS-only provider feasibility is OPEN (ADR-002). Validate protocol component against OIDC conformance tests and adversarial tests before pilot.

## References (normative starting points)
https://openid.net/specs/openid-connect-core-1_0.html
https://openid.net/specs/openid-connect-discovery-1_0.html
https://www.rfc-editor.org/rfc/rfc7636
https://www.rfc-editor.org/rfc/rfc9700
