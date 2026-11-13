# ADR-007 — Python-first, provider-independent modular MT-IAM core

**Status: ACCEPTED (architecture direction explicitly selected by project owner, 2026-11-13).** Risk R3. Implementation, dependency review, OIDC conformance and production approval: **NOT RUN**.

## Context
ADR-006 selected Google Apps Script as initial domain backend and Supabase only as PostgreSQL hosting. The project owner has since explicitly selected **Python as the primary language, Google Cloud Run as the first runtime, and portability to non-Google infrastructure**. Existing app autonomy, standard identity protocol and Supabase database-only constraints remain.

## Decision
1. Own the MT-IAM application/domain source; reuse maintained open-source libraries and protocols instead of reinventing frameworks or cryptography.
2. Python-first **modular monolith** with domain/application/ports/adapters boundaries, isolated engines, dependency injection and typed contracts. FastAPI is a candidate HTTP layer, **not evidence of an OIDC provider**.
3. Deploy OCI-compliant containers initially on Google Cloud Run. Local Linux/Compose and at least one non-Google deployment target are mandatory portability demonstrations before a portability claim.
4. Supabase hosts **PostgreSQL only**; no Supabase Auth, OAuth provider, auth.users dependency, Edge Functions, proprietary application API or DB SDK in domain contracts.
5. Maintain MT-IAM-owned HTTPS issuer, OIDC/OAuth authorization-code+PKCE integration profile; independent EA clients retain their own admission, business permissions and data.
6. Database library separation: psycopg is PostgreSQL driver; SQLAlchemy manages queries, unit-of-work and pool policy; Alembic manages migrations. Alembic is **not** the runtime connector.
7. Use explicit configuration and secrets providers, path manager, per-resource ownership, bounded concurrency, tested shutdown and structured audit/telemetry.
8. Trace every R3 feature: Actor -> Use Case -> Rule -> State/Sequence -> API Contract -> Tests -> evidence. Block production until verified.
9. Preserve previous ADR/POC as historical decisions; do not delete history. This ADR **supersedes ADR-006 decision 2 (GAS as primary domain backend)** and architecture v0.4 GAS-specific physical layout, but retains ADR-006 provider independence and PostgreSQL-only policy.
10. GAS may be an optional integration client or adapter, not the mandatory core engine.

## Decisions intentionally open
- OIDC authorization-server implementation (maintained product vs validated library integration) and its interoperability/conformance evidence.
- Authentication factors, account recovery, administrative approval policy, session/revocation latency SLO, issuer domain, signing-key custody/rotation.
- PostgreSQL runtime connection topology and prepared-statement compatibility after empirical test.
- Pricing/availability/regulated-data approval and deployment topology for production.

## Consequences
- Positive: one coherent Python testable domain stack; migration, security testing and portable packaging simpler.
- Tradeoffs: team owns OIDC operations, secure key handling, upgrades, incident response and PostgreSQL lifecycle; OCI alone does not guarantee seamless migration.
- Migration: update index/SSOT links; replace GAS-specific POC criteria; do not rewrite historical records; require approved design and POC before implementation release.

## References
- NIST SP 800-63-4: https://pages.nist.gov/800-63-4/
- OIDC Core: https://openid.net/specs/openid-connect-core-1_0.html
- OIDC Discovery: https://openid.net/specs/openid-connect-discovery-1_0.html
- OAuth Security BCP RFC 9700: https://www.rfc-editor.org/rfc/rfc9700.html
- PKCE RFC 7636: https://www.rfc-editor.org/rfc/rfc7636.html
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- Google Cloud Run container contract: https://cloud.google.com/run/docs/container-contract
- Supabase PostgreSQL connections: https://supabase.com/docs/guides/database/connecting-to-postgres
