# MT-IAM POC Platform v0.3 — Isolated Orchestrator extension

Baseline: v0.2 registry stays canonical for 52 fixed IDs plus controlled TOML additions. This design extends, never replaces, [Platform v0.2](POC_PLATFORM_DESIGN_v0.2.md).

## Execution pipeline

```
Validated TOML -> Registry + Dependency DAG -> IsolatedPOCOrchestrator
  -> bounded local scheduling (max 4, default 2)
  -> only reviewed built-in CHECKS handler ID
  -> python -m mt_iam.poc.isolated_worker --id ID
  -> typed result: LOCAL_CHECK_PASS / BLOCKED / FAIL / TIMEOUT / CANCELLED
  -> versioned JSON evidence (NOT_CERTIFIED)
```

Inputs from TOML are **data only**, never arbitrary executable code, shell commands or imports. POC result `LOCAL_CHECK_PASS` is not full compliance evidence. External POCs fail closed when missing real provider tests. Each child owns one handler run. Parent owns and reaps the process on exit, timeout or cancellation.

## Configuration controls

- `[poc.orchestrator] execution_mode = "isolated"` (or legacy `"sequential"`)
- `max_parallel = 1..4` isolated; sequential requires 1.
- `timeout_seconds = 1..300` in TOML (float 0.1..300 accepted programmatically)
- `fail_fast` aborts queued follow-on checks on real `FAIL`/`TIMEOUT`.
- CLI `--config configs/platform.toml --dry-run --report <owned-path>`.
- Unapproved remote execution, new dynamic handler imports, secret-redaction disabling and arbitrary registry paths are rejected.

## Limitations and next design gates

1. Validate process-tree shutdown, cooperative cancellation and restart against Windows and Linux real runners. Re-run full 52-case suite and benchmark >1 consecutive execution.
2. Add durable execution IDs, structured cancellation and per-task monotonic state transitions with explicit ownership.
3. Implement OS-level CPU/memory/cgroup or job-object quotas where available, rather than treating `max_parallel` as a hard memory/CPU limit.
4. Add bound on worker output byte size while process is running, not just after collecting it (stdout pipes can buffer heavily).
5. Add schema-versioned evidence and provenance manifest (commit SHA, env, resolved package hashes, reviewer).
6. Pin dependencies in reproducible lock, run GitHub CI matrix Windows/Linux and Python 3.12/3.13.
7. Live integration remains separate: Supabase DB pooling, OIDC conformance, Cloud Run, migration/recovery and cost.

**Release gate:** v0.3 local tests do not authorize IAM deployment. Security/privacy R3 and independent code review needed.
