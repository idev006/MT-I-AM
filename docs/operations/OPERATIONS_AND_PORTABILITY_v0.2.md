# MT-IAM Operations and Portability Plan v0.2
Status: DRAFT; procedures not yet exercised.

## Environments
- DEV: synthetic profiles, isolated Supabase project/schema and GAS deployments, throwaway keys.
- STAGING: isolated test data, production-like secure protocol endpoint and client registration.
- PROD: separate accounts/credentials, TLS, logging, backup, monitoring and change approval. Free tier may not meet required availability.
No production secrets in GitHub or browser.

## Versioned deployment
- GAS via clasp/versioned immutable deployments and environment config (never commit .clasp.json with secrets).
- Supabase PostgreSQL via ordered reviewed SQL migrations and constrained database roles.
- Vue static assets via repeatable build with dependency locks and reviewed GitHub Actions if adopted.
- OIDC protocol runtime chosen after POC; record issuer URL, client callback allowlist, cookie policy, TLS and JWKS.
- Separate app deployments never depend on IAM code internals.

## Recovery and migration
Export PostgreSQL schema/data from a least-privileged maintenance environment and verify restore to another PostgreSQL target. Preserve stable user IDs and source provenance. Signing private keys and encryption materials require protected separate export with authorized custody; never store them alongside public database backups. Any issuer URL change is a trust migration for every client; create a dual-issuer/transition plan if needed and test it.

## Monitoring
Track auth success/error rates, P95 request latency, database connection failures, GAS quota errors, rate-limited clients, suspensions, token/key validation errors and unusual sign-in patterns. Logs redact credentials, raw tokens and unnecessary personal details.

## Incident response
Detect -> contain (disable client, revoke sessions/rotate secrets) -> preserve protected evidence -> assess privacy implications -> recover -> review. Define owner, contacts, notification policy and change log before pilot.

## Capacity and failure policy
- Avoid synchronous IAM requests on every business operation.
- Client local sessions may survive short IAM outage within defined security policy; privileged actions fail securely when necessary.
- Set timeouts, retry budgets and circuit breakers; never infinite retries.
- Measure GAS concurrency and Supabase free tier limits under realistic scenarios.

## Portability exit tests
Clean deployment from repository, restore migrated PostgreSQL, re-register two external clients, validate JWKS/key rollover, verify login + app-local authorization and complete smoke/security tests without reliance on former managed service identity assumptions.
