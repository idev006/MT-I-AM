"""Hard wall-time supervisor for a fixed, trusted POC repeatability module.

No shell command is accepted via CLI or TOML. Results remain local diagnostics,
not a production SSO/identity POC certification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic, sleep
from typing import Sequence

from mt_iam.poc.resource_telemetry import TreeTelemetry

MAX_REPORT_BYTES = 2 * 1024 * 1024


def _atomic_report(path: Path, document: dict) -> None:
    """Write through an exclusive temporary file and atomically replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.{os.getpid()}.supervisor.tmp")
    try:
        with temp.open("x", encoding="utf-8") as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _checkpoint(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_REPORT_BYTES:
            raise ValueError("Checkpoint too large")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Invalid checkpoint")
        return data
    except (FileNotFoundError, OSError, ValueError, UnicodeError):
        return {"schema_version": 2, "scope": "LOCAL_DIAGNOSTICS_ONLY",
                "full_poc_verification": "NOT_CERTIFIED",
                "rounds": [], "completed_repeats": 0}


def _end_tree(process: subprocess.Popen) -> None:
    """Kill the owned POSIX group or live Windows tree and reap the leader."""
    if os.name == "nt":
        if process.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, timeout=5, check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                if process.poll() is None:
                    process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _supervise_command(command: Sequence[str], *, report: Path,
                       hard_timeout_seconds: float) -> int:
    """Internal test seam. Public CLI builds only a fixed trusted command."""
    if type(hard_timeout_seconds) not in (float, int) or not 0.2 <= hard_timeout_seconds <= 3600:
        raise ValueError("Hard timeout must be 0.2..3600 seconds")
    report = Path(report)
    if report.exists():
        raise FileExistsError("Refusing to overwrite a prior evidence report")
    report.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        list(command), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, start_new_session=os.name != "nt",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    started = monotonic()
    telemetry = TreeTelemetry()
    telemetry.sample(process.pid)
    timed_out = False
    try:
        while process.poll() is None:
            telemetry.sample(process.pid)
            if monotonic() - started >= hard_timeout_seconds:
                timed_out = True
                break
            sleep(0.04)
    except BaseException:
        _end_tree(process)
        partial = _checkpoint(report)
        partial.update(resource_telemetry=telemetry.as_report(),
                       stage="INTERRUPTED", repeatability_pass=False,
                       supervisor_status="INTERRUPTED",
                       updated_at_utc=datetime.now(timezone.utc).isoformat())
        _atomic_report(report, partial)
        raise
    finally:
        if not timed_out and process.poll() is not None:
            _end_tree(process)

    if timed_out:
        _end_tree(process)
        partial = _checkpoint(report)
        partial.update(resource_telemetry=telemetry.as_report(),
                       stage="TIMEOUT", repeatability_pass=False,
                       supervisor_status="TIMEOUT",
                       updated_at_utc=datetime.now(timezone.utc).isoformat())
        _atomic_report(report, partial)
        return 124

    data = _checkpoint(report)
    data["resource_telemetry"] = telemetry.as_report()
    accepted = (
        process.returncode == 0
        and data.get("stage") == "COMPLETE"
        and data.get("repeatability_pass") is True
        and data.get("full_poc_verification") == "NOT_CERTIFIED"
        and isinstance(data.get("requested_repeats"), int)
        and type(data.get("completed_repeats")) is int
        and data["requested_repeats"] == data["completed_repeats"]
        and isinstance(data.get("rounds"), list)
        and len(data["rounds"]) == data["completed_repeats"]
    )
    if not accepted:
        data.update(stage="FAILED", repeatability_pass=False,
                    supervisor_status="CHILD_ERROR_OR_INCOMPLETE",
                    updated_at_utc=datetime.now(timezone.utc).isoformat())
        _atomic_report(report, data)
        return 1
    _atomic_report(report, data)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hard deadline trusted POC repeatability")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--hard-timeout", type=float, default=120)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--round-timeout", type=float, default=40)
    parser.add_argument("--id", action="append", dest="selected")
    args = parser.parse_args(argv)
    if not 1 <= args.repeats <= 10 or not 1 <= args.workers <= 4:
        parser.error("repeats and workers outside approved ranges")
    if not 1 <= args.round_timeout <= 600 or not 0.2 <= args.hard_timeout <= 3600:
        parser.error("timeout outside approved range")
    command = [sys.executable, "-m", "mt_iam.poc.repeatability",
               "--repeats", str(args.repeats), "--workers", str(args.workers),
               "--round-timeout", str(args.round_timeout), "--report", str(args.report)]
    for item in args.selected or []:
        if not item.startswith("POC-G") or len(item) > 24:
            parser.error("Invalid POC ID")
        command.extend(["--id", item])
    try:
        result = _supervise_command(command, report=args.report,
                                    hard_timeout_seconds=args.hard_timeout)
    except (FileExistsError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Repeatability supervisor exit={result}; report={args.report}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
