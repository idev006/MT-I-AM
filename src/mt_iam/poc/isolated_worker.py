"""Trusted local-check worker. NEVER accepts an import string or shell command."""
from argparse import ArgumentParser
import json
from mt_iam.poc.checks import CHECKS, EXTERNAL
from mt_iam.poc.windows_job import managed_worker_lifetime
from mt_iam.poc.resource_budget import WorkerBudget, enforce_posix_budget
import os


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--memory-mb", type=int, default=768)
    parser.add_argument("--cpu-seconds", type=int, default=30)
    args = parser.parse_args(argv)
    if args.id not in CHECKS or args.id in EXTERNAL:
        print(json.dumps({"status": "BLOCKED", "detail": "Unknown or external ID"}))
        return 2
    try:
        # Attach to Windows Job Object before any trusted handler can spawn children.
        budget = WorkerBudget(args.memory_mb, args.cpu_seconds)
        if os.name != "nt":
            enforce_posix_budget(budget)
        with managed_worker_lifetime():
            detail = CHECKS[args.id]()
            print(json.dumps({"status": "LOCAL_CHECK_PASS", "detail": str(detail)}), flush=True)
        return 0
    except BaseException:
        print(json.dumps({"status": "FAIL", "detail": "Trusted handler failed"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
