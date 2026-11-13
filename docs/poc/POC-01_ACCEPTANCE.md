# POC-01 — SSO and Identity Acceptance

## Setup
Two independent test apps: A uses Vue+GAS; B uses a different backend/runtime and host. Synthetic users only. MT-IAM candidate GAS+Supabase, with optional protocol component if required.

| ID | Test | Pass criteria |
|---|---|---|
| SSO-01 | Login A then visit B | No repeat password with valid central session |
| SSO-02 | User has no access to B | B denies; A remains available |
| SSO-03 | Close and reopen browser | Session policy observed safely |
| SEC-01 | Bad issuer, audience, expiry or signature | Reject |
| SEC-02 | Replayed code or missing PKCE/state | Reject |
| SEC-03 | Forged user ID / direct protected API | Reject |
| SEC-04 | Disable central account | New login denied and active sessions end within declared bound |
| OPS-01 | IAM outage | Safe documented behavior |
| DATA-01 | Profile changed | Authorized refresh/sync works |
| PORT-01 | Backup and restore to another environment | Demonstrated |
| PERF-01 | Representative concurrency | Publish measured p50/p95 and bottlenecks |

Evidence: automated scripts, sanitized traces, configuration inventory, security review and sign-off. This document is a test plan, not a claimed PASS result.
