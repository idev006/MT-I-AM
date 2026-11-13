> **CURRENT LIVE ISSUE STATUS (2026-11-13):** 52 unique OPEN POC Issues and 12 OPEN Epic Issues now exist. All 52 POCs remain **unverified full PASS**; the [local runner snapshot](../poc/POC52_EXECUTION_REPORT_v0.1.md) records 30 LOCAL_CHECK_PASS and 22 BLOCKED, not live Kanban workflow status. Duplicate Issues #38–#40 were CLOSED as duplicates of #35–#37. The actual GitHub Projects board is **NOT CONFIGURED**; [Issue #18](https://github.com/idev006/MT-I-AM/issues/18) remains the board-activation blocker. Do not interpret older activation counts below as current.

# MT-IAM Agile Kanban & Single Source of Truth Governance v1.0

**Decision status: PROPOSED operational governance (2026-11-13).** Architecture risk R3. **Board activation: NOT RUN** because the current integration can manage GitHub Issues but not create/configure a GitHub Projects board. Do not claim a board already exists.

## Executive rule — one fact, one owner, one authoritative location
**GitHub repository `idev006/MT-I-AM` is the project system of record.** Separate authority by *kind of fact*, not by duplicating lists:
- **Current work item lifecycle and ownership:** one GitHub Issue per POC/deliverable/decision task. Canonical Issue URL and number are the work ID. A Kanban board is a **view of these same issues**, not a separately maintained spreadsheet or task database.
- **Project progress:** computed from those issues and agreed completion criteria. Dashboards/reports must pull live Issue metadata; do not edit a separate progress percentage by hand.
- **Architecture decisions:** versioned ADRs in GitHub. Link Issue to ADR commit; do not paste conflicting decisions into the board.
- **POC design and actual evidence:** Markdown in `docs/poc` and versioned results in `docs/poc/evidence/<POC-ID>/RESULT.md`. Link from Issue; do not copy logs/secret data into labels.
- **Application source, API contracts, tests and config definitions:** files at reviewed Git commit.
- **Operational staff/identity master records:** PostgreSQL (NOT GitHub).
- **Credential/private keys:** secure secret provider (NOT GitHub).
- **Actual cloud usage/billing:** provider reports; link to redacted evidence, never hand-maintained as a second money ledger.
This means there is **one authoritative value for each fact**, not one physical file/database for all facts.

## Kanban source and lifecycle
Recommended view: one GitHub Projects board containing only `idev006/MT-I-AM` Issues/PRs as linked items. As an immediately available fallback, GitHub Issues remain the source while the graphical board is configured.

**Lifecycle (one active status only per Issue):**
1. `Backlog` — known, not yet committed.
2. `Ready` — acceptance criteria, prerequisites, owner/reviewer, priority and allowed cost established.
3. `In Progress` — someone is executing; obey WIP cap.
4. `In Review` — evidence and reviewer needed, not PASS yet.
5. `Blocked` — cannot move until documented dependency/risk is resolved.
6. `Done` — acceptance and independent review passed, artifacts linked, no required clean-up outstanding, Issue closed.
Use only a **single canonical status field** when a GitHub Projects board exists. Do not independently set competing `status:*` labels; without Projects support, use **exactly one** `status:backlog|ready|in-progress|in-review|blocked` label on an OPEN Issue; CLOSED Issue = Done. Remove old status label during transitions. Migration from labels to Projects must be one-way, not simultaneous. Labels for domain (`poc:G05`), priority (`priority:P0`) and risk (`risk:R3`) are categories, not alternative status.

**Separate verification from workflow:** POC verification is `PASS / FAIL / BLOCKED / NOT RUN` with result evidence. An Issue marked `In Review` does not mean a test passed. A finished review may record `FAIL` and create/follow-up a new defect Issue; it must not mark an unsuccessful experiment as PASS.

## Work-item granularity and traceability
- **Epic:** One Issue for each POC domain G01..G12 or major delivery stream. It links its 3–6 child POC Issues; epics are not parallel status ledgers.
- **POC:** One Issue for each of the 52 IDs, created *as execution is prepared* rather than opening all 52 without owners or accepted scope. Title: `[POC-G05-01] Evaluate OIDC authorization server`.
- **Implementation:** One Issue for each tested vertical slice/feature; link associated POC and UC/BR/API/ADR.
- **Bug/Risk:** An Issue for an actionable defect, blocker or decision; link the owning POC. Avoid duplicate issues for same fact.
- **Pull Request:** Reference closing Issue(s), tested commit and acceptance evidence. Merging code is NOT equal to closing a R3 Issue without review.

### Required Issue fields/body
```text
ID: POC-GXX-NN / UC-...
Goal / why:
Business value and architectural question:
Acceptance criteria (falsifiable, precommitted):
Related architecture / ADR / UC / API contracts:
Dependencies / blocker / owner:
Priority P0/P1; risk tier R3:
Estimate (optional; not a completion claim):
Reviewers and approval requirements:
Evidence path: docs/poc/evidence/POC-GXX-NN/RESULT.md
Cost/risk stop condition:
Exit: tests and reviewer confirmation, cleanup, decision update
```
No actual secrets, production identifiers, personal records or card/payment details.

