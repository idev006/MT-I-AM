# MT-IAM Project Delivery Plan v0.2
Based on MT Project Delivery Standard; R3 security/privacy/release-critical. Current state: design documents only.

## Delivery operating model
Follow Intent -> Architecture -> API/Data Contracts -> POC -> Implementation -> Security/Performance -> Deployment/Operations. Every work item requires owner, evidence, and acceptance condition. Do not conflate "file committed" with "running system" or "release ready".

## Gate register
| Gate | Description | Current state | Evidence required |
|---|---|---|---|
| G0 | requirements, constraints, SSOT, R3 classification | PASS for documented baseline; approval of v0.2 technical details pending | Charter, architecture brief approval |
| G1 | architecture, contracts, data ownership, threat model | REVIEW_REQUIRED | ADRs, diagrams, schema, threat and API reviews |
| G2 | build/static | NOT RUN | source/tests, lint, type and dependency verification |
| G3 | functional/integration/SSO | NOT RUN | two independent apps, contract and adversarial results |
| G4 | AI/safety evaluation | NOT APPLICABLE (no AI in core) | scope reasoning |
| G5 | resources/reliability | NOT RUN | quota, load, concurrency, timeouts, recovery |
| G6 | security/supply chain | NOT RUN | SAST, secret scanning, SBOM, threat controls |
| G7 | deployment | NOT RUN | clean deploy, restore, rollback, HTTPS/key readiness |
| G8 | operations/signoff | BLOCKED | monitoring, incident playbook, pilot approval |

## Requirements -> test traceability
| Requirement | Design | Tests |
|---|---|---|
| R-SSO-001 reuse valid central login across apps | OIDC Profile | SSO-01 / SSO-03 |
| R-AUTH-002 app may deny access | ADR-004 | SSO-02 |
| R-SEC-003 reject token abuse | OIDC Profile / Threat Model | SEC-01 / SEC-02 / SEC-03 |
| R-DATA-004 personnel SSOT | Data Model | DATA-01 |
| R-DEC-005 no central business permission | ADR-004 | BOUNDARY-01 |
| R-PORT-006 portable exports | Data Model / ADR-003 | PORT-01 |
| R-PERF-007 no central per-business request | Detailed Architecture | PERF-01 / load trace |

## Project disciplines
- GitHub PR review for R3 changes, protected main branch recommended.
- Unit, integration and contract tests first; add negative tests before endpoint code.
- Record exact command, environment, revision, result and evidence link for all gates.
- Restrict any external service usage to free tiers with alerting and budget guardrails.
- Scripts and migrations must be idempotent or rollbackable; never upload real personal data to public repos.
- Maintain architectural decisions as versioned ADRs, with explicit approval after POC.

## Suggested milestone outputs
M0 baseline docs; M1 protocol & data reviewed; M2 secure SSO POC; M3 directory core; M4 cross-stack clients; M5 hardening; M6 controlled pilot/release review. No promised dates before capacity and blockers are assessed.

## Ownership roles to assign
Product Owner, EA/Architecture Owner, Security Reviewer, Personnel Data Steward, Backend Engineer, Interoperability Test Lead, Operations Owner. Names deliberately unspecified pending assignment.
