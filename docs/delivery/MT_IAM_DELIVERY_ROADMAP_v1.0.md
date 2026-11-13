# MT-IAM Delivery Roadmap v1.0 — POC-first, Evidence-gated

**Baseline: 2026-11-13.** Status: ROADMAP ACCEPTANCE PROPOSED; dates/owners not assigned. The source of truth for *current issue status and responsibility* is [GitHub Issues / the existing Project Board](https://github.com/idev006/MT-I-AM/issues), **not this roadmap**. Roadmap describes sequencing, outcomes, dependencies, and decision gates; results live in POC evidence and reviews.

## North star
Deliver secure, portable, standards-based MT-IAM central authentication / SSO for multiple independently owned EA applications with **Python-first modular core**, **PostgreSQL (Supabase database hosting only)**, **Cloud Run initially**, no custom OAuth cryptography, and **app-local admission/permissions**. Never infer production suitability from a working localhost prototype.

## Current factual baseline
- [Architecture baseline v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md) and [12-group/52-POC master registry](../poc/MASTER_POC_PLAN_v1.0.md) exist.
- [POC platform design v0.2](../poc/POC_PLATFORM_DESIGN_v0.2.md), dynamic TOML registry, sequential orchestrator, fail-closed unknown handler, and [local-only evidence](../poc/POC_PLATFORM_LOCAL_EVIDENCE_v0.2.md) exist.
- Latest documented local run: 79 pytest checks passed; 30 synthetic/local checks; 22 require external evidence. **Zero full POC PASS independently confirmed.** Local result labels must never be confused with final security or release acceptance.
- Production-grade subprocess isolation, deadlines/cancellation, process-tree cleanup, bounded concurrency, cross-platform CI and dependency locks remain open, see [Issue #69](https://github.com/idev006/MT-I-AM/issues/69).
- Supabase PostgreSQL, OIDC conformance, Cloud Run, independent app SSO, operational billing and data protection gates are **BLOCKED/NOT RUN**, pending valid environment and independent test evidence.
- This is a **sequence roadmap**, NOT a fixed delivery-time estimate or manually editable percentage-complete board.

## Workstreams and gated milestones
| Phase | Purpose and deliverables | Core dependencies | Gate to exit | Status source |
|---|---|---|---|---|
| P1 — POC Platform v0.3 | Registry lifecycle/versioning, trusted handler allowlist, orchestrator subprocess isolation, cancellation/deadline, process-tree cleanup, bounded concurrency/WIP, evidence schemas, secure TOML config, CLI/API tests | v0.2 foundation; security/resource safety review | Hard-fail/timeout/cancel/restart/cleanup and repeated-run evidence, CI Python 3.12/3.13 Windows/Linux, review; no untrusted execution | [#69](https://github.com/idev006/MT-I-AM/issues/69) |
| P2 — Critical POC verification | Real OIDC provider feasibility, Supabase PostgreSQL pooler/migrations, OCI/Cloud Run, two-app SSO, authorization denial, threat tests, portability, restore, cost/reliability | P1 trusted harness relevant portions; approved test infrastructure and secrets | Each critical POC gains PASS with reproducible independent evidence; FAIL/BLOCKED gaps have explicit owners and decisions | 52 [POC Issues](https://github.com/idev006/MT-I-AM/issues) + evidence |
| P3 — Detailed system architecture | Revised ADRs, bounded contexts, actors/use cases, contracts, sequences/states, threat model, deployment model, operational ownership | P2 critical architecture decisions | Reviewable v1.0 architecture + traceability ACT→UC→BR→API/SEQ→TEST, unresolved R3 decisions clearly blocked | Architecture Issues/PRs |
| P4 — Detailed database design | PostgreSQL ERD, normalized schema, primary/unique/foreign constraints, indexing, partition/retention, migration/rollback, audit/privacy boundaries | P2 transaction/pooling evidence, P3 domain ownership | Schema changes proven via Alembic migration/rollback, integrity, concurrency and PostgreSQL compatibility tests | Data design Issues/PRs |
| P5 — Vertical-slice application engineering | Enrollment/admin, credentials/MFA, client registration, sessions, consent/privacy, standards-based OIDC integrations, app-local authorization | P3/P4 reviewed; provider and keys proven | Each slice with unit/integration/contract/security/e2e/fault tests, code review, evidence; no broad untested release | Feature Issues/PRs |
| P6 — Staging/hardening/release | Full E2E SSO, conformance, secrets/key rotation, backup/restore, load/soak, telemetry/alerts, incident drills, costing, risk/legal approval | P5 slices and secure staging environments | Independent R3 sign-off + release checklist + recoverable rollbacks; **no production approval by implication** | Release gate Issues |

## P1 — next actionable tasks; pull in dependency order, not dates
1. **POC-P1A — Registry contract & TOML SSOT:** schema version and migration rule, duplicate IDs, dependency cycle/unknown IDs, typed config hierarchy, secrets sourced only from environment, safe-path resolution and audit. Existing dynamic registry tests form a baseline; prove *add one new item without editing core*.
2. **POC-P1B — Isolated Orchestrator execution:** handler is a fixed trusted registry key; launch isolated subprocess with hard timeout, cooperative cancellation, forced kill and reaping, no descendant orphan, bounded output/exit codes and sanitized evidence. Test success, exception, timeout, SIGTERM, concurrent cancel and recovery.
3. **POC-P1C — Resource governance:** configure concurrency, CPU/memory/DB-connection budgets and backpressure; enforce correct invariants rather than accepting inert TOML settings. On limited 8 GB developer PCs default to one worker unless measured safe.
4. **POC-P1D — Verification pipeline:** Windows/Linux × Python 3.12/3.13 CI, pinned dependency resolution/lock, Ruff/type/security/dependency checks, reproducible test command and evidence digest. Workflow existence alone is NOT run evidence.
5. **POC-P1E — Evidence and progress SSOT:** versioned RESULT schema with POC-ID, code/test/environment fingerprints, observed metrics, negative paths, reviewer/sign-off and exact verification verdict. **GitHub Project Status alone is workflow state**, not evidence PASS.
6. **P1 Exit Review:** prove runner of all 52 IDs terminates predictably, returns evidence for each, bounded resources and no false PASS for blocked providers. Confirm source commit/PR and do not close #69 without independent review.

## P2 — suggested first experiments and required external proof
| POC | Technical question | Minimum external evidence |
|---|---|---|
| [G05-01](https://github.com/idev006/MT-I-AM/issues/13) | Maintained standards-compliant OIDC authorization-server approach, integrated with Python | Candidate comparison, security/lifecycle/portability review, decision ADR |
| [G10-01](https://github.com/idev006/MT-I-AM/issues/14) | Reproducible test harness in supported environments | CI logs on target Python/OS matrix |
| [G01-01](https://github.com/idev006/MT-I-AM/issues/15) | Same OCI runtime local + Cloud Run | Revision, health/shutdown evidence and configuration |
| [G02-01](https://github.com/idev006/MT-I-AM/issues/16) | psycopg SQLAlchemy to real Supabase PostgreSQL | Bounded credential-safe connection/rollback evidence |
| [G02-04](https://github.com/idev006/MT-I-AM/issues/17) | Pooling + transaction pooler behavior | Measured pool mode, concurrency, prepared-statement and reconnect tests |

Follow with protocol conformance G05-02..06, app-local denial G06-04, R3 security G09, resources G08, portability G11, operations G12. Prerequisite, risk and result status for each ID remain in its own Issue/evidence. Avoid using the registry as a second manually edited status table.

## Definition of Ready for engineering
- Assigned owner/reviewer, explicit tested hypothesis, POC dependencies and risk class, approved synthetic data/test environment, cost stop rules, acceptable failure/negative criteria.
- Security/PII/cloud identity boundaries declared; secret names only in source, secrets outside repo.
- Chosen architecture slice is reversible and maps to UC/BR/API and an ADR where required.

## Definition of Done for gated work
- Evidence saved at exact source SHA, commands, dependency versions, environment, test input, output/error bounds and actual costs as applicable.
- Happy, negative, boundary, cleanup/cancel/restart, concurrency and recovery cases tested proportional to R3 risk.
- No stale PASS after a changing dependency or cloud topology; required reviewers confirm and linked Issues/PRs updated.
- Release/production is separate from POC completion and requires all applicable security/privacy/operational approvals.

## Configurable SSOT grouping (nonsecret TOML)
- `[project]`: name/environment/issuer policy.
- `[poc.registry]`: source path, schema version, extension policy and allowed handler keys.
- `[poc.orchestrator]`: execution mode, timeout/cancel/grace, max workers, stop/fail policy.
- `[poc.resources]`: worker/resource/queue/connection budgets.
- `[poc.evidence]`: output dir/schema/redaction/digests and retention.
- `[poc.security]`: network/remote execution disabled by default, trusted key allowlist and access policy.
- `[database]`: engine/pool and transport settings; credentials only via secret source.
- `[testing]`: deterministic fixtures, negative/security/concurrency suites.
- `[cloud]`: approved provider profiles and billing guardrails. No automatic paid provisioning via TOML alone.
All settings must have explicit consumer, type, bounds, default and test; **no inert configuration switches** and never executable import paths in TOML.

## Governance and measurement
- Kanban workflow data has **one owner**: existing GitHub Project/Issues. This document is planning/exit-gate SSOT, not a duplicate progress board.
- POC outcome SSOT: versioned reviewer-verified RESULT; test runner JSON is diagnostic and does not automatically confer acceptance.
- Metrics computed only from Issue timestamps, linked evidence and registry denominator: `verified_full_POC_PASS / 52`, blockers and age, WIP, median cycle time, relevant CI gates. Record owner, source, timestamp and methodology.
- WIP policy initially 2 P0 streams until real team capacity is known; do not promise dates without staffed capacity and measured throughput.
- Every blocked step needs one issue with explicit unblocking action and accountable owner.

## Decision gates that can halt progression
- OIDC protocol interoperability/conformance fail; ambiguous JWT issuer/subject/key continuity.
- DB pooler/transaction anomalies or unproved recovery.
- Orchestrator leaves orphan processes/resources, can execute untrusted handlers, or reports false PASS.
- Security/privacy/legal authorization missing or service billing beyond approved budgets.
- Failure to move the same OCI application and PostgreSQL schema to independent environments.

## Primary references
- [Master POC Registry](../poc/MASTER_POC_PLAN_v1.0.md)
- [POC Platform v0.2 design](../poc/POC_PLATFORM_DESIGN_v0.2.md)
- [Kanban/SSOT governance](AGILE_KANBAN_SSOT_GOVERNANCE_v1.0.md)
- [Engineering Verification Standard](ENGINEERING_VERIFICATION_STANDARD_v0.5.md)
- https://openid.net/specs/openid-connect-core-1_0.html
- https://www.rfc-editor.org/rfc/rfc9700.html
- https://pages.nist.gov/800-63-4/
- https://owasp.org/www-project-application-security-verification-standard/
