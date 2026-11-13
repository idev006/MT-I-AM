# Development Roadmap — Gate-based (DRAFT)

| Phase | Work | Deliverable | Gate |
|---|---|---|---|
| 0 Foundation | Define boundaries, risks, principles | Charter, ADRs | Scope approved |
| 1 Protocol | OIDC profile, trust, claims, API contracts, threat model | MT-ISP draft and security review | Architecture review |
| 2 SSO feasibility POC | Cross-domain login, GAS limitations, secure token and session lifecycle with two independent apps | Working proof, negative security tests | SSO/security passed |
| 3 Core services | Personnel directory, account lifecycle, app registry, audit, Supabase schemas, admin | Tested services and migrations | Data/integration passed |
| 4 Independent integration | GAS client and different-language/host client; user without app access | Reference implementations, conformance suite | Cross-app tests passed |
| 5 Hardening | Load, failures, revocation, key rotation, restore, privacy | Security/performance/recovery reports | Risk sign-off |
| 6 Pilot | Limited-user operational trial | Pilot report, release candidate | Release approval |

## First critical gate
Prove a secure standards-compliant central SSO, not merely a custom verify API. If GAS cannot implement cookies/headers securely, evaluate a minimal portable identity protocol component.

## POC acceptance
Login A then B without re-entering credentials while central session valid; App B denies unassigned user; forged/wrong-audience/expired tokens rejected; revocation bounded; no secret leakage; performance and quotas measured rather than claimed.
