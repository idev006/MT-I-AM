> **LIVE TRACKING UPDATE (2026-11-13):** 52 unique POC GitHub Issues exist, grouped under 12 Epics; read their open/closed state from [Issues](https://github.com/idev006/MT-I-AM/issues), not static columns below. [Python runner source](../../src/mt_iam/poc/) and [executed local check evidence](POC52_EXECUTION_REPORT_v0.1.md) are now available: 30 LOCAL_CHECK_PASS, 22 BLOCKED, **0 POCs verified full PASS**. Do not edit master-plan verification columns as a second live status system. [Projects board setup #18](https://github.com/idev006/MT-I-AM/issues/18) remains BLOCKED.

> **PROGRESS SSOT NOTE (2026-11-13):** Live task ownership/flow status is maintained through GitHub Issues and one derived Kanban view per [Kanban Governance](../delivery/AGILE_KANBAN_SSOT_GOVERNANCE_v1.0.md). Any NOT RUN column in this versioned plan is a *baseline snapshot*, not the current dynamic status; actual POC outcome comes only from evidence with reviewer confirmation. Do not maintain a second manually edited progress table here.

# MT-IAM Master POC Plan & Verification Matrix v1.0

**Status: APPROVED DIRECTION (POC-FIRST); individual experiments NOT RUN. Risk: R3.** Baseline 2026-11-13.
**Purpose:** Give every incoming team the same scope, order, evidence rules and decision criteria before investing in complex MT-IAM source code.
**Canonical references:** [Architecture v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md), [System Models v0.5](../architecture/SYSTEM_MODEL_v0.5.md), [ADR-007](../adr/ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md), [Engineering Standard v0.5](../delivery/ENGINEERING_VERIFICATION_STANDARD_v0.5.md), [Execution Playbook](POC_EXECUTION_AND_HANDOFF_v1.0.md), [Experiment Template](POC_SPEC_TEMPLATE_v1.0.md).

## North star and immutable boundary
Prove that a **Python-first, portable, modular MT-IAM** can offer standards-based central identity and browser SSO to independent EA applications. Each app retains admission, roles, business rules, hosting and storage. **Supabase = PostgreSQL hosting ONLY, not authentication**. Google Cloud Run = initial OCI deployment, not a mandatory code dependency. No proprietary API in domain contracts; no real personnel data in POCs. Reuse vetted open-source technology; never implement home-grown OAuth cryptography.

## Status and evidence vocabulary
- **Execution:** PLANNED / IN PROGRESS / DONE (project management only).
- **Verification:** PASS (executed evidence), FAIL (contradictory evidence), BLOCKED (required dependency/evidence unavailable), NOT RUN (unexecuted). Every item starts **NOT RUN**.
- A PASS requires source commit, versions, environment, commands, test inputs, sanitized output, measured limits/cost where relevant, owner/reviewer and date. A successful hello-world demo does NOT imply security/production readiness.
- Any change to core dependency, deployment topology or threat boundary requires impacted POCs to be rerun. Never roll up 52 green cells as proof of production safety.

## Portfolio — 12 domains, 52 POCs
| Group | Domain | Priority | Count |
|---|---|---|---|
| G01 | Runtime & Cloud Infrastructure | P0 | 4 |
| G02 | Database & Data Integrity | P0 | 5 |
| G03 | Modular Architecture & Engine | P0 | 5 |
| G04 | Identity & Authentication | P0 | 5 |
| G05 | OIDC / SSO / Federation | P0 | 6 |
| G06 | Authorization & Governance | P1 | 4 |
| G07 | API & Integration | P1 | 4 |
| G08 | Resource & Concurrency | P0 | 5 |
| G09 | Security & Privacy | P0 | 4 |
| G10 | Automated Testing & Delivery | P0 | 4 |
| G11 | Portability & Disaster Recovery | P1 | 3 |
| G12 | Operations, Performance & Cost | P1 | 3 |
| **Total** | | | **52** |

Priority P0 = architectural uncertainty to eliminate before implementing dependent critical functionality; P1 = mandatory before relevant production capability, can run in parallel with foundational work. Both priorities still require individual risk review.

## Registry and proposed acceptance evidence
The table is the authoritative registry; exact thresholds are set **before** running an experiment (with measurement method, baseline and owner). The 'proof' is the minimum question, not a presumption of PASS.

| ID | Experiment | Minimum proof needed | Verification |
|---|---|---|---|
| POC-G01-01 | FastAPI in local OCI and Cloud Run | Repeatable local/cloud run commands and logs | NOT RUN |
| POC-G01-02 | Startup, readiness, SIGTERM and shutdown cleanup | Repeatable local/cloud run commands and logs | NOT RUN |
| POC-G01-03 | Typed config, secret loading and environment isolation | Repeatable local/cloud run commands and logs | NOT RUN |
| POC-G01-04 | HTTPS, issuer/custom domain and revision routing | Repeatable local/cloud run commands and logs | NOT RUN |
| POC-G02-01 | psycopg + SQLAlchemy connection to Supabase PostgreSQL | Actual PostgreSQL SQL/transaction/migration evidence | NOT RUN |
| POC-G02-02 | Alembic schema migrations and controlled recovery path | Actual PostgreSQL SQL/transaction/migration evidence | NOT RUN |
| POC-G02-03 | Transactions, constraints and concurrent atomic writes | Actual PostgreSQL SQL/transaction/migration evidence | NOT RUN |
| POC-G02-04 | Runtime pooler compatibility and prepared statements | Actual PostgreSQL SQL/transaction/migration evidence | NOT RUN |
| POC-G02-05 | Backup/restore to independent PostgreSQL provider | Actual PostgreSQL SQL/transaction/migration evidence | NOT RUN |
| POC-G03-01 | Module boundaries and clean domain ports/adapters | Replaceable fake adapter and module contract tests | NOT RUN |
| POC-G03-02 | Dependency injection with replaceable fake adapters | Replaceable fake adapter and module contract tests | NOT RUN |
| POC-G03-03 | Use-case orchestrator coordinating engines | Replaceable fake adapter and module contract tests | NOT RUN |
| POC-G03-04 | Transactional outbox, idempotency and event contracts | Replaceable fake adapter and module contract tests | NOT RUN |
| POC-G03-05 | Configuration SSOT, PathManager and engine lifecycle | Replaceable fake adapter and module contract tests | NOT RUN |
| POC-G04-01 | Identity enrollment and account lifecycle | Valid + denied flows, state invariants and audit | NOT RUN |
| POC-G04-02 | Password hashing and credential verification policies | Valid + denied flows, state invariants and audit | NOT RUN |
| POC-G04-03 | MFA, step-up and recovery security flow | Valid + denied flows, state invariants and audit | NOT RUN |
| POC-G04-04 | Session establishment, expiry and revocation | Valid + denied flows, state invariants and audit | NOT RUN |
| POC-G04-05 | Suspension/deprovision race conditions | Valid + denied flows, state invariants and audit | NOT RUN |
| POC-G05-01 | Evaluate maintained open-source OIDC authorization server | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G05-02 | OIDC discovery, JWKS, key custody and rollover | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G05-03 | Authorization code + PKCE, state, nonce and validation | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G05-04 | Cross-origin two-app SSO with independent permission checks | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G05-05 | Logout, revocation and replay/suspension behavior | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G05-06 | OIDC conformance and adversarial protocol tests | OIDC conformance/security evidence with independent clients and negatives | NOT RUN |
| POC-G06-01 | Actor-role-permission and separation-of-duties matrix | Allow/deny matrix for scoped actors and apps | NOT RUN |
| POC-G06-02 | Scoped organization administration | Allow/deny matrix for scoped actors and apps | NOT RUN |
| POC-G06-03 | Client app registration/approval and lifecycle | Allow/deny matrix for scoped actors and apps | NOT RUN |
| POC-G06-04 | App-local rejection after valid MT-IAM login | Allow/deny matrix for scoped actors and apps | NOT RUN |
| POC-G07-01 | OpenAPI-first contracts and compatibility checks | Published contract and independently verified consumer | NOT RUN |
| POC-G07-02 | Versioning, errors, pagination and idempotency | Published contract and independently verified consumer | NOT RUN |
| POC-G07-03 | Machine API auth, throttling and dependency failure | Published contract and independently verified consumer | NOT RUN |
| POC-G07-04 | Cross-language client interoperability and contract checks | Published contract and independently verified consumer | NOT RUN |
| POC-G08-01 | Shared pool ownership and connection cleanup | Measured resource bounds, failure path and cleanup | NOT RUN |
| POC-G08-02 | Structured tasks, cancellation and deadlines | Measured resource bounds, failure path and cleanup | NOT RUN |
| POC-G08-03 | Per-engine concurrency limits, backpressure and bounded queues | Measured resource bounds, failure path and cleanup | NOT RUN |
| POC-G08-04 | Memory/FD/connection stability across repeated workloads | Measured resource bounds, failure path and cleanup | NOT RUN |
| POC-G08-05 | Crash/restart, durable jobs and partial-failure recovery | Measured resource bounds, failure path and cleanup | NOT RUN |
| POC-G09-01 | Threat model and risk-selected OWASP ASVS controls | Threat-specific negative tests and sanitized security evidence | NOT RUN |
| POC-G09-02 | Secrets/key custody, rotation and least privilege | Threat-specific negative tests and sanitized security evidence | NOT RUN |
| POC-G09-03 | PII minimization, retention, scoped access and audit integrity | Threat-specific negative tests and sanitized security evidence | NOT RUN |
| POC-G09-04 | Abuse cases: credential attacks, CSRF, replay and privilege escalation | Threat-specific negative tests and sanitized security evidence | NOT RUN |
| POC-G10-01 | pytest unit/integration/contract harness | Automated CI output at exact revision | NOT RUN |
| POC-G10-02 | Ruff, typing, dependency audit and supply-chain checks | Automated CI output at exact revision | NOT RUN |
| POC-G10-03 | GitHub CI, OCI build, staging deploy and smoke gates | Automated CI output at exact revision | NOT RUN |
| POC-G10-04 | Traceability IDs and automated evidence gates | Automated CI output at exact revision | NOT RUN |
| POC-G11-01 | Same OCI artifact on Cloud Run and non-Google Linux host | Repeatable migration/restore on a different host or DB | NOT RUN |
| POC-G11-02 | PostgreSQL migration away from Supabase | Repeatable migration/restore on a different host or DB | NOT RUN |
| POC-G11-03 | Issuer/keys/client continuity plus recovery drill | Repeatable migration/restore on a different host or DB | NOT RUN |
| POC-G12-01 | Load, burst, soak and sign-in latency benchmark | Recorded metrics, realistic billing/alert checks and limits | NOT RUN |
| POC-G12-02 | Structured telemetry, alerts and incident runbooks | Recorded metrics, realistic billing/alert checks and limits | NOT RUN |
| POC-G12-03 | Free-tier attribution, billing review and cost guardrails | Recorded metrics, realistic billing/alert checks and limits | NOT RUN |

## Risk-first execution waves
**Wave 0 — design-risk screen before implementation:** POC-G05-01 (compare feasible OIDC authorization servers, library lifecycle, license, security model, integration), define issuer/subject invariants and threat assumptions. This is a comparison study, not authorization to ship.

**Wave 1 — cheapest infrastructure foundation:** POC-G10-01 then POC-G01-01, G01-02, G03-02; reproduce same FastAPI ASGI app locally first; deploy minimum Cloud Run resources only when local checks pass. Read-only/no-secret smoke checks first.

**Wave 2 — data + architecture:** POC-G02-01, G02-04, G02-03, G02-02; G03-01/03/05; G08-01/02. Confirm pooling vs Supabase transaction-pooler/driver features empirically; migration through one controlled job, never startup of every instance.

**Wave 3 — security critical identity slice:** POC-G04-01/02/04, G05-02/03/04/05/06, G06-04, G09-01/02/04. Synthetic identities; two different app origins/stacks. Prove invalid redirect URI, wrong iss/aud/nonce, code reuse, forged tokens and denied app membership fail closed.

**Wave 4 — operationalization:** remaining G03/G04/G06/G07/G08/G09/G10/G11/G12. Rehearse alternate host, PostgreSQL restore, key continuity, failure recovery, per-instance budgets and real incident procedures before production.
Parallelism is allowed when explicit prerequisites and evidence environments do not conflict; do not interpret numerical ID as chronological requirement.

## Critical cross-group decisions (risk ledger)
| Risk / decision | Dependencies | Gate |
|---|---|---|
| Suitable, maintained OIDC authorization server integrated with Python | G05-01, G05-03, G05-06, G09 | BLOCKED until selection and evidence |
| Browser first-party SSO with distinct origins and app-local denial | G05-04, G06-04, G07-04 | NOT RUN |
| PostgreSQL serverless pool/transaction behavior and recovery | G02-04, G08-01, G02-05 | NOT RUN |
| No vendor lock-in / preserve identity issuer on relocation | G11-01/02/03 | NOT RUN |
| Cleanup, cancellation, consistency under load | G08, G12-01 | NOT RUN |
| Operational/cost/privacy authorization to handle real personnel | G09-03, G12-03, operations approvals | BLOCKED |

## Scope boundaries for initial spending
- Start with local Python and local PostgreSQL/testcontainers. Use minimal Cloud Run revisions with minimum instances = 0 and bounded max instances for POCs; delete unused test resources after capturing evidence.
- Verify current Google price/quotas for every enabled product before use. Free request quotas do not automatically cover builds, registry image storage, egress, logs, domain/networking or Supabase costs.
- Budget alerts are not hard spending caps. Prepayment remaining in billing is not evidence of free tier eligibility. Record cloud service costs and ownership.
- No passwords/API tokens/PII in public GitHub, artifacts or CI logs. Use test accounts and synthetic names.

## Required POC deliverables
Per executed POC create `docs/poc/evidence/<POC-ID>/RESULT.md` (template-linked), sanitized commands/logs, measured outcomes, decision and relevant ADR update. Add new source/testing files only for a scoped experiment; every experiment must be independently removable or promoted with review. Preserve failures and superseded trials.

## Exit conditions
**Proceed to a dependent implementation slice** only if its named P0 dependencies PASS and security/contract review is satisfied. **Production approval** separately requires all applicable R3 gates, conformance, data protection/legal signoff, reliability and recovery evidence. Zero POCs are marked PASS at baseline creation.

## Further authoritative references
- https://openid.net/specs/openid-connect-core-1_0.html
- https://www.rfc-editor.org/rfc/rfc9700.html
- https://pages.nist.gov/800-63-4/
- https://owasp.org/www-project-application-security-verification-standard/
- https://cloud.google.com/run/docs/container-contract
- https://supabase.com/docs/guides/database/connecting-to-postgres
