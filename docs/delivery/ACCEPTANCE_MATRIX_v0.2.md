# MT-IAM Acceptance Matrix v0.2
Status: DESIGN TARGETS, not passed tests.

| ID | Acceptance criterion | Test approach | Required evidence |
|---|---|---|---|
| A01 | User signs in once to App A then App B without reentering password while SSO session valid | Browser E2E on separate domains | HAR sanitized, timestamped execution |
| A02 | User denied app access by App B despite valid IAM identity; App A unaffected | Two-app integration | Backend 403/denial and SSO continuity trace |
| A03 | Roles/permissions not stored or decided by MT-IAM | Schema/API/architecture inspection | Review + contract tests |
| A04 | GAS client and different-language client use identical published protocol | Integration tests | Client examples + results |
| A05 | Wrong issuer/audience/expired/tampered tokens are rejected | Negative tests | Automated security report |
| A06 | Invalid/duplicate/expired codes and PKCE errors rejected | Adversarial login tests | Request-response evidence |
| A07 | Account suspension propagates within approved bounded window | Time-controlled tests | elapsed time, policy ID |
| A08 | MT-IAM never receives each app's business request | Observability trace | representative traffic topology |
| A09 | Directory returns only authorized minimal fields | Schema/access tests | API tests and data classification |
| A10 | Backup/restore and migration to second PostgreSQL environment works | Recovery drill | verified recovery report |
| A11 | No secrets or private personnel data in public repository | secret scan + review | scan log, finding disposition |
| A12 | Auth performance measured under agreed concurrency | Load test | P50/P95/P99, error rates and quotas |

## KPI contracts (must be completed before benchmark)
- **Cross-app no-password SSO success rate**: successful B session without credential prompt / eligible B attempts; source browser E2E; window test run; owner QA; target TBD; guardrail no bypass of app access.
- **Auth P95**: 95th percentile elapsed from auth start until app session established; source frontend trace + server correlation; window representative load run; owner performance lead; target TBD; guardrail timeout/error <= TBD.
- **Revocation propagation P95/max**: duration from committed central disable to last usable local session; source synthetic account scenarios; window test run; owner security; target TBD before pilot; guardrail all privileged actions closed within defined maximum.
- **Contract conformance**: passed critical normative cases / attempted critical cases by stack and version; source automated test reports; owner integration lead; target 100% of mandatory critical cases.

Do not report PASS until executable evidence from current revision exists.
