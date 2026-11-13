> **HISTORICAL POC PLAN — SUPERSEDED PHYSICAL ASSUMPTIONS (2026-11-13).** GAS-first tasks below are no longer the implementation target. See [ADR-007](../adr/ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md) and [Target v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md). Retain protocol-security outcome tests but redesign POC for Python-based portable runtime. All tests remain NOT RUN.

# POC-03 — Provider-Independent MT-IAM SSO Feasibility

**Status: NOT RUN.** Date: 2026-11-13. Supersedes POC-02 (Supabase Native OAuth) and disallows Supabase Auth.

## Fixed baseline
- GAS: identity domain operations.
- Supabase: PostgreSQL database hosting **only**.
- Identity protocol runtime: to be selected based on concrete HTTP/cookie/OIDC capabilities and portability; not assumed available in GAS.
- Two independent apps with different backend technologies and browser origins.

## Phase A — protocol feasibility
1. Establish stable HTTPS issuer under organization control.
2. Prototype standards-compliant authorization code + PKCE S256, top-level browser redirects, first-party Secure/HttpOnly cookie, token endpoint and JWKS.
3. Evaluate GAS native web app limitations objectively; if insufficient, isolate only protocol HTTP/session capabilities into a replaceable narrow component that does not impose Supabase Auth.
4. Verify key custody and tested cryptographic library; no handwritten token signatures.

## Phase B — outcome tests
| ID | Expected behavior |
|---|---|
| SSO-01 | App A login followed by App B does not ask password again while eligible |
| SSO-02 | App B denies user without local app access, A unaffected |
| SSO-03 | App A/B on different hosts, languages and callback domains |
| SSO-04 | Session persistence obeys inactivity and absolute timeouts |
| SEC-01 | Wrong iss/aud/signature/exp/nonce rejected |
| SEC-02 | Invalid PKCE/state/code replay and URI mismatch rejected |
| SEC-03 | Backend API checks local authorization independently of browser UI |
| SEC-04 | No secrets, private key or real personnel data exposed |
| REV-01 | Suspended users blocked and local sessions revoked within explicit tested bound |
| PORT-01 | Change domain data backend GAS to Python adapter without changing public OIDC/client contract |
| PORT-02 | Export/restore PostgreSQL to another provider and re-run app integration tests |
| PERF-01 | Measure p50/p95, errors, and service limits under specified load |

## Evidence and conditions
For every case: test environment, exact commands, source revision, timestamps, outputs, sanitized HAR/logs, reviewer and result PASS/FAIL/BLOCKED/NOT RUN. No release claim without protocol security, database restore and operational readiness.
