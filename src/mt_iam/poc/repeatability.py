"""Bounded POC scheduler repeat-run diagnostics; NOT POC certification."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from statistics import mean
from threading import Event, Timer
from time import perf_counter
from datetime import datetime, timezone
import os

from mt_iam.poc.platform import IsolatedPOCOrchestrator, POCRegistry, RegistryError
from mt_iam.poc.resource_budget import WorkerBudget


@dataclass(frozen=True)
class RepeatabilityRound:
    run: int
    duration_ms: float
    statuses: dict[str, int]
    count: int
    matched_baseline: bool


def measure(registry: POCRegistry, *, selected: list[str] | None = None,
            repeats: int = 2, max_workers: int = 2, timeout_seconds: float = 15,
            budget: WorkerBudget | None = None, total_timeout_seconds: float = 90,
            checkpoint_path: Path | None = None) -> dict:
    """Require identical complete local results; external checks cannot become PASS."""
    if type(repeats) is not int or not 1 <= repeats <= 10:
        raise ValueError('repeats must be in 1..10')
    if not 1 <= total_timeout_seconds <= 600:
        raise ValueError('total_timeout_seconds must be in 1..600')
    plan = registry.plan(selected)
    expected_ids = [spec.id for spec in plan]
    engine = IsolatedPOCOrchestrator(
        registry, max_workers=max_workers, timeout_seconds=timeout_seconds, budget=budget
    )
    rounds: list[RepeatabilityRound] = []
    baseline: dict[str, str] | None = None

    def publish(*, stage: str, active_round: int | None = None) -> dict:
        passed = stage == 'COMPLETE' and len(rounds) == repeats and all(
            row.matched_baseline for row in rounds
        )
        summary = {
            'schema_version': 2,
            'scope': 'LOCAL_DIAGNOSTICS_ONLY',
            'full_poc_verification': 'NOT_CERTIFIED',
            'requested_repeats': repeats,
            'completed_repeats': len(rounds),
            'planned_ids': expected_ids,
            'rounds': [asdict(row) for row in rounds],
            'mean_duration_ms': round(mean(row.duration_ms for row in rounds), 2) if rounds else None,
            'repeatability_pass': passed,
            'per_round_timeout_seconds': total_timeout_seconds,
            'stage': stage,
            'active_round': active_round,
            'updated_at_utc': datetime.now(timezone.utc).isoformat(),
        }
        if checkpoint_path is not None:
            target = Path(checkpoint_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + f'.{os.getpid()}.tmp')
            try:
                temp.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
                os.replace(temp, target)
            finally:
                temp.unlink(missing_ok=True)
        return summary

    publish(stage='IN_PROGRESS', active_round=1)
    for index in range(repeats):
        publish(stage='IN_PROGRESS', active_round=index + 1)
        start = perf_counter()
        cancelled = Event()
        timer = Timer(total_timeout_seconds, cancelled.set)
        timer.daemon = True
        timer.start()
        try:
            result = engine.run(selected, cancel_event=cancelled)
        finally:
            timer.cancel()
            timer.join(timeout=1)
        elapsed = round((perf_counter() - start) * 1000, 2)
        statuses = {item.id: item.status for item in result}
        complete = (
            len(result) == len(expected_ids)
            and len(statuses) == len(expected_ids)
            and set(statuses) == set(expected_ids)
            and all(status in {'LOCAL_CHECK_PASS', 'BLOCKED', 'SKIPPED'}
                    for status in statuses.values())
            and all(statuses[spec.id] != 'LOCAL_CHECK_PASS'
                    for spec in plan if spec.mode == 'external')
        )
        if baseline is None:
            baseline = statuses.copy()
        matched = complete and statuses == baseline
        rounds.append(RepeatabilityRound(
            index + 1, elapsed, dict(Counter(statuses.values())), len(result), matched
        ))
        publish(stage='IN_PROGRESS' if matched else 'FAILED', active_round=(index + 2 if matched and index + 1 < repeats else None))
        if not matched:
            break
    return publish(stage='COMPLETE' if len(rounds) == repeats and all(row.matched_baseline for row in rounds) else 'FAILED')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Bounded local POC repeatability verification')
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout', type=float, default=15)
    parser.add_argument('--round-timeout', type=float, default=90)
    parser.add_argument('--id', action='append', dest='selected')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    try:
        summary = measure(
            POCRegistry.from_toml(), selected=args.selected,
            repeats=args.repeats, max_workers=args.workers,
            timeout_seconds=args.timeout, total_timeout_seconds=args.round_timeout,
            checkpoint_path=args.report,
        )
    except (ValueError, RegistryError) as exc:
        parser.error(str(exc))
    document = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(document + '\n', encoding='utf-8')
    print(document)
    return 0 if summary['repeatability_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
