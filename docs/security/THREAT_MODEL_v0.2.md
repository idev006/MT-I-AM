# MT-IAM Threat Model v0.2 — STRIDE-Oriented
Risk tier: **R3** security and personal-information critical. Status: DRAFT. No security test evidence yet.

## 1. Protected assets
Personnel SSOT, account state, credentials and session material, OIDC signing key material, authorization codes and refresh tokens, app client configuration, identity audit evidence, Supabase backend keys.

## 2. Trust boundaries
Browser (untrusted) <> independently hosted app <> OIDC protocol boundary <> GAS domain backend <> Supabase database. Each app's local authorization and business logs are a separate owner boundary.

## 3. Attack scenarios and controls
| STRIDE | Scenario | Mitigations to test | Responsible layer |
|---|---|---|---|
| Spoofing | Fabricated user_id or login request | derive identity from verified OIDC claims; PKCE/state; rate limiting | Protocol + app |
| Spoofing | Service impersonates trusted client | client registration, exact redirect URI, confidential-client auth | Protocol |
| Tampering | Code replay or callback injection | one-time short-lived code, PKCE S256, state and nonce | Protocol |
| Tampering | JWT claims modified or wrong audience | cryptographic signature + issuer/audience/exp/nonce checks | App + protocol |
| Repudiation | Account disabled with no trace | append-oriented audit with actor, timestamp, correlation_id | IAM audit |
| Information disclosure | Personnel fields exposed to other apps | scoped profiles, minimal claims, privacy classification, logs redaction | Directory |
| Information disclosure | Supabase privileged key leaked from static web | backend secret only; no service_role in browser; rotate & monitor | GAS/DB |
| Denial of service | Scripts/DB exhausted by auth storms | quotas, per-client throttles, bounded requests, alarms | Edge/GAS |
| Elevation of privilege | App A token used in App B | strict audience/client validation | App B |
| Elevation of privilege | App client reads raw IAM tables | authenticated APIs, restricted DB roles/RLS | DB/GAS |
| Session attack | session fixation, CSRF, cookie theft | session rotation; Secure/HttpOnly/SameSite; CSRF defense | Protocol |
| Persistence | Disabled user retains active app session | bounded revalidation and suspension workflow | App + IAM |
| Supply chain | tampered dependency or leaked secret in public repository | lock files, SAST, secret scanning, peer review, SBOM | Delivery |

## 4. Abuse cases / negative tests
Attempt direct GAS endpoint bypass; cross-origin credential theft; duplicated authorization code; mismatched redirect URI; bogus nonce; token substitution; access after suspension; app access denial despite valid SSO; hidden business API calls without local permission; malicious directory query; partial DB writes; exhausted free quotas; lost signing key; stale cached directory entries.

## 5. Data privacy and law
Map personal data fields to purpose, source, lawful basis, who can access, retention/deletion and subject correction procedure. Follow applicable Thai personal data requirements and organizational policy; legal/privacy review required before using real personnel data. Public GitHub contains only synthesized examples.

## 6. Security gates
G1: assets/data flows and owner agreed; unresolved R3 risks listed.
G2: code/PKCE/cookie flow validated with independent apps and adversarial tests.
G6: SAST, dependencies, secret scan, key management, incident response, backup/restore evidence; no open critical vulnerabilities for production.
Failure: fail closed on unverified identity or inability to validate high-risk operations. Never claim compliance from documentation alone.

## 7. Open risks
- OIDC endpoint/session cookie feasibility with GAS remains BLOCKED.
- Signing key storage, domain/TLS, MFA/account recovery, incident controls, logging retention not yet implemented.
- Free provider availability/quota not guaranteed for production.
