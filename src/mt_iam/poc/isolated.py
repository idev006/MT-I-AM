"""Bounded, trusted-handler subprocess runner for local POC checks only.

Never execute a command or Python import path supplied by TOML. Only a POC ID
validated by the canonical CHECKS allowlist can reach this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import signal
import subprocess
import sys
import threading
from time import monotonic

MAX_DETAIL_CHARS = 1600


@dataclass(frozen=True)
class IsolatedResult:
    status: str
    detail: str


def _terminate_tree(process: subprocess.Popen[str]) -> None:
    """Terminate a process group on POSIX / child tree on Windows, then reap."""
    if process.poll() is not None:
        process.communicate(timeout=1)
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True, timeout=5, check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=5)


def run_isolated(
    poc_id: str, *, timeout_seconds: float = 15,
    cancel_event: threading.Event | None = None,
) -> IsolatedResult:
    from mt_iam.poc.checks import CHECKS, EXTERNAL

    if poc_id not in CHECKS or poc_id in EXTERNAL:
        return IsolatedResult("BLOCKED", "Handler is not on the trusted local allowlist")
    if not 0.1 <= timeout_seconds <= 300:
        raise ValueError("Timeout outside approved range")
    if cancel_event is not None and cancel_event.is_set():
        return IsolatedResult("CANCELLED", "Cancelled before process start")

    # Launch by module identifier, never from config-supplied command strings.
    # Preserve test package root while allowing standalone local editable installs.
    proc = subprocess.Popen(
        [sys.executable, "-m", "mt_iam.poc.isolated_worker", "--id", poc_id],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
        start_new_session=(os.name != "nt"),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        env={k: v for k, v in os.environ.items() if k.upper() in {
            "PATH", "PYTHONPATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP",
            "HOME", "LANG", "LC_ALL", "VIRTUAL_ENV", "PYTHONIOENCODING",
            "PYTHONDONTWRITEBYTECODE"}},
    )
    started = monotonic()
    try:
        while proc.poll() is None:
            if cancel_event is not None and cancel_event.is_set():
                _terminate_tree(proc)
                return IsolatedResult("CANCELLED", "Cancellation requested")
            if monotonic() - started >= timeout_seconds:
                _terminate_tree(proc)
                return IsolatedResult("TIMEOUT", "Trusted handler deadline exceeded")
            try:
                # Poll at bounded intervals without awaiting a potentially non-terminating worker.
                stdout, _stderr = proc.communicate(timeout=min(0.1, max(0.01, timeout_seconds / 10)))
                break
            except subprocess.TimeoutExpired:
                continue
        else:
            stdout, _stderr = proc.communicate(timeout=2)
        if proc.returncode != 0:
            return IsolatedResult("FAIL", f"Handler process failed, exit={proc.returncode}")
        if len(stdout) > 65536:
            return IsolatedResult("FAIL", "Handler output exceeded limit")
        payload = json.loads(stdout)
        if not isinstance(payload, dict) or payload.get("status") != "LOCAL_CHECK_PASS":
            return IsolatedResult("FAIL", "Handler returned an invalid result")
        detail = payload.get("detail")
        if not isinstance(detail, str) or len(detail) > MAX_DETAIL_CHARS:
            return IsolatedResult("FAIL", "Handler returned an invalid detail")
        return IsolatedResult("LOCAL_CHECK_PASS", detail)
    except (ValueError, json.JSONDecodeError, subprocess.SubprocessError, OSError):
        if proc.poll() is None:
            _terminate_tree(proc)
        return IsolatedResult("FAIL", "Handler transport or output validation failed")
    finally:
        if proc.poll() is None:
            _terminate_tree(proc)
