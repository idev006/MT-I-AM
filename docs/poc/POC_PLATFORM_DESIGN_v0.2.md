# MT-IAM POC Platform — Registry / Orchestrator / Config SSOT v0.2

**Status:** local-first prototype; reviewed code paths have executed tests. **Not a production IAM** and no full POC claims.

## Architecture and responsibility

`Master POC Plan` remains SSOT for the **identity and specification** of canonical 52 POCs. `GitHub Issues/Projects` remains SSOT for **live Kanban work state**. Versioned TOML is SSOT for **non-secret runtime execution policy and newly proposed POC metadata**. JSON output is per-run evidence only, **not** another editable status board. Credential values are never in TOML.

- `src/mt_iam/poc/registry.py` — immutable baseline catalog of 52 canonical ID/title pairs (existing).
- `src/mt_iam/poc/platform.py` — merge validated TOML declarations; reject duplicate/unknown/cyclic dependency records; provide deterministic topological order and fail-closed executor.
- `src/mt_iam/poc/settings.py` — strict typed groups, rejects unsupported parallel mode, remote execution and dynamic plugin loading.
- `src/mt_iam/poc/platform_cli.py` — CLI selecting ID(s), dry-run and atomic sanitized JSON output.
- `configs/platform.toml` — human-editable platform settings grouped by domain.
- `configs/poc_registry.toml` — optional POC dependencies, enable/disable switches and *new, non-executable* metadata-only candidates.
- `src/mt_iam/poc/checks.py` — trusted Python check handlers for existing baseline; no unreviewed imports or `eval`.

## Configurable Sections

| Section | Examples | Authority |
|---|---|---|
| `[project]` | `name`, `environment` | human-reviewed TOML |
| `[poc.registry]` | `path`, `allow_new` | validated; no arbitrary imports |
| `[poc.orchestrator]` | `execution_mode`, `max_parallel`, `fail_fast`, `include_dependencies` | sequential-only enforced in v0.2 |
| `[poc.evidence]` | `output_directory`, `redact_secrets` | redaction cannot be disabled |
| `[database]` | `provider`, `pool_size`, `max_overflow`, `pool_timeout_seconds` | definitions only; secrets external |
| `[security]` | `allow_remote_execution`, `allow_dynamic_plugins`, `require_review_for_new_handlers` | remote execution/plugin loading disabled |
| `[cloud]` | `enabled`, `max_instances` | no implicit cloud provisioning |
| `[testing]` | `require_negative_tests`, `require_cleanup_tests` | policy values; no automatic conformance claim |

Some settings in TOML are *future policy inputs*, not connected to the current runner. The only controls presently acted on are registry file selection and the fail-closed orchestrator execution mode / security restrictions. Do not assume `fail_fast`, `include_dependencies`, cloud provisioning, resource pooling or metrics are operational just because keys exist.

## Adding an item

1. Propose ID such as `POC-G99-01`, title, group, priority, acceptance and security risk in a GitHub Issue; update Master Plan if accepted as canonical. Existing ID/title pairs may not be overwritten by TOML.
2. Add `[[poc]]` record in `configs/poc_registry.toml` with dependencies and `enabled=false`. Unregistered IDs do not execute by default.
3. Add explicitly reviewed Python handler to trusted registry and tests. New ID is BLOCKED until this happens. **No Python module path, shell command, URL, secrets or arbitrary expression is accepted as a TOML handler.**
4. Execute local positive/negative/exception tests and then (if necessary) provider-specific conformance tests. Record evidence with SHA and independent review; promote to full PASS only when all required gates meet criteria.

## Safe CLI usage

```powershell
python -m pip install -e ".[test,database]"
python -m pytest -q
python -m mt_iam.poc.platform_cli --config configs/platform.toml --dry-run
python -m mt_iam.poc.platform_cli --config configs/platform.toml --id POC-G03-03 --report artifacts/poc-results/g03-03.json
python -m mt_iam.poc.platform_cli --config configs/platform.toml --report artifacts/poc-results/all.json
python -m mt_iam.poc.platform_cli --config configs/platform.toml --strict
```

`--strict` deliberately exits nonzero when at least one requested POC is not locally verified. This is only a local gate, not a production release gate. A new experimental POC (`G99`) appears in the example Registry as `SKIPPED` and must not count toward the canonical 52 denominator.

## Remaining gates before architecture freeze

A. Owner review of the architecture decision records, user experience and business rules; B. actual OIDC provider selection and conformance; C. Supabase PostgreSQL pooler, TLS and real restore; D. bounded subprocess execution and timeout/cancellation (v0.2 does not claim it); E. source-lock, SBOM, review and CI validation; F. real Cloud Run/portability/ops; G. formal requirements tracing `UC -> API -> test -> evidence`.

## Reference standards used

- Python `tomllib` standard library: https://docs.python.org/3/library/tomllib.html
- `pytest` parametrization and markers: https://docs.pytest.org/en/stable/how-to/parametrize.html
- Python concurrency cancellation caveats: https://docs.python.org/3/library/concurrent.futures.html
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OAuth 2.0 Security BCP: https://www.rfc-editor.org/rfc/rfc9700.html
