"""Bounded repeat-run smoke benchmark for one trusted local POC, not soak certification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from mt_iam.poc.isolated import run_isolated
from mt_iam.poc.resource_budget import WorkerBudget


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--id', default='POC-G01-03')
    p.add_argument('--repeats', type=int, default=5)
    p.add_argument('--report', type=Path, default=None)
    args = p.parse_args(argv)
    if not 1 <= args.repeats <= 50:
        p.error('repeats must be 1..50')
    results = []
    for _ in range(args.repeats):
        start = perf_counter()
        outcome = run_isolated(args.id, timeout_seconds=10, budget=WorkerBudget(768, 10))
        results.append({'status': outcome.status, 'duration_ms': round(1000*(perf_counter()-start),2)})
        if outcome.status != 'LOCAL_CHECK_PASS':
            break
    out = {'poc_id': args.id, 'requested_repeats': args.repeats, 'executed': len(results),
           'mean_duration_ms': round(mean(r['duration_ms'] for r in results),2),
           'results': results, 'full_poc_verification': 'NOT_CERTIFIED'}
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out))
    return 0 if len(results) == args.repeats and all(r['status'] == 'LOCAL_CHECK_PASS' for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
