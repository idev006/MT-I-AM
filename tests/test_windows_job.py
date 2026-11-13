"""Windows Job Object lifecycle smoke/integration checks, without cloud access."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from mt_iam.poc.windows_job import managed_worker_lifetime


def test_non_windows_noop():
    if os.name != "nt":
        with managed_worker_lifetime():
            assert True


@pytest.mark.skipif(os.name != "nt", reason="Requires real Windows Job Object support")
def test_windows_job_kills_child_when_worker_exits(tmp_path: Path):
    """A successful Windows worker must not leave a running child process."""
    pid_path = tmp_path / "child_pid.txt"
    script = (
        "import subprocess,sys\n"
        "from mt_iam.poc.windows_job import managed_worker_lifetime\n"
        "with managed_worker_lifetime():\n"
        "    p = subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],"
        " stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        f"    open({str(pid_path)!r},'w').write(str(p.pid))\n"
    )
    process = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=10
    )
    assert process.returncode == 0, process.stderr
    pid = int(pid_path.read_text())
    import ctypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.GetExitCodeProcess.argtypes = (
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)
    )
    kernel.GetExitCodeProcess.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel.CloseHandle.restype = ctypes.c_int

    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        handle = kernel.OpenProcess(0x1000, 0, pid)
        if not handle:
            return
        try:
            exit_code = ctypes.c_uint32()
            if (
                not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code))
                or exit_code.value != 259
            ):
                return
        finally:
            kernel.CloseHandle(handle)
        time.sleep(0.05)
    pytest.fail("Child survived closing the worker-owned Windows Job Object")
