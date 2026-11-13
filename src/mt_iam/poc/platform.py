"""Extensible, fail-closed POC registry and dependency-aware orchestrator.

Security boundary: TOML is data, NEVER an executable plugin import path. Only
pre-reviewed CHECKS handlers are eligible; unknown new IDs become BLOCKED.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from mt_iam.poc.isolated import run_isolated
from typing import Callable
import json
import re
import tomllib

from mt_iam.poc.checks import CHECKS, EXTERNAL
from mt_iam.poc.registry import CASES

ID_PATTERN = re.compile(r"^POC-G\d{2}-\d{2,4}$")
MAX_TOML_BYTES = 1024 * 1024


@dataclass(frozen=True)
class POCSpec:
    id: str
    group: str
    title: str
    priority: str
    depends_on: tuple[str, ...] = ()
    enabled: bool = True
    mode: str = "local"  # local or external


@dataclass(frozen=True)
class RunResult:
    id: str
    status: str
    detail: str
    duration_ms: float | None = None


class RegistryError(ValueError):
    pass


def _read_toml(path: Path) -> dict:
    if path.stat().st_size > MAX_TOML_BYTES:
        raise RegistryError("TOML config exceeds one-megabyte cap")
    with path.open("rb") as stream:
        return tomllib.load(stream)


class POCRegistry:
    """Builds from 52 canonical plans; supports new metadata-only POC items."""

    def __init__(self, specs: list[POCSpec]):
        self.by_id: dict[str, POCSpec] = {}
        for spec in specs:
            if not ID_PATTERN.fullmatch(spec.id) or spec.group != spec.id[4:7]:
                raise RegistryError(f"Invalid ID or group: {spec.id}")
            if spec.id in self.by_id:
                raise RegistryError(f"Duplicate POC ID: {spec.id}")
            if spec.priority not in ("P0", "P1", "P2") or spec.mode not in ("local", "external"):
                raise RegistryError(f"Invalid priority or mode: {spec.id}")
            if not spec.title.strip():
                raise RegistryError(f"Missing title: {spec.id}")
            self.by_id[spec.id] = spec
        self._validate_dependencies()

    @classmethod
    def from_toml(cls, path: Path | None = None) -> POCRegistry:
        specs = [POCSpec(c.id, c.group, c.title, c.priority,
                         mode="external" if c.id in EXTERNAL else "local") for c in CASES]
        if path is None:
            return cls(specs)
        data = _read_toml(Path(path))
        records = data.get("poc", [])
        if not isinstance(records, list):
            raise RegistryError("TOML [[poc]] entries must be an array")
        seen = set()
        existing = {item.id: item for item in specs}
        allowed = {"id", "title", "priority", "depends_on", "enabled", "mode"}
        for record in records:
            if not isinstance(record, dict) or set(record) - allowed:
                raise RegistryError("Unexpected/invalid POC metadata fields")
            poc_id = record.get("id")
            if not isinstance(poc_id, str) or not ID_PATTERN.fullmatch(poc_id):
                raise RegistryError("Bad POC ID")
            if poc_id in seen:
                raise RegistryError(f"Duplicate override: {poc_id}")
            seen.add(poc_id)
            previous = existing.get(poc_id)
            if previous is not None and ("title" in record and record["title"] != previous.title):
                raise RegistryError("Canonical titles must be updated in Master POC Plan")
            deps = record.get("depends_on", list(previous.depends_on) if previous else [])
            if not isinstance(deps, list) or not all(isinstance(s, str) for s in deps):
                raise RegistryError("depends_on must be array of strings")
            enabled = record.get("enabled", previous.enabled if previous else True)
            if not isinstance(enabled, bool):
                raise RegistryError("enabled must be boolean")
            mode = record.get("mode", previous.mode if previous else "external")
            # Built-in external checks may not be turned into local tests using TOML.
            if poc_id in EXTERNAL and mode != "external":
                raise RegistryError("External POC cannot be promoted by config")
            if previous is None and mode != "external":
                raise RegistryError("New POC needs reviewed Python handler before local execution")
            existing[poc_id] = POCSpec(
                poc_id, poc_id[4:7], record.get("title", previous.title if previous else ""),
                record.get("priority", previous.priority if previous else "P1"),
                tuple(deps), enabled, mode,
            )
        return cls(list(existing.values()))

    def _validate_dependencies(self) -> None:
        colors: dict[str, int] = {}
        def visit(poc_id: str) -> None:
            state = colors.get(poc_id, 0)
            if state == 1:
                raise RegistryError(f"Cyclic dependencies at {poc_id}")
            if state == 2:
                return
            colors[poc_id] = 1
            for dep in self.by_id[poc_id].depends_on:
                if dep not in self.by_id:
                    raise RegistryError(f"Unknown prerequisite {dep} for {poc_id}")
                if dep == poc_id:
                    raise RegistryError(f"Self dependency at {poc_id}")
                visit(dep)
            colors[poc_id] = 2
        for poc_id in self.by_id:
            visit(poc_id)

    def plan(self, selected: list[str] | None = None) -> list[POCSpec]:
        ids = sorted(selected if selected is not None else self.by_id)
        for poc_id in ids:
            if poc_id not in self.by_id:
                raise RegistryError(f"Unknown POC: {poc_id}")
        result = []
        seen = set()
        def visit(poc_id: str) -> None:
            if poc_id not in seen:
                for dep in self.by_id[poc_id].depends_on:
                    visit(dep)
                seen.add(poc_id)
                result.append(self.by_id[poc_id])
        for poc_id in ids:
            visit(poc_id)
        return result


class POCOrchestrator:
    """Safely executes trusted deterministic handlers in dependency order.

    Deliberately sequential: no thread/process is abandoned on timeout. Handler
    timeouts are unsupported until isolated subprocess contracts are developed.
    """
    def __init__(self, registry: POCRegistry,
                 checks: dict[str, Callable[[], str]] | None = None):
        self.registry = registry
        self.checks = CHECKS if checks is None else checks

    def run(self, selected: list[str] | None = None, *, dry_run: bool = False) -> list[RunResult]:
        results: list[RunResult] = []
        current: dict[str, RunResult] = {}
        for spec in self.registry.plan(selected):
            failed_dep = next((dep for dep in spec.depends_on
                               if current[dep].status != "LOCAL_CHECK_PASS"), None)
            if not spec.enabled:
                output = RunResult(spec.id, "SKIPPED", "Disabled by configured policy")
            elif failed_dep:
                output = RunResult(spec.id, "BLOCKED", f"Prerequisite {failed_dep} not locally verified")
            elif dry_run:
                output = RunResult(spec.id, "NOT_RUN", "Dry-run, no handler executed")
            elif spec.mode == "external" or spec.id not in self.checks:
                output = RunResult(spec.id, "BLOCKED", EXTERNAL.get(
                    spec.id, "No independently reviewed executable handler"))
            else:
                started = perf_counter()
                try:
                    detail = self.checks[spec.id]()
                    output = RunResult(spec.id, "LOCAL_CHECK_PASS", str(detail),
                                       round((perf_counter()-started)*1000, 2))
                except Exception as exc:
                    output = RunResult(spec.id, "FAIL", f"{type(exc).__name__}: local check failed",
                                       round((perf_counter()-started)*1000, 2))
            results.append(output)
            current[spec.id] = output
        return results


class IsolatedPOCOrchestrator:
    """Dependency-aware, fail-closed worker scheduler with bounded fanout.

    Local checks are not full POC certifications; remote checks remain BLOCKED.
    """

    def __init__(self, registry: POCRegistry, *, max_workers: int = 1,
                 timeout_seconds: float = 15, fail_fast: bool = False):
        if not 1 <= max_workers <= 4:
            raise RegistryError("Worker count must be 1..4 for local POC lab")
        if not 0.1 <= timeout_seconds <= 300:
            raise RegistryError("Timeout must be 0.1..300 seconds")
        self.registry = registry
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.fail_fast = fail_fast

    def run(self, selected: list[str] | None = None, *, dry_run: bool = False,
            cancel_event: Event | None = None) -> list[RunResult]:
        plan = self.registry.plan(selected)
        results: dict[str, RunResult] = {}
        pending = {spec.id: spec for spec in plan}
        cancelled = cancel_event if cancel_event is not None else Event()

        def execute(spec: POCSpec) -> RunResult:
            started = perf_counter()
            out = run_isolated(spec.id, timeout_seconds=self.timeout_seconds,
                               cancel_event=cancelled)
            return RunResult(spec.id, out.status, out.detail,
                             round((perf_counter() - started) * 1000, 2))

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            while pending:
                ready = [spec for spec in plan if spec.id in pending and
                         all(dep in results for dep in spec.depends_on)]
                if not ready:
                    raise RegistryError("Missing resolved dependency while scheduling")
                # Submit a bounded level; each result is committed before downstream work.
                for start in range(0, len(ready), self.max_workers):
                    batch = ready[start:start + self.max_workers]
                    futures = {}
                    for spec in batch:
                        denied = next((d for d in spec.depends_on
                                       if results[d].status != "LOCAL_CHECK_PASS"), None)
                        if cancelled.is_set():
                            results[spec.id] = RunResult(spec.id, "CANCELLED", "Run cancelled")
                        elif not spec.enabled:
                            results[spec.id] = RunResult(spec.id, "SKIPPED", "Disabled by policy")
                        elif denied:
                            results[spec.id] = RunResult(spec.id, "BLOCKED", f"Prerequisite {denied} not verified")
                        elif dry_run:
                            results[spec.id] = RunResult(spec.id, "NOT_RUN", "Dry-run")
                        elif spec.mode == "external" or spec.id not in CHECKS:
                            results[spec.id] = RunResult(spec.id, "BLOCKED", EXTERNAL.get(
                                spec.id, "No reviewed local handler"))
                        else:
                            futures[spec.id] = pool.submit(execute, spec)
                    for poc_id, future in futures.items():
                        results[poc_id] = future.result()
                        if self.fail_fast and results[poc_id].status in ("FAIL", "TIMEOUT"):
                            cancelled.set()
                    for spec in batch:
                        pending.pop(spec.id)
        return [results[spec.id] for spec in plan]


def report(results: list[RunResult], *, config_path: Path | None = None) -> dict:
    status = {key: sum(r.status == key for r in results) for key in
              ("LOCAL_CHECK_PASS", "BLOCKED", "NOT_RUN", "SKIPPED", "FAIL")}
    config_hash = sha256(config_path.read_bytes()).hexdigest() if config_path else None
    return {"schema_version": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config_sha256": config_hash,
            "summary": status,
            "full_poc_verification": "NOT_CERTIFIED",
            "results": [asdict(x) for x in results]}


def write_report(path: Path, payload: dict) -> None:
    """Report destination must be supplied by owner; write atomically, no secrets."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)
