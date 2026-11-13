# MT-IAM POC52 Runner — Local Execution Baseline v0.1

**Status: 52 identifiers covered; 30 executable local checks passing; 22 BLOCKED external; no full POC PASS.**

**Environment:** isolated Python 3.13.5 container, not the user PC or Cloud Run. Synthetic data and disposable SQLite only.
**Commands:** `PYTHONPATH=src python -m pytest -q tests` and `PYTHONPATH=src python -m mt_iam.poc.runner --output docs/poc/evidence/POC52_LOCAL_REPORT.json`.
**Observed:** pytest **65 passed** (52 parametrized registry cases + foundational tests and runner/negative checks); runner **30 LOCAL_CHECK_PASS / 22 BLOCKED / 0 FAIL**.
**Caveat:** pytest passes because required external dependencies are accurately classified BLOCKED, not because all 52 POCs passed. `--require-all-pass` exits nonzero and should be used for release gating.

**Not tested:** Supabase PostgreSQL / prepared statements, Cloud Run/OCI, OIDC authorization server, official OIDC conformance, real identity federation, key rotation, OS Windows, cloud billing, load/soak and incident drills. Ruff and GitHub Actions remote execution not verified locally.

## Minimum next verification steps
1. Reviewer signs off on registry parity against canonical Master POC Plan; add architecture and test evidence links to each work item.
2. Use `pytest -q` on user's Windows Python 3.12 and record exact revision.
3. Evaluate OIDC authorization server alternatives and provider-maintained conformance. Do not author own JWT crypto.
4. Set approved isolated test secrets (outside repository) and opt into `live_probes postgresql`, `cloudrun`, `oidc` as needed.
5. Execute all remaining POCs with real environments, adversarial tests and independent review. Only then mark each parent POC as PASS and Kanban Done.

## Cost/privacy guard
No cloud resources or live credentials used in this run. Cloud budgets are alerts, not hard caps. Never add staff personal data, card information, database password or JWT signing key to GitHub.
