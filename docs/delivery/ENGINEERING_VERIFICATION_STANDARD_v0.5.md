# MT-IAM Engineering & Verification Standard v0.5

**Status: PROPOSED / engineering policy pending measured implementation. R3.** 2026-11-13.
Related: [Target v0.5](../architecture/TARGET_ARCHITECTURE_v0.5_PYTHON_FIRST.md), [System Models](../architecture/SYSTEM_MODEL_v0.5.md), [ADR-007](../adr/ADR-007_PYTHON_FIRST_PORTABLE_MODULAR_CORE.md).

## Non-negotiable development rules
- Reuse reputable maintained open-source packages with compatible licenses; pin exact resolved versions after compatibility/security tests. Do not implement cryptographic primitives, JWT signing or provider conformance ad hoc.
- Test-friendly: domain logic pure where possible; dependencies injected via ports, clock, IDs and in-memory adapters for unit tests; actual PostgreSQL integration tests distinct.
- Modular boundaries: no circular imports; domain does not import FastAPI, SQLAlchemy, Google Cloud or Supabase SDK.
- Contracts-first: OpenAPI/JSON schemas and protocol standards; route handlers thin; explicit Typed Result/Exception taxonomies and error mapping.
- Changes to R3 controls require threat model update, security acceptance tests and peer review.
- Source/architecture SSOT: GitHub. Operational identity SSOT: PostgreSQL. Deployment config: validated schemas + environment. Secrets: external provider, never Git.
- Use a portable PathManager: pathlib/importlib.resources/tempfile; no writable persistent dependency on Cloud Run local filesystem. Generated files cleaned when scope ends.
- Container is standard OCI with reproducible dependencies and health checks. Cloud-specific components confined to adapters.

## Proposed repository structure (not yet created)
```text
pyproject.toml
uv.lock
Dockerfile
compose.yaml
configs/{default,development,testing}.yaml
src/mt_iam/
  api/{oidc,admin,directory,health}/
  application/{commands,queries,workflows}/
  domain/{identity,authentication,sessions,organizations,clients,policy,audit}/
  ports/{repositories,clock,secrets,events,telemetry}.py
  adapters/{postgres,secret_providers,http,observability}/
  core/{config,paths,lifecycle,errors}.py
  bootstrap.py
migrations/{env.py,versions/}
tests/{unit,integration,contract,security,load,portability}/
docs/{architecture,adr,delivery,protocol,security,operations}/
```

## Resource and concurrency safety (mandatory design review)
| Resource | Scope & ownership | Runtime policy | Evidence |
|---|---|---|---|
| SQL engine/pool | one per app process | bound total connections = instances * workers * per-worker pool size, with margin; Dispose on shutdown | connection count under burst/failure |
| DB session/UoW | one per request/use-case | context manager; rollback on error; never shared between concurrent tasks | no leaked sessions, correct atomicity |
| HTTPX client | per app lifespan | finite pool, connect/read timeout, close at shutdown | file descriptors stable |
| Async jobs | structured task scope | deadline, propagation, bounded concurrency; no fire-and-forget critical work | cancellation and restart tests |
| Queue workers | durable worker | at-least-once handling, idempotency keys, bounded retry + dead letter as relevant | crash/retry/de-dup |
| Temporary files | scoped task | tempfile and cleanup, no persistent local state | cleanup after exceptions |
| Signing keys | approved key provider | restricted access, rotation, no logs | sign/verify rollover drills |
| Observability buffers | app lifecycle | bounded flush/close, PII redaction | log review and shutdown |

Avoid long DB transactions across external HTTP calls. Transaction pooler compatibility (prepared statements/session features) is a **required empirical decision**. Alembic migrates schema as a controlled CI/CD job, not inside every runtime boot.

## Configuration contract
- Typed Settings validation fails startup on missing mandatory secrets, invalid issuer, unsafe CORS/cookie/debug/redirect configs.
- Env-specific settings from env/secret provider; YAML only for non-secret defaults. No `.env` with secrets committed.
- PathManager resolves package/config/cache/tmp without dependency on current working directory; explicitly restrict writable destinations.
- Global resource budgets and per-engine limits configured centrally, with effective settings visible only in redacted diagnostic reports.

## Automated test matrix and evidence
| Gate | Minimum scope | Status |
|---|---|---|
| G-01 Docs consistency | ADR/current architecture/README links and supersession unambiguous | NOT RUN |
| G-02 Static | Ruff + mypy + dependency audit/license scan | NOT RUN — app code absent |
| G-03 Unit | domain rules, guards, error mapping, fake adapters | NOT RUN |
| G-04 API/contract | ASGI tests, OpenAPI snapshots, wrong roles/errors | NOT RUN |
| G-05 Database | real PostgreSQL, migration up/down/restore, concurrency | NOT RUN |
| G-06 OIDC/security | provider conformance, PKCE, state/nonce, exact redirect, JWT iss/aud/exp, key rotation, replay, session/CSRF | BLOCKED — provider not selected |
| G-07 Resource | exception/cancellation/timeout, finite pools and cleanup; memory/FD/task trends vs baseline | NOT RUN |
| G-08 Load | planned 30k-50k/month and 30 RPM peaks plus burst/failure; measured p50/p95/error/CPU/DB pressure | NOT RUN |
| G-09 Portability | same core image Local Compose, Cloud Run, non-Google Linux; export/restore PostgreSQL provider | NOT RUN |
| G-10 Operations | incident and backup drill, recovery target, billing, alerts, on-call, data governance/approval | BLOCKED |
| G-11 Release | all applicable gates PASS at exact deployed revision; no open critical security defects | BLOCKED |

For PASS evidence capture source commit, environment and dependency versions, commands, sanitized output, duration, reviewer, date and artifacts. A document or successful deployment alone is never production validation.

## SSOT traceability automation (planned)
- Parse catalogs: ACT, UC, BR, API, STM, SEQ, TEST.
- Reject duplicate identifiers, dangling references, missing owner, missing tests for privileged mutations.
- Link API operation IDs to UC/BR, OpenAPI schemas to implementation, migration revisions to data model.
- Generate human-readable traceability report in CI without replacing review.

## Acceptance for initial vertical slice
UC-AUTH-001 + UC-AUTH-002 with two independent applications in different stacks/domains, B-local denial despite SSO, expired/replayed codes rejected, signed ID token validation, secure cookie/CSRF, key rotation, failed database recovery, concurrency cap, resource cleanup, issuer continuity in alternate host.

## References
- https://docs.pytest.org/
- https://docs.sqlalchemy.org/
- https://alembic.sqlalchemy.org/
- https://www.psycopg.org/psycopg3/docs/
- https://fastapi.tiangolo.com/
- https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- https://cloud.google.com/run/docs/container-contract
- https://supabase.com/docs/guides/database/connecting-to-postgres
- https://opentelemetry.io/docs/

## POC execution baseline (2026-11-13)
See [Master POC Registry](../poc/MASTER_POC_PLAN_v1.0.md), [Team Handoff Playbook](../poc/POC_EXECUTION_AND_HANDOFF_v1.0.md) and [Experiment Template](../poc/POC_SPEC_TEMPLATE_v1.0.md). These are plans, not PASS evidence. Every selected experiment must have a falsifiable hypothesis, test cases (positive/negative/failure), measured thresholds, resource cleanup, cloud cost review and linked ADR decision before promoting implementation.
