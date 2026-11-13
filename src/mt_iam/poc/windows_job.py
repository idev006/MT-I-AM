"""Windows trusted-worker process-tree lifetime via KILL_ON_JOB_CLOSE Job Objects.

The worker attaches *itself* before executing a POC handler. This avoids
racing the parent's attempt to attach an already-running child process.
This is lifetime ownership, NOT a security sandbox against hostile code.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from typing import Iterator
from mt_iam.poc.resource_budget import WorkerBudget


def _create_current_process_job(budget: WorkerBudget | None = None) -> tuple[object, object]:
    """Create a non-inheritable job and assign this worker before running a POC.

    Host job policies may reject nested job assignment; in that event fail
    closed rather than executing a worker with an uncontrolled child tree.
    """
    budget = budget or WorkerBudget()
    if os.name != "nt":
        raise OSError("Windows Job Objects require Windows")

    import ctypes
    from ctypes import wintypes

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class BASIC_LIMIT(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class EXTENDED_LIMIT(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BASIC_LIMIT),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = (
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
    )
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.GetCurrentProcess.argtypes = ()
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL

    handle = kernel.CreateJobObjectW(None, None)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        config = EXTENDED_LIMIT()
        # 0x200: job-wide committed memory; 0x2: per-process user CPU time.
        config.BasicLimitInformation.LimitFlags = 0x00002000 | 0x00000200 | 0x00000002
        config.BasicLimitInformation.PerProcessUserTimeLimit = budget.cpu_seconds * 10_000_000
        config.JobMemoryLimit = budget.memory_mb * 1024 * 1024
        if not kernel.SetInformationJobObject(
            handle, 9, ctypes.byref(config), ctypes.sizeof(config)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if not kernel.AssignProcessToJobObject(handle, kernel.GetCurrentProcess()):
            raise ctypes.WinError(ctypes.get_last_error())
        return kernel, handle
    except BaseException:
        kernel.CloseHandle(handle)
        raise


_OWNED_JOBS: list[tuple[object, object]] = []


@contextmanager
def managed_worker_lifetime(budget: WorkerBudget | None = None) -> Iterator[None]:
    """Own child lifetime on Windows; POSIX remains parent process-group owned."""
    if os.name != "nt":
        yield
        return
    kernel, handle = _create_current_process_job(budget)
    # The current process itself is in the job. Closing its last handle here
    # would forcibly terminate this worker and turn success into a failure.
    # Hold the handle until process exit, when Windows closes it automatically
    # and terminates any surviving child processes.
    _OWNED_JOBS.append((kernel, handle))
    yield