## Definition of Ready (DoR)
- One accountable owner, reviewer or review rule, priority, related architecture, prerequisites explicit.
- Hypothesis and falsifiable success + negative/failure cases specified; estimated cloud cost and permissions checked.
- Test environment and synthetic fixtures identified; no unclear access to real personnel data.
- Blockers visible; no work started that needs unavailable credentials or production authorization.

## Definition of Done (DoD)
- Recorded test command, input, env, source SHA, sanitized output and predeclared measurable result.
- Expected negative/security/error paths verified to the experiment's scope.
- Resource clean-up verified; actual billing reviewed for cloud POCs.
- Required design/ADR/SSOT updated; architecture impact recorded.
- Independent reviewer signs evidence; issue linked to result commit; no critical R3 exception unowned.
- Relevant verification status PASS (or documented terminal FAIL with follow-up and not counted as successful POC).
- Issue is closed; progress aggregation counts only accepted, verified outcomes.

## WIP controls and flow
- Team WIP cap should be explicit and small, **initial proposal**: max 2 concurrent P0 POCs for the whole project until capacity observed (excludes paused Blocked items, but track aging).
- Pull from Ready by risk/critical dependency first; prioritize G05-01 OIDC feasibility, then G10-01 test harness and local runtime. Avoid multi-engine work until foundational feasibility established.
- Review blocked Issues daily while active; weekly review flow/WIP risks and dependency aging. Do not invent a fixed delivery date.
- No issue can be Done solely because a plan document was written; actual R3 tests and security gates must pass as applicable.

## Measurements — all computed, never hand-edited
| Measure | Formula | Source |
|---|---|---|
| POC verified-pass count | `count(unique POC IDs whose evidence verdict is PASS and reviewer confirmed)` | POC evidence + linked GitHub Issues |
| POC pass coverage | `verified passes / 52 planned registry entries` | registry fixed denominator, evidence numerator |
| Work in progress | `count(issues Status = In Progress)` | GitHub Issues/Projects |
| Blocked aging | `current timestamp - time moved to Blocked` | Issue events, not a manual date column |
| Lead time | `accepted/closed timestamp - work item creation timestamp` | GitHub Issue timestamps |
| Cycle time | `accepted/closed timestamp - In Progress start timestamp` | status history |
| Review latency | `accepted timestamp - In Review timestamp` | status history |
These figures cannot be claimed without actual event/evidence collection. A closed issue is **not** sufficient proof of POC PASS.

## Team working agreement
- Every active task must have a GitHub Issue. Updates happen in the issue, not in chat, spreadsheet or presentation.
- Every team uses the same IDs from [Master POC Plan](../poc/MASTER_POC_PLAN_v1.0.md) and references the [Handoff Playbook](../poc/POC_EXECUTION_AND_HANDOFF_v1.0.md).
- Link PRs and evidence to issues; project status is displayed from canonical Issues/board source. Generated weekly reports are snapshots with source link + as-of timestamp, never new editable records.
- Risks and architectural choices become ADRs or open Issues; do not silently overwrite previously accepted ADRs.
- Product owner signs off production-critical changes; security/privacy gates fail closed when evidence absent.

## Board setup when GitHub Projects access is available
Create one project titled `MT-IAM — EA Core Delivery`, select **Board** view, configure Status choices Backlog/Ready/In Progress/In Review/Blocked/Done, Priority P0/P1 and Group G01..G12; add **linked repository Issues only**, no free-text duplicate cards. Set project access for team, auto-add relevant repository issues, and optionally enable close/open item automation. Confirm the configured Project URL in README before claiming activation. If native GitHub Projects tools are unavailable, owner must configure UI or use a capable integration; do not fabricate a URL.

## Current activation checklist
| Item | Current evidence status |
|---|---|
| Governance document saved in GitHub | Check after writing |
| POC registry 12 groups / 52 IDs | Previously read back and checked |
| Issues/board configured for all active work | NOT RUN |
| Kanban Project URL confirmed | BLOCKED — connector has no Projects operations |
| Live status synchronization from Issues | NOT RUN |
| Actual POC execution results | NOT RUN |
| Production approval | BLOCKED |

## Activation record (2026-11-13)
- Created 12 Epic Issues #1–#12 mapping to G01–G12 and five first-wave POC Issues #13–#17 (G05-01, G10-01, G01-01, G02-01, G02-04). Existing GitHub Issues are the live work records.
- GitHub Projects board activation is explicitly tracked by [Issue #18](https://github.com/idev006/MT-I-AM/issues/18) and remains **BLOCKED**, as the connected GitHub interface has no Projects configuration action. No board URL has been invented; add a verified URL here only after owner configures the real board.
- Remaining POC IDs are design registry entries, intentionally not 47 extra issue cards until they are ready for scoped execution.
