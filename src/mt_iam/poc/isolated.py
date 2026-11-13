"""Trusted POC worker isolation with bounded IO, deadlines and process cleanup.

A TOML file must NEVER determine a Python import, shell command or executable.
Only reviewed built-in POC IDs in CHECKS can be executed. This is local isolation,
not a production-grade OS sandbox against malicious Python code.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
from time import monotonic
from mt_iam.poc.resource_budget import WorkerBudget

MAX_DETAIL_CHARS = 1600
MAX_OUTPUT_BYTES = 65536


@dataclass(frozen=True)
class IsolatedResult:
    status: str
    detail: str


def _terminate_tree(process: subprocess.Popen) -> None:
    """Kill an owned process group/tree and reap it, including on error paths."""
    # On POSIX the group may still contain descendants after the leader exits.
    # Workers run in dedicated sessions, so always clean up the owned group.
    if os.name != "nt":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL, capture_output=True, timeout=5, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _safe_worker_env() -> dict[str, str]:
    """Minimal environment; never propagate DB credentials or cloud tokens."""
    names = {
        "PATH", "PYTHONPATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
        "HOME", "LANG", "LC_ALL", "VIRTUAL_ENV", "PYTHONIOENCODING",
        "PYTHONDONTWRITEBYTECODE", "PYTHONUTF8",
    }
    return {key: value for key, value in os.environ.items() if key.upper() in names}


def _spawn_worker(poc_id: str, **kwargs) -> subprocess.Popen:
    """Create an allowlisted Python worker; separate seam for lifecycle tests."""
    env = kwargs.get("env", {})
    budget = WorkerBudget(int(env["MT_POC_MEMORY_MB"]), int(env["MT_POC_CPU_SECONDS"]))
    return subprocess.Popen(
        [sys.executable, "-m", "mt_iam.poc.isolated_worker", "--id", poc_id,
         "--memory-mb", str(budget.memory_mb), "--cpu-seconds", str(budget.cpu_seconds)],
        **kwargs,
    )


def run_isolated(
    poc_id: str, *, timeout_seconds: float = 15,
    cancel_event: threading.Event | None = None,
    budget: WorkerBudget | None = None,
) -> IsolatedResult:
    """Run one trusted local handler with hard parent deadline and bounded output.

    TemporaryFile-backed pipes prevent unbounded RAM use if worker writes large
    output. This is NOT a CPU/RAM sandbox; such limits need OS-level controls.
    """
    from mt_iam.poc.checks import CHECKS, EXTERNAL

    if poc_id not in CHECKS or poc_id in EXTERNAL:
        return IsolatedResult("BLOCKED", "No trusted local handler")
    budget = budget or WorkerBudget()
    if not 0.1 <= timeout_seconds <= 300:
        raise ValueError("Timeout outside 0.1..300 seconds")
    if cancel_event is not None and cancel_event.is_set():
        return IsolatedResult("CANCELLED", "Cancelled before process start")

    with tempfile.TemporaryFile(mode="w+b") as stdout_file, tempfile.TemporaryFile(mode="w+b") as stderr_file:
        try:
            process = _spawn_worker(
                poc_id,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                start_new_session=os.name != "nt",
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
                env={**_safe_worker_env(), "MT_POC_MEMORY_MB": str(budget.memory_mb),
                     "MT_POC_CPU_SECONDS": str(budget.cpu_seconds)},
            )
        except OSError:
            return IsolatedResult("FAIL", "Unable to start trusted worker")
        start = monotonic()
        try:
            while process.poll() is None:
                if cancel_event is not None and cancel_event.is_set():
                    _terminate_tree(process)
                    return IsolatedResult("CANCELLED", "Cancellation requested")
                if monotonic() - start >= timeout_seconds:
                    _terminate_tree(process)
                    return IsolatedResult("TIMEOUT", "Trusted handler deadline exceeded")
                if (os.fstat(stdout_file.fileno()).st_size > MAX_OUTPUT_BYTES
                        or os.fstat(stderr_file.fileno()).st_size > MAX_OUTPUT_BYTES):
                    _terminate_tree(process)
                    return IsolatedResult("FAIL", "Trusted handler output exceeded limit")
                try:
                    process.wait(timeout=min(0.05, max(0.01, timeout_seconds / 10)))
                except subprocess.TimeoutExpired:
                    continue
            if (os.fstat(stdout_file.fileno()).st_size > MAX_OUTPUT_BYTES
                    or os.fstat(stderr_file.fileno()).st_size > MAX_OUTPUT_BYTES):
                return IsolatedResult("FAIL", "Trusted handler output exceeded limit")
            if process.returncode != 0:
                return IsolatedResult("FAIL", f"Handler process failed, exit={process.returncode}")
            stdout_file.seek(0)
            raw = stdout_file.read(MAX_OUTPUT_BYTES + 1)
            try:
                payload = json.loads(raw.decode("utf-8", errors="strict"))
            except (ValueError, UnicodeDecodeError):
                return IsolatedResult("FAIL", "Invalid worker result")
            if not isinstance(payload, dict) or payload.get("status") != "LOCAL_CHECK_PASS":
                return IsolatedResult("FAIL", "Unexpected worker result")
            detail = payload.get("detail")
            if not isinstance(detail, str) or len(detail) > MAX_DETAIL_CHARS:
                return IsolatedResult("FAIL", "Invalid worker detail")
            return IsolatedResult("LOCAL_CHECK_PASS", detail)
        finally:
            # Even a successful worker can leave a child behind.
            _terminate_tree(process)
