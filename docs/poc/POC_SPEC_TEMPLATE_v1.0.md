# MT-IAM POC Experiment Specification & Result Template v1.0

**Copy this file to `docs/poc/evidence/<POC-ID>/RESULT.md` before execution. Never treat filled planning fields as evidence of PASS.**
**Risk tier:** R3 by default for identity/protocol/security; identify if scoped differently and document reason.

## 1. Identification
| Field | Entry |
|---|---|
| POC ID / title | POC-GXX-NN / ... |
| Group / priority | GXX / P0 or P1 |
| Owner / independent reviewer | TBD / TBD |
| Related ACT / UC / BR / API / SEQ / STM | TBD |
| Related ADR / architecture revision | ADR-007 / target v0.5 |
| PR / Git commit SHA | TBD |
| Test date / reviewer date | TBD |
| Verification result | **NOT RUN** |

## 2. Falsifiable research question
- **Question / problem:**
- **Hypothesis (can be disproved):**
- **Alternatives evaluated** (at least one where feasible):
- **Architecture decision affected:**
- **Explicit exclusions / out of scope:**

## 3. Prerequisites and environment
- Predecessor POC IDs and status:
- OS / Python / dependency versions / container digest:
- Runtime, hostname/network shape, PostgreSQL version, connection/pooling mode:
- Test-only accounts and synthetic fixtures:
- Environment variables (NAMES only, never values):
- Secrets provider (name/permission scope only):
- Cloud Billing approval and estimated max spend / stop threshold:

## 4. Acceptance criteria (decided before execution)
| Case ID | Scenario | Expected measurable result | Metric, threshold and measurement method | Actual | Status |
|---|---|---|---|---|---|
| T-POC-GXX-NN-001 | Happy path | TBD | TBD | Not run | NOT RUN |
| T-POC-GXX-NN-002 | Negative/abuse path | Safe failure | TBD | Not run | NOT RUN |
| T-POC-GXX-NN-003 | Timeout/exception/restart | Cleanup and safe recovery | TBD | Not run | NOT RUN |
| T-POC-GXX-NN-004 | Repeatability/portability | Same contract across target environments | TBD | Not run | NOT RUN |

Security-critical experiments: include wrong client redirect, JWT iss/aud/exp/nonce/signature, PKCE mismatch/code replay, CSRF, invalid state, race conditions and suspension behavior as relevant. Performance experiments: report p50/p95, error denominator, request window, concurrency, memory, DB pools and sample size. Never invent thresholds post hoc to get PASS.

## 5. Procedure and exact commands
1. Setup:
2. Execute positive/negative/failure tests:
3. Cleanup / tear-down:
4. Independent verification:

```sh
# Replace with actual commands when executed. Do not paste secrets.
```

## 6. Evidence manifest
| Artifact | Revision | Meaning | Location / SHA-256 | Sanitized? |
|---|---|---|---|---|
| console log / test report | TBD | TBD | TBD | TBD |
| metrics / connection snapshots | TBD | TBD | TBD | TBD |
| billing / resources ledger | TBD | TBD | TBD | TBD |

## 7. Findings
- Observed facts (not assumptions):
- Deviations from expected:
- Limitations and blind spots:
- Unexpected billing / service implications:
- Resource leak, concurrency and shutdown observations:
- Threats or privacy observations:

## 8. Architectural verdict
- **Overall verification status**: PASS / FAIL / BLOCKED / NOT RUN
- Decision: ACCEPT / REVISE / REJECT / DEFER
- Impacted components / contract/schema / ADR:
- Follow-up defects / owner / priority:
- Dependencies unblocked (if any):
- Reviewer confirmation with date and evidence:
- Production gate: **BLOCKED** unless all applicable independent evidence and approvals exist

## 9. Handoff
- State of work and branch:
- Resources created and exact clean-up status:
- Next safe step / missing prerequisite:
- Other-team assumptions to preserve:

## Protocol and engineering references
- [Master registry](../../MASTER_POC_PLAN_v1.0.md)
- [Execution playbook](../../POC_EXECUTION_AND_HANDOFF_v1.0.md)
- [Engineering standard](../../../delivery/ENGINEERING_VERIFICATION_STANDARD_v0.5.md)
