"""Trusted local-check worker. NEVER accepts an import string or shell command."""
from argparse import ArgumentParser
import json
from mt_iam.poc.checks import CHECKS, EXTERNAL
from mt_iam.poc.windows_job import managed_worker_lifetime


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args(argv)
    if args.id not in CHECKS or args.id in EXTERNAL:
        print(json.dumps({"status": "BLOCKED", "detail": "Unknown or external ID"}))
        return 2
    try:
        # Attach to Windows Job Object before any trusted handler can spawn children.
        with managed_worker_lifetime():
            detail = CHECKS[args.id]()
            print(json.dumps({"status": "LOCAL_CHECK_PASS", "detail": str(detail)}), flush=True)
        return 0
    except BaseException:
        print(json.dumps({"status": "FAIL", "detail": "Trusted handler failed"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
