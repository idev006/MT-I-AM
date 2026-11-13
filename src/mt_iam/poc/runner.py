"""Run local deterministic checks; report BLOCKED for external dependencies.

Exit code: 0 = no local check failed (BLOCKED is expected); 1 = test failure.
Use --require-all-pass to signal incompleteness as nonzero (appropriate for releases).
"""
from argparse import ArgumentParser
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import platform
import sys
from time import perf_counter

from mt_iam.poc.registry import BY_ID, CASES
from mt_iam.poc.checks import CHECKS, EXTERNAL

@dataclass(frozen=True)
class Result:
    id: str
    group: str
    title: str
    status: str
    detail: str
    duration_ms: float | None


def execute(poc_id: str) -> Result:
    case = BY_ID[poc_id]
    if poc_id in EXTERNAL:
        return Result(case.id, case.group, case.title, "BLOCKED", EXTERNAL[poc_id], None)
    start = perf_counter()
    try:
        evidence = CHECKS[poc_id]()
        return Result(case.id, case.group, case.title, "LOCAL_CHECK_PASS", evidence,
                      round((perf_counter() - start) * 1000, 2))
    except Exception as exc:
        return Result(case.id, case.group, case.title, "FAIL",
                      f"Local check {type(exc).__name__}; inspect test logs", round((perf_counter() - start) * 1000, 2))


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="MT-IAM POC52 local check runner")
    parser.add_argument("--id", choices=sorted(BY_ID), help="Run one POC ID (default all)")
    parser.add_argument("--output", help="Optional JSON report path")
    parser.add_argument("--require-all-pass", action="store_true", help="Block release if any POC incomplete")
    args = parser.parse_args(argv)
    results = [execute(c.id) for c in (CASES if args.id is None else [BY_ID[args.id]])]
    totals = {state: sum(r.status == state for r in results) for state in ("LOCAL_CHECK_PASS", "BLOCKED", "FAIL")}
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "disclaimer": "LOCAL_CHECK_PASS is not complete POC PASS nor production approval",
        "summary": totals,
        "all_52_poc_verification": "NOT COMPLETE",
        "results": [asdict(r) for r in results],
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        from pathlib import Path
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    print(f"Executed {len(results)} registered POC entries: {totals}")
    for r in results:
        print(f"{r.id}: {r.status} — {r.detail}")
    return 1 if totals["FAIL"] or (args.require_all_pass and totals["BLOCKED"]) else 0


if __name__ == "__main__":
    sys.exit(main())
