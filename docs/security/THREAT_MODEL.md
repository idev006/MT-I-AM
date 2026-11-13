# MT-IAM Initial Threat Model (DRAFT)

| Risk | Mandatory control |
|---|---|
| Token theft | Short-lived tokens, secure sessions, XSS protections, revocation |
| Cross-app token reuse | Audience, issuer and signature validation |
| OAuth code replay/login CSRF | State, PKCE, nonce when required, one-time codes |
| Caller ID spoofing | Identity from verified evidence, not request body |
| Direct GAS bypass | Authenticated gateway/service boundary, not secret URL |
| Supabase service key leak | Backend only, scope and rotation |
| Unauthorized directory access | Minimized claims, access filtering and audit |
| Revoked users still active | Explicit bounded revocation policy and test |
| Session/cookie interception | Secure, HttpOnly, SameSite appropriately configured |
| Sensitive logging | No passwords, raw tokens, keys or unnecessary personnel details |
| Service outage | Fail-safe design, monitoring and documented recovery |
| Public repository | No secrets, real personal data or credentials |

No production release until security testing and OIDC/session feasibility pass.
