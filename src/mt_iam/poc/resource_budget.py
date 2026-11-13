"""Bounded per-worker resource budgets; not a malicious-code sandbox.

POSIX RLIMIT_AS/RLIMIT_CPU apply to the worker process only; Windows limits
must be supplied by its Job Object and validated separately on Windows CI.
"""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class WorkerBudget:
    memory_mb: int = 768
    cpu_seconds: int = 30

    def __post_init__(self) -> None:
        if type(self.memory_mb) is not int or not 128 <= self.memory_mb <= 4096:
            raise ValueError("memory_mb must be integer 128..4096")
        if type(self.cpu_seconds) is not int or not 1 <= self.cpu_seconds <= 300:
            raise ValueError("cpu_seconds must be integer 1..300")


def enforce_posix_budget(budget: WorkerBudget) -> None:
    """Apply hard limits before executing a trusted POC handler.

    This function runs *inside* the child, not in unsafe preexec_fn.
    Unsupported POSIX hosts fail closed instead of silently ignoring limits.
    """
    if os.name == "nt":
        raise RuntimeError("Windows budgets require a configured Job Object")
    import resource
    if not hasattr(resource, "RLIMIT_AS") or not hasattr(resource, "RLIMIT_CPU"):
        raise RuntimeError("Required POSIX rlimits unavailable")
    resource.setrlimit(resource.RLIMIT_AS, (budget.memory_mb * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (budget.cpu_seconds, budget.cpu_seconds))
